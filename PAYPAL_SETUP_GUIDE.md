# PayPal Integration Setup Guide

## Current Issue
Your PayPal integration is failing with 400 errors because you're using placeholder credentials:
```
PAYPAL_CLIENT_ID=sb-1vjnx44839480@business.example.com
PAYPAL_SECRET=EIeNSv_r8UGAX5qlwRlQ2BJGzfyOvjomZqp5-sbXww_JCcSXfOeBL7cwh-6f3FZQ0pnfV7WgQzbgbs4Z
```

## Step-by-Step Setup

### 1. Create PayPal Developer Account
1. Go to https://developer.paypal.com/
2. Click "Log in to Dashboard"
3. Log in with your PayPal account (or create one)

### 2. Create Sandbox Application
1. In the PayPal Developer Dashboard, click "Create App"
2. Fill in the details:
   - **App Name**: "Access Auto Services Booking"
   - **Merchant**: Select your sandbox business account (or create one)
   - **Features**: Check "Accept Payments"
3. Click "Create App"

### 3. Get Your Credentials
After creating the app, you'll see:
- **Client ID**: Copy this (starts with "sb-" for sandbox)
- **Client Secret**: Click "Show" and copy this

### 4. Update Your .env File
Replace the placeholder credentials in your `.env` file:

```env
# Replace with your real PayPal sandbox credentials
PAYPAL_CLIENT_ID=your_real_client_id_here
PAYPAL_SECRET=your_real_client_secret_here
PAYPAL_API_BASE=https://api-m.sandbox.paypal.com
```

### 5. Update Production Environment (Render)
1. Go to your Render dashboard
2. Select your backend service
3. Go to "Environment" tab
4. Update these variables:
   - `PAYPAL_CLIENT_ID`
   - `PAYPAL_SECRET`
5. Your service will automatically redeploy

### 6. Test Your Configuration
Run the test script to verify everything works:
```bash
python test_paypal_config.py
```

You should see:
```
✅ Access token obtained: eyJ0eXAiOiJKV1QiLCJhbGc...
✅ Test order created: 8XY12345678901234
```

## Sandbox vs Production

### For Development/Testing (Current)
- Use **Sandbox** credentials
- API Base: `https://api-m.sandbox.paypal.com`
- Test with fake PayPal accounts

### For Production (Later)
- Create a **Live** application in PayPal Developer Dashboard
- Use **Live** credentials
- API Base: `https://api-m.paypal.com`
- Real money transactions

## Troubleshooting

### Common Issues:

1. **401 Unauthorized**
   - Check your Client ID and Secret are correct
   - Make sure you're using sandbox credentials with sandbox API base

2. **400 Bad Request**
   - Usually means invalid credentials or malformed request
   - Check the logs for detailed error messages

3. **App Not Found**
   - Make sure your app is active in PayPal Developer Dashboard
   - Check you're using the right environment (sandbox vs live)

### Test Payments
In sandbox mode, you can use these test PayPal accounts:
- **Buyer Account**: Use the sandbox personal account created automatically
- **Seller Account**: Your sandbox business account

## Security Notes
- Never commit real PayPal credentials to version control
- Use environment variables for all sensitive data
- Regularly rotate your API credentials
- Monitor your PayPal dashboard for suspicious activity

## Support
If you need help:
1. Check PayPal Developer Documentation: https://developer.paypal.com/docs/
2. PayPal Developer Community: https://www.paypal-community.com/
3. Run `python test_paypal_config.py` to diagnose issues