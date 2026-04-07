#!/usr/bin/env bash
set -e

echo "============================================"
echo "  ShadowMesh / Hornet — One-Command Start"
echo "============================================"

# ── Backend setup ──────────────────────────────
echo ""
echo ">>> Installing Python dependencies..."
cd backend
pip install -r requirements.txt -q
cd ..

# ── Frontend setup ─────────────────────────────
echo ""
echo ">>> Installing Node.js dependencies..."
cd frontend
npm install --silent
cd ..

# ── Environment ────────────────────────────────
if [ ! -f .env ]; then
  cp .env.example .env
  echo ">>> Created .env from .env.example (edit secrets before production use)"
fi

# ── Start services ─────────────────────────────
echo ""
echo ">>> Starting backend on port 8000..."
cd backend
uvicorn main:app --host localhost --port 8000 --reload &
BACKEND_PID=$!
cd ..

echo ">>> Starting frontend on port 5000..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "============================================"
echo "  Backend  : http://localhost:8000"
echo "  Frontend : http://localhost:5000"
echo "  API Docs : http://localhost:8000/docs"
echo "============================================"
echo ""
echo "Press Ctrl+C to stop all services"

trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; echo 'Stopped.'" INT TERM
wait
