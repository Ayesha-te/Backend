# Frontend PayPal Integration Guide

## 🎯 Connecting Your React Frontend to the Simplified PayPal Backend

Your backend now uses a single endpoint `/api/paypal/capture-payment/` for everything. Here's how to integrate it with your React frontend.

## 📦 Required Dependencies

First, install the PayPal JavaScript SDK:

```bash
npm install @paypal/react-paypal-js
```

## 🔧 PayPal Integration Component

Create a PayPal payment component:

```jsx
// components/PayPalPayment.jsx
import React, { useState } from 'react';
import { PayPalScriptProvider, PayPalButtons } from '@paypal/react-paypal-js';

const PayPalPayment = ({ bookingData, onSuccess, onError, onCancel }) => {
  const [loading, setLoading] = useState(false);
  const [paypalOrderId, setPaypalOrderId] = useState(null);

  // Calculate total amount
  const calculateTotal = () => {
    if (bookingData.fromCart && bookingData.cart?.length > 0) {
      return bookingData.cart.reduce((total, item) => total + (item.price * item.qty), 0);
    }
    return bookingData.selectedService?.price || 0;
  };

  const total = calculateTotal();

  // PayPal configuration
  const initialOptions = {
    "client-id": "YOUR_PAYPAL_CLIENT_ID", // Replace with your actual client ID
    currency: "GBP",
    intent: "capture",
    "disable-funding": "credit,card" // Optional: disable other payment methods
  };

  // Create PayPal order
  const createOrder = async (data, actions) => {
    setLoading(true);
    try {
      // First create the booking
      const bookingResponse = await fetch('/api/paypal/bookings/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          service_id: bookingData.selectedService?.id,
          date: bookingData.date,
          time: bookingData.time,
          customer_first_name: bookingData.customer.firstName,
          customer_last_name: bookingData.customer.lastName,
          customer_email: bookingData.customer.email,
          customer_phone: bookingData.customer.phone,
          vehicle_registration: bookingData.vehicle.registration,
          vehicle_make: bookingData.vehicle.make,
          vehicle_model: bookingData.vehicle.model,
          vehicle_year: bookingData.vehicle.year,
          payment_amount: total,
          payment_currency: 'GBP',
          payment_method: 'paypal'
        })
      });

      if (!bookingResponse.ok) {
        throw new Error('Failed to create booking');
      }

      const booking = await bookingResponse.json();

      // Create PayPal order using your simplified endpoint
      const orderResponse = await fetch('/api/paypal/capture-payment/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          booking_id: booking.id,
          customer_email: bookingData.customer.email,
          action: 'create'
        })
      });

      if (!orderResponse.ok) {
        throw new Error('Failed to create PayPal order');
      }

      const orderData = await orderResponse.json();
      setPaypalOrderId(orderData.order_id);
      
      return orderData.order_id;

    } catch (error) {
      console.error('Error creating PayPal order:', error);
      onError(error.message);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  // Capture PayPal payment
  const onApprove = async (data, actions) => {
    setLoading(true);
    try {
      // Capture payment using your simplified endpoint
      const captureResponse = await fetch('/api/paypal/capture-payment/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          booking_id: bookingData.bookingId, // You'll need to store this from createOrder
          paypal_order_id: data.orderID,
          customer_email: bookingData.customer.email,
          action: 'capture'
        })
      });

      if (!captureResponse.ok) {
        throw new Error('Failed to capture payment');
      }

      const captureData = await captureResponse.json();
      
      // Payment successful
      onSuccess({
        transactionId: captureData.transaction_id,
        bookingId: captureData.booking_id,
        message: captureData.message
      });

    } catch (error) {
      console.error('Error capturing payment:', error);
      onError(error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="paypal-payment-container">
      {loading && (
        <div className="text-center py-4">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <p className="mt-2 text-gray-600">Processing payment...</p>
        </div>
      )}
      
      <PayPalScriptProvider options={initialOptions}>
        <PayPalButtons
          style={{
            layout: "vertical",
            color: "blue",
            shape: "rect",
            label: "paypal"
          }}
          createOrder={createOrder}
          onApprove={onApprove}
          onError={(err) => {
            console.error('PayPal error:', err);
            onError('Payment failed. Please try again.');
          }}
          onCancel={() => {
            onCancel('Payment was cancelled');
          }}
          disabled={loading}
        />
      </PayPalScriptProvider>
    </div>
  );
};

export default PayPalPayment;
```

## 🔄 Updated Step 4 Component

Update your Step 4 to include the PayPal component:

