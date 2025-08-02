try:
    from celery import shared_task
    CELERY_AVAILABLE = True
except ImportError:
    CELERY_AVAILABLE = False
    # Create a dummy decorator when Celery is not available
    def shared_task(func):
        return func

import logging
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from .models import BookingReminder

logger = logging.getLogger(__name__)

@shared_task
def send_reminder_email_task(reminder_id):
    """
    Celery task to send booking reminder emails
    """
    try:
        booking_reminder = BookingReminder.objects.get(id=reminder_id)
        
        # Check if reminder was already sent
        if booking_reminder.reminder_sent:
            logger.info(f"Reminder {reminder_id} already sent, skipping")
            return
        
        # Format booking details for email
        booking_details = booking_reminder.booking_details
        booking_summary = format_booking_details(booking_details)
        
        subject = "Appointment Reminder - Access Auto Services"
        message = f"""Dear Customer,

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
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[booking_reminder.email],
            fail_silently=False,
        )
        
        # Mark as sent
        booking_reminder.reminder_sent = True
        booking_reminder.sent_at = timezone.now()
        booking_reminder.save()
        
        logger.info(f"Reminder email sent successfully to {booking_reminder.email}")
        
    except BookingReminder.DoesNotExist:
        logger.error(f"BookingReminder {reminder_id} not found")
    except Exception as e:
        logger.error(f"Error sending reminder email for {reminder_id}: {e}")
        raise

def format_booking_details(booking_details):
    """Format booking details for email display"""
    formatted = ""
    
    if isinstance(booking_details, list):
        for i, booking in enumerate(booking_details, 1):
            formatted += f"\nService {i}:\n"
            formatted += f"{'='*30}\n"
            formatted += f"Service: {booking.get('service_name', 'N/A')}\n"
            if booking.get('mot_class'):
                formatted += f"MOT Class: {booking.get('mot_class')}\n"
            formatted += f"Date: {booking.get('date', 'N/A')}\n"
            formatted += f"Time: {booking.get('time', 'N/A')}\n"
            if booking.get('vehicle_registration'):
                formatted += f"Vehicle Registration: {booking.get('vehicle_registration')}\n"
            formatted += f"Price: £{booking.get('price', 0)}\n"
            formatted += "\n"
    else:
        # Single booking
        formatted += f"{'='*50}\n"
        formatted += f"Service: {booking_details.get('service_name', 'N/A')}\n"
        if booking_details.get('mot_class'):
            formatted += f"MOT Class: {booking_details.get('mot_class')}\n"
        formatted += f"Date: {booking_details.get('date', 'N/A')}\n"
        formatted += f"Time: {booking_details.get('time', 'N/A')}\n"
        if booking_details.get('vehicle_registration'):
            formatted += f"Vehicle Registration: {booking_details.get('vehicle_registration')}\n"
        formatted += f"Price: £{booking_details.get('price', 0)}\n"
        formatted += f"{'='*50}\n"
    
    return formatted

# Synchronous version for when Celery is not available
def send_reminder_email_sync(reminder_id):
    """
    Synchronous version of send_reminder_email_task for when Celery is not available
    """
    return send_reminder_email_task(reminder_id)