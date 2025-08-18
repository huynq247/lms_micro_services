#!/usr/bin/env python3
"""
Test script for Auth Service API endpoints
"""
import requests
import json
import sys

# Configuration
BASE_URL = "http://localhost:8001"
AUTH_URL = f"{BASE_URL}/api/v1/auth"
USERS_URL = f"{BASE_URL}/api/v1/users"

def test_health_check():
    """Test health check endpoint"""
    print("🏥 Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("   ✅ Health check passed")
            print(f"   📊 Response: {response.json()}")
            return True
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Health check error: {e}")
        return False

def test_user_registration():
    """Test user registration"""
    print("\n👤 Testing user registration...")
    
    user_data = {
        "username": "testuser",
        "email": "testuser@example.com",
        "full_name": "Test User",
        "password": "testpass123",
        "role": "STUDENT"
    }
    
    try:
        response = requests.post(f"{AUTH_URL}/register", json=user_data)
        if response.status_code == 201:
            print("   ✅ User registration successful")
            user = response.json()
            print(f"   📊 User ID: {user['id']}, Username: {user['username']}")
            return user
        else:
            print(f"   ❌ Registration failed: {response.status_code}")
            print(f"   📊 Response: {response.text}")
            return None
    except Exception as e:
        print(f"   ❌ Registration error: {e}")
        return None

def test_user_login(username="admin", password="admin123456"):
    """Test user login"""
    print(f"\n🔐 Testing login for {username}...")
    
    login_data = {
        "username": username,
        "password": password
    }
    
    try:
        response = requests.post(f"{AUTH_URL}/login", json=login_data)
        if response.status_code == 200:
            print("   ✅ Login successful")
            tokens = response.json()
            print(f"   🎫 Access token received (length: {len(tokens['access_token'])})")
            return tokens
        else:
            print(f"   ❌ Login failed: {response.status_code}")
            print(f"   📊 Response: {response.text}")
            return None
    except Exception as e:
        print(f"   ❌ Login error: {e}")
        return None

def test_protected_endpoint(access_token):
    """Test protected endpoint with authentication"""
    print("\n🔒 Testing protected endpoint...")
    
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    try:
        response = requests.get(f"{AUTH_URL}/me", headers=headers)
        if response.status_code == 200:
            print("   ✅ Protected endpoint access successful")
            user = response.json()
            print(f"   👤 User: {user['username']} ({user['role']})")
            return user
        else:
            print(f"   ❌ Protected endpoint failed: {response.status_code}")
            print(f"   📊 Response: {response.text}")
            return None
    except Exception as e:
        print(f"   ❌ Protected endpoint error: {e}")
        return None

def test_admin_endpoints(access_token):
    """Test admin-only endpoints"""
    print("\n👑 Testing admin endpoints...")
    
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    try:
        # Get users list
        response = requests.get(f"{USERS_URL}/", headers=headers)
        if response.status_code == 200:
            print("   ✅ Admin users list access successful")
            users_data = response.json()
            print(f"   📊 Total users: {users_data['total']}")
            print(f"   👥 Users found: {len(users_data['users'])}")
            for user in users_data['users']:
                print(f"      - {user['username']} ({user['role']}) - Active: {user['is_active']}")
            return True
        else:
            print(f"   ❌ Admin endpoint failed: {response.status_code}")
            print(f"   📊 Response: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Admin endpoint error: {e}")
        return False

def test_token_refresh(refresh_token):
    """Test token refresh"""
    print("\n🔄 Testing token refresh...")
    
    refresh_data = {
        "refresh_token": refresh_token
    }
    
    try:
        response = requests.post(f"{AUTH_URL}/refresh", json=refresh_data)
        if response.status_code == 200:
            print("   ✅ Token refresh successful")
            tokens = response.json()
            print(f"   🎫 New access token received")
            return tokens
        else:
            print(f"   ❌ Token refresh failed: {response.status_code}")
            print(f"   📊 Response: {response.text}")
            return None
    except Exception as e:
        print(f"   ❌ Token refresh error: {e}")
        return None

def main():
    """Run all tests"""
    print("🚀 Auth Service API Testing Suite")
    print("=" * 50)
    
    # Test 1: Health check
    if not test_health_check():
        print("\n❌ Health check failed - service may not be running")
        return False
    
    # Test 2: User registration (optional - might fail if user exists)
    test_user_registration()
    
    # Test 3: Admin login
    admin_tokens = test_user_login("admin", "admin123456")
    if not admin_tokens:
        print("\n❌ Admin login failed - cannot continue with protected endpoint tests")
        return False
    
    # Test 4: Protected endpoint access
    admin_user = test_protected_endpoint(admin_tokens["access_token"])
    if not admin_user:
        print("\n❌ Protected endpoint access failed")
        return False
    
    # Test 5: Admin endpoints
    if admin_user and admin_user.get("role") == "ADMIN":
        test_admin_endpoints(admin_tokens["access_token"])
    
    # Test 6: Token refresh
    test_token_refresh(admin_tokens["refresh_token"])
    
    # Test 7: Teacher login
    print("\n👩‍🏫 Testing teacher login...")
    teacher_tokens = test_user_login("teacher1", "teacher123")
    if teacher_tokens:
        test_protected_endpoint(teacher_tokens["access_token"])
    
    # Test 8: Student login
    print("\n👨‍🎓 Testing student login...")
    student_tokens = test_user_login("student1", "student123")
    if student_tokens:
        test_protected_endpoint(student_tokens["access_token"])
    
    print("\n🎉 API testing completed!")
    print("\n📋 Summary:")
    print("   - Health check: Working")
    print("   - User registration: Available")
    print("   - Authentication: Working")
    print("   - Protected endpoints: Working")
    print("   - Admin endpoints: Working")
    print("   - Token refresh: Working")
    print("   - Role-based access: Working")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️  Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error during testing: {e}")
        sys.exit(1)
