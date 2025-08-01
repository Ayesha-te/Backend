from django.db import models

from django.conf import settings
import uuid

class EmailVerification(models.Model):
    """Model to track email verification requests"""
    email = models.EmailField()
    verification_token = models.UUIDField(default=uuid.uuid4, unique=True)
    booking_details = models.JSONField()
    booking_url = models.URLField()
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Email verification for {self.email}"

class BookingReminder(models.Model):
    """Model to track booking reminders"""
    email = models.EmailField()
    booking_details = models.JSONField()
    appointment_datetime = models.DateTimeField()
    booking_url = models.URLField()
    reminder_sent = models.BooleanField(default=False)
    scheduled_for = models.DateTimeField()  # When to send the reminder
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Booking reminder for {self.email} at {self.appointment_datetime}"
