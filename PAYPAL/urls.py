from django.urls import path
from .views import (
    ServiceListAPIView, 
    BookingListCreateAPIView, 
    BookingVerifyAPIView, 
    PaymentCaptureAPIView,
    BookingDebugAPIView
)

urlpatterns = [
    path('services/', ServiceListAPIView.as_view(), name='services-list'),
    path('bookings/', BookingListCreateAPIView.as_view(), name='booking-list-create'),
    path('bookings/debug/', BookingDebugAPIView.as_view(), name='booking-debug'),
    path('bookings/verify/<str:token>/', BookingVerifyAPIView.as_view(), name='booking-verify'),
    path('capture-payment/', PaymentCaptureAPIView.as_view(), name='paypal-capture-payment'),
]
