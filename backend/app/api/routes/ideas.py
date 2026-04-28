from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.models import Idea, User
from app.schemas.schemas import IdeaCreate, IdeaUpdate, IdeaResponse
from typing import List

router = APIRouter()


@router.post("/", response_model=IdeaResponse, status_code=status.HTTP_201_CREATED)
async def create_idea(
    idea_data: IdeaCreate,
    user_id: int = 1,  # Default to demo user=1 for testing
    db: Session = Depends(get_db)
):
    """Create a new business idea"""
    
    # For demo purposes, create a default user if needed
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        # Create demo user for testing
        demo_user = User(
            id=user_id,
            email=f"demo_user_{user_id}@example.com",
            password_hash="demo_hash_placeholder",
            full_name="Demo User",
            is_active=True
        )
        db.add(demo_user)
        db.commit()
        user = demo_user
    
    # Create new idea
    new_idea = Idea(
        user_id=user_id,
        title=idea_data.title,
        description=idea_data.description,
        problem_statement=idea_data.problem_statement,
        target_market=idea_data.target_market,
        proposed_solution=idea_data.proposed_solution,
        value_proposition=idea_data.value_proposition,
        business_model=idea_data.business_model,
        status="pending"
    )
    
    db.add(new_idea)
    db.commit()
    db.refresh(new_idea)
    
    return new_idea


@router.get("/{idea_id}", response_model=IdeaResponse)
async def get_idea(idea_id: int, db: Session = Depends(get_db)):
    """Get a specific idea"""
    
    idea = db.query(Idea).filter(Idea.id == idea_id).first()
    if not idea:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Idea not found"
        )
    
    return idea


@router.get("/", response_model=List[IdeaResponse])
async def list_ideas(
    user_id: int = None,
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """List ideas (optionally filtered by user)"""
    
    query = db.query(Idea)
    
    if user_id:
        query = query.filter(Idea.user_id == user_id)
    
    ideas = query.offset(skip).limit(limit).all()
    return ideas


@router.put("/{idea_id}", response_model=IdeaResponse)
async def update_idea(
    idea_id: int,
    idea_data: IdeaUpdate,
    db: Session = Depends(get_db)
):
    """Update an idea"""
    
    idea = db.query(Idea).filter(Idea.id == idea_id).first()
    if not idea:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Idea not found"
        )
    
    # Update fields if provided
    if idea_data.title is not None:
        idea.title = idea_data.title
    if idea_data.description is not None:
        idea.description = idea_data.description
    if idea_data.problem_statement is not None:
        idea.problem_statement = idea_data.problem_statement
    if idea_data.target_market is not None:
        idea.target_market = idea_data.target_market
    if idea_data.proposed_solution is not None:
        idea.proposed_solution = idea_data.proposed_solution
    if idea_data.value_proposition is not None:
        idea.value_proposition = idea_data.value_proposition
    if idea_data.business_model is not None:
        idea.business_model = idea_data.business_model
    
    db.commit()
    db.refresh(idea)
    
    return idea


@router.delete("/{idea_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_idea(idea_id: int, db: Session = Depends(get_db)):
    """Delete an idea"""
    
    idea = db.query(Idea).filter(Idea.id == idea_id).first()
    if not idea:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Idea not found"
        )
    
    db.delete(idea)
    db.commit()
    
    return None
