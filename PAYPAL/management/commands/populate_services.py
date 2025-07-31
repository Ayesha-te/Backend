from django.core.management.base import BaseCommand
from PAYPAL.models import Service

class Command(BaseCommand):
    help = 'Populate services with predefined data'

    def handle(self, *args, **options):
        services_data = [
            {'id': 1, 'code': 'mot', 'name': 'MOT Test', 'price': 54.85, 'description': 'Official MOT testing for Class 4, 5 & 7 vehicles'},
            {'id': 2, 'code': 'service', 'name': 'Full Service', 'price': 89.00, 'description': 'Complete vehicle health check and maintenance'},
            {'id': 3, 'code': 'repair', 'name': 'Vehicle Repair', 'price': 0, 'description': 'Custom repair based on your vehicle needs'},
            {'id': 4, 'code': 'brakes', 'name': 'Brake Service', 'price': 120.00, 'description': 'Brake inspection and replacement'},
            {'id': 5, 'code': 'battery', 'name': 'Battery Service', 'price': 80.00, 'description': 'Battery testing and replacement'},
            {'id': 6, 'code': 'clutch', 'name': 'Clutch Repair', 'price': 0, 'description': 'Clutch repair and replacement'},
            {'id': 7, 'code': 'exhaust', 'name': 'Exhaust Service', 'price': 150.00, 'description': 'Exhaust system inspection and repair'},
            {'id': 8, 'code': 'diagnostics', 'name': 'Vehicle Diagnostics', 'price': 45.00, 'description': 'Comprehensive diagnostic scan'},
            # MOT subcategories
            {'id': 9, 'code': 'mot-base', 'name': 'MOT', 'price': 30, 'description': 'Basic MOT test'},
            {'id': 10, 'code': 'mot_iv', 'name': 'MOT IV', 'price': 45, 'description': 'MOT Class IV test'},
            {'id': 11, 'code': 'mot_v', 'name': 'MOT V', 'price': 49, 'description': 'MOT Class V test'},
            {'id': 12, 'code': 'motvii', 'name': 'MOT VII', 'price': 60, 'description': 'MOT Class VII test'},
        ]

        for service_data in services_data:
            service, created = Service.objects.get_or_create(
                code=service_data['code'],
                defaults={
                    'name': service_data['name'],
                    'price': service_data['price'],
                    'description': service_data['description'],
                    'active': True
                }
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully created service: {service.name}')
                )
            else:
                # Update existing service
                service.name = service_data['name']
                service.price = service_data['price']
                service.description = service_data['description']
                service.save()
                self.stdout.write(
                    self.style.WARNING(f'Updated existing service: {service.name}')
                )

        self.stdout.write(
            self.style.SUCCESS('Successfully populated all services!')
        )