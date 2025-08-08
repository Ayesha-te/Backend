# PayPal Credentials Setup Guide

## 🚀 Complete PayPal Integration (No Webhooks Required)

Your PayPal integration has been simplified to use only **3 credentials** and the **capture-payment** endpoint handles everything.

## 📋 Required Credentials

You need exactly **3 PayPal credentials** in your `.env` file:

```env
PAYPAL_CLIENT_ID=your_real_client_id_here
PAYPAL_SECRET=your_real_secret_here
PAYPAL_API_BASE=https://api-m.paypal.com  # For live payments
# OR
PAYPAL_API_BASE=https://api-m.sandbox.paypal.com  # For testing
```

## 🔧 How to Get Real PayPal Credentials

### Step 1: Create PayPal Developer Account
1. Go to https://developer.paypal.com/
2. Sign in with your PayPal business account
3. Click "Create App"

### Step 2: Create Your Application
1. **App Name**: "Access Auto Services Payment"
2. **Merchant**: Select your business account
3. **Features**: Check "Accept payments"
4. **Environment**: 
   - Choose "Sandbox" for testing
   - Choose "Live" for production

### Step 3: Get Your Credentials
After creating the app, you'll see:
- **Client ID**: Copy this to `PAYPAL_CLIENT_ID`
- **Secret**: Click "Show" and copy to `PAYPAL_SECRET`

### Step 4: Update Your .env File
```env
# For TESTING (Sandbox)
PAYPAL_CLIENT_ID=your_sandbox_client_id
PAYPAL_SECRET=your_sandbox_secret
PAYPAL_API_BASE=https://api-m.sandbox.paypal.com

# For PRODUCTION (Live)
PAYPAL_CLIENT_ID=your_live_client_id
PAYPAL_SECRET=your_live_secret
PAYPAL_API_BASE=https://api-m.paypal.com
```

## 🎯 How Your Simplified PayPal Integration Works

### Single Endpoint: `/api/paypal/capture-payment/`

This endpoint handles both order creation and payment capture:

#### 1. Create PayPal Order
```json
POST /api/paypal/capture-payment/
{
    "booking_id": 123,
    "customer_email": "customer@example.com",  // For anonymous users
    "action": "create"
}
```

**Response:**
```json
{
    "order_id": "paypal_order_id_here",
    "booking_id": 123,
    "amount": 50.00,
    "currency": "GBP"
}
```

#### 2. Capture Payment
```json
POST /api/paypal/capture-payment/
{
    "booking_id": 123,
    "paypal_order_id": "order_id_from_step_1",
    "customer_email": "customer@example.com",  // For anonymous users
    "action": "capture"  // This is the default
}
```

**Response:**
```json
{
    "message": "Payment captured successfully!",
    "transaction_id": "capture_id_here",
    "booking_id": 123,
    "booking_status": "confirmed",
    "payment_status": "completed"
}
```

## ✅ What's Been Removed/Simplified

- ❌ **Webhooks**: No webhook setup required
- ❌ **PAYPAL_WEBHOOK_ID**: Not needed anymore
- ❌ **Complex webhook verification**: Removed
- ✅ **Simple 3-credential setup**: Only Client ID, Secret, and API Base
- ✅ **Single endpoint**: Everything happens in capture-payment
- ✅ **Immediate confirmation**: Payment confirmation happens instantly

## 🧪 Testing Your Setup

Run this command to test your PayPal credentials:

```bash
python test_paypal_simplified.py
```

## 🔒 Security Notes

1. **Never commit real credentials** to version control
2. **Use sandbox for testing** before going live
3. **Use HTTPS in production** (already configured)
4. **Validate all payments** server-side (already implemented)

## 🚀 Frontend Integration

Your frontend needs to:

1. **Create Order**: Call capture-payment with `action: "create"`
2. **Show PayPal Button**: Use the returned `order_id`
3. **Capture Payment**: Call capture-payment with the `order_id` after user approval

## 📞 Support

If you need help getting your PayPal credentials:
1. Contact PayPal Developer Support
2. Check PayPal Developer Documentation
3. Ensure your PayPal account is a Business account

---

**Your PayPal integration is now simplified and ready to use with just 3 credentials!**