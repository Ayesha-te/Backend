#!/usr/bin/env python
"""
Production deployment script for Access Auto Services Backend
This script handles database migrations and initial data setup
"""
import os
import sys
import django
from django.core.management import execute_from_command_line

def setup_django():
    """Setup Django environment"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
    django.setup()

def run_migrations():
    """Run database migrations"""
    print("🔄 Running database migrations...")
    try:
        execute_from_command_line(['manage.py', 'migrate'])
        print("✅ Database migrations completed successfully!")
        return True
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

def populate_services():
    """Populate services data"""
    print("🔄 Populating services data...")
    try:
        execute_from_command_line(['manage.py', 'populate_services'])
        print("✅ Services data populated successfully!")
        return True
    except Exception as e:
        print(f"❌ Service population failed: {e}")
        return False

def collect_static():
    """Collect static files"""
    print("🔄 Collecting static files...")
    try:
        execute_from_command_line(['manage.py', 'collectstatic', '--noinput'])
        print("✅ Static files collected successfully!")
        return True
    except Exception as e:
        print(f"❌ Static file collection failed: {e}")
        return False

def main():
    """Main deployment function"""
    print("🚀 Starting production deployment...")
    print("=" * 50)
    
    # Setup Django
    setup_django()
    
    # Run migrations
    if not run_migrations():
        sys.exit(1)
    
    # Populate services
    if not populate_services():
        sys.exit(1)
    
    # Collect static files
    if not collect_static():
        sys.exit(1)
    
    print("=" * 50)
    print("🎉 Production deployment completed successfully!")
    print("Your application is ready to serve requests.")

if __name__ == '__main__':
    main()