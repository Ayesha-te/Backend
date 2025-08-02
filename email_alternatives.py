#!/usr/bin/env python
"""
Alternative email configurations for production
"""

# OPTION 1: SendGrid (Recommended for production)
SENDGRID_CONFIG = {
    'EMAIL_BACKEND': 'django.core.mail.backends.smtp.EmailBackend',
    'EMAIL_HOST': 'smtp.sendgrid.net',
    'EMAIL_PORT': 587,
    'EMAIL_USE_TLS': True,
    'EMAIL_HOST_USER': 'apikey',  # Always 'apikey' for SendGrid
    'EMAIL_HOST_PASSWORD': 'YOUR_SENDGRID_API_KEY',  # Get from SendGrid dashboard
    'DEFAULT_FROM_EMAIL': 'Access Auto Services <noreply@access-auto-services.co.uk>',
}

# OPTION 2: Mailgun
MAILGUN_CONFIG = {
    'EMAIL_BACKEND': 'django.core.mail.backends.smtp.EmailBackend',
    'EMAIL_HOST': 'smtp.mailgun.org',
    'EMAIL_PORT': 587,
    'EMAIL_USE_TLS': True,
    'EMAIL_HOST_USER': 'postmaster@your-domain.mailgun.org',
    'EMAIL_HOST_PASSWORD': 'YOUR_MAILGUN_PASSWORD',
    'DEFAULT_FROM_EMAIL': 'Access Auto Services <noreply@access-auto-services.co.uk>',
}

# OPTION 3: AWS SES
AWS_SES_CONFIG = {
    'EMAIL_BACKEND': 'django.core.mail.backends.smtp.EmailBackend',
    'EMAIL_HOST': 'email-smtp.us-east-1.amazonaws.com',  # Change region as needed
    'EMAIL_PORT': 587,
    'EMAIL_USE_TLS': True,
    'EMAIL_HOST_USER': 'YOUR_AWS_ACCESS_KEY_ID',
    'EMAIL_HOST_PASSWORD': 'YOUR_AWS_SECRET_ACCESS_KEY',
    'DEFAULT_FROM_EMAIL': 'Access Auto Services <noreply@access-auto-services.co.uk>',
}

# OPTION 4: Keep Gmail but with better error handling
GMAIL_PRODUCTION_CONFIG = {
    'EMAIL_BACKEND': 'django.core.mail.backends.smtp.EmailBackend',
    'EMAIL_HOST': 'smtp.gmail.com',
    'EMAIL_PORT': 587,
    'EMAIL_USE_TLS': True,
    'EMAIL_HOST_USER': 'ayeshajahangir280@gmail.com',
    'EMAIL_HOST_PASSWORD': 'YOUR_NEW_APP_PASSWORD',  # Generate new one
    'DEFAULT_FROM_EMAIL': 'Access Auto Services <ayeshajahangir280@gmail.com>',
    'EMAIL_TIMEOUT': 30,  # Add timeout
}

print("Email service alternatives for production:")
print("1. SendGrid - Most reliable for production")
print("2. Mailgun - Good for transactional emails") 
print("3. AWS SES - Cost-effective for high volume")
print("4. Gmail - Fix App Password issue")