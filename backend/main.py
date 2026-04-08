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
from core.memory import learn_trust  # NEW: Agent Learning

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Hornet Defence API")

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
    # Give a welcome message from the system
    await websocket.send_json({"type": "agent_msg", "text": "🛡️ [SYSTEM]: SWAT Agents online. Uplink secure."})
    try:
        while True: await websocket.receive_text()
    except:
        clients.remove(websocket)

async def broadcast(data):
    for client in clients:
        try: await client.send_json(data)
        except: continue

# NEW: Tactical Agent Reporting Logic
async def agent_report(agent, message):
    icons = {"VANGUARD": "📡", "INTERCEPTOR": "⚔️", "WARDEN": "🔒"}
    await broadcast({
        "type": "agent_msg",
        "text": f"{icons.get(agent, '🤖')} [{agent}]: {message}"
    })

# 2. ENDPOINTS
@app.get("/scan")
async def run_scan(background_tasks: BackgroundTasks):
    await agent_report("INTERCEPTOR", "Initiating area sweep. Standby for signature analysis.")
    background_tasks.add_task(scan_system, broadcast_func=agent_report) 
    return {"status": "started"}

@app.post("/restore")
async def run_restore(item: dict):
    # Agent Learning: Warden tells the memory to trust this hash
    if "file_hash" in item:
        learn_trust(item["file_hash"])
    
    await agent_report("WARDEN", f"User override detected. Restoring target and updating memory signatures.")
    return restore_file(item["quarantined_path"], item["original_path"])

@app.post("/delete-quarantine")
async def run_delete(item: dict):
    await agent_report("WARDEN", "Neutralizing threat permanently. Clearing vault space.")
    return delete_quarantined_file(item["quarantined_path"])

# 3. USB MONITOR
def start_usb_monitor():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    def callback(results):
        # Vanguard reports the breach
        loop.run_until_complete(agent_report("VANGUARD", "Perimeter breach! Removable drive detected. Intercepting data..."))
        loop.run_until_complete(broadcast({"type": "usb_scan", "results": results}))
    
    monitor_usb_with_callback(callback)

@app.on_event("startup")
def startup():
    thread = threading.Thread(target=start_usb_monitor, daemon=True)
    thread.start()
