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
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        # Allow authenticated users to see their bookings
        if self.request.user.is_authenticated:
            try:
                logger.info(f"Fetching bookings for authenticated user {self.request.user.id}")
                queryset = Booking.objects.filter(user=self.request.user).order_by('-created')
                logger.info(f"Found {queryset.count()} bookings for user {self.request.user.id}")
                return queryset
            except Exception as e:
                logger.error(f"Error fetching bookings for user {self.request.user.id}: {e}")
                return Booking.objects.none()
        
        # Allow anonymous users to see bookings by providing email
        email = self.request.query_params.get('email')
        if email:
            try:
                logger.info(f"Fetching bookings for email {email}")
                queryset = Booking.objects.filter(customer_email=email).order_by('-created')
                logger.info(f"Found {queryset.count()} bookings for email {email}")
                return queryset
            except Exception as e:
                logger.error(f"Error fetching bookings for email {email}: {e}")
                return Booking.objects.none()
        
        # If no email provided and not authenticated, return empty queryset
        return Booking.objects.none()
    
    def list(self, request, *args, **kwargs):
        """Override list to provide better error handling"""
        try:
            user_info = f"user {request.user.id}" if request.user.is_authenticated else "anonymous user"
            logger.info(f"Booking list request from {user_info}")
            return super().list(request, *args, **kwargs)
        except Exception as e:
            user_info = f"user {request.user.id}" if request.user.is_authenticated else "anonymous user"
            logger.error(f"Error in booking list for {user_info}: {e}")
            return Response(
                {'error': 'An error occurred while fetching bookings. Please try again.'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def create(self, request, *args, **kwargs):
        """Override create to provide better error handling"""
        try:
            user_info = f"user {request.user.id}" if request.user.is_authenticated else "anonymous user"
            logger.info(f"Booking creation request from {user_info}")
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
            
            user_info = f"user {self.request.user.id}" if self.request.user.is_authenticated else "anonymous user"
            logger.info(f"Creating booking for {user_info}")
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
            # Only assign user if authenticated, otherwise allow null for anonymous bookings
            user = self.request.user if self.request.user.is_authenticated else None
            booking = serializer.save(
                user=user,
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
                        
                        # Send to both customer and owner
                        recipient_list = [customer_email]
                        owner_email = settings.OWNER_EMAIL
                        if owner_email and owner_email not in recipient_list:
                            recipient_list.append(owner_email)
                        
                        # Send email with timeout and error handling
                        import threading
                        import signal
                        
                        def send_email_with_timeout():
                            try:
                                email_result = send_mail(
                                    subject='Booking Confirmation - Access Auto Services',
                                    message=(
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
                                    ),
                                    from_email=settings.DEFAULT_FROM_EMAIL,
                                    recipient_list=recipient_list,
                                    fail_silently=True,  # Changed to True to prevent blocking
                                )
                                
                                if email_result:
                                    logger.info(f"✅ Booking confirmation email sent successfully to {customer_email}")
                                else:
                                    logger.warning(f"⚠️ Email sending returned False for {customer_email}")
                                    
                                return email_result
                                
                            except Exception as e:
                                logger.error(f"❌ Failed to send booking confirmation email: {e}")
                                return False
                        
                        # Run email sending in a separate thread with timeout
                        email_thread = threading.Thread(target=send_email_with_timeout)
                        email_thread.daemon = True
                        email_thread.start()
                        email_thread.join(timeout=10)  # 10 second timeout
                        
                        if email_thread.is_alive():
                            logger.warning(f"⚠️ Email sending timed out for booking {booking.id}")
                        
                    except Exception as e:
                        logger.error(f"❌ Error in email preparation for booking {booking.id}: {e}")
                        
                else:
                    logger.warning(f"⚠️ No customer email provided for booking {booking.id}")
                    
            except Exception as e:
                logger.error(f"❌ Unexpected error in email handling for booking {booking.id}: {e}")

            # Schedule reminder email (24 hours before appointment)
            try:
                if CELERY_AVAILABLE:
                    # Calculate when to send reminder (24 hours before appointment)
                    appointment_datetime = datetime.combine(booking.date, datetime.strptime(booking.time, '%H:%M').time())
                    reminder_datetime = appointment_datetime - timedelta(hours=24)
                    
                    # Only schedule if reminder time is in the future
                    if reminder_datetime > datetime.now():
                        send_booking_reminder.apply_async(
                            args=[booking.id],
                            eta=reminder_datetime
                        )
                        logger.info(f"📅 Reminder scheduled for booking {booking.id} at {reminder_datetime}")
                    else:
                        logger.info(f"⏰ Appointment too soon for reminder - booking {booking.id}")
                else:
                    logger.info(f"📧 Celery not available - no reminder scheduled for booking {booking.id}")
                    
            except Exception as e:
                logger.error(f"❌ Failed to schedule reminder for booking {booking.id}: {e}")

        except Exception as e:
            logger.error(f"❌ Error in perform_create: {e}")
            raise


class BookingVerifyAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, token):
        try:
            booking = Booking.objects.get(verification_token=token)
            booking.is_verified = True
            booking.save()
            return Response({'message': 'Booking successfully verified.'}, status=200)
        except Booking.DoesNotExist:
            return Response({'error': 'Invalid verification token.'}, status=404)


class BookingDebugAPIView(APIView):
    """Debug endpoint to test booking data structure"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        user_info = f"user {request.user.id}" if request.user.is_authenticated else "anonymous user"
        logger.info(f"Debug booking request from {user_info}")
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
            'user': request.user.username if request.user.is_authenticated else 'anonymous',
            'service': service.name,
            'received_data': request.data
        })

     
class PaymentCaptureAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        booking_id = request.data.get('booking_id')
        paypal_order_id = request.data.get('paypal_order_id')
        customer_email = request.data.get('customer_email')  # For anonymous users

        if not booking_id or not paypal_order_id:
            return Response({"error": "Missing booking_id or paypal_order_id"}, status=400)

        try:
            # For authenticated users, filter by user
            if request.user.is_authenticated:
                booking = Booking.objects.get(id=booking_id, user=request.user)
            else:
                # For anonymous users, require email verification
                if not customer_email:
                    return Response({"error": "Email required for anonymous payment"}, status=400)
                booking = Booking.objects.get(id=booking_id, customer_email=customer_email)
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

            # Send payment confirmation email to both customer and owner
            try:
                recipient_list = [booking.customer_email]
                owner_email = settings.OWNER_EMAIL
                if owner_email and owner_email not in recipient_list:
                    recipient_list.append(owner_email)
                
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
                    recipient_list=recipient_list,
                    fail_silently=False,
                )
                logger.info(f"Payment confirmation email sent for booking {booking_id} to {recipient_list}")
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
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        booking_id = request.data.get('booking_id')
        customer_email = request.data.get('customer_email')  # For anonymous users
        
        if not booking_id:
            return Response({"error": "Missing booking_id"}, status=400)

        try:
            # For authenticated users, filter by user
            if request.user.is_authenticated:
                booking = Booking.objects.get(id=booking_id, user=request.user)
            else:
                # For anonymous users, require email verification
                if not customer_email:
                    return Response({"error": "Email required for anonymous payment"}, status=400)
                booking = Booking.objects.get(id=booking_id, customer_email=customer_email)
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
                description=description,
                custom_id=booking.id
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


class BookingDetailAPIView(APIView):
    """Retrieve individual booking details"""
    permission_classes = [permissions.AllowAny]

    def get(self, request, booking_id):
        customer_email = request.query_params.get('email')
        
        try:
            # For authenticated users, filter by user
            if request.user.is_authenticated:
                booking = Booking.objects.get(id=booking_id, user=request.user)
            else:
                # For anonymous users, require email verification
                if not customer_email:
                    return Response({"error": "Email required for anonymous access"}, status=400)
                booking = Booking.objects.get(id=booking_id, customer_email=customer_email)
        except Booking.DoesNotExist:
            return Response({"error": "Booking not found"}, status=404)

        serializer = BookingSerializer(booking)
        return Response(serializer.data, status=200)


class PayPalWebhookAPIView(APIView):
    """Handle PayPal webhook notifications"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        try:
            # Get webhook headers and body
            headers = {
                'PAYPAL-AUTH-ALGO': request.META.get('HTTP_PAYPAL_AUTH_ALGO'),
                'PAYPAL-CERT-ID': request.META.get('HTTP_PAYPAL_CERT_ID'),
                'PAYPAL-TRANSMISSION-ID': request.META.get('HTTP_PAYPAL_TRANSMISSION_ID'),
                'PAYPAL-TRANSMISSION-SIG': request.META.get('HTTP_PAYPAL_TRANSMISSION_SIG'),
                'PAYPAL-TRANSMISSION-TIME': request.META.get('HTTP_PAYPAL_TRANSMISSION_TIME'),
            }
            
            # Verify webhook signature
            if not paypal_api.verify_webhook_signature(headers, request.data):
                logger.warning("PayPal webhook signature verification failed")
                return Response({"error": "Invalid signature"}, status=400)
            
            event_type = request.data.get('event_type')
            resource = request.data.get('resource', {})
            
            logger.info(f"PayPal webhook received: {event_type}")
            
            # Handle payment completion
            if event_type == 'PAYMENT.CAPTURE.COMPLETED':
                self.handle_payment_completed(resource)
            elif event_type == 'PAYMENT.CAPTURE.DENIED':
                self.handle_payment_denied(resource)
            elif event_type == 'PAYMENT.CAPTURE.REFUNDED':
                self.handle_payment_refunded(resource)
            
            return Response({"status": "success"}, status=200)
            
        except Exception as e:
            logger.error(f"PayPal webhook error: {e}")
            return Response({"error": "Webhook processing failed"}, status=500)
    
    def handle_payment_completed(self, resource):
        """Handle completed payment"""
        try:
            # Extract payment details
            capture_id = resource.get('id')
            amount = resource.get('amount', {})
            custom_id = resource.get('custom_id')  # This should contain booking ID
            
            if custom_id:
                try:
                    booking = Booking.objects.get(id=custom_id)
                    booking.payment_status = 'completed'
                    booking.is_paid = True
                    booking.paypal_transaction_id = capture_id
                    booking.save()
                    
                    # Send payment confirmation email
                    self.send_payment_confirmation_email(booking)
                    
                    logger.info(f"Payment completed for booking {booking.id}: {capture_id}")
                    
                except Booking.DoesNotExist:
                    logger.error(f"Booking not found for payment: {custom_id}")
            
        except Exception as e:
            logger.error(f"Error handling payment completion: {e}")
    
    def handle_payment_denied(self, resource):
        """Handle denied payment"""
        try:
            custom_id = resource.get('custom_id')
            if custom_id:
                try:
                    booking = Booking.objects.get(id=custom_id)
                    booking.payment_status = 'failed'
                    booking.save()
                    
                    logger.info(f"Payment denied for booking {booking.id}")
                    
                except Booking.DoesNotExist:
                    logger.error(f"Booking not found for denied payment: {custom_id}")
                    
        except Exception as e:
            logger.error(f"Error handling payment denial: {e}")
    
    def handle_payment_refunded(self, resource):
        """Handle refunded payment"""
        try:
            custom_id = resource.get('custom_id')
            if custom_id:
                try:
                    booking = Booking.objects.get(id=custom_id)
                    booking.payment_status = 'refunded'
                    booking.save()
                    
                    logger.info(f"Payment refunded for booking {booking.id}")
                    
                except Booking.DoesNotExist:
                    logger.error(f"Booking not found for refunded payment: {custom_id}")
                    
        except Exception as e:
            logger.error(f"Error handling payment refund: {e}")
    
    def send_payment_confirmation_email(self, booking):
        """Send payment confirmation email"""
        try:
            from django.core.mail import send_mail
            from django.conf import settings
            
            recipient_list = [booking.customer_email]
            owner_email = settings.OWNER_EMAIL
            if owner_email and owner_email not in recipient_list:
                recipient_list.append(owner_email)
            
            subject = 'Payment Confirmed - Access Auto Services'
            message = f"""
Dear {booking.customer_first_name or 'Customer'},

Your payment has been successfully processed!

Booking Details:
- Service: {booking.service.name}
- Date: {booking.date}
- Time: {booking.time}
- Vehicle: {booking.vehicle_make} {booking.vehicle_model} ({booking.vehicle_registration})
- Amount: £{booking.payment_amount}
- Transaction ID: {booking.paypal_transaction_id}

Your booking is now confirmed. We look forward to seeing you!

Best regards,
Access Auto Services Team
            """
            
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=recipient_list,
                fail_silently=False,
            )
            
            logger.info(f"Payment confirmation email sent for booking {booking.id}")
            
        except Exception as e:
            logger.error(f"Failed to send payment confirmation email: {e}")