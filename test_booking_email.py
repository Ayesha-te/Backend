#!/usr/bin/env python
import os
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from PAYPAL.models import Service, Booking
from accounts.models import CustomUser
from datetime import datetime, timedelta
from django.utils import timezone
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def test_booking_creation_with_email():
    """Test creating a booking and verify email sending"""
    
    print("=== Testing Booking Creation with Email ===")
    
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
    
    # Get a service
    try:
        service = Service.objects.first()
        if not service:
            print("❌ No services found in database")
            return
        print(f"Using service: {service.name}")
    except Exception as e:
        print(f"❌ Error getting service: {e}")
        return
    
    # Create test booking data
    future_date = (timezone.now() + timedelta(days=3)).date()
    booking_data = {
        'user': user,
        'service': service,
        'date': future_date,
        'time': '14:00',
        'customer_first_name': 'Test',
        'customer_last_name': 'Customer',
        'customer_email': 'ayeshajahangir280@gmail.com',  # Use your email for testing
        'customer_phone': '1234567890',
        'customer_address': '123 Test Street',
        'vehicle_make': 'Toyota',
        'vehicle_model': 'Camry',
        'vehicle_year': '2020',
        'vehicle_registration': 'TEST123',
        'vehicle_mileage': '50000',
        'payment_method': 'card',
        'payment_amount': 50.00,
        'payment_currency': 'GBP',
        'is_verified': False,
        'verification_token': 'test_token_123'
    }
    
    print(f"Creating booking for {booking_data['customer_email']} on {future_date}")
    
    try:
        # Create the booking
        booking = Booking.objects.create(**booking_data)
        print(f"✅ Booking created successfully with ID: {booking.id}")
        
        # Now manually trigger the email sending logic
        from PAYPAL.views import BookingListCreateAPIView
        from django.core.mail import send_mail
        from email_service.models import EmailVerification, BookingReminder
        
        customer_email = booking.customer_email
        quantity = 1  # Default quantity
        
        print(f"\n=== Testing Email Sending Logic ===")
        
        # Test immediate confirmation email
        try:
            print(f"Sending immediate confirmation email to {customer_email}")
            email_result = send_mail(
                subject='Booking Confirmation - Access Auto Services',
                message=(
                    f"Dear {booking.customer_first_name or 'Customer'},\n\n"
                    f"Your booking has been successfully created!\n\n"
                    f"Booking Details:\n"
                    f"Service: {booking.service.name}\n"
                    f"Date: {booking.date}\n"
                    f"Time: {booking.time}\n"
                    f"Vehicle: {booking.vehicle_make} {booking.vehicle_model} ({booking.vehicle_registration})\n"
                    f"Amount: £{booking.payment_amount}\n\n"
                   
                    f"Thank you for choosing Access Auto Services!\n\n"
                    f"Best regards,\nThe Access Auto Services Team"
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[customer_email],
                fail_silently=False,
            )
            
            if email_result:
                print(f"✅ Immediate confirmation email sent successfully")
            else:
                print(f"❌ Immediate confirmation email failed (result: {email_result})")
                
        except Exception as email_error:
            print(f"❌ Error sending immediate confirmation email: {email_error}")
        
        # Email verification removed as requested - only booking confirmation is sent
        
        # Test booking reminder creation
        try:
            print(f"Creating booking reminder for {customer_email}")
            booking_datetime = datetime.combine(booking.date, datetime.strptime(booking.time, '%H:%M').time())
            booking_datetime = timezone.make_aware(booking_datetime)
            reminder_time = booking_datetime - timedelta(hours=24)
            
            print(f"Booking datetime: {booking_datetime}")
            print(f"Reminder time: {reminder_time}")
            print(f"Current time: {timezone.now()}")
            
            if reminder_time > timezone.now():
                booking_details = {
                    'service_name': booking.service.name,
                    'mot_class': booking.mot_class if booking.mot_class else None,
                    'price': float(booking.payment_amount) if booking.payment_amount else 0,
                    'quantity': quantity,
                    'date': str(booking.date),
                    'time': booking.time,
                    'vehicle_registration': booking.vehicle_registration
                }
                
                booking_reminder = BookingReminder.objects.create(
                    email=customer_email,
                    booking_details=booking_details,
                    appointment_datetime=booking_datetime,
                    booking_url=f"https://www.access-auto-services.co.uk/booking",
                    scheduled_for=reminder_time
                )
                print(f"✅ Booking reminder created with ID: {booking_reminder.id}")
            else:
                print(f"⚠️ Booking is too soon for reminder scheduling")
                
        except Exception as reminder_error:
            print(f"❌ Error creating booking reminder: {reminder_error}")
        
        print(f"\n=== Test Complete ===")
        print(f"Booking ID: {booking.id}")
        print(f"Customer Email: {customer_email}")
        print(f"Check your email inbox for booking confirmation email")
        
    except Exception as e:
        print(f"❌ Error creating booking: {e}")

if __name__ == "__main__":
    test_booking_creation_with_email()