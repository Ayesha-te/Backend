from django.contrib import admin
from .models import Service, CartItem, Booking
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count, Sum

class BookingInline(admin.TabularInline):
    model = Booking
    extra = 0
    fields = ('service', 'quantity', 'scheduled_for', 'status', 'payment_completed')
    readonly_fields = ('service', 'quantity', 'scheduled_for', 'status')
    can_delete = False

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    fields = ('service', 'quantity')
    readonly_fields = ('service', 'quantity')

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'price_display', 'duration_display', 'booking_count', 'revenue', 'avg_rating')
    search_fields = ('name', 'description')
    list_filter = ('price', 'duration_minutes')
    ordering = ('name',)
    inlines = [BookingInline]
    list_per_page = 25
    
    fieldsets = (
        ('Service Information', {
            'fields': ('name', 'description')
        }),
        ('Pricing & Duration', {
            'fields': ('price', 'duration_minutes')
        }),
    )
    
    @admin.display(description='Price')
    def price_display(self, obj):
        return format_html('<strong>£{}</strong>', obj.price)
    
    @admin.display(description='Duration')
    def duration_display(self, obj):
        hours = obj.duration_minutes // 60
        minutes = obj.duration_minutes % 60
        if hours > 0:
            return f"{hours}h {minutes}m" if minutes > 0 else f"{hours}h"
        return f"{minutes}m"
    
    @admin.display(description='Bookings')
    def booking_count(self, obj):
        count = obj.dvlaa_bookings.count()
        if count > 0:
            url = reverse('admin:DVLAA_booking_changelist') + f'?service__id__exact={obj.id}'
            return format_html('<a href="{}">{} bookings</a>', url, count)
        return "0 bookings"
    
    @admin.display(description='Revenue')
    def revenue(self, obj):
        paid_bookings = obj.dvlaa_bookings.filter(payment_completed=True)
        total_revenue = sum(booking.quantity * obj.price for booking in paid_bookings)
        return format_html('<strong>£{}</strong>', total_revenue)
    
    @admin.display(description='Rating')
    def avg_rating(self, obj):
        # Placeholder for future rating system
        return format_html('<span style="color: #ffa500;">★★★★☆</span>')
    
    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('dvlaa_bookings')

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('user_link', 'service_link', 'quantity', 'total_price', 'created_date')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'service__name')
    list_filter = ('service', 'quantity')
    list_per_page = 25
    
    @admin.display(description='User')
    def user_link(self, obj):
        url = reverse('admin:accounts_customuser_change', args=[obj.user.id])
        return format_html('<a href="{}">{}</a>', url, obj.user.email)
    
    @admin.display(description='Service')
    def service_link(self, obj):
        url = reverse('admin:DVLAA_service_change', args=[obj.service.id])
        return format_html('<a href="{}">{}</a>', url, obj.service.name)
    
    @admin.display(description='Total Price')
    def total_price(self, obj):
        total = obj.quantity * obj.service.price
        return format_html('<strong>£{}</strong>', total)
    
    @admin.display(description='Added')
    def created_date(self, obj):
        # Since there's no created field, we'll show a placeholder
        return "Recently"

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'user_link', 'service_link', 'quantity', 'mot_class_display', 
        'scheduled_for', 'status_display', 'payment_status', 'created_at'
    )
    list_filter = (
        'status', 'payment_completed', 'payment_method', 
        'scheduled_for', 'created_at', 'service'
    )
    search_fields = (
        'user__email', 'user__first_name', 'user__last_name', 
        'service__name', 'motClass', 'payment_id'
    )
    readonly_fields = ('created_at', 'payment_id')
    date_hierarchy = 'scheduled_for'
    list_per_page = 25
    actions = ['mark_as_confirmed', 'mark_as_paid', 'mark_as_cancelled']
    
    fieldsets = (
        ('Booking Information', {
            'fields': ('user', 'service', 'quantity', 'motClass', 'scheduled_for'),
            'classes': ('wide',)
        }),
        ('Payment Information', {
            'fields': ('payment_completed', 'payment_id', 'payment_method'),
            'classes': ('wide',)
        }),
        ('Status & Tracking', {
            'fields': ('status', 'created_at'),
            'classes': ('wide',)
        }),
    )
    
    @admin.display(description='User')
    def user_link(self, obj):
        url = reverse('admin:accounts_customuser_change', args=[obj.user.id])
        return format_html('<a href="{}">{}</a>', url, obj.user.email)
    
    @admin.display(description='Service')
    def service_link(self, obj):
        url = reverse('admin:DVLAA_service_change', args=[obj.service.id])
        return format_html('<a href="{}">{}</a>', url, obj.service.name)
    
    @admin.display(description='MOT Class')
    def mot_class_display(self, obj):
        if obj.motClass:
            return format_html('<span style="background: #e3f2fd; padding: 2px 6px; border-radius: 3px;">{}</span>', obj.motClass)
        return "-"
    
    @admin.display(description='Status')
    def status_display(self, obj):
        colors = {
            'pending': 'orange',
            'confirmed': 'green',
            'cancelled': 'red',
        }
        icons = {
            'pending': '⏳',
            'confirmed': '✓',
            'cancelled': '✗',
        }
        color = colors.get(obj.status, 'gray')
        icon = icons.get(obj.status, '?')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{} {}</span>',
            color, icon, obj.status.title()
        )
    
    @admin.display(description='Payment')
    def payment_status(self, obj):
        if obj.payment_completed:
            status = f'✓ Paid'
            if obj.payment_id:
                status += f'<br><small>ID: {obj.payment_id[:15]}...</small>'
            return format_html('<span style="color: green; font-weight: bold;">{}</span>', status)
        else:
            return format_html('<span style="color: red; font-weight: bold;">✗ Unpaid</span>')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'service')
    
    @admin.action(description='Mark selected bookings as confirmed')
    def mark_as_confirmed(self, request, queryset):
        updated = queryset.update(status='confirmed')
        self.message_user(request, f'{updated} bookings marked as confirmed.')
    
    @admin.action(description='Mark selected bookings as paid')
    def mark_as_paid(self, request, queryset):
        updated = queryset.update(payment_completed=True)
        self.message_user(request, f'{updated} bookings marked as paid.')
    
    @admin.action(description='Mark selected bookings as cancelled')
    def mark_as_cancelled(self, request, queryset):
        updated = queryset.update(status='cancelled')
        self.message_user(request, f'{updated} bookings marked as cancelled.')
