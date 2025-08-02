from datetime import datetime, timedelta
import secrets
import logging

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone

from .models import Service, Booking
from .serializers import ServiceSerializer, BookingSerializer
from .paypal_utils import paypal_api

# Set up logging
logger = logging.getLogger(__name__)

# Import tasks with error handling
try:
    from .tasks import send_booking_reminder
    CELERY_AVAILABLE = True
except ImportError:
    # If Celery is not available, create a dummy function
    CELERY_AVAILABLE = False
    def send_booking_reminder(booking_id):
        logger.warning(f"Celery not available, skipping reminder for booking {booking_id}")
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
    
    def create(self, request, *args, **kwargs):
        """Override create to provide better error handling"""
        try:
            logger.info(f"Booking creation request from user {request.user.id}")
            return super().create(request, *args, **kwargs)
        except ValueError as e:
            logger.error(f"Validation error in booking creation: {e}")
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Unexpected error in booking creation: {e}")
            return Response(
                {'error': 'An error occurred while creating the booking. Please try again.'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def perform_create(self, serializer):
        try:
            data = self.request.data
            verification_token = secrets.token_urlsafe(32)
            
            logger.info(f"Creating booking for user {self.request.user.id}")
            logger.debug(f"Booking data received: {data}")

            # Parse and combine date and time
            try:
                date_str = data.get('date')
                time_str = data.get('time')
                
                if not date_str or not time_str:
                    raise ValueError("Date and time are required")
                
                date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
                time_obj = datetime.strptime(time_str, '%H:%M').time()
                
                logger.debug(f"Parsed date: {date_obj}, time: {time_obj}")
                
            except (ValueError, TypeError) as e:
                logger.error(f"Date/time parsing error: {e}")
                raise ValueError(f"Invalid date or time format: {e}")

            # Extract nested data safely
            vehicle_data = data.get('vehicle', {})
            customer_data = data.get('customer', {})
            payment_data = data.get('payment', {})

            # Calculate payment amount
            price = data.get('price', 0)
            quantity = data.get('quantity', 1)
            payment_amount = float(price) * int(quantity)

            # Save the booking
            booking = serializer.save(
                user=self.request.user,
                mot_class=data.get('motClass', ''),
                date=date_obj,
                time=time_obj.strftime('%H:%M'),
                vehicle_make=vehicle_data.get('make', ''),
                vehicle_model=vehicle_data.get('model', ''),
                vehicle_year=vehicle_data.get('year', ''),
                vehicle_registration=vehicle_data.get('registration', ''),
                vehicle_mileage=vehicle_data.get('mileage', ''),
                customer_first_name=customer_data.get('firstName', ''),
                customer_last_name=customer_data.get('lastName', ''),
                customer_email=customer_data.get('email', ''),
                customer_phone=customer_data.get('phone', ''),
                customer_address=customer_data.get('address', ''),
                payment_method=payment_data.get('method', 'card'),
                card_number=payment_data.get('cardNumber', ''),
                expiry_date=payment_data.get('expiryDate', ''),
                cvv=payment_data.get('cvv', ''),
                name_on_card=payment_data.get('nameOnCard', ''),
                is_verified=False,
                verification_token=verification_token,
                payment_amount=payment_amount,
                payment_currency='GBP'
            )
            
            logger.info(f"Booking created successfully with ID: {booking.id}")

            # Send immediate booking confirmation email
            try:
                customer_email = booking.customer_email
                if customer_email:
                    logger.info(f"Attempting to send confirmation email to {customer_email} for booking {booking.id}")
                    
                    # Send immediate confirmation email
                    try:
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
                                f"Please complete your payment to confirm this booking.\n\n"
                                f"Thank you for choosing Access Auto Services!\n\n"
                                f"Best regards,\nThe Access Auto Services Team"
                            ),
                            from_email=settings.DEFAULT_FROM_EMAIL,
                            recipient_list=[customer_email],
                            fail_silently=False,  # Changed to False to catch errors
                        )
                        
                        if email_result:
                            logger.info(f"✅ Booking confirmation email sent successfully to {customer_email}")
                        else:
                            logger.error(f"❌ Booking confirmation email failed to send to {customer_email} (result: {email_result})")
                            
                    except Exception as email_error:
                        logger.error(f"❌ Error sending booking confirmation email to {customer_email}: {email_error}")
                        
                else:
                    logger.warning(f"⚠️ No email address provided for booking {booking.id}")
            except Exception as e:
                logger.error(f"❌ Failed to send confirmation email for booking {booking.id}: {e}")

            # Schedule reminder email 24 hours before the booking
            try:
                if customer_email:
                    booking_datetime = datetime.combine(booking.date, datetime.strptime(booking.time, '%H:%M').time())
                    booking_datetime = timezone.make_aware(booking_datetime)
                    reminder_time = booking_datetime - timedelta(hours=24)
                    
                    logger.info(f"Booking datetime: {booking_datetime}, Reminder time: {reminder_time}, Current time: {timezone.now()}")
                    
                    # Only schedule if reminder time is in the future
                    if reminder_time > timezone.now():
                        try:
                            from email_service.models import BookingReminder
                            booking_details = {
                                'service_name': booking.service.name,
                                'mot_class': booking.mot_class if booking.mot_class else None,
                                'price': float(booking.payment_amount) if booking.payment_amount else 0,
                                'quantity': quantity,
                                'date': str(booking.date),
                                'time': booking.time,
                                'vehicle_registration': booking.vehicle_registration
                            }
                            
                            logger.info(f"Creating booking reminder for {customer_email}")
                            booking_reminder = BookingReminder.objects.create(
                                email=customer_email,
                                booking_details=booking_details,
                                appointment_datetime=booking_datetime,
                                booking_url=f"https://www.access-auto-services.co.uk/booking",
                                scheduled_for=reminder_time
                            )
                            logger.info(f"Booking reminder created with ID: {booking_reminder.id}")
                            
                            # Schedule with Celery if available
                            if CELERY_AVAILABLE:
                                try:
                                    from email_service.tasks import send_reminder_email_task
                                    send_reminder_email_task.apply_async(
                                        args=[booking_reminder.id],
                                        eta=reminder_time
                                    )
                                    logger.info(f"✅ Reminder scheduled with Celery for booking {booking.id} at {reminder_time}")
                                except Exception as celery_error:
                                    logger.error(f"❌ Failed to schedule reminder with Celery: {celery_error}")
                            else:
                                logger.info(f"⚠️ Celery not available, reminder created but not scheduled for booking {booking.id}")
                                
                        except Exception as e:
                            logger.error(f"❌ Failed to create booking reminder: {e}")
                            # Fallback to old method
                            try:
                                if CELERY_AVAILABLE:
                                    send_booking_reminder.apply_async(
                                        args=[booking.id],
                                        eta=reminder_time
                                    )
                                    logger.info(f"✅ Fallback reminder scheduled for booking {booking.id}")
                            except Exception as fallback_error:
                                logger.error(f"❌ Fallback reminder scheduling also failed: {fallback_error}")
                    else:
                        logger.info(f"⚠️ Booking {booking.id} is too soon for reminder scheduling (reminder time: {reminder_time})")
                else:
                    logger.warning(f"⚠️ No email provided for booking {booking.id}, skipping reminder scheduling")
                    
            except Exception as e:
                # Log the error but don't fail the booking creation
                logger.error(f"❌ Failed to schedule reminder for booking {booking.id}: {e}")
                
        except Exception as e:
            logger.error(f"Error creating booking: {e}")
            raise


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


