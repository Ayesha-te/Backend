#!/usr/bin/env python
import os
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from PAYPAL.models import Booking
from email_service.models import EmailVerification, BookingReminder
from django.utils import timezone
from datetime import timedelta

def debug_recent_bookings():
    """Debug recent bookings and their email status"""
    
    print("=== Recent Bookings Debug ===")
    
    # Get recent bookings (last 7 days)
    recent_date = timezone.now() - timedelta(days=7)
    recent_bookings = Booking.objects.filter(created__gte=recent_date).order_by('-created')
    
    print(f"Found {recent_bookings.count()} bookings in the last 7 days")
    
    for booking in recent_bookings:
        print(f"\n--- Booking ID: {booking.id} ---")
        print(f"Created: {booking.created}")
        print(f"Service: {booking.service.name}")
        print(f"Customer Email: {booking.customer_email}")
        print(f"Customer Name: {booking.customer_first_name} {booking.customer_last_name}")
        print(f"Date: {booking.date}")
        print(f"Time: {booking.time}")
        print(f"Is Verified: {booking.is_verified}")
        print(f"Is Paid: {booking.is_paid}")
        
        # Check for email verifications
        email_verifications = EmailVerification.objects.filter(email=booking.customer_email)
        print(f"Email Verifications: {email_verifications.count()}")
        for ev in email_verifications:
            print(f"  - Created: {ev.created_at}, Verified: {ev.is_verified}")
        
        # Check for booking reminders
        booking_reminders = BookingReminder.objects.filter(email=booking.customer_email)
        print(f"Booking Reminders: {booking_reminders.count()}")
        for br in booking_reminders:
            print(f"  - Scheduled: {br.scheduled_for}, Sent: {br.reminder_sent}")

def debug_email_models():
    """Debug email service models"""
    
    print("\n=== Email Service Models Debug ===")
    
    # Check EmailVerification records
    email_verifications = EmailVerification.objects.all().order_by('-created_at')[:10]
    print(f"\nRecent Email Verifications ({email_verifications.count()}):")
    for ev in email_verifications:
        print(f"  ID: {ev.id}, Email: {ev.email}, Created: {ev.created_at}, Verified: {ev.is_verified}")
    
    # Check BookingReminder records
    booking_reminders = BookingReminder.objects.all().order_by('-created_at')[:10]
    print(f"\nRecent Booking Reminders ({booking_reminders.count()}):")
    for br in booking_reminders:
        print(f"  ID: {br.id}, Email: {br.email}, Scheduled: {br.scheduled_for}, Sent: {br.reminder_sent}")

def check_email_issues():
    """Check for common email issues"""
    
    print("\n=== Email Issues Check ===")
    
    # Check for bookings without customer email
    bookings_no_email = Booking.objects.filter(customer_email__isnull=True).count()
    bookings_empty_email = Booking.objects.filter(customer_email='').count()
    
    print(f"Bookings without customer email (NULL): {bookings_no_email}")
    print(f"Bookings with empty customer email: {bookings_empty_email}")
    
    # Check for failed email verifications
    failed_verifications = EmailVerification.objects.filter(is_verified=False).count()
    print(f"Unverified email verifications: {failed_verifications}")
    
    # Check for unsent reminders
    unsent_reminders = BookingReminder.objects.filter(reminder_sent=False).count()
    print(f"Unsent booking reminders: {unsent_reminders}")
    
    # Check recent bookings with email issues
    recent_date = timezone.now() - timedelta(days=3)
    recent_bookings = Booking.objects.filter(created__gte=recent_date)
    
    print(f"\nRecent bookings analysis (last 3 days):")
    for booking in recent_bookings:
        issues = []
        
        if not booking.customer_email:
            issues.append("No email address")
        
        if booking.customer_email:
            # Check if email verification was created
            email_verification_exists = EmailVerification.objects.filter(email=booking.customer_email).exists()
            if not email_verification_exists:
                issues.append("No email verification created")
            
            # Check if booking reminder was created (for future bookings)
            booking_datetime = timezone.make_aware(
                timezone.datetime.combine(booking.date, timezone.datetime.strptime(booking.time, '%H:%M').time())
            )
            if booking_datetime > timezone.now():
                reminder_exists = BookingReminder.objects.filter(email=booking.customer_email).exists()
                if not reminder_exists:
                    issues.append("No booking reminder created")
        
        if issues:
            print(f"  Booking {booking.id}: {', '.join(issues)}")

if __name__ == "__main__":
    print("Starting booking email diagnostics...\n")
    
    debug_recent_bookings()
    debug_email_models()
    check_email_issues()
    
    print("\n=== Diagnostics Complete ===")