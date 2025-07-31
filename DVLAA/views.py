from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
import requests
from django.conf import settings

from .models import Service, CartItem, Booking
from .serializers import ServiceSerializer, CartItemSerializer, BookingSerializer

# 1. Vehicle info lookup - user submits vehicle reg number and gets data from DVLA API
class VehicleInfoAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        reg_number = request.data.get('reg_number')
        if not reg_number:
            return Response({"error": "Registration number is required"}, status=status.HTTP_400_BAD_REQUEST)

        DVLA_API_URL = "https://driver-vehicle-licensing.api.gov.uk/vehicle-enquiry/v1/vehicles"
        headers = {
            "x-api-key": settings.DVLA_API_KEY,
            "Content-Type": "application/json",
        }

        try:
            response = requests.post(
                DVLA_API_URL,
                json={"registrationNumber": reg_number},
                headers=headers,
                timeout=10,
            )
            if response.status_code == 200:
                return Response(response.json())
            elif response.status_code == 404:
                return Response({"error": "Vehicle not found"}, status=status.HTTP_404_NOT_FOUND)
            else:
                return Response({"error": "DVLA API error"}, status=response.status_code)
        except requests.RequestException as e:
            return Response({"error": str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)


# 2. List all available services
class ServiceListAPIView(generics.ListAPIView):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [permissions.AllowAny]


# 3. Cart: List and Add cart items (authenticated)
class CartListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return CartItem.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # Add or update quantity if item exists
        service = serializer.validated_data.get('service')
        user = self.request.user
        cart_item, created = CartItem.objects.get_or_create(user=user, service=service)
        if not created:
            cart_item.quantity += serializer.validated_data.get('quantity', 1)
            cart_item.save()
        else:
            serializer.save(user=user)


# 4. Remove item from cart
class CartItemDestroyAPIView(generics.DestroyAPIView):
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_url_kwarg = 'item_id'

    def get_queryset(self):
        return CartItem.objects.filter(user=self.request.user)


# 5. Proceed to Booking from Cart (create bookings for each cart item, then clear cart)
class ProceedToBookingAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        cart_items = CartItem.objects.filter(user=request.user)
        if not cart_items.exists():
            return Response({"error": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST)

        bookings_created = []
        for item in cart_items:
            booking = Booking.objects.create(
                user=request.user,
                service=item.service,
                quantity=item.quantity,
                date=request.data.get('date'),  # front sends booking date/time etc.
                time=request.data.get('time'),
                status='pending',
                # Add any other required fields here
            )
            bookings_created.append(booking.id)

        # Clear the cart after booking
        cart_items.delete()

        return Response({
            "message": f"Created {len(bookings_created)} booking(s) from cart",
            "booking_ids": bookings_created
        }, status=status.HTTP_201_CREATED)


# 6. List user's bookings
class BookingListAPIView(generics.ListAPIView):
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user)

