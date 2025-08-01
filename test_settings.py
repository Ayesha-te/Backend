#!/usr/bin/env python3
"""
Test Django settings configuration
"""

import os
import django
from django.conf import settings

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

def test_settings():
    """Test critical Django settings"""
    print("=== Django Settings Test ===")
    print(f"DEBUG: {settings.DEBUG}")
    print(f"SECRET_KEY: {'*' * 20} (hidden)")
    print(f"ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
    print(f"CORS_ALLOWED_ORIGINS: {getattr(settings, 'CORS_ALLOWED_ORIGINS', 'Not set')}")
    
    # Check if critical settings are properly configured
    issues = []
    
    if settings.DEBUG:
        issues.append("⚠️  DEBUG is True - should be False in production")
    
    if 'django-insecure' in settings.SECRET_KEY:
        issues.append("⚠️  SECRET_KEY appears to be insecure")
    
    if '*' in settings.ALLOWED_HOSTS:
        issues.append("⚠️  ALLOWED_HOSTS contains '*' - too permissive for production")
    
    if not hasattr(settings, 'CORS_ALLOWED_ORIGINS'):
        issues.append("⚠️  CORS_ALLOWED_ORIGINS not configured")
    
    if issues:
        print("\n=== Issues Found ===")
        for issue in issues:
            print(issue)
    else:
        print("\n✅ All critical settings look good!")
    
    print("\n=== Apps Installed ===")
    for app in settings.INSTALLED_APPS:
        print(f"  - {app}")

if __name__ == '__main__':
    test_settings()