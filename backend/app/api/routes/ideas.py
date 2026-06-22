from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.models import Idea, User
from app.schemas.schemas import IdeaCreate, IdeaUpdate, IdeaResponse
from typing import List
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
router = APIRouter()


@router.post("/", response_model=IdeaResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("100/minute")
async def create_idea(
    request: Request,
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


@router.get("/", response_model=List[IdeaResponse])
async def list_ideas(
    user_id: int = None,
    status: str = None,
    search: str = None,
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """List ideas (optionally filtered by user, status, and search query)"""
    
    query = db.query(Idea)
    
    if user_id:
        query = query.filter(Idea.user_id == user_id)
        
    if status:
        query = query.filter(Idea.status == status)
        
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (Idea.title.ilike(search_filter)) | 
            (Idea.description.ilike(search_filter))
        )
    
    ideas = query.offset(skip).limit(limit).all()
    return ideas


# NOTE: This MUST be defined BEFORE /{idea_id} to avoid path parameter capture
@router.get("/user/recommendations")
async def get_idea_recommendations(
    user_id: int = 1,
    db: Session = Depends(get_db)
):
    """Advanced Recommendation Engine: Suggest new ideas based on past failures/successes"""
    # Get user's past ideas with their scores
    ideas = db.query(Idea).filter(Idea.user_id == user_id).all()
    if not ideas:
        return {"recommendations": []}
        
    history = []
    for idea in ideas:
        if idea.analysis_result:
            history.append(f"- Idea: {idea.title}\n  Description: {idea.description}\n  Overall Score: {idea.analysis_result.overall_score}\n  Weaknesses: {idea.analysis_result.weaknesses}")
        else:
            history.append(f"- Idea: {idea.title}\n  Description: {idea.description}\n  Status: Not analyzed yet")
            
    history_text = "\n".join(history)
    
    try:
        from app.services.ai_service import AIAnalysisService
        ai_service = AIAnalysisService()
        recommendations = ai_service.generate_idea_recommendations(history_text)
    except Exception:
        # Gracefully return empty recommendations if AI service is unavailable
        recommendations = []
    
    return {"recommendations": recommendations}


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

