import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.database import Base, get_db
from app.main import app

SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test_reports.db"
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


class TestPDFReportGeneration:
    """Test cases for PDF report generation"""
    
    def setup_method(self):
        """Setup before each test"""
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
    
    def test_generate_pdf_report(self):
        """Test PDF report can be generated"""
        # Create idea
        idea_data = {
            "title": "Innovative Product",
            "description": "A revolutionary product",
            "problem_statement": "Current solutions are inadequate",
            "target_market": "Enterprise customers",
            "proposed_solution": "Our unique solution",
            "value_proposition": "10x better than alternatives",
            "business_model": "SaaS subscription"
        }
        create_response = client.post("/api/v1/ideas", json=idea_data)
        idea_id = create_response.json()["id"]
        
        # Generate PDF
        response = client.get(f"/api/v1/ideas/{idea_id}/report/pdf")
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/pdf"
        assert len(response.content) > 0
    
    def test_generate_json_report(self):
        """Test JSON report can be generated"""
        # Create idea
        idea_data = {
            "title": "Innovative Product",
            "description": "A revolutionary product"
        }
        create_response = client.post("/api/v1/ideas", json=idea_data)
        idea_id = create_response.json()["id"]
        
        # Generate JSON report
        response = client.get(f"/api/v1/ideas/{idea_id}/report/json")
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"
        
        data = response.json()
        assert "idea" in data
        assert "analysis" in data
        assert data["idea"]["id"] == idea_id
    
    def test_report_includes_all_analysis_data(self):
        """Test that report includes all required analysis data"""
        # Create idea
        idea_data = {
            "title": "Test Idea",
            "description": "Test"
        }
        create_response = client.post("/api/v1/ideas", json=idea_data)
        idea_id = create_response.json()["id"]
        
        # Get JSON report
        response = client.get(f"/api/v1/ideas/{idea_id}/report/json")
        data = response.json()
        
        analysis = data["analysis"]
        assert "overall_score" in analysis
        assert "market_score" in analysis
        assert "feasibility_score" in analysis
        assert "financial_score" in analysis
        assert "risk_score" in analysis
        assert "market_analysis" in analysis
        assert "recommendations" in analysis
    
    def test_pdf_report_nonexistent_idea(self):
        """Test PDF report for non-existent idea returns 404"""
        response = client.get("/api/v1/ideas/9999/report/pdf")
        assert response.status_code == 404
    
    def test_report_has_professional_formatting(self):
        """Test that JSON report has professional formatting"""
        # Create idea
        idea_data = {
            "title": "Professional Idea",
            "description": "A professional business idea",
            "problem_statement": "Problem",
            "target_market": "Market",
            "proposed_solution": "Solution",
            "value_proposition": "Value",
            "business_model": "Model"
        }
        create_response = client.post("/api/v1/ideas", json=idea_data)
        idea_id = create_response.json()["id"]
        
        response = client.get(f"/api/v1/ideas/{idea_id}/report/json")
        data = response.json()
        
        # Check professional structure
        assert "generated_at" in data
        assert "version" in data
        assert data["version"] == "1.0"
