#!/usr/bin/env python
"""
Test script to verify the responsive navigation layout.
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

def test_responsive_navigation():
    """Test the responsive navigation system."""
    client = Client()
    
    print("=== Responsive Navigation Test ===\n")
    
    # Test layout template rendering
    try:
        response = client.get('/')
        print(f"Homepage Status Code: {response.status_code}")
        
        if response.status_code == 200:
            content = response.content.decode('utf-8')
            
            # Check for responsive navigation elements
            navigation_elements = [
                'mobile-menu-btn',         # Mobile hamburger button
                'mobile-sidebar',          # Mobile sidebar
                'sidebar-overlay',         # Sidebar overlay
                'close-sidebar',           # Close sidebar button
                'hamburger-line',          # Hamburger menu lines
                'lg:flex',                 # Desktop navigation classes
                'lg:hidden',               # Mobile-only classes
                'hidden lg:flex',          # Desktop-only navigation
            ]
            
            print("Checking responsive navigation elements:")
            for element in navigation_elements:
                if element in content:
                    print(f"✅ {element}")
                else:
                    print(f"❌ {element} - missing")
            
            # Check for JavaScript functionality
            js_functions = [
                'openSidebar',
                'closeSidebarMenu',
                'mobile-menu-btn',
                'addEventListener',
            ]
            
            print("\nChecking JavaScript functionality:")
            for js_func in js_functions:
                if js_func in content:
                    print(f"✅ {js_func}")
                else:
                    print(f"❌ {js_func} - missing")
            
            # Check for mobile-responsive classes
            responsive_classes = [
                'sm:text-2xl',             # Small screen responsive text
                'lg:flex',                 # Large screen flex
                'hidden lg:flex',          # Hidden on mobile, flex on desktop
                'lg:hidden',               # Hidden on desktop
                'w-80',                    # Fixed sidebar width
                'fixed top-0',             # Fixed positioning
            ]
            
            print("\nChecking responsive CSS classes:")
            missing_classes = []
            for css_class in responsive_classes:
                if css_class in content:
                    print(f"✅ {css_class}")
                else:
                    missing_classes.append(css_class)
            
            if missing_classes:
                print(f"❌ Missing responsive classes: {', '.join(missing_classes)}")
            else:
                print("✅ All responsive classes present")
                
            # Check for proper SVG icons
            if 'svg' in content and 'viewBox' in content:
                print("✅ SVG icons present")
            else:
                print("❌ SVG icons missing")
                
            print(f"\n📊 Total content length: {len(content)} characters")
            
        else:
            print(f"❌ Homepage failed to load: HTTP {response.status_code}")
    
    except Exception as e:
        print(f"❌ Error testing navigation: {str(e)}")
    
    print("\n=== Test Complete ===")
    print("\n📱 Mobile Navigation Features:")
    print("   • Hamburger menu button (top-right on mobile)")
    print("   • Slide-out sidebar with user info")
    print("   • Navigation links with icons")
    print("   • Overlay background when sidebar is open")
    print("   • Auto-close on link click or outside tap")
    print("\n💻 Desktop Navigation Features:")
    print("   • Full horizontal navbar")
    print("   • Logo with full text")
    print("   • Direct navigation links")
    print("   • User authentication buttons")

if __name__ == '__main__':
    test_responsive_navigation()