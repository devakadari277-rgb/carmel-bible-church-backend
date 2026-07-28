@echo off
echo ==========================================
echo   Carmel Bible Church - Startup Script
echo ==========================================

:: Step 1: Check Python installation
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH. Please install Python.
    pause
    exit /b
)

:: Step 2: Check Node.js / npm installation
where npm >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Node.js / npm is not installed or not in PATH. Please install Node.js.
    pause
    exit /b
)

echo [1/4] Installing backend dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt

echo [2/4] Installing frontend dependencies...
cd frontend
call npm install
cd ..

echo [3/4] Running migrations and seeding database...
python manage.py makemigrations
python manage.py migrate
python seed.py

echo [4/4] Starting servers...
echo Starting Django Backend on http://127.0.0.1:8000 ...
start "Django Backend Server" cmd /k "python manage.py runserver 8000"

echo Starting Vite Frontend on http://localhost:5173 ...
cd frontend
start "Vite Frontend Server" cmd /k "npm run dev"
cd ..

echo =========================================================
echo Setup and starting complete!
echo - Frontend: http://localhost:5173
echo - Backend API: http://localhost:8000
echo - Admin panel: http://localhost:8000/admin
echo
echo To expose your frontend via ngrok:
echo Open a new terminal and run:
echo   python -c "from pyngrok import ngrok; tunnel=ngrok.connect(5173); print('Public URL: ' + tunnel.public_url); import time; time.sleep(3600)"
echo =========================================================
pause
