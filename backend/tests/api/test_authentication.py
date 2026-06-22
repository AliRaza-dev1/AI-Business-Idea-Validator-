import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.database import Base, get_db
from app.main import app

SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test_auth.db"
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


class TestUserAuthentication:
    """Test cases for user registration and authentication"""
    
    def setup_method(self):
        """Setup before each test"""
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
    
    def test_user_registration(self):
        """Test user can register"""
        user_data = {
            "email": "user@example.com",
            "password": "SecurePassword123!",
            "full_name": "Test User"
        }
        response = client.post("/api/v1/auth/register", json=user_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "user@example.com"
        assert "id" in data
        assert data["full_name"] == "Test User"
    
    def test_user_registration_duplicate_email(self):
        """Test cannot register with same email twice"""
        user_data = {
            "email": "user@example.com",
            "password": "SecurePassword123!",
            "full_name": "Test User"
        }
        
        # First registration
        client.post("/api/v1/auth/register", json=user_data)
        
        # Second registration with same email
        response = client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()
    
    def test_user_registration_invalid_email(self):
        """Test registration with invalid email fails"""
        user_data = {
            "email": "not-an-email",
            "password": "SecurePassword123!",
            "full_name": "Test User"
        }
        response = client.post("/api/v1/auth/register", json=user_data)
        
        assert response.status_code == 422
    
    def test_user_login(self):
        """Test user can login"""
        # Register first
        user_data = {
            "email": "user@example.com",
            "password": "SecurePassword123!",
            "full_name": "Test User"
        }
        client.post("/api/v1/auth/register", json=user_data)
        
        # Login
        login_data = {
            "email": "user@example.com",
            "password": "SecurePassword123!"
        }
        response = client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "user" in data
    
    def test_user_login_wrong_password(self):
        """Test login fails with wrong password"""
        # Register
        user_data = {
            "email": "user@example.com",
            "password": "SecurePassword123!",
            "full_name": "Test User"
        }
        client.post("/api/v1/auth/register", json=user_data)
        
        # Login with wrong password
        login_data = {
            "email": "user@example.com",
            "password": "WrongPassword"
        }
        response = client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == 401
        assert "Invalid credentials" in response.json()["detail"]
    
    def test_user_login_nonexistent_email(self):
        """Test login fails with non-existent email"""
        login_data = {
            "email": "nonexistent@example.com",
            "password": "AnyPassword"
        }
        response = client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == 401
    
    def test_get_current_user_with_token(self):
        """Test can get current user with valid token"""
        # Register and login
        user_data = {
            "email": "user@example.com",
            "password": "SecurePassword123!",
            "full_name": "Test User"
        }
        client.post("/api/v1/auth/register", json=user_data)
        
        login_response = client.post("/api/v1/auth/login", json={
            "email": "user@example.com",
            "password": "SecurePassword123!"
        })
        token = login_response.json()["access_token"]
        
        # Get current user
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/api/v1/auth/me", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "user@example.com"
    
    def test_get_current_user_without_token(self):
        """Test cannot get user without token"""
        response = client.get("/api/v1/auth/me")
        
        assert response.status_code == 403
