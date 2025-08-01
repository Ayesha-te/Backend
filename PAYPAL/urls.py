from django.urls import path
from .views import (
    ServiceListAPIView, 
    BookingListCreateAPIView, 
    BookingVerifyAPIView, 
    PaymentCaptureAPIView,
    PayPalCreateOrderAPIView,
    BookingDebugAPIView
)

urlpatterns = [
    path('services/', ServiceListAPIView.as_view(), name='services-list'),
    path('bookings/', BookingListCreateAPIView.as_view(), name='booking-list-create'),
    path('bookings/debug/', BookingDebugAPIView.as_view(), name='booking-debug'),
    path('bookings/verify/<str:token>/', BookingVerifyAPIView.as_view(), name='booking-verify'),
    path('create-order/', PayPalCreateOrderAPIView.as_view(), name='paypal-create-order'),
    path('capture-payment/', PaymentCaptureAPIView.as_view(), name='paypal-capture-payment'),
]
