#!/usr/bin/env python
"""
Quick script to check leaderboard data and create test data if needed.
Run this with: python check_leaderboard.py
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

def check_leaderboard_data():
    print("=== LEADERBOARD DATA CHECK ===")
    
    # Check users
    total_users = User.objects.count()
    print(f"Total users: {total_users}")
    
    # Check footprints
    total_footprints = CarbonFootprint.objects.count()
    print(f"Total footprints: {total_footprints}")
    
    # Check users with footprints
    users_with_footprints = User.objects.filter(footprints__isnull=False).distinct()
    print(f"Users with footprints: {users_with_footprints.count()}")
    
    if users_with_footprints.exists():
        print("\n=== USER BREAKDOWN ===")
        for user in users_with_footprints:
            total_emission = sum(fp.total_emission or 0 for fp in user.footprints.all())
            entry_count = user.footprints.count()
            print(f"{user.username}: {total_emission:.2f} kg CO₂ ({entry_count} entries)")
    else:
        print("\nNo users with footprint data found!")
        print("To create test data, run: python manage.py create_test_data")

if __name__ == "__main__":
    check_leaderboard_data()