from fastapi import APIRouter, Depends, HTTPException, status, Query
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List, Optional

from app.core.database import get_database
from app.schemas.content import (
    DeckCreate, DeckUpdate, DeckResponse, DeckFilter,
    FlashcardCreate, FlashcardUpdate, FlashcardResponse,
    ReorderRequest, PaginationParams, PaginatedResponse, MessageResponse
)
from app.utils.crud import DeckCRUD, FlashcardCRUD

router = APIRouter(prefix="/decks", tags=["Decks & Flashcards"])

# Deck endpoints
@router.post("/", response_model=DeckResponse, status_code=status.HTTP_201_CREATED)
async def create_deck(
    deck: DeckCreate,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Create a new deck"""
    deck_crud = DeckCRUD(db)
    
    # TODO: Get instructor name from auth service
    instructor_name = f"Instructor {deck.instructor_id}"
    
    try:
        db_deck = await deck_crud.create_deck(deck, instructor_name)
        return DeckResponse(**db_deck.dict())
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating deck: {str(e)}"
        )

@router.get("/{deck_id}", response_model=DeckResponse)
async def get_deck(
    deck_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get deck by ID"""
    deck_crud = DeckCRUD(db)
    deck = await deck_crud.get_deck(deck_id)
    
    if not deck:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deck not found"
        )
    
    return DeckResponse(**deck.dict())

@router.get("/", response_model=PaginatedResponse)
async def get_decks(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None, max_length=100),
    instructor_id: Optional[int] = Query(None),
    category: Optional[str] = Query(None),
    tags: Optional[str] = Query(None, description="Comma-separated tags"),
    is_published: Optional[bool] = Query(None),
    is_active: Optional[bool] = Query(True),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get decks with pagination and filtering"""
    deck_crud = DeckCRUD(db)
    
    pagination = PaginationParams(page=page, size=size, search=search)
    
    # Parse tags from comma-separated string
    tag_list = None
    if tags:
        tag_list = [tag.strip().lower() for tag in tags.split(",") if tag.strip()]
    
    filters = DeckFilter(
        instructor_id=instructor_id,
        category=category,
        tags=tag_list,
        is_published=is_published,
        is_active=is_active
    )
    
    result = await deck_crud.get_decks(pagination, filters)
    
    # Convert decks to response format
    decks_response = [DeckResponse(**deck.dict()) for deck in result["items"]]
    result["items"] = decks_response
    
    return PaginatedResponse(**result)

@router.put("/{deck_id}", response_model=DeckResponse)
async def update_deck(
    deck_id: str,
    deck_update: DeckUpdate,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Update deck"""
    deck_crud = DeckCRUD(db)
    
    updated_deck = await deck_crud.update_deck(deck_id, deck_update)
    if not updated_deck:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deck not found or no changes made"
        )
    
    return DeckResponse(**updated_deck.dict())

@router.delete("/{deck_id}", response_model=MessageResponse)
async def delete_deck(
    deck_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Soft delete deck"""
    deck_crud = DeckCRUD(db)
    
    success = await deck_crud.delete_deck(deck_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deck not found"
        )
    
    return MessageResponse(message="Deck deleted successfully")

@router.get("/instructor/{instructor_id}", response_model=List[DeckResponse])
async def get_decks_by_instructor(
    instructor_id: int,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get all decks by instructor"""
    deck_crud = DeckCRUD(db)
    decks = await deck_crud.get_decks_by_instructor(instructor_id)
    
    return [DeckResponse(**deck.dict()) for deck in decks]

# Flashcard endpoints
@router.post("/{deck_id}/flashcards", response_model=FlashcardResponse, status_code=status.HTTP_201_CREATED)
async def create_flashcard(
    deck_id: str,
    flashcard: FlashcardCreate,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Create a new flashcard for a deck"""
    # Verify deck exists
    deck_crud = DeckCRUD(db)
    deck = await deck_crud.get_deck(deck_id)
    if not deck:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deck not found"
        )
    
    # Set deck_id from URL
    flashcard.deck_id = deck_id
    
    flashcard_crud = FlashcardCRUD(db)
    
    try:
        db_flashcard = await flashcard_crud.create_flashcard(flashcard)
        return FlashcardResponse(**db_flashcard.dict())
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating flashcard: {str(e)}"
        )

@router.get("/{deck_id}/flashcards", response_model=List[FlashcardResponse])
async def get_flashcards_by_deck(
    deck_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get all flashcards for a deck"""
    # Verify deck exists
    deck_crud = DeckCRUD(db)
    deck = await deck_crud.get_deck(deck_id)
    if not deck:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deck not found"
        )
    
    flashcard_crud = FlashcardCRUD(db)
    flashcards = await flashcard_crud.get_flashcards_by_deck(deck_id)
    
    return [FlashcardResponse(**flashcard.dict()) for flashcard in flashcards]

@router.get("/flashcards/{flashcard_id}", response_model=FlashcardResponse)
async def get_flashcard(
    flashcard_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get flashcard by ID"""
    flashcard_crud = FlashcardCRUD(db)
    flashcard = await flashcard_crud.get_flashcard(flashcard_id)
    
    if not flashcard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Flashcard not found"
        )
    
    return FlashcardResponse(**flashcard.dict())

@router.put("/flashcards/{flashcard_id}", response_model=FlashcardResponse)
async def update_flashcard(
    flashcard_id: str,
    flashcard_update: FlashcardUpdate,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Update flashcard"""
    flashcard_crud = FlashcardCRUD(db)
    
    updated_flashcard = await flashcard_crud.update_flashcard(flashcard_id, flashcard_update)
    if not updated_flashcard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Flashcard not found or no changes made"
        )
    
    return FlashcardResponse(**updated_flashcard.dict())

@router.delete("/flashcards/{flashcard_id}", response_model=MessageResponse)
async def delete_flashcard(
    flashcard_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Soft delete flashcard"""
    flashcard_crud = FlashcardCRUD(db)
    
    success = await flashcard_crud.delete_flashcard(flashcard_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Flashcard not found"
        )
    
    return MessageResponse(message="Flashcard deleted successfully")

@router.put("/{deck_id}/flashcards/reorder", response_model=MessageResponse)
async def reorder_flashcards(
    deck_id: str,
    reorder_request: ReorderRequest,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Reorder flashcards in a deck"""
    # Verify deck exists
    deck_crud = DeckCRUD(db)
    deck = await deck_crud.get_deck(deck_id)
    if not deck:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deck not found"
        )
    
    flashcard_crud = FlashcardCRUD(db)
    success = await flashcard_crud.reorder_flashcards(deck_id, reorder_request.items)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error reordering flashcards"
        )
    
    return MessageResponse(message="Flashcards reordered successfully")
