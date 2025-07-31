from rest_framework import serializers
from .models import Service, CartItem, Booking

class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ['id', 'name', 'description', 'price', 'duration_minutes']


class CartItemSerializer(serializers.ModelSerializer):
    service = ServiceSerializer(read_only=True)
    service_id = serializers.PrimaryKeyRelatedField(queryset=Service.objects.all(), source='service', write_only=True)

    class Meta:
        model = CartItem
        fields = ['id', 'service', 'service_id', 'quantity']

    def create(self, validated_data):
        user = self.context['request'].user
        service = validated_data['service']
        quantity = validated_data.get('quantity', 1)
        cart_item, created = CartItem.objects.get_or_create(user=user, service=service)
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
        return cart_item


class BookingSerializer(serializers.ModelSerializer):
    service = ServiceSerializer(read_only=True)
    service_id = serializers.PrimaryKeyRelatedField(queryset=Service.objects.all(), source='service', write_only=True)

    class Meta:
        model = Booking
        fields = [
            'id', 'user', 'service', 'service_id', 'quantity', 'motClass', 'scheduled_for', 'payment_completed',
            'payment_id', 'payment_method', 'status', 'created_at'
        ]
        read_only_fields = ['id', 'user', 'payment_completed', 'payment_id', 'payment_method', 'status', 'created_at']

    def create(self, validated_data):
        return super().create(validated_data)
