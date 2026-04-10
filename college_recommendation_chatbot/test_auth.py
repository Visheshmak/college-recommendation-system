#!/usr/bin/env python3
"""
Test script for College Recommendation System v2.1
Tests the new user authentication and favorites features
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:5000"

def test_registration():
    """Test user registration"""
    print("🧪 Testing User Registration...")

    # Use a unique username to avoid conflicts
    import time
    unique_id = str(int(time.time()))
    user_data = {
        "username": f"testuser{unique_id}",
        "email": f"test{unique_id}@example.com",
        "name": "Test User",
        "password": "password123"
    }

    try:
        response = requests.post(f"{BASE_URL}/register", data=user_data, allow_redirects=False)
        print(f"Registration response status: {response.status_code}")
        if response.status_code in [200, 302]:
            print("✅ Registration successful")
            return user_data
        else:
            print(f"❌ Registration failed: {response.status_code}")
            print(f"Response content: {response.text[:500]}")
            return None
    except Exception as e:
        print(f"❌ Registration error: {e}")
        return None

def test_login(user_data):
    """Test user login"""
    print("🧪 Testing User Login...")

    login_data = {
        "username": user_data["username"],
        "password": user_data["password"]
    }

    try:
        session = requests.Session()
        response = session.post(f"{BASE_URL}/login", data=login_data, allow_redirects=False)
        print(f"Login response status: {response.status_code}")
        if response.status_code == 302:  # Redirect after successful login
            print("✅ Login successful")
            return session
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(f"Response content: {response.text[:500]}")
            return None
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None

def test_dashboard_access(session):
    """Test dashboard access for logged-in user"""
    print("🧪 Testing Dashboard Access...")

    try:
        response = session.get(f"{BASE_URL}/dashboard")
        if response.status_code == 200:
            print("✅ Dashboard access successful")
            return True
        else:
            print(f"❌ Dashboard access failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Dashboard access error: {e}")
        return False

def test_favorites_functionality(session):
    """Test adding and removing favorites"""
    print("🧪 Testing Favorites Functionality...")

    try:
        # Test adding favorite
        response = session.get(f"{BASE_URL}/add_favorite/VJTI", allow_redirects=False)
        if response.status_code == 302:
            print("✅ Add favorite successful")
        else:
            print(f"❌ Add favorite failed: {response.status_code}")
            return False

        # Test removing favorite
        response = session.get(f"{BASE_URL}/remove_favorite/VJTI", allow_redirects=False)
        if response.status_code == 302:
            print("✅ Remove favorite successful")
            return True
        else:
            print(f"❌ Remove favorite failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Favorites functionality error: {e}")
        return False

def test_compare_page_access(session):
    """Test compare page access"""
    print("🧪 Testing Compare Page Access...")

    try:
        response = session.get(f"{BASE_URL}/compare")
        if response.status_code == 200:
            print("✅ Compare page access successful")
            return True
        else:
            print(f"❌ Compare page access failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Compare page access error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting College Recommendation System Tests")
    print("=" * 50)

    # Test registration
    user_data = test_registration()
    if not user_data:
        print("❌ Tests failed at registration")
        return

    # Test login
    session = test_login(user_data)
    if not session:
        print("❌ Tests failed at login")
        return

    # Test dashboard access
    if not test_dashboard_access(session):
        print("❌ Tests failed at dashboard access")
        return

    # Test favorites functionality
    if not test_favorites_functionality(session):
        print("❌ Tests failed at favorites functionality")
        return

    # Test compare page access
    if not test_compare_page_access(session):
        print("❌ Tests failed at compare page access")
        return

    print("=" * 50)
    print("🎉 All tests passed! User authentication system is working correctly.")
    print("\n📋 Test Summary:")
    print("✅ User Registration")
    print("✅ User Login")
    print("✅ Dashboard Access")
    print("✅ Favorites System")
    print("✅ College Comparison")

if __name__ == "__main__":
    main()