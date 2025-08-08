# Get Real PayPal Credentials - Step by Step Guide

## Current Issue
Your system shows this error:
```
ERROR: PayPal credentials are still placeholders. Please update with real credentials from https://developer.paypal.com/
```

This means you need to replace the placeholder values with real PayPal credentials.

## Step 1: Create PayPal Developer Account

### 1.1 Go to PayPal Developer Portal
- Open your browser and go to: https://developer.paypal.com/
- Click "Log in to Dashboard" (top right)

### 1.2 Sign In
- Use your existing PayPal account OR create a new one
- If you don't have a PayPal account, click "Sign Up" first

## Step 2: Create a PayPal Application

### 2.1 Access Developer Dashboard
- Once logged in, you'll see the PayPal Developer Dashboard
- Click "Create App" button

### 2.2 Fill Application Details
```
App Name: Access Auto Services Booking
Merchant: [Select your business account or create one]
Features: ✓ Accept Payments
Environment: 
  - Choose "Sandbox" for testing
  - Choose "Live" for production
```

### 2.3 Click "Create App"

## Step 3: Get Your Credentials

After creating the app, you'll see:

### For SANDBOX (Testing):
```
Client ID: sb-xxxxxx@business.example.com (starts with 'sb-')
Client Secret: ExxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxQ
```

### For LIVE (Production):
```
Client ID: AxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxQ
Client Secret: ExxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxQ
```

## Step 4: Update Your .env File

### 4.1 Open Your .env File
Navigate to: `C:\Users\Ayesha Jahangir\Downloads\Backend-main (4)\Backend-main\.env`

### 4.2 Replace Placeholder Values

**For SANDBOX (Testing):**
```env
# PayPal Sandbox Credentials
PAYPAL_CLIENT_ID=sb-your-actual-client-id-here
PAYPAL_SECRET=your-actual-secret-here
PAYPAL_API_BASE=https://api-m.sandbox.paypal.com
```

**For LIVE (Production):**
```env
# PayPal Live Credentials
PAYPAL_CLIENT_ID=your-actual-live-client-id-here
PAYPAL_SECRET=your-actual-live-secret-here
PAYPAL_API_BASE=https://api-m.paypal.com
```

### 4.3 Example of What It Should Look Like
```env
# Before (Placeholder - WRONG):
PAYPAL_CLIENT_ID=your_live_paypal_client_id_here
PAYPAL_SECRET=your_live_paypal_secret_here

# After (Real Credentials - CORRECT):
PAYPAL_CLIENT_ID=sb-1a2b3c4d5e6f7g@business.example.com
PAYPAL_SECRET=EIeNSv_r8UGAX5qlwRlQ2BJGzfyOvjomZqp5-sbXww_JCcSXfOeBL7cwh-6f3FZQ0pnfV7WgQzbgbs4Z
```

## Step 5: Set Up Webhooks (Important!)

### 5.1 In PayPal App Dashboard
- Go to your app in PayPal Developer Dashboard
- Click on "Webhooks" tab
- Click "Add Webhook"

### 5.2 Configure Webhook
```
Webhook URL: https://backend-kzpz.onrender.com/api/paypal/webhook/
Event types: Select these events:
  ✓ Payment capture completed
  ✓ Payment capture denied
  ✓ Payment capture refunded
```

### 5.3 Get Webhook ID
- After creating webhook, copy the "Webhook ID"
- Add it to your .env file:
```env
PAYPAL_WEBHOOK_ID=your-webhook-id-here
```

## Step 6: Update Production Environment (Render)

### 6.1 Go to Render Dashboard
- Open https://dashboard.render.com/
- Select your backend service

### 6.2 Update Environment Variables
- Go to "Environment" tab
- Update these variables:
  - `PAYPAL_CLIENT_ID`
  - `PAYPAL_SECRET`
  - `PAYPAL_API_BASE`
  - `PAYPAL_WEBHOOK_ID`

### 6.3 Redeploy
- Your service will automatically redeploy with new credentials

## Step 7: Test Your Configuration

### 7.1 Run Test Script
```bash
python test_paypal_config.py
```

### 7.2 Expected Success Output
```
✅ PayPal configuration loaded successfully
✅ Access token obtained: eyJ0eXAiOiJKV1QiLCJhbGc...
✅ Test order created: 8XY12345678901234
```

## Common Issues & Solutions

### Issue 1: "Invalid client credentials"
**Solution**: Double-check your Client ID and Secret are copied correctly

### Issue 2: "Webhook verification failed"
**Solution**: Make sure webhook URL is exactly: `https://backend-kzpz.onrender.com/api/paypal/webhook/`

### Issue 3: "Still showing placeholder error"
**Solution**: Make sure you saved the .env file and restarted your server

## Sandbox vs Live

### Use SANDBOX for:
- Testing payments
- Development
- Debugging
- Learning the system

### Use LIVE for:
- Production website
- Real customer payments
- Actual money transactions

## Security Notes

### ⚠️ Important Security Tips:
1. **Never share your credentials** publicly
2. **Don't commit credentials** to version control
3. **Use environment variables** only
4. **Regularly rotate** your credentials
5. **Monitor your PayPal dashboard** for suspicious activity

## Need Help?

### If you're stuck:
1. **Check PayPal Developer Docs**: https://developer.paypal.com/docs/
2. **PayPal Community**: https://www.paypal-community.com/
3. **Test with our script**: `python test_paypal_config.py`

### Contact PayPal Support:
- For credential issues
- For webhook problems
- For API questions

---

## Quick Checklist ✅

- [ ] Created PayPal Developer account
- [ ] Created PayPal application
- [ ] Copied real Client ID and Secret
- [ ] Updated .env file with real credentials
- [ ] Set up webhook with correct URL
- [ ] Added webhook ID to .env
- [ ] Updated Render environment variables
- [ ] Tested configuration with test script
- [ ] Verified no more placeholder errors

Once you complete these steps, your PayPal integration will be fully functional with real payment processing! 💰