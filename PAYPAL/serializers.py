from rest_framework import serializers
from .models import Service, Booking

class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ['id', 'name', 'price', 'category']

class BookingSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    service = ServiceSerializer(read_only=True)
    service_id = serializers.PrimaryKeyRelatedField(
        queryset=Service.objects.all(), source='service', write_only=True
    )

    class Meta:
        model = Booking
        fields = [
            'id', 'user', 'service', 'service_id', 'scheduled_for',
            'vehicle_number', 'vehicle_details', 'status', 'created_at',
            'payment_completed', 'payment_id',
        ]
        read_only_fields = ['status', 'created_at', 'payment_completed', 'payment_id']
