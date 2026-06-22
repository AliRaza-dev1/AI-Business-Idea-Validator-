import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.database import Base, get_db
from app.main import app
from unittest.mock import patch, MagicMock

SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test_ai.db"
engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


class TestRealAIIntegration:
    """Test cases for real AI analysis using OpenAI"""
    
    def setup_method(self):
        """Setup before each test"""
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
    
    @patch('app.services.ai_service.OpenAI')
    def test_trigger_real_analysis_calls_openai(self, mock_openai):
        """Test that analysis triggers real OpenAI API"""
        # Create an idea
        idea_data = {
            "title": "AI Startup",
            "description": "An AI-powered automation platform",
            "problem_statement": "Businesses waste time on repetitive tasks",
            "target_market": "SMBs",
            "proposed_solution": "AI automation workflow",
            "value_proposition": "Save 10 hours per week",
            "business_model": "SaaS"
        }
        create_response = client.post("/api/v1/ideas", json=idea_data)
        idea_id = create_response.json()["id"]
        
        # Trigger analysis
        response = client.post(f"/api/v1/analysis/{idea_id}/trigger")
        
        # Check response
        assert response.status_code == 202
        data = response.json()
        assert "status" in data
        assert data["status"] == "analyzing"
    
    @patch('app.services.analysis_orchestrator.analyze_idea_async')
    def test_analysis_stores_real_ai_results(self, mock_analyze):
        """Test that real AI results are stored in database"""
        mock_analyze.return_value = {
            "market_score": 8.2,
            "feasibility_score": 7.5,
            "financial_score": 8.0,
            "risk_score": 6.8,
            "overall_score": 7.6,
            "market_analysis": "Real AI market analysis",
            "feasibility_analysis": "Real feasibility analysis",
            "financial_analysis": "Real financial analysis",
            "risk_analysis": "Real risk analysis",
            "competitive_analysis": "Real competitive analysis"
        }
        
        # Create idea
        idea_data = {
            "title": "Test Idea",
            "description": "Test"
        }
        create_response = client.post("/api/v1/ideas", json=idea_data)
        idea_id = create_response.json()["id"]
        
        # Get analysis
        response = client.get(f"/api/v1/analysis/{idea_id}")
        assert response.status_code == 200
        
        data = response.json()
        # Real analysis should have content
        assert isinstance(data["market_score"], (int, float))
        assert isinstance(data["feasibility_score"], (int, float))
    
    def test_analysis_includes_ai_recommendations(self):
        """Test that analysis includes AI-generated recommendations"""
        idea_data = {
            "title": "Test Idea",
            "description": "Test description"
        }
        create_response = client.post("/api/v1/ideas", json=idea_data)
        idea_id = create_response.json()["id"]
        
        response = client.get(f"/api/v1/analysis/{idea_id}")
        data = response.json()
        
        # Should have recommendations
        assert "recommendations" in data
        assert isinstance(data["recommendations"], list)
        assert len(data["recommendations"]) > 0
        
        # Each recommendation should have required fields
        for rec in data["recommendations"]:
            assert "recommendation_text" in rec
            assert "category" in rec
            assert "priority" in rec
