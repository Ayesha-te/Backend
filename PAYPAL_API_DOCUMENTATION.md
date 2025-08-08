# PayPal Integration API Documentation

## Overview
This document describes the backend API endpoints for PayPal payment integration. The backend has been updated to properly handle PayPal payments with the frontend data structure.

## Frontend Data Structure

The frontend should send booking data in this format:

```javascript
const bookingData = {
  service_id: 1,
  date: '2024-01-15',
  time: '10:00',
  motClass: 'Class 4',
  price: 54.85,
  quantity: 1,
  vehicle: {
    make: 'Toyota',
    model: 'Corolla',
    year: '2018',
    registration: 'AB18 XYZ',
    mileage: '45000'
  },
  customer: {
    firstName: 'John',
    lastName: 'Doe',
    email: 'john.doe@example.com',
    phone: '07123456789',
    address: '123 Test Street, Test City, TE1 2ST'
  },
  payment: {
    method: 'paypal',
    cardNumber: '',      // Empty for PayPal
    expiryDate: '',      // Empty for PayPal
    cvv: '',             // Empty for PayPal
    nameOnCard: ''       // Empty for PayPal
  }
};
```

## API Endpoints

### 1. Create Booking
**Endpoint:** `POST /api/bookings/`

**Description:** Creates a new booking with PayPal payment method.

**Request Body:** Use the `bookingData` structure above.

**Response:**
```json
{
  "id": 123,
  "service": {
    "id": 1,
    "name": "MOT Test",
    "price": "54.85"
  },
  "payment_method": "paypal",
  "payment_amount": "54.85",
  "payment_currency": "GBP",
  "customer_email": "john.doe@example.com",
  "date": "2024-01-15",
  "time": "10:00",
  "created": "2024-01-10T10:00:00Z"
}
```

### 2. Create PayPal Order
**Endpoint:** `POST /api/create-order/`

**Description:** Creates a PayPal order for an existing booking.

**Request Body:**
```json
{
  "booking_id": 123,
  "customer_email": "john.doe@example.com"  // Required for anonymous users
}
```

**Response:**
```json
{
  "order_id": "8XY12345678901234",
  "booking_id": 123,
  "amount": 54.85,
  "currency": "GBP",
  "status": "created"
}
```

### 3. Capture Payment
**Endpoint:** `POST /api/capture-payment/`

**Description:** Captures payment after user approves PayPal payment.

**Request Body:**
```json
{
  "booking_id": 123,
  "paypal_order_id": "8XY12345678901234",
  "customer_email": "john.doe@example.com",  // Required for anonymous users
  "action": "capture",
  "payment_method": "paypal"
}
```

**Response:**
```json
{
  "message": "Payment captured successfully!",
  "transaction_id": "9AB12345678901234",
  "booking_id": 123,
  "booking_status": "confirmed",
  "payment_status": "completed",
  "payment_method": "paypal"
}
```

## Frontend Integration Flow

### Step 1: Create Booking
```javascript
// Create booking with PayPal payment method
const response = await fetch('/api/bookings/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify(bookingData)
});

const booking = await response.json();
const bookingId = booking.id;
```

### Step 2: Create PayPal Order
```javascript
// Create PayPal order
const orderResponse = await fetch('/api/create-order/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    booking_id: bookingId,
    customer_email: bookingData.customer.email
  })
});

const orderData = await orderResponse.json();
const paypalOrderId = orderData.order_id;
```

### Step 3: Initialize PayPal Checkout
```javascript
// Initialize PayPal checkout with the order ID
paypal.Buttons({
  createOrder: function(data, actions) {
    // Return the order ID from step 2
    return paypalOrderId;
  },
  onApprove: function(data, actions) {
    // Capture payment on backend
    return fetch('/api/capture-payment/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        booking_id: bookingId,
        paypal_order_id: data.orderID,
        customer_email: bookingData.customer.email,
        action: 'capture',
        payment_method: 'paypal'
      })
    }).then(response => response.json())
      .then(result => {
        if (result.message) {
          // Payment successful
          alert('Payment completed successfully!');
          // Redirect to success page
          window.location.href = '/booking-success';
        } else {
          // Payment failed
          alert('Payment failed: ' + result.error);
        }
      });
  },
  onError: function(err) {
    console.error('PayPal error:', err);
    alert('Payment failed. Please try again.');
  }
}).render('#paypal-button-container');
```

## Error Handling

### Common Error Responses

**400 Bad Request:**
```json
{
  "error": "Missing booking_id"
}
```

**404 Not Found:**
```json
{
  "error": "Booking not found"
}
```

**500 Internal Server Error:**
```json
{
  "error": "Failed to create payment order. Please try again.",
  "details": "Detailed error message (only in DEBUG mode)"
}
```

## Backend Changes Made

### 1. Improved Booking Creation
- Enhanced `BookingListCreateAPIView.perform_create()` to properly handle PayPal payments
- Card fields are left empty when payment method is 'paypal'
- Better error handling and logging

### 2. Enhanced Serializer Validation
- Added `validate()` method in `BookingSerializer` to handle different payment methods
- Automatically clears card fields for PayPal payments
- Maintains compatibility with existing card payments

### 3. Improved PayPal Order Creation
- Enhanced `PayPalCreateOrderAPIView` with better logging and error handling
- Validates payment amounts before creating orders
- Ensures payment method is set to 'paypal' when creating orders
- Returns more detailed response data

### 4. Better Error Handling
- Comprehensive logging throughout the payment flow
- Detailed error messages for debugging
- Graceful handling of edge cases

## Testing

A test script has been created at `test_paypal_integration.py` to verify the integration:

```bash
python test_paypal_integration.py
```

This script tests:
1. PayPal API connection
2. Booking creation with PayPal payment method
3. PayPal order creation
4. Order details retrieval

## Environment Variables

Ensure these environment variables are set:

```bash
PAYPAL_CLIENT_ID=your_paypal_client_id
PAYPAL_SECRET=your_paypal_secret
PAYPAL_API_BASE=https://api-m.sandbox.paypal.com  # For sandbox
# PAYPAL_API_BASE=https://api-m.paypal.com  # For production
```

## Notes

1. **Anonymous Users:** The API supports both authenticated and anonymous users. For anonymous users, `customer_email` is required in PayPal order creation and payment capture requests.

2. **Payment Amount:** The system uses `booking.payment_amount` if available, otherwise falls back to `booking.service.price`.

3. **Currency:** Currently hardcoded to 'GBP' but can be made configurable.

4. **Card Fields:** For PayPal payments, all card-related fields (`cardNumber`, `expiryDate`, `cvv`, `nameOnCard`) should be empty strings.

5. **Logging:** Comprehensive logging is implemented for debugging and monitoring payment flows.

## Support

If you encounter any issues with the PayPal integration, check:
1. PayPal credentials are correctly configured
2. API endpoints are being called in the correct order
3. Required fields are being sent in requests
4. Check server logs for detailed error messages