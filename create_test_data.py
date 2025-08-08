#!/usr/bin/env python
import os
import sys
import django
from decimal import Decimal

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from PAYPAL.models import Service as PayPalService, Booking as PayPalBooking

User = get_user_model()

def create_test_data():
    print("Creating test data...")
    
    # Create test users
    users_data = [
        {
            'email': 'john.doe@example.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'password': 'testpass123'
        },
        {
            'email': 'jane.smith@example.com',
            'first_name': 'Jane',
            'last_name': 'Smith',
            'password': 'testpass123'
        },
        {
            'email': 'admin@accessauto.com',
            'first_name': 'Admin',
            'last_name': 'User',
            'password': 'admin123',
            'is_staff': True,
            'is_superuser': True
        }
    ]
    
    created_users = []
    for user_data in users_data:
        user, created = User.objects.get_or_create(
            email=user_data['email'],
            defaults=user_data
        )
        if created:
            user.set_password(user_data['password'])
            if 'is_staff' in user_data:
                user.is_staff = user_data['is_staff']
            if 'is_superuser' in user_data:
                user.is_superuser = user_data['is_superuser']
            user.save()
            print(f"Created user: {user.email}")
        else:
            print(f"User already exists: {user.email}")
        created_users.append(user)
    
    # Create test services
    services_data = [
        {
            'code': 'MOT_TEST',
            'name': 'MOT Test',
            'description': 'Annual MOT test for vehicles',
            'price': Decimal('54.85'),
            'active': True
        },
        {
            'code': 'FULL_SERVICE',
            'name': 'Full Service',
            'description': 'Complete vehicle service and inspection',
            'price': Decimal('150.00'),
            'active': True
        },
        {
            'code': 'OIL_CHANGE',
            'name': 'Oil Change',
            'description': 'Engine oil and filter change',
            'price': Decimal('45.00'),
            'active': True
        },
        {
            'code': 'BRAKE_CHECK',
            'name': 'Brake Check',
            'description': 'Comprehensive brake system inspection',
            'price': Decimal('25.00'),
            'active': False
        }
    ]
    
    created_services = []
    for service_data in services_data:
        service, created = PayPalService.objects.get_or_create(
            code=service_data['code'],
            defaults=service_data
        )
        if created:
            print(f"Created service: {service.name}")
        else:
            print(f"Service already exists: {service.name}")
        created_services.append(service)
    
    # Create test bookings
    bookings_data = [
        {
            'user': created_users[0],  # John Doe
            'service': created_services[0],  # MOT Test
            'customer_first_name': 'John',
            'customer_last_name': 'Doe',
            'customer_email': 'john.doe@example.com',
            'customer_phone': '+44 7123 456789',
            'customer_address': '123 Main Street, London, SW1A 1AA',
            'date': '2025-08-15',
            'time': '10:00',
            'payment_amount': Decimal('54.85'),
            'is_paid': True,
            'is_verified': True,
            'payment_status': 'completed'
        },
        {
            'user': created_users[1],  # Jane Smith
            'service': created_services[1],  # Full Service
            'customer_first_name': 'Jane',
            'customer_last_name': 'Smith',
            'customer_email': 'jane.smith@example.com',
            'customer_phone': '+44 7987 654321',
            'customer_address': '456 Oak Avenue, Manchester, M1 1AA',
            'date': '2025-08-20',
            'time': '14:30',
            'payment_amount': Decimal('150.00'),
            'is_paid': False,
            'is_verified': False,
            'payment_status': 'pending'
        },
        {
            'user': created_users[0],  # John Doe again
            'service': created_services[2],  # Oil Change
            'customer_first_name': 'John',
            'customer_last_name': 'Doe',
            'customer_email': 'john.doe@example.com',
            'customer_phone': '+44 7123 456789',
            'customer_address': '123 Main Street, London, SW1A 1AA',
            'date': '2025-08-25',
            'time': '09:00',
            'payment_amount': Decimal('45.00'),
            'is_paid': True,
            'is_verified': True,
            'payment_status': 'completed'
        }
    ]
    
    for booking_data in bookings_data:
        booking, created = PayPalBooking.objects.get_or_create(
            user=booking_data['user'],
            service=booking_data['service'],
            date=booking_data['date'],
            time=booking_data['time'],
            defaults=booking_data
        )
        if created:
            print(f"Created booking: {booking.customer_first_name} {booking.customer_last_name} - {booking.service.name}")
        else:
            print(f"Booking already exists: {booking.customer_first_name} {booking.customer_last_name} - {booking.service.name}")
    
    print("\nTest data creation completed!")
    print("\nYou can now access the admin panel at: http://127.0.0.1:8000/static/admin/")
    print("Admin login: admin@accessauto.com / admin123")

if __name__ == '__main__':
    create_test_data()