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


# 3. Cart: List and Add cart items (now allows anonymous users)
class CartListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = CartItemSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        # For authenticated users, return their cart items
        if self.request.user.is_authenticated:
            return CartItem.objects.filter(user=self.request.user)
        
        # For anonymous users, use session-based cart (simplified approach)
        # In a real implementation, you might want to use session storage
        # For now, return empty queryset for anonymous users
        return CartItem.objects.none()

    def perform_create(self, serializer):
        # Add or update quantity if item exists
        service = serializer.validated_data.get('service')
        
        if self.request.user.is_authenticated:
            user = self.request.user
            cart_item, created = CartItem.objects.get_or_create(user=user, service=service)
            if not created:
                cart_item.quantity += serializer.validated_data.get('quantity', 1)
                cart_item.save()
            else:
                serializer.save(user=user)
        else:
            # For anonymous users, we'll skip cart functionality for now
            # In a real implementation, you'd use session storage
            pass


# 4. Remove item from cart
class CartItemDestroyAPIView(generics.DestroyAPIView):
    serializer_class = CartItemSerializer
    permission_classes = [permissions.AllowAny]
    lookup_url_kwarg = 'item_id'

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return CartItem.objects.filter(user=self.request.user)
        # For anonymous users, return empty queryset (cart functionality disabled)
        return CartItem.objects.none()


# 5. Proceed to Booking from Cart (create bookings for each cart item, then clear cart)
class ProceedToBookingAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        if request.user.is_authenticated:
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
        else:
            # For anonymous users, allow direct booking without cart
            # They can provide booking details directly in the request
            service_id = request.data.get('service_id')
            if not service_id:
                return Response({"error": "service_id is required for anonymous booking"}, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                service = Service.objects.get(id=service_id)
                booking = Booking.objects.create(
                    user=None,  # Anonymous user
                    service=service,
                    quantity=request.data.get('quantity', 1),
                    date=request.data.get('date'),
                    time=request.data.get('time'),
                    status='pending',
                    # Add customer information for anonymous bookings
                    customer_email=request.data.get('customer_email', ''),
                    customer_first_name=request.data.get('customer_first_name', ''),
                    customer_last_name=request.data.get('customer_last_name', ''),
                    customer_phone=request.data.get('customer_phone', ''),
                )
                return Response({
                    "message": "Anonymous booking created successfully",
                    "booking_id": booking.id
                }, status=status.HTTP_201_CREATED)
            except Service.DoesNotExist:
                return Response({"error": "Service not found"}, status=status.HTTP_404_NOT_FOUND)


# 6. List user's bookings
class BookingListAPIView(generics.ListAPIView):
    serializer_class = BookingSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        # Allow authenticated users to see their bookings
        if self.request.user.is_authenticated:
            return Booking.objects.filter(user=self.request.user)
        
        # Allow anonymous users to see bookings by providing email
        email = self.request.query_params.get('email')
        if email:
            return Booking.objects.filter(customer_email=email)
        
        # If no email provided and not authenticated, return empty queryset
        return Booking.objects.none()

