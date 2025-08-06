#!/usr/bin/env python
import os
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.core.mail import send_mail
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_email_configuration():
    """Test email configuration and sending"""
    
    print("=== Email Configuration Test ===")
    
    # Print current email settings
    print(f"EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
    print(f"EMAIL_HOST: {settings.EMAIL_HOST}")
    print(f"EMAIL_PORT: {settings.EMAIL_PORT}")
    print(f"EMAIL_USE_TLS: {getattr(settings, 'EMAIL_USE_TLS', 'Not set')}")
    print(f"EMAIL_USE_SSL: {getattr(settings, 'EMAIL_USE_SSL', 'Not set')}")
    print(f"EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
    print(f"DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
    print(f"OWNER_EMAIL: {settings.OWNER_EMAIL}")
    
    # Test email sending
    print("\n=== Testing Email Send ===")
    
    try:
        result = send_mail(
            subject='Test Email - Access Auto Services',
            message='This is a test email to verify email configuration.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.OWNER_EMAIL],
            fail_silently=False,
        )
        
        if result:
            print("✅ Email sent successfully!")
        else:
            print("❌ Email sending failed (result: 0)")
            
    except Exception as e:
        print(f"❌ Email sending failed with error: {e}")
        
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    test_email_configuration()