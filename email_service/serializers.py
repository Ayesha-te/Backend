from rest_framework import serializers
from .models import EmailVerification, BookingReminder

class EmailVerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailVerification
        fields = ['email', 'booking_details', 'booking_url']

class BookingReminderSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookingReminder
        fields = ['email', 'booking_details', 'appointment_datetime', 'booking_url']