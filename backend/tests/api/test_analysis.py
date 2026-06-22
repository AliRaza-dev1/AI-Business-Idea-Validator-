import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.database import Base, get_db
from app.main import app

# Test database
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test_analysis.db"
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


class TestAnalysisAPI:
    """Test cases for Analysis API endpoints"""
    
    def setup_method(self):
        """Setup before each test"""
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
    
    def test_get_analysis_returns_data(self):
        """Test that analysis endpoint returns valid data"""
        # Create an idea first
        idea_data = {
            "title": "Test Idea",
            "description": "Test description"
        }
        create_response = client.post("/api/v1/ideas", json=idea_data)
        idea_id = create_response.json()["id"]
        
        # Get analysis
        response = client.get(f"/api/v1/analysis/{idea_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert "id" in data
        assert "overall_score" in data
        assert "market_score" in data
        assert "feasibility_score" in data
        assert "financial_score" in data
        assert "risk_score" in data
        assert "market_analysis" in data
        assert "recommendations" in data
    
    def test_analysis_scores_are_valid_range(self):
        """Test that analysis scores are between 0-10"""
        idea_data = {
            "title": "Test Idea",
            "description": "Test description"
        }
        create_response = client.post("/api/v1/ideas", json=idea_data)
        idea_id = create_response.json()["id"]
        
        response = client.get(f"/api/v1/analysis/{idea_id}")
        data = response.json()
        
        # Verify scores are in valid range
        assert 0 <= data["overall_score"] <= 10
        assert 0 <= data["market_score"] <= 10
        assert 0 <= data["feasibility_score"] <= 10
        assert 0 <= data["financial_score"] <= 10
        assert 0 <= data["risk_score"] <= 10
    
    def test_analysis_has_recommendations(self):
        """Test that analysis includes recommendations"""
        idea_data = {
            "title": "Test Idea",
            "description": "Test description"
        }
        create_response = client.post("/api/v1/ideas", json=idea_data)
        idea_id = create_response.json()["id"]
        
        response = client.get(f"/api/v1/analysis/{idea_id}")
        data = response.json()
        
        assert isinstance(data["recommendations"], list)
        assert len(data["recommendations"]) > 0
        assert "recommendation_text" in data["recommendations"][0]
    
    def test_analysis_has_text_analysis(self):
        """Test that analysis includes detailed text analysis"""
        idea_data = {
            "title": "Test Idea",
            "description": "Test description"
        }
        create_response = client.post("/api/v1/ideas", json=idea_data)
        idea_id = create_response.json()["id"]
        
        response = client.get(f"/api/v1/analysis/{idea_id}")
        data = response.json()
        
        assert data["market_analysis"] is not None
        assert len(data["market_analysis"]) > 0
        assert data["feasibility_analysis"] is not None
        assert data["financial_analysis"] is not None
        assert data["risk_analysis"] is not None
