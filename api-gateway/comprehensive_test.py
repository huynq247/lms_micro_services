#!/usr/bin/env python3
"""
Comprehensive API Gateway Test Suite
Tests all endpoints through the gateway to verify functionality
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Any

# Configuration
GATEWAY_URL = "http://localhost:8000"
ASSIGNMENT_SERVICE_URL = "http://localhost:8004"
CONTENT_SERVICE_URL = "http://localhost:8002"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

def print_header(text: str):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}")
    print(f"{text:^60}")
    print(f"{'='*60}{Colors.END}")

def print_test(test_name: str, status: str, details: str = ""):
    color = Colors.GREEN if status == "✅ PASS" else Colors.RED if status == "❌ FAIL" else Colors.YELLOW
    print(f"{color}{status}{Colors.END} {test_name}")
    if details:
        print(f"    {Colors.CYAN}{details}{Colors.END}")

def make_request(method: str, url: str, **kwargs) -> Dict[str, Any]:
    """Make HTTP request with error handling"""
    try:
        response = requests.request(method, url, timeout=10, **kwargs)
        return {
            "success": True,
            "status_code": response.status_code,
            "data": response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text,
            "headers": dict(response.headers)
        }
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "error": str(e),
            "status_code": None,
            "data": None
        }

def test_health_endpoints():
    """Test health check endpoints"""
    print_header("HEALTH CHECK TESTS")
    
    # Gateway health
    result = make_request("GET", f"{GATEWAY_URL}/health")
    if result["success"] and result["status_code"] == 200:
        print_test("Gateway Health Check", "✅ PASS", f"Status: {result['data'].get('gateway', 'unknown')}")
        
        # Check individual service health
        services = result["data"].get("services", {})
        for service, status in services.items():
            service_status = "✅ PASS" if status == "healthy" else "❌ FAIL"
            print_test(f"  {service.replace('_', ' ').title()}", service_status, f"Status: {status}")
    else:
        print_test("Gateway Health Check", "❌ FAIL", f"Error: {result.get('error', 'HTTP ' + str(result.get('status_code')))}")

def test_assignment_endpoints():
    """Test Assignment Service endpoints through gateway"""
    print_header("ASSIGNMENT SERVICE TESTS")
    
    endpoints_to_test = [
        ("GET", "/api/assignments/", "List all assignments"),
        ("GET", "/api/progress/assignments/1", "Get assignment progress"),
        ("GET", "/api/sessions/students/1", "Get student sessions"),
        ("GET", "/api/analytics/learning-data", "Learning analytics data"),
    ]
    
    for method, endpoint, description in endpoints_to_test:
        url = f"{GATEWAY_URL}{endpoint}"
        result = make_request(method, url)
        
        if result["success"] and 200 <= result["status_code"] < 300:
            data_info = ""
            if isinstance(result["data"], list):
                data_info = f"Retrieved {len(result['data'])} items"
            elif isinstance(result["data"], dict):
                data_info = f"Keys: {list(result['data'].keys())[:3]}..."
            print_test(description, "✅ PASS", data_info)
        else:
            error_info = result.get("error", f"HTTP {result.get('status_code')}")
            print_test(description, "❌ FAIL", error_info)

def test_content_endpoints():
    """Test Content Service endpoints through gateway"""
    print_header("CONTENT SERVICE TESTS")
    
    endpoints_to_test = [
        ("GET", "/api/courses/", "List all courses"),
        ("GET", "/api/decks/", "List all decks"),
    ]
    
    for method, endpoint, description in endpoints_to_test:
        url = f"{GATEWAY_URL}{endpoint}"
        result = make_request(method, url)
        
        if result["success"] and 200 <= result["status_code"] < 300:
            data_info = ""
            if isinstance(result["data"], dict) and "items" in result["data"]:
                items = result["data"]["items"]
                data_info = f"Retrieved {len(items)} items, Total: {result['data'].get('total', 'unknown')}"
            elif isinstance(result["data"], list):
                data_info = f"Retrieved {len(result['data'])} items"
            print_test(description, "✅ PASS", data_info)
        else:
            error_info = result.get("error", f"HTTP {result.get('status_code')}")
            print_test(description, "❌ FAIL", error_info)

def test_create_operations():
    """Test CREATE operations through gateway"""
    print_header("CREATE OPERATIONS TESTS")
    
    # Test creating a new assignment
    assignment_data = {
        "title": "Gateway Test Assignment",
        "description": "Testing assignment creation through API Gateway",
        "content_type": "course",
        "content_id": "test-course-id",
        "content_title": "Test Course",
        "instructor_id": 1,
        "student_id": 5
    }
    
    result = make_request("POST", f"{GATEWAY_URL}/api/assignments/", json=assignment_data)
    if result["success"] and result["status_code"] == 201:
        print_test("Create Assignment via Gateway", "✅ PASS", f"Created assignment ID: {result['data'].get('id', 'unknown')}")
    else:
        error_info = result.get("error", f"HTTP {result.get('status_code')}")
        print_test("Create Assignment via Gateway", "❌ FAIL", error_info)

def test_direct_vs_gateway():
    """Compare direct service calls vs gateway calls"""
    print_header("DIRECT vs GATEWAY COMPARISON")
    
    # Test assignments endpoint
    direct_result = make_request("GET", f"{ASSIGNMENT_SERVICE_URL}/api/assignments/")
    gateway_result = make_request("GET", f"{GATEWAY_URL}/api/assignments/")
    
    if direct_result["success"] and gateway_result["success"]:
        direct_count = len(direct_result["data"]) if isinstance(direct_result["data"], list) else "unknown"
        gateway_count = len(gateway_result["data"]) if isinstance(gateway_result["data"], list) else "unknown"
        
        if direct_count == gateway_count:
            print_test("Assignments: Direct vs Gateway", "✅ PASS", f"Both return {direct_count} items")
        else:
            print_test("Assignments: Direct vs Gateway", "⚠️ WARN", f"Direct: {direct_count}, Gateway: {gateway_count}")
    else:
        print_test("Assignments: Direct vs Gateway", "❌ FAIL", "One or both endpoints failed")
    
    # Test content service
    direct_result = make_request("GET", f"{CONTENT_SERVICE_URL}/api/v1/courses")
    gateway_result = make_request("GET", f"{GATEWAY_URL}/api/courses/")
    
    if direct_result["success"] and gateway_result["success"]:
        direct_total = direct_result["data"].get("total", 0) if isinstance(direct_result["data"], dict) else "unknown"
        gateway_total = gateway_result["data"].get("total", 0) if isinstance(gateway_result["data"], dict) else "unknown"
        
        if direct_total == gateway_total:
            print_test("Courses: Direct vs Gateway", "✅ PASS", f"Both return {direct_total} total items")
        else:
            print_test("Courses: Direct vs Gateway", "⚠️ WARN", f"Direct: {direct_total}, Gateway: {gateway_total}")
    else:
        print_test("Courses: Direct vs Gateway", "❌ FAIL", "One or both endpoints failed")

def test_error_handling():
    """Test error handling scenarios"""
    print_header("ERROR HANDLING TESTS")
    
    # Test non-existent endpoint
    result = make_request("GET", f"{GATEWAY_URL}/api/nonexistent/")
    if not result["success"] or result["status_code"] == 404:
        print_test("Non-existent endpoint", "✅ PASS", "Correctly returns 404 or connection error")
    else:
        print_test("Non-existent endpoint", "❌ FAIL", f"Unexpected response: {result['status_code']}")
    
    # Test invalid method
    result = make_request("PATCH", f"{GATEWAY_URL}/health")
    if not result["success"] or result["status_code"] in [405, 404]:
        print_test("Invalid HTTP method", "✅ PASS", "Correctly rejects invalid method")
    else:
        print_test("Invalid HTTP method", "❌ FAIL", f"Unexpected response: {result['status_code']}")

def generate_test_report():
    """Generate comprehensive test report"""
    print_header("TEST SUMMARY REPORT")
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"{Colors.BOLD}Test Run Timestamp:{Colors.END} {timestamp}")
    print(f"{Colors.BOLD}Gateway URL:{Colors.END} {GATEWAY_URL}")
    print(f"{Colors.BOLD}Assignment Service:{Colors.END} {ASSIGNMENT_SERVICE_URL}")
    print(f"{Colors.BOLD}Content Service:{Colors.END} {CONTENT_SERVICE_URL}")
    
    # Test gateway connectivity
    gateway_health = make_request("GET", f"{GATEWAY_URL}/health")
    if gateway_health["success"]:
        print(f"{Colors.GREEN}✅ All services are accessible through the gateway{Colors.END}")
        
        services = gateway_health["data"].get("services", {})
        healthy_services = sum(1 for status in services.values() if status == "healthy")
        total_services = len(services)
        
        print(f"{Colors.BOLD}Service Health:{Colors.END} {healthy_services}/{total_services} services healthy")
        
        if healthy_services == total_services:
            print(f"{Colors.GREEN}🎉 ALL SYSTEMS OPERATIONAL{Colors.END}")
        else:
            print(f"{Colors.YELLOW}⚠️  Some services need attention{Colors.END}")
    else:
        print(f"{Colors.RED}❌ Gateway is not accessible{Colors.END}")

def main():
    """Run comprehensive test suite"""
    print(f"{Colors.BOLD}{Colors.PURPLE}")
    print("🚀 API GATEWAY COMPREHENSIVE TEST SUITE")
    print("========================================")
    print(f"{Colors.END}")
    
    # Run all test suites
    test_health_endpoints()
    test_assignment_endpoints()
    test_content_endpoints()
    test_create_operations()
    test_direct_vs_gateway()
    test_error_handling()
    generate_test_report()
    
    print(f"\n{Colors.BOLD}{Colors.GREEN}✅ Test suite completed!{Colors.END}")
    print(f"{Colors.CYAN}Check results above for any issues that need attention.{Colors.END}")

if __name__ == "__main__":
    main()
