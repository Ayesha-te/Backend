# Access Auto Services - Backend API Documentation

## Overview
This backend provides a comprehensive booking system with PayPal integration, email verification, and automated reminders for Access Auto Services.

## Base URL
- Production: `https://backend-kzpz.onrender.com`
- Development: `http://localhost:8000`

## Authentication
Most endpoints require JWT authentication. Include the token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

## API Endpoints

### 1. PayPal/Booking Endpoints (`/api/paypal/`)

#### Get Services
- **URL**: `/api/paypal/services/`
- **Method**: `GET`
- **Auth**: Not required
- **Description**: Get list of all active services
- **Response**:
```json
[
  {
    "id": 1,
    "code": "mot",
    "name": "MOT Test",
    "description": "Official MOT testing for Class 4, 5 & 7 vehicles",
    "price": "54.85",
    "active": true
  }
]
```

#### Create Booking
- **URL**: `/api/paypal/bookings/`
- **Method**: `POST`
- **Auth**: Required
- **Description**: Create a new booking
- **Request Body**:
```json
{
  "service_id": 1,
  "motClass": "MOT IV",
  "date": "2024-01-15",
  "time": "10:00",
  "quantity": 1,
  "price": 54.85,
  "vehicle": {
    "make": "Toyota",
    "model": "Corolla",
    "year": "2020",
    "registration": "AB12 CDE",
    "mileage": "50000"
  },
  "customer": {
    "firstName": "John",
    "lastName": "Doe",
    "email": "john@example.com",
    "phone": "01234567890",
    "address": "123 Main St, City"
  },
  "payment": {
    "method": "card",
    "cardNumber": "1234567890123456",
    "expiryDate": "12/25",
    "cvv": "123",
    "nameOnCard": "John Doe"
  }
}
```
- **Response**:
```json
{
  "id": 1,
  "service": 1,
  "date": "2024-01-15",
  "time": "10:00",
  "payment_amount": "54.85",
  "payment_status": "pending",
  "is_verified": false,
  "created": "2024-01-01T10:00:00Z"
}
```

#### Get User Bookings
- **URL**: `/api/paypal/bookings/`
- **Method**: `GET`
- **Auth**: Required
- **Description**: Get all bookings for the authenticated user

#### Create PayPal Order
- **URL**: `/api/paypal/create-order/`
- **Method**: `POST`
- **Auth**: Required
- **Description**: Create a PayPal order for payment
- **Request Body**:
```json
{
  "booking_id": 1
}
```
- **Response**:
```json
{
  "order_id": "PAYPAL_ORDER_ID",
  "booking_id": 1,
  "amount": 54.85,
  "currency": "GBP"
}
```

#### Capture PayPal Payment
- **URL**: `/api/paypal/capture-payment/`
- **Method**: `POST`
- **Auth**: Required
- **Description**: Capture a PayPal payment
- **Request Body**:
```json
{
  "booking_id": 1,
  "paypal_order_id": "PAYPAL_ORDER_ID"
}
```
- **Response**:
```json
{
  "message": "Payment captured successfully!",
  "transaction_id": "TRANSACTION_ID",
  "booking_id": 1
}
```

#### Verify Booking
- **URL**: `/api/paypal/bookings/verify/<token>/`
- **Method**: `GET`
- **Auth**: Not required
- **Description**: Verify a booking using verification token

### 2. Email Service Endpoints (`/api/email/`)

#### Send Email Verification
- **URL**: `/api/email/verification/`
- **Method**: `POST`
- **Auth**: Required
- **Description**: Send email verification for booking
- **Request Body**:
```json
{
  "email": "customer@example.com",
  "booking_details": [
    {
      "service_name": "MOT Test",
      "price": 54.85,
      "date": "2024-01-15",
      "time": "10:00",
      "vehicle_registration": "AB12 CDE"
    }
  ],
  "booking_url": "https://www.access-auto-services.co.uk/booking"
}
```
- **Response**:
```json
{
  "message": "Verification email sent successfully",
  "verification_id": 1
}
```

