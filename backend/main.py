from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.api_routes import router
from core.swarm_engine import SwarmEngine
import threading
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="ShadowMesh API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")

@app.get("/")
def root():
    return {"message": "ShadowMesh is running", "status": "operational"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.on_event("startup")
def startup_event():
    def delayed_swarm():
        import time
        time.sleep(3)
        logger.info("[ShadowMesh] Starting swarm engine...")
        try:
            swarm = SwarmEngine()
            swarm.run()
        except Exception as e:
            logger.error(f"[Swarm] Engine stopped: {e}")

    thread = threading.Thread(target=delayed_swarm, daemon=True)
    thread.start()
    logger.info("[ShadowMesh] API started — swarm engine will begin in 3 seconds")
