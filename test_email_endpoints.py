#!/usr/bin/env python
"""
Test email service endpoints
"""
import os
import sys
import django
from pathlib import Path
import requests
import json

# Add the project directory to Python path
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.test import Client
from django.urls import reverse
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_email_verification_endpoint():
    """Test email verification endpoint"""
    print("=" * 50)
    print("Testing Email Verification Endpoint")
    print("=" * 50)
    
    client = Client()
    
    # Test data
    test_data = {
        'email': 'test@example.com',
        'booking_details': {
            'service_name': 'MOT Test',
            'price': 50.00,
            'date': '2024-01-15',
            'time': '10:00'
        },
        'booking_url': 'https://www.access-auto-services.co.uk/booking'
    }
    
    try:
        response = client.post(
            '/api/email/verification/',
            data=json.dumps(test_data),
            content_type='application/json'
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json() if response.content else 'No content'}")
        
        if response.status_code == 201:
            print("✅ Email verification endpoint working!")
            return True
        elif response.status_code == 401:
            print("❌ Still getting 401 - authentication required")
            return False
        else:
            print(f"❌ Unexpected status code: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing email verification: {e}")
        return False

def test_booking_reminder_endpoint():
    """Test booking reminder endpoint"""
    print("\n" + "=" * 50)
    print("Testing Booking Reminder Endpoint")
    print("=" * 50)
    
    client = Client()
    
    # Test data
    test_data = {
        'email': 'test@example.com',
        'appointment_datetime': '2024-01-15T10:00:00Z',
        'booking_details': {
            'service_name': 'MOT Test',
            'price': 50.00,
            'date': '2024-01-15',
            'time': '10:00'
        },
        'booking_url': 'https://www.access-auto-services.co.uk/booking'
    }
    
    try:
        response = client.post(
            '/api/email/reminder/',
            data=json.dumps(test_data),
            content_type='application/json'
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json() if response.content else 'No content'}")
        
        if response.status_code in [200, 201]:
            print("✅ Booking reminder endpoint working!")
            return True
        elif response.status_code == 401:
            print("❌ Still getting 401 - authentication required")
            return False
        else:
            print(f"❌ Unexpected status code: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing booking reminder: {e}")
        return False

def test_booking_detail_endpoint():
    """Test booking detail endpoint"""
    print("\n" + "=" * 50)
    print("Testing Booking Detail Endpoint")
    print("=" * 50)
    
    client = Client()
    
    try:
        # Test with a non-existent booking ID
        response = client.get('/api/paypal/bookings/999/?email=test@example.com')
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json() if response.content else 'No content'}")
        
        if response.status_code == 404:
            print("✅ Booking detail endpoint working (correctly returns 404 for non-existent booking)!")
            return True
        elif response.status_code == 401:
            print("❌ Still getting 401 - authentication required")
            return False
        else:
            print(f"❌ Unexpected status code: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing booking detail: {e}")
        return False

if __name__ == "__main__":
    print("Starting email endpoints test...\n")
    
    email_ok = test_email_verification_endpoint()
    reminder_ok = test_booking_reminder_endpoint()
    booking_ok = test_booking_detail_endpoint()
    
    print("\n" + "=" * 50)
    print("Test Summary:")
    print(f"Email Verification: {'✅ PASS' if email_ok else '❌ FAIL'}")
    print(f"Booking Reminder: {'✅ PASS' if reminder_ok else '❌ FAIL'}")
    print(f"Booking Detail: {'✅ PASS' if booking_ok else '❌ FAIL'}")
    print("=" * 50)