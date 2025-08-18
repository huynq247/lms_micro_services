#!/usr/bin/env python3
"""
Test API Gateway - End-to-End Workflow Testing
"""

import asyncio
import aiohttp
import json

GATEWAY_URL = "http://localhost:8000"

async def test_api_gateway():
    """Test API Gateway with end-to-end workflows"""
    
    print("🌐 Testing API Gateway")
    print("=" * 50)
    
    async with aiohttp.ClientSession() as session:
        
        # Test 1: Gateway Health Check
        print("\n1. Testing Gateway Health...")
        try:
            async with session.get(f"{GATEWAY_URL}/health") as response:
                if response.status == 200:
                    health_data = await response.json()
                    print(f"✅ Gateway Health: {health_data}")
                else:
                    print(f"❌ Gateway Health Failed: {response.status}")
        except Exception as e:
            print(f"❌ Gateway Health Error: {e}")
        
        # Test 2: Gateway Info
        print("\n2. Testing Gateway Info...")
        try:
            async with session.get(f"{GATEWAY_URL}/") as response:
                if response.status == 200:
                    info_data = await response.json()
                    print(f"✅ Gateway Info: {info_data['service']} v{info_data['version']}")
                    print(f"   Routes: {list(info_data['routes'].keys())}")
                else:
                    print(f"❌ Gateway Info Failed: {response.status}")
        except Exception as e:
            print(f"❌ Gateway Info Error: {e}")
        
        # Test 3: Assignment Service through Gateway
        print("\n3. Testing Assignment Service through Gateway...")
        assignment_id = None
        
        # Create Assignment
        try:
            assignment_data = {
                "title": "Gateway Test Assignment",
                "description": "Testing assignment creation through API Gateway",
                "content_type": "course",
                "content_id": 123,
                "instructor_id": 2,
                "student_id": 1,
                "status": "pending",
                "priority": "medium",
                "difficulty_level": "intermediate",
                "estimated_duration_minutes": 60,
                "due_date": "2025-08-22T00:00:00Z"
            }
            
            async with session.post(
                f"{GATEWAY_URL}/api/assignments",
                json=assignment_data
            ) as response:
                if response.status == 201:
                    assignment = await response.json()
                    assignment_id = assignment['id']
                    print(f"✅ Assignment Created via Gateway: ID {assignment_id}")
                else:
                    error_text = await response.text()
                    print(f"❌ Assignment Creation Failed: {response.status} - {error_text}")
        except Exception as e:
            print(f"❌ Assignment Creation Error: {e}")
        
        # Get Assignment
        if assignment_id:
            try:
                async with session.get(f"{GATEWAY_URL}/api/assignments/{assignment_id}") as response:
                    if response.status == 200:
                        assignment = await response.json()
                        print(f"✅ Assignment Retrieved via Gateway: {assignment['title']}")
                    else:
                        print(f"❌ Assignment Retrieval Failed: {response.status}")
            except Exception as e:
                print(f"❌ Assignment Retrieval Error: {e}")
        
        # Test 4: Content Service through Gateway
        print("\n4. Testing Content Service through Gateway...")
        course_id = None
        
        # Create Course
        try:
            course_data = {
                "title": "Gateway Test Course",
                "description": "Testing course creation through API Gateway",
                "instructor_id": 1,
                "total_lessons": 5,
                "estimated_duration": 300
            }
            
            async with session.post(
                f"{GATEWAY_URL}/api/courses",
                json=course_data
            ) as response:
                if response.status == 201:
                    course = await response.json()
                    course_id = course['id']
                    print(f"✅ Course Created via Gateway: ID {course_id}")
                else:
                    error_text = await response.text()
                    print(f"❌ Course Creation Failed: {response.status} - {error_text}")
        except Exception as e:
            print(f"❌ Course Creation Error: {e}")
        
        # Get Courses
        try:
            async with session.get(f"{GATEWAY_URL}/api/courses") as response:
                if response.status == 200:
                    courses = await response.json()
                    course_count = len(courses) if isinstance(courses, list) else courses.get('total', 0)
                    print(f"✅ Courses Retrieved via Gateway: {course_count} courses found")
                else:
                    print(f"❌ Courses Retrieval Failed: {response.status}")
        except Exception as e:
            print(f"❌ Courses Retrieval Error: {e}")
        
        # Test 5: Cross-Service Workflow
        print("\n5. Testing Cross-Service Workflow...")
        if assignment_id and course_id:
            # Update Progress
            try:
                progress_data = {
                    "total_items": 10,
                    "completed_items": 3,
                    "completion_percentage": 30.0
                }
                
                async with session.put(
                    f"{GATEWAY_URL}/api/assignments/{assignment_id}/progress",
                    json=progress_data
                ) as response:
                    if response.status == 200:
                        progress = await response.json()
                        print(f"✅ Progress Updated via Gateway: {progress['completion_percentage']}%")
                    else:
                        error_text = await response.text()
                        print(f"❌ Progress Update Failed: {response.status} - {error_text}")
            except Exception as e:
                print(f"❌ Progress Update Error: {e}")
            
            # Start Study Session
            try:
                async with session.post(
                    f"{GATEWAY_URL}/api/sessions/assignments/{assignment_id}/start?student_id=1"
                ) as response:
                    if response.status == 201:
                        session_data = await response.json()
                        session_id = session_data['id']
                        print(f"✅ Study Session Started via Gateway: ID {session_id}")
                        
                        # End Session
                        end_data = {"items_studied": 5}
                        async with session.post(
                            f"{GATEWAY_URL}/api/sessions/{session_id}/end",
                            json=end_data
                        ) as end_response:
                            if end_response.status == 200:
                                end_result = await end_response.json()
                                print(f"✅ Study Session Ended via Gateway")
                            else:
                                print(f"❌ Session End Failed: {end_response.status}")
                    else:
                        error_text = await response.text()
                        print(f"❌ Session Start Failed: {response.status} - {error_text}")
            except Exception as e:
                print(f"❌ Session Error: {e}")
        
        # Test 6: Analytics through Gateway
        print("\n6. Testing Analytics through Gateway...")
        try:
            async with session.get(f"{GATEWAY_URL}/api/analytics/instructors/2/dashboard") as response:
                if response.status == 200:
                    analytics = await response.json()
                    print(f"✅ Analytics Retrieved via Gateway: {analytics.get('instructor_id')} dashboard")
                else:
                    error_text = await response.text()
                    print(f"❌ Analytics Failed: {response.status} - {error_text}")
        except Exception as e:
            print(f"❌ Analytics Error: {e}")
        
        # Cleanup
        print("\n7. Cleanup...")
        if assignment_id:
            try:
                async with session.delete(f"{GATEWAY_URL}/api/assignments/{assignment_id}") as response:
                    if response.status == 200:
                        print(f"✅ Assignment {assignment_id} deleted via Gateway")
                    else:
                        print(f"❌ Assignment deletion failed: {response.status}")
            except Exception as e:
                print(f"❌ Cleanup Error: {e}")
        
        print("\n" + "=" * 50)
        print("🎉 API Gateway End-to-End Test Completed!")

if __name__ == "__main__":
    print("🚀 Starting API Gateway End-to-End Test")
    print("Make sure the following services are running:")
    print("  - API Gateway: http://localhost:8000")
    print("  - Assignment Service: http://localhost:8004") 
    print("  - Content Service: http://localhost:8002")
    print()
    
    asyncio.run(test_api_gateway())