```jsx
// In your main booking component
import PayPalPayment from './components/PayPalPayment';

// Add state for PayPal
const [paypalLoading, setPaypalLoading] = useState(false);
const [paypalError, setPaypalError] = useState(null);

// PayPal handlers
const handlePayPalSuccess = (paymentData) => {
  console.log('PayPal payment successful:', paymentData);
  setBookingSuccess(true);
  setStep(5);
  // Store transaction details if needed
  setBookingData(prev => ({
    ...prev,
    payment: {
      ...prev.payment,
      transactionId: paymentData.transactionId,
      status: 'completed'
    }
  }));
};

const handlePayPalError = (error) => {
  console.error('PayPal payment error:', error);
  setPaypalError(error);
  alert('Payment failed: ' + error);
};

const handlePayPalCancel = (message) => {
  console.log('PayPal payment cancelled:', message);
  alert('Payment was cancelled. You can try again.');
};

// Updated Step 4 JSX
{step === 4 && (
  <div className="bg-white rounded-lg shadow-lg p-8">
    <h2 className="text-3xl font-bold text-gray-800 mb-8">Payment Information</h2>
    
    {/* Payment Method Selection */}
    <div className="space-y-6">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-4">Payment Method</label>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* PayPal Option */}
          <div
            className={`p-4 border-2 rounded-lg cursor-pointer transition-all duration-300 ${
              bookingData.payment.method === 'paypal' ? 'border-blue-600 bg-blue-50' : 'border-gray-200 hover:border-blue-300'
            }`}
            onClick={() => handleInputChange('payment', 'method', 'paypal')}
          >
            <div className="text-center">
              <div className="text-2xl mb-2">💳</div>
              <div className="font-semibold">PayPal</div>
              <div className="text-sm text-gray-600">Secure online payment</div>
            </div>
          </div>
          
          {/* Cash Option */}
          <div
            className={`p-4 border-2 rounded-lg cursor-pointer transition-all duration-300 ${
              bookingData.payment.method === 'cash' ? 'border-blue-600 bg-blue-50' : 'border-gray-200 hover:border-blue-300'
            }`}
            onClick={() => handleInputChange('payment', 'method', 'cash')}
          >
            <div className="text-center">
              <div className="text-2xl mb-2">💷</div>
              <div className="font-semibold">Cash</div>
              <div className="text-sm text-gray-600">Pay on arrival</div>
            </div>
          </div>
        </div>
      </div>

      {/* PayPal Payment Section */}
      {bookingData.payment.method === 'paypal' && (
        <div className="bg-blue-50 p-6 rounded-lg">
          <h3 className="text-lg font-semibold text-blue-800 mb-4">PayPal Payment</h3>
          
          {paypalError && (
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
              {paypalError}
            </div>
          )}
          
          <PayPalPayment
            bookingData={bookingData}
            onSuccess={handlePayPalSuccess}
            onError={handlePayPalError}
            onCancel={handlePayPalCancel}
          />
        </div>
      )}

      {/* Cash Payment Section */}
      {bookingData.payment.method === 'cash' && (
        <div className="bg-green-50 p-6 rounded-lg">
          <h3 className="text-lg font-semibold text-green-800 mb-2">Cash Payment</h3>
          <p className="text-green-700 mb-4">
            You can pay in cash when you arrive for your appointment. Please bring the exact amount if possible.
          </p>
          
          {/* Continue button for cash payments */}
          <button
            onClick={handleCashBooking}
            className="bg-green-600 text-white px-6 py-3 rounded-lg hover:bg-green-700 transition-colors"
          >
            Confirm Cash Booking
          </button>
        </div>
      )}
    </div>

    {/* Booking Summary */}
    <div className="mt-8 bg-gray-50 p-6 rounded-lg">
      <h3 className="text-lg font-semibold text-gray-800 mb-4">Booking Summary</h3>
      {/* Your existing booking summary code */}
    </div>
  </div>
)}
```

## 🔧 Cash Booking Handler

Add a handler for cash bookings:

```jsx
const handleCashBooking = async () => {
  try {
    setLoading(true);
    
    const response = await fetch('/api/paypal/bookings/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        service_id: bookingData.selectedService?.id,
        date: bookingData.date,
        time: bookingData.time,
        customer_first_name: bookingData.customer.firstName,
        customer_last_name: bookingData.customer.lastName,
        customer_email: bookingData.customer.email,
        customer_phone: bookingData.customer.phone,
        vehicle_registration: bookingData.vehicle.registration,
        vehicle_make: bookingData.vehicle.make,
        vehicle_model: bookingData.vehicle.model,
        vehicle_year: bookingData.vehicle.year,
        payment_amount: calculateTotal(),
        payment_currency: 'GBP',
        payment_method: 'cash',
        payment_status: 'pending'
      })
    });

    if (!response.ok) {
      throw new Error('Failed to create booking');
    }

    const booking = await response.json();
    setBookingSuccess(true);
    setStep(5);
    
  } catch (error) {
    console.error('Error creating cash booking:', error);
    alert('Failed to create booking. Please try again.');
  } finally {
    setLoading(false);
  }
};
```

## 🔑 Environment Configuration

Add your PayPal Client ID to your environment variables:

```env
# Frontend .env file
REACT_APP_PAYPAL_CLIENT_ID=your_real_paypal_client_id_here
```

Then use it in your component:

```jsx
const initialOptions = {
  "client-id": process.env.REACT_APP_PAYPAL_CLIENT_ID,
  currency: "GBP",
  intent: "capture"
};
```

## 🚀 Key Benefits

✅ **Single Backend Endpoint**: Uses your simplified `/api/paypal/capture-payment/` for everything  
✅ **No Webhooks**: Direct payment confirmation  
✅ **Error Handling**: Comprehensive error handling  
✅ **Loading States**: User-friendly loading indicators  
✅ **Multiple Payment Methods**: PayPal and Cash options  

Your frontend will now work seamlessly with your simplified PayPal backend system!