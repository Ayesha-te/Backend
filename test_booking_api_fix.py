#!/usr/bin/env python
import os
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth import get_user_model
from PAYPAL.views import BookingListCreateAPIView
from PAYPAL.models import Service, Booking
import json

User = get_user_model()

def test_booking_api():
    """Test the booking API to ensure it doesn't timeout"""
    
    print("=== Booking API Test ===")
    
    # Create or get a test user
    try:
        user = User.objects.get(email='test@example.com')
        print(f"Using existing test user: {user.email}")
    except User.DoesNotExist:
        user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        print(f"Created test user: {user.email}")
    
    # Create or get a test service
    try:
        service = Service.objects.get(code='MOT_TEST')
    except Service.DoesNotExist:
        service = Service.objects.create(
            code='MOT_TEST',
            name='MOT Test',
            description='Standard MOT Test',
            price=45.00,
            active=True
        )
        print(f"Created test service: {service.name}")
    
    # Test GET request (list bookings)
    print("\n--- Testing GET /api/paypal/bookings/ ---")
    
    factory = RequestFactory()
    request = factory.get('/api/paypal/bookings/')
    request.user = user
    
    view = BookingListCreateAPIView()
    view.request = request
    
    try:
        queryset = view.get_queryset()
        print(f"✅ GET request successful - Found {queryset.count()} bookings for user")
    except Exception as e:
        print(f"❌ GET request failed: {e}")
    
    # Test POST request (create booking) - simulate the data structure
    print("\n--- Testing POST /api/paypal/bookings/ ---")
    
    booking_data = {
        'service_id': service.id,
        'motClass': 'MOT IV',
        'date': '2025-08-15',
        'time': '14:30',
        'vehicle': {
            'make': 'Toyota',
            'model': 'Corolla',
            'year': '2020',
            'registration': 'AB12 CDE',
            'mileage': '50000'
        },
        'customer': {
            'firstName': 'Test',
            'lastName': 'Customer',
            'email': 'test@example.com',
            'phone': '01234567890',
            'address': 'Test Address'
        },
        'payment': {
            'method': 'cash',
            'cardNumber': '',
            'expiryDate': '',
            'cvv': '',
            'nameOnCard': ''
        },
        'quantity': 1,
        'price': 45
    }
    
    request = factory.post(
        '/api/paypal/bookings/',
        data=json.dumps(booking_data),
        content_type='application/json'
    )
    request.user = user
    
    view = BookingListCreateAPIView()
    view.request = request
    
    try:
        # This should not timeout anymore
        print("Creating booking...")
        response = view.create(request)
        print(f"✅ POST request successful - Status: {response.status_code}")
        if hasattr(response, 'data'):
            print(f"Response data: {response.data}")
    except Exception as e:
        print(f"❌ POST request failed: {e}")
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    test_booking_api()