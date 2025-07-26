from django.db import models
from django.conf import settings

class Service(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    category = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bookings')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='bookings')
    scheduled_for = models.DateTimeField()  # Date and time of booking
    vehicle_number = models.CharField(max_length=20)
    vehicle_details = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    payment_completed = models.BooleanField(default=False)
    payment_id = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        # If user has username attribute, use it, else fallback to email or str(user)
        user_identifier = getattr(self.user, 'username', None) or getattr(self.user, 'email', str(self.user))
        return f'Booking #{self.id} by {user_identifier} for {self.service.name}'
