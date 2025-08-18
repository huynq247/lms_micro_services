"""
Simple API Gateway simulation for development testing
WITHOUT Docker - just run the services manually and use this gateway for routing
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import httpx
import asyncio
from typing import Any

app = FastAPI(
    title="🌐 LMS API Gateway",
    description="""
    # Learning Management System - API Gateway
    
    Central routing point for all LMS microservices.
    
    ## Available Services:
    
    ### 📚 Assignment Service (`/api/assignments/*`)
    - Manages assignments, user progress, and study sessions
    - Endpoints: assignments, users, progress, analytics
    - Database: PostgreSQL
    - Port: 8004
    
    ### 📖 Content Service (`/api/courses/*`, `/api/decks/*`)
    - Manages courses, lessons, decks, and flashcards
    - Endpoints: courses, lessons, decks, flashcards
    - Database: MongoDB  
    - Port: 8002
    
    ## Authentication
    - JWT tokens (coming soon)
    - API key authentication (coming soon)
    
    ## Rate Limiting
    - Per-user limits (coming soon)
    - Per-IP limits (coming soon)
    
    ## Health Monitoring
    - Gateway health: `GET /health`
    - Individual service health monitoring
    """,
    version="1.0.0",
    contact={
        "name": "LMS Development Team",
        "email": "dev@lms.local"
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT"
    }
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Service URLs - update these if services run on different ports
ASSIGNMENT_SERVICE_URL = "http://localhost:8004"
CONTENT_SERVICE_URL = "http://localhost:8002"

async def forward_request(url: str, method: str, headers: dict, params: dict = None, json_data: Any = None):
    """Forward request to target service"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            if method == "GET":
                response = await client.get(url, headers=headers, params=params)
            elif method == "POST":
                response = await client.post(url, headers=headers, params=params, json=json_data)
            elif method == "PUT":
                response = await client.put(url, headers=headers, params=params, json=json_data)
            elif method == "DELETE":
                response = await client.delete(url, headers=headers, params=params)
            else:
                raise HTTPException(status_code=405, detail="Method not allowed")
            
            return {
                "status_code": response.status_code,
                "content": response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text,
                "headers": dict(response.headers)
            }
        except httpx.ConnectError:
            raise HTTPException(status_code=503, detail=f"Service unavailable: {url}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Gateway error: {str(e)}")

@app.get("/")
async def gateway_info():
    """API Gateway information - Frontend Integration Ready"""
    return {
        "service": "LMS API Gateway",
        "version": "1.0.0",
        "status": "ready_for_frontend",
        "base_url": "http://localhost:8000",
        "documentation": {
            "swagger_ui": "/docs",
            "redoc": "/redoc",
            "openapi_json": "/openapi.json"
        },
        "services": {
            "assignment_service": ASSIGNMENT_SERVICE_URL,
            "content_service": CONTENT_SERVICE_URL
        },
        "available_endpoints": {
            "assignments": "/api/assignments/",
            "courses": "/api/courses/*",
            "decks": "/api/decks/*",
            "health": "/health",
            "status": {
                "assignments": "/api/assignments/status",
                "courses": "/api/courses/status"
            }
        },
        "frontend_notes": {
            "cors": "enabled_for_all_origins",
            "authentication": "jwt_implementation_pending",
            "pagination": "supported_with_page_size_params",
            "error_handling": "standard_http_status_codes"
        }
    }

@app.get("/health")
async def health_check():
    """Aggregate health check"""
    health_status = {"gateway": "healthy", "services": {}}
    
    # Check Assignment Service
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{ASSIGNMENT_SERVICE_URL}/health")
            health_status["services"]["assignment_service"] = "healthy" if response.status_code == 200 else "unhealthy"
    except:
        health_status["services"]["assignment_service"] = "unavailable"
    
    # Check Content Service
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{CONTENT_SERVICE_URL}/health")
            health_status["services"]["content_service"] = "healthy" if response.status_code == 200 else "unhealthy"
    except:
        health_status["services"]["content_service"] = "unavailable"
    
    return health_status

# Assignment Service Routes
@app.api_route("/api/assignments/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def route_assignments(request: Request, path: str):
    """Route assignments requests"""
    url = f"{ASSIGNMENT_SERVICE_URL}/api/assignments/{path}"
    json_data = await request.json() if request.headers.get("content-type") == "application/json" else None
    
    result = await forward_request(
        url=url,
        method=request.method,
        headers=dict(request.headers),
        params=dict(request.query_params),
        json_data=json_data
    )
    
    return JSONResponse(
        content=result["content"],
        status_code=result["status_code"]
    )

@app.api_route("/api/progress/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def route_progress(request: Request, path: str):
    """Route progress requests"""
    url = f"{ASSIGNMENT_SERVICE_URL}/api/progress/{path}"
    json_data = await request.json() if request.headers.get("content-type") == "application/json" else None
    
    result = await forward_request(
        url=url,
        method=request.method,
        headers=dict(request.headers),
        params=dict(request.query_params),
        json_data=json_data
    )
    
    return result["content"]

@app.api_route("/api/sessions/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def route_sessions(request: Request, path: str):
    """Route sessions requests"""
    url = f"{ASSIGNMENT_SERVICE_URL}/api/sessions/{path}"
    json_data = await request.json() if request.headers.get("content-type") == "application/json" else None
    
    result = await forward_request(
        url=url,
        method=request.method,
        headers=dict(request.headers),
        params=dict(request.query_params),
        json_data=json_data
    )
    
    return result["content"]

@app.api_route("/api/analytics/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def route_analytics(request: Request, path: str):
    """Route analytics requests"""
    url = f"{ASSIGNMENT_SERVICE_URL}/api/analytics/{path}"
    json_data = await request.json() if request.headers.get("content-type") == "application/json" else None
    
    result = await forward_request(
        url=url,
        method=request.method,
        headers=dict(request.headers),
        params=dict(request.query_params),
        json_data=json_data
    )
    
    return result["content"]

# Content Service Routes
@app.api_route("/api/courses/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def route_courses(request: Request, path: str):
    """Route courses requests"""
    url = f"{CONTENT_SERVICE_URL}/api/v1/courses/{path}"
    json_data = await request.json() if request.headers.get("content-type") == "application/json" else None
    
    result = await forward_request(
        url=url,
        method=request.method,
        headers=dict(request.headers),
        params=dict(request.query_params),
        json_data=json_data
    )
    
    return JSONResponse(
        content=result["content"],
        status_code=result["status_code"]
    )

@app.api_route("/api/decks/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def route_decks(request: Request, path: str):
    """Route decks requests"""
    url = f"{CONTENT_SERVICE_URL}/api/v1/decks/{path}"
    json_data = await request.json() if request.headers.get("content-type") == "application/json" else None
    
    result = await forward_request(
        url=url,
        method=request.method,
        headers=dict(request.headers),
        params=dict(request.query_params),
        json_data=json_data
    )
    
    return JSONResponse(
        content=result["content"],
        status_code=result["status_code"]
    )

if __name__ == "__main__":
    import uvicorn
    print("🌐 Starting API Gateway on http://localhost:8000")
    print("📚 Assignment Service: http://localhost:8004")
    print("📖 Content Service: http://localhost:8002")
    print("🔗 Gateway Routes:")
    print("  - /api/assignments/* → Assignment Service")
    print("  - /api/courses/* → Content Service")
    uvicorn.run(app, host="0.0.0.0", port=8000)
