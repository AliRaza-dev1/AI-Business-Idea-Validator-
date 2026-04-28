@echo off
REM Run Backend and Frontend Unit Tests

echo ========================================
echo AI Business Idea Validator - Test Runner
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

echo ========================================
echo [1/2] Running Backend Unit Tests (Pytest)
echo ========================================
cd backend
REM Execute the backend test suite directly in the console
call .\venv\Scripts\pytest tests/ -v
if %errorlevel% neq 0 (
    echo.
    echo [X] Backend tests encountered an error!
) else (
    echo.
    echo [~] All Backend tests passed!
)
cd ..

echo.
echo ========================================
echo [2/2] Running Frontend Unit Tests (Jest)
echo ========================================
cd frontend
REM Set CI=true so it runs as a standard test suite instead of interactive watch mode
set CI=true
call npx react-scripts test --watchAll=false
if %errorlevel% neq 0 (
    echo.
    echo [X] Frontend tests encountered an error!
) else (
    echo.
    echo [~] All Frontend tests passed!
)
cd ..

echo.
echo ========================================
echo All Testing Processes Completed!
echo ========================================
echo Press any key to exit...
pause
