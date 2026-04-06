from fastapi import FastAPI
from api.routes import router
from core.swarm_engine import SwarmEngine
import threading

app = FastAPI(title="ShadowMesh API")

# Include API routes
app.include_router(router)

# Initialize swarm engine
swarm = SwarmEngine()

# Run swarm in background
def start_swarm():
    swarm.run()

@app.on_event("startup")
def startup_event():
    thread = threading.Thread(target=start_swarm, daemon=True)
    thread.start()

@app.get("/")
def root():
    return {"message": "ShadowMesh is running"}