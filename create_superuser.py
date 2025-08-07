#!/usr/bin/env python
"""
Script to create a superuser for Access Auto Services admin panel
"""
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

def create_superuser():
    email = 'info@access-auto-services.co.uk'
    password = 'AccessAuto2024!'  # Strong password
    first_name = 'Access Auto'
    last_name = 'Admin'
    
    # Check if user already exists
    if User.objects.filter(email=email).exists():
        user = User.objects.get(email=email)
        # Update existing user to be superuser
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.set_password(password)
        user.first_name = first_name
        user.last_name = last_name
        user.save()
        
        print(f'✅ Updated existing user {email} with admin privileges')
    else:
        # Create new superuser
        user = User.objects.create_superuser(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        
        print(f'✅ Created new superuser: {email}')
    
    print(f'''
🔐 Admin Credentials:
   Email: {email}
   Password: {password}
   Name: {first_name} {last_name}

🌐 Access URLs:
   Main Admin Panel: http://127.0.0.1:8000/admin/
   Custom Dashboard: http://127.0.0.1:8000/admin-dashboard/
   Analytics: http://127.0.0.1:8000/admin-dashboard/analytics/
   Reports: http://127.0.0.1:8000/admin-dashboard/reports/

🚀 The superuser is ready to use!
''')

if __name__ == '__main__':
    create_superuser()