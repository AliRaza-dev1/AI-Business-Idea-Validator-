# Backend - AI Business Idea Validator

This is the FastAPI backend for the AI Business Idea Validator application.

## Project Structure

```
backend/
├── app/
│   ├── api/
│   │   └── routes/
│   │       ├── auth.py       # Authentication endpoints
│   │       ├── ideas.py      # Ideas management endpoints
│   │       └── analysis.py   # Analysis endpoints
│   ├── core/
│   │   ├── config.py         # Configuration settings
│   │   └── security.py       # Security utilities (JWT, password hashing)
│   ├── db/
│   │   └── database.py       # Database connection and session
│   ├── models/
│   │   └── models.py         # SQLAlchemy ORM models
│   ├── schemas/
│   │   └── schemas.py        # Pydantic request/response schemas
│   ├── services/
│   │   └── ai_service.py     # AI analysis service
│   └── main.py               # FastAPI application entry point
├── tests/                     # Unit and integration tests
├── requirements.txt           # Python dependencies
└── .env.example              # Environment variables template
```

## Setup Instructions

### 1. Create Virtual Environment

```bash
cd backend
python -m venv venv

# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
# Copy the example env file
cp .env.example .env

# Edit .env with your settings:
# - DATABASE_URL: PostgreSQL connection string
# - OPENAI_API_KEY: Your OpenAI API key
# - SECRET_KEY: A secure random key for JWT
```

### 4. Setup Database

```bash
# Create PostgreSQL database
createdb ai_validator_db

# Run migrations (migrations setup coming in next phase)
# alembic upgrade head
```

### 5. Run Development Server

```bash
uvicorn app.main:app --reload --port 8000
```

The API will be available at: `http://localhost:8000`

### API Documentation

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login and get token

### Ideas
- `POST /api/v1/ideas/` - Create new idea
- `GET /api/v1/ideas/` - List ideas
- `GET /api/v1/ideas/{idea_id}` - Get specific idea
- `PUT /api/v1/ideas/{idea_id}` - Update idea
- `DELETE /api/v1/ideas/{idea_id}` - Delete idea

### Analysis
- `POST /api/v1/analysis/{idea_id}/analyze` - Trigger analysis
- `GET /api/v1/analysis/{idea_id}` - Get analysis results
- `GET /api/v1/analysis/{idea_id}/report` - Get comprehensive report

## Environment Variables

Create a `.env` file based on `.env.example`:

```env
DATABASE_URL=postgresql://user:password@localhost/ai_validator
OPENAI_API_KEY=sk-...
SECRET_KEY=your-secret-key
DEBUG=False
```

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_auth.py
```

## Database Models

- **User**: User accounts and authentication
- **Idea**: Business ideas submitted by users
- **AnalysisResult**: AI analysis results and scores
- **Recommendation**: Specific recommendations from analysis
- **AuditLog**: Audit trail of user actions

## Features Implemented (Phase 1)

✅ FastAPI application structure
✅ Database models and ORM setup
✅ Authentication (registration, login, JWT)
✅ Ideas CRUD operations
✅ AI analysis service integration
✅ Comprehensive API endpoints
✅ Error handling and validation

## Next Steps (Phase 2)

- [ ] Implement remaining analysis modules
- [ ] Add caching layer
- [ ] Improve error handling
- [ ] Add comprehensive unit tests
- [ ] Create API documentation
