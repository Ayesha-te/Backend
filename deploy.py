#!/usr/bin/env python
"""
Deployment script to ensure static files are properly collected and cached
"""
import os
import sys
import django
from django.core.management import execute_from_command_line
from django.conf import settings

def main():
    """Run deployment tasks"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
    django.setup()
    
    print("🚀 Starting deployment process...")
    
    # Collect static files
    print("📁 Collecting static files...")
    execute_from_command_line(['manage.py', 'collectstatic', '--noinput', '--clear'])
    
    # Run migrations
    print("🔄 Running migrations...")
    execute_from_command_line(['manage.py', 'migrate'])
    
    # Create real services if they don't exist
    print("🛠️ Creating real services...")
    try:
        execute_from_command_line(['manage.py', 'create_real_services'])
    except:
        print("⚠️ Services already exist or command not found")
    
    # Clean up dummy data
    print("🧹 Cleaning up dummy data...")
    try:
        execute_from_command_line(['manage.py', 'cleanup_dummy_data', '--force'])
    except:
        print("⚠️ Cleanup command not found or already clean")
    
    print("✅ Deployment completed successfully!")
    print("🌐 Admin panel available at: /static/admin/login.html")

if __name__ == '__main__':
    main()