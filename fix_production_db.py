#!/usr/bin/env python
"""
Quick fix for production database issues
Run this script on your production server to create missing tables and populate data
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.core.management import call_command
from django.db import connection

def check_table_exists(table_name):
    """Check if a table exists in the database"""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name=?;
        """, [table_name])
        return cursor.fetchone() is not None

def main():
    print("🔧 Fixing production database...")
    
    # Check if PAYPAL_service table exists
    if not check_table_exists('PAYPAL_service'):
        print("❌ PAYPAL_service table missing. Running migrations...")
        
        # Run migrations
        try:
            call_command('migrate', verbosity=2)
            print("✅ Migrations completed!")
        except Exception as e:
            print(f"❌ Migration error: {e}")
            return
    else:
        print("✅ PAYPAL_service table exists")
    
    # Populate services
    try:
        call_command('populate_services')
        print("✅ Services populated!")
    except Exception as e:
        print(f"❌ Service population error: {e}")
        return
    
    # Verify services exist
    from PAYPAL.models import Service
    service_count = Service.objects.count()
    print(f"✅ Database now has {service_count} services")
    
    if service_count > 0:
        print("🎉 Production database fixed successfully!")
        print("Your API endpoints should now work correctly.")
    else:
        print("⚠️  No services found. Please check the populate_services command.")

if __name__ == '__main__':
    main()