@echo off
REM Start Backend and Frontend

echo ========================================
echo AI Business Idea Validator - Startup Script
echo ========================================
echo.

REM Check if required directories exist
if not exist "backend" (
    echo Error: backend directory not found
    exit /b 1
)

if not exist "frontend" (
    echo Error: frontend directory not found
    exit /b 1
)

REM Start Backend in new window
echo Starting Backend (FastAPI)...
cd backend
start "Backend - FastAPI" cmd /k "python -m venv venv 2>nul || echo Venv exists & venv\Scripts\activate & pip install -r requirements.txt -q & uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
cd ..

REM Wait a bit for backend to start
timeout /t 5 /nobreak

REM Start Frontend in new window
echo Starting Frontend (React)...
cd frontend
start "Frontend - React" cmd /k "npm install 2>nul || echo Packages installed & npm start"
cd ..

echo.
echo ========================================
echo Starting Services:
echo Backend: http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo Frontend: http://localhost:3000
echo ========================================
echo.
echo Press any key to continue...
pause
