from django.db import models
from django.conf import settings

class Service(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    duration_minutes = models.PositiveIntegerField(default=60)

    def __str__(self):
        return self.name


class CartItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cart_items')
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('user', 'service')

    def __str__(self):
        return f"{self.service.name} x {self.quantity} for {self.user}"


class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='dvlaa_bookings', null=True, blank=True)
    service = models.ForeignKey(Service, on_delete=models.PROTECT, related_name='dvlaa_bookings')
    quantity = models.PositiveIntegerField(default=1)
    motClass = models.CharField(max_length=100, blank=True, null=True)
    scheduled_for = models.DateTimeField(null=True, blank=True)
    payment_completed = models.BooleanField(default=False)
    payment_id = models.CharField(max_length=255, blank=True, null=True)
    payment_method = models.CharField(max_length=20, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Customer information for anonymous bookings
    customer_email = models.EmailField(blank=True, null=True)
    customer_first_name = models.CharField(max_length=64, blank=True, null=True)
    customer_last_name = models.CharField(max_length=64, blank=True, null=True)
    customer_phone = models.CharField(max_length=32, blank=True, null=True)
    customer_address = models.TextField(blank=True, null=True)

    def __str__(self):
        user_info = self.user.username if self.user else "Anonymous"
        return f"Booking #{self.id} - {self.service.name} for {user_info}"
