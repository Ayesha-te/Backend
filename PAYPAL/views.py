from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Service, Booking
from .serializers import ServiceSerializer, BookingSerializer
from django.conf import settings
import requests

# List all services
class ServiceListAPIView(generics.ListAPIView):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [permissions.AllowAny]

# Booking List/Create View
class BookingListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

# PayPal payment capture endpoint (simplified example)
class PayPalCapturePaymentAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        # Payload expected: {"orderID": "paypal-order-id", "bookingID": booking_id}
        order_id = request.data.get('orderID')
        booking_id = request.data.get('bookingID')

        if not order_id or not booking_id:
            return Response({"error": "orderID and bookingID are required"}, status=status.HTTP_400_BAD_REQUEST)

        # Verify the payment with PayPal API
        # This example assumes you have client_id and secret in settings and you fetch access token
        # Then verify order and capture payment
        access_token = get_paypal_access_token()
        capture_response = capture_paypal_order(access_token, order_id)

        if capture_response.get('status') == 'COMPLETED':
            # Mark booking payment as completed
            try:
                booking = Booking.objects.get(id=booking_id, user=request.user)
                booking.payment_completed = True
                booking.payment_id = order_id
                booking.status = 'confirmed'
                booking.save()
                return Response({"message": "Payment successful and booking confirmed"})
            except Booking.DoesNotExist:
                return Response({"error": "Booking not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"error": "Payment not completed"}, status=status.HTTP_400_BAD_REQUEST)


# Helper functions for PayPal API

def get_paypal_access_token():
    import base64

    client_id = settings.PAYPAL_CLIENT_ID
    secret = settings.PAYPAL_SECRET
    auth = base64.b64encode(f"{client_id}:{secret}".encode()).decode()

    headers = {
        "Authorization": f"Basic {auth}",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {"grant_type": "client_credentials"}

    response = requests.post("https://api-m.sandbox.paypal.com/v1/oauth2/token", headers=headers, data=data)
    response.raise_for_status()
    return response.json()['access_token']

def capture_paypal_order(access_token, order_id):
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    url = f"https://api-m.sandbox.paypal.com/v2/checkout/orders/{order_id}/capture"
    response = requests.post(url, headers=headers)
    if response.status_code == 201:
        return response.json()['purchase_units'][0]['payments']['captures'][0]
    return {"status": "FAILED"}
