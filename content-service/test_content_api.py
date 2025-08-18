#!/usr/bin/env python3
"""
Test script for Content Service API endpoints
"""

import requests
import json
from datetime import datetime

# Content Service configuration
BASE_URL = "http://localhost:8002"

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

def test_create_course():
    """Test create course endpoint"""
    print("\n🔍 Testing Create Course endpoint...")
    course_data = {
        "title": "Python Programming Fundamentals",
        "description": "Learn the basics of Python programming language",
        "instructor_id": 1,
        "instructor_name": "John Teacher",
        "estimated_duration": 120,
        "is_published": True
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/v1/courses/", json=course_data)
        print(f"Status: {response.status_code}")
        if response.status_code == 201:
            course = response.json()
            print(f"✅ Course created: {course['title']}")
            print(f"Course ID: {course['id']}")
            return course
        else:
            print(f"❌ Error: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_get_courses():
    """Test get courses endpoint"""
    print("\n🔍 Testing Get Courses endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/courses/")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Found {len(data['items'])} courses")
            print(f"Total: {data['total']}")
            return data['items']
        else:
            print(f"❌ Error: {response.text}")
            return []
    except Exception as e:
        print(f"❌ Error: {e}")
        return []

def test_create_lesson(course_id):
    """Test create lesson endpoint"""
    print("\n🔍 Testing Create Lesson endpoint...")
    lesson_data = {
        "title": "Introduction to Variables",
        "content": "Learn about variables in Python programming",
        "course_id": course_id,
        "order": 1,
        "image_url": "https://example.com/lesson1.jpg",
        "video_url": "https://youtube.com/watch?v=abc123",
        "duration": 15
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/v1/courses/{course_id}/lessons", json=lesson_data)
        print(f"Status: {response.status_code}")
        if response.status_code == 201:
            lesson = response.json()
            print(f"✅ Lesson created: {lesson['title']}")
            print(f"Lesson ID: {lesson['id']}")
            return lesson
        else:
            print(f"❌ Error: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_create_deck():
    """Test create deck endpoint"""
    print("\n🔍 Testing Create Deck endpoint...")
    deck_data = {
        "title": "Python Vocabulary",
        "description": "Essential Python programming terms",
        "instructor_id": 1,
        "instructor_name": "John Teacher",
        "category": "Programming",
        "tags": ["python", "vocabulary", "basics"],
        "is_published": True
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/v1/decks/", json=deck_data)
        print(f"Status: {response.status_code}")
        if response.status_code == 201:
            deck = response.json()
            print(f"✅ Deck created: {deck['title']}")
            print(f"Deck ID: {deck['id']}")
            return deck
        else:
            print(f"❌ Error: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_create_flashcard(deck_id):
    """Test create flashcard endpoint"""
    print("\n🔍 Testing Create Flashcard endpoint...")
    flashcard_data = {
        "front": "What is a variable in Python?",
        "back": "A variable is a name that refers to a value stored in memory",
        "deck_id": deck_id,
        "order": 1,
        "front_image_url": "https://example.com/variable-front.jpg",
        "difficulty": "easy"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/v1/decks/{deck_id}/flashcards", json=flashcard_data)
        print(f"Status: {response.status_code}")
        if response.status_code == 201:
            flashcard = response.json()
            print(f"✅ Flashcard created: {flashcard['front'][:50]}...")
            print(f"Flashcard ID: {flashcard['id']}")
            return flashcard
        else:
            print(f"❌ Error: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_get_decks():
    """Test get decks endpoint"""
    print("\n🔍 Testing Get Decks endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/decks/")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Found {len(data['items'])} decks")
            return data['items']
        else:
            print(f"❌ Error: {response.text}")
            return []
    except Exception as e:
        print(f"❌ Error: {e}")
        return []

def main():
    """Run all tests"""
    print("🚀 Starting Content Service API Tests")
    print("=" * 50)
    
    # Test health
    if not test_health():
        print("❌ Health check failed. Make sure Content Service is running on port 8002")
        return
    
    # Test course creation
    course = test_create_course()
    if not course:
        print("❌ Course creation failed")
        return
    
    # Test get courses
    courses = test_get_courses()
    
    # Test lesson creation
    lesson = test_create_lesson(course['id'])
    
    # Test deck creation
    deck = test_create_deck()
    if not deck:
        print("❌ Deck creation failed")
        return
    
    # Test flashcard creation
    flashcard = test_create_flashcard(deck['id'])
    
    # Test get decks
    decks = test_get_decks()
    
    print("\n" + "=" * 50)
    print("🎉 Content Service API Tests Completed!")
    print(f"✅ Created: {len(courses)} courses, {len(decks)} decks")
    if lesson:
        print(f"✅ Created lesson: {lesson['title']}")
    if flashcard:
        print(f"✅ Created flashcard in deck: {deck['title']}")

if __name__ == "__main__":
    main()
