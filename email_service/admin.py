from django.contrib import admin
from .models import EmailVerification, BookingReminder

@admin.register(EmailVerification)
class EmailVerificationAdmin(admin.ModelAdmin):
    list_display = ['email', 'is_verified', 'created_at', 'verified_at']
    list_filter = ['is_verified', 'created_at']
    search_fields = ['email']
    readonly_fields = ['verification_token', 'created_at', 'verified_at']

@admin.register(BookingReminder)
class BookingReminderAdmin(admin.ModelAdmin):
    list_display = ['email', 'appointment_datetime', 'scheduled_for', 'reminder_sent', 'created_at']
    list_filter = ['reminder_sent', 'created_at', 'appointment_datetime']
    search_fields = ['email']
    readonly_fields = ['created_at', 'sent_at']
