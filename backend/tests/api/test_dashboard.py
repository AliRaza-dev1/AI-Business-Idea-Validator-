import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.models import Idea, AnalysisResult, User

def test_get_dashboard_stats_empty(client: TestClient):
    """Test dashboard stats when database is empty"""
    response = client.get("/api/v1/dashboard/stats")
    assert response.status_code == 200
    data = response.json()
    
    assert data["total_ideas"] == 0
    assert data["success_rate"] == 0.0
    assert data["average_score"] == 0.0
    assert data["total_analyzed"] == 0
    assert "total_users" in data
    assert data["recent_activity"] == []

def test_get_dashboard_stats_with_data(client: TestClient, db_session: Session):
    """Test dashboard stats with some data in DB"""
    # Create test user
    user = User(email="dash@test.com", password_hash="hash", full_name="Dash User")
    db_session.add(user)
    db_session.commit()

    # Create test ideas
    idea1 = Idea(
        title="Idea 1",
        description="Desc 1",
        status="completed"
    )
    idea2 = Idea(
        title="Idea 2",
        description="Desc 2",
        status="completed"
    )
    db_session.add(idea1)
    db_session.add(idea2)
    db_session.commit()
    db_session.refresh(idea1)
    db_session.refresh(idea2)
    
    # Create analysis results
    analysis1 = AnalysisResult(
        idea_id=idea1.id,
        overall_score=8.0,
        market_score=8.0,
        feasibility_score=8.0,
        financial_score=8.0,
        risk_score=8.0,
        market_analysis="market",
        feasibility_analysis="feasibility",
        financial_analysis="financial",
        risk_analysis="risk",
        competitive_analysis="competitive"
    )
    analysis2 = AnalysisResult(
        idea_id=idea2.id,
        overall_score=6.0,
        market_score=6.0,
        feasibility_score=6.0,
        financial_score=6.0,
        risk_score=6.0,
        market_analysis="market",
        feasibility_analysis="feasibility",
        financial_analysis="financial",
        risk_analysis="risk",
        competitive_analysis="competitive"
    )
    db_session.add(analysis1)
    db_session.add(analysis2)
    db_session.commit()

    # Get stats
    response = client.get("/api/v1/dashboard/stats")
    assert response.status_code == 200
    data = response.json()
    
    assert data["total_ideas"] >= 2
    assert data["total_analyzed"] >= 2
    
    # One is 8.0 (>=7), one is 6.0 (<7), so 1/2 = 50%
    assert data["success_rate"] == 50.0
    assert data["average_score"] == 7.0
    assert len(data["recent_activity"]) >= 2
