#!/usr/bin/env python3
"""
Check database data for debugging
"""

import os
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from PAYPAL.models import Service, Booking
from accounts.models import CustomUser

def check_data():
    print("=== Database Data Check ===")
    
    # Check services
    services = Service.objects.all()
    print(f"\n📋 Services ({services.count()}):")
    for service in services:
        print(f"  - ID: {service.id}, Name: {service.name}, Price: £{service.price}, Active: {service.active}")
    
    # Check users
    users = CustomUser.objects.all()
    print(f"\n👥 Users ({users.count()}):")
    for user in users[:5]:  # Show first 5 users
        username = getattr(user, 'username', getattr(user, 'email', 'No identifier'))
        print(f"  - ID: {user.id}, Username: {username}, Email: {user.email}")
    
    # Check bookings
    bookings = Booking.objects.all()
    print(f"\n📅 Bookings ({bookings.count()}):")
    for booking in bookings[:5]:  # Show first 5 bookings
        user_id = getattr(booking.user, 'username', getattr(booking.user, 'email', f'User {booking.user.id}'))
        print(f"  - ID: {booking.id}, User: {user_id}, Service: {booking.service.name}, Date: {booking.date}")
    
    if services.count() == 0:
        print("\n⚠️  WARNING: No services found! This could cause booking creation to fail.")
        print("   You need to create services in the admin panel or via fixtures.")
    
    if users.count() == 0:
        print("\n⚠️  WARNING: No users found!")

if __name__ == '__main__':
    check_data()