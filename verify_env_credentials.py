#!/usr/bin/env python3
"""
Verify that PayPal credentials are being loaded correctly from .env file
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
BASE_DIR = Path(__file__).resolve().parent
env_path = BASE_DIR / '.env'

print("🔍 Verifying PayPal Credentials from .env file")
print("=" * 60)

# Check if .env file exists
if env_path.exists():
    print(f"✅ .env file found at: {env_path}")
    load_dotenv(env_path)
else:
    print(f"❌ .env file not found at: {env_path}")
    sys.exit(1)

# Check PayPal credentials
print("\n📋 PayPal Credentials Status:")
print("-" * 30)

client_id = os.getenv('PAYPAL_CLIENT_ID', '').strip()
secret = os.getenv('PAYPAL_SECRET', '').strip()
api_base = os.getenv('PAYPAL_API_BASE', '').strip()

# Client ID
if client_id:
    client_preview = f"{client_id[:8]}...{client_id[-4:]}" if len(client_id) > 12 else "***"
    print(f"PAYPAL_CLIENT_ID: ✅ Set ({client_preview})")
    print(f"  Length: {len(client_id)} characters")
else:
    print("PAYPAL_CLIENT_ID: ❌ Missing or empty")

# Secret
if secret:
    secret_preview = f"{secret[:8]}...{secret[-4:]}" if len(secret) > 12 else "***"
    print(f"PAYPAL_SECRET: ✅ Set ({secret_preview})")
    print(f"  Length: {len(secret)} characters")
else:
    print("PAYPAL_SECRET: ❌ Missing or empty")

# API Base
if api_base:
    env_type = "SANDBOX" if 'sandbox' in api_base.lower() else "LIVE"
    print(f"PAYPAL_API_BASE: ✅ Set ({api_base})")
    print(f"  Environment: {env_type}")
else:
    print("PAYPAL_API_BASE: ❌ Missing or empty")

print("\n" + "=" * 60)

# Overall status
if client_id and secret and api_base:
    print("✅ All PayPal credentials are present in .env file")
    print("\n🚀 Ready to test PayPal integration!")
    print("Run: python test_paypal_simplified.py")
else:
    print("❌ Some PayPal credentials are missing")
    print("\n📝 Please check your .env file and ensure these variables are set:")
    if not client_id:
        print("  - PAYPAL_CLIENT_ID")
    if not secret:
        print("  - PAYPAL_SECRET")
    if not api_base:
        print("  - PAYPAL_API_BASE")

print("\n💡 Current .env file content (PayPal section):")
print("-" * 40)
try:
    with open(env_path, 'r') as f:
        lines = f.readlines()
        paypal_section = False
        for line in lines:
            line = line.strip()
            if line.startswith('# PayPal') or line.startswith('PAYPAL_'):
                paypal_section = True
                print(line)
            elif paypal_section and line.startswith('#'):
                print(line)
            elif paypal_section and line == '':
                break
except Exception as e:
    print(f"Error reading .env file: {e}")