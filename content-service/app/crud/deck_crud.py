from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List, Optional, Dict, Any
from bson import ObjectId
from datetime import datetime
from app.models.content import Deck, PyObjectId
from app.schemas.content import (
    DeckCreate, DeckUpdate
)
import logging

logger = logging.getLogger(__name__)

class DeckCRUD:
    """CRUD operations for flashcard decks"""
    
    def __init__(self, database: AsyncIOMotorDatabase):
        self.db = database
        self.collection = database.decks
    
    async def create_deck(self, deck_data: DeckCreate) -> Deck:
        """Create a new deck"""
        deck_dict = deck_data.dict()
        deck_dict["lesson_id"] = ObjectId(deck_dict["lesson_id"])
        deck_dict["created_at"] = datetime.utcnow()
        deck_dict["flashcard_count"] = 0  # Initialize count
        
        result = await self.collection.insert_one(deck_dict)
        deck_dict["_id"] = result.inserted_id
        
        return Deck(**deck_dict)
    
    async def get_deck(self, deck_id: str) -> Optional[Deck]:
        """Get deck by ID"""
        try:
            deck_data = await self.collection.find_one({"_id": ObjectId(deck_id)})
            if deck_data:
                return Deck(**deck_data)
            return None
        except Exception as e:
            logger.error(f"Error getting deck {deck_id}: {e}")
            return None
    
    async def get_decks(self, pagination: Dict[str, Any], filters: Dict[str, Any]) -> Dict[str, Any]:
        """Get decks with pagination and filters"""
        try:
            # Build query
            query = {"is_active": True}
            
            # Apply filters
            if filters.get("lesson_id"):
                query["lesson_id"] = ObjectId(filters["lesson_id"])
            if filters.get("course_id"):
                # Get lessons for this course first
                lessons_cursor = self.db.lessons.find({
                    "course_id": ObjectId(filters["course_id"]),
                    "is_active": True
                })
                lessons_data = await lessons_cursor.to_list(length=None)
                lesson_ids = [lesson["_id"] for lesson in lessons_data]
                query["lesson_id"] = {"$in": lesson_ids}
            if filters.get("instructor_id"):
                query["instructor_id"] = filters["instructor_id"]
            if filters.get("search"):
                query["$or"] = [
                    {"title": {"$regex": filters["search"], "$options": "i"}},
                    {"description": {"$regex": filters["search"], "$options": "i"}}
                ]
            
            # Get total count
            total = await self.collection.count_documents(query)
            
            # Build cursor with pagination
            cursor = self.collection.find(query).sort("created_at", -1)
            
            # Apply pagination
            page = pagination.get("page", 1)
            limit = pagination.get("size", 20)  # Use 'size' instead of 'limit'
            skip = (page - 1) * limit
            
            cursor = cursor.skip(skip).limit(limit)
            
            decks_data = await cursor.to_list(length=None)
            decks = [Deck(**deck_data) for deck_data in decks_data]
            
            # Calculate pagination info
            total_pages = (total + limit - 1) // limit
            has_next = page < total_pages
            has_prev = page > 1
            
            return {
                "items": decks,
                "total": total,
                "page": page,
                "size": limit,
                "pages": total_pages,
                "has_next": has_next,
                "has_prev": has_prev
            }
        except Exception as e:
            logger.error(f"Error getting decks: {e}")
            return {
                "items": [],
                "total": 0,
                "page": 1,
                "size": 20,
                "pages": 0,
                "has_next": False,
                "has_prev": False
            }
    
    async def get_decks_by_lesson(self, lesson_id: str) -> List[Deck]:
        """Get all decks for a lesson"""
        try:
            cursor = self.collection.find({
                "lesson_id": ObjectId(lesson_id),
                "is_active": True
            }).sort("created_at", 1)
            
            decks_data = await cursor.to_list(length=None)
            return [Deck(**deck_data) for deck_data in decks_data]
        except Exception as e:
            logger.error(f"Error getting decks for lesson {lesson_id}: {e}")
            return []
    
    async def get_decks_by_course(self, course_id: str) -> List[Deck]:
        """Get all decks for a course (through lessons)"""
        try:
            # First get all lessons for the course
            lessons_cursor = self.db.lessons.find({
                "course_id": ObjectId(course_id),
                "is_active": True
            })
            lessons_data = await lessons_cursor.to_list(length=None)
            lesson_ids = [lesson["_id"] for lesson in lessons_data]
            
            # Then get all decks for those lessons
            cursor = self.collection.find({
                "lesson_id": {"$in": lesson_ids},
                "is_active": True
            }).sort("created_at", 1)
            
            decks_data = await cursor.to_list(length=None)
            return [Deck(**deck_data) for deck_data in decks_data]
        except Exception as e:
            logger.error(f"Error getting decks for course {course_id}: {e}")
            return []
    
    async def update_deck(self, deck_id: str, deck_update: DeckUpdate) -> Optional[Deck]:
        """Update deck"""
        try:
            update_data = deck_update.dict(exclude_unset=True)
            if update_data:
                update_data["updated_at"] = datetime.utcnow()
                
                result = await self.collection.update_one(
                    {"_id": ObjectId(deck_id)},
                    {"$set": update_data}
                )
                
                if result.modified_count > 0:
                    return await self.get_deck(deck_id)
            
            return None
        except Exception as e:
            logger.error(f"Error updating deck {deck_id}: {e}")
            return None
    
    async def delete_deck(self, deck_id: str) -> bool:
        """Soft delete deck and all its flashcards"""
        try:
            # First delete all flashcards in this deck
            from .flashcard_crud import FlashcardCRUD
            flashcard_crud = FlashcardCRUD(self.db)
            await flashcard_crud.delete_flashcards_by_deck(deck_id)
            
            # Then soft delete the deck
            result = await self.collection.update_one(
                {"_id": ObjectId(deck_id)},
                {"$set": {"is_active": False, "updated_at": datetime.utcnow()}}
            )
            
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error deleting deck {deck_id}: {e}")
            return False
    
    async def update_deck_flashcard_count(self, deck_id: str):
        """Update flashcard count for a deck"""
        try:
            count = await self.db.flashcards.count_documents({
                "deck_id": ObjectId(deck_id),
                "is_active": True
            })
            
            await self.collection.update_one(
                {"_id": ObjectId(deck_id)},
                {"$set": {"flashcard_count": count, "updated_at": datetime.utcnow()}}
            )
        except Exception as e:
            logger.error(f"Error updating flashcard count for deck {deck_id}: {e}")
    
    async def get_user_decks(self, user_id: str) -> List[Deck]:
        """Get all decks accessible to a user"""
        try:
            # Get user's enrolled courses
            enrollments_cursor = self.db.enrollments.find({
                "user_id": ObjectId(user_id),
                "is_active": True
            })
            enrollments_data = await enrollments_cursor.to_list(length=None)
            course_ids = [enrollment["course_id"] for enrollment in enrollments_data]
            
            # Get all lessons for enrolled courses
            lessons_cursor = self.db.lessons.find({
                "course_id": {"$in": course_ids},
                "is_active": True
            })
            lessons_data = await lessons_cursor.to_list(length=None)
            lesson_ids = [lesson["_id"] for lesson in lessons_data]
            
            # Get all decks for those lessons
            cursor = self.collection.find({
                "lesson_id": {"$in": lesson_ids},
                "is_active": True
            }).sort("created_at", 1)
            
            decks_data = await cursor.to_list(length=None)
            return [Deck(**deck_data) for deck_data in decks_data]
        except Exception as e:
            logger.error(f"Error getting user decks for user {user_id}: {e}")
            return []
