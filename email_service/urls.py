from django.urls import path
from .views import (
    EmailVerificationAPIView,
    EmailVerifyTokenAPIView,
    BookingReminderAPIView,
    SendReminderNowAPIView
)

urlpatterns = [
    path('verification/', EmailVerificationAPIView.as_view(), name='email-verification'),
    path('verification/verify/<uuid:token>/', EmailVerifyTokenAPIView.as_view(), name='email-verify-token'),
    path('reminder/', BookingReminderAPIView.as_view(), name='booking-reminder'),
    path('reminder/send/', SendReminderNowAPIView.as_view(), name='send-reminder-now'),
]