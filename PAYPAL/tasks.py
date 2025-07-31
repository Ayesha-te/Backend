from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from .models import Booking

@shared_task
def send_booking_reminder(booking_id):
    try:
        booking = Booking.objects.get(id=booking_id)
        user = booking.user
        send_mail(
            subject='Booking Reminder',
            message=(
                f"Hi {user.first_name or user.username},\n\n"
                f"This is a reminder that your booking for {booking.service.name} "
                f"is scheduled at {booking.date} {booking.time}.\n\n"
                "See you soon!"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
    except Booking.DoesNotExist:
        pass
