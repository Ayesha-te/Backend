#!/usr/bin/env python
"""
Test PayPal API connection with current credentials
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

def test_paypal_api():
    print("=" * 60)
    print("TESTING PAYPAL API CONNECTION")
    print("=" * 60)
    
    try:
        from PAYPAL.paypal_utils import paypal_api
        from django.conf import settings
        
        print(f"Client ID: {settings.PAYPAL_CLIENT_ID}")
        print(f"API Base: {settings.PAYPAL_API_BASE}")
        print(f"Secret: {'*' * 20}...")
        
        print("\n🔄 Testing PayPal API connection...")
        
        # Test getting access token
        token = paypal_api.get_access_token()
        
        if token:
            print("✅ SUCCESS: PayPal API connection working!")
            print(f"   Access token obtained: {token[:30]}...")
            
            # Test creating a small order
            print("\n🔄 Testing order creation...")
            try:
                test_order = paypal_api.create_order(
                    amount=1.00,
                    currency="GBP",
                    description="Test Order"
                )
                
                if test_order and 'id' in test_order:
                    print("✅ SUCCESS: Test order created!")
                    print(f"   Order ID: {test_order['id']}")
                    
                    # Get approval URL
                    approval_url = None
                    for link in test_order.get('links', []):
                        if link.get('rel') == 'approve':
                            approval_url = link.get('href')
                            break
                    
                    if approval_url:
                        print(f"   Approval URL: {approval_url[:50]}...")
                    
                    print("\n🎉 PAYPAL INTEGRATION IS WORKING PERFECTLY!")
                    print("Your credentials are valid and the API is responding correctly.")
                    return True
                else:
                    print("❌ FAILED: Could not create test order")
                    print(f"   Response: {test_order}")
                    return False
                    
            except Exception as e:
                print(f"❌ FAILED: Order creation failed - {e}")
                return False
                
        else:
            print("❌ FAILED: Could not get access token")
            return False
            
    except Exception as e:
        print(f"❌ FAILED: API connection failed - {e}")
        return False

if __name__ == "__main__":
    success = test_paypal_api()
    
    if success:
        print("\n" + "=" * 60)
        print("🚀 READY FOR PRODUCTION!")
        print("=" * 60)
        print("Your PayPal integration is working correctly.")
        print("You can now accept real payments through your system.")
    else:
        print("\n" + "=" * 60)
        print("❌ NEEDS ATTENTION")
        print("=" * 60)
        print("Please check your PayPal credentials and try again.")
        print("Make sure you have:")
        print("1. Valid PayPal Client ID")
        print("2. Valid PayPal Secret")
        print("3. Correct API Base URL")