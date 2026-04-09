#!/usr/bin/env bash
set -e

echo "============================================"
echo "  🐝 Hornet Defence — One-Command Start"
echo "============================================"

# ── Check prerequisites ─────────────────────────
command -v python3 >/dev/null 2>&1 || { echo "❌ Python3 is not installed"; exit 1; }
command -v npm >/dev/null 2>&1 || { echo "❌ Node.js/npm is not installed"; exit 1; }

# ── Backend setup ──────────────────────────────
echo ""
echo ">>> Installing Python dependencies..."
cd backend || exit
pip install -r requirements.txt -q
cd ..

# ── Frontend setup ─────────────────────────────
echo ""
echo ">>> Installing Node.js dependencies..."
cd frontend || exit
npm install --silent
cd ..

# ── Environment ────────────────────────────────
if [ ! -f .env ]; then
  cp .env.example .env
  echo ">>> Created .env from .env.example (⚠️ edit before production)"
fi

# ── Start services ─────────────────────────────
echo ""
echo ">>> Starting backend (FastAPI) on port 8000..."
cd backend || exit
uvicorn main:app --host 127.0.0.1 --port 8000 --reload &
BACKEND_PID=$!
cd ..

echo ">>> Starting frontend (Vite) on port 5173..."
cd frontend || exit
npm run dev &
FRONTEND_PID=$!
cd ..

# ── Info ───────────────────────────────────────
echo ""
echo "============================================"
echo "  Backend  : http://127.0.0.1:8000"
echo "  Frontend : http://localhost:5173"
echo "  API Docs : http://127.0.0.1:8000/docs"
echo "============================================"
echo ""
echo "Press Ctrl+C to stop all services"

# ── Cleanup on exit ────────────────────────────
cleanup() {
  echo ""
  echo ">>> Stopping services..."
  kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
  echo "✅ All services stopped."
  exit 0
}

trap cleanup INT TERM
wait