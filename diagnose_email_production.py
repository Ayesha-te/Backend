#!/usr/bin/env python
import os
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.core.mail import get_connection, send_mail
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def diagnose_email_production():
    """Diagnose email issues on production server"""
    
    print("=== Production Email Diagnostics ===\n")
    
    # Check environment variables
    print("📧 EMAIL CONFIGURATION:")
    print(f"EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
    print(f"EMAIL_HOST: {settings.EMAIL_HOST}")
    print(f"EMAIL_PORT: {settings.EMAIL_PORT}")
    print(f"EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
    print(f"EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
    print(f"DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
    print(f"EMAIL_HOST_PASSWORD: {'*' * len(settings.EMAIL_HOST_PASSWORD) if settings.EMAIL_HOST_PASSWORD else 'NOT SET'}")
    
    # Check if all required settings are present
    missing_settings = []
    if not settings.EMAIL_HOST_USER:
        missing_settings.append('EMAIL_HOST_USER')
    if not settings.EMAIL_HOST_PASSWORD:
        missing_settings.append('EMAIL_HOST_PASSWORD')
    
    if missing_settings:
        print(f"\n❌ MISSING SETTINGS: {', '.join(missing_settings)}")
        return False
    
    print("\n✅ All email settings are configured")
    
    # Test Django email connection
    print("\n🔍 TESTING DJANGO EMAIL CONNECTION:")
    try:
        connection = get_connection()
        connection.open()
        print("✅ Django email connection successful!")
        connection.close()
    except Exception as e:
        print(f"❌ Django email connection failed: {e}")
        
        # Try to diagnose the specific error
        if "530" in str(e) and "Authentication Required" in str(e):
            print("\n🚨 GMAIL AUTHENTICATION ERROR DETECTED!")
            print("This usually means:")
            print("1. Gmail App Password is incorrect or expired")
            print("2. 2-Factor Authentication is not enabled on Gmail account")
            print("3. App Password was not generated correctly")
            print("\nSOLUTION STEPS:")
            print("1. Go to https://myaccount.google.com/security")
            print("2. Enable 2-Factor Authentication if not already enabled")
            print("3. Generate a new App Password for 'Mail'")
            print("4. Update EMAIL_HOST_PASSWORD environment variable with the new App Password")
            print("5. Restart your application")
        
        return False
    
    # Test sending actual email
    print("\n📨 TESTING EMAIL SENDING:")
    try:
        result = send_mail(
            subject='Production Email Test - Access Auto Services',
            message='This is a test email from your production server to verify email functionality.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.EMAIL_HOST_USER],  # Send to self
            fail_silently=False,
        )
        
        if result:
            print("✅ Test email sent successfully!")
            return True
        else:
            print("❌ Test email failed to send (no exception but result was 0)")
            return False
            
    except Exception as e:
        print(f"❌ Test email failed: {e}")
        return False

def test_raw_smtp_connection():
    """Test raw SMTP connection to diagnose issues"""
    
    print("\n🔧 RAW SMTP CONNECTION TEST:")
    
    try:
        # Create SMTP connection
        server = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
        server.set_debuglevel(1)  # Enable debug output
        
        print("✅ SMTP server connection established")
        
        # Start TLS
        server.starttls()
        print("✅ TLS connection established")
        
        # Login
        server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
        print("✅ SMTP authentication successful!")
        
        # Create test message
        msg = MIMEMultipart()
        msg['From'] = settings.EMAIL_HOST_USER
        msg['To'] = settings.EMAIL_HOST_USER
        msg['Subject'] = "Raw SMTP Test - Access Auto Services"
        
        body = "This is a raw SMTP test email to verify the connection works."
        msg.attach(MIMEText(body, 'plain'))
        
        # Send email
        text = msg.as_string()
        server.sendmail(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_USER, text)
        print("✅ Raw SMTP email sent successfully!")
        
        server.quit()
        return True
        
    except Exception as e:
        print(f"❌ Raw SMTP connection failed: {e}")
        return False

def provide_solutions():
    """Provide solutions for common email issues"""
    
    print("\n🛠️ COMMON SOLUTIONS:")
    print("="*60)
    
    print("\n1. GMAIL APP PASSWORD ISSUES:")
    print("   • Go to https://myaccount.google.com/security")
    print("   • Enable 2-Factor Authentication")
    print("   • Go to 'App passwords' section")
    print("   • Generate new password for 'Mail'")
    print("   • Use this 16-character password (not your Gmail password)")
    
    print("\n2. ENVIRONMENT VARIABLES:")
    print("   • Check your production server's environment variables")
    print("   • Ensure EMAIL_HOST_PASSWORD is set correctly")
    print("   • Restart your application after updating")
    
    print("\n3. GMAIL SECURITY SETTINGS:")
    print("   • Make sure 'Less secure app access' is OFF (use App Password instead)")
    print("   • Check if Gmail account is locked or suspended")
    print("   • Verify the Gmail account is active")
    
    print("\n4. PRODUCTION SERVER ISSUES:")
    print("   • Check if your server's IP is blocked by Gmail")
    print("   • Verify network connectivity to smtp.gmail.com:587")
    print("   • Check firewall settings")

if __name__ == "__main__":
    print("Starting production email diagnostics...\n")
    
    # Run diagnostics
    django_success = diagnose_email_production()
    
    if not django_success:
        print("\n" + "="*60)
        raw_success = test_raw_smtp_connection()
        
        if not raw_success:
            provide_solutions()
    
    print("\n" + "="*60)
    print("DIAGNOSTICS COMPLETE")
    
    if django_success:
        print("✅ Email system is working correctly!")
    else:
        print("❌ Email system needs attention. See solutions above.")