import asyncio
import aiohttp
import json
from datetime import datetime, timedelta

# Service URLs
ASSIGNMENT_SERVICE = "http://localhost:8004"

async def test_assignment_service():
    """Simple test for Assignment Service only"""
    print("🧪 Assignment Service Basic Test")
    print("=" * 50)
    
    async with aiohttp.ClientSession() as session:
        # Test 1: Health check
        print("1. Testing health endpoint...")
        try:
            async with session.get(f"{ASSIGNMENT_SERVICE}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Health check: {data['status']}")
                else:
                    print(f"❌ Health check failed: {response.status}")
        except Exception as e:
            print(f"❌ Health check error: {e}")
            return
        
        # Test 2: Create assignment
        print("\n2. Testing create assignment...")
        assignment_data = {
            "title": "Test Assignment",
            "description": "A test assignment",
            "content_type": "course",
            "content_id": "507f1f77bcf86cd799439011",
            "content_title": "Test Course",
            "due_date": (datetime.now() + timedelta(days=7)).isoformat(),
            "student_id": 1,
            "instructor_id": 2
        }
        
        assignment_id = None
        try:
            async with session.post(
                f"{ASSIGNMENT_SERVICE}/api/assignments",
                json=assignment_data
            ) as response:
                if response.status == 201:
                    assignment = await response.json()
                    assignment_id = assignment['id']
                    print(f"✅ Assignment created: ID {assignment_id}")
                    print(f"   Title: {assignment['title']}")
                    print(f"   Status: {assignment['status']}")
                else:
                    error_text = await response.text()
                    print(f"❌ Create failed: {response.status} - {error_text}")
                    return
        except Exception as e:
            print(f"❌ Create error: {e}")
            return
        
        # Test 3: Get assignment
        if assignment_id:
            print(f"\n3. Testing get assignment {assignment_id}...")
            try:
                async with session.get(
                    f"{ASSIGNMENT_SERVICE}/api/assignments/{assignment_id}"
                ) as response:
                    if response.status == 200:
                        assignment = await response.json()
                        print(f"✅ Retrieved assignment: {assignment['title']}")
                    else:
                        print(f"❌ Get failed: {response.status}")
            except Exception as e:
                print(f"❌ Get error: {e}")
        
        # Test 4: Update progress
        if assignment_id:
            print(f"\n4. Testing update progress for assignment {assignment_id}...")
            progress_data = {
                "total_items": 10,
                "completed_items": 3,
                "completion_percentage": 30.0
            }
            
            try:
                async with session.put(
                    f"{ASSIGNMENT_SERVICE}/api/progress/assignments/{assignment_id}",
                    json=progress_data
                ) as response:
                    if response.status == 200:
                        progress = await response.json()
                        print(f"✅ Progress updated: {progress['completion_percentage']}%")
                    else:
                        error_text = await response.text()
                        print(f"❌ Progress update failed: {response.status} - {error_text}")
            except Exception as e:
                print(f"❌ Progress update error: {e}")
        
        # Test 5: Start study session
        if assignment_id:
            print(f"\n5. Testing start study session for assignment {assignment_id}...")
            try:
                async with session.post(
                    f"{ASSIGNMENT_SERVICE}/api/sessions/assignments/{assignment_id}/start?student_id=1"
                ) as response:
                    if response.status == 201:
                        session_data = await response.json()
                        session_id = session_data['id']
                        print(f"✅ Session started: ID {session_id}")
                        
                        # End the session
                        print(f"   Ending session {session_id}...")
                        async with session.post(
                            f"{ASSIGNMENT_SERVICE}/api/sessions/{session_id}/end",
                            json={"items_studied": 2}
                        ) as end_response:
                            if end_response.status == 200:
                                print(f"✅ Session ended successfully")
                            else:
                                print(f"❌ End session failed: {end_response.status}")
                    else:
                        error_text = await response.text()
                        print(f"❌ Start session failed: {response.status} - {error_text}")
            except Exception as e:
                print(f"❌ Session error: {e}")
        
        # Test 6: List assignments
        print(f"\n6. Testing list assignments by instructor...")
        try:
            async with session.get(
                f"{ASSIGNMENT_SERVICE}/api/assignments/instructors/2"
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    count = len(data) if isinstance(data, list) else data.get('total', 0)
                    print(f"✅ Found {count} assignments for instructor")
                else:
                    error_text = await response.text()
                    print(f"❌ List failed: {response.status} - {error_text}")
        except Exception as e:
            print(f"❌ List error: {e}")
        
        # Test 7: Delete assignment (cleanup)
        if assignment_id:
            print(f"\n7. Testing delete assignment {assignment_id}...")
            try:
                async with session.delete(
                    f"{ASSIGNMENT_SERVICE}/api/assignments/{assignment_id}"
                ) as response:
                    if response.status == 200:
                        print(f"✅ Assignment deleted successfully")
                    else:
                        print(f"❌ Delete failed: {response.status}")
            except Exception as e:
                print(f"❌ Delete error: {e}")
        
        print("\n" + "=" * 50)
        print("🏁 Assignment Service Test Completed!")

if __name__ == "__main__":
    print("Make sure Assignment Service is running on http://localhost:8004")
    print()
    asyncio.run(test_assignment_service())
