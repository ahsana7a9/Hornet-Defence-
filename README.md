<p align="center">
  <img src="https://raw.githubusercontent.com/ahsana7a9/Hornet-Defence-/main/assets/logo.png" width="300" alt="Hornet-Defence Logo">
</p>

<h1 align="center">Hornet-Defence</h1>

<p align="center">
  <strong>The Self-Learning Cyber Swarm</strong><br>
  <em>Powered by MARL and Llama3 Intelligence</em>
</p>


# Hornet-Defence 

A distributed cybersecurity defense and monitoring system using swarm intelligence. Independent AI agents (ReconAgent, BruteAgent) detect anomalies in real time, coordinate via Redis, log to Elasticsearch, and visualize the swarm topology on a live dashboard.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 19, Vite 8, Canvas API |
| Backend | Python 3.12, FastAPI, Uvicorn |
| AI/ML | scikit-learn (IsolationForest) |
| Messaging | Redis (Pub/Sub) — optional |
| Storage | Elasticsearch 8 — optional, falls back to in-memory |
| Auth | JWT via python-jose |
| Container | Docker + docker-compose |

---

## Quick Start

### Option 1 — One Command (Linux/macOS) 
## License & Usage

This project is proprietary software.

You are NOT allowed to:
- Copy the code
- Modify the code
- Reuse any part of it
- Distribute it

Without explicit permission from the author.

```bash
chmod +x run.sh
./run.sh
```

Installs all dependencies, creates `.env` from `.env.example`, and starts both services.

### Option 2 — Docker (Full Stack incl. Redis & Elasticsearch)

```bash
docker-compose up --build
```

| Service | URL |
|---------|-----|
| Frontend | http://localhost:5000 |
| Backend API | http://localhost:8000 |
| API Docs (Swagger) | http://localhost:8000/docs |
| Redis | localhost:6379 |
| Elasticsearch | localhost:9200 |

### Option 3 — Manual

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --host localhost --port 8000 --reload

# Frontend (separate terminal)
cd frontend
npm install
npm run dev
```

---

## Environment Variables

Copy `.env.example` to `.env` and edit before going to production:

```env
JWT_SECRET=change_this_to_a_random_secret_in_production
ELASTICSEARCH_URL=http://localhost:9200
REDIS_HOST=localhost
REDIS_PORT=6379
VITE_API_URL=/api
```

> Redis and Elasticsearch are **optional**. The system falls back gracefully to in-memory storage when they are unavailable.

---

## Project Structure

```
.
├── backend/
│   ├── agents/
│   │   ├── recon_agent.py          # Reconnaissance agent
│   │   └── brute_agent.py          # Brute-force detection agent
│   ├── ai/
│   │   └── anomaly_model.py        # IsolationForest anomaly detection
│   ├── api/
│   │   ├── api_routes.py           # FastAPI routes
│   │   └── api_auth.py             # JWT token generation
│   ├── core/
│   │   ├── swarm_engine.py         # Swarm orchestration loop
│   │   ├── agent_manager.py        # Agent lifecycle management
│   │   ├── agent_listener.py       # Redis Pub/Sub listener (optional)
│   │   ├── anomaly_detector.py     # Detection gateway
│   │   ├── pheromone_system.py     # Local threat tagging
│   │   ├── redis_client.py         # Redis wrapper (graceful fallback)
│   │   ├── elasticsearch_client.py # ES wrapper (graceful fallback)
│   │   ├── auth.py                 # JWT verification middleware
│   │   └── websocket.py            # Socket.IO (optional)
│   ├── main.py                     # FastAPI entrypoint
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   └── SwarmGraph.jsx      # Animated Canvas swarm topology
│   │   ├── pages/
│   │   │   └── dashboard.jsx       # Command center UI
│   │   ├── services/
│   │   │   └── api.js              # Backend API client
│   │   └── App.jsx
│   ├── vite.config.js
│   ├── package.json
│   └── dockerfile
├── docker-compose.yml
├── run.sh                          # One-command launcher
├── .env.example
└── README.md
```

---

## API Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/` | No | Root / health check |
| GET | `/health` | No | Health status |
| GET | `/api/status` | No | System status |
| GET | `/api/logs/public` | No | Recent threats (no auth) |
| GET | `/api/logs` | Bearer JWT | Recent threats (secured) |
| GET | `/api/secure` | Bearer JWT | Auth test endpoint |
| POST | `/api/auth/token` | No | Generate a JWT token |
| GET | `/docs` | No | Swagger UI |

---

## How It Works

1. **Swarm Engine** runs a loop every 2 seconds cycling through all agents
2. Each **Agent** collects simulated network data (recon patterns, brute-force signals)
3. The **IsolationForest** ML model scores each data point for anomalies
4. On threat detection:
   - **Pheromone System** tags the source locally
   - **Redis** broadcasts the threat to all peer agents (if available)
   - **Elasticsearch** (or in-memory) logs the event persistently
5. The **Dashboard** polls `/api/logs/public` every 5 seconds and renders a live animated swarm topology

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Port 5000 in use | `lsof -ti:5000 \| xargs kill` |
| Port 8000 in use | `lsof -ti:8000 \| xargs kill` |
| Redis warnings in logs | Normal — Redis is optional. Use Docker to enable Pub/Sub |
| Elasticsearch warnings | Normal — ES is optional. Use Docker for full persistence |
| `ModuleNotFoundError` | `pip install -r backend/requirements.txt` |
| Frontend shows no threats | Backend may not be running — check port 8000 |

---

## Security

- Change `JWT_SECRET` in `.env` before any production deployment
- The default secret is intentionally weak for development only
- `.env` is in `.gitignore` — never commit it
