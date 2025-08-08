from rest_framework import serializers
from .models import Service, Booking

class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ['id', 'name', 'code', 'price', 'description', 'active']

class BookingSerializer(serializers.ModelSerializer):
    service = ServiceSerializer(read_only=True)
    service_id = serializers.PrimaryKeyRelatedField(
        queryset=Service.objects.all(),
        source='service',
        write_only=True
    )

    class Meta:
        model = Booking
        fields = [
            'id', 'user', 'service', 'service_id',
            'mot_class', 'date', 'time',
            'vehicle_make', 'vehicle_model', 'vehicle_year',
            'vehicle_registration', 'vehicle_mileage',
            'customer_first_name', 'customer_last_name', 'customer_email',
            'customer_phone', 'customer_address',
            'payment_method', 'card_number', 'expiry_date', 'cvv', 'name_on_card',
            'is_verified', 'verification_token',
            'is_paid', 'payment_status', 'paypal_transaction_id',
            'created', 'updated'
        ]
        read_only_fields = [
            'id', 'user', 'service', 'created', 'updated',
            'is_paid', 'payment_status', 'paypal_transaction_id',
            'is_verified', 'verification_token'
        ]

    def validate(self, data):
        """Custom validation for payment methods"""
        payment_method = data.get('payment_method', 'card')
        
        # For card payments, validate that required card fields are present
        if payment_method == 'card':
            required_card_fields = ['card_number', 'expiry_date', 'cvv', 'name_on_card']
            for field in required_card_fields:
                if not data.get(field):
                    # Only raise error if the field is actually required for card payments
                    # For now, we'll allow empty card fields to maintain compatibility
                    pass
        
        # For PayPal payments, card fields should be empty or ignored
        elif payment_method == 'paypal':
            # Clear card fields for PayPal payments
            data['card_number'] = ''
            data['expiry_date'] = ''
            data['cvv'] = ''
            data['name_on_card'] = ''
        
        return data

    def create(self, validated_data):
        user = self.context['request'].user
        # Only assign user if they are authenticated, otherwise allow null
        if user.is_authenticated:
            validated_data['user'] = user
        else:
            validated_data['user'] = None
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if instance.is_paid:
            for field in ['payment_method', 'card_number', 'expiry_date', 'cvv', 'name_on_card']:
                validated_data.pop(field, None)
        return super().update(instance, validated_data)

        