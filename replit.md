# ShadowMesh / Hornet — Replit Project

## Project Overview

A distributed cybersecurity defense and monitoring system using swarm intelligence. Independent AI agents detect anomalies in real time, coordinate via Redis pub/sub, and visualize the swarm topology on a live dashboard.

## Architecture

- **Frontend**: React 19 + Vite 8, on port 5000
- **Backend**: Python 3.12 + FastAPI + Uvicorn, on port 8000
- **AI/ML**: scikit-learn IsolationForest (lazy-loaded after startup)
- **Messaging**: Redis pub/sub (optional — graceful fallback to no-op)
- **Storage**: Elasticsearch (optional — graceful fallback to in-memory)
- **Auth**: JWT via python-jose

## Folder Structure

```
backend/
  agents/       # ReconAgent, BruteAgent (simulate network data collection)
  ai/           # IsolationForest anomaly model (lazy-loaded)
  api/          # FastAPI routes + JWT auth endpoint
  core/         # SwarmEngine, AgentManager, Pheromone, Redis/ES clients
  main.py       # FastAPI app entrypoint
  requirements.txt

frontend/
  src/
    components/ # SwarmGraph.jsx (animated Canvas topology)
    pages/      # Dashboard (command center)
    services/   # api.js (backend client, uses /api proxy)
  vite.config.js  # port 5000, host 0.0.0.0, /api proxy to 8000
```

## Workflows

- **Start application** — `cd frontend && npm run dev` → port 5000 (webview)
- **Backend API** — `cd backend && uvicorn main:app --host localhost --port 8000` → port 8000 (console)

## Key Design Decisions

1. **Lazy model loading**: IsolationForest trains on first prediction call, not at import, so uvicorn starts and binds port 8000 in ~1s
2. **Graceful fallbacks**: Redis and Elasticsearch are both optional — the system logs in-memory and skips pub/sub if unavailable
3. **One-check ES**: `elasticsearch_client.py` uses `max_retries=0` and checks once; subsequent calls use a cached result
4. **Vite proxy**: Frontend proxies `/api/*` to `http://localhost:8000` so there are no CORS issues in dev
5. **Swarm engine delay**: SwarmEngine starts 3 seconds after FastAPI startup to allow the HTTP server to bind first

## Running Locally (One Command)

```bash
./run.sh
```

## Docker

```bash
docker-compose up --build
```

## Important Files

- `backend/main.py` — FastAPI app entry, delayed swarm start
- `backend/core/swarm_engine.py` — Main agent loop
- `backend/ai/anomaly_model.py` — IsolationForest (lazy)
- `backend/core/elasticsearch_client.py` — ES with in-memory fallback
- `frontend/vite.config.js` — Port 5000, allowedHosts: true, /api proxy
- `.env.example` — Environment variable template
