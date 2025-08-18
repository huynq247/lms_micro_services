from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_database
from app.models.assignment import Assignment
from app.schemas.assignment import (
    AssignmentCreate, AssignmentUpdate, AssignmentResponse,
    AssignmentFilter, AssignmentStatus
)
from app.schemas.common import PaginatedResponse, PaginationParams, get_pagination_params
from app.utils.crud import AssignmentCRUD
from app.utils.external_services import AuthServiceClient, ContentServiceClient

router = APIRouter(prefix="/assignments", tags=["assignments"])

auth_client = AuthServiceClient()
content_client = ContentServiceClient()


@router.post("/", response_model=AssignmentResponse, status_code=status.HTTP_201_CREATED)
async def create_assignment(
    assignment: AssignmentCreate,
    db: AsyncSession = Depends(get_database)
):
    """Create a new assignment"""
    assignment_crud = AssignmentCRUD(db)
    
    try:
        # TODO: Re-enable external service validation when services are properly integrated
        # Validate instructor exists
        # instructor_valid = await auth_client.validate_user(assignment.instructor_id)
        # if not instructor_valid:
        #     raise HTTPException(
        #         status_code=status.HTTP_404_NOT_FOUND,
        #         detail=f"Instructor with ID {assignment.instructor_id} not found"
        #     )
        
        # Validate student exists  
        # student_valid = await auth_client.validate_user(assignment.student_id)
        # if not student_valid:
        #     raise HTTPException(
        #         status_code=status.HTTP_404_NOT_FOUND,
        #         detail=f"Student with ID {assignment.student_id} not found"
        #     )
        
        # Validate content exists and get details
        # content_data = await content_client.get_content_details(assignment.content_id)
        # if not content_data:
        #     raise HTTPException(
        #         status_code=status.HTTP_404_NOT_FOUND,
        #         detail=f"Content with ID {assignment.content_id} not found"
        #     )
        
        # Create assignment (using provided content_title for now)
        db_assignment = await assignment_crud.create_assignment(assignment)
        return db_assignment
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating assignment: {str(e)}"
        )


@router.get("/status")
async def get_assignments_status(db: AsyncSession = Depends(get_database)):
    """Get assignments service status and basic stats"""
    try:
        from sqlalchemy import select
        result = await db.execute(select(Assignment).limit(1))
        assignment = result.scalar_one_or_none()
        
        if assignment:
            return {
                "service": "assignment-service",
                "status": "healthy",
                "sample_assignment": {
                    "id": assignment.id,
                    "title": assignment.title,
                    "status": assignment.status,
                    "created_at": assignment.created_at.isoformat() if assignment.created_at else None
                },
                "message": "Service is operational"
            }
        else:
            return {
                "service": "assignment-service", 
                "status": "healthy",
                "message": "No assignments found"
            }
    except Exception as e:
        return {
            "service": "assignment-service",
            "status": "error", 
            "error": str(e)
        }


@router.get("/{assignment_id}", response_model=AssignmentResponse)
async def get_assignment(
    assignment_id: int,
    db: AsyncSession = Depends(get_database)
):
    """Get assignment by ID"""
    assignment_crud = AssignmentCRUD(db)
    
    assignment = await assignment_crud.get_assignment(assignment_id)
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found"
        )
    
    return assignment


@router.get("/")
async def get_assignments(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    student_id: Optional[int] = Query(None),
    instructor_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_database)
):
    """Get assignments - NO RESPONSE MODEL TO AVOID SERIALIZATION ISSUES"""
    try:
        assignment_crud = AssignmentCRUD(db)
        
        # Create filter and pagination
        assignment_filter = AssignmentFilter(
            student_id=student_id,
            instructor_id=instructor_id
        )
        pagination = PaginationParams(page=page, size=size)
        
        assignments, total = await assignment_crud.get_assignments(assignment_filter, pagination)
        
        # Manual serialization
        items = []
        for assignment in assignments:
            items.append({
                "id": assignment.id,
                "instructor_id": assignment.instructor_id,
                "student_id": assignment.student_id,
                "content_type": assignment.content_type,
                "content_id": assignment.content_id,
                "content_title": assignment.content_title,
                "title": assignment.title,
                "description": assignment.description,
                "instructions": assignment.instructions,
                "status": assignment.status,
                "is_active": assignment.is_active,
                "created_at": assignment.created_at.isoformat() if assignment.created_at else None
            })
        
        # Return properly formatted response for frontend/testing
        return {
            "assignments": items,
            "total": total,
            "page": page,
            "size": size,
            "total_pages": (total + size - 1) // size
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error: {str(e)}"
        )


@router.get("/instructors/{instructor_id}", response_model=List[AssignmentResponse])
async def get_instructor_assignments(
    instructor_id: int,
    status_filter: Optional[AssignmentStatus] = Query(None),
    db: AsyncSession = Depends(get_database)
):
    """Get assignments for a specific instructor"""
    assignment_crud = AssignmentCRUD(db)
    
    try:
        assignments = await assignment_crud.get_instructor_assignments(instructor_id)
        return assignments
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting instructor assignments: {str(e)}"
        )


@router.get("/students/{student_id}", response_model=List[AssignmentResponse])
async def get_student_assignments(
    student_id: int,
    status_filter: Optional[AssignmentStatus] = Query(None),
    db: AsyncSession = Depends(get_database)
):
    """Get assignments for a specific student"""
    assignment_crud = AssignmentCRUD(db)
    
    try:
        assignments = await assignment_crud.get_student_assignments(student_id, status_filter)
        return assignments
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting student assignments: {str(e)}"
        )


@router.put("/{assignment_id}", response_model=AssignmentResponse)
async def update_assignment(
    assignment_id: int,
    assignment_update: AssignmentUpdate,
    db: AsyncSession = Depends(get_database)
):
    """Update an assignment"""
    assignment_crud = AssignmentCRUD(db)
    
    assignment = await assignment_crud.update_assignment(assignment_id, assignment_update)
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found"
        )
    
    return assignment


@router.delete("/{assignment_id}")
async def delete_assignment(
    assignment_id: int,
    db: AsyncSession = Depends(get_database)
):
    """Delete an assignment"""
    assignment_crud = AssignmentCRUD(db)
    
    deleted = await assignment_crud.delete_assignment(assignment_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found"
        )
    
    return {"message": "Assignment deleted successfully"}
