#!/bin/bash
# Start Backend and Frontend

echo "========================================"
echo "AI Business Idea Validator - Startup Script"
echo "========================================"
echo ""

# Check directories
if [ ! -d "backend" ]; then
    echo "Error: backend directory not found"
    exit 1
fi

if [ ! -d "frontend" ]; then
    echo "Error: frontend directory not found"
    exit 1
fi

# Start Backend
echo "Starting Backend (FastAPI)..."
cd backend
python -m venv venv 2>/dev/null || echo "Venv exists"
source venv/bin/activate
pip install -q -r requirements.txt 2>/dev/null || echo "Dependencies installed"
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd ..

# Wait for backend
sleep 5

# Start Frontend
echo "Starting Frontend (React)..."
cd frontend
npm install 2>/dev/null || echo "Packages installed"
npm start &
FRONTEND_PID=$!
cd ..

echo ""
echo "========================================"
echo "Starting Services:"
echo "Backend: http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"
echo "Frontend: http://localhost:3000"
echo "========================================"
echo ""

wait
