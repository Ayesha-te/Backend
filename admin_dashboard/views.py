from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import datetime, timedelta
import csv
import json

from accounts.models import CustomUser, Booking as AccountsBooking, Vehicle, Document
from PAYPAL.models import Booking as PaypalBooking, Service as PaypalService
from DVLAA.models import Booking as DVLABooking, Service as DVLAService, CartItem


@staff_member_required
def dashboard_view(request):
    """Enhanced dashboard with statistics and charts"""
    context = get_dashboard_context()
    return render(request, 'admin/dashboard.html', context)


@staff_member_required
def analytics_view(request):
    """Analytics page with detailed insights"""
    context = get_analytics_context()
    return render(request, 'admin/analytics.html', context)


@staff_member_required
def reports_view(request):
    """Reports page with downloadable reports"""
    context = get_reports_context()
    return render(request, 'admin/reports.html', context)


@staff_member_required
def dashboard_stats_api(request):
    """API endpoint for dashboard statistics"""
    stats = get_dashboard_stats()
    return JsonResponse(stats)


@staff_member_required
def export_data(request):
    """Export data in various formats"""
    data_type = request.GET.get('type', 'users')
    format_type = request.GET.get('format', 'csv')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    if format_type == 'csv':
        return export_csv(data_type, date_from, date_to)
    elif format_type == 'json':
        return export_json(data_type, date_from, date_to)
    else:
        return JsonResponse({'error': 'Unsupported format'}, status=400)


def get_dashboard_context():
    """Get context data for dashboard"""
    today = timezone.now().date()
    last_30_days = today - timedelta(days=30)
    
    # User statistics
    total_users = CustomUser.objects.count()
    new_users_today = CustomUser.objects.filter(date_joined__date=today).count()
    new_users_month = CustomUser.objects.filter(date_joined__date__gte=last_30_days).count()
    
    # Booking statistics
    total_bookings = PaypalBooking.objects.count() + DVLABooking.objects.count()
    bookings_today = (
        PaypalBooking.objects.filter(created__date=today).count() +
        DVLABooking.objects.filter(created_at__date=today).count()
    )
    
    # Revenue statistics
    paypal_revenue = PaypalBooking.objects.filter(is_paid=True).aggregate(
        total=Sum('service__price')
    )['total'] or 0
    
    dvla_revenue = DVLABooking.objects.filter(payment_completed=True).aggregate(
        total=Sum('service__price')
    )['total'] or 0
    
    total_revenue = paypal_revenue + dvla_revenue
    
    # Recent activities
    recent_bookings = list(PaypalBooking.objects.select_related('user', 'service').order_by('-created')[:5])
    recent_users = CustomUser.objects.order_by('-date_joined')[:5]
    
    return {
        'total_users': total_users,
        'new_users_today': new_users_today,
        'new_users_month': new_users_month,
        'total_bookings': total_bookings,
        'bookings_today': bookings_today,
        'total_revenue': total_revenue,
        'recent_bookings': recent_bookings,
        'recent_users': recent_users,
    }


def get_analytics_context():
    """Get context data for analytics"""
    # Service popularity
    paypal_services = PaypalService.objects.annotate(
        booking_count=Count('booking')
    ).order_by('-booking_count')
    
    dvla_services = DVLAService.objects.annotate(
        booking_count=Count('dvlaa_bookings')
    ).order_by('-booking_count')
    
    # Monthly booking trends
    monthly_data = []
    for i in range(12):
        month_start = timezone.now().replace(day=1) - timedelta(days=30*i)
        month_end = month_start + timedelta(days=30)
        
        paypal_count = PaypalBooking.objects.filter(
            created__gte=month_start, created__lt=month_end
        ).count()
        
        dvla_count = DVLABooking.objects.filter(
            created_at__gte=month_start, created_at__lt=month_end
        ).count()
        
        monthly_data.append({
            'month': month_start.strftime('%B %Y'),
            'paypal_bookings': paypal_count,
            'dvla_bookings': dvla_count,
            'total': paypal_count + dvla_count
        })
    
    return {
        'paypal_services': paypal_services,
        'dvla_services': dvla_services,
        'monthly_data': list(reversed(monthly_data)),
    }


def get_reports_context():
    """Get context data for reports"""
    return {
        'report_types': [
            {'name': 'User Report', 'description': 'Complete user information and statistics'},
            {'name': 'Booking Report', 'description': 'All bookings with payment status'},
            {'name': 'Revenue Report', 'description': 'Financial summary and trends'},
            {'name': 'Service Report', 'description': 'Service usage and popularity'},
        ]
    }


