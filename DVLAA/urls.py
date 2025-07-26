from django.urls import path
from .views import (
    VehicleInfoAPIView,
    ServiceListAPIView,
    CartListCreateAPIView,
    CartItemDestroyAPIView,
    BookingListCreateAPIView,
)

urlpatterns = [
    path('api/vehicle-info/', VehicleInfoAPIView.as_view(), name='vehicle-info'),
    path('api/services/', ServiceListAPIView.as_view(), name='services-list'),
    path('api/cart/', CartListCreateAPIView.as_view(), name='cart-list-create'),
    path('api/cart/<int:item_id>/', CartItemDestroyAPIView.as_view(), name='cart-item-delete'),
    path('api/bookings/', BookingListCreateAPIView.as_view(), name='booking-list-create'),
]
