#!/usr/bin/env bash
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

echo "========================================================"
echo "              RareRoot - Plant Marketplace              "
echo "========================================================"
echo ""

# Create virtualenv if not exists
if [ ! -d ".venv" ]; then
    echo "[*] Creating virtual environment (.venv)..."
    python3 -m venv .venv
fi

# Activate virtualenv
source .venv/bin/activate

# Copy .env if not exists
if [ ! -f "backend/.env" ]; then
    echo "[*] Copying backend/.env.example to backend/.env..."
    cp backend/.env.example backend/.env
fi

# Install dependencies
echo "[*] Installing backend dependencies..."
pip install --upgrade pip --quiet
pip install -r backend/requirements.txt --quiet

# Open browser in background
(sleep 2 && (xdg-open http://127.0.0.1:8000/app/index.html || open http://127.0.0.1:8000/app/index.html || true)) &

# Run server
echo "[*] Starting FastAPI server on http://127.0.0.1:8000..."
cd backend
python3 -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
