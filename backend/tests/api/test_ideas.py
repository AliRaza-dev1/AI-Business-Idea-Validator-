import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.database import Base, get_db
from app.main import app
from app.models.models import User

# Test database setup
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test_ideas.db"
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


class TestIdeasAPI:
    """Test cases for Ideas API endpoints"""
    
    def setup_method(self):
        """Setup before each test"""
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
    
    def test_create_idea_success(self):
        """Test successful idea creation"""
        idea_data = {
            "title": "AI Email Manager",
            "description": "Automated email management with AI",
            "problem_statement": "Email overload",
            "target_market": "Business professionals",
            "proposed_solution": "AI-powered email filtering",
            "value_proposition": "Save 2 hours daily on emails",
            "business_model": "SaaS Subscription"
        }
        response = client.post("/api/v1/ideas", json=idea_data)
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "AI Email Manager"
        assert data["id"] == 1
    
    def test_create_idea_missing_required_field(self):
        """Test idea creation with missing required field"""
        idea_data = {
            "description": "Automated email management",
            # Missing 'title'
        }
        response = client.post("/api/v1/ideas", json=idea_data)
        assert response.status_code == 422  # Validation error
    
    def test_get_idea_success(self):
        """Test retrieving an idea"""
        # First create an idea
        idea_data = {
            "title": "Test Idea",
            "description": "Test description"
        }
        create_response = client.post("/api/v1/ideas", json=idea_data)
        idea_id = create_response.json()["id"]
        
        # Then retrieve it
        response = client.get(f"/api/v1/ideas/{idea_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Test Idea"
    
    def test_get_nonexistent_idea(self):
        """Test retrieving non-existent idea"""
        response = client.get("/api/v1/ideas/9999")
        assert response.status_code == 404
    
    def test_list_ideas(self):
        """Test listing all ideas"""
        # Create multiple ideas
        for i in range(3):
            idea_data = {
                "title": f"Idea {i+1}",
                "description": f"Description {i+1}"
            }
            client.post("/api/v1/ideas", json=idea_data)
        
        response = client.get("/api/v1/ideas")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 3
    
    def test_update_idea_success(self):
        """Test updating an idea"""
        # Create idea
        idea_data = {
            "title": "Original Title",
            "description": "Original description"
        }
        create_response = client.post("/api/v1/ideas", json=idea_data)
        idea_id = create_response.json()["id"]
        
        # Update it
        update_data = {
            "title": "Updated Title"
        }
        response = client.put(f"/api/v1/ideas/{idea_id}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"
    
    def test_delete_idea_success(self):
        """Test deleting an idea"""
        # Create idea
        idea_data = {
            "title": "To Delete",
            "description": "This will be deleted"
        }
        create_response = client.post("/api/v1/ideas", json=idea_data)
        idea_id = create_response.json()["id"]
        
        # Delete it
        response = client.delete(f"/api/v1/ideas/{idea_id}")
        assert response.status_code == 204  # No Content is correct for DELETE
        
        # Verify it's deleted
        get_response = client.get(f"/api/v1/ideas/{idea_id}")
        assert get_response.status_code == 404
