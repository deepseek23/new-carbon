from django import forms 
from .models import CarbonFootprint
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

        

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField()
    class Meta:
        model = User
        fields = ('username', 'email','password1', 'password2')