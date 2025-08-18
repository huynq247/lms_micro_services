import asyncio
import aiohttp
import json
from datetime import datetime, timedelta

# Service URLs
AUTH_SERVICE = "http://localhost:8001"
CONTENT_SERVICE = "http://localhost:8002"
ASSIGNMENT_SERVICE = "http://localhost:8004"

class AssignmentServiceTester:
    def __init__(self):
        self.session = None
        self.test_data = {}
        self.instructor_id = None
        self.student_id = None
        
        # Use real users from test-accounts.txt
        self.instructor_data = {
            "username": "teacher1",
            "email": "teacher1@example.com",
            "password": "teacher123"
        }
        self.student_data = {
            "username": "student1", 
            "email": "student1@example.com",
            "password": "student123"
        }
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def authenticate_user(self, user_data):
        """Authenticate user and get token"""
        print(f"🔐 Authenticating user: {user_data['username']}")
        
        try:
            # Login to Auth Service
            login_data = {
                "username": user_data["username"],
                "password": user_data["password"]
            }
            
            async with self.session.post(
                f"{AUTH_SERVICE}/api/v1/auth/login",
                data=login_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    token = data.get("access_token")
                    if token:
                        print(f"✅ Authentication successful for {user_data['username']}")
                        return token
                    else:
                        print(f"❌ No token in response: {data}")
                        return None
                else:
                    text = await response.text()
                    print(f"❌ Authentication failed: {response.status} - {text}")
                    return None
                    
        except Exception as e:
            print(f"❌ Authentication error: {e}")
            return None
    
    async def get_user_info(self, token):
        """Get user info from token"""
        try:
            headers = {"Authorization": f"Bearer {token}"}
            async with self.session.get(
                f"{AUTH_SERVICE}/api/v1/users/me",
                headers=headers
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    print(f"❌ Failed to get user info: {response.status}")
                    return None
        except Exception as e:
            print(f"❌ Error getting user info: {e}")
            return None
    
    async def test_health_endpoints(self):
        """Test health endpoints for all services"""
        print("🔍 Testing Health Endpoints...")
        
        services = [
            ("Auth Service", f"{AUTH_SERVICE}/health"),
            ("Content Service", f"{CONTENT_SERVICE}/health"),
            ("Assignment Service", f"{ASSIGNMENT_SERVICE}/health")
        ]
        
        for name, url in services:
            try:
                async with self.session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        print(f"✅ {name}: {data.get('status', 'healthy')}")
                    else:
                        print(f"❌ {name}: HTTP {response.status}")
            except Exception as e:
                print(f"❌ {name}: Connection failed - {str(e)}")
    
    async def test_assignment_endpoints(self):
        """Test Assignment CRUD endpoints"""
        print("\n📝 Testing Assignment Endpoints...")
        
        # Use authenticated user IDs or fallback
        instructor_id = self.instructor_id or 2
        student_id = self.student_id or 1
        
        # Test 1: Create Assignment
        print("1. Testing CREATE assignment...")
        assignment_data = {
            "title": "Test Assignment - Math Course",
            "description": "Complete all lessons in the math course",
            "instructions": "Study each lesson carefully and complete exercises",
            "content_type": "course",
            "content_id": "674e123456789abcdef12345",  # Sample MongoDB ObjectId
            "content_title": "Mathematics Fundamentals",
            "due_date": (datetime.now() + timedelta(days=7)).isoformat(),
            "student_id": student_id,
            "instructor_id": instructor_id
        }
        
        try:
            async with self.session.post(
                f"{ASSIGNMENT_SERVICE}/api/assignments",
                json=assignment_data
            ) as response:
                if response.status == 201:
                    assignment = await response.json()
                    self.test_data['assignment_id'] = assignment['id']
                    print(f"✅ Assignment created: ID {assignment['id']}")
                else:
                    error_text = await response.text()
                    print(f"❌ Create assignment failed: {response.status} - {error_text}")
        except Exception as e:
            print(f"❌ Create assignment error: {str(e)}")
        
        # Test 2: Get Assignment by ID
        if 'assignment_id' in self.test_data:
            print("2. Testing GET assignment by ID...")
            try:
                async with self.session.get(
                    f"{ASSIGNMENT_SERVICE}/api/assignments/{self.test_data['assignment_id']}"
                ) as response:
                    if response.status == 200:
                        assignment = await response.json()
                        print(f"✅ Retrieved assignment: {assignment['title']}")
                    else:
                        print(f"❌ Get assignment failed: {response.status}")
            except Exception as e:
                print(f"❌ Get assignment error: {str(e)}")
        
        # Test 3: List assignments by instructor
        print("3. Testing LIST assignments by instructor...")
        try:
            async with self.session.get(
                f"{ASSIGNMENT_SERVICE}/api/assignments/instructors/{instructor_id}"
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Found {data.get('total', 0)} assignments for instructor")
                else:
                    print(f"❌ List instructor assignments failed: {response.status}")
        except Exception as e:
            print(f"❌ List instructor assignments error: {str(e)}")
        
        # Test 4: List assignments by student
        print("4. Testing LIST assignments by student...")
        try:
            async with self.session.get(
                f"{ASSIGNMENT_SERVICE}/api/assignments/students/{student_id}"
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Found {data.get('total', 0)} assignments for student")
                else:
                    print(f"❌ List student assignments failed: {response.status}")
        except Exception as e:
            print(f"❌ List student assignments error: {str(e)}")
    
    async def test_progress_endpoints(self):
        """Test Progress endpoints"""
        print("\n📊 Testing Progress Endpoints...")
        
        if 'assignment_id' not in self.test_data:
            print("❌ No assignment ID available for progress testing")
            return
        
        assignment_id = self.test_data['assignment_id']
        
        # Test 1: Update progress
        print("1. Testing UPDATE progress...")
        progress_data = {
            "total_items": 10,
            "completed_items": 3,
            "completion_percentage": 30.0,
            "items_studied": 3
        }
        
        try:
            async with self.session.put(
                f"{ASSIGNMENT_SERVICE}/api/progress/assignments/{assignment_id}",
                json=progress_data
            ) as response:
                if response.status == 200:
                    progress = await response.json()
                    print(f"✅ Progress updated: {progress['completion_percentage']}%")
                else:
                    error_text = await response.text()
                    print(f"❌ Update progress failed: {response.status} - {error_text}")
        except Exception as e:
            print(f"❌ Update progress error: {str(e)}")
        
        # Test 2: Get progress
        print("2. Testing GET progress...")
        try:
            async with self.session.get(
                f"{ASSIGNMENT_SERVICE}/api/progress/assignments/{assignment_id}"
            ) as response:
                if response.status == 200:
                    progress = await response.json()
                    print(f"✅ Retrieved progress: {progress['completion_percentage']}%")
                else:
                    print(f"❌ Get progress failed: {response.status}")
        except Exception as e:
            print(f"❌ Get progress error: {str(e)}")
    
    async def test_session_endpoints(self):
        """Test Study Session endpoints"""
        print("\n📚 Testing Study Session Endpoints...")
        
        if 'assignment_id' not in self.test_data:
            print("❌ No assignment ID available for session testing")
            return
        
        assignment_id = self.test_data['assignment_id']
        student_id = self.student_id or 1
        
        # Test 1: Start session
        print("1. Testing START session...")
        try:
            async with self.session.post(
                f"{ASSIGNMENT_SERVICE}/api/sessions/assignments/{assignment_id}/start",
                json={"student_id": student_id}
            ) as response:
                if response.status == 201:
                    session = await response.json()
                    self.test_data['session_id'] = session['id']
                    print(f"✅ Session started: ID {session['id']}")
                else:
                    error_text = await response.text()
                    print(f"❌ Start session failed: {response.status} - {error_text}")
        except Exception as e:
            print(f"❌ Start session error: {str(e)}")
        
        # Test 2: Update session progress
        if 'session_id' in self.test_data:
            print("2. Testing UPDATE session progress...")
            session_update = {
                "items_studied": 2,
                "items_completed": 1,
                "session_notes": "Making good progress"
            }
            
            try:
                async with self.session.put(
                    f"{ASSIGNMENT_SERVICE}/api/sessions/{self.test_data['session_id']}/progress",
                    json=session_update
                ) as response:
                    if response.status == 200:
                        session = await response.json()
                        print(f"✅ Session updated: {session['items_studied']} items studied")
                    else:
                        error_text = await response.text()
                        print(f"❌ Update session failed: {response.status} - {error_text}")
            except Exception as e:
                print(f"❌ Update session error: {str(e)}")
        
        # Test 3: End session
        if 'session_id' in self.test_data:
            print("3. Testing END session...")
            try:
                async with self.session.post(
                    f"{ASSIGNMENT_SERVICE}/api/sessions/{self.test_data['session_id']}/end",
                    json={"items_studied": 3}
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        print(f"✅ Session ended successfully")
                    else:
                        error_text = await response.text()
                        print(f"❌ End session failed: {response.status} - {error_text}")
            except Exception as e:
                print(f"❌ End session error: {str(e)}")
    
    async def test_analytics_endpoints(self):
        """Test Analytics endpoints"""
        print("\n📈 Testing Analytics Endpoints...")
        
        instructor_id = self.instructor_id or 2
        student_id = self.student_id or 1
        
        # Test 1: Instructor dashboard
        print("1. Testing INSTRUCTOR dashboard...")
        try:
            async with self.session.get(
                f"{ASSIGNMENT_SERVICE}/api/analytics/instructors/{instructor_id}/dashboard"
            ) as response:
                if response.status == 200:
                    dashboard = await response.json()
                    print(f"✅ Dashboard loaded: {dashboard.get('assignments', {}).get('total', 0)} assignments")
                else:
                    error_text = await response.text()
                    print(f"❌ Instructor dashboard failed: {response.status} - {error_text}")
        except Exception as e:
            print(f"❌ Instructor dashboard error: {str(e)}")
        
        # Test 2: Student summary
        print("2. Testing STUDENT summary...")
        try:
            async with self.session.get(
                f"{ASSIGNMENT_SERVICE}/api/analytics/students/{student_id}/summary"
            ) as response:
                if response.status == 200:
                    summary = await response.json()
                    print(f"✅ Student summary loaded: {summary.get('assignments', {}).get('total', 0)} assignments")
                else:
                    error_text = await response.text()
                    print(f"❌ Student summary failed: {response.status} - {error_text}")
        except Exception as e:
            print(f"❌ Student summary error: {str(e)}")
        
        # Test 3: Learning analytics
        print("3. Testing LEARNING analytics...")
        try:
            async with self.session.get(
                f"{ASSIGNMENT_SERVICE}/api/analytics/learning-data?days=30"
            ) as response:
                if response.status == 200:
                    analytics = await response.json()
                    print(f"✅ Learning analytics loaded for {analytics.get('period', 'unknown')} period")
                else:
                    error_text = await response.text()
                    print(f"❌ Learning analytics failed: {response.status} - {error_text}")
        except Exception as e:
            print(f"❌ Learning analytics error: {str(e)}")
    
    async def run_all_tests(self):
        """Run all API tests"""
        print("🚀 Starting Assignment Service API Tests...")
        print("=" * 60)
        
        # Step 1: Authenticate users and get their IDs
        print("🔐 Authenticating test users...")
        
        # Authenticate instructor
        instructor_token = await self.authenticate_user(self.instructor_data)
        if instructor_token:
            instructor_info = await self.get_user_info(instructor_token)
            if instructor_info:
                self.instructor_id = instructor_info.get('id')
                print(f"✅ Instructor ID: {self.instructor_id}")
        
        # Authenticate student  
        student_token = await self.authenticate_user(self.student_data)
        if student_token:
            student_info = await self.get_user_info(student_token)
            if student_info:
                self.student_id = student_info.get('id')
                print(f"✅ Student ID: {self.student_id}")
        
        if not self.instructor_id or not self.student_id:
            print("❌ Failed to get user IDs. Using fallback IDs...")
            self.instructor_id = 2  # Fallback to test user IDs
            self.student_id = 1
        
        # Step 2: Run tests
        await self.test_health_endpoints()
        await self.test_assignment_endpoints()
        await self.test_progress_endpoints()
        await self.test_session_endpoints()
        await self.test_analytics_endpoints()
        
        print("\n" + "=" * 60)
        print("🏁 Assignment Service API Tests Completed!")
        
        # Cleanup - Delete test assignment
        if 'assignment_id' in self.test_data:
            print(f"\n🧹 Cleaning up test assignment {self.test_data['assignment_id']}...")
            try:
                async with self.session.delete(
                    f"{ASSIGNMENT_SERVICE}/api/assignments/{self.test_data['assignment_id']}"
                ) as response:
                    if response.status == 200:
                        print("✅ Test assignment deleted")
                    else:
                        print(f"⚠️ Could not delete test assignment: {response.status}")
            except Exception as e:
                print(f"⚠️ Cleanup error: {str(e)}")

async def main():
    """Main test runner"""
    async with AssignmentServiceTester() as tester:
        await tester.run_all_tests()

if __name__ == "__main__":
    print("🧪 Assignment Service API Test Suite")
    print("Make sure all 3 services are running:")
    print("  - Auth Service: http://localhost:8001")
    print("  - Content Service: http://localhost:8002") 
    print("  - Assignment Service: http://localhost:8004")
    print()
    asyncio.run(main())
