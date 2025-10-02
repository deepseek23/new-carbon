import os
import sys
import django

# Add the project directory to Python path
sys.path.append(r'd:\Django jemit\Carbon-footprint-tracker')

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'carbon.settings')
django.setup()

# Now run the commands
from django.core.management import execute_from_command_line

print("Creating migrations for challenges app...")
try:
    execute_from_command_line(['manage.py', 'makemigrations', 'challenges'])
    print("✓ Migrations created successfully")
except Exception as e:
    print(f"Error creating migrations: {e}")

print("\nRunning migrations...")
try:
    execute_from_command_line(['manage.py', 'migrate'])
    print("✓ Migrations applied successfully")
except Exception as e:
    print(f"Error running migrations: {e}")

print("\nCreating initial challenge data...")
try:
    execute_from_command_line(['manage.py', 'create_challenges'])
    print("✓ Initial challenges created successfully")
except Exception as e:
    print(f"Error creating challenges: {e}")

print("\nSetup complete! You can now:")
print("1. Run the server: python manage.py runserver")
print("2. Visit http://127.0.0.1:8000/challenges/ to see the challenges")
print("3. Login and join challenges")
print("4. Track progress on the dashboard")