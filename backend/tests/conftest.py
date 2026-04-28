"""
conftest.py — Shared pytest fixtures for all backend test files.
Uses an in-memory SQLite database so tests are fully isolated and do not
touch the real test.db file.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db.database import Base, get_db
from app.models.models import User, Idea, AnalysisResult, Recommendation
from app.core.security import hash_password

# ── In-memory SQLite (separate DB per test session) ──────────────────────────
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_unit.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def create_tables():
    """Create all tables once per test session, drop afterwards."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def db():
    """Provide a transactional DB session that rolls back after each test."""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture()
def client(db):
    """FastAPI TestClient with the test DB injected via dependency override."""
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


# ── Helper to seed common data ────────────────────────────────────────────────

@pytest.fixture()
def test_user(db):
    """Create and return a test user."""
    user = User(
        email="test@example.com",
        password_hash=hash_password("TestPassword123!"),
        full_name="Test User",
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture()
def inactive_user(db):
    """Create and return an inactive test user."""
    user = User(
        email="inactive@example.com",
        password_hash=hash_password("TestPassword123!"),
        full_name="Inactive User",
        is_active=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture()
def test_idea(db, test_user):
    """Create and return a test idea linked to test_user."""
    idea = Idea(
        user_id=test_user.id,
        title="AI Email Manager",
        description="Intelligent email management using AI",
        problem_statement="Email overload",
        target_market="Corporate professionals",
        proposed_solution="AI-powered categorization",
        value_proposition="Save 2+ hours daily",
        business_model="Freemium SaaS",
        status="pending",
    )
    db.add(idea)
    db.commit()
    db.refresh(idea)
    return idea


@pytest.fixture()
def test_analysis(db, test_idea):
    """Create and return an analysis result for test_idea."""
    result = AnalysisResult(
        idea_id=test_idea.id,
        market_score=8.5,
        feasibility_score=7.8,
        financial_score=8.2,
        risk_score=6.5,
        overall_score=7.75,
        market_analysis="Strong market potential.",
        feasibility_analysis="Technically feasible.",
        financial_analysis="Good unit economics.",
        risk_analysis="Moderate risk.",
        competitive_analysis="Fragmented market.",
        strengths="Large TAM",
        weaknesses="Competitive landscape",
    )
    db.add(result)
    db.commit()
    db.refresh(result)
    return result


# ── Reusable idea payload ─────────────────────────────────────────────────────

IDEA_PAYLOAD = {
    "title": "Smart Delivery App",
    "description": "AI-optimized last-mile delivery platform",
    "problem_statement": "Slow and expensive deliveries",
    "target_market": "E-commerce retailers",
    "proposed_solution": "Route optimization with ML",
    "value_proposition": "30% cost reduction in delivery",
    "business_model": "Subscription SaaS",
}
