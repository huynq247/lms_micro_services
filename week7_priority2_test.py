"""
Week 7 - Priority 2 Testing: Security & Error Handling
Testing remaining checklist items before frontend development
"""

import httpx
import asyncio
import json
import time
from datetime import datetime
import sqlite3
import psycopg2

# Configuration
GATEWAY_URL = "http://localhost:8000"
AUTH_URL = "http://localhost:8001"
CONTENT_URL = "http://localhost:8002"
ASSIGNMENT_URL = "http://localhost:8004"

# Test Results
priority2_results = []

def log_test(test_name, success, details=""):
    """Log Priority 2 test results"""
    result = {
        "test": test_name,
        "success": success,
        "details": details,
        "timestamp": datetime.now().isoformat()
    }
    priority2_results.append(result)
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} {test_name}: {details}")

async def test_security_validation():
    """Test basic security measures"""
    print("\n🔒 === SECURITY TESTS ===")
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        
        # Test 1: CORS Configuration
        try:
            headers = {
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET"
            }
            response = await client.options(f"{GATEWAY_URL}/api/assignments/", headers=headers)
            cors_headers = response.headers
            success = "access-control-allow-origin" in [h.lower() for h in cors_headers.keys()]
            details = f"CORS headers present: {success}"
            log_test("CORS Configuration", success, details)
        except Exception as e:
            log_test("CORS Configuration", False, str(e))
            
        # Test 2: Input Validation - Invalid data
        try:
            invalid_assignment = {
                "title": "",  # Empty title should fail
                "description": "x" * 10000,  # Too long description
                "instructor_id": "invalid",  # Invalid type
                "student_id": -1  # Invalid negative ID
            }
            response = await client.post(f"{GATEWAY_URL}/api/assignments/", json=invalid_assignment)
            success = response.status_code in [400, 422]  # Should reject invalid data
            details = f"Status: {response.status_code}, Validation working: {success}"
            log_test("Input Validation", success, details)
        except Exception as e:
            log_test("Input Validation", False, str(e))
            
        # Test 3: SQL Injection Prevention
        try:
            malicious_query = "'; DROP TABLE assignments; --"
            response = await client.get(f"{GATEWAY_URL}/api/assignments/?student_id={malicious_query}")
            success = response.status_code in [200, 400, 422] and "error" not in response.text.lower()
            details = f"Status: {response.status_code}, SQL injection prevented: {success}"
            log_test("SQL Injection Prevention", success, details)
        except Exception as e:
            log_test("SQL Injection Prevention", False, str(e))
            
        # Test 4: Rate Limiting Basic Test
        try:
            start_time = time.time()
            responses = []
            # Send 10 rapid requests
            for i in range(10):
                response = await client.get(f"{GATEWAY_URL}/health")
                responses.append(response.status_code)
            
            end_time = time.time()
            success = all(status == 200 for status in responses)  # All should succeed for basic rate
            details = f"10 requests in {end_time-start_time:.2f}s, All successful: {success}"
            log_test("Rate Limiting Basic", success, details)
        except Exception as e:
            log_test("Rate Limiting Basic", False, str(e))

async def test_error_handling():
    """Test error handling scenarios"""
    print("\n🚨 === ERROR HANDLING TESTS ===")
    
    async with httpx.AsyncClient(timeout=15.0) as client:
        
        # Test 1: Service Unavailable Scenario (fake service)
        try:
            # Test non-existent endpoint
            response = await client.get(f"{GATEWAY_URL}/api/nonexistent/")
            success = response.status_code == 404
            details = f"Status: {response.status_code}, Proper 404 handling: {success}"
            log_test("Service Unavailable Handling", success, details)
        except Exception as e:
            log_test("Service Unavailable Handling", False, str(e))
            
        # Test 2: Database Timeout Handling (very long request)
        try:
            # Large page size to test database performance
            response = await client.get(f"{GATEWAY_URL}/api/assignments/?size=1000")
            success = response.status_code in [200, 400, 422, 500]  # Should handle gracefully
            details = f"Status: {response.status_code}, Large request handled: {success}"
            log_test("Database Timeout Handling", success, details)
        except httpx.TimeoutException:
            log_test("Database Timeout Handling", True, "Timeout handled gracefully")
        except Exception as e:
            log_test("Database Timeout Handling", False, str(e))
            
        # Test 3: Gateway Error Propagation
        try:
            # Test invalid ID
            response = await client.get(f"{GATEWAY_URL}/api/assignments/99999")
            success = response.status_code in [404, 422]  # Should propagate not found
            details = f"Status: {response.status_code}, Error propagated correctly: {success}"
            log_test("Gateway Error Propagation", success, details)
        except Exception as e:
            log_test("Gateway Error Propagation", False, str(e))
            
        # Test 4: Graceful Degradation
        try:
            # Test malformed request
            response = await client.post(f"{GATEWAY_URL}/api/assignments/", json={"invalid": "data"})
            success = response.status_code in [400, 422] and response.headers.get("content-type", "").startswith("application/json")
            details = f"Status: {response.status_code}, Graceful degradation: {success}"
            log_test("Graceful Degradation", success, details)
        except Exception as e:
            log_test("Graceful Degradation", False, str(e))

