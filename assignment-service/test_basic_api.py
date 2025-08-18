#!/usr/bin/env python3
"""
Test script for Assignment Service API endpoints
"""

import requests
import json
from datetime import datetime, timedelta

# Assignment Service configuration
BASE_URL = "http://localhost:8004"

def test_health():
    """Test health endpoint"""
    print("🔍 Testing Health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_root():
    """Test root endpoint"""
    print("\n🔍 Testing Root endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Run basic tests"""
    print("🚀 Starting Assignment Service Basic Tests")
    print("=" * 50)
    
    # Test health
    if not test_health():
        print("❌ Health check failed. Make sure Assignment Service is running on port 8004")
        return
    
    # Test root
    test_root()
    
    print("\n" + "=" * 50)
    print("✅ Basic Assignment Service tests completed!")
    print("Service is ready for API implementation")

if __name__ == "__main__":
    main()
