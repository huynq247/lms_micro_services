"""
Week 7 - End-to-End Workflow Testing Script
Testing all services through API Gateway
"""

import httpx
import asyncio
import json
from datetime import datetime

# Configuration
GATEWAY_URL = "http://localhost:8000"
AUTH_URL = "http://localhost:8001"
CONTENT_URL = "http://localhost:8002"
ASSIGNMENT_URL = "http://localhost:8004"

# Test Results
test_results = []

def log_test(test_name, success, details=""):
    """Log test results"""
    result = {
        "test": test_name,
        "success": success,
        "details": details,
        "timestamp": datetime.now().isoformat()
    }
    test_results.append(result)
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} {test_name}: {details}")

async def test_health_checks():
    """Test all service health endpoints"""
    print("\n🔍 === HEALTH CHECK TESTS ===")
    
    services = [
        ("API Gateway", f"{GATEWAY_URL}/health"),
        ("Auth Service", f"{AUTH_URL}/health"),
        ("Content Service", f"{CONTENT_URL}/api/v1/courses/status"),
        ("Assignment Service", f"{ASSIGNMENT_URL}/api/assignments/status")
    ]
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        for service_name, url in services:
            try:
                response = await client.get(url)
                success = response.status_code == 200
                details = f"{response.status_code} - {response.text[:100]}"
                log_test(f"{service_name} Health", success, details)
            except Exception as e:
                log_test(f"{service_name} Health", False, str(e))

async def test_gateway_routing():
    """Test API Gateway routing to all services"""
    print("\n🌐 === GATEWAY ROUTING TESTS ===")
    
    routes = [
        ("Assignment Service Routing", f"{GATEWAY_URL}/api/assignments/status"),
        ("Content Service Routing", f"{GATEWAY_URL}/api/courses/status"),
    ]
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        for route_name, url in routes:
            try:
                response = await client.get(url)
                success = response.status_code == 200
                details = f"{response.status_code} - Routing working"
                log_test(route_name, success, details)
            except Exception as e:
                log_test(route_name, False, str(e))

async def test_assignment_workflow():
    """Test Assignment Service core workflow"""
    print("\n📚 === ASSIGNMENT WORKFLOW TESTS ===")
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        
        # Test 1: Get all assignments through gateway
        try:
            response = await client.get(f"{GATEWAY_URL}/api/assignments/")
            success = response.status_code == 200
            data = response.json() if success else {}
            details = f"Status: {response.status_code}, Count: {len(data.get('assignments', []))}"
            log_test("Get Assignments via Gateway", success, details)
        except Exception as e:
            log_test("Get Assignments via Gateway", False, str(e))
            
        # Test 2: Get progress for assignment 1 (if exists)
        try:
            response = await client.get(f"{GATEWAY_URL}/api/progress/assignments/1")
            success = response.status_code in [200, 404]  # 404 is acceptable if no data
            details = f"Status: {response.status_code}, Progress endpoint accessible"
            log_test("Get Progress via Gateway", success, details)
        except Exception as e:
            log_test("Get Progress via Gateway", False, str(e))
            
        # Test 3: Get analytics
        try:
            response = await client.get(f"{GATEWAY_URL}/api/analytics/summary")
            success = response.status_code in [200, 404]  # 404 is acceptable if no data
            details = f"Status: {response.status_code}, Analytics endpoint accessible"
            log_test("Get Analytics via Gateway", success, details)
        except Exception as e:
            log_test("Get Analytics via Gateway", False, str(e))

async def test_content_workflow():
    """Test Content Service core workflow"""
    print("\n📖 === CONTENT WORKFLOW TESTS ===")
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        
        # Test 1: Get all courses through gateway
        try:
            response = await client.get(f"{GATEWAY_URL}/api/courses/")
            success = response.status_code == 200
            data = response.json() if success else {}
            details = f"Status: {response.status_code}, Courses: {len(data.get('courses', []))}"
            log_test("Get Courses via Gateway", success, details)
        except Exception as e:
            log_test("Get Courses via Gateway", False, str(e))
            
        # Test 2: Get decks
        try:
            response = await client.get(f"{GATEWAY_URL}/api/decks/")
            success = response.status_code == 200
            data = response.json() if success else {}
            details = f"Status: {response.status_code}, Decks: {len(data.get('decks', []))}"
            log_test("Get Decks via Gateway", success, details)
        except Exception as e:
            log_test("Get Decks via Gateway", False, str(e))

async def test_performance():
    """Test response times - Relaxed targets for development"""
    print("\n⚡ === PERFORMANCE TESTS ===")
    
    endpoints = [
        ("Gateway Health", f"{GATEWAY_URL}/health"),
        ("Assignment Status", f"{GATEWAY_URL}/api/assignments/status"),
        ("Content Status", f"{GATEWAY_URL}/api/courses/status"),
    ]
    
    async with httpx.AsyncClient(timeout=15.0) as client:
        for endpoint_name, url in endpoints:
            try:
                start_time = datetime.now()
                response = await client.get(url)
                end_time = datetime.now()
                
                response_time = (end_time - start_time).total_seconds() * 1000  # ms
                success = response.status_code == 200 and response_time < 5000  # Relaxed to 5 seconds for dev
                details = f"{response.status_code} - {response_time:.0f}ms"
                log_test(f"{endpoint_name} Performance", success, details)
            except Exception as e:
                log_test(f"{endpoint_name} Performance", False, str(e))

async def run_all_tests():
    """Run all end-to-end tests"""
    print("🧪 Starting Week 7 End-to-End Testing...")
    print("=" * 60)
    
    # Run all test suites
    await test_health_checks()
    await test_gateway_routing()
    await test_assignment_workflow()
    await test_content_workflow()
    await test_performance()
    
    # Summary
    print("\n📊 === TEST SUMMARY ===")
    total_tests = len(test_results)
    passed_tests = sum(1 for result in test_results if result["success"])
    failed_tests = total_tests - passed_tests
    
    print(f"Total Tests: {total_tests}")
    print(f"✅ Passed: {passed_tests}")
    print(f"❌ Failed: {failed_tests}")
    print(f"📈 Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    # Show failed tests
    if failed_tests > 0:
        print("\n🚨 Failed Tests:")
        for result in test_results:
            if not result["success"]:
                print(f"  - {result['test']}: {result['details']}")
    
    # Save results to file
    with open("test_results.json", "w") as f:
        json.dump(test_results, f, indent=2)
    
    print(f"\n📄 Detailed results saved to: test_results.json")
    
    # Checklist update
    success_rate = (passed_tests/total_tests)*100
    if success_rate >= 90:
        print("\n🎉 EXCELLENT! System ready for frontend integration!")
    elif success_rate >= 75:
        print("\n✅ GOOD! Minor issues to fix before frontend.")
    else:
        print("\n⚠️ NEEDS WORK! Critical issues must be resolved.")

if __name__ == "__main__":
    asyncio.run(run_all_tests())
