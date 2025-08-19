from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List, Optional, Dict, Any
from bson import ObjectId
from datetime import datetime
from app.models.content import Lesson, PyObjectId
from app.schemas.content import (
    LessonCreate, LessonUpdate
)
import logging

logger = logging.getLogger(__name__)

class LessonCRUD:
    """CRUD operations for lessons"""
    
    def __init__(self, database: AsyncIOMotorDatabase):
        self.db = database
        self.collection = database.lessons
    
    async def create_lesson(self, lesson_data: LessonCreate) -> Lesson:
        """Create a new lesson"""
        lesson_dict = lesson_data.dict()
        lesson_dict["course_id"] = ObjectId(lesson_dict["course_id"])
        lesson_dict["created_at"] = datetime.utcnow()
        
        result = await self.collection.insert_one(lesson_dict)
        lesson_dict["_id"] = result.inserted_id
        
        # Update course lesson count
        from .course_crud import CourseCRUD
        course_crud = CourseCRUD(self.db)
        await course_crud.update_course_lesson_count(lesson_data.course_id)
        
        return Lesson(**lesson_dict)
    
    async def get_lesson(self, lesson_id: str) -> Optional[Lesson]:
        """Get lesson by ID"""
        try:
            lesson_data = await self.collection.find_one({"_id": ObjectId(lesson_id)})
            if lesson_data:
                return Lesson(**lesson_data)
            return None
        except Exception as e:
            logger.error(f"Error getting lesson {lesson_id}: {e}")
            return None
    
    async def get_lessons_by_course(self, course_id: str) -> List[Lesson]:
        """Get all lessons for a course, ordered by order field"""
        try:
            cursor = self.collection.find({
                "course_id": ObjectId(course_id),
                "is_active": True
            }).sort("order", 1)
            
            lessons_data = await cursor.to_list(length=None)
            return [Lesson(**lesson_data) for lesson_data in lessons_data]
        except Exception as e:
            logger.error(f"Error getting lessons for course {course_id}: {e}")
            return []
    
    async def update_lesson(self, lesson_id: str, lesson_update: LessonUpdate) -> Optional[Lesson]:
        """Update lesson"""
        try:
            update_data = lesson_update.dict(exclude_unset=True)
            if update_data:
                update_data["updated_at"] = datetime.utcnow()
                
                result = await self.collection.update_one(
                    {"_id": ObjectId(lesson_id)},
                    {"$set": update_data}
                )
                
                if result.modified_count > 0:
                    return await self.get_lesson(lesson_id)
            
            return None
        except Exception as e:
            logger.error(f"Error updating lesson {lesson_id}: {e}")
            return None
    
    async def delete_lesson(self, lesson_id: str) -> bool:
        """Soft delete lesson"""
        try:
            # Get lesson to find course_id for updating count
            lesson = await self.get_lesson(lesson_id)
            if not lesson:
                return False
            
            result = await self.collection.update_one(
                {"_id": ObjectId(lesson_id)},
                {"$set": {"is_active": False, "updated_at": datetime.utcnow()}}
            )
            
            if result.modified_count > 0:
                # Update course lesson count
                from .course_crud import CourseCRUD
                course_crud = CourseCRUD(self.db)
                await course_crud.update_course_lesson_count(str(lesson.course_id))
                return True
            
            return False
        except Exception as e:
            logger.error(f"Error deleting lesson {lesson_id}: {e}")
            return False
    
    async def reorder_lessons(self, course_id: str, lesson_orders: List[Dict[str, Any]]) -> bool:
        """Reorder lessons in a course"""
        try:
            # Update each lesson's order
            for item in lesson_orders:
                await self.collection.update_one(
                    {"_id": ObjectId(item["id"]), "course_id": ObjectId(course_id)},
                    {"$set": {"order": item["order"], "updated_at": datetime.utcnow()}}
                )
            
            return True
        except Exception as e:
            logger.error(f"Error reordering lessons for course {course_id}: {e}")
            return False
