from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import requests
from django.conf import settings

from .models import Service, CartItem, Booking
from .serializers import ServiceSerializer, CartItemSerializer, BookingSerializer


# DVLA Vehicle info API view
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


# Services list view
class ServiceListAPIView(generics.ListAPIView):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [permissions.AllowAny]


# Cart Views
class CartListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return CartItem.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CartItemDestroyAPIView(generics.DestroyAPIView):
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_url_kwarg = 'item_id'

    def get_queryset(self):
        return CartItem.objects.filter(user=self.request.user)


# Booking Create & List View
class BookingListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
