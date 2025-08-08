from django.urls import path
from .views import (
    ServiceListAPIView, 
    BookingListCreateAPIView, 
    BookingDetailAPIView,
    BookingVerifyAPIView, 
    PaymentCaptureAPIView,
    PayPalCreateOrderAPIView,
    PayPalWebhookAPIView,
    BookingDebugAPIView
)

urlpatterns = [
    path('services/', ServiceListAPIView.as_view(), name='services-list'),
    path('bookings/', BookingListCreateAPIView.as_view(), name='booking-list-create'),
    path('bookings/<int:booking_id>/', BookingDetailAPIView.as_view(), name='booking-detail'),
    path('bookings/debug/', BookingDebugAPIView.as_view(), name='booking-debug'),
    path('bookings/verify/<str:token>/', BookingVerifyAPIView.as_view(), name='booking-verify'),
    path('create-order/', PayPalCreateOrderAPIView.as_view(), name='paypal-create-order'),
    path('capture-payment/', PaymentCaptureAPIView.as_view(), name='paypal-capture-payment'),
    path('webhook/', PayPalWebhookAPIView.as_view(), name='paypal-webhook'),
]