def get_dashboard_stats():
    """Get dashboard statistics for API"""
    today = timezone.now().date()
    
    return {
        'users': {
            'total': CustomUser.objects.count(),
            'active': CustomUser.objects.filter(is_active=True).count(),
            'staff': CustomUser.objects.filter(is_staff=True).count(),
        },
        'bookings': {
            'total': PaypalBooking.objects.count() + DVLABooking.objects.count(),
            'paid': PaypalBooking.objects.filter(is_paid=True).count() + 
                   DVLABooking.objects.filter(payment_completed=True).count(),
            'pending': PaypalBooking.objects.filter(is_paid=False).count() + 
                      DVLABooking.objects.filter(payment_completed=False).count(),
        },
        'services': {
            'paypal_services': PaypalService.objects.filter(active=True).count(),
            'dvla_services': DVLAService.objects.count(),
        }
    }


def export_csv(data_type, date_from=None, date_to=None):
    """Export data as CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{data_type}_export.csv"'
    
    writer = csv.writer(response)
    
    if data_type == 'users':
        writer.writerow(['Email', 'First Name', 'Last Name', 'Date Joined', 'Is Active', 'Is Staff'])
        users = CustomUser.objects.all()
        if date_from:
            users = users.filter(date_joined__gte=date_from)
        if date_to:
            users = users.filter(date_joined__lte=date_to)
        
        for user in users:
            writer.writerow([
                user.email, user.first_name, user.last_name,
                user.date_joined, user.is_active, user.is_staff
            ])
    
    elif data_type == 'bookings':
        writer.writerow(['ID', 'User', 'Service', 'Date', 'Status', 'Payment Status'])
        
        # PayPal bookings
        paypal_bookings = PaypalBooking.objects.select_related('user', 'service')
        if date_from:
            paypal_bookings = paypal_bookings.filter(created__gte=date_from)
        if date_to:
            paypal_bookings = paypal_bookings.filter(created__lte=date_to)
        
        for booking in paypal_bookings:
            writer.writerow([
                f'PP-{booking.id}', booking.user.email, booking.service.name,
                booking.date, 'Verified' if booking.is_verified else 'Pending',
                'Paid' if booking.is_paid else 'Unpaid'
            ])
        
        # DVLA bookings
        dvla_bookings = DVLABooking.objects.select_related('user', 'service')
        if date_from:
            dvla_bookings = dvla_bookings.filter(created_at__gte=date_from)
        if date_to:
            dvla_bookings = dvla_bookings.filter(created_at__lte=date_to)
        
        for booking in dvla_bookings:
            writer.writerow([
                f'DV-{booking.id}', booking.user.email, booking.service.name,
                booking.scheduled_for, booking.status,
                'Paid' if booking.payment_completed else 'Unpaid'
            ])
    
    return response


def export_json(data_type, date_from=None, date_to=None):
    """Export data as JSON"""
    data = []
    
    if data_type == 'users':
        users = CustomUser.objects.all()
        if date_from:
            users = users.filter(date_joined__gte=date_from)
        if date_to:
            users = users.filter(date_joined__lte=date_to)
        
        for user in users:
            data.append({
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'date_joined': user.date_joined.isoformat(),
                'is_active': user.is_active,
                'is_staff': user.is_staff
            })
    
    elif data_type == 'bookings':
        # PayPal bookings
        paypal_bookings = PaypalBooking.objects.select_related('user', 'service')
        if date_from:
            paypal_bookings = paypal_bookings.filter(created__gte=date_from)
        if date_to:
            paypal_bookings = paypal_bookings.filter(created__lte=date_to)
        
        for booking in paypal_bookings:
            data.append({
                'id': f'PP-{booking.id}',
                'user': booking.user.email,
                'service': booking.service.name,
                'date': booking.date.isoformat(),
                'status': 'Verified' if booking.is_verified else 'Pending',
                'payment_status': 'Paid' if booking.is_paid else 'Unpaid',
                'type': 'PayPal'
            })
        
        # DVLA bookings
        dvla_bookings = DVLABooking.objects.select_related('user', 'service')
        if date_from:
            dvla_bookings = dvla_bookings.filter(created_at__gte=date_from)
        if date_to:
            dvla_bookings = dvla_bookings.filter(created_at__lte=date_to)
        
        for booking in dvla_bookings:
            data.append({
                'id': f'DV-{booking.id}',
                'user': booking.user.email,
                'service': booking.service.name,
                'date': booking.scheduled_for.isoformat() if booking.scheduled_for else None,
                'status': booking.status,
                'payment_status': 'Paid' if booking.payment_completed else 'Unpaid',
                'type': 'DVLA'
            })
    
    response = HttpResponse(
        json.dumps(data, indent=2),
        content_type='application/json'
    )
    response['Content-Disposition'] = f'attachment; filename="{data_type}_export.json"'
    return response