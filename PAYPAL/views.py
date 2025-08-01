from datetime import datetime, timedelta
import secrets

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone

from .models import Service, Booking
from .serializers import ServiceSerializer, BookingSerializer

# Import tasks with error handling
try:
    from .tasks import send_booking_reminder
except ImportError:
    # If Celery is not available, create a dummy function
    def send_booking_reminder(booking_id):
        pass


class ServiceListAPIView(generics.ListAPIView):
    queryset = Service.objects.filter(active=True)
    serializer_class = ServiceSerializer
    permission_classes = [permissions.AllowAny]


class BookingListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        data = self.request.data
        verification_token = secrets.token_urlsafe(32)

        # Parse and combine date and time
        try:
            date_str = data.get('date')
            time_str = data.get('time')
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
            time_obj = datetime.strptime(time_str, '%H:%M').time()
        except (ValueError, TypeError):
            raise ValueError("Invalid date or time format.")

        booking = serializer.save(
            user=self.request.user,
            mot_class=data.get('motClass', ''),
            date=date_obj,
            time=time_obj.strftime('%H:%M'),
            vehicle_make=data.get('vehicle', {}).get('make', ''),
            vehicle_model=data.get('vehicle', {}).get('model', ''),
            vehicle_year=data.get('vehicle', {}).get('year', ''),
            vehicle_registration=data.get('vehicle', {}).get('registration', ''),
            vehicle_mileage=data.get('vehicle', {}).get('mileage', ''),
            customer_first_name=data.get('customer', {}).get('firstName', ''),
            customer_last_name=data.get('customer', {}).get('lastName', ''),
            customer_email=data.get('customer', {}).get('email', ''),
            customer_phone=data.get('customer', {}).get('phone', ''),
            customer_address=data.get('customer', {}).get('address', ''),
            payment_method=data.get('payment', {}).get('method', 'card'),
            card_number=data.get('payment', {}).get('cardNumber', ''),
            expiry_date=data.get('payment', {}).get('expiryDate', ''),
            cvv=data.get('payment', {}).get('cvv', ''),
            name_on_card=data.get('payment', {}).get('nameOnCard', ''),
            is_verified=False,
            verification_token=verification_token,
        )

        # Send booking confirmation email
        send_mail(
            subject='Booking Confirmation',
            message=(
                f"Dear {booking.customer_first_name},\n\n"
                f"Your booking has been successfully made for {booking.date} at {booking.time}.\n"
                f"Service: {booking.service.name}\n"
                f"Vehicle: {booking.vehicle_make} {booking.vehicle_model} ({booking.vehicle_registration})\n\n"
                f"Thank you for choosing us!\n\n"
                f"Best regards,\nThe Team"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[booking.customer_email],
            fail_silently=False,
        )

        # Schedule reminder email 24 hours before the booking
        try:
            booking_datetime = datetime.combine(booking.date, datetime.strptime(booking.time, '%H:%M').time())
            booking_datetime = timezone.make_aware(booking_datetime)
            reminder_time = booking_datetime - timedelta(hours=24)
            
            # Only schedule if reminder time is in the future
            if reminder_time > timezone.now():
                send_booking_reminder.apply_async(
                    args=[booking.id],
                    eta=reminder_time
                )
        except Exception as e:
            # Log the error but don't fail the booking creation
            print(f"Failed to schedule reminder for booking {booking.id}: {e}")


class BookingVerifyAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, token):
        try:
            booking = Booking.objects.get(verification_token=token)
            if booking.is_verified:
                return Response({'message': 'Booking already verified.'}, status=200)
            booking.is_verified = True
            booking.save()
            return Response({'message': 'Booking successfully verified.'}, status=200)
        except Booking.DoesNotExist:
            return Response({'error': 'Invalid verification token.'}, status=404)
from django.core.mail import send_mail
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from .models import Booking
from .serializers import BookingSerializer
from django.conf import settings

     
class PaymentCaptureAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        booking_id = request.data.get('booking_id')
        paypal_order_id = request.data.get('paypal_order_id')

        if not booking_id or not paypal_order_id:
            return Response({"error": "Missing booking_id or paypal_order_id"}, status=400)

        try:
            booking = Booking.objects.get(id=booking_id, user=request.user)
        except Booking.DoesNotExist:
            return Response({"error": "Booking not found"}, status=404)

        # Simulate PayPal capture logic
        booking.payment_status = 'paid'
        booking.is_paid = True
        booking.paypal_transaction_id = paypal_order_id
        booking.save()

        # Send payment confirmation email
        send_mail(
            subject='Payment Confirmed - Booking Confirmed',
            message=(
                f"Dear {booking.customer_first_name},\n\n"
                f"Your payment has been successfully processed!\n\n"
                f"Booking Details:\n"
                f"Service: {booking.service.name}\n"
                f"Date: {booking.date}\n"
                f"Time: {booking.time}\n"
                f"Vehicle: {booking.vehicle_make} {booking.vehicle_model} ({booking.vehicle_registration})\n"
                f"Transaction ID: {paypal_order_id}\n\n"
                f"Your booking is now confirmed. We look forward to seeing you!\n\n"
                f"Best regards,\nThe Team"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[booking.customer_email],
            fail_silently=False,
        )

        return Response({"message": "Payment captured successfully!"}, status=200)  
