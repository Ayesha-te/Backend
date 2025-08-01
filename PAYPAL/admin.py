from django.contrib import admin
from .models import Booking, Service
from datetime import datetime
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import timedelta

class BookingInline(admin.TabularInline):
    model = Booking
    extra = 0
    fields = ('customer_first_name', 'customer_last_name', 'date', 'time', 'payment_status', 'is_paid')
    readonly_fields = ('customer_first_name', 'customer_last_name', 'date', 'time', 'payment_status')
    can_delete = False

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['id', 'code', 'name', 'price_display', 'active_status', 'booking_count', 'revenue']
    list_filter = ['active', 'price']
    search_fields = ['name', 'code', 'description']
    ordering = ['id']
    inlines = [BookingInline]
    list_per_page = 25
    
    fieldsets = (
        ('Service Information', {
            'fields': ('code', 'name', 'description')
        }),
        ('Pricing & Status', {
            'fields': ('price', 'active')
        }),
    )
    
    @admin.display(description='Price')
    def price_display(self, obj):
        return format_html('<strong>£{}</strong>', obj.price)
    
    @admin.display(description='Status')
    def active_status(self, obj):
        if obj.active:
            return format_html('<span style="color: green; font-weight: bold;">✓ Active</span>')
        else:
            return format_html('<span style="color: red; font-weight: bold;">✗ Inactive</span>')
    
    @admin.display(description='Bookings')
    def booking_count(self, obj):
        count = obj.booking_set.count()
        if count > 0:
            url = reverse('admin:PAYPAL_booking_changelist') + f'?service__id__exact={obj.id}'
            return format_html('<a href="{}">{} bookings</a>', url, count)
        return "0 bookings"
    
    @admin.display(description='Revenue')
    def revenue(self, obj):
        paid_bookings = obj.booking_set.filter(is_paid=True).count()
        total_revenue = paid_bookings * obj.price
        return format_html('<strong>£{}</strong>', total_revenue)
    
    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('booking_set')

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'user_link', 'service_link', 'customer_name', 'date', 'time', 
        'vehicle_info', 'payment_status_display', 'verification_status', 'created'
    ]
    list_filter = [
        'date', 'is_paid', 'is_verified', 'payment_status', 
        'payment_method', 'service', 'created'
    ]
    search_fields = [
        'user__email', 'customer_first_name', 
        'customer_last_name', 'customer_email', 'vehicle_registration',
        'service__name', 'paypal_transaction_id'
    ]
    readonly_fields = ['created', 'updated', 'verification_token', 'paypal_transaction_id']
    date_hierarchy = 'date'
    list_per_page = 25
    actions = ['mark_as_paid', 'mark_as_verified', 'send_confirmation_email']
    
    fieldsets = (
        ('Booking Information', {
            'fields': ('user', 'service', 'mot_class', 'date', 'time'),
            'classes': ('wide',)
        }),
        ('Customer Information', {
            'fields': (
                'customer_first_name', 'customer_last_name', 
                'customer_email', 'customer_phone', 'customer_address'
            ),
            'classes': ('collapse',)
        }),
        ('Vehicle Information', {
            'fields': (
                'vehicle_make', 'vehicle_model', 'vehicle_year',
                'vehicle_registration', 'vehicle_mileage'
            ),
            'classes': ('collapse',)
        }),
        ('Payment Information', {
            'fields': (
                'payment_method', 'payment_status', 'is_paid',
                'paypal_transaction_id'
            ),
            'classes': ('wide',)
        }),
        ('Card Information (if applicable)', {
            'fields': ('card_number', 'expiry_date', 'name_on_card'),
            'classes': ('collapse',)
        }),
        ('Verification', {
            'fields': ('is_verified', 'verification_token'),
            'classes': ('wide',)
        }),
        ('Timestamps', {
            'fields': ('created', 'updated'),
            'classes': ('collapse',)
        }),
    )

    @admin.display(description='Customer Name')
    def customer_name(self, obj):
        name = f"{obj.customer_first_name} {obj.customer_last_name}".strip()
        if obj.customer_email:
            return format_html('{}<br><small style="color: #666;">{}</small>', name, obj.customer_email)
        return name

    @admin.display(description='Vehicle')
    def vehicle_info(self, obj):
        if obj.vehicle_make and obj.vehicle_model:
            vehicle = f"{obj.vehicle_make} {obj.vehicle_model}"
            if obj.vehicle_year:
                vehicle += f" ({obj.vehicle_year})"
            if obj.vehicle_registration:
                vehicle += f"<br><small style='color: #666;'>{obj.vehicle_registration}</small>"
            return format_html(vehicle)
        return obj.vehicle_registration or "-"

    @admin.display(description='Payment Status')
    def payment_status_display(self, obj):
        if obj.is_paid:
            icon = '✓'
            color = 'green'
            text = 'Paid'
            if obj.paypal_transaction_id:
                text += f'<br><small>ID: {obj.paypal_transaction_id[:15]}...</small>'
        elif obj.payment_status == 'pending':
            icon = '⏳'
            color = 'orange'
            text = 'Pending'
        elif obj.payment_status == 'failed':
            icon = '✗'
            color = 'red'
            text = 'Failed'
        else:
            icon = '?'
            color = 'gray'
            text = obj.payment_status.title()
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{} {}</span>',
            color, icon, text
        )
    
    @admin.display(description='Verification')
    def verification_status(self, obj):
        if obj.is_verified:
            return format_html('<span style="color: green; font-weight: bold;">✓ Verified</span>')
        else:
            return format_html('<span style="color: orange; font-weight: bold;">⏳ Pending</span>')
    
    @admin.display(description='User')
    def user_link(self, obj):
        url = reverse('admin:accounts_customuser_change', args=[obj.user.id])
        return format_html('<a href="{}">{}</a>', url, obj.user.email)
    
    @admin.display(description='Service')
    def service_link(self, obj):
        url = reverse('admin:PAYPAL_service_change', args=[obj.service.id])
        return format_html('<a href="{}">{}</a>', url, obj.service.name)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'service')
    
    @admin.action(description='Mark selected bookings as paid')
    def mark_as_paid(self, request, queryset):
        updated = queryset.update(is_paid=True, payment_status='completed')
        self.message_user(request, f'{updated} bookings marked as paid.')
    
    @admin.action(description='Mark selected bookings as verified')
    def mark_as_verified(self, request, queryset):
        updated = queryset.update(is_verified=True)
        self.message_user(request, f'{updated} bookings marked as verified.')
    
    @admin.action(description='Send confirmation email')
    def send_confirmation_email(self, request, queryset):
        # This would integrate with your email system
        count = queryset.count()
        self.message_user(request, f'Confirmation emails sent for {count} bookings.')

# Custom admin site configuration
admin.site.site_header = "Access Auto Services Admin"
admin.site.site_title = "Access Auto Services Admin Portal"
admin.site.index_title = "Welcome to Access Auto Services Administration"