class BookingDebugAPIView(APIView):
    """Debug endpoint to test booking data structure"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        logger.info(f"Debug booking request from user {request.user.id}")
        logger.info(f"Request data: {request.data}")
        
        # Check required fields
        required_fields = ['service_id', 'date', 'time']
        missing_fields = []
        
        for field in required_fields:
            if field not in request.data:
                missing_fields.append(field)
        
        if missing_fields:
            return Response({
                'error': f'Missing required fields: {missing_fields}',
                'received_data': request.data
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if service exists
        try:
            service = Service.objects.get(id=request.data['service_id'])
            logger.info(f"Service found: {service.name}")
        except Service.DoesNotExist:
            return Response({
                'error': f'Service with id {request.data["service_id"]} not found',
                'available_services': list(Service.objects.values('id', 'name'))
            }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            'message': 'Debug successful',
            'user': request.user.username,
            'service': service.name,
            'received_data': request.data
        })

     
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

        try:
            # Capture payment through PayPal API
            capture_result = paypal_api.capture_order(paypal_order_id)
            
            # Extract transaction details
            capture_id = None
            if capture_result.get('purchase_units'):
                payments = capture_result['purchase_units'][0].get('payments', {})
                captures = payments.get('captures', [])
                if captures:
                    capture_id = captures[0].get('id')
            
            # Update booking with payment information
            booking.payment_status = 'completed'
            booking.is_paid = True
            booking.paypal_order_id = paypal_order_id
            booking.paypal_transaction_id = capture_id or paypal_order_id
            booking.save()

            logger.info(f"Payment captured for booking {booking_id}: {capture_id}")

            # Send payment confirmation email
            try:
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
                        f"Amount: £{booking.payment_amount}\n"
                        f"Transaction ID: {booking.paypal_transaction_id}\n\n"
                        f"Your booking is now confirmed. We look forward to seeing you!\n\n"
                        f"Best regards,\nAccess Auto Services Team"
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[booking.customer_email],
                    fail_silently=False,
                )
                logger.info(f"Payment confirmation email sent for booking {booking_id}")
            except Exception as e:
                logger.error(f"Failed to send payment confirmation email: {e}")

            return Response({
                "message": "Payment captured successfully!",
                "transaction_id": booking.paypal_transaction_id,
                "booking_id": booking.id
            }, status=200)

        except Exception as e:
            logger.error(f"PayPal capture failed for order {paypal_order_id}: {e}")
            return Response({
                "error": "Payment capture failed. Please try again."
            }, status=400)


class PayPalCreateOrderAPIView(APIView):
    """Create PayPal order for booking payment"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        booking_id = request.data.get('booking_id')
        
        if not booking_id:
            return Response({"error": "Missing booking_id"}, status=400)

        try:
            booking = Booking.objects.get(id=booking_id, user=request.user)
        except Booking.DoesNotExist:
            return Response({"error": "Booking not found"}, status=404)

        if booking.is_paid:
            return Response({"error": "Booking is already paid"}, status=400)

        try:
            # Create PayPal order
            amount = float(booking.payment_amount) if booking.payment_amount else 0
            description = f"Booking for {booking.service.name} on {booking.date}"
            
            order = paypal_api.create_order(
                amount=amount,
                currency=booking.payment_currency,
                description=description
            )
            
            # Store PayPal order ID in booking
            booking.paypal_order_id = order.get('id')
            booking.payment_status = 'created'
            booking.save()
            
            logger.info(f"PayPal order created for booking {booking_id}: {order.get('id')}")
            
            return Response({
                "order_id": order.get('id'),
                "booking_id": booking.id,
                "amount": amount,
                "currency": booking.payment_currency
            }, status=201)

        except Exception as e:
            logger.error(f"Failed to create PayPal order for booking {booking_id}: {e}")
            return Response({
                "error": "Failed to create payment order. Please try again."
            }, status=500)
