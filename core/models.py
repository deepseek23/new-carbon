from django.db import models
from django.contrib.auth.models import User

class CarbonFootprint(models.Model):
    FUEL_CHOICES = [
        ('petrol', 'Petrol'),
        ('diesel', 'Diesel'),
        ('electric', 'Electric'),
        ('hybrid', 'Hybrid'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="footprints")
    car_travel_km = models.FloatField(default=0)
    fuel_type = models.CharField(max_length=20, choices=FUEL_CHOICES, default='petrol')
    flights_hours = models.FloatField(default=0)
    public_transport_km = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.created_at.date()}"
