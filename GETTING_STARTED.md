# AI Business Idea Validator - Getting Started Guide

## Quick Start

### Option 1: Automatic Startup (Windows)

```bash
# Double-click start.bat or run:
start.bat
```

This will automatically:
1. Start the backend (FastAPI) on port 8000
2. Start the frontend (React) on port 3000

### Option 2: Automatic Startup (Mac/Linux)

```bash
chmod +x start.sh
./start.sh
```

### Option 3: Manual Startup

#### Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment (if not exists)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env with your OpenAI API key and database settings

# Create database (PostgreSQL must be running)
createdb ai_validator_db

# Run backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at: `http://localhost:8000`
API Documentation: `http://localhost:8000/docs`

#### Frontend Setup (in new terminal)

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

Frontend will be available at: `http://localhost:3000`

---

## Prerequisites

### For Backend
- Python 3.8+
- PostgreSQL (or any SQL database)
- OpenAI API key

### For Frontend
- Node.js 14+
- npm

---

## Architecture

```
┌─────────────────────────────────┐
│     Frontend (React)            │
│     http://localhost:3000       │
└────────────────┬────────────────┘
                 │
                 │ HTTP/REST
                 ▼
┌─────────────────────────────────┐
│   Backend API (FastAPI)         │
│   http://localhost:8000         │
│   /api/v1/...                   │
└────────────────┬────────────────┘
                 │
    ┌────────────┼────────────┐
    │            │            │
    ▼            ▼            ▼
┌────────┐  ┌──────────┐  ┌─────────────┐
│  DB    │  │  AI      │  │  External   │
│ (PostgreSQL)  │(OpenAI) │  │  Services   │
└────────┘  └──────────┘  └─────────────┘
```

---

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register user
- `POST /api/v1/auth/login` - Login user

### Ideas
- `POST /api/v1/ideas/` - Create idea
- `GET /api/v1/ideas/` - List ideas
- `GET /api/v1/ideas/{id}` - Get idea
- `PUT /api/v1/ideas/{id}` - Update idea
- `DELETE /api/v1/ideas/{id}` - Delete idea

### Analysis
- `POST /api/v1/analysis/{idea_id}/analyze` - Trigger analysis
- `GET /api/v1/analysis/{idea_id}` - Get analysis results
- `GET /api/v1/analysis/{idea_id}/report` - Get report

---

## Environment Configuration

### Backend (.env)

```
# Database
DATABASE_URL=postgresql://user:password@localhost/ai_validator_db

# OpenAI
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4
OPENAI_TEMPERATURE=0.7
OPENAI_MAX_TOKENS=2000

# Security
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Server
DEBUG=True
ENVIRONMENT=development
```

---

## Features

✅ AI-powered business idea analysis
✅ Real-time scoring across 5 dimensions
✅ Comprehensive market analysis
✅ Financial projections
✅ Risk assessment
✅ Competitive analysis
✅ Feasibility evaluation
✅ Responsive web interface

---

## Project Phases

- ✅ Phase 1: Backend Infrastructure (100%)
- ✅ Phase 2: Analysis Modules (100%)
- ✅ Phase 3: Frontend Development (100%)
- ⚪ Phase 4: Integration & Testing (Coming)
- ⚪ Phase 5: Deployment (Coming)

---

## Troubleshooting

### Backend Issues

**Port 8000 already in use**
```bash
# Find and kill process on port 8000
# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Mac/Linux:
lsof -i :8000
kill -9 <PID>
```

**Database connection error**
- Ensure PostgreSQL is running
- Check DATABASE_URL in .env
- Verify database exists: `psql -l`

**OpenAI API error**
- Verify OPENAI_API_KEY is set
- Check API key is valid
- Monitor API usage and limits

### Frontend Issues

**Port 3000 already in use**
```bash
# Windows:
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# Mac/Linux:
lsof -i :3000
kill -9 <PID>
```

**npm install issues**
```bash
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

---

## Development

### Backend Development
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload
```

### Frontend Development
```bash
cd frontend
npm start
```

Both run in hot-reload mode during development.

---

## Production Deployment

See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for:
- Docker containerization
- Cloud deployment (AWS/GCP/Azure)
- CI/CD pipeline setup
- Performance optimization

---

## Support & Documentation

- Backend API Docs: `http://localhost:8000/docs`
- Frontend README: [frontend/README.md](frontend/README.md)
- Backend README: [backend/README.md](backend/README.md)
- Project Plan: [PROJECT_PLAN.md](PROJECT_PLAN.md)

---

**Ready to validate business ideas with AI! 🚀**

Date: April 14, 2026
Version: 1.0.0
