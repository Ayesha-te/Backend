from django.urls import path
from .views import ServiceListAPIView, BookingListCreateAPIView, BookingVerifyAPIView, PaymentCaptureAPIView

urlpatterns = [
    path('services/', ServiceListAPIView.as_view(), name='services-list'),
    path('bookings/', BookingListCreateAPIView.as_view(), name='booking-list-create'),
    path('bookings/verify/<str:token>/', BookingVerifyAPIView.as_view(), name='booking-verify'),
    path('capture-payment/', PaymentCaptureAPIView.as_view(), name='paypal-capture-payment'),
]
