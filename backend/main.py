import threading
import logging
import asyncio
import ctypes
from fastapi import FastAPI, WebSocket, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware

# Core Logic Imports
from core.scanner import scan_system
from core.quarantine import restore_file, delete_quarantined_file
from core.usb_monitor import monitor_usb_with_callback

# 0. ADMIN CHECK
def is_admin():
    try: return ctypes.windll.shell32.IsUserAnAdmin()
    except: return False

if not is_admin():
    print("⚠️ WARNING: Not running as Administrator. Quarantine will fail.")

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Hornet Defence API")

# 1. CORS Middleware (Allow React on port 3000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

clients = []

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.append(websocket)
    try:
        while True: await websocket.receive_text()
    except:
        clients.remove(websocket)

async def broadcast(data):
    for client in clients:
        try: await client.send_json(data)
        except: continue

# 2. ENDPOINTS
@app.get("/scan")
async def run_scan(background_tasks: BackgroundTasks):
    # We trigger the scan in the background so the API responds immediately
    # In a real app, you'd send results back via WebSocket as they are found
    background_tasks.add_task(scan_system) 
    return {"status": "started"}

@app.post("/restore")
def run_restore(item: dict):
    return restore_file(item["quarantined_path"], item["original_path"])

@app.post("/delete-quarantine")
def run_delete(item: dict):
    return delete_quarantined_file(item["quarantined_path"])

# 3. USB MONITOR
def start_usb_monitor():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    def callback(results):
        loop.run_until_complete(broadcast({"type": "usb_scan", "results": results}))
    monitor_usb_with_callback(callback)

@app.on_event("startup")
def startup():
    thread = threading.Thread(target=start_usb_monitor, daemon=True)
    thread.start()
