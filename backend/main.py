import threading
import logging
import asyncio
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware

# Core Logic Imports
from core.scanner import scan_system
from core.quarantine import restore_file
from core.usb_monitor import monitor_usb_with_callback
from api.api_routes import router # Assuming you still want your modular routes

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Hornet Defence API")

# 1. Middleware (Critical for React communication)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. WebSocket Connection Manager
clients = []

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.append(websocket)
    logger.info(f"Client connected to WebSocket. Total clients: {len(clients)}")
    try:
        while True:
            # Keep the connection alive
            await websocket.receive_text()
    except Exception:
        clients.remove(websocket)
        logger.info("Client disconnected from WebSocket.")

async def broadcast(data):
    for client in clients:
        try:
            await client.send_json(data)
        except Exception as e:
            logger.error(f"Broadcast error: {e}")

# 3. HTTP Endpoints (Scan & Restore)
@app.get("/scan")
def run_scan(background_tasks: BackgroundTasks):
    # This fires and forgets, so the UI stays alive
    background_tasks.add_task(scan_system)
    return {"status": "started", "message": "Scan is running in background"}

@app.post("/restore")
def run_restore(item: dict):
    """
    Expects: {"quarantined_path": "...", "original_path": "..."}
    """
    result = restore_file(item["quarantined_path"], item["original_path"])
    return result

# 4. Background USB Monitor Logic
def start_usb_monitor():
    # Create a new event loop for this specific thread to handle broadcasts
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    def callback(results):
        logger.info(f"[USB Event] Detected potential threats: {len(results)}")
        loop.run_until_complete(broadcast({
            "type": "usb_scan",
            "results": results
        }))

    # This function should contain the 'while True' loop for hardware monitoring
    monitor_usb_with_callback(callback)

@app.on_event("startup")
def startup():
    logger.info("Initializing Hornet Defence background services...")
    thread = threading.Thread(target=start_usb_monitor, daemon=True)
    thread.start()
