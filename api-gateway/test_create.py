#!/usr/bin/env python3
"""
Test create assignment functionality
"""
import requests
import json

def test_create_assignment():
    url = "http://localhost:8000/api/assignments/"
    
    data = {
        "title": "Test Assignment from Gateway",
        "description": "Testing creation via API Gateway",
        "content_type": "course",
        "content_id": "689ec117d3c5b0476fe4d1a2",
        "content_title": "Python Programming Fundamentals",
        "instructor_id": 1,
        "student_id": 5
    }
    
    print("🧪 Testing Create Assignment via Gateway...")
    print(f"URL: {url}")
    print(f"Data: {json.dumps(data, indent=2)}")
    
    try:
        response = requests.post(url, json=data)
        print(f"\n📊 Response Status: {response.status_code}")
        print(f"📝 Response Headers: {dict(response.headers)}")
        
        if response.text:
            try:
                result = response.json()
                print(f"📄 Response Body: {json.dumps(result, indent=2)}")
            except:
                print(f"📄 Response Text: {response.text}")
        
        if response.status_code == 201:
            print("✅ SUCCESS: Assignment created with correct status code")
        elif response.status_code == 200:
            print("⚠️  WARNING: Assignment created but returned 200 instead of 201")
        else:
            print(f"❌ ERROR: Unexpected status code {response.status_code}")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")

def test_direct_create():
    url = "http://localhost:8004/api/assignments/"
    
    data = {
        "title": "Test Assignment Direct",
        "description": "Testing creation directly",
        "content_type": "course",
        "content_id": "689ec117d3c5b0476fe4d1a2",
        "content_title": "Python Programming Fundamentals",
        "instructor_id": 1,
        "student_id": 6
    }
    
    print("\n🧪 Testing Create Assignment Directly...")
    print(f"URL: {url}")
    
    try:
        response = requests.post(url, json=data)
        print(f"\n📊 Response Status: {response.status_code}")
        
        if response.text:
            try:
                result = response.json()
                print(f"📄 Response Body: {json.dumps(result, indent=2)}")
            except:
                print(f"📄 Response Text: {response.text}")
        
        if response.status_code == 201:
            print("✅ SUCCESS: Direct assignment created with correct status code")
        elif response.status_code == 200:
            print("⚠️  WARNING: Direct assignment created but returned 200 instead of 201")
        else:
            print(f"❌ ERROR: Unexpected status code {response.status_code}")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    test_create_assignment()
    test_direct_create()
