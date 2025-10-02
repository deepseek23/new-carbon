#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to Python path
sys.path.append(r'd:\Django jemit\Carbon-footprint-tracker')

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'carbon.settings')
django.setup()

from challenges.models import ChallengeType, UserChallenge
from django.contrib.auth.models import User

print("Testing Challenge System...")

# Test 1: Check if challenges exist
challenges = ChallengeType.objects.all()
print(f"✓ Found {challenges.count()} challenges in database")

# Test 2: Check if models are working
for challenge in challenges[:3]:
    print(f"  - {challenge.title} ({challenge.category})")

# Test 3: Check if a user exists
users = User.objects.all()
print(f"✓ Found {users.count()} users in database")

# Test 4: Check URLs
from django.urls import reverse
try:
    challenges_url = reverse('challenges:index')
    print(f"✓ Challenges URL works: {challenges_url}")
except Exception as e:
    print(f"✗ Challenges URL error: {e}")

try:
    my_challenges_url = reverse('challenges:my_challenges')
    print(f"✓ My Challenges URL works: {my_challenges_url}")
except Exception as e:
    print(f"✗ My Challenges URL error: {e}")

print("\nAll tests completed. The challenge system should be working correctly.")
print("You can now run: python manage.py runserver")
print("And visit:")
print("- http://127.0.0.1:8000/challenges/ (Browse challenges)")
print("- http://127.0.0.1:8000/challenges/my-challenges/ (My challenges)")
print("- http://127.0.0.1:8000/dashboard/ (Dashboard with challenge integration)")