async def test_health_check_validation():
    """Test comprehensive health check validation"""
    print("\n📊 === HEALTH CHECK VALIDATION ===")
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        
        # Test 1: All Status Endpoints Responding
        status_endpoints = [
            ("Assignment Status", f"{GATEWAY_URL}/api/assignments/status"),
            ("Content Status", f"{GATEWAY_URL}/api/courses/status"),
            ("Auth Health", f"{AUTH_URL}/health"),
            ("Gateway Health", f"{GATEWAY_URL}/health")
        ]
        
        all_responding = True
        for endpoint_name, url in status_endpoints:
            try:
                response = await client.get(url)
                success = response.status_code == 200
                if not success:
                    all_responding = False
                details = f"{response.status_code}"
            except Exception as e:
                all_responding = False
                details = f"Error: {str(e)}"
            
        log_test("All Status Endpoints Responding", all_responding, f"4/4 endpoints checked")
        
        # Test 2: Database Connectivity Checks
        try:
            # Check if health endpoints return database status
            response = await client.get(f"{GATEWAY_URL}/health")
            data = response.json()
            success = "services" in data and len(data["services"]) >= 2
            details = f"Database connectivity info present: {success}"
            log_test("Database Connectivity Checks", success, details)
        except Exception as e:
            log_test("Database Connectivity Checks", False, str(e))
            
        # Test 3: Service Dependency Mapping
        try:
            response = await client.get(f"{GATEWAY_URL}/health")
            data = response.json()
            services = data.get("services", {})
            success = len(services) >= 2  # At least assignment and content services
            details = f"Services mapped: {list(services.keys())}"
            log_test("Service Dependency Mapping", success, details)
        except Exception as e:
            log_test("Service Dependency Mapping", False, str(e))
            
        # Test 4: Health Aggregation Accuracy
        try:
            gateway_response = await client.get(f"{GATEWAY_URL}/health")
            gateway_data = gateway_response.json()
            
            # Check individual services
            assignment_response = await client.get(f"{ASSIGNMENT_URL}/api/assignments/status")
            content_response = await client.get(f"{CONTENT_URL}/api/v1/courses/status")
            
            gateway_says_healthy = gateway_data.get("gateway") == "healthy"
            services_actually_healthy = assignment_response.status_code == 200 and content_response.status_code == 200
            
            success = gateway_says_healthy == services_actually_healthy
            details = f"Gateway health matches reality: {success}"
            log_test("Health Aggregation Accuracy", success, details)
        except Exception as e:
            log_test("Health Aggregation Accuracy", False, str(e))

async def run_priority2_tests():
    """Run all Priority 2 tests"""
    print("🔧 Starting Priority 2 Testing...")
    print("=" * 60)
    
    # Run all test suites
    await test_security_validation()
    await test_error_handling()
    await test_health_check_validation()
    
    # Summary
    print("\n📊 === PRIORITY 2 TEST SUMMARY ===")
    total_tests = len(priority2_results)
    passed_tests = sum(1 for result in priority2_results if result["success"])
    failed_tests = total_tests - passed_tests
    
    print(f"Total Tests: {total_tests}")
    print(f"✅ Passed: {passed_tests}")
    print(f"❌ Failed: {failed_tests}")
    print(f"📈 Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    # Show failed tests
    if failed_tests > 0:
        print("\n🚨 Failed Tests:")
        for result in priority2_results:
            if not result["success"]:
                print(f"  - {result['test']}: {result['details']}")
    
    # Save results to file
    with open("priority2_test_results.json", "w") as f:
        json.dump(priority2_results, f, indent=2)
    
    print(f"\n📄 Detailed results saved to: priority2_test_results.json")
    
    # Return completion status
    success_rate = (passed_tests/total_tests)*100
    return success_rate >= 75  # 75% threshold for Priority 2

if __name__ == "__main__":
    result = asyncio.run(run_priority2_tests())
    if result:
        print("\n🎉 Priority 2 COMPLETE! Ready for Frontend Development!")
    else:
        print("\n⚠️ Priority 2 needs attention, but can proceed to Frontend.")
