#!/usr/bin/env python
"""
Test script to verify PayPal integration with frontend data structure
"""
import os
import sys
import django
import json
from datetime import datetime, date

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from PAYPAL.models import Service, Booking
from PAYPAL.paypal_utils import paypal_api

def test_paypal_integration():
    """Test PayPal integration with frontend-like data"""
    
    print("=== PayPal Integration Test ===")
    
    # 1. Test PayPal API connection
    print("\n1. Testing PayPal API connection...")
    try:
        token = paypal_api.get_access_token()
        if token:
            print("✅ PayPal API connection successful")
        else:
            print("❌ PayPal API connection failed - no token received")
            return False
    except Exception as e:
        print(f"❌ PayPal API connection failed: {e}")
        return False
    
    # 2. Test booking creation with PayPal payment method
    print("\n2. Testing booking creation with PayPal payment method...")
    
    # Create a test service if it doesn't exist
    service, created = Service.objects.get_or_create(
        code='MOT_TEST',
        defaults={
            'name': 'MOT Test',
            'description': 'Annual MOT Test',
            'price': 54.85,
            'active': True
        }
    )
    
    if created:
        print(f"✅ Created test service: {service.name}")
    else:
        print(f"✅ Using existing service: {service.name}")
    
    # Frontend-like data structure
    frontend_data = {
        'service_id': service.id,
        'date': '2024-01-15',
        'time': '10:00',
        'motClass': 'Class 4',
        'price': 54.85,
        'quantity': 1,
        'vehicle': {
            'make': 'Toyota',
            'model': 'Corolla',
            'year': '2018',
            'registration': 'AB18 XYZ',
            'mileage': '45000'
        },
        'customer': {
            'firstName': 'John',
            'lastName': 'Doe',
            'email': 'john.doe@example.com',
            'phone': '07123456789',
            'address': '123 Test Street, Test City, TE1 2ST'
        },
        'payment': {
            'method': 'paypal',
            'cardNumber': '',      # Empty for PayPal
            'expiryDate': '',      # Empty for PayPal
            'cvv': '',             # Empty for PayPal
            'nameOnCard': ''       # Empty for PayPal
        }
    }
    
    try:
        # Create booking with PayPal payment method
        booking = Booking.objects.create(
            service=service,
            mot_class=frontend_data['motClass'],
            date=datetime.strptime(frontend_data['date'], '%Y-%m-%d').date(),
            time=frontend_data['time'],
            vehicle_make=frontend_data['vehicle']['make'],
            vehicle_model=frontend_data['vehicle']['model'],
            vehicle_year=frontend_data['vehicle']['year'],
            vehicle_registration=frontend_data['vehicle']['registration'],
            vehicle_mileage=frontend_data['vehicle']['mileage'],
            customer_first_name=frontend_data['customer']['firstName'],
            customer_last_name=frontend_data['customer']['lastName'],
            customer_email=frontend_data['customer']['email'],
            customer_phone=frontend_data['customer']['phone'],
            customer_address=frontend_data['customer']['address'],
            payment_method=frontend_data['payment']['method'],
            card_number=frontend_data['payment']['cardNumber'],
            expiry_date=frontend_data['payment']['expiryDate'],
            cvv=frontend_data['payment']['cvv'],
            name_on_card=frontend_data['payment']['nameOnCard'],
            payment_amount=frontend_data['price'] * frontend_data['quantity'],
            payment_currency='GBP'
        )
        
        print(f"✅ Booking created successfully: ID {booking.id}")
        print(f"   Payment method: {booking.payment_method}")
        print(f"   Payment amount: £{booking.payment_amount}")
        print(f"   Card fields empty: {not any([booking.card_number, booking.expiry_date, booking.cvv, booking.name_on_card])}")
        
    except Exception as e:
        print(f"❌ Booking creation failed: {e}")
        return False
    
    # 3. Test PayPal order creation
    print("\n3. Testing PayPal order creation...")
    try:
        amount = float(booking.payment_amount)
        description = f"Booking for {booking.service.name} on {booking.date}"
        
        order = paypal_api.create_order(
            amount=amount,
            currency=booking.payment_currency,
            description=description,
            custom_id=booking.id
        )
        
        if order and order.get('id'):
            print(f"✅ PayPal order created successfully: {order.get('id')}")
            print(f"   Amount: {amount} {booking.payment_currency}")
            print(f"   Status: {order.get('status', 'Unknown')}")
            
            # Update booking with PayPal order ID
            booking.paypal_order_id = order.get('id')
            booking.payment_status = 'created'
            booking.save()
            
            print(f"✅ Booking updated with PayPal order ID")
            
        else:
            print("❌ PayPal order creation failed - no order ID received")
            return False
            
    except Exception as e:
        print(f"❌ PayPal order creation failed: {e}")
        return False
    
    # 4. Test order details retrieval
    print("\n4. Testing PayPal order details retrieval...")
    try:
        order_details = paypal_api.get_order_details(booking.paypal_order_id)
        
        if order_details:
            print(f"✅ PayPal order details retrieved successfully")
            print(f"   Order ID: {order_details.get('id')}")
            print(f"   Status: {order_details.get('status')}")
            print(f"   Intent: {order_details.get('intent')}")
            
            # Check if order has approval links
            links = order_details.get('links', [])
            approve_link = next((link['href'] for link in links if link['rel'] == 'approve'), None)
            if approve_link:
                print(f"   Approval URL available: {approve_link[:50]}...")
            
        else:
            print("❌ PayPal order details retrieval failed")
            return False
            
    except Exception as e:
        print(f"❌ PayPal order details retrieval failed: {e}")
        return False
    
    print("\n=== Test Summary ===")
    print("✅ All PayPal integration tests passed!")
    print(f"✅ Test booking ID: {booking.id}")
    print(f"✅ PayPal order ID: {booking.paypal_order_id}")
    print("\nThe backend is ready to handle PayPal payments from the frontend.")
    print("\nFrontend should:")
    print("1. Create booking with payment.method = 'paypal'")
    print("2. Call /create-order/ API with booking_id and customer_email")
    print("3. Use returned order_id to initialize PayPal checkout")
    print("4. Call /capture-payment/ API after user approves payment")
    
    # Clean up test data
    print(f"\n🧹 Cleaning up test booking {booking.id}...")
    booking.delete()
    print("✅ Test data cleaned up")
    
    return True

if __name__ == '__main__':
    success = test_paypal_integration()
    sys.exit(0 if success else 1)