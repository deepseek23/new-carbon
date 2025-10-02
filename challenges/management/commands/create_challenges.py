from django.core.management.base import BaseCommand
from challenges.models import ChallengeType

class Command(BaseCommand):
    help = 'Create initial challenge data'

    def handle(self, *args, **options):
        challenges_data = [
            {
                'title': 'Meatless Mondays',
                'description': 'Skip meat for one day a week. Reducing meat consumption is one of the most effective ways to lower your carbon footprint from food.',
                'category': 'food',
                'duration_type': 'weekly',
                'duration_days': 7,
                'carbon_impact': 2.5,
                'difficulty_level': 1,
                'icon_color': 'green'
            },
            {
                'title': 'Commute Smart',
                'description': 'Ditch the car! For 30 days, try to walk, bike, or use public transport for your daily commute at least twice a week.',
                'category': 'transport',
                'duration_type': 'monthly',
                'duration_days': 30,
                'carbon_impact': 15.0,
                'difficulty_level': 2,
                'icon_color': 'blue'
            },
            {
                'title': 'Plastic Free Week',
                'description': 'Aim to avoid single-use plastics for an entire week. This includes bags, bottles, straws, and food packaging. Every piece matters!',
                'category': 'waste',
                'duration_type': 'weekly',
                'duration_days': 7,
                'carbon_impact': 1.8,
                'difficulty_level': 2,
                'icon_color': 'yellow'
            },
            {
                'title': 'Home Energy Saver',
                'description': 'Reduce your home electricity usage by 10% this month. Unplug devices, switch to LEDs, and be mindful of your energy consumption.',
                'category': 'energy',
                'duration_type': 'monthly',
                'duration_days': 30,
                'carbon_impact': 8.5,
                'difficulty_level': 2,
                'icon_color': 'purple'
            },
            {
                'title': 'Waste Not Challenge',
                'description': 'For two weeks, actively work to reduce your household food waste. Plan meals, use leftovers creatively, and compost scraps.',
                'category': 'waste',
                'duration_type': 'weekly',
                'duration_days': 14,
                'carbon_impact': 3.2,
                'difficulty_level': 1,
                'icon_color': 'red'
            },
            {
                'title': 'Go Local',
                'description': 'Commit to buying locally grown produce whenever possible. This reduces "food miles" and supports your local community farmers.',
                'category': 'shopping',
                'duration_type': 'ongoing',
                'duration_days': 0,
                'carbon_impact': 5.0,
                'difficulty_level': 1,
                'icon_color': 'indigo'
            },
            {
                'title': 'Zero Waste Day',
                'description': 'Challenge yourself to produce zero waste for an entire day. Plan ahead and be creative with reusing items.',
                'category': 'waste',
                'duration_type': 'daily',
                'duration_days': 1,
                'carbon_impact': 0.8,
                'difficulty_level': 3,
                'icon_color': 'gray'
            },
            {
                'title': 'Digital Detox Hour',
                'description': 'Reduce screen time and electronic device usage for one hour daily. This saves energy and improves well-being.',
                'category': 'energy',
                'duration_type': 'daily',
                'duration_days': 30,
                'carbon_impact': 1.2,
                'difficulty_level': 1,
                'icon_color': 'teal'
            }
        ]

        created_count = 0
        for challenge_data in challenges_data:
            challenge, created = ChallengeType.objects.get_or_create(
                title=challenge_data['title'],
                defaults=challenge_data
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created challenge: {challenge.title}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Challenge already exists: {challenge.title}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'\nSuccessfully created {created_count} new challenges!')
        )