from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from .forms import UserRegistrationForm, CarbonFootprintForm

def index(request):
    return render(request, 'index.html')

def register(request):
    if request.method == 'POST':
         form = UserRegistrationForm(request.POST)
         if form.is_valid():
             user = form.save(commit=False)
             user.email = form.cleaned_data.get('email', '')
             user.save()
             login(request, user)
             return redirect('home')
    else:
        form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def home_page(request):
    return render(request, 'home.html')

@login_required
def home(request):
    result = None
    emission_breakdown = None
    tips = None
    
    if request.method == "POST":
        form = CarbonFootprintForm(request.POST)
        if form.is_valid():
            footprint = form.save(commit=False)
            footprint.user = request.user
            footprint.save()
            result = footprint.total_emission
            emission_breakdown = footprint.get_emission_breakdown()
            
            # Generate predefined tips based on user's data
            tips = generate_predefined_tips(emission_breakdown, footprint)
    else:
        form = CarbonFootprintForm()

    return render(request, "home.html", {
        "form": form,
        "result": result,
        "emission_breakdown": emission_breakdown,
        "tips": tips,
    })

def generate_predefined_tips(emission_breakdown, footprint):
    """Generate predefined tips based on user's carbon footprint data"""
    tips = []
    
    # Transportation tips
    if emission_breakdown['transportation'] > 50:
        tips.append({
            "tip": "Consider carpooling or using public transport for your daily commute",
            "savings": "15-25 kg CO₂/month",
            "category": "Transportation",
            "icon": "🚗"
        })
    
    if footprint.car_travel_km > 100:
        tips.append({
            "tip": "Switch to a fuel-efficient vehicle or consider electric/hybrid options",
            "savings": "20-40 kg CO₂/month",
            "category": "Transportation",
            "icon": "⚡"
        })
    
    if footprint.flights_hours > 2:
        tips.append({
            "tip": "Reduce unnecessary flights and choose direct routes when possible",
            "savings": "30-60 kg CO₂/month",
            "category": "Transportation",
            "icon": "✈️"
        })
    
    # Food tips
    if footprint.meal_type in ['heavy', 'meat_heavy']:
        tips.append({
            "tip": "Try incorporating more plant-based meals into your diet",
            "savings": "20-40 kg CO₂/month",
            "category": "Food",
            "icon": "🥗"
        })
    
    if footprint.meals_per_day > 3:
        tips.append({
            "tip": "Consider reducing portion sizes and avoiding food waste",
            "savings": "10-20 kg CO₂/month",
            "category": "Food",
            "icon": "🍽️"
        })
    
    # Electricity tips
    if emission_breakdown['electricity'] > 30:
        tips.append({
            "tip": "Switch to LED bulbs and unplug devices when not in use",
            "savings": "5-15 kg CO₂/month",
            "category": "Energy",
            "icon": "💡"
        })
    
    if footprint.electricity_kwh > 200:
        tips.append({
            "tip": "Use energy-efficient appliances and smart thermostats",
            "savings": "10-25 kg CO₂/month",
            "category": "Energy",
            "icon": "🏠"
        })
    
    # Waste tips
    if footprint.waste_type == 'high':
        tips.append({
            "tip": "Start composting organic waste and recycle more",
            "savings": "8-12 kg CO₂/month",
            "category": "Waste",
            "icon": "♻️"
        })
    
    if footprint.waste_kg > 20:
        tips.append({
            "tip": "Reduce packaging waste by buying in bulk and using reusable containers",
            "savings": "5-10 kg CO₂/month",
            "category": "Waste",
            "icon": "📦"
        })
    
    # General tips based on total emissions
    if emission_breakdown['total'] > 150:
        tips.append({
            "tip": "Plant trees or support reforestation projects to offset emissions",
            "savings": "10-20 kg CO₂/month",
            "category": "Offset",
            "icon": "🌳"
        })
    
    if emission_breakdown['total'] > 200:
        tips.append({
            "tip": "Consider investing in renewable energy sources like solar panels",
            "savings": "25-50 kg CO₂/month",
            "category": "Energy",
            "icon": "☀️"
        })
    
    # Always include these general tips
    general_tips = [
        {
            "tip": "Walk or cycle for short distances instead of driving",
            "savings": "5-15 kg CO₂/month",
            "category": "Transportation",
            "icon": "🚶"
        },
        {
            "tip": "Use public transportation or carpool whenever possible",
            "savings": "10-30 kg CO₂/month",
            "category": "Transportation",
            "icon": "🚌"
        },
        {
            "tip": "Buy local and seasonal food to reduce transportation emissions",
            "savings": "5-15 kg CO₂/month",
            "category": "Food",
            "icon": "🌱"
        },
        {
            "tip": "Reduce water heating temperature and take shorter showers",
            "savings": "3-8 kg CO₂/month",
            "category": "Energy",
            "icon": "🚿"
        },
        {
            "tip": "Use reusable bags, bottles, and containers",
            "savings": "2-5 kg CO₂/month",
            "category": "Waste",
            "icon": "👜"
        }
    ]
    
    # Add general tips if we don't have enough specific tips
    while len(tips) < 5 and general_tips:
        tip = general_tips.pop(0)
        if tip not in tips:  # Avoid duplicates
            tips.append(tip)
    
    # Generate assessment
    total_emissions = emission_breakdown['total']
    if total_emissions < 100:
        assessment = "🌟 Excellent! Your carbon footprint is quite low. Keep up the great work!"
        level = "low"
    elif total_emissions < 150:
        assessment = "👍 Good effort! You're doing well, but there's room for improvement."
        level = "moderate"
    elif total_emissions < 200:
        assessment = "⚠️ Your carbon footprint is above average. Consider implementing some of the tips below."
        level = "high"
    else:
        assessment = "🚨 Your carbon footprint is significantly high. Immediate action is recommended."
        level = "very_high"
    
    return {
        "assessment": assessment,
        "level": level,
        "tips": tips[:5],  # Limit to top 5 tips
        "motivation": "Every small change makes a difference! You're taking an important step towards a more sustainable future."
    }