#!/usr/bin/env python
"""
Check if PayPal credentials are real or still placeholders
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

def check_credentials():
    print("=" * 60)
    print("PAYPAL CREDENTIALS CHECK")
    print("=" * 60)
    
    client_id = settings.PAYPAL_CLIENT_ID
    secret = settings.PAYPAL_SECRET
    api_base = settings.PAYPAL_API_BASE
    webhook_id = getattr(settings, 'PAYPAL_WEBHOOK_ID', None)
    
    print(f"\n📋 Current Configuration:")
    print(f"Client ID: {client_id[:20]}..." if client_id else "❌ Not set")
    print(f"Secret: {'*' * 20}..." if secret else "❌ Not set")
    print(f"API Base: {api_base}")
    print(f"Webhook ID: {webhook_id[:20]}..." if webhook_id else "❌ Not set")
    
    # Check for placeholder values
    placeholder_patterns = [
        "your_live_paypal_client_id_here",
        "your_live_paypal_secret_here", 
        "your_real_client_id",
        "your_real_secret",
        "sb-1vjnx44839480@business.example.com",
        "your_webhook_id_here"
    ]
    
    issues = []
    
    # Check Client ID
    if not client_id:
        issues.append("❌ PAYPAL_CLIENT_ID is not set")
    elif client_id in placeholder_patterns:
        issues.append("❌ PAYPAL_CLIENT_ID is still a placeholder")
    elif client_id.startswith('sb-') and '@business.example.com' in client_id:
        issues.append("❌ PAYPAL_CLIENT_ID appears to be a placeholder")
    else:
        print("✅ Client ID looks real")
    
    # Check Secret
    if not secret:
        issues.append("❌ PAYPAL_SECRET is not set")
    elif secret in placeholder_patterns:
        issues.append("❌ PAYPAL_SECRET is still a placeholder")
    else:
        print("✅ Secret looks real")
    
    # Check API Base
    if api_base in ["https://api-m.paypal.com", "https://api-m.sandbox.paypal.com"]:
        print("✅ API Base is correct")
    else:
        issues.append("❌ PAYPAL_API_BASE should be https://api-m.paypal.com or https://api-m.sandbox.paypal.com")
    
    # Check Webhook ID
    if not webhook_id:
        issues.append("⚠️  PAYPAL_WEBHOOK_ID is not set (optional but recommended)")
    elif webhook_id in placeholder_patterns:
        issues.append("❌ PAYPAL_WEBHOOK_ID is still a placeholder")
    else:
        print("✅ Webhook ID looks real")
    
    print("\n" + "=" * 60)
    
    if issues:
        print("❌ ISSUES FOUND:")
        for issue in issues:
            print(f"   {issue}")
        
        print("\n🔧 TO FIX THESE ISSUES:")
        print("1. Go to https://developer.paypal.com/")
        print("2. Create a PayPal application")
        print("3. Copy the real Client ID and Secret")
        print("4. Update your .env file with real values")
        print("5. Set up webhooks and get Webhook ID")
        print("\n📖 See GET_REAL_PAYPAL_CREDENTIALS.md for detailed instructions")
        
        return False
    else:
        print("✅ ALL CREDENTIALS LOOK GOOD!")
        print("\n🎉 Your PayPal credentials appear to be real and properly configured.")
        print("You can now test the PayPal integration.")
        
        return True

def test_connection():
    """Test actual connection to PayPal API"""
    try:
        from PAYPAL.paypal_utils import paypal_api
        
        print("\n" + "=" * 60)
        print("TESTING PAYPAL CONNECTION")
        print("=" * 60)
        
        # Test getting access token
        token = paypal_api.get_access_token()
        if token:
            print("✅ Successfully connected to PayPal API!")
            print(f"   Access token obtained: {token[:30]}...")
            return True
        else:
            print("❌ Failed to get access token from PayPal")
            return False
            
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return False

if __name__ == "__main__":
    print("Checking your PayPal credentials...\n")
    
    credentials_ok = check_credentials()
    
    if credentials_ok:
        connection_ok = test_connection()
        
        if connection_ok:
            print("\n🚀 READY FOR PAYMENTS!")
            print("Your PayPal integration is properly configured and working.")
        else:
            print("\n⚠️  CREDENTIALS LOOK GOOD BUT CONNECTION FAILED")
            print("Check your internet connection and PayPal service status.")
    
    print("\n" + "=" * 60)