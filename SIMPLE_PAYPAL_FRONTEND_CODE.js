// Simple PayPal Integration for Your React Component
// Add this to your existing booking component

// 1. Install PayPal SDK
// npm install @paypal/react-paypal-js

// 2. Import at the top of your component
import { PayPalScriptProvider, PayPalButtons } from '@paypal/react-paypal-js';

// 3. Add these functions to your component

// PayPal configuration
const paypalOptions = {
  "client-id": "YOUR_PAYPAL_CLIENT_ID", // Replace with your real client ID
  currency: "GBP",
  intent: "capture"
};

// Calculate total amount
const calculateTotal = () => {
  if (fromCart && cart.length > 0) {
    return cart.reduce((total, item) => total + (item.price * item.qty), 0);
  }
  return selectedService?.code === 'mot' && bookingData.motClass ? motPrice : selectedService?.price || 0;
};

// Create PayPal order
const createPayPalOrder = async () => {
  try {
    // First create the booking
    const bookingResponse = await fetch('/api/paypal/bookings/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        service_id: selectedService?.id,
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
        payment_method: 'paypal'
      })
    });

    const booking = await bookingResponse.json();
    
    // Create PayPal order using your simplified endpoint
    const orderResponse = await fetch('/api/paypal/capture-payment/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        booking_id: booking.id,
        customer_email: bookingData.customer.email,
        action: 'create'
      })
    });

    const orderData = await orderResponse.json();
    
    // Store booking ID for later use
    setBookingData(prev => ({ ...prev, bookingId: booking.id }));
    
    return orderData.order_id;
    
  } catch (error) {
    console.error('Error creating PayPal order:', error);
    alert('Failed to create payment order. Please try again.');
    throw error;
  }
};

// Capture PayPal payment
const capturePayPalPayment = async (data) => {
  try {
    const response = await fetch('/api/paypal/capture-payment/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        booking_id: bookingData.bookingId,
        paypal_order_id: data.orderID,
        customer_email: bookingData.customer.email,
        action: 'capture'
      })
    });

    const result = await response.json();
    
    if (response.ok) {
      // Payment successful - go to success step
      setBookingSuccess(true);
      setStep(5);
      alert('Payment successful! Booking confirmed.');
    } else {
      throw new Error(result.error || 'Payment failed');
    }
    
  } catch (error) {
    console.error('Error capturing payment:', error);
    alert('Payment failed: ' + error.message);
  }
};

// Handle cash booking
const handleCashBooking = async () => {
  try {
    const response = await fetch('/api/paypal/bookings/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        service_id: selectedService?.id,
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

    if (response.ok) {
      setBookingSuccess(true);
      setStep(5);
      alert('Cash booking confirmed!');
    } else {
      throw new Error('Failed to create booking');
    }
    
  } catch (error) {
    console.error('Error creating cash booking:', error);
    alert('Failed to create booking. Please try again.');
  }
};

// 4. Replace your Step 4 PayPal section with this:

{bookingData.payment.method === 'paypal' && (
  <div className="bg-blue-50 p-6 rounded-lg">
    <h3 className="text-lg font-semibold text-blue-800 mb-4">PayPal Payment</h3>
    <p className="text-blue-700 mb-4">
      Click the PayPal button below to complete your payment securely.
    </p>
    
    <PayPalScriptProvider options={paypalOptions}>
      <PayPalButtons
        style={{
          layout: "vertical",
          color: "blue",
          shape: "rect",
          label: "paypal"
        }}
        createOrder={createPayPalOrder}
        onApprove={capturePayPalPayment}
        onError={(err) => {
          console.error('PayPal error:', err);
          alert('Payment failed. Please try again.');
        }}
        onCancel={() => {
          alert('Payment was cancelled. You can try again.');
        }}
      />
    </PayPalScriptProvider>
  </div>
)}

// 5. Update your cash payment section:

{bookingData.payment.method === 'cash' && (
  <div className="bg-green-50 p-6 rounded-lg">
    <h3 className="text-lg font-semibold text-green-800 mb-2">Cash Payment</h3>
    <p className="text-green-700 mb-4">
      You can pay in cash when you arrive for your appointment. Please bring the exact amount if possible.
    </p>
    
    <button
      onClick={handleCashBooking}
      className="bg-green-600 text-white px-6 py-3 rounded-lg hover:bg-green-700 transition-colors"
    >
      Confirm Cash Booking
    </button>
  </div>
)}

// 6. Remove the credit card section since you're only using PayPal and Cash

// 7. Don't forget to replace "YOUR_PAYPAL_CLIENT_ID" with your real PayPal Client ID