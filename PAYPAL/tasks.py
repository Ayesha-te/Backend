from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from .models import Booking

@shared_task
def send_booking_reminder(booking_id):
    try:
        booking = Booking.objects.get(id=booking_id)
        # Prefer user.email, fallback to customer_email
        email_to = booking.user.email if booking.user and booking.user.email else booking.customer_email
        
        if not email_to:
            # No valid email to send to, skip sending email
            return
        
        # Compose message using customer name if available, else user info
        recipient_name = booking.customer_first_name or (booking.user.first_name if booking.user else '') or (booking.user.username if booking.user else 'Customer')
        
        send_mail(
            subject='Booking Reminder',
            message=(
                f"Hi {recipient_name},\n\n"
                f"This is a reminder that your booking for {booking.service.name} "
                f"is scheduled at {booking.date} {booking.time}.\n\n"
                "See you soon!"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email_to],
            fail_silently=False,
        )
    except Booking.DoesNotExist:
        # Booking not found, silently ignore or log if needed
        pass
