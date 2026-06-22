from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
import json
from app.db.database import get_db
from app.models.models import Idea, AnalysisResult, User
from typing import Dict, Any

router = APIRouter(prefix="/api/v1/dashboard", tags=["Dashboard"])

@router.get("/stats", response_model=Dict[str, Any])
async def get_dashboard_stats(db: Session = Depends(get_db)):
    """Get statistics for the dashboard including advanced AI validation metrics"""
    total_ideas = db.query(Idea).count()
    
    # Calculate average score
    avg_score_query = db.query(func.avg(AnalysisResult.overall_score)).scalar()
    avg_score = float(avg_score_query) if avg_score_query else 0.0
    
    # Original success rate logic (overall_score >= 7.0)
    high_scoring = db.query(AnalysisResult).filter(AnalysisResult.overall_score >= 7.0).count()
    total_analyzed = db.query(AnalysisResult).count()
    success_rate = (high_scoring / total_analyzed * 100) if total_analyzed > 0 else 0.0
    
    # Find highest rated idea
    highest_analysis = db.query(AnalysisResult).order_by(AnalysisResult.overall_score.desc()).first()
    highest_rated = "N/A"
    highest_score = 0.0
    if highest_analysis and highest_analysis.idea:
        highest_rated = highest_analysis.idea.title
        highest_score = highest_analysis.overall_score
        
    # Find most risky idea (lowest risk management resilience score represents highest risk)
    riskiest_analysis = db.query(AnalysisResult).order_by(AnalysisResult.risk_score.asc()).first()
    most_risky = "N/A"
    highest_risk_val = 0.0
    if riskiest_analysis and riskiest_analysis.idea:
        most_risky = riskiest_analysis.idea.title
        highest_risk_val = riskiest_analysis.risk_score
        
    # Calculate average agent confidence dynamically
    analyses = db.query(AnalysisResult).all()
    confidences = []
    for analysis in analyses:
        try:
            if analysis.weaknesses and analysis.weaknesses.startswith("{"):
                weaknesses_data = json.loads(analysis.weaknesses)
                conf = weaknesses_data.get("overall_confidence")
                if conf is not None:
                    confidences.append(float(conf))
        except Exception:
            pass
            
    avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
    
    # Recent activity
    recent_ideas = db.query(Idea).order_by(Idea.created_at.desc()).limit(5).all()
    recent_ideas_data = [
        {
            "id": idea.id,
            "title": idea.title,
            "status": idea.status,
            "created_at": idea.created_at.isoformat()
        } for idea in recent_ideas
    ]
    
    # Active users
    total_users = db.query(User).count()
    
    return {
        "total_ideas": total_ideas,
        "success_rate": round(success_rate, 1),
        "average_score": round(avg_score, 1),
        "total_analyzed": total_analyzed,
        "highest_rated_idea": f"{highest_rated} ({highest_score * 10}/100)" if highest_analysis else "N/A",
        "most_risky_idea": f"{most_risky} (Resilience: {highest_risk_val}/20)" if riskiest_analysis else "N/A",
        "average_confidence": round(avg_confidence, 1),
        "total_users": total_users,
        "recent_activity": recent_ideas_data
    }

@router.get("/advanced-analytics", response_model=Dict[str, Any])
async def get_advanced_analytics(db: Session = Depends(get_db)):
    """Advanced analytics for B2B insights"""
    analyses = db.query(AnalysisResult).all()
    
    # Compute distribution thresholds (scaled out of 100 for frontend compatibility)
    excellent = sum(1 for a in analyses if a.overall_score >= 85)
    good = sum(1 for a in analyses if 70 <= a.overall_score < 85)
    average = sum(1 for a in analyses if 50 <= a.overall_score < 70)
    poor = sum(1 for a in analyses if a.overall_score < 50)
    
    score_ranges = {
        "excellent (85-100)": excellent,
        "good (70-84)": good,
        "average (50-69)": average,
        "poor (<50)": poor
    }
    
    # Subscores
    avg_market = db.query(func.avg(AnalysisResult.market_score)).scalar() or 0.0
    avg_feasibility = db.query(func.avg(AnalysisResult.feasibility_score)).scalar() or 0.0
    avg_financial = db.query(func.avg(AnalysisResult.financial_score)).scalar() or 0.0
    avg_risk = db.query(func.avg(AnalysisResult.risk_score)).scalar() or 0.0
    
    avg_subscores = {
        "market": float(avg_market),
        "feasibility": float(avg_feasibility),
        "financial": float(avg_financial),
        "risk": float(avg_risk)
    }
    
    status_distribution = dict(db.query(Idea.status, func.count(Idea.id)).group_by(Idea.status).all())
    
    return {
        "score_distribution": score_ranges,
        "average_subscores": {k: round(v, 2) for k, v in avg_subscores.items()},
        "status_distribution": status_distribution
    }
