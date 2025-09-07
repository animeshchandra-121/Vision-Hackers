#!/usr/bin/env python3
"""
Test script for the AI Talent Management System
"""

import requests
import time
import sys

def test_application():
    """Test the application endpoints"""
    base_url = "http://localhost:5000"
    
    print("Testing AI Talent Management System...")
    print("=" * 50)
    
    # Test main page
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            print("✓ Main page accessible")
        else:
            print(f"✗ Main page failed: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"✗ Main page error: {e}")
        return False
    
    # Test dashboard
    try:
        response = requests.get(f"{base_url}/dashboard", timeout=5)
        if response.status_code == 200:
            print("✓ Dashboard accessible")
        else:
            print(f"✗ Dashboard failed: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"✗ Dashboard error: {e}")
    
    # Test prototype page
    try:
        response = requests.get(f"{base_url}/prototype", timeout=5)
        if response.status_code == 200:
            print("✓ Prototype page accessible")
        else:
            print(f"✗ Prototype page failed: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"✗ Prototype page error: {e}")
    
    # Test API endpoints
    try:
        response = requests.get(f"{base_url}/api/data", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ API data endpoint working - Employees: {data.get('employees_count', 0)}, Projects: {data.get('projects_count', 0)}")
        else:
            print(f"✗ API data endpoint failed: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"✗ API data endpoint error: {e}")
    
    print("=" * 50)
    print("Test completed!")
    return True

if __name__ == "__main__":
    print("Make sure the application is running with: python app.py")
    print("Then run this test script...")
    
    # Wait a moment for the server to start
    time.sleep(2)
    
    success = test_application()
    sys.exit(0 if success else 1)
