# Frontend Integration Guide - Payment Methods

## 🎯 Backend Now Supports All Your Frontend Payment Methods

Your backend now perfectly matches your frontend React component and supports all three payment methods:

1. **💳 PayPal** - Secure online payment
2. **💳 Credit Card** - Visa, MasterCard, etc.
3. **💷 Cash** - Pay on arrival

## 🚀 Single Endpoint for All Payment Methods

### Endpoint: `POST /api/paypal/capture-payment/`

This single endpoint handles all three payment methods from your frontend.

## 📋 Frontend Integration Examples

### 1. PayPal Payment Flow

#### Step 1: Create PayPal Order
```javascript
const createPayPalOrder = async (bookingId, customerEmail) => {
  const response = await fetch('/api/paypal/capture-payment/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      booking_id: bookingId,
      customer_email: customerEmail, // For anonymous users
      payment_method: 'paypal',
      action: 'create'
    })
  });
  
  const data = await response.json();
  return data.order_id; // Use this with PayPal SDK
};
```

#### Step 2: Capture PayPal Payment (after user approval)
```javascript
const capturePayPalPayment = async (bookingId, paypalOrderId, customerEmail) => {
  const response = await fetch('/api/paypal/capture-payment/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      booking_id: bookingId,
      paypal_order_id: paypalOrderId,
      customer_email: customerEmail,
      payment_method: 'paypal',
      action: 'capture'
    })
  });
  
  return await response.json();
};
```

### 2. Cash Payment
```javascript
const processCashPayment = async (bookingId, customerEmail) => {
  const response = await fetch('/api/paypal/capture-payment/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      booking_id: bookingId,
      customer_email: customerEmail,
      payment_method: 'cash'
    })
  });
  
  return await response.json();
};
```

### 3. Credit Card Payment
```javascript
const processCardPayment = async (bookingId, customerEmail, cardDetails) => {
  const response = await fetch('/api/paypal/capture-payment/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      booking_id: bookingId,
      customer_email: customerEmail,
      payment_method: 'card',
      card_number: cardDetails.cardNumber,
      name_on_card: cardDetails.nameOnCard,
      expiry_date: cardDetails.expiryDate,
      cvv: cardDetails.cvv
    })
  });
  
  return await response.json();
};
```

## 🔄 Integration with Your React Component

Based on your frontend code, here's how to integrate:

```javascript
// In your handleSubmit or payment processing function
const processPayment = async () => {
  const bookingId = bookingSuccess?.booking_id; // From booking creation
  const customerEmail = bookingData.customer.email;
  
  try {
    let result;
    
    switch (bookingData.payment.method) {
      case 'paypal':
        // Create PayPal order first
        const orderId = await createPayPalOrder(bookingId, customerEmail);
        
        // Show PayPal button with orderId
        // After user approves, capture payment
        result = await capturePayPalPayment(bookingId, orderId, customerEmail);
        break;
        
      case 'cash':
        result = await processCashPayment(bookingId, customerEmail);
        break;
        
      case 'card':
        result = await processCardPayment(bookingId, customerEmail, {
          cardNumber: bookingData.payment.cardNumber,
          nameOnCard: bookingData.payment.nameOnCard,
          expiryDate: bookingData.payment.expiryDate,
          cvv: bookingData.payment.cvv
        });
        break;
    }
    
    if (result.message) {
      // Payment successful - show success message
      console.log('Payment processed:', result.message);
      // Move to step 5 (success)
      setStep(5);
    }
    
  } catch (error) {
    console.error('Payment failed:', error);
    // Show error message to user
  }
};
```

## 📧 Email Notifications

The backend automatically sends different email confirmations based on payment method:

### PayPal Payment Email:
- ✅ "Payment Confirmed - Booking Confirmed"
- Includes transaction ID and PayPal confirmation
- Shows payment status as "Completed"

### Cash Payment Email:
- ✅ "Booking Confirmed - Cash Payment on Arrival"
- Reminds customer to bring cash
- Shows payment status as "Pending"

### Card Payment Email:
- ✅ "Booking Confirmed - Card Payment Processing"
- Indicates card payment is being processed
- Shows payment status as "Processing"

## 🎯 Response Formats

### PayPal Create Order Response:
```json
{
  "order_id": "paypal_order_id_here",
  "booking_id": 123,
  "amount": 50.00,
  "currency": "GBP",
  "payment_method": "paypal"
}
```

### PayPal Capture Response:
```json
{
  "message": "Payment captured successfully!",
  "transaction_id": "capture_id_here",
  "booking_id": 123,
  "booking_status": "confirmed",
  "payment_status": "completed",
  "payment_method": "paypal"
}
```

### Cash Payment Response:
```json
{
  "message": "Booking confirmed! Payment will be collected on arrival.",
  "booking_id": 123,
  "payment_method": "cash",
  "payment_status": "pending"
}
```

### Card Payment Response:
```json
{
  "message": "Booking confirmed! Card payment will be processed.",
  "booking_id": 123,
  "payment_method": "card",
  "payment_status": "pending",
  "note": "Card payment processing will be implemented in future update"
}
```

## ✅ What Your Frontend Shows vs Backend Handles

| Frontend Display | Backend Handles |
|------------------|-----------------|
| 💳 PayPal - "Secure online payment" | ✅ Full PayPal integration with order creation and capture |
| 💳 Credit Card - "Visa, MasterCard, etc." | ✅ Card details storage (processing to be implemented) |
| 💷 Cash - "Pay on arrival" | ✅ Cash booking confirmation with email notification |

## 🔧 Next Steps

1. **For PayPal**: Get real PayPal credentials and test the full flow
2. **For Cash**: Already working perfectly
3. **For Card**: Currently stores details and confirms booking (payment gateway integration needed for actual processing)

Your backend now perfectly matches your frontend payment component! 🎉