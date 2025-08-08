#!/usr/bin/env python3
"""
Test PayPal integration with simplified setup (no webhooks)
"""
import os
import sys
import django
from pathlib import Path

# Add the project directory to Python path
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from PAYPAL.paypal_utils import paypal_api
from django.conf import settings

def test_paypal_credentials():
    """Test PayPal credentials and configuration"""
    print("🔍 Testing PayPal Configuration from .env file...")
    print("=" * 50)
    
    # Check environment variables
    client_id_status = "✅ Set" if settings.PAYPAL_CLIENT_ID else "❌ Missing"
    secret_status = "✅ Set" if settings.PAYPAL_SECRET else "❌ Missing"
    
    print(f"PAYPAL_CLIENT_ID: {client_id_status}")
    print(f"PAYPAL_SECRET: {secret_status}")
    print(f"PAYPAL_API_BASE: {settings.PAYPAL_API_BASE}")
    
    # Show credential previews (without exposing full credentials)
    if settings.PAYPAL_CLIENT_ID:
        client_preview = f"{settings.PAYPAL_CLIENT_ID[:8]}...{settings.PAYPAL_CLIENT_ID[-4:]}" if len(settings.PAYPAL_CLIENT_ID) > 12 else "***"
        print(f"Client ID Preview: {client_preview}")
    
    if settings.PAYPAL_SECRET:
        secret_preview = f"{settings.PAYPAL_SECRET[:8]}...{settings.PAYPAL_SECRET[-4:]}" if len(settings.PAYPAL_SECRET) > 12 else "***"
        print(f"Secret Preview: {secret_preview}")
    
    # Determine environment
    env_type = "SANDBOX" if 'sandbox' in settings.PAYPAL_API_BASE.lower() else "LIVE"
    print(f"Environment: {env_type}")
    
    if not settings.PAYPAL_CLIENT_ID or not settings.PAYPAL_SECRET:
        print("\n❌ PayPal credentials are missing!")
        print("Please check your .env file and ensure PAYPAL_CLIENT_ID and PAYPAL_SECRET are set")
        return False
    
    print("\n🔑 Testing PayPal API Connection...")
    try:
        # Test getting access token
        token = paypal_api.get_access_token()
        if token:
            print("✅ Successfully obtained PayPal access token")
            print(f"Token (first 20 chars): {token[:20]}...")
            print(f"Token expires in: ~1 hour (PayPal default)")
            return True
        else:
            print("❌ Failed to obtain access token")
            return False
    except Exception as e:
        print(f"❌ PayPal API connection failed: {e}")
        if "401" in str(e) or "invalid_client" in str(e):
            print("💡 This usually means:")
            print("   - Client ID or Secret is incorrect")
            print("   - Credentials don't match the API environment (sandbox vs live)")
            print("   - PayPal app is not properly configured")
        return False

def test_order_creation():
    """Test creating a PayPal order"""
    print("\n💳 Testing PayPal Order Creation...")
    try:
        order = paypal_api.create_order(
            amount=50.00,
            currency="GBP",
            description="Test booking payment",
            custom_id="test_booking_123"
        )
        
        if order and order.get('id'):
            print(f"✅ Successfully created PayPal order: {order.get('id')}")
            print(f"Order status: {order.get('status')}")
            
            # Get approval URL
            links = order.get('links', [])
            approval_url = None
            for link in links:
                if link.get('rel') == 'approve':
                    approval_url = link.get('href')
                    break
            
            if approval_url:
                print(f"🔗 Approval URL: {approval_url}")
            
            return order.get('id')
        else:
            print("❌ Failed to create PayPal order")
            return None
    except Exception as e:
        print(f"❌ Order creation failed: {e}")
        return None

def main():
    """Main test function"""
    print("🚀 PayPal Integration Test (Simplified - No Webhooks)")
    print("=" * 60)
    
    # Test credentials
    if not test_paypal_credentials():
        return
    
    # Test order creation
    order_id = test_order_creation()
    
    print("\n" + "=" * 60)
    if order_id:
        print("✅ All PayPal tests passed!")
        print("\n📋 Summary:")
        print("- PayPal credentials are valid")
        print("- API connection is working")
        print("- Order creation is functional")
        print("- Webhook functionality has been removed")
        print("\n🎯 Your PayPal integration is ready!")
        print("\nNext steps:")
        print("1. Use the 'capture-payment' endpoint with action='create' to create orders")
        print("2. Use the 'capture-payment' endpoint with action='capture' to capture payments")
        print("3. All payment processing happens through the capture-payment URL")
    else:
        print("❌ Some tests failed. Please check your PayPal configuration.")

if __name__ == "__main__":
    main()