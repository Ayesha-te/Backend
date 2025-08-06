#!/usr/bin/env python
"""
Integration test to verify backend works with frontend
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from PAYPAL.models import Service
from PAYPAL.paypal_utils import paypal_api
from django.conf import settings
from django.core.mail import send_mail

def test_services():
    """Test that services match frontend expectations"""
    print("=== TESTING SERVICES ===")
    services = Service.objects.filter(active=True).order_by('id')
    print(f"Active services count: {services.count()}")
    
    expected_ids = [1, 2, 3, 4, 5, 6, 7, 8]
    existing_ids = list(services.values_list('id', flat=True))
    
    for expected_id in expected_ids:
        if expected_id in existing_ids:
            service = services.get(id=expected_id)
            print(f"✅ Service ID {expected_id}: {service.name} - £{service.price}")
        else:
            print(f"❌ Missing service ID {expected_id}")
    
    return all(id in existing_ids for id in expected_ids)

def test_paypal_config():
    """Test PayPal configuration"""
    print("\n=== TESTING PAYPAL CONFIG ===")
    
    client_id_ok = bool(paypal_api.client_id)
    secret_ok = bool(paypal_api.client_secret)
    api_base_ok = bool(paypal_api.api_base)
    
    print(f"PayPal Client ID configured: {'✅' if client_id_ok else '❌'}")
    print(f"PayPal Secret configured: {'✅' if secret_ok else '❌'}")
    print(f"PayPal API Base: {paypal_api.api_base}")
    
    if client_id_ok and secret_ok:
        try:
            token = paypal_api.get_access_token()
            print(f"PayPal token generation: ✅ SUCCESS")
            return True
        except Exception as e:
            print(f"PayPal token generation: ❌ FAILED - {e}")
            return False
    else:
        print("PayPal configuration incomplete")
        return False

def test_email_config():
    """Test email configuration"""
    print("\n=== TESTING EMAIL CONFIG ===")
    
    print(f"Email Backend: {settings.EMAIL_BACKEND}")
    print(f"Email Host: {settings.EMAIL_HOST}")
    print(f"Email Port: {settings.EMAIL_PORT}")
    print(f"Email Use SSL: {settings.EMAIL_USE_SSL}")
    print(f"Email Host User: {settings.EMAIL_HOST_USER}")
    print(f"Default From Email: {settings.DEFAULT_FROM_EMAIL}")
    
    try:
        # Test email sending
        result = send_mail(
            'Backend Test Email',
            'This is a test email to verify backend email configuration.',
            settings.DEFAULT_FROM_EMAIL,
            [settings.OWNER_EMAIL],
            fail_silently=False,
        )
        print(f"Email test: {'✅ SUCCESS' if result == 1 else '❌ FAILED'}")
        return result == 1
    except Exception as e:
        print(f"Email test: ❌ FAILED - {e}")
        return False

def test_api_endpoints():
    """Test that all expected API endpoints exist"""
    print("\n=== TESTING API ENDPOINTS ===")
    
    from django.urls import reverse
    from django.test import Client
    
    client = Client()
    
    endpoints = [
        ('paypal:services-list', 'GET'),
        ('paypal:booking-list-create', 'GET'),
        ('paypal:paypal-create-order', 'POST'),
        ('paypal:paypal-capture-payment', 'POST'),
        ('email-verification', 'POST'),
        ('booking-reminder', 'POST'),
    ]
    
    for endpoint_name, method in endpoints:
        try:
            if endpoint_name.startswith('paypal:'):
                url = reverse(endpoint_name)
            else:
                url = f"/api/email/{endpoint_name.replace('-', '/')}/"
            
            if method == 'GET':
                response = client.get(url)
            else:
                response = client.post(url, {}, content_type='application/json')
            
            # We expect 401 (unauthorized) or 400 (bad request) for most endpoints
            # 200 is OK for services list
            if response.status_code in [200, 400, 401]:
                print(f"✅ {method} {url} - Status: {response.status_code}")
            else:
                print(f"❌ {method} {url} - Status: {response.status_code}")
                
        except Exception as e:
            print(f"❌ {endpoint_name} - Error: {e}")

def main():
    """Run all tests"""
    print("🚀 Starting Backend Integration Tests\n")
    
    services_ok = test_services()
    paypal_ok = test_paypal_config()
    email_ok = test_email_config()
    test_api_endpoints()
    
    print(f"\n=== TEST SUMMARY ===")
    print(f"Services: {'✅ PASS' if services_ok else '❌ FAIL'}")
    print(f"PayPal: {'✅ PASS' if paypal_ok else '❌ FAIL'}")
    print(f"Email: {'✅ PASS' if email_ok else '❌ FAIL'}")
    
    if services_ok and paypal_ok and email_ok:
        print(f"\n🎉 ALL TESTS PASSED! Your backend is ready for the frontend.")
    else:
        print(f"\n⚠️ Some tests failed. Please check the configuration.")

if __name__ == '__main__':
    main()