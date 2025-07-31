from django.urls import path
from .views import (
    VehicleInfoAPIView,
    ServiceListAPIView,
    CartListCreateAPIView,
    CartItemDestroyAPIView,
    ProceedToBookingAPIView,
    BookingListAPIView,
)

urlpatterns = [
    path('vehicle-info/', VehicleInfoAPIView.as_view(), name='vehicle-info'),
    path('services/', ServiceListAPIView.as_view(), name='service-list'),
    path('cart/', CartListCreateAPIView.as_view(), name='cart-list-create'),
    path('cart/item/<int:item_id>/', CartItemDestroyAPIView.as_view(), name='cart-item-destroy'),
    path('proceed-to-booking/', ProceedToBookingAPIView.as_view(), name='proceed-to-booking'),
    path('bookings/', BookingListAPIView.as_view(), name='booking-list'),
]
