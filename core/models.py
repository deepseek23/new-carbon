from django.db import models
from django.contrib.auth.models import User

class CarbonFootprint(models.Model):
    FUEL_CHOICES = [
        ('petrol', 'Petrol'),
        ('diesel', 'Diesel'),
        ('electric', 'Electric'),
        ('hybrid', 'Hybrid'),
    ]

    MEAL_TYPE_CHOICES = [
        ('light', 'Light Meal (vegetarian/vegan)'),
        ('medium', 'Medium Meal (some meat)'),
        ('heavy', 'Heavy Meal (meat-heavy)'),
        ('meat_heavy', 'Meat-Heavy Diet'),
    ]

    WASTE_TYPE_CHOICES = [
        ('low', 'Low Waste (mostly recycled)'),
        ('medium', 'Medium Waste (some recycling)'),
        ('high', 'High Waste (minimal recycling)'),
    ]

    # Emission factors (kg CO₂ per unit)
    FUEL_EMISSION_FACTORS = {
        "petrol": 0.180,   # kg/km
        "diesel": 0.160,   # kg/km
        "electric": 0.060, # kg/km (depends on grid mix, avg value)
        "hybrid": 0.090,   # kg/km
    }

    # Food emission factors (kg CO₂ per meal)
    FOOD_EMISSION_FACTORS = {
        "light": 0.5,      # Vegetarian/vegan meals
        "medium": 1.2,     # Mixed diet with some meat
        "heavy": 2.0,      # Meat-heavy meals
        "meat_heavy": 3.5, # Very meat-heavy diet
    }

    # Waste emission factors (kg CO₂ per kg waste)
    WASTE_EMISSION_FACTORS = {
        "low": 0.3,        # Well-recycled waste
        "medium": 0.8,     # Partially recycled
        "high": 1.5,       # Mostly landfill
    }

    FLIGHT_EMISSION_FACTOR = 0.255   # kg CO₂ per passenger-km (ICAO avg)
    PUBLIC_TRANSPORT_FACTOR = 0.100  # kg CO₂ per km (bus/metro avg)
    ELECTRICITY_FACTOR = 0.4         # kg CO₂ per kWh (grid average)

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="footprints")
    
    
    # Transportation
    car_travel_km = models.FloatField(default=0)
    fuel_type = models.CharField(max_length=20, choices=FUEL_CHOICES, default="petrol")
    flights_hours = models.FloatField(default=0)  # flight time in hours
    public_transport_km = models.FloatField(default=0)
    
    # Food consumption
    meals_per_day = models.IntegerField(default=3, help_text="Number of meals per day")
    meal_type = models.CharField(max_length=20, choices=MEAL_TYPE_CHOICES, default="medium")
    
    # Electricity usage
    electricity_kwh = models.FloatField(default=0, help_text="Monthly electricity consumption in kWh")
    
    # Waste management
    waste_kg = models.FloatField(default=0, help_text="Monthly waste generation in kg")
    waste_type = models.CharField(max_length=20, choices=WASTE_TYPE_CHOICES, default="medium")
    
    created_at = models.DateTimeField(auto_now_add=True)
    total_emission = models.FloatField(default=0, editable=False)  # auto-calculated (kg CO₂)
    
    def save(self, *args, **kwargs):
        # Calculate and set the total emission before saving
        self.total_emission = self.calculate_emission()
        super().save(*args, **kwargs)

    def calculate_emission(self):
        # Transportation emissions
        car_factor = self.FUEL_EMISSION_FACTORS.get(self.fuel_type, 0)
        car_emission = self.car_travel_km * car_factor

        flight_distance = self.flights_hours * 900
        flight_emission = flight_distance * self.FLIGHT_EMISSION_FACTOR

        public_emission = self.public_transport_km * self.PUBLIC_TRANSPORT_FACTOR

        # Food emissions
        food_factor = self.FOOD_EMISSION_FACTORS.get(self.meal_type, 0)
        food_emission = self.meals_per_day * food_factor * 30  # Monthly calculation

        # Electricity emissions
        electricity_emission = self.electricity_kwh * self.ELECTRICITY_FACTOR

        # Waste emissions
        waste_factor = self.WASTE_EMISSION_FACTORS.get(self.waste_type, 0)
        waste_emission = self.waste_kg * waste_factor

        total = car_emission + flight_emission + public_emission + food_emission + electricity_emission + waste_emission
        return round(total, 2)

    def get_emission_breakdown(self):
        """Return detailed breakdown of emissions by category"""
        car_factor = self.FUEL_EMISSION_FACTORS.get(self.fuel_type, 0)
        car_emission = self.car_travel_km * car_factor

        flight_distance = self.flights_hours * 900
        flight_emission = flight_distance * self.FLIGHT_EMISSION_FACTOR

        public_emission = self.public_transport_km * self.PUBLIC_TRANSPORT_FACTOR

        food_factor = self.FOOD_EMISSION_FACTORS.get(self.meal_type, 0)
        food_emission = self.meals_per_day * food_factor * 30

        electricity_emission = self.electricity_kwh * self.ELECTRICITY_FACTOR

        waste_factor = self.WASTE_EMISSION_FACTORS.get(self.waste_type, 0)
        waste_emission = self.waste_kg * waste_factor

        return {
            'transportation': round(car_emission + flight_emission + public_emission, 2),
            'food': round(food_emission, 2),
            'electricity': round(electricity_emission, 2),
            'waste': round(waste_emission, 2),
            'total': round(car_emission + flight_emission + public_emission + food_emission + electricity_emission + waste_emission, 2)
        }

    @classmethod
    def get_daily_calculation_count(cls, user, date=None):
        """Get the number of calculations a user has made today"""
        from django.utils import timezone
        if date is None:
            date = timezone.now().date()
        
        return cls.objects.filter(
            user=user,
            created_at__date=date
        ).count()
    
    @classmethod
    def can_calculate_today(cls, user, date=None):
        """Check if user can make another calculation today (limit: 3 per day)"""
        daily_count = cls.get_daily_calculation_count(user, date)
        return daily_count < 3
    
    @classmethod
    def get_remaining_calculations(cls, user, date=None):
        """Get remaining calculations for today"""
        daily_count = cls.get_daily_calculation_count(user, date)
        return max(0, 3 - daily_count)

    def __str__(self):
        return f"{self.user.username} - {self.created_at.date()} - {self.total_emission} kg CO₂"
