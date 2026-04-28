from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


# ============ User Schemas ============
class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    full_name: Optional[str] = None


class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ============ Idea Schemas ============
class IdeaBase(BaseModel):
    title: str
    description: str
    problem_statement: Optional[str] = None
    target_market: Optional[str] = None
    proposed_solution: Optional[str] = None
    value_proposition: Optional[str] = None
    business_model: Optional[str] = None


class IdeaCreate(IdeaBase):
    pass


class IdeaUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    problem_statement: Optional[str] = None
    target_market: Optional[str] = None
    proposed_solution: Optional[str] = None
    value_proposition: Optional[str] = None
    business_model: Optional[str] = None


class IdeaResponse(IdeaBase):
    id: int
    user_id: int
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ============ Analysis Result Schemas ============
class RecommendationResponse(BaseModel):
    id: int
    recommendation_text: str
    category: str
    priority: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class AnalysisResultResponse(BaseModel):
    id: int
    idea_id: int
    market_score: float
    feasibility_score: float
    financial_score: float
    risk_score: float
    overall_score: float
    market_analysis: Optional[str] = None
    feasibility_analysis: Optional[str] = None
    financial_analysis: Optional[str] = None
    risk_analysis: Optional[str] = None
    competitive_analysis: Optional[str] = None
    strengths: Optional[str] = None
    weaknesses: Optional[str] = None
    recommendations: List[RecommendationResponse] = []
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ============ Auth Schemas ============
class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# ============ Analysis Request Schema ============
class AnalyzeIdeaRequest(BaseModel):
    pass  # Analysis is triggered without additional input after idea is created


# ============ Report Schema ============
class ReportResponse(BaseModel):
    idea: IdeaResponse
    analysis: AnalysisResultResponse
    
    class Config:
        from_attributes = True
