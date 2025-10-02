#!/usr/bin/env python
"""
Quick test to verify the enhanced leaderboard functionality.
This script will test the leaderboard with different time periods.
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
from core.models import CarbonFootprint
from datetime import datetime, timedelta
import json

def test_leaderboard():
    """Test the leaderboard functionality with different time periods."""
    client = Client()
    
    print("=== Enhanced Leaderboard Test ===\n")
    
    # Test different time period URLs
    periods = ['daily', 'weekly', 'monthly', 'all']
    
    for period in periods:
        print(f"Testing {period.upper()} leaderboard...")
        
        try:
            response = client.get(f'/leaderboard/?period={period}')
            print(f"  Status Code: {response.status_code}")
            
            if response.status_code == 200:
                # Check if context variables are present
                context = response.context
                if context:
                    print(f"  Time Period: {context.get('time_period', 'N/A')}")
                    print(f"  Period Label: {context.get('period_label', 'N/A')}")
                    print(f"  Ranked Users: {len(context.get('ranked', []))}")
                    print(f"  Total Users: {context.get('total_users', 'N/A')}")
                    print(f"  Total Emissions: {context.get('total_emissions', 'N/A')}")
                    print(f"  Average Emission: {context.get('avg_emission', 'N/A')}")
                else:
                    print("  No context data available")
            else:
                print(f"  Error: HTTP {response.status_code}")
            
        except Exception as e:
            print(f"  Error: {str(e)}")
        
        print()
    
    # Test default leaderboard (no period parameter)
    print("Testing DEFAULT leaderboard...")
    try:
        response = client.get('/leaderboard/')
        print(f"  Status Code: {response.status_code}")
        
        if response.status_code == 200:
            context = response.context
            if context:
                print(f"  Default Period: {context.get('time_period', 'N/A')}")
                print(f"  Period Label: {context.get('period_label', 'N/A')}")
        
    except Exception as e:
        print(f"  Error: {str(e)}")
    
    print("\n=== Test Complete ===")

if __name__ == '__main__':
    test_leaderboard()