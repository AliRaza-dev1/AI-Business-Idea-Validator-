from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base


class User(Base):
    """User model"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    ideas = relationship("Idea", back_populates="user", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user", cascade="all, delete-orphan")


class Idea(Base):
    """Business Idea model"""
    __tablename__ = "ideas"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=False)
    problem_statement = Column(Text, nullable=True)
    target_market = Column(Text, nullable=True)
    proposed_solution = Column(Text, nullable=True)
    value_proposition = Column(Text, nullable=True)
    business_model = Column(Text, nullable=True)
    status = Column(String(50), default="pending")  # pending, analyzing, completed, failed
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="ideas")
    analysis_result = relationship("AnalysisResult", back_populates="idea", uselist=False, cascade="all, delete-orphan")


class AnalysisResult(Base):
    """Analysis results model"""
    __tablename__ = "analysis_results"
    
    id = Column(Integer, primary_key=True, index=True)
    idea_id = Column(Integer, ForeignKey("ideas.id"), nullable=False, unique=True, index=True)
    market_score = Column(Float, default=0.0)
    feasibility_score = Column(Float, default=0.0)
    financial_score = Column(Float, default=0.0)
    risk_score = Column(Float, default=0.0)
    overall_score = Column(Float, default=0.0)
    
    # Detailed analysis
    market_analysis = Column(Text, nullable=True)
    feasibility_analysis = Column(Text, nullable=True)
    financial_analysis = Column(Text, nullable=True)
    risk_analysis = Column(Text, nullable=True)
    competitive_analysis = Column(Text, nullable=True)
    strengths = Column(Text, nullable=True)
    weaknesses = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    idea = relationship("Idea", back_populates="analysis_result")
    recommendations = relationship("Recommendation", back_populates="analysis_result", cascade="all, delete-orphan")


class Recommendation(Base):
    """Recommendations model"""
    __tablename__ = "recommendations"
    
    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, ForeignKey("analysis_results.id"), nullable=False, index=True)
    recommendation_text = Column(Text, nullable=False)
    category = Column(String(100), nullable=False)  # market, financial, technical, operational
    priority = Column(String(50), default="medium")  # high, medium, low
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    analysis_result = relationship("AnalysisResult", back_populates="recommendations")


class AuditLog(Base):
    """Audit logs model"""
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    action = Column(String(255), nullable=False)
    resource = Column(String(255), nullable=True)
    resource_id = Column(Integer, nullable=True)
    details = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    user = relationship("User", back_populates="audit_logs")
