#!/usr/bin/env python
"""
Test script to verify carbon footprint data saving functionality.
Run this with: python test_data_saving.py
"""

import os
import sys
import django

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'carbon.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import CarbonFootprint

def test_data_saving():
    print("=== TESTING DATA SAVING ===")
    
    # Get or create a test user
    test_user, created = User.objects.get_or_create(
        username='testuser',
        defaults={
            'email': 'test@example.com',
            'first_name': 'Test'
        }
    )
    if created:
        test_user.set_password('testpass123')
        test_user.save()
        print(f"Created test user: {test_user.username}")
    else:
        print(f"Using existing test user: {test_user.username}")
    
    # Count existing footprints
    initial_count = CarbonFootprint.objects.filter(user=test_user).count()
    print(f"Initial footprints for test user: {initial_count}")
    
    # Create a test footprint entry
    test_footprint = CarbonFootprint.objects.create(
        user=test_user,
        car_travel_km=50.5,
        fuel_type='petrol',
        flights_hours=2.0,
        public_transport_km=20.0,
        meals_per_day=3,
        meal_type='medium',
        electricity_kwh=300.0,
        waste_kg=25.0,
        waste_type='medium'
    )
    
    print(f"Created test footprint with ID: {test_footprint.id}")
    print(f"Total emission calculated: {test_footprint.total_emission} kg CO₂")
    
    # Count footprints after creation
    final_count = CarbonFootprint.objects.filter(user=test_user).count()
    print(f"Final footprints for test user: {final_count}")
    
    if final_count > initial_count:
        print("✅ SUCCESS: Data is being saved correctly!")
    else:
        print("❌ FAILURE: Data is not being saved!")
    
    # Show all footprints for the test user
    print("\n=== ALL FOOTPRINTS FOR TEST USER ===")
    for fp in CarbonFootprint.objects.filter(user=test_user).order_by('-created_at'):
        print(f"ID: {fp.id}, Created: {fp.created_at}, Emission: {fp.total_emission} kg CO₂")

if __name__ == "__main__":
    test_data_saving()