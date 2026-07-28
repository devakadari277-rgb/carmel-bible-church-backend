#!/bin/bash
echo "=========================================="
echo "  Carmel Bible Church - Startup Script"
echo "=========================================="

# Check Python
if ! command -v python3 &> /dev/null
then
    echo "[ERROR] Python3 is not installed. Please install Python."
    exit 1
fi

# Check npm
if ! command -v npm &> /dev/null
then
    echo "[ERROR] npm is not installed. Please install Node.js."
    exit 1
fi

echo "[1/4] Installing backend dependencies..."
python3 -m pip install --upgrade pip
pip3 install -r requirements.txt

echo "[2/4] Installing frontend dependencies..."
cd frontend
npm install
cd ..

echo "[3/4] Running migrations and seeding database..."
python3 manage.py makemigrations
python3 manage.py migrate
python3 seed.py

echo "[4/4] Starting servers..."
echo "Starting Django Backend on http://127.0.0.1:8000 ..."
python3 manage.py runserver 8000 &
BACKEND_PID=$!

echo "Starting Vite Frontend on http://localhost:5173 ..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo "========================================================="
echo "Setup and starting complete!"
echo "- Frontend: http://localhost:5173"
echo "- Backend API: http://127.0.0.1:8000"
echo "- Admin panel: http://127.0.0.1:8000/admin"
echo ""
echo "Press Ctrl+C to stop both servers."
echo "========================================================="

# Handle shutdown gracefully
cleanup() {
    echo "Stopping servers..."
    kill $BACKEND_PID
    kill $FRONTEND_PID
    exit 0
}

trap cleanup SIGINT SIGTERM

# Keep the script running
wait
