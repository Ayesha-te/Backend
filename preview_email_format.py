#!/usr/bin/env python
import os
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from PAYPAL.models import Booking
from datetime import datetime

def preview_email_formats():
    """Preview the new email formats"""
    
    print("=== Email Format Preview ===\n")
    
    # Get a recent booking to show the format
    try:
        booking = Booking.objects.last()
        if not booking:
            print("No bookings found to preview")
            return
            
        customer_email = booking.customer_email or "customer@example.com"
        
        # Get customer name - prefer customer data, fallback to user data
        customer_name = booking.customer_first_name
        if not customer_name and booking.user:
            customer_name = booking.user.first_name or booking.user.username
        if not customer_name:
            customer_name = 'Customer'
        
        # Build vehicle information
        vehicle_info = ""
        if booking.vehicle_make or booking.vehicle_model or booking.vehicle_registration:
            vehicle_parts = []
            if booking.vehicle_make:
                vehicle_parts.append(booking.vehicle_make)
            if booking.vehicle_model:
                vehicle_parts.append(booking.vehicle_model)
            if booking.vehicle_year:
                vehicle_parts.append(f"({booking.vehicle_year})")
            
            vehicle_info = " ".join(vehicle_parts)
            if booking.vehicle_registration:
                vehicle_info += f" - {booking.vehicle_registration}"
            
            if booking.vehicle_mileage:
                vehicle_info += f" - {booking.vehicle_mileage} miles"
        else:
            vehicle_info = "Not specified"
        
        # Build MOT class information
        mot_info = ""
        if booking.mot_class:
            mot_info = f"MOT Class: {booking.mot_class}\n"
        
        # Build customer information section
        customer_info = ""
        if booking.customer_first_name or booking.customer_last_name:
            full_name = f"{booking.customer_first_name or ''} {booking.customer_last_name or ''}".strip()
            if full_name:
                customer_info += f"Customer: {full_name}\n"
        elif booking.user:
            user_name = f"{booking.user.first_name or ''} {booking.user.last_name or ''}".strip()
            if user_name:
                customer_info += f"Customer: {user_name}\n"
            else:
                customer_info += f"Customer: {booking.user.username}\n"
        
        if booking.customer_phone:
            customer_info += f"Phone: {booking.customer_phone}\n"
        
        if booking.customer_address:
            customer_info += f"Address: {booking.customer_address}\n"
        
        # Build payment information
        payment_info = ""
        if booking.payment_amount:
            payment_info = f"Amount: £{booking.payment_amount}"
            if booking.payment_currency and booking.payment_currency != 'GBP':
                payment_info = f"Amount: {booking.payment_amount} {booking.payment_currency}"
        else:
            # Fallback to service price
            payment_info = f"Amount: £{booking.service.price}"
        
        print("📧 BOOKING CONFIRMATION EMAIL PREVIEW:")
        print("=" * 80)
        print(f"Subject: Booking Confirmation - Access Auto Services")
        print(f"To: {customer_email}")
        print(f"From: {settings.DEFAULT_FROM_EMAIL}")
        print("-" * 80)
        
        confirmation_message = (
            f"Dear {customer_name},\n\n"
            f"Your booking has been successfully created!\n\n"
            f"BOOKING DETAILS:\n"
            f"{'='*50}\n"
            f"Service: {booking.service.name}\n"
            f"{mot_info}"
            f"Date: {booking.date.strftime('%A, %B %d, %Y')}\n"
            f"Time: {booking.time}\n"
            f"Vehicle: {vehicle_info}\n"
            f"{payment_info}\n\n"
            f"CUSTOMER INFORMATION:\n"
            f"{'='*50}\n"
            f"{customer_info}"
            f"Email: {customer_email}\n\n"
            f"NEXT STEPS:\n"
            f"{'='*50}\n"
           
            f"• You will receive a reminder email 24 hours before your appointment\n"
            f"• If you need to reschedule or cancel, please contact us as soon as possible\n\n"
            f"CONTACT INFORMATION:\n"
            f"{'='*50}\n"
            f"Access Auto Services\n"
            f"Email: {settings.DEFAULT_FROM_EMAIL}\n"
            f"Website: https://www.access-auto-services.co.uk\n\n"
            f"Thank you for choosing Access Auto Services!\n\n"
            f"Best regards,\n"
            f"The Access Auto Services Team"
        )
        
        print(confirmation_message)
        print("=" * 80)
        
        # Preview reminder email format
        print("\n📧 BOOKING REMINDER EMAIL PREVIEW:")
        print("=" * 80)
        print(f"Subject: Appointment Reminder - Access Auto Services")
        print(f"To: {customer_email}")
        print(f"From: {settings.DEFAULT_FROM_EMAIL}")
        print("-" * 80)
        
        booking_details = {
            'service_name': booking.service.name,
            'mot_class': booking.mot_class if booking.mot_class else None,
            'price': float(booking.payment_amount) if booking.payment_amount else float(booking.service.price),
            'date': str(booking.date),
            'time': booking.time,
            'vehicle_registration': booking.vehicle_registration
        }
        
        # Format booking details
        booking_summary = f"{'='*50}\n"
        booking_summary += f"Service: {booking_details.get('service_name', 'N/A')}\n"
        if booking_details.get('mot_class'):
            booking_summary += f"MOT Class: {booking_details.get('mot_class')}\n"
        booking_summary += f"Date: {booking_details.get('date', 'N/A')}\n"
        booking_summary += f"Time: {booking_details.get('time', 'N/A')}\n"
        if booking_details.get('vehicle_registration'):
            booking_summary += f"Vehicle Registration: {booking_details.get('vehicle_registration')}\n"
        booking_summary += f"Price: £{booking_details.get('price', 0)}\n"
        booking_summary += f"{'='*50}\n"
        
        reminder_message = f"""Dear Customer,

This is a friendly reminder about your upcoming appointment with Access Auto Services.

APPOINTMENT DETAILS:
{booking_summary}

IMPORTANT REMINDERS:
• Please arrive 10 minutes before your scheduled time
• Bring your vehicle registration documents
• Ensure your vehicle is accessible and ready for service
• If you need to reschedule, please contact us at least 24 hours in advance

CONTACT INFORMATION:
Access Auto Services
Email: {settings.DEFAULT_FROM_EMAIL}
Website: https://www.access-auto-services.co.uk

We look forward to seeing you!

Best regards,
The Access Auto Services Team"""
        
        print(reminder_message)
        print("=" * 80)
        
    except Exception as e:
        print(f"Error previewing email formats: {e}")

if __name__ == "__main__":
    preview_email_formats()