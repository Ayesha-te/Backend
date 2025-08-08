from django.db import models
from django.conf import settings  # for AUTH_USER_MODEL

class Service(models.Model):
    code = models.CharField(max_length=64, unique=True)
    name = models.CharField(max_length=128)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Booking(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bookings', null=True, blank=True)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    mot_class = models.CharField(max_length=32, blank=True)
    date = models.DateField()
    time = models.CharField(max_length=16)

    # Vehicle info
    vehicle_make = models.CharField(max_length=64, blank=True)
    vehicle_model = models.CharField(max_length=64, blank=True)
    vehicle_year = models.CharField(max_length=8, blank=True)
    vehicle_registration = models.CharField(max_length=32, blank=True)
    vehicle_mileage = models.CharField(max_length=32, blank=True)

    # Customer info
    customer_first_name = models.CharField(max_length=64, blank=True)
    customer_last_name = models.CharField(max_length=64, blank=True)
    customer_email = models.EmailField(blank=True)
    customer_phone = models.CharField(max_length=32, blank=True)
    customer_address = models.TextField(blank=True)

    # Payment info
    payment_method = models.CharField(max_length=16, default='card')
    card_number = models.CharField(max_length=32, blank=True)
    expiry_date = models.CharField(max_length=8, blank=True)
    cvv = models.CharField(max_length=8, blank=True)
    name_on_card = models.CharField(max_length=128, blank=True)

    # Booking status
    is_verified = models.BooleanField(default=False)
    verification_token = models.CharField(max_length=64, blank=True, null=True)

    # Payment status
    is_paid = models.BooleanField(default=False)
    payment_status = models.CharField(max_length=32, default='pending')
    paypal_order_id = models.CharField(max_length=128, blank=True, null=True)
    paypal_transaction_id = models.CharField(max_length=128, blank=True, null=True)
    payment_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    payment_currency = models.CharField(max_length=3, default='GBP')

    # Timestamps
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Booking: {self.service.name} on {self.date} for {self.user.username}"
