from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from accounts.models import Vehicle, Document
from PAYPAL.models import Service as PaypalService, Booking as PaypalBooking
from DVLAA.models import Service as DVLAService, Booking as DVLABooking

User = get_user_model()


class Command(BaseCommand):
    help = 'Test admin panel data and display statistics'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=== ADMIN PANEL TEST ==='))
        
        # Test Users
        users_count = User.objects.count()
        active_users = User.objects.filter(is_active=True).count()
        staff_users = User.objects.filter(is_staff=True).count()
        
        self.stdout.write(f'👥 Users: {users_count} total, {active_users} active, {staff_users} staff')
        
        # Test PayPal Services
        paypal_services = PaypalService.objects.count()
        active_paypal_services = PaypalService.objects.filter(active=True).count()
        
        self.stdout.write(f'🔧 PayPal Services: {paypal_services} total, {active_paypal_services} active')
        
        # Test DVLA Services
        dvla_services = DVLAService.objects.count()
        
        self.stdout.write(f'🚗 DVLA Services: {dvla_services} total')
        
        # Test Bookings
        paypal_bookings = PaypalBooking.objects.count()
        paid_paypal_bookings = PaypalBooking.objects.filter(is_paid=True).count()
        
        dvla_bookings = DVLABooking.objects.count()
        paid_dvla_bookings = DVLABooking.objects.filter(payment_completed=True).count()
        
        total_bookings = paypal_bookings + dvla_bookings
        total_paid = paid_paypal_bookings + paid_dvla_bookings
        
        self.stdout.write(f'📅 Bookings: {total_bookings} total ({total_paid} paid)')
        self.stdout.write(f'   - PayPal: {paypal_bookings} total ({paid_paypal_bookings} paid)')
        self.stdout.write(f'   - DVLA: {dvla_bookings} total ({paid_dvla_bookings} paid)')
        
        # Test Vehicles
        vehicles_count = Vehicle.objects.count()
        self.stdout.write(f'🚙 Vehicles: {vehicles_count} total')
        
        # Test Documents
        documents_count = Document.objects.count()
        approved_docs = Document.objects.filter(status='approved').count()
        
        self.stdout.write(f'📄 Documents: {documents_count} total ({approved_docs} approved)')
        
        # Revenue calculation
        paypal_revenue = 0
        for booking in PaypalBooking.objects.filter(is_paid=True).select_related('service'):
            paypal_revenue += float(booking.service.price)
        
        dvla_revenue = 0
        for booking in DVLABooking.objects.filter(payment_completed=True).select_related('service'):
            dvla_revenue += float(booking.service.price) * booking.quantity
        
        total_revenue = paypal_revenue + dvla_revenue
        
        self.stdout.write(f'💰 Revenue: £{total_revenue:.2f} total')
        self.stdout.write(f'   - PayPal: £{paypal_revenue:.2f}')
        self.stdout.write(f'   - DVLA: £{dvla_revenue:.2f}')
        
        self.stdout.write(self.style.SUCCESS('\n✅ Admin panel test completed successfully!'))
        
        if total_bookings == 0:
            self.stdout.write(self.style.WARNING('\n⚠️  No bookings found. Run: python manage.py create_sample_data'))
        
        self.stdout.write(self.style.SUCCESS('\n🌐 Access admin panel at: http://127.0.0.1:8000/admin/'))
        self.stdout.write('📊 Custom dashboard at: http://127.0.0.1:8000/admin-dashboard/')