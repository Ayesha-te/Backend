from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Count, Sum, Q
from datetime import datetime, timedelta
import csv
import os

from accounts.models import CustomUser, Vehicle, Document
from PAYPAL.models import Service as PaypalService, Booking as PaypalBooking
from DVLAA.models import Service as DVLAService, Booking as DVLABooking


class Command(BaseCommand):
    help = 'Generate various reports for the admin panel'

    def add_arguments(self, parser):
        parser.add_argument(
            '--type',
            type=str,
            choices=['users', 'bookings', 'revenue', 'services', 'all'],
            default='all',
            help='Type of report to generate'
        )
        parser.add_argument(
            '--output-dir',
            type=str,
            default='reports',
            help='Output directory for reports'
        )
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Number of days to include in the report'
        )

    def handle(self, *args, **options):
        report_type = options['type']
        output_dir = options['output_dir']
        days = options['days']
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        self.stdout.write(self.style.SUCCESS(f'Generating {report_type} report(s)...'))
        
        if report_type == 'all':
            self.generate_users_report(output_dir, days)
            self.generate_bookings_report(output_dir, days)
            self.generate_revenue_report(output_dir, days)
            self.generate_services_report(output_dir, days)
        elif report_type == 'users':
            self.generate_users_report(output_dir, days)
        elif report_type == 'bookings':
            self.generate_bookings_report(output_dir, days)
        elif report_type == 'revenue':
            self.generate_revenue_report(output_dir, days)
        elif report_type == 'services':
            self.generate_services_report(output_dir, days)
        
        self.stdout.write(
            self.style.SUCCESS(f'Reports generated successfully in {output_dir}/')
        )

    def generate_users_report(self, output_dir, days):
        """Generate users report"""
        filename = os.path.join(output_dir, f'users_report_{timezone.now().strftime("%Y%m%d")}.csv')
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Header
            writer.writerow([
                'Email', 'First Name', 'Last Name', 'Date Joined', 
                'Is Active', 'Is Staff', 'Vehicles Count', 'Bookings Count'
            ])
            
            # Data
            users = CustomUser.objects.all().prefetch_related(
                'accounts_vehicles', 'accounts_bookings'
            )
            
            for user in users:
                writer.writerow([
                    user.email,
                    user.first_name,
                    user.last_name,
                    user.date_joined.strftime('%Y-%m-%d %H:%M:%S'),
                    user.is_active,
                    user.is_staff,
                    user.accounts_vehicles.count(),
                    user.accounts_bookings.count()
                ])
        
        self.stdout.write(f'Users report saved to: {filename}')

    def generate_bookings_report(self, output_dir, days):
        """Generate bookings report"""
        filename = os.path.join(output_dir, f'bookings_report_{timezone.now().strftime("%Y%m%d")}.csv')
        
        cutoff_date = timezone.now() - timedelta(days=days)
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Header
            writer.writerow([
                'ID', 'Type', 'User Email', 'Service Name', 'Date/Time', 
                'Status', 'Payment Status', 'Amount', 'Created'
            ])
            
            # PayPal bookings
            paypal_bookings = PaypalBooking.objects.filter(
                created__gte=cutoff_date
            ).select_related('user', 'service')
            
            for booking in paypal_bookings:
                writer.writerow([
                    f'PP-{booking.id}',
                    'PayPal',
                    booking.user.email,
                    booking.service.name,
                    f'{booking.date} {booking.time}',
                    'Verified' if booking.is_verified else 'Pending',
                    'Paid' if booking.is_paid else 'Unpaid',
                    f'£{booking.service.price}',
                    booking.created.strftime('%Y-%m-%d %H:%M:%S')
                ])
            
            # DVLA bookings
            dvla_bookings = DVLABooking.objects.filter(
                created_at__gte=cutoff_date
            ).select_related('user', 'service')
            
            for booking in dvla_bookings:
                amount = booking.quantity * booking.service.price
                writer.writerow([
                    f'DV-{booking.id}',
                    'DVLA',
                    booking.user.email,
                    booking.service.name,
                    booking.scheduled_for.strftime('%Y-%m-%d %H:%M:%S') if booking.scheduled_for else 'Not scheduled',
                    booking.status.title(),
                    'Paid' if booking.payment_completed else 'Unpaid',
                    f'£{amount}',
                    booking.created_at.strftime('%Y-%m-%d %H:%M:%S')
                ])
        
        self.stdout.write(f'Bookings report saved to: {filename}')

    def generate_revenue_report(self, output_dir, days):
        """Generate revenue report"""
        filename = os.path.join(output_dir, f'revenue_report_{timezone.now().strftime("%Y%m%d")}.csv')
        
        cutoff_date = timezone.now() - timedelta(days=days)
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Header
            writer.writerow([
                'Date', 'PayPal Revenue', 'DVLA Revenue', 'Total Revenue',
                'PayPal Bookings', 'DVLA Bookings', 'Total Bookings'
            ])
            
            # Generate daily revenue data
            current_date = cutoff_date.date()
            end_date = timezone.now().date()
            
            while current_date <= end_date:
                next_date = current_date + timedelta(days=1)
                
                # PayPal revenue
                paypal_revenue = PaypalBooking.objects.filter(
                    created__date=current_date,
                    is_paid=True
                ).aggregate(
                    total=Sum('service__price')
                )['total'] or 0
                
                paypal_bookings = PaypalBooking.objects.filter(
                    created__date=current_date
                ).count()
                
                # DVLA revenue
                dvla_bookings_qs = DVLABooking.objects.filter(
                    created_at__date=current_date,
                    payment_completed=True
                ).select_related('service')
                
                dvla_revenue = sum(
                    booking.quantity * booking.service.price 
                    for booking in dvla_bookings_qs
                )
                
                dvla_bookings = DVLABooking.objects.filter(
                    created_at__date=current_date
                ).count()
                
                total_revenue = paypal_revenue + dvla_revenue
                total_bookings = paypal_bookings + dvla_bookings
                
                writer.writerow([
                    current_date.strftime('%Y-%m-%d'),
                    f'£{paypal_revenue:.2f}',
                    f'£{dvla_revenue:.2f}',
                    f'£{total_revenue:.2f}',
                    paypal_bookings,
                    dvla_bookings,
                    total_bookings
                ])
                
                current_date = next_date
        
        self.stdout.write(f'Revenue report saved to: {filename}')

    def generate_services_report(self, output_dir, days):
        """Generate services report"""
        filename = os.path.join(output_dir, f'services_report_{timezone.now().strftime("%Y%m%d")}.csv')
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Header
            writer.writerow([
                'Type', 'Service Name', 'Price', 'Total Bookings', 
                'Paid Bookings', 'Revenue', 'Conversion Rate'
            ])
            
            # PayPal services
            paypal_services = PaypalService.objects.annotate(
                total_bookings=Count('booking'),
                paid_bookings=Count('booking', filter=Q(booking__is_paid=True))
            )
            
            for service in paypal_services:
                revenue = service.paid_bookings * service.price
                conversion_rate = (
                    (service.paid_bookings / service.total_bookings * 100) 
                    if service.total_bookings > 0 else 0
                )
                
                writer.writerow([
                    'PayPal',
                    service.name,
                    f'£{service.price}',
                    service.total_bookings,
                    service.paid_bookings,
                    f'£{revenue:.2f}',
                    f'{conversion_rate:.1f}%'
                ])
            
            # DVLA services
            dvla_services = DVLAService.objects.annotate(
                total_bookings=Count('dvlaa_bookings'),
                paid_bookings=Count('dvlaa_bookings', filter=Q(dvlaa_bookings__payment_completed=True))
            )
            
            for service in dvla_services:
                # Calculate revenue considering quantity
                paid_bookings_qs = service.dvlaa_bookings.filter(payment_completed=True)
                revenue = sum(booking.quantity * service.price for booking in paid_bookings_qs)
                
                conversion_rate = (
                    (service.paid_bookings / service.total_bookings * 100) 
                    if service.total_bookings > 0 else 0
                )
                
                writer.writerow([
                    'DVLA',
                    service.name,
                    f'£{service.price}',
                    service.total_bookings,
                    service.paid_bookings,
                    f'£{revenue:.2f}',
                    f'{conversion_rate:.1f}%'
                ])
        
        self.stdout.write(f'Services report saved to: {filename}')

    def print_summary_stats(self):
        """Print summary statistics"""
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS('SUMMARY STATISTICS'))
        self.stdout.write('='*50)
        
        # Users
        total_users = CustomUser.objects.count()
        active_users = CustomUser.objects.filter(is_active=True).count()
        staff_users = CustomUser.objects.filter(is_staff=True).count()
        
        self.stdout.write(f'Users: {total_users} total, {active_users} active, {staff_users} staff')
        
        # Bookings
        paypal_bookings = PaypalBooking.objects.count()
        dvla_bookings = DVLABooking.objects.count()
        total_bookings = paypal_bookings + dvla_bookings
        
        self.stdout.write(f'Bookings: {total_bookings} total ({paypal_bookings} PayPal, {dvla_bookings} DVLA)')
        
        # Revenue
        paypal_revenue = PaypalBooking.objects.filter(is_paid=True).aggregate(
            total=Sum('service__price')
        )['total'] or 0
        
        dvla_revenue_qs = DVLABooking.objects.filter(payment_completed=True).select_related('service')
        dvla_revenue = sum(booking.quantity * booking.service.price for booking in dvla_revenue_qs)
        
        total_revenue = paypal_revenue + dvla_revenue
        
        self.stdout.write(f'Revenue: £{total_revenue:.2f} total (£{paypal_revenue:.2f} PayPal, £{dvla_revenue:.2f} DVLA)')
        
        self.stdout.write('='*50)