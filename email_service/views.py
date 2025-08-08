from datetime import datetime, timedelta
import logging
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import EmailVerification, BookingReminder
from .serializers import EmailVerificationSerializer, BookingReminderSerializer

# Set up logging
logger = logging.getLogger(__name__)

# Import tasks with error handling
try:
    from .tasks import send_reminder_email_task
    CELERY_AVAILABLE = True
except ImportError:
    CELERY_AVAILABLE = False
    def send_reminder_email_task(reminder_id):
        logger.warning(f"Celery not available, skipping reminder task for reminder {reminder_id}")
        pass

class EmailVerificationAPIView(APIView):
    """
    Handle email verification requests
    POST: Send verification email
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        try:
            serializer = EmailVerificationSerializer(data=request.data)
            if serializer.is_valid():
                email_verification = serializer.save()
                
                # Send verification email
                self.send_verification_email(email_verification)
                
                logger.info(f"Email verification created for {email_verification.email}")
                return Response({
                    'message': 'Verification email sent successfully',
                    'verification_id': email_verification.id
                }, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            logger.error(f"Error in email verification: {e}")
            return Response({
                'error': 'Failed to send verification email'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def send_verification_email(self, email_verification):
        """Send the verification email"""
        try:
            # Format booking details for email
            booking_details = email_verification.booking_details
            booking_summary = self.format_booking_details(booking_details)
            
            verification_url = f"{email_verification.booking_url}?verify={email_verification.verification_token}"
            
            subject = "Booking Confirmation - Access Auto Services"
            message = f"""
Dear Customer,

Thank you for booking with Access Auto Services!

Your booking details:
{booking_summary}

Please click the link below to verify your email and confirm your booking:
{verification_url}

If you did not make this booking, please ignore this email.

Best regards,
Access Auto Services Team
            """
            
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email_verification.email],
                fail_silently=False,
            )
            
            logger.info(f"Verification email sent to {email_verification.email}")
            
        except Exception as e:
            logger.error(f"Failed to send verification email: {e}")
            raise
    
    def format_booking_details(self, booking_details):
        """Format booking details for email display"""
        formatted = ""
        
        if isinstance(booking_details, list):
            for i, booking in enumerate(booking_details, 1):
                formatted += f"\nBooking {i}:\n"
                formatted += f"  Service: {booking.get('service_name', 'N/A')}\n"
                if booking.get('mot_class'):
                    formatted += f"  MOT Class: {booking.get('mot_class')}\n"
                formatted += f"  Price: £{booking.get('price', 0)}\n"
                formatted += f"  Quantity: {booking.get('quantity', 1)}\n"
                formatted += f"  Date: {booking.get('date', 'N/A')}\n"
                formatted += f"  Time: {booking.get('time', 'N/A')}\n"
                if booking.get('vehicle_registration'):
                    formatted += f"  Vehicle: {booking.get('vehicle_registration')}\n"
                formatted += "\n"
        else:
            # Single booking
            formatted += f"Service: {booking_details.get('service_name', 'N/A')}\n"
            if booking_details.get('mot_class'):
                formatted += f"MOT Class: {booking_details.get('mot_class')}\n"
            formatted += f"Price: £{booking_details.get('price', 0)}\n"
            formatted += f"Date: {booking_details.get('date', 'N/A')}\n"
            formatted += f"Time: {booking_details.get('time', 'N/A')}\n"
            if booking_details.get('vehicle_registration'):
                formatted += f"Vehicle: {booking_details.get('vehicle_registration')}\n"
        
        return formatted

class EmailVerifyTokenAPIView(APIView):
    """
    Handle email verification token validation
    GET: Verify email with token
    """
    permission_classes = [AllowAny]
    
    def get(self, request, token):
        try:
            email_verification = EmailVerification.objects.get(
                verification_token=token,
                is_verified=False
            )
            
            # Mark as verified
            email_verification.is_verified = True
            email_verification.verified_at = timezone.now()
            email_verification.save()
            
            logger.info(f"Email verified for {email_verification.email}")
            
            return Response({
                'message': 'Email verified successfully',
                'email': email_verification.email
            }, status=status.HTTP_200_OK)
            
        except EmailVerification.DoesNotExist:
            return Response({
                'error': 'Invalid or expired verification token'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error verifying email: {e}")
            return Response({
                'error': 'Verification failed'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class BookingReminderAPIView(APIView):
    """
    Handle booking reminder scheduling
    POST: Schedule a booking reminder
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        try:
            serializer = BookingReminderSerializer(data=request.data)
            if serializer.is_valid():
                # Calculate reminder time (24 hours before appointment)
                appointment_datetime = serializer.validated_data['appointment_datetime']
                reminder_time = appointment_datetime - timedelta(hours=24)
                
                # Only schedule if reminder time is in the future
                if reminder_time <= timezone.now():
                    return Response({
                        'message': 'Appointment is too soon for reminder scheduling'
                    }, status=status.HTTP_200_OK)
                
                booking_reminder = serializer.save(scheduled_for=reminder_time)
                
                # Schedule the reminder email
                self.schedule_reminder_email(booking_reminder)
                
                logger.info(f"Booking reminder scheduled for {booking_reminder.email} at {reminder_time}")
                
                return Response({
                    'message': 'Booking reminder scheduled successfully',
                    'reminder_id': booking_reminder.id,
                    'scheduled_for': reminder_time
                }, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            logger.error(f"Error scheduling booking reminder: {e}")
            return Response({
                'error': 'Failed to schedule booking reminder'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def schedule_reminder_email(self, booking_reminder):
        """Schedule the reminder email using Celery or immediate sending"""
        try:
            if CELERY_AVAILABLE:
                try:
                    # Test Redis connection first
                    from django.core.cache import cache
                    cache.get('test_key')  # This will fail if Redis is not available
                    
                    # Schedule with Celery
                    send_reminder_email_task.apply_async(
                        args=[booking_reminder.id],
                        eta=booking_reminder.scheduled_for
                    )
                    logger.info(f"Reminder email scheduled with Celery for {booking_reminder.id}")
                except Exception as celery_error:
                    logger.warning(f"Celery/Redis not available ({celery_error}). Reminder created but not scheduled.")
                    # Don't raise the error, just log it
            else:
                # For development/testing - send immediately or log
                logger.info(f"Celery not available. Reminder would be sent at {booking_reminder.scheduled_for}")
                
        except Exception as e:
            logger.error(f"Failed to schedule reminder email: {e}")
            # Don't raise the error to prevent booking creation from failing
            logger.warning("Continuing without reminder scheduling...")

class SendReminderNowAPIView(APIView):
    """
    Manual endpoint to send reminder emails (for testing or manual triggers)
    POST: Send reminder email immediately
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        reminder_id = request.data.get('reminder_id')
        
        if not reminder_id:
            return Response({
                'error': 'reminder_id is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            booking_reminder = BookingReminder.objects.get(id=reminder_id)
            
            if booking_reminder.reminder_sent:
                return Response({
                    'message': 'Reminder already sent'
                }, status=status.HTTP_200_OK)
            
            # Send the reminder email
            self.send_reminder_email(booking_reminder)
            
            # Mark as sent
            booking_reminder.reminder_sent = True
            booking_reminder.sent_at = timezone.now()
            booking_reminder.save()
            
            return Response({
                'message': 'Reminder email sent successfully'
            }, status=status.HTTP_200_OK)
            
        except BookingReminder.DoesNotExist:
            return Response({
                'error': 'Booking reminder not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error sending reminder email: {e}")
            return Response({
                'error': 'Failed to send reminder email'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def send_reminder_email(self, booking_reminder):
        """Send the reminder email"""
        try:
            # Format booking details for email
            booking_details = booking_reminder.booking_details
            booking_summary = self.format_booking_details(booking_details)
            
            subject = "Booking Reminder - Access Auto Services"
            message = f"""
Dear Customer,

This is a friendly reminder about your upcoming appointment with Access Auto Services.

Your booking details:
{booking_summary}

Appointment Date & Time: {booking_reminder.appointment_datetime.strftime('%Y-%m-%d at %H:%M')}

We look forward to seeing you!

If you need to reschedule or have any questions, please contact us.

Best regards,
Access Auto Services Team
            """
            
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[booking_reminder.email],
                fail_silently=False,
            )
            
            logger.info(f"Reminder email sent to {booking_reminder.email}")
            
        except Exception as e:
            logger.error(f"Failed to send reminder email: {e}")
            raise
    
    def format_booking_details(self, booking_details):
        """Format booking details for email display"""
        formatted = ""
        
        if isinstance(booking_details, list):
            for i, booking in enumerate(booking_details, 1):
                formatted += f"\nService {i}:\n"
                formatted += f"  Service: {booking.get('service_name', 'N/A')}\n"
                if booking.get('mot_class'):
                    formatted += f"  MOT Class: {booking.get('mot_class')}\n"
                formatted += f"  Price: £{booking.get('price', 0)}\n"
                formatted += f"  Quantity: {booking.get('quantity', 1)}\n"
                if booking.get('vehicle_registration'):
                    formatted += f"  Vehicle: {booking.get('vehicle_registration')}\n"
                formatted += "\n"
        else:
            # Single booking
            formatted += f"Service: {booking_details.get('service_name', 'N/A')}\n"
            if booking_details.get('mot_class'):
                formatted += f"MOT Class: {booking_details.get('mot_class')}\n"
            formatted += f"Price: £{booking_details.get('price', 0)}\n"
            if booking_details.get('vehicle_registration'):
                formatted += f"Vehicle: {booking_details.get('vehicle_registration')}\n"
        
        return formatted