#### Verify Email Token
- **URL**: `/api/email/verification/verify/<token>/`
- **Method**: `GET`
- **Auth**: Not required
- **Description**: Verify email using verification token
- **Response**:
```json
{
  "message": "Email verified successfully",
  "email": "customer@example.com"
}
```

#### Schedule Booking Reminder
- **URL**: `/api/email/reminder/`
- **Method**: `POST`
- **Auth**: Required
- **Description**: Schedule a 24-hour reminder email
- **Request Body**:
```json
{
  "email": "customer@example.com",
  "booking_details": [
    {
      "service_name": "MOT Test",
      "price": 54.85,
      "vehicle_registration": "AB12 CDE"
    }
  ],
  "appointment_datetime": "2024-01-15T10:00:00",
  "booking_url": "https://www.access-auto-services.co.uk/booking"
}
```
- **Response**:
```json
{
  "message": "Booking reminder scheduled successfully",
  "reminder_id": 1,
  "scheduled_for": "2024-01-14T10:00:00Z"
}
```

#### Send Reminder Now (Manual)
- **URL**: `/api/email/reminder/send/`
- **Method**: `POST`
- **Auth**: Required
- **Description**: Manually send a reminder email
- **Request Body**:
```json
{
  "reminder_id": 1
}
```

### 3. Account Endpoints (`/api/accounts/`)
- User registration, login, and profile management
- JWT token management

### 4. DVLA Endpoints (`/api/dvla/`)
- Vehicle lookup and verification services

## Email Features

### Immediate Emails
When a booking is created, the system automatically sends:
1. **Booking Confirmation Email** - Immediate confirmation with booking details
2. **Email Verification Email** - Link to verify the customer's email address

### Scheduled Emails
- **24-Hour Reminder** - Automatically scheduled 24 hours before the appointment
- Uses Celery for background task processing (falls back gracefully if not available)

## PayPal Integration

### Configuration
Set these environment variables:
```
PAYPAL_CLIENT_ID=your_paypal_client_id
PAYPAL_SECRET=your_paypal_secret
PAYPAL_API_BASE=https://api-m.sandbox.paypal.com  # or production URL
```

### Payment Flow
1. Create booking → Get booking ID
2. Create PayPal order → Get PayPal order ID
3. Customer completes payment on frontend
4. Capture payment → Booking marked as paid
5. Confirmation email sent automatically

## Error Handling

### Common Error Responses
```json
{
  "error": "Error message description"
}
```

### HTTP Status Codes
- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `404` - Not Found
- `500` - Internal Server Error

## Environment Variables

### Required
```
SECRET_KEY=your-django-secret-key
DEBUG=False
ALLOWED_HOSTS=your-domain.com,localhost
DEFAULT_FROM_EMAIL=your-email@gmail.com
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
PAYPAL_CLIENT_ID=your-paypal-client-id
PAYPAL_SECRET=your-paypal-secret
```

### Optional
```
DATABASE_URL=postgresql://user:pass@host:port/db
REDIS_URL=redis://localhost:6379/0
CORS_ALLOWED_ORIGINS=https://your-frontend.com
```

## Database Models

### Service
- `id`, `code`, `name`, `description`, `price`, `active`

### Booking
- User info, service, date/time, vehicle details, customer info, payment info
- Payment tracking: `paypal_order_id`, `paypal_transaction_id`, `payment_amount`
- Status: `is_paid`, `is_verified`, `payment_status`

### EmailVerification
- `email`, `verification_token`, `booking_details`, `is_verified`

### BookingReminder
- `email`, `booking_details`, `appointment_datetime`, `scheduled_for`, `reminder_sent`

## Testing

Run the test script to verify all components:
```bash
python test_booking_system.py
```

## Deployment

### Production Checklist
1. Set all environment variables
2. Configure email settings (SMTP)
3. Set up PayPal production credentials
4. Configure Redis for Celery (optional)
5. Set up SSL certificates
6. Configure CORS for your frontend domain

### Celery Setup (Optional)
For background email processing:
```bash
# Install Redis
# Start Celery worker
celery -A backend worker --loglevel=info

# Start Celery beat (for scheduled tasks)
celery -A backend beat --loglevel=info
```

## Support
For issues or questions, check the logs in the Django admin panel or contact the development team.