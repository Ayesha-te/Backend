from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import datetime, timedelta
import random

from accounts.models import Vehicle, Document
from PAYPAL.models import Service as PaypalService, Booking as PaypalBooking
from DVLAA.models import Service as DVLAService, Booking as DVLABooking

User = get_user_model()


class Command(BaseCommand):
    help = 'Create sample data for testing the admin panel'

    def add_arguments(self, parser):
        parser.add_argument(
            '--users',
            type=int,
            default=10,
            help='Number of users to create'
        )
        parser.add_argument(
            '--services',
            type=int,
            default=5,
            help='Number of services to create for each app'
        )
        parser.add_argument(
            '--bookings',
            type=int,
            default=20,
            help='Number of bookings to create'
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Creating sample data...'))
        
        # Create users
        users_count = options['users']
        self.create_users(users_count)
        
        # Create services
        services_count = options['services']
        self.create_paypal_services(services_count)
        self.create_dvla_services(services_count)
        
        # Create bookings
        bookings_count = options['bookings']
        self.create_bookings(bookings_count)
        
        # Create vehicles and documents
        self.create_vehicles_and_documents()
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created sample data:\n'
                f'- {users_count} users\n'
                f'- {services_count * 2} services\n'
                f'- {bookings_count} bookings\n'
                f'- Vehicles and documents for users'
            )
        )

    def create_users(self, count):
        """Create sample users"""
        self.stdout.write('Creating users...')
        
        sample_users = [
            {'email': 'john.doe@example.com', 'first_name': 'John', 'last_name': 'Doe'},
            {'email': 'jane.smith@example.com', 'first_name': 'Jane', 'last_name': 'Smith'},
            {'email': 'mike.johnson@example.com', 'first_name': 'Mike', 'last_name': 'Johnson'},
            {'email': 'sarah.wilson@example.com', 'first_name': 'Sarah', 'last_name': 'Wilson'},
            {'email': 'david.brown@example.com', 'first_name': 'David', 'last_name': 'Brown'},
            {'email': 'lisa.davis@example.com', 'first_name': 'Lisa', 'last_name': 'Davis'},
            {'email': 'tom.miller@example.com', 'first_name': 'Tom', 'last_name': 'Miller'},
            {'email': 'emma.garcia@example.com', 'first_name': 'Emma', 'last_name': 'Garcia'},
            {'email': 'james.martinez@example.com', 'first_name': 'James', 'last_name': 'Martinez'},
            {'email': 'olivia.anderson@example.com', 'first_name': 'Olivia', 'last_name': 'Anderson'},
        ]
        
        for i in range(count):
            if i < len(sample_users):
                user_data = sample_users[i]
            else:
                user_data = {
                    'email': f'user{i+1}@example.com',
                    'first_name': f'User{i+1}',
                    'last_name': 'Test'
                }
            
            if not User.objects.filter(email=user_data['email']).exists():
                user = User.objects.create_user(
                    email=user_data['email'],
                    password='testpass123',
                    first_name=user_data['first_name'],
                    last_name=user_data['last_name']
                )
                # Randomize join dates
                days_ago = random.randint(1, 365)
                user.date_joined = timezone.now() - timedelta(days=days_ago)
                user.save()

    def create_paypal_services(self, count):
        """Create sample PayPal services"""
        self.stdout.write('Creating PayPal services...')
        
        sample_services = [
            {
                'code': 'MOT_CLASS_4',
                'name': 'MOT Test - Class 4 (Cars)',
                'description': 'Annual MOT test for cars and light vans',
                'price': 54.85
            },
            {
                'code': 'MOT_CLASS_7',
                'name': 'MOT Test - Class 7 (Heavy Goods)',
                'description': 'Annual MOT test for heavy goods vehicles',
                'price': 124.50
            },
            {
                'code': 'VEHICLE_INSPECTION',
                'name': 'Pre-Purchase Vehicle Inspection',
                'description': 'Comprehensive vehicle inspection before purchase',
                'price': 89.99
            },
            {
                'code': 'BRAKE_TEST',
                'name': 'Brake Performance Test',
                'description': 'Professional brake system testing',
                'price': 45.00
            },
            {
                'code': 'EMISSIONS_TEST',
                'name': 'Emissions Test',
                'description': 'Vehicle emissions testing and certification',
                'price': 35.00
            },
        ]
        
        for i in range(count):
            if i < len(sample_services):
                service_data = sample_services[i]
            else:
                service_data = {
                    'code': f'SERVICE_{i+1}',
                    'name': f'Service {i+1}',
                    'description': f'Description for service {i+1}',
                    'price': random.uniform(25.00, 150.00)
                }
            
            if not PaypalService.objects.filter(code=service_data['code']).exists():
                PaypalService.objects.create(**service_data)

    def create_dvla_services(self, count):
        """Create sample DVLA services"""
        self.stdout.write('Creating DVLA services...')
        
        sample_services = [
            {
                'name': 'Vehicle Registration Check',
                'description': 'Check vehicle registration details',
                'price': 2.50,
                'duration_minutes': 5
            },
            {
                'name': 'MOT History Check',
                'description': 'View complete MOT test history',
                'price': 3.00,
                'duration_minutes': 10
            },
            {
                'name': 'Tax Status Check',
                'description': 'Check vehicle tax status and expiry',
                'price': 2.00,
                'duration_minutes': 5
            },
            {
                'name': 'Insurance Status Check',
                'description': 'Verify vehicle insurance status',
                'price': 4.00,
                'duration_minutes': 10
            },
            {
                'name': 'Vehicle Valuation',
                'description': 'Get current market value of vehicle',
                'price': 9.99,
                'duration_minutes': 15
            },
        ]
        
        for i in range(count):
            if i < len(sample_services):
                service_data = sample_services[i]
            else:
                service_data = {
                    'name': f'DVLA Service {i+1}',
                    'description': f'Description for DVLA service {i+1}',
                    'price': random.uniform(2.00, 15.00),
                    'duration_minutes': random.choice([5, 10, 15, 30, 60])
                }
            
            if not DVLAService.objects.filter(name=service_data['name']).exists():
                DVLAService.objects.create(**service_data)

    def create_bookings(self, count):
        """Create sample bookings"""
        self.stdout.write('Creating bookings...')
        
        users = list(User.objects.all())
        paypal_services = list(PaypalService.objects.all())
        dvla_services = list(DVLAService.objects.all())
        
        if not users:
            self.stdout.write(self.style.WARNING('No users found. Creating bookings skipped.'))
            return
        if not paypal_services:
            self.stdout.write(self.style.WARNING('No PayPal services found. Creating PayPal bookings skipped.'))
        if not dvla_services:
            self.stdout.write(self.style.WARNING('No DVLA services found. Creating DVLA bookings skipped.'))
        
        # Create PayPal bookings
        if paypal_services:
            for i in range(count // 2):
                try:
                    user = random.choice(users)
                    service = random.choice(paypal_services)
                    
                    # Random date within last 90 days or next 30 days
                    days_offset = random.randint(-90, 30)
                    booking_date = timezone.now().date() + timedelta(days=days_offset)
                    
                    PaypalBooking.objects.create(
                        user=user,
                        service=service,
                        date=booking_date,
                        time=f"{random.randint(9, 17):02d}:{random.choice(['00', '30'])}",
                        customer_first_name=user.first_name or 'John',
                        customer_last_name=user.last_name or 'Doe',
                        customer_email=user.email,
                        customer_phone=f"07{random.randint(100000000, 999999999)}",
                        vehicle_make=random.choice(['Ford', 'Vauxhall', 'BMW', 'Audi', 'Toyota']),
                        vehicle_model=random.choice(['Focus', 'Corsa', '3 Series', 'A4', 'Corolla']),
                        vehicle_year=str(random.randint(2010, 2023)),
                        vehicle_registration=f"{random.choice(['AB', 'CD', 'EF'])}{random.randint(10, 99)} {random.choice(['ABC', 'DEF', 'GHI'])}",
                        is_paid=random.choice([True, False]),
                        is_verified=random.choice([True, False]),
                        payment_status=random.choice(['completed', 'pending', 'failed']),
                    )
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error creating PayPal booking {i}: {str(e)}'))
        
        # Create DVLA bookings
        if dvla_services:
            for i in range(count // 2):
                try:
                    user = random.choice(users)
                    service = random.choice(dvla_services)
                    
                    # Random datetime within last 60 days or next 30 days
                    days_offset = random.randint(-60, 30)
                    hours_offset = random.randint(0, 23)
                    scheduled_for = timezone.now() + timedelta(days=days_offset, hours=hours_offset)
                    
                    DVLABooking.objects.create(
                        user=user,
                        service=service,
                        quantity=random.randint(1, 3),
                        motClass=random.choice(['Class 4', 'Class 7', 'Class 1', 'Class 2']),
                        scheduled_for=scheduled_for,
                        payment_completed=random.choice([True, False]),
                        payment_method=random.choice(['card', 'paypal', 'bank_transfer']),
                        status=random.choice(['pending', 'confirmed', 'cancelled']),
                    )
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error creating DVLA booking {i}: {str(e)}'))

    def create_vehicles_and_documents(self):
        """Create sample vehicles and documents"""
        self.stdout.write('Creating vehicles and documents...')
        
        users = User.objects.all()
        
        makes_models = [
            ('Ford', 'Focus'), ('Ford', 'Fiesta'), ('Vauxhall', 'Corsa'),
            ('BMW', '3 Series'), ('Audi', 'A4'), ('Toyota', 'Corolla'),
            ('Volkswagen', 'Golf'), ('Mercedes', 'C-Class'), ('Nissan', 'Qashqai')
        ]
        
        for user in users:
            try:
                # Create 1-2 vehicles per user
                num_vehicles = random.randint(1, 2)
                
                for _ in range(num_vehicles):
                    make, model = random.choice(makes_models)
                    
                    # Random MOT expiry date
                    mot_expiry = timezone.now().date() + timedelta(days=random.randint(-30, 365))
                    last_service = timezone.now().date() - timedelta(days=random.randint(30, 365))
                    
                    vehicle = Vehicle.objects.create(
                        user=user,
                        make=make,
                        model=model,
                        year=random.randint(2010, 2023),
                        registration=f"{random.choice(['AB', 'CD', 'EF'])}{random.randint(10, 99)} {random.choice(['ABC', 'DEF', 'GHI'])}",
                        mileage=random.randint(10000, 150000),
                        mot_expiry=mot_expiry,
                        last_service=last_service
                    )
                    
                    # Create documents for this vehicle
                    doc_types = ['MOT Certificate', 'Service Record', 'Insurance Certificate']
                    for doc_type in random.sample(doc_types, random.randint(1, 3)):
                        try:
                            Document.objects.create(
                                user=user,
                                doc_type=doc_type,
                                date=timezone.now().date() - timedelta(days=random.randint(1, 365)),
                                vehicle=vehicle.registration,
                                status=random.choice(['approved', 'pending', 'rejected'])
                            )
                        except Exception as e:
                            self.stdout.write(self.style.ERROR(f'Error creating document for {user.email}: {str(e)}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error creating vehicle for {user.email}: {str(e)}'))