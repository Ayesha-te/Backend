from django.http import JsonResponse
from django.views import View
from django.contrib.auth import get_user_model
from django.db.models import Count, Sum, Q
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from datetime import datetime, timedelta
from PAYPAL.models import Booking as PayPalBooking, Service as PayPalService
import json
import logging

User = get_user_model()
logger = logging.getLogger(__name__)

class UsersListView(View):
    def get(self, request):
        try:
            users = User.objects.all().order_by('-date_joined')
            
            # Add booking count for each user
            users_data = []
            for user in users:
                paypal_bookings = PayPalBooking.objects.filter(user=user).count()
                
                users_data.append({
                    'id': user.id,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'is_active': user.is_active,
                    'is_staff': user.is_staff,
                    'date_joined': user.date_joined.isoformat(),
                    'booking_count': paypal_bookings
                })
            
            return JsonResponse({'results': users_data})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

class UsersCountView(View):
    def get(self, request):
        try:
            total_users = User.objects.count()
            week_ago = timezone.now() - timedelta(days=7)
            new_this_week = User.objects.filter(date_joined__gte=week_ago).count()
            
            return JsonResponse({
                'total': total_users,
                'new_this_week': new_this_week
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class BookingsListView(View):
    def get(self, request):
        try:
            # Get only PayPal bookings (DVLA removed)
            paypal_bookings = PayPalBooking.objects.select_related('user', 'service').all().order_by('-created')
            
            bookings_data = []
            
            # Add PayPal bookings
            for booking in paypal_bookings:
                bookings_data.append({
                    'id': booking.id,
                    'user': {
                        'id': booking.user.id if booking.user else None,
                        'first_name': booking.user.first_name if booking.user else '',
                        'last_name': booking.user.last_name if booking.user else '',
                        'email': booking.user.email if booking.user else ''
                    },
                    'service': {
                        'id': booking.service.id if booking.service else None,
                        'name': booking.service.name if booking.service else 'Unknown Service',
                        'price': float(booking.service.price) if booking.service else 0
                    },
                    'customer_first_name': booking.customer_first_name,
                    'customer_last_name': booking.customer_last_name,
                    'customer_email': booking.customer_email,
                    'customer_phone': booking.customer_phone,
                    'customer_address': booking.customer_address,
                    'booking_date': booking.date.isoformat() if booking.date else None,
                    'booking_time': booking.time if booking.time else None,
                    'status': 'confirmed' if booking.is_verified else 'pending',
                    'payment_status': booking.payment_status,
                    'payment_method': booking.payment_method,
                    'amount': float(booking.payment_amount) if booking.payment_amount else 0,
                    'currency': booking.payment_currency,
                    'paypal_order_id': booking.paypal_order_id,
                    'paypal_transaction_id': booking.paypal_transaction_id,
                    'is_paid': booking.is_paid,
                    'created_at': booking.created.isoformat(),
                    'updated_at': booking.updated.isoformat(),
                })
            
            return JsonResponse({'results': bookings_data})
        except Exception as e:
            logger.error(f"Error fetching bookings: {e}")
            return JsonResponse({'error': str(e)}, status=500)
    
    def post(self, request):
        """Create a new booking"""
        try:
            data = json.loads(request.body)
            logger.info(f"Creating new booking with data: {data}")
            
            # Validate required fields
            required_fields = ['service_id', 'customer_email', 'booking_date', 'booking_time']
            for field in required_fields:
                if not data.get(field):
                    return JsonResponse({'error': f'{field} is required'}, status=400)
            
            # Get service
            try:
                service = PayPalService.objects.get(id=data['service_id'])
            except PayPalService.DoesNotExist:
                return JsonResponse({'error': 'Service not found'}, status=404)
            
            # Get user if provided
            user = None
            if data.get('user_id'):
                try:
                    user = User.objects.get(id=data['user_id'])
                except User.DoesNotExist:
                    return JsonResponse({'error': 'User not found'}, status=404)
            
            # Parse date and time
            try:
                booking_date = datetime.strptime(data['booking_date'], '%Y-%m-%d').date()
                booking_time = data['booking_time']
                # Validate time format
                datetime.strptime(booking_time, '%H:%M')
            except ValueError as e:
                return JsonResponse({'error': f'Invalid date/time format: {e}'}, status=400)
            
            # Create booking
            booking = PayPalBooking.objects.create(
                user=user,
                service=service,
                date=booking_date,
                time=booking_time,
                customer_first_name=data.get('customer_first_name', ''),
                customer_last_name=data.get('customer_last_name', ''),
                customer_email=data['customer_email'],
                customer_phone=data.get('customer_phone', ''),
                customer_address=data.get('customer_address', ''),
                payment_method='paypal',  # Default to PayPal
                payment_amount=data.get('amount', service.price),
                payment_currency=data.get('currency', 'GBP'),
                payment_status=data.get('payment_status', 'pending'),
                is_verified=data.get('is_verified', False),
                is_paid=data.get('is_paid', False)
            )
            
            logger.info(f"Booking created successfully with ID: {booking.id}")
            
            return JsonResponse({
                'message': 'Booking created successfully',
                'booking_id': booking.id
            }, status=201)
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        except Exception as e:
            logger.error(f"Error creating booking: {e}")
            return JsonResponse({'error': str(e)}, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class BookingDetailView(View):
    def get(self, request, booking_id):
        """Get individual booking details"""
        try:
            booking = PayPalBooking.objects.select_related('user', 'service').get(id=booking_id)
            
            booking_data = {
                'id': booking.id,
                'user': {
                    'id': booking.user.id if booking.user else None,
                    'first_name': booking.user.first_name if booking.user else '',
                    'last_name': booking.user.last_name if booking.user else '',
                    'email': booking.user.email if booking.user else ''
                },
                'service': {
                    'id': booking.service.id if booking.service else None,
                    'name': booking.service.name if booking.service else 'Unknown Service',
                    'price': float(booking.service.price) if booking.service else 0
                },
                'customer_first_name': booking.customer_first_name,
                'customer_last_name': booking.customer_last_name,
                'customer_email': booking.customer_email,
                'customer_phone': booking.customer_phone,
                'customer_address': booking.customer_address,
                'booking_date': booking.date.isoformat() if booking.date else None,
                'booking_time': booking.time if booking.time else None,
                'status': 'confirmed' if booking.is_verified else 'pending',
                'payment_status': booking.payment_status,
                'payment_method': booking.payment_method,
                'amount': float(booking.payment_amount) if booking.payment_amount else 0,
                'currency': booking.payment_currency,
                'paypal_order_id': booking.paypal_order_id,
                'paypal_transaction_id': booking.paypal_transaction_id,
                'is_paid': booking.is_paid,
                'is_verified': booking.is_verified,
                'created_at': booking.created.isoformat(),
                'updated_at': booking.updated.isoformat(),
            }
            
            return JsonResponse(booking_data)
        except PayPalBooking.DoesNotExist:
            return JsonResponse({'error': 'Booking not found'}, status=404)
        except Exception as e:
            logger.error(f"Error fetching booking {booking_id}: {e}")
            return JsonResponse({'error': str(e)}, status=500)
    
    def put(self, request, booking_id):
        """Update booking"""
        try:
            booking = PayPalBooking.objects.get(id=booking_id)
            data = json.loads(request.body)
            
            # Update fields if provided
            if 'service_id' in data:
                try:
                    service = PayPalService.objects.get(id=data['service_id'])
                    booking.service = service
                except PayPalService.DoesNotExist:
                    return JsonResponse({'error': 'Service not found'}, status=404)
            
            if 'user_id' in data:
                if data['user_id']:
                    try:
                        user = User.objects.get(id=data['user_id'])
                        booking.user = user
                    except User.DoesNotExist:
                        return JsonResponse({'error': 'User not found'}, status=404)
                else:
                    booking.user = None
            
            # Update booking date and time
            if 'booking_date' in data:
                try:
                    booking.date = datetime.strptime(data['booking_date'], '%Y-%m-%d').date()
                except ValueError:
                    return JsonResponse({'error': 'Invalid date format'}, status=400)
            
            if 'booking_time' in data:
                try:
                    datetime.strptime(data['booking_time'], '%H:%M')
                    booking.time = data['booking_time']
                except ValueError:
                    return JsonResponse({'error': 'Invalid time format'}, status=400)
            
            # Update customer information
            for field in ['customer_first_name', 'customer_last_name', 'customer_email', 
                         'customer_phone', 'customer_address']:
                if field in data:
                    setattr(booking, field, data[field])
            
            # Update payment information
            for field in ['payment_status', 'payment_method', 'amount', 'currency', 
                         'paypal_order_id', 'paypal_transaction_id']:
                if field in data:
                    if field == 'amount':
                        booking.payment_amount = data[field]
                    elif field == 'currency':
                        booking.payment_currency = data[field]
                    else:
                        setattr(booking, field, data[field])
            
            # Update status fields
            if 'is_paid' in data:
                booking.is_paid = bool(data['is_paid'])
            if 'is_verified' in data:
                booking.is_verified = bool(data['is_verified'])
            
            booking.save()
            
            logger.info(f"Booking {booking_id} updated successfully")
            return JsonResponse({'message': 'Booking updated successfully'})
            
        except PayPalBooking.DoesNotExist:
            return JsonResponse({'error': 'Booking not found'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        except Exception as e:
            logger.error(f"Error updating booking {booking_id}: {e}")
            return JsonResponse({'error': str(e)}, status=500)
    
    def delete(self, request, booking_id):
        """Delete booking"""
        try:
            booking = PayPalBooking.objects.get(id=booking_id)
            booking.delete()
            
            logger.info(f"Booking {booking_id} deleted successfully")
            return JsonResponse({'message': 'Booking deleted successfully'})
            
        except PayPalBooking.DoesNotExist:
            return JsonResponse({'error': 'Booking not found'}, status=404)
        except Exception as e:
            logger.error(f"Error deleting booking {booking_id}: {e}")
            return JsonResponse({'error': str(e)}, status=500)

class BookingsCountView(View):
    def get(self, request):
        try:
            paypal_count = PayPalBooking.objects.count()
            total_bookings = paypal_count  # Only PayPal bookings now
            
            # Today's bookings
            today = timezone.now().date()
            paypal_today = PayPalBooking.objects.filter(created__date=today).count()
            today_bookings = paypal_today
            
            return JsonResponse({
                'total': total_bookings,
                'today': today_bookings,
                'paypal': paypal_count
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

class BookingTrendsView(View):
    def get(self, request):
        try:
            # Get last 12 months data
            months = []
            paypal_data = []
            
            for i in range(11, -1, -1):
                date = timezone.now() - timedelta(days=30*i)
                month_start = date.replace(day=1)
                if i == 0:
                    month_end = timezone.now()
                else:
                    next_month = month_start.replace(month=month_start.month + 1) if month_start.month < 12 else month_start.replace(year=month_start.year + 1, month=1)
                    month_end = next_month - timedelta(days=1)
                
                months.append(date.strftime('%b %Y'))
                
                paypal_count = PayPalBooking.objects.filter(
                    created__gte=month_start,
                    created__lte=month_end
                ).count()
                
                paypal_data.append(paypal_count)
            
            return JsonResponse({
                'labels': months,
                'paypal_data': paypal_data
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

class ServiceDistributionView(View):
    def get(self, request):
        try:
            # Get service distribution by actual services
            services_data = PayPalService.objects.filter(active=True).annotate(
                booking_count=Count('booking')
            ).values('name', 'booking_count')
            
            labels = []
            values = []
            
            for service in services_data:
                if service['booking_count'] > 0:
                    labels.append(service['name'])
                    values.append(service['booking_count'])
            
            # If no data, show placeholder
            if not labels:
                labels = ['No Bookings Yet']
                values = [1]
            
            return JsonResponse({
                'labels': labels,
                'values': values
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

class PaymentsTotalView(View):
    def get(self, request):
        try:
            # Calculate total revenue from PayPal bookings only
            paypal_total = PayPalBooking.objects.filter(
                is_paid=True
            ).aggregate(total=Sum('payment_amount'))['total'] or 0
            
            total_revenue = float(paypal_total)
            
            # Today's revenue
            today = timezone.now().date()
            paypal_today = PayPalBooking.objects.filter(
                is_paid=True,
                created__date=today
            ).aggregate(total=Sum('payment_amount'))['total'] or 0
            
            today_revenue = float(paypal_today)
            
            # This week's revenue
            week_ago = today - timedelta(days=7)
            week_revenue = PayPalBooking.objects.filter(
                is_paid=True,
                created__date__gte=week_ago
            ).aggregate(total=Sum('payment_amount'))['total'] or 0
            
            # This month's revenue
            month_start = today.replace(day=1)
            month_revenue = PayPalBooking.objects.filter(
                is_paid=True,
                created__date__gte=month_start
            ).aggregate(total=Sum('payment_amount'))['total'] or 0
            
            return JsonResponse({
                'total': total_revenue,
                'today': today_revenue,
                'week': float(week_revenue),
                'month': float(month_revenue),
                'paypal': float(paypal_total)
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class ServicesListView(View):
    def get(self, request):
        try:
            # Return actual PayPal services
            services = PayPalService.objects.all().order_by('name')
            services_data = []
            
            for service in services:
                booking_count = PayPalBooking.objects.filter(service=service).count()
                services_data.append({
                    'id': service.id,
                    'code': service.code,
                    'name': service.name,
                    'description': service.description,
                    'price': float(service.price),
                    'active': service.active,
                    'booking_count': booking_count
                })
            
            return JsonResponse({'results': services_data})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    def post(self, request):
        """Create a new service"""
        try:
            data = json.loads(request.body)
            
            # Validate required fields
            required_fields = ['code', 'name', 'price']
            for field in required_fields:
                if not data.get(field):
                    return JsonResponse({'error': f'{field} is required'}, status=400)
            
            # Check if code already exists
            if PayPalService.objects.filter(code=data['code']).exists():
                return JsonResponse({'error': 'Service code already exists'}, status=400)
            
            service = PayPalService.objects.create(
                code=data['code'],
                name=data['name'],
                description=data.get('description', ''),
                price=data['price'],
                active=data.get('active', True)
            )
            
            return JsonResponse({
                'message': 'Service created successfully',
                'service_id': service.id
            }, status=201)
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        except Exception as e:
            logger.error(f"Error creating service: {e}")
            return JsonResponse({'error': str(e)}, status=500)

# Vehicles functionality removed as requested

@method_decorator(csrf_exempt, name='dispatch')
class ServiceDetailView(View):
    def get(self, request, service_id):
        """Get individual service details"""
        try:
            service = PayPalService.objects.get(id=service_id)
            booking_count = PayPalBooking.objects.filter(service=service).count()
            
            service_data = {
                'id': service.id,
                'code': service.code,
                'name': service.name,
                'description': service.description,
                'price': float(service.price),
                'active': service.active,
                'booking_count': booking_count
            }
            
            return JsonResponse(service_data)
        except PayPalService.DoesNotExist:
            return JsonResponse({'error': 'Service not found'}, status=404)
        except Exception as e:
            logger.error(f"Error fetching service {service_id}: {e}")
            return JsonResponse({'error': str(e)}, status=500)
    
    def put(self, request, service_id):
        """Update service"""
        try:
            service = PayPalService.objects.get(id=service_id)
            data = json.loads(request.body)
            
            # Update fields if provided
            if 'code' in data:
                # Check if code already exists for other services
                if PayPalService.objects.filter(code=data['code']).exclude(id=service_id).exists():
                    return JsonResponse({'error': 'Service code already exists'}, status=400)
                service.code = data['code']
            
            for field in ['name', 'description', 'price']:
                if field in data:
                    setattr(service, field, data[field])
            
            if 'active' in data:
                service.active = bool(data['active'])
            
            service.save()
            
            logger.info(f"Service {service_id} updated successfully")
            return JsonResponse({'message': 'Service updated successfully'})
            
        except PayPalService.DoesNotExist:
            return JsonResponse({'error': 'Service not found'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        except Exception as e:
            logger.error(f"Error updating service {service_id}: {e}")
            return JsonResponse({'error': str(e)}, status=500)
    
    def delete(self, request, service_id):
        """Delete service"""
        try:
            service = PayPalService.objects.get(id=service_id)
            
            # Check if service has bookings
            booking_count = PayPalBooking.objects.filter(service=service).count()
            if booking_count > 0:
                return JsonResponse({
                    'error': f'Cannot delete service. It has {booking_count} associated bookings.'
                }, status=400)
            
            service.delete()
            
            logger.info(f"Service {service_id} deleted successfully")
            return JsonResponse({'message': 'Service deleted successfully'})
            
        except PayPalService.DoesNotExist:
            return JsonResponse({'error': 'Service not found'}, status=404)
        except Exception as e:
            logger.error(f"Error deleting service {service_id}: {e}")
            return JsonResponse({'error': str(e)}, status=500)