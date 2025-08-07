from django.http import JsonResponse
from django.views import View
from django.contrib.auth import get_user_model
from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import datetime, timedelta
from PAYPAL.models import Booking as PayPalBooking, Service as PayPalService
from DVLAA.models import Booking as DVLABooking, Service as DVLAService
import json

User = get_user_model()

class UsersListView(View):
    def get(self, request):
        try:
            users = User.objects.all().order_by('-date_joined')
            
            # Add booking count for each user
            users_data = []
            for user in users:
                paypal_bookings = PayPalBooking.objects.filter(user=user).count()
                dvla_bookings = DVLABooking.objects.filter(user=user).count()
                
                users_data.append({
                    'id': user.id,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'is_active': user.is_active,
                    'is_staff': user.is_staff,
                    'date_joined': user.date_joined.isoformat(),
                    'booking_count': paypal_bookings + dvla_bookings
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

class BookingsListView(View):
    def get(self, request):
        try:
            # Get PayPal bookings
            paypal_bookings = PayPalBooking.objects.select_related('user').all()
            dvla_bookings = DVLABooking.objects.select_related('user').all()
            
            bookings_data = []
            
            # Add PayPal bookings
            for booking in paypal_bookings:
                bookings_data.append({
                    'id': f'PP{booking.id}',
                    'user': {
                        'first_name': booking.user.first_name if booking.user else '',
                        'last_name': booking.user.last_name if booking.user else '',
                        'email': booking.user.email if booking.user else ''
                    },
                    'service_type': booking.service.name if booking.service else 'PayPal Service',
                    'booking_date': booking.date.isoformat() if booking.date else None,
                    'booking_time': booking.time if booking.time else None,
                    'status': 'confirmed' if booking.is_verified else 'pending',
                    'payment_status': booking.payment_status,
                    'amount': float(booking.payment_amount) if booking.payment_amount else 0,
                    'created_at': booking.created.isoformat(),
                    'type': 'paypal'
                })
            
            # Add DVLA bookings
            for booking in dvla_bookings:
                bookings_data.append({
                    'id': f'DV{booking.id}',
                    'user': {
                        'first_name': booking.user.first_name if booking.user else '',
                        'last_name': booking.user.last_name if booking.user else '',
                        'email': booking.user.email if booking.user else ''
                    },
                    'service_type': booking.service.name if booking.service else 'DVLA Service',
                    'booking_date': booking.scheduled_for.date().isoformat() if booking.scheduled_for else None,
                    'booking_time': booking.scheduled_for.time().strftime('%H:%M') if booking.scheduled_for else None,
                    'status': booking.status,
                    'payment_status': 'completed' if booking.payment_completed else 'pending',
                    'amount': float(booking.service.price * booking.quantity) if booking.service else 0,
                    'created_at': booking.created_at.isoformat(),
                    'type': 'dvla'
                })
            
            # Sort by created_at descending
            bookings_data.sort(key=lambda x: x['created_at'], reverse=True)
            
            return JsonResponse({'results': bookings_data})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

class BookingsCountView(View):
    def get(self, request):
        try:
            paypal_count = PayPalBooking.objects.count()
            dvla_count = DVLABooking.objects.count()
            total_bookings = paypal_count + dvla_count
            
            # Today's bookings
            today = timezone.now().date()
            paypal_today = PayPalBooking.objects.filter(created__date=today).count()
            dvla_today = DVLABooking.objects.filter(created_at__date=today).count()
            today_bookings = paypal_today + dvla_today
            
            return JsonResponse({
                'total': total_bookings,
                'today': today_bookings,
                'paypal': paypal_count,
                'dvla': dvla_count
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

class BookingTrendsView(View):
    def get(self, request):
        try:
            # Get last 12 months data
            months = []
            paypal_data = []
            dvla_data = []
            
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
                
                dvla_count = DVLABooking.objects.filter(
                    created_at__gte=month_start,
                    created_at__lte=month_end
                ).count()
                
                paypal_data.append(paypal_count)
                dvla_data.append(dvla_count)
            
            return JsonResponse({
                'labels': months,
                'paypal_data': paypal_data,
                'dvla_data': dvla_data
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

class ServiceDistributionView(View):
    def get(self, request):
        try:
            paypal_count = PayPalBooking.objects.count()
            dvla_count = DVLABooking.objects.count()
            
            # Get service types distribution
            labels = ['PayPal Services', 'DVLA Services']
            values = [paypal_count, dvla_count]
            
            # Filter out zero values
            filtered_data = [(label, value) for label, value in zip(labels, values) if value > 0]
            
            if filtered_data:
                labels, values = zip(*filtered_data)
            else:
                labels, values = [], []
            
            return JsonResponse({
                'labels': list(labels),
                'values': list(values)
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

class PaymentsTotalView(View):
    def get(self, request):
        try:
            # Calculate total revenue from both PayPal and DVLA bookings
            paypal_total = PayPalBooking.objects.filter(
                is_paid=True
            ).aggregate(total=Sum('payment_amount'))['total'] or 0
            
            dvla_total = DVLABooking.objects.filter(
                payment_completed=True
            ).aggregate(total=Sum('service__price'))['total'] or 0
            
            total_revenue = float(paypal_total) + float(dvla_total)
            
            # Today's revenue
            today = timezone.now().date()
            paypal_today = PayPalBooking.objects.filter(
                is_paid=True,
                created__date=today
            ).aggregate(total=Sum('payment_amount'))['total'] or 0
            
            dvla_today = DVLABooking.objects.filter(
                payment_completed=True,
                created_at__date=today
            ).aggregate(total=Sum('service__price'))['total'] or 0
            
            today_revenue = float(paypal_today) + float(dvla_today)
            
            return JsonResponse({
                'total': total_revenue,
                'today': today_revenue,
                'paypal': float(paypal_total),
                'dvla': float(dvla_total)
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

class ServicesListView(View):
    def get(self, request):
        try:
            # Return available services
            services = [
                {
                    'id': 1,
                    'name': 'PayPal Services',
                    'type': 'paypal',
                    'active': True,
                    'booking_count': PayPalBooking.objects.count()
                },
                {
                    'id': 2,
                    'name': 'DVLA Services',
                    'type': 'dvla',
                    'active': True,
                    'booking_count': DVLABooking.objects.count()
                }
            ]
            
            return JsonResponse({'results': services})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

class VehiclesListView(View):
    def get(self, request):
        try:
            # Get vehicles from PayPal bookings (they have vehicle info)
            vehicles_data = []
            
            # Get unique vehicles from PayPal bookings
            paypal_bookings = PayPalBooking.objects.select_related('user').filter(
                vehicle_registration__isnull=False
            ).exclude(vehicle_registration='')
            
            for booking in paypal_bookings:
                vehicles_data.append({
                    'id': booking.id,
                    'registration': booking.vehicle_registration,
                    'make': booking.vehicle_make,
                    'model': booking.vehicle_model,
                    'year': booking.vehicle_year,
                    'user': {
                        'first_name': booking.user.first_name if booking.user else '',
                        'last_name': booking.user.last_name if booking.user else '',
                        'email': booking.user.email if booking.user else ''
                    },
                    'last_service': booking.created.isoformat()
                })
            
            return JsonResponse({'results': vehicles_data})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

class ServiceDistributionView(View):
    def get(self, request):
        try:
            # Get service distribution data
            paypal_count = PayPalBooking.objects.count()
            dvla_count = DVLABooking.objects.count()
            
            if paypal_count == 0 and dvla_count == 0:
                return JsonResponse({
                    'labels': ['No Data'],
                    'values': [1]
                })
            
            return JsonResponse({
                'labels': ['PayPal Services', 'DVLA Services'],
                'values': [paypal_count, dvla_count]
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)