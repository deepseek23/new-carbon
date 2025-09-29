import os
import json
from datetime import datetime, timedelta

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.utils import timezone

from .forms import UserRegistrationForm, CarbonFootprintForm
from .models import CarbonFootprint

# Optional Google Gemini client (may be None)
try:
    import google.generativeai as genai  # type: ignore
except Exception:
    genai = None


def index(request):
    return render(request, 'landing.html')


def login_view(request):
    """Simple login view — posts username/password and logs the user in."""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'Successfully logged in!')
            # redirect to dashboard (or tracking page) after login
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'registration/login.html')


def register(request):
    """User registration. On success logs in and redirects to track page."""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            # Some registration forms include email — set if present
            user.email = form.cleaned_data.get('email', '') or ''
            user.save()
            login(request, user)
            messages.success(request, 'Registration successful! Welcome to Carbon Tracker.')
            return redirect('track')
        else:
            # Show form errors via messages so user sees them on the page
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})


@login_required
def track(request):
    """
    View to create a new CarbonFootprint entry. Uses CarbonFootprintForm.
    Named 'track' because your template links to {% url 'track' %}.
    """
    if request.method == 'POST':
        form = CarbonFootprintForm(request.POST)
        if form.is_valid():
            footprint = form.save(commit=False)
            footprint.user = request.user
            # If your model needs a computed total_emission, either compute here
            # or ensure model.save() handles it.
            footprint.save()
            messages.success(request, 'Carbon footprint entry saved.')
            return redirect('dashboard')
        else:
            # expose form errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = CarbonFootprintForm()
    return render(request, 'track.html', {'form': form})

@login_required
def dashboard(request):
    # Get time period from request (default to 'monthly')
    time_period = request.GET.get('period', 'monthly')
    
    # Initialize default values
    latest = None
    breakdown = {
        'total': 0,
        'transportation': 0,
        'electricity': 0,
        'food': 0,
        'waste': 0
    }
    avg_daily = 0
    
    # Get all footprints for the user
    all_footprints = CarbonFootprint.objects.filter(user=request.user).order_by("-created_at")
    
    # Filter footprints based on time period
    now = timezone.now()
    if time_period == 'daily':
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        footprints = all_footprints.filter(created_at__gte=start_date)
        period_label = "Today"
    elif time_period == 'weekly':
        start_date = now - timedelta(days=7)
        footprints = all_footprints.filter(created_at__gte=start_date)
        period_label = "This Week"
    elif time_period == 'monthly':
        start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        footprints = all_footprints.filter(created_at__gte=start_date)
        period_label = "This Month"
    else:
        footprints = all_footprints
        period_label = "All Time"
    
    # Calculate aggregated data for the selected period
    if footprints.exists():
        # Calculate total emissions for the period
        total_emissions = sum(footprint.total_emission for footprint in footprints if footprint.total_emission is not None)
        
        # Calculate breakdown for the period
        breakdown = {
            'total': total_emissions,
            'transportation': sum(footprint.get_emission_breakdown().get('transportation', 0) for footprint in footprints if hasattr(footprint, 'get_emission_breakdown')),
            'electricity': sum(footprint.get_emission_breakdown().get('electricity', 0) for footprint in footprints if hasattr(footprint, 'get_emission_breakdown')),
            'food': sum(footprint.get_emission_breakdown().get('food', 0) for footprint in footprints if hasattr(footprint, 'get_emission_breakdown')),
            'waste': sum(footprint.get_emission_breakdown().get('waste', 0) for footprint in footprints if hasattr(footprint, 'get_emission_breakdown')),
        }
        
        # Get the latest footprint for display
        latest = footprints.first()
        
        # Calculate average daily emissions for the period
        if time_period == 'daily':
            avg_daily = total_emissions
        elif time_period == 'weekly':
            avg_daily = total_emissions / 7
        elif time_period == 'monthly':
            avg_daily = total_emissions / 30
        else:
            avg_daily = total_emissions / max(len(footprints), 1) if footprints else 0
    
    # Prepare chart data
    chart_footprints = footprints[:10]  # Limit to last 10 entries for chart
    
    context = {
        "latest": latest,
        "breakdown": breakdown,
        "footprints": chart_footprints,
        "all_footprints": all_footprints,
        "time_period": time_period,
        "period_label": period_label,
        "avg_daily": avg_daily,
        "total_entries": footprints.count(),
    }
    return render(request, "dashboard.html", context)

