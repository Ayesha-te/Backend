#!/usr/bin/env python
import os
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.core.mail import send_mail

def test_dual_email_sending():
    """Test sending emails to both customer and owner"""
    
    print("=== Testing Dual Email Sending ===")
    print(f"Owner Email: {settings.OWNER_EMAIL}")
    print(f"Default From Email: {settings.DEFAULT_FROM_EMAIL}")
    
    # Test customer email
    customer_email = "customer@example.com"  # This would be the actual customer email
    
    # Build recipient list (customer + owner)
    recipient_list = [customer_email]
    owner_email = settings.OWNER_EMAIL
    if owner_email and owner_email not in recipient_list:
        recipient_list.append(owner_email)
    
    print(f"Recipients: {recipient_list}")
    
    try:
        result = send_mail(
            subject='Test Booking Confirmation - Access Auto Services',
            message=(
                "Dear Customer,\n\n"
                "Your booking has been successfully created!\n\n"
                "BOOKING DETAILS:\n"
                "=" * 50 + "\n"
                "Service: MOT Test\n"
                "Date: Monday, January 15, 2024\n"
                "Time: 10:00\n"
                "Vehicle: Ford Focus (ABC123)\n"
                "Amount: £54.85\n\n"
                "CUSTOMER INFORMATION:\n"
                "=" * 50 + "\n"
                "Customer: John Doe\n"
                "Phone: 07123456789\n"
                "Email: customer@example.com\n\n"
                "NEXT STEPS:\n"
                "=" * 50 + "\n"
                "• You will receive a reminder email 24 hours before your appointment\n"
                "• If you need to reschedule or cancel, please contact us as soon as possible\n\n"
                "CONTACT INFORMATION:\n"
                "=" * 50 + "\n"
                "Access Auto Services\n"
                f"Email: {settings.DEFAULT_FROM_EMAIL}\n"
                "Website: https://www.access-auto-services.co.uk\n\n"
                "Thank you for choosing Access Auto Services!\n\n"
                "Best regards,\n"
                "The Access Auto Services Team"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipient_list,
            fail_silently=False,
        )
        
        if result:
            print(f"✅ Booking confirmation email sent successfully to {len(recipient_list)} recipients!")
            print(f"   - Customer: {customer_email}")
            print(f"   - Owner: {owner_email}")
            return True
        else:
            print("❌ Email failed to send")
            return False
            
    except Exception as e:
        print(f"❌ Email sending error: {e}")
        return False

if __name__ == "__main__":
    print("Testing dual email functionality...\n")
    success = test_dual_email_sending()
    
    if success:
        print("\n✅ Dual email system is working correctly!")
        print("Both customer and owner will receive booking notifications.")
    else:
        print("\n❌ There was an issue with the dual email system.")
    
    print("\n=== Test Complete ===")