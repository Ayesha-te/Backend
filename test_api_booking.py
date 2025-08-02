#!/usr/bin/env python
import os
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from rest_framework.test import APIClient
from rest_framework import status
from accounts.models import CustomUser
from PAYPAL.models import Service
from datetime import datetime, timedelta
from django.utils import timezone
import json

# Add testserver to ALLOWED_HOSTS for testing
if 'testserver' not in settings.ALLOWED_HOSTS:
    settings.ALLOWED_HOSTS.append('testserver')

def test_booking_api_with_email():
    """Test booking creation through API and verify email sending"""
    
    print("=== Testing Booking API with Email ===")
    
    # Create API client
    client = APIClient()
    
    # Get or create a test user
    try:
        user = CustomUser.objects.get(email='test@example.com')
        print(f"Using existing user: {user.email}")
    except CustomUser.DoesNotExist:
        user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        print(f"Created new user: {user.email}")
    
    # Authenticate the user
    client.force_authenticate(user=user)
    
    # Get a service
    try:
        service = Service.objects.first()
        if not service:
            print("❌ No services found in database")
            return
        print(f"Using service: {service.name} (ID: {service.id})")
    except Exception as e:
        print(f"❌ Error getting service: {e}")
        return
    
    # Create booking data
    future_date = (timezone.now() + timedelta(days=2)).date()
    booking_data = {
        'service_id': service.id,
        'date': future_date.strftime('%Y-%m-%d'),
        'time': '15:30',
        'motClass': 'Class 4',
        'quantity': 1,
        'price': 45.00,
        'vehicle': {
            'make': 'Honda',
            'model': 'Civic',
            'year': '2019',
            'registration': 'API123',
            'mileage': '45000'
        },
        'customer': {
            'firstName': 'API',
            'lastName': 'Test',
            'email': 'ayeshajahangir280@gmail.com',  # Your email for testing
            'phone': '0987654321',
            'address': '456 API Street, Test City'
        },
        'payment': {
            'method': 'card',
            'cardNumber': '4111111111111111',
            'expiryDate': '12/25',
            'cvv': '123',
            'nameOnCard': 'API Test'
        }
    }
    
    print(f"Creating booking through API for {booking_data['customer']['email']} on {future_date}")
    
    try:
        # Make API request to create booking
        response = client.post('/api/paypal/bookings/', data=booking_data, format='json')
        
        print(f"API Response Status: {response.status_code}")
        
        if hasattr(response, 'data'):
            print(f"API Response Data: {response.data}")
            
            if response.status_code == status.HTTP_201_CREATED:
                print("✅ Booking created successfully through API")
                print("✅ Check your email for booking confirmation")
                
                # Get the created booking ID if available
                if 'id' in response.data:
                    booking_id = response.data['id']
                    print(f"Booking ID: {booking_id}")
            else:
                print(f"❌ Booking creation failed: {response.data}")
        else:
            print(f"API Response Content: {response.content.decode()}")
            if response.status_code == status.HTTP_201_CREATED:
                print("✅ Booking created successfully through API")
                print("✅ Check your email for booking confirmation")
            else:
                print(f"❌ Booking creation failed with status {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error making API request: {e}")

if __name__ == "__main__":
    test_booking_api_with_email()