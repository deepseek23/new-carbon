#!/usr/bin/env python
"""
Quick dashboard test to verify the CSS fixes and layout improvements.
"""

import os
import sys
import django

# Add the project root to Python path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'carbon.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User

def test_dashboard():
    """Test the dashboard page layout and styling."""
    client = Client()
    
    print("=== Dashboard Layout Test ===\n")
    
    # Create a test user
    try:
        user = User.objects.get(username='testuser')
    except User.DoesNotExist:
        user = User.objects.create_user(username='testuser', password='testpass123')
    
    # Login the user
    client.login(username='testuser', password='testpass123')
    
    # Test dashboard access
    response = client.get('/dashboard/')
    print(f"Dashboard Status Code: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ Dashboard loads successfully")
        
        # Check if the main sections are present in the response
        content = response.content.decode('utf-8')
        
        sections = [
            'dashboard-container',
            'period-selector', 
            'categories-section',
            'charts-section',
            'challenges-section',
            'insights-section',
            'action-section'
        ]
        
        print("\nChecking dashboard sections:")
        for section in sections:
            if section in content:
                print(f"✅ {section}")
            else:
                print(f"❌ {section} - missing")
                
        # Check for Tailwind classes
        tailwind_classes = [
            'grid',
            'bg-white',
            'rounded-xl',
            'shadow-sm',
            'text-gray-900',
            'px-6',
            'py-4'
        ]
        
        print("\nChecking Tailwind CSS classes:")
        missing_classes = []
        for css_class in tailwind_classes:
            if css_class in content:
                print(f"✅ {css_class}")
            else:
                missing_classes.append(css_class)
                
        if missing_classes:
            print(f"❌ Missing classes: {', '.join(missing_classes)}")
        else:
            print("✅ All essential Tailwind classes present")
            
    else:
        print(f"❌ Dashboard failed to load: HTTP {response.status_code}")
    
    print("\n=== Test Complete ===")

if __name__ == '__main__':
    test_dashboard()