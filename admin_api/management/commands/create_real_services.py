from django.core.management.base import BaseCommand
from PAYPAL.models import Service as PaypalService

class Command(BaseCommand):
    help = 'Create real services for the admin panel'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Creating real services...'))
        
        services = [
            {
                'code': 'MOT_CLASS_4',
                'name': 'MOT Test - Class 4 (Cars)',
                'description': 'Annual MOT test for cars and light vans up to 3,000kg',
                'price': 54.85
            },
            {
                'code': 'MOT_CLASS_7',
                'name': 'MOT Test - Class 7 (Heavy Goods)',
                'description': 'Annual MOT test for heavy goods vehicles over 3,500kg',
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
                'description': 'Professional brake system testing and certification',
                'price': 45.00
            },
            {
                'code': 'EMISSIONS_TEST',
                'name': 'Emissions Test',
                'description': 'Vehicle emissions testing and environmental compliance check',
                'price': 35.00
            },
            {
                'code': 'HEADLIGHT_TEST',
                'name': 'Headlight Alignment Test',
                'description': 'Professional headlight alignment and beam pattern testing',
                'price': 25.00
            },
            {
                'code': 'TYRE_CHECK',
                'name': 'Tyre Safety Check',
                'description': 'Comprehensive tyre condition and safety assessment',
                'price': 20.00
            },
            {
                'code': 'BATTERY_TEST',
                'name': 'Battery Health Check',
                'description': 'Complete battery performance and health assessment',
                'price': 15.00
            }
        ]
        
        created_count = 0
        for service_data in services:
            service, created = PaypalService.objects.get_or_create(
                code=service_data['code'],
                defaults=service_data
            )
            if created:
                created_count += 1
                self.stdout.write(f'Created service: {service.name}')
            else:
                self.stdout.write(f'Service already exists: {service.name}')
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} new services!')
        )