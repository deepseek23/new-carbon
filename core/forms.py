from django import forms 
from .models import CarbonFootprint
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

        

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField()
    class Meta:
        model = User
        fields = ('username', 'email','password1', 'password2')


class CarbonFootprintForm(forms.ModelForm):
    class Meta:
        model = CarbonFootprint
        fields = [
            "car_travel_km", "fuel_type", "flights_hours", "public_transport_km",
            "meals_per_day", "meal_type", "electricity_kwh", "waste_kg", "waste_type"
        ]
        widgets = {
            'car_travel_km': forms.NumberInput(attrs={'step': '0.1', 'min': '0'}),
            'flights_hours': forms.NumberInput(attrs={'step': '0.1', 'min': '0'}),
            'public_transport_km': forms.NumberInput(attrs={'step': '0.1', 'min': '0'}),
            'meals_per_day': forms.NumberInput(attrs={'min': '1', 'max': '10'}),
            'electricity_kwh': forms.NumberInput(attrs={'step': '0.1', 'min': '0'}),
            'waste_kg': forms.NumberInput(attrs={'step': '0.1', 'min': '0'}),
        }

        