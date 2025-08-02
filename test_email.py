#!/usr/bin/env python
import os
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.core.mail import send_mail
from django.core.mail import get_connection
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def test_email_configuration():
    """Test email configuration and send a test email"""
    
    print("=== Email Configuration Test ===")
    print(f"EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
    print(f"EMAIL_HOST: {settings.EMAIL_HOST}")
    print(f"EMAIL_PORT: {settings.EMAIL_PORT}")
    print(f"EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
    print(f"EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
    print(f"DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
    print(f"EMAIL_HOST_PASSWORD: {'*' * len(settings.EMAIL_HOST_PASSWORD) if settings.EMAIL_HOST_PASSWORD else 'Not set'}")
    
    # Test connection
    print("\n=== Testing Email Connection ===")
    try:
        connection = get_connection()
        connection.open()
        print("✅ Email connection successful!")
        connection.close()
    except Exception as e:
        print(f"❌ Email connection failed: {e}")
        return False
    
    # Send test email
    print("\n=== Sending Test Email ===")
    try:
        result = send_mail(
            subject='Test Email - Access Auto Services',
            message='This is a test email to verify email configuration is working.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.EMAIL_HOST_USER],  # Send to self for testing
            fail_silently=False,
        )
        
        if result:
            print("✅ Test email sent successfully!")
            return True
        else:
            print("❌ Test email failed to send (no exception but result was 0)")
            return False
            
    except Exception as e:
        print(f"❌ Test email failed: {e}")
        return False

def test_booking_email_flow():
    """Test the booking email flow"""
    print("\n=== Testing Booking Email Flow ===")
    
    # Test data
    test_email = "ayeshajahangir280@gmail.com"
    
    try:
        # Test immediate confirmation email
        result = send_mail(
            subject='Booking Confirmation - Access Auto Services',
            message=(
                "Dear Customer,\n\n"
                "Your booking has been successfully created!\n\n"
                "Booking Details:\n"
                "Service: Test Service\n"
                "Date: 2024-01-15\n"
                "Time: 10:00\n"
                "Vehicle: Test Vehicle (ABC123)\n"
                "Amount: £50.00\n\n"
                
                "Thank you for choosing Access Auto Services!\n\n"
                "Best regards,\nThe Access Auto Services Team"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[test_email],
            fail_silently=False,
        )
        
        if result:
            print("✅ Booking confirmation email sent successfully!")
        else:
            print("❌ Booking confirmation email failed")
            
    except Exception as e:
        print(f"❌ Booking confirmation email error: {e}")
    
    try:
        # Test verification email
        verification_url = "https://www.access-auto-services.co.uk/booking?verify=test_token"
        result = send_mail(
            subject='Email Verification - Access Auto Services',
            message=(
                "Dear Customer,\n\n"
                "Please verify your email address to complete your booking:\n\n"
                "Booking Details:\n"
                "Service: Test Service\n"
                "Date: 2024-01-15 at 10:00\n"
                "Amount: £50.00\n\n"
                f"Click here to verify: {verification_url}\n\n"
                "Best regards,\nAccess Auto Services Team"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[test_email],
            fail_silently=False,
        )
        
        if result:
            print("✅ Email verification sent successfully!")
        else:
            print("❌ Email verification failed")
            
    except Exception as e:
        print(f"❌ Email verification error: {e}")

if __name__ == "__main__":
    print("Starting email diagnostics...\n")
    
    # Test basic email configuration
    config_ok = test_email_configuration()
    
    if config_ok:
        # Test booking email flow
        test_booking_email_flow()
    else:
        print("\n❌ Email configuration issues detected. Please fix configuration before testing booking emails.")
    
    print("\n=== Email Diagnostics Complete ===")