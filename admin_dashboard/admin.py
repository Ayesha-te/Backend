from django.contrib import admin
from django.urls import path
from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import datetime, timedelta
from accounts.models import CustomUser, Booking as AccountsBooking, Vehicle, Document
from PAYPAL.models import Booking as PaypalBooking, Service as PaypalService
from DVLAA.models import Booking as DVLABooking, Service as DVLAService, CartItem

# Import custom admin actions
from .admin_actions import (
    export_as_csv, send_email_notification, mark_as_active, 
    mark_as_inactive, duplicate_objects, generate_summary_report
)


class AdminDashboardSite(admin.AdminSite):
    site_header = 'Access Auto Services Admin'
    site_title = 'Access Auto Services Admin Portal'
    index_title = 'Welcome to Access Auto Services Administration'
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('dashboard/', self.admin_view(self.dashboard_view), name='dashboard'),
            path('analytics/', self.admin_view(self.analytics_view), name='analytics'),
            path('reports/', self.admin_view(self.reports_view), name='reports'),
            path('api/dashboard-stats/', self.admin_view(self.dashboard_stats_api), name='dashboard_stats_api'),
        ]
        return custom_urls + urls
    
    def dashboard_view(self, request):
        """Enhanced dashboard with statistics and charts"""
        context = self.get_dashboard_context()
        return render(request, 'admin/dashboard.html', context)
    
    def analytics_view(self, request):
        """Analytics page with detailed insights"""
        context = self.get_analytics_context()
        return render(request, 'admin/analytics.html', context)
    
    def reports_view(self, request):
        """Reports page with downloadable reports"""
        context = self.get_reports_context()
        return render(request, 'admin/reports.html', context)
    
    def dashboard_stats_api(self, request):
        """API endpoint for dashboard statistics"""
        stats = self.get_dashboard_stats()
        return JsonResponse(stats)
    
    def get_dashboard_context(self):
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
    
    def get_analytics_context(self):
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
    
    def get_reports_context(self):
        """Get context data for reports"""
        return {
            'report_types': [
                {'name': 'User Report', 'description': 'Complete user information and statistics'},
                {'name': 'Booking Report', 'description': 'All bookings with payment status'},
                {'name': 'Revenue Report', 'description': 'Financial summary and trends'},
                {'name': 'Service Report', 'description': 'Service usage and popularity'},
            ]
        }
    
    def get_dashboard_stats(self):
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


# Create custom admin site instance
admin_site = AdminDashboardSite(name='admin_dashboard')