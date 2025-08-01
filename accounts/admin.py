from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Booking, Vehicle, Document
from django.utils.translation import gettext_lazy as _
from django import forms
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count

# Custom UserCreationForm and UserChangeForm if you want to customize forms (optional)
from django.contrib.auth.forms import UserCreationForm, UserChangeForm


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('email',)


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ('email',)


class VehicleInline(admin.TabularInline):
    model = Vehicle
    extra = 0
    fields = ('make', 'model', 'year', 'registration', 'mileage', 'mot_expiry')
    readonly_fields = ('registration',)


class BookingInline(admin.TabularInline):
    model = Booking
    extra = 0
    fields = ('service', 'date', 'time', 'status', 'price')
    readonly_fields = ('service', 'date', 'time', 'price')


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ('email', 'full_name', 'is_staff', 'is_active', 'date_joined', 'booking_count', 'vehicle_count')
    list_filter = ('is_staff', 'is_active', 'is_superuser', 'date_joined')
    ordering = ('-date_joined',)
    search_fields = ('email', 'first_name', 'last_name')
    list_per_page = 25
    inlines = [VehicleInline, BookingInline]
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )
    
    @admin.display(description='Full Name')
    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip() or "No name provided"
    
    @admin.display(description='Bookings')
    def booking_count(self, obj):
        count = obj.accounts_bookings.count()
        if count > 0:
            url = reverse('admin:accounts_booking_changelist') + f'?user__id__exact={obj.id}'
            return format_html('<a href="{}">{} bookings</a>', url, count)
        return "0 bookings"
    
    @admin.display(description='Vehicles')
    def vehicle_count(self, obj):
        count = obj.accounts_vehicles.count()
        if count > 0:
            url = reverse('admin:accounts_vehicle_changelist') + f'?user__id__exact={obj.id}'
            return format_html('<a href="{}">{} vehicles</a>', url, count)
        return "0 vehicles"
    
    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('accounts_bookings', 'accounts_vehicles')


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('service', 'date', 'time', 'status_display', 'user_link', 'vehicle', 'price_display')
    list_filter = ('status', 'date', 'service')
    search_fields = ('service', 'user__email', 'user__first_name', 'user__last_name', 'vehicle')
    date_hierarchy = 'date'
    list_per_page = 25
    
    fieldsets = (
        ('Booking Information', {
            'fields': ('user', 'service', 'date', 'time', 'vehicle')
        }),
        ('Status & Pricing', {
            'fields': ('status', 'price')
        }),
    )
    
    @admin.display(description='Status')
    def status_display(self, obj):
        colors = {
            'confirmed': 'green',
            'pending': 'orange',
            'cancelled': 'red',
            'completed': 'blue'
        }
        color = colors.get(obj.status.lower(), 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.status.title()
        )
    
    @admin.display(description='User')
    def user_link(self, obj):
        url = reverse('admin:accounts_customuser_change', args=[obj.user.id])
        return format_html('<a href="{}">{}</a>', url, obj.user.email)
    
    @admin.display(description='Price')
    def price_display(self, obj):
        return format_html('<strong>£{}</strong>', obj.price)


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('registration', 'make_model', 'year', 'user_link', 'mileage', 'mot_status', 'last_service')
    search_fields = ('make', 'model', 'registration', 'user__email', 'user__first_name', 'user__last_name')
    list_filter = ('year', 'make', 'mot_expiry')
    date_hierarchy = 'mot_expiry'
    list_per_page = 25
    
    fieldsets = (
        ('Vehicle Information', {
            'fields': ('user', 'make', 'model', 'year', 'registration')
        }),
        ('Service Information', {
            'fields': ('mileage', 'mot_expiry', 'last_service')
        }),
    )
    
    @admin.display(description='Vehicle')
    def make_model(self, obj):
        return f"{obj.make} {obj.model}"
    
    @admin.display(description='User')
    def user_link(self, obj):
        url = reverse('admin:accounts_customuser_change', args=[obj.user.id])
        return format_html('<a href="{}">{}</a>', url, obj.user.email)
    
    @admin.display(description='MOT Status')
    def mot_status(self, obj):
        from datetime import date, timedelta
        today = date.today()
        
        if obj.mot_expiry < today:
            return format_html('<span style="color: red; font-weight: bold;">Expired</span>')
        elif obj.mot_expiry <= today + timedelta(days=30):
            return format_html('<span style="color: orange; font-weight: bold;">Expires Soon</span>')
        else:
            return format_html('<span style="color: green;">Valid</span>')


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('doc_type', 'date', 'vehicle', 'status_display', 'user_link')
    search_fields = ('doc_type', 'vehicle', 'user__email', 'user__first_name', 'user__last_name')
    list_filter = ('status', 'doc_type', 'date')
    date_hierarchy = 'date'
    list_per_page = 25
    
    @admin.display(description='Status')
    def status_display(self, obj):
        colors = {
            'approved': 'green',
            'pending': 'orange',
            'rejected': 'red',
            'processing': 'blue'
        }
        color = colors.get(obj.status.lower(), 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.status.title()
        )
    
    @admin.display(description='User')
    def user_link(self, obj):
        url = reverse('admin:accounts_customuser_change', args=[obj.user.id])
        return format_html('<a href="{}">{}</a>', url, obj.user.email)