@login_required
def tips_api(request):
    """Return a single, concise tips message based on the user's calculation data.
    This endpoint intentionally avoids AI calls and generates a heuristic message.
    """
    if request.method != 'POST':
        return JsonResponse({"error": "Method not allowed"}, status=405)

    try:
        data = json.loads(request.body or '{}')
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    result = data.get('result')
    breakdown = data.get('emission_breakdown') or {}

    def as_float(x, default=0.0):
        try:
            return float(x)
        except (TypeError, ValueError):
            return default

    total = as_float(breakdown.get('total', result))
    transportation = as_float(breakdown.get('transportation'))
    food = as_float(breakdown.get('food'))
    electricity = as_float(breakdown.get('electricity'))
    waste = as_float(breakdown.get('waste'))
    result_val = as_float(result, total)

    categories = {
        'Transportation': transportation,
        'Food': food,
        'Electricity': electricity,
        'Waste': waste,
    }
    top_cat = max(categories.items(), key=lambda kv: kv[1] if kv[1] is not None else -1)
    top_name, top_value = top_cat
    total_for_pct = total if total > 0 else (transportation + food + electricity + waste)
    pct = (top_value / total_for_pct * 100) if total_for_pct else 0

    if result_val < 100:
        level = "excellent"
        tone = "Great job keeping your footprint low."
    elif result_val < 150:
        level = "good"
        tone = "You're doing well—small improvements will add up."
    elif result_val < 200:
        level = "moderate"
        tone = "A few focused changes can make a big difference."
    else:
        level = "high"
        tone = "Consider making some immediate, impactful changes."

    suggestions = {
        'Transportation': "combine trips, carpool when possible, or swap short drives for walking/cycling",
        'Food': "shift a few meals per week toward plant-based options and cut food waste",
        'Electricity': "set appliances to energy-saving modes and switch to LED/efficient lighting",
        'Waste': "separate recyclables/organics and reduce single-use packaging",
    }
    nudge = suggestions.get(top_name, "make a few small changes across your routine")

    annual = result_val * 12
    trees = result_val / 22 if result_val else 0

    message = (
        f"Your monthly footprint is {result_val:.0f} kg CO₂ (≈ {annual:.0f} kg/year). "
        f"Biggest source: {top_name} at {top_value:.0f} kg (~{pct:.0f}%). {tone} "
        f"This week, try to {nudge}."
    )

    return JsonResponse({
        "message": message,
        "result": round(result_val, 2),
        "emission_breakdown": {
            "transportation": round(transportation, 2),
            "food": round(food, 2),
            "electricity": round(electricity, 2),
            "waste": round(waste, 2),
            "total": round(total, 2),
        },
        "level": level,
        "trees_to_offset": round(trees, 1),
    })


@login_required
def ai_tips_api(request):
    """Accept raw form values, compute emissions, and return a concise Gemini AI tip."""
    if request.method != 'POST':
        return JsonResponse({"error": "Method not allowed"}, status=405)

    try:
        data = json.loads(request.body or '{}')
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    def f(name, default=0.0):
        try:
            return float(data.get(name, default))
        except (TypeError, ValueError):
            return default

    def s(name, default=""):
        v = data.get(name, default)
        return (v or default)

    car_travel_km = f('car_travel_km')
    fuel_type = s('fuel_type', 'petrol')
    flights_hours = f('flights_hours')
    public_transport_km = f('public_transport_km')
    meals_per_day = int(f('meals_per_day', 3)) if data.get('meals_per_day') is not None else 3
    meal_type = s('meal_type', 'medium')
    electricity_kwh = f('electricity_kwh')
    waste_kg = f('waste_kg')
    waste_type = s('waste_type', 'medium')

    car_factor = CarbonFootprint.FUEL_EMISSION_FACTORS.get(fuel_type, 0)
    food_factor = CarbonFootprint.FOOD_EMISSION_FACTORS.get(meal_type, 0)
    waste_factor = CarbonFootprint.WASTE_EMISSION_FACTORS.get(waste_type, 0)
    flight_distance = flights_hours * 900

    car_emission = car_travel_km * car_factor
    flight_emission = flight_distance * CarbonFootprint.FLIGHT_EMISSION_FACTOR
    public_emission = public_transport_km * CarbonFootprint.PUBLIC_TRANSPORT_FACTOR
    food_emission = meals_per_day * food_factor * 30
    electricity_emission = electricity_kwh * CarbonFootprint.ELECTRICITY_FACTOR
    waste_emission = waste_kg * waste_factor

    transportation = round(car_emission + flight_emission + public_emission, 2)
    food = round(food_emission, 2)
    electricity = round(electricity_emission, 2)
    waste = round(waste_emission, 2)
    total = round(transportation + food + electricity + waste, 2)

    if total < 100:
        level = "excellent"
    elif total < 150:
        level = "good"
    elif total < 200:
        level = "moderate"
    else:
        level = "high"

    tip_message = None
    if genai and getattr(settings, 'GEMINI_API_KEY', None):
        try:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            model = genai.GenerativeModel('gemini-2.0-flash-lite')
            prompt = (
                "You are a sustainability coach. Based on the user's monthly carbon footprint, "
                "give exactly ONE short, actionable tip in 1 sentence (<= 25 words). "
                "Avoid lists, no JSON, no code blocks. Be encouraging and specific.\n\n"
                f"Totals (kg CO2/month): total={total}, transportation={transportation}, food={food}, electricity={electricity}, waste={waste}.\n"
                f"Fuel type={fuel_type}, meal type={meal_type}, waste type={waste_type}.\n"
                "Start directly with the tip."
            )
            resp = model.generate_content(prompt)
            tip_message = (resp.text or '').strip()
        except Exception:
            tip_message = None

    if not tip_message:
        cat_pairs = [
            ("Transportation", transportation),
            ("Food", food),
            ("Electricity", electricity),
            ("Waste", waste),
        ]
        top_name, _ = max(cat_pairs, key=lambda kv: kv[1])
        defaults = {
            "Transportation": "Combine trips or use public transit for short distances this week to cut transport emissions.",
            "Food": "Swap a few meals for plant-based options and avoid food waste to reduce your food emissions.",
            "Electricity": "Switch to LED bulbs and turn off idle appliances to lower electricity emissions.",
            "Waste": "Sort recyclables and avoid single-use packaging to reduce waste emissions.",
        }
        tip_message = defaults.get(top_name)

    return JsonResponse({
        "message": tip_message,
        "result": total,
        "emission_breakdown": {
            "transportation": transportation,
            "food": food,
            "electricity": electricity,
            "waste": waste,
            "total": total,
        },
        "level": level,
    })
