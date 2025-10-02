from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import CarbonFootprint
import random


class Command(BaseCommand):
    help = 'Create test data for leaderboard'

    def handle(self, *args, **options):
        # Check existing data
        user_count = User.objects.count()
        footprint_count = CarbonFootprint.objects.count()
        
        self.stdout.write(f"Current users: {user_count}")
        self.stdout.write(f"Current footprints: {footprint_count}")
        
        # Create test users if they don't exist
        test_users = ['alice', 'bob', 'charlie', 'diana', 'eve']
        
        for username in test_users:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': f'{username}@example.com',
                    'first_name': username.capitalize(),
                }
            )
            if created:
                user.set_password('testpass123')
                user.save()
                self.stdout.write(f"Created user: {username}")
            
            # Create random footprint entries for each user
            for i in range(random.randint(1, 5)):
                footprint = CarbonFootprint.objects.create(
                    user=user,
                    car_travel_km=random.uniform(10, 100),
                    fuel_type=random.choice(['petrol', 'diesel', 'electric', 'hybrid']),
                    flights_hours=random.uniform(0, 10),
                    public_transport_km=random.uniform(5, 50),
                    meals_per_day=random.randint(2, 4),
                    meal_type=random.choice(['light', 'medium', 'heavy', 'meat_heavy']),
                    electricity_kwh=random.uniform(200, 800),
                    waste_kg=random.uniform(10, 50),
                    waste_type=random.choice(['low', 'medium', 'high'])
                )
                self.stdout.write(f"Created footprint for {username}: {footprint.total_emission:.2f} kg CO₂")
        
        # Show leaderboard data
        self.stdout.write("\n=== LEADERBOARD DATA ===")
        users_with_data = User.objects.filter(footprints__isnull=False).distinct()
        
        for user in users_with_data:
            total_emission = sum(fp.total_emission for fp in user.footprints.all())
            entry_count = user.footprints.count()
            self.stdout.write(f"{user.username}: {total_emission:.2f} kg CO₂ ({entry_count} entries)")