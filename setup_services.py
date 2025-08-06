#!/usr/bin/env python
"""
Setup script to ensure services match frontend expectations
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from PAYPAL.models import Service

# Services that your frontend expects (from your React component)
expected_services = [
    {'id': 1, 'code': 'mot', 'name': 'MOT Test', 'price': 54.85, 'description': 'Official MOT testing for Class 4, 5 & 7 vehicles'},
    {'id': 2, 'code': 'service', 'name': 'Full Service', 'price': 89.00, 'description': 'Complete vehicle health check and maintenance'},
    {'id': 3, 'code': 'repair', 'name': 'Vehicle Repair', 'price': 0, 'description': 'Custom repair based on your vehicle needs'},
    {'id': 4, 'code': 'brakes', 'name': 'Brake Service', 'price': 120.00, 'description': 'Brake inspection and replacement'},
    {'id': 5, 'code': 'battery', 'name': 'Battery Service', 'price': 80.00, 'description': 'Battery testing and replacement'},
    {'id': 6, 'code': 'clutch', 'name': 'Clutch Repair', 'price': 0, 'description': 'Clutch repair and replacement'},
    {'id': 7, 'code': 'exhaust', 'name': 'Exhaust Service', 'price': 150.00, 'description': 'Exhaust system inspection and repair'},
    {'id': 8, 'code': 'diagnostics', 'name': 'Vehicle Diagnostics', 'price': 45.00, 'description': 'Comprehensive diagnostic scan'}
]

def setup_services():
    print("Setting up services to match frontend expectations...")
    
    for service_data in expected_services:
        service, created = Service.objects.get_or_create(
            id=service_data['id'],
            defaults={
                'code': service_data['code'],
                'name': service_data['name'],
                'price': service_data['price'],
                'description': service_data['description'],
                'active': True
            }
        )
        
        if created:
            print(f"✅ Created service: {service.name} (ID: {service.id})")
        else:
            # Update existing service if needed
            updated = False
            if service.code != service_data['code']:
                service.code = service_data['code']
                updated = True
            if service.name != service_data['name']:
                service.name = service_data['name']
                updated = True
            if service.price != service_data['price']:
                service.price = service_data['price']
                updated = True
            if service.description != service_data['description']:
                service.description = service_data['description']
                updated = True
            if not service.active:
                service.active = True
                updated = True
                
            if updated:
                service.save()
                print(f"🔄 Updated service: {service.name} (ID: {service.id})")
            else:
                print(f"✓ Service already exists: {service.name} (ID: {service.id})")
    
    print(f"\n📊 Total services in database: {Service.objects.count()}")
    print("Services setup complete!")

if __name__ == '__main__':
    setup_services()