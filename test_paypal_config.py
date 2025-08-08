#!/usr/bin/env python
"""
Test PayPal configuration and API connectivity
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

from django.conf import settings
from PAYPAL.paypal_utils import paypal_api
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_paypal_config():
    """Test PayPal configuration and connectivity"""
    print("=" * 50)
    print("PayPal Configuration Test")
    print("=" * 50)
    
    # Check environment variables
    print(f"PAYPAL_CLIENT_ID: {settings.PAYPAL_CLIENT_ID[:10]}..." if settings.PAYPAL_CLIENT_ID else "Not set")
    print(f"PAYPAL_SECRET: {'*' * 10}..." if settings.PAYPAL_SECRET else "Not set")
    print(f"PAYPAL_API_BASE: {settings.PAYPAL_API_BASE}")
    
    if not settings.PAYPAL_CLIENT_ID or not settings.PAYPAL_SECRET:
        print("❌ PayPal credentials not configured!")
        return False
    
    if settings.PAYPAL_CLIENT_ID == "sb-1vjnx44839480@business.example.com":
        print("⚠️  Using placeholder PayPal credentials!")
        print("   Please update with real credentials from https://developer.paypal.com/")
        return False
    
    # Test access token
    print("\n" + "=" * 30)
    print("Testing PayPal Access Token")
    print("=" * 30)
    
    try:
        token = paypal_api.get_access_token()
        if token:
            print(f"✅ Access token obtained: {token[:20]}...")
            return True
        else:
            print("❌ Failed to obtain access token")
            return False
    except Exception as e:
        print(f"❌ Error getting access token: {e}")
        return False

def test_create_order():
    """Test creating a PayPal order"""
    print("\n" + "=" * 30)
    print("Testing PayPal Order Creation")
    print("=" * 30)
    
    try:
        order = paypal_api.create_order(
            amount=10.00,
            currency="GBP",
            description="Test booking payment"
        )
        
        if order and order.get('id'):
            print(f"✅ Test order created: {order.get('id')}")
            print(f"   Status: {order.get('status')}")
            return True
        else:
            print("❌ Failed to create test order")
            return False
            
    except Exception as e:
        print(f"❌ Error creating test order: {e}")
        return False

if __name__ == "__main__":
    print("Starting PayPal configuration test...\n")
    
    config_ok = test_paypal_config()
    
    if config_ok:
        test_create_order()
    
    print("\n" + "=" * 50)
    print("Test completed!")
    print("=" * 50)