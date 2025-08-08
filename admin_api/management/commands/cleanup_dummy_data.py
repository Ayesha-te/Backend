from django.core.management.base import BaseCommand
from django.db import transaction
from accounts.models import CustomUser, Vehicle, Document, Booking as AccountsBooking
from PAYPAL.models import Booking as PaypalBooking, Service as PaypalService
from DVLAA.models import Booking as DvlaaBooking, Service as DvlaaService, CartItem
from django.contrib.auth import get_user_model
import re

User = get_user_model()

class Command(BaseCommand):
    help = 'Clean up dummy data from the database and keep only real PayPal payments'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force deletion without confirmation',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        force = options['force']

        self.stdout.write(self.style.SUCCESS('Starting cleanup of dummy data...'))
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No data will be deleted'))

        # Identify dummy data patterns
        dummy_email_patterns = [
            r'.*@example\.com$',
            r'.*@test\.com$',
            r'.*@dummy\.com$',
            r'.*@fake\.com$',
            r'test.*@.*',
            r'dummy.*@.*',
            r'fake.*@.*',
            r'sample.*@.*',
        ]

        # Find dummy users
        dummy_users = []
        for pattern in dummy_email_patterns:
            users = User.objects.filter(email__iregex=pattern)
            dummy_users.extend(users)

        # Remove duplicates
        dummy_users = list(set(dummy_users))

        # Also find users with obviously fake names
        fake_name_users = User.objects.filter(
            first_name__in=['Test', 'Dummy', 'Fake', 'Sample', 'John', 'Jane']
        ).filter(
            last_name__in=['User', 'Test', 'Dummy', 'Fake', 'Sample', 'Doe']
        )
        dummy_users.extend(fake_name_users)
        dummy_users = list(set(dummy_users))

        # Keep only superusers and staff
        dummy_users = [user for user in dummy_users if not (user.is_superuser or user.is_staff)]

        self.stdout.write(f'Found {len(dummy_users)} dummy users to clean up')

        # Find bookings with non-PayPal payment methods
        non_paypal_bookings = PaypalBooking.objects.exclude(payment_method='paypal')
        
        # Find bookings without proper PayPal transaction IDs
        invalid_paypal_bookings = PaypalBooking.objects.filter(
            payment_method='paypal'
        ).filter(
            paypal_transaction_id__isnull=True
        ).exclude(
            is_paid=True
        )

        self.stdout.write(f'Found {non_paypal_bookings.count()} non-PayPal bookings')
        self.stdout.write(f'Found {invalid_paypal_bookings.count()} invalid PayPal bookings')

        # Find all DVLAA bookings (since we're removing vehicle functionality)
        dvlaa_bookings = DvlaaBooking.objects.all()
        dvlaa_services = DvlaaService.objects.all()
        cart_items = CartItem.objects.all()

        self.stdout.write(f'Found {dvlaa_bookings.count()} DVLAA bookings to remove')
        self.stdout.write(f'Found {dvlaa_services.count()} DVLAA services to remove')
        self.stdout.write(f'Found {cart_items.count()} cart items to remove')

        # Find all vehicles and documents
        vehicles = Vehicle.objects.all()
        documents = Document.objects.all()
        accounts_bookings = AccountsBooking.objects.all()

        self.stdout.write(f'Found {vehicles.count()} vehicles to remove')
        self.stdout.write(f'Found {documents.count()} documents to remove')
        self.stdout.write(f'Found {accounts_bookings.count()} accounts bookings to remove')

        if not force and not dry_run:
            confirm = input('Are you sure you want to proceed with cleanup? (yes/no): ')
            if confirm.lower() != 'yes':
                self.stdout.write(self.style.ERROR('Cleanup cancelled'))
                return

        if not dry_run:
            with transaction.atomic():
                # Delete in order to avoid foreign key constraints
                
                # 1. Delete DVLAA related data
                deleted_cart_items = cart_items.count()
                cart_items.delete()
                self.stdout.write(f'Deleted {deleted_cart_items} cart items')

                deleted_dvlaa_bookings = dvlaa_bookings.count()
                dvlaa_bookings.delete()
                self.stdout.write(f'Deleted {deleted_dvlaa_bookings} DVLAA bookings')

                deleted_dvlaa_services = dvlaa_services.count()
                dvlaa_services.delete()
                self.stdout.write(f'Deleted {deleted_dvlaa_services} DVLAA services')

                # 2. Delete vehicle-related data
                deleted_documents = documents.count()
                documents.delete()
                self.stdout.write(f'Deleted {deleted_documents} documents')

                deleted_vehicles = vehicles.count()
                vehicles.delete()
                self.stdout.write(f'Deleted {deleted_vehicles} vehicles')

                deleted_accounts_bookings = accounts_bookings.count()
                accounts_bookings.delete()
                self.stdout.write(f'Deleted {deleted_accounts_bookings} accounts bookings')

                # 3. Delete non-PayPal bookings
                deleted_non_paypal = non_paypal_bookings.count()
                non_paypal_bookings.delete()
                self.stdout.write(f'Deleted {deleted_non_paypal} non-PayPal bookings')

                deleted_invalid_paypal = invalid_paypal_bookings.count()
                invalid_paypal_bookings.delete()
                self.stdout.write(f'Deleted {deleted_invalid_paypal} invalid PayPal bookings')

                # 4. Delete dummy users (this will cascade to their bookings)
                deleted_users = len(dummy_users)
                for user in dummy_users:
                    user.delete()
                self.stdout.write(f'Deleted {deleted_users} dummy users')

                self.stdout.write(self.style.SUCCESS('Cleanup completed successfully!'))
        else:
            self.stdout.write(self.style.WARNING('DRY RUN - No data was actually deleted'))

        # Show final statistics
        self.stdout.write('\n' + '='*50)
        self.stdout.write('CLEANUP SUMMARY:')
        self.stdout.write('='*50)
        
        if not dry_run:
            remaining_users = User.objects.count()
            remaining_paypal_bookings = PaypalBooking.objects.count()
            remaining_paypal_services = PaypalService.objects.count()
            
            self.stdout.write(f'Remaining users: {remaining_users}')
            self.stdout.write(f'Remaining PayPal bookings: {remaining_paypal_bookings}')
            self.stdout.write(f'Remaining PayPal services: {remaining_paypal_services}')
            self.stdout.write(f'Remaining DVLAA bookings: 0')
            self.stdout.write(f'Remaining vehicles: 0')
            self.stdout.write(f'Remaining documents: 0')
        else:
            self.stdout.write('Run without --dry-run to perform actual cleanup')

        self.stdout.write(self.style.SUCCESS('\nCleanup process completed!'))