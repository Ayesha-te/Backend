from django.contrib import admin
from .models import Service, CartItem, Booking

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'price')  # Removed 'category'
    search_fields = ('name',)          # Removed 'category'

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('user', 'service', 'quantity')
    search_fields = ('user__email', 'service__name')

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'service', 'scheduled_for', 'status', 'created_at')  # replaced booking_date
    list_filter = ('status', 'scheduled_for', 'created_at')                      # replaced booking_date
    search_fields = ('user__email', 'service__name', 'status')
    readonly_fields = ('created_at',)
