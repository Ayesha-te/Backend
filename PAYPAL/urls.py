from django.urls import path
from .views import ServiceListAPIView, BookingListCreateAPIView, PayPalCapturePaymentAPIView

urlpatterns = [
    path('api/services/', ServiceListAPIView.as_view(), name='services-list'),
    path('api/bookings/', BookingListCreateAPIView.as_view(), name='booking-list-create'),
    path('api/paypal/capture-payment/', PayPalCapturePaymentAPIView.as_view(), name='paypal-capture-payment'),
]
