# PayPal Frontend Integration Guide

## Overview
This guide shows how to integrate the enhanced PayPal payment system with your React frontend.

## Backend Changes Made

### 1. Real PayPal Integration
- Removed placeholder credentials
- Added webhook support for payment confirmations
- Enhanced error handling and logging
- Added automatic payment confirmation emails

### 2. New Endpoints
- `POST /api/paypal/webhook/` - PayPal webhook handler
- Enhanced `POST /api/paypal/create-order/` - Now includes booking tracking

## Frontend Integration

### 1. Install PayPal SDK
```bash
npm install @paypal/react-paypal-js
```

### 2. Update Your Payment Component

```jsx
import { PayPalScriptProvider, PayPalButtons } from "@paypal/react-paypal-js";

// Add this to your main App component or payment page
const PayPalPayment = ({ bookingData, onPaymentSuccess, onPaymentError }) => {
  const [paypalOrderId, setPaypalOrderId] = useState(null);
  const [bookingId, setBookingId] = useState(null);

  // Create booking first, then create PayPal order
  const createBookingAndOrder = async () => {
    try {
      // 1. Create booking
      const bookingResponse = await fetch('/api/paypal/bookings/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(bookingData)
      });

      if (!bookingResponse.ok) {
        throw new Error('Failed to create booking');
      }

      const booking = await bookingResponse.json();
      setBookingId(booking.id);

      // 2. Create PayPal order
      const orderResponse = await fetch('/api/paypal/create-order/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          booking_id: booking.id,
          customer_email: bookingData.customer.email
        })
      });

      if (!orderResponse.ok) {
        throw new Error('Failed to create PayPal order');
      }

      const orderData = await orderResponse.json();
      setPaypalOrderId(orderData.order_id);
      
      return orderData.order_id;

    } catch (error) {
      console.error('Error creating booking/order:', error);
      onPaymentError(error.message);
      throw error;
    }
  };

  const handleApprove = async (data) => {
    try {
      // Capture payment
      const response = await fetch('/api/paypal/capture-payment/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          booking_id: bookingId,
          paypal_order_id: data.orderID,
          customer_email: bookingData.customer.email
        })
      });

      if (!response.ok) {
        throw new Error('Payment capture failed');
      }

      const result = await response.json();
      onPaymentSuccess(result);

    } catch (error) {
      console.error('Payment capture error:', error);
      onPaymentError(error.message);
    }
  };

  return (
    <PayPalScriptProvider options={{
      "client-id": "YOUR_PAYPAL_CLIENT_ID", // Get this from your PayPal app
      currency: "GBP"
    }}>
      <PayPalButtons
        createOrder={createBookingAndOrder}
        onApprove={handleApprove}
        onError={(err) => {
          console.error('PayPal error:', err);
          onPaymentError('Payment failed. Please try again.');
        }}
        onCancel={() => {
          console.log('Payment cancelled');
        }}
        style={{
          layout: 'vertical',
          color: 'blue',
          shape: 'rect',
          label: 'paypal'
        }}
      />
    </PayPalScriptProvider>
  );
};
```

### 3. Update Your Booking Component

```jsx
// In your booking component (step 4 - Payment)
{bookingData.payment.method === 'paypal' && (
  <div className="bg-blue-50 p-6 rounded-lg">
    <h3 className="text-lg font-semibold text-blue-800 mb-4">PayPal Payment</h3>
    <PayPalPayment
      bookingData={bookingData}
      onPaymentSuccess={(result) => {
        console.log('Payment successful:', result);
        setBookingSuccess(true);
        setStep(5); // Move to success step
      }}
      onPaymentError={(error) => {
        console.error('Payment error:', error);
        alert('Payment failed: ' + error);
      }}
    />
  </div>
)}
```

### 4. Handle Payment Success

```jsx
// Update your success step (step 5)
{step === 5 && bookingSuccess && (
  <div className="bg-white rounded-lg shadow-lg p-8 text-center">
    <div className="text-6xl text-green-500 mb-6">✅</div>
    <h2 className="text-3xl font-bold text-gray-800 mb-4">Payment Confirmed!</h2>
    <p className="text-lg text-gray-600 mb-6">
      Your payment has been processed and your booking is confirmed.
    </p>
    <div className="bg-green-50 p-6 rounded-lg mb-6">
      <h3 className="text-lg font-semibold text-green-800 mb-2">What happens next?</h3>
      <ul className="text-green-700 text-left space-y-2">
        <li>• Payment confirmation email sent immediately</li>
        <li>• Booking confirmation email sent to you and our team</li>
        <li>• Reminder email will be sent 24 hours before your appointment</li>
        <li>• Your payment has been securely processed through PayPal</li>
      </ul>
    </div>
  </div>
)}
```

## Required Configuration

### 1. Get Real PayPal Credentials

#### For Production (Live Payments):
1. Go to https://developer.paypal.com/
2. Create a **LIVE** application (not sandbox)
3. Get your Live Client ID and Secret
4. Update your `.env` file:

```env
PAYPAL_CLIENT_ID=your_live_client_id_here
PAYPAL_SECRET=your_live_secret_here
PAYPAL_API_BASE=https://api-m.paypal.com
```

#### For Testing (Sandbox):
1. Create a **SANDBOX** application
2. Use sandbox credentials:

```env
PAYPAL_CLIENT_ID=your_sandbox_client_id_here
PAYPAL_SECRET=your_sandbox_secret_here
PAYPAL_API_BASE=https://api-m.sandbox.paypal.com
```

### 2. Set Up Webhooks

1. In your PayPal app dashboard, go to "Webhooks"
2. Add webhook URL: `https://backend-kzpz.onrender.com/api/paypal/webhook/`
3. Select these events:
   - `PAYMENT.CAPTURE.COMPLETED`
   - `PAYMENT.CAPTURE.DENIED`
   - `PAYMENT.CAPTURE.REFUNDED`
4. Copy the Webhook ID and add to your `.env`:

```env
PAYPAL_WEBHOOK_ID=your_webhook_id_here
```

### 3. Update Frontend PayPal Client ID

In your React component, replace `YOUR_PAYPAL_CLIENT_ID` with your actual PayPal Client ID (the same one from your `.env` file).

## Payment Flow

1. **User selects PayPal payment method**
2. **Frontend creates booking** via `/api/paypal/bookings/`
3. **Frontend creates PayPal order** via `/api/paypal/create-order/`
4. **User completes payment** on PayPal
5. **PayPal sends webhook** to `/api/paypal/webhook/`
6. **Backend processes payment** and sends confirmation emails
7. **Frontend shows success message**

## Email Notifications

The system automatically sends:
- **Immediate**: Booking confirmation email
- **After Payment**: Payment confirmation email
- **24 hours before**: Appointment reminder email

## Error Handling

The enhanced system handles:
- Invalid PayPal credentials
- Payment failures
- Network errors
- Webhook verification failures
- Email sending failures

## Testing

1. Use sandbox credentials for testing
2. Test with PayPal sandbox accounts
3. Verify webhook delivery in PayPal dashboard
4. Check email delivery

## Security Features

- Webhook signature verification
- Secure credential handling
- Payment status tracking
- Transaction logging
- Error monitoring

## Support

If you encounter issues:
1. Check the backend logs for detailed error messages
2. Verify your PayPal credentials are correct
3. Ensure webhook URL is accessible
4. Test with PayPal's sandbox environment first