#!/usr/bin/env python
"""
Test script for the booking system with email verification and PayPal integration
"""
import os
import sys
import django
from datetime import datetime, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from PAYPAL.models import Service, Booking
from email_service.models import EmailVerification, BookingReminder
from django.utils import timezone

User = get_user_model()

def test_services():
    """Test that services are properly loaded"""
    print("=== Testing Services ===")
    services = Service.objects.filter(active=True)
    print(f"Found {services.count()} active services:")
    for service in services:
        print(f"  - {service.name} (£{service.price}) - {service.code}")
    print()

def test_booking_creation():
    """Test booking creation"""
    print("=== Testing Booking Creation ===")
    
    # Get or create a test user
    user, created = User.objects.get_or_create(
        email='test@example.com',
        defaults={
            'first_name': 'Test',
            'last_name': 'User'
        }
    )
    if created:
        user.set_password('testpass123')
        user.save()
        print(f"Created test user: {user.email}")
    else:
        print(f"Using existing test user: {user.email}")
    
    # Get a test service
    service = Service.objects.filter(active=True).first()
    if not service:
        print("No active services found!")
        return
    
    # Create a test booking
    booking_date = (timezone.now() + timedelta(days=2)).date()
    booking_time = "10:00"
    
    booking = Booking.objects.create(
        user=user,
        service=service,
        date=booking_date,
        time=booking_time,
        vehicle_make='Toyota',
        vehicle_model='Corolla',
        vehicle_year='2020',
        vehicle_registration='AB12 CDE',
        vehicle_mileage='50000',
        customer_first_name='Test',
        customer_last_name='Customer',
        customer_email='test@example.com',
        customer_phone='01234567890',
        customer_address='123 Test Street, Test City',
        payment_method='card',
        payment_amount=service.price,
        payment_currency='GBP'
    )
    
    print(f"Created test booking: {booking.id}")
    print(f"  Service: {booking.service.name}")
    print(f"  Date: {booking.date} at {booking.time}")
    print(f"  Amount: £{booking.payment_amount}")
    print()
    
    return booking

def test_email_verification():
    """Test email verification creation"""
    print("=== Testing Email Verification ===")
    
    booking_details = {
        'service_name': 'MOT Test',
        'price': 54.85,
        'date': '2024-01-15',
        'time': '10:00',
        'vehicle_registration': 'AB12 CDE'
    }
    
    email_verification = EmailVerification.objects.create(
        email='test@example.com',
        booking_details=booking_details,
        booking_url='https://www.access-auto-services.co.uk/booking'
    )
    
    print(f"Created email verification: {email_verification.id}")
    print(f"  Email: {email_verification.email}")
    print(f"  Token: {email_verification.verification_token}")
    print(f"  Verified: {email_verification.is_verified}")
    print()
    
    return email_verification

def test_booking_reminder():
    """Test booking reminder creation"""
    print("=== Testing Booking Reminder ===")
    
    appointment_datetime = timezone.now() + timedelta(days=2)
    reminder_time = appointment_datetime - timedelta(hours=24)
    
    booking_details = {
        'service_name': 'Full Service',
        'price': 89.00,
        'date': appointment_datetime.strftime('%Y-%m-%d'),
        'time': appointment_datetime.strftime('%H:%M'),
        'vehicle_registration': 'XY98 ZAB'
    }
    
    booking_reminder = BookingReminder.objects.create(
        email='test@example.com',
        booking_details=booking_details,
        appointment_datetime=appointment_datetime,
        booking_url='https://www.access-auto-services.co.uk/booking',
        scheduled_for=reminder_time
    )
    
    print(f"Created booking reminder: {booking_reminder.id}")
    print(f"  Email: {booking_reminder.email}")
    print(f"  Appointment: {booking_reminder.appointment_datetime}")
    print(f"  Scheduled for: {booking_reminder.scheduled_for}")
    print(f"  Sent: {booking_reminder.reminder_sent}")
    print()
    
    return booking_reminder

def test_paypal_configuration():
    """Test PayPal configuration"""
    print("=== Testing PayPal Configuration ===")
    
    from django.conf import settings
    
    print(f"PayPal Client ID: {'Set' if settings.PAYPAL_CLIENT_ID else 'Not Set'}")
    print(f"PayPal Secret: {'Set' if settings.PAYPAL_SECRET else 'Not Set'}")
    print(f"PayPal API Base: {settings.PAYPAL_API_BASE}")
    print()
    
    # Test PayPal API connection (if credentials are set)
    if settings.PAYPAL_CLIENT_ID and settings.PAYPAL_SECRET:
        try:
            from PAYPAL.paypal_utils import paypal_api
            token = paypal_api.get_access_token()
            print(f"PayPal API Connection: {'Success' if token else 'Failed'}")
        except Exception as e:
            print(f"PayPal API Connection: Failed - {e}")
    else:
        print("PayPal API Connection: Skipped (credentials not set)")
    print()

def main():
    """Run all tests"""
    print("Starting Booking System Tests...\n")
    
    try:
        test_services()
        test_booking_creation()
        test_email_verification()
        test_booking_reminder()
        test_paypal_configuration()
        
        print("=== Test Summary ===")
        print("All tests completed successfully!")
        
        # Show counts
        print(f"Total Services: {Service.objects.count()}")
        print(f"Total Bookings: {Booking.objects.count()}")
        print(f"Total Email Verifications: {EmailVerification.objects.count()}")
        print(f"Total Booking Reminders: {BookingReminder.objects.count()}")
        
    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()