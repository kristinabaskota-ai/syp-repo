@echo off
setlocal enabledelayedexpansion

echo ========================================================
echo               RareRoot - Plant Marketplace
echo ========================================================
echo.

cd /d "%~dp0"

:: Check if virtual environment exists
if not exist ".venv" (
    echo [*] Creating Python virtual environment in .venv ...
    python -m venv .venv
    if errorlevel 1 (
        echo [!] Error creating virtual environment. Please ensure Python 3.12+ is installed.
        pause
        exit /b 1
    )
)

:: Activate virtual environment
call .venv\Scripts\activate.bat

:: Copy .env if not present
if not exist "backend\.env" (
    echo [*] Setting up environment configuration from .env.example ...
    copy "backend\.env.example" "backend\.env" >nul
)

:: Install dependencies
echo [*] Installing / verifying backend dependencies ...
python -m pip install --upgrade pip --quiet
python -m pip install -r backend\requirements.txt --quiet

:: Open default browser after a brief delay in the background
start "" cmd /c "timeout /t 3 /nobreak >nul & start http://127.0.0.1:8000/app/index.html"

:: Start the application server
echo [*] Starting RareRoot server at http://127.0.0.1:8000 ...
echo [*] Press Ctrl+C to stop the server.
echo.

cd backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

pause
