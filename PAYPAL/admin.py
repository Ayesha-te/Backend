from django.contrib import admin
from .models import Booking, Service
from datetime import datetime
from django.utils.html import format_html

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['id', 'code', 'name', 'price', 'active']
    list_filter = ['active']
    search_fields = ['name', 'code', 'description']
    list_editable = ['active', 'price']
    ordering = ['id']

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'user', 'service', 'customer_name', 'date', 'time', 
        'vehicle_info', 'payment_status_display', 'is_verified', 'created'
    ]
    list_filter = [
        'date', 'is_paid', 'is_verified', 'payment_status', 
        'payment_method', 'created'
    ]
    search_fields = [
        'user__username', 'user__email', 'customer_first_name', 
        'customer_last_name', 'customer_email', 'vehicle_registration',
        'service__name'
    ]
    readonly_fields = ['created', 'updated', 'verification_token']
    
    fieldsets = (
        ('Booking Information', {
            'fields': ('user', 'service', 'mot_class', 'date', 'time')
        }),
        ('Customer Information', {
            'fields': (
                'customer_first_name', 'customer_last_name', 
                'customer_email', 'customer_phone', 'customer_address'
            )
        }),
        ('Vehicle Information', {
            'fields': (
                'vehicle_make', 'vehicle_model', 'vehicle_year',
                'vehicle_registration', 'vehicle_mileage'
            )
        }),
        ('Payment Information', {
            'fields': (
                'payment_method', 'payment_status', 'is_paid',
                'paypal_transaction_id'
            )
        }),
        ('Verification', {
            'fields': ('is_verified', 'verification_token')
        }),
        ('Timestamps', {
            'fields': ('created', 'updated')
        }),
    )

    @admin.display(description='Customer Name')
    def customer_name(self, obj):
        return f"{obj.customer_first_name} {obj.customer_last_name}".strip()

    @admin.display(description='Vehicle')
    def vehicle_info(self, obj):
        if obj.vehicle_make and obj.vehicle_model:
            return f"{obj.vehicle_make} {obj.vehicle_model} ({obj.vehicle_registration})"
        return obj.vehicle_registration or "-"

    @admin.display(description='Payment Status')
    def payment_status_display(self, obj):
        if obj.is_paid:
            return format_html('<span style="color: green;">✓ Paid</span>')
        elif obj.payment_status == 'pending':
            return format_html('<span style="color: orange;">⏳ Pending</span>')
        else:
            return format_html('<span style="color: red;">✗ Failed</span>')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'service')

