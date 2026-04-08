import threading
import logging
import asyncio
import ctypes
import uvicorn
import sys
from fastapi import FastAPI, WebSocket, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware

# Core Logic Imports
from core.scanner import scan_system
from core.quarantine import restore_file, delete_quarantined_file
from core.usb_monitor import monitor_usb_with_callback
from core.memory import learn_trust
from tray_app import create_tray_icon  # NEW: Tray logic

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Hornet Defence API")

# Global stop event to shut down all threads gracefully
stop_event = threading.Event()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

clients = []

# --- AGENT LOGIC ---
async def broadcast(data):
    for client in clients:
        try: await client.send_json(data)
        except: continue

async def agent_report(agent, message):
    icons = {"VANGUARD": "📡", "INTERCEPTOR": "⚔️", "WARDEN": "🔒"}
    await broadcast({
        "type": "agent_msg",
        "text": f"{icons.get(agent, '🤖')} [{agent}]: {message}"
    })

# --- WEBSOCKET & ENDPOINTS ---
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.append(websocket)
    await websocket.send_json({"type": "agent_msg", "text": "🛡️ [SYSTEM]: SWAT Agents online. Uplink secure."})
    try:
        while not stop_event.is_set():
            # Minimal timeout to keep loop responsive to stop_event
            await asyncio.wait_for(websocket.receive_text(), timeout=1.0)
    except:
        pass
    finally:
        clients.remove(websocket)

@app.get("/scan")
async def run_scan(background_tasks: BackgroundTasks):
    await agent_report("INTERCEPTOR", "Initiating area sweep. Standby for signature analysis.")
    background_tasks.add_task(scan_system, broadcast_func=agent_report) 
    return {"status": "started"}

@app.post("/restore")
async def run_restore(item: dict):
    if "file_hash" in item:
        learn_trust(item["file_hash"])
    await agent_report("WARDEN", f"User override detected. Restoring target and updating memory.")
    return restore_file(item["quarantined_path"], item["original_path"])

@app.post("/delete-quarantine")
async def run_delete(item: dict):
    await agent_report("WARDEN", "Neutralizing threat permanently. Clearing vault space.")
    return delete_quarantined_file(item["quarantined_path"])

# --- BACKGROUND THREADS ---
def start_api():
    """Runs the FastAPI server in a background thread."""
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="error")

def start_usb_monitor():
    """Vanguard Agent: Monitors USB in a background thread."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    def callback(results):
        if not stop_event.is_set():
            loop.run_until_complete(agent_report("VANGUARD", "Perimeter breach! Intercepting data..."))
            loop.run_until_complete(broadcast({"type": "usb_scan", "results": results}))
    
    monitor_usb_with_callback(callback)

# --- ENTRY POINT ---
if __name__ == "__main__":
    # 1. Admin Check
    if not ctypes.windll.shell32.IsUserAnAdmin():
        logger.warning("⚠️ Running without Admin rights. Quarantine features may fail.")

    # 2. Start API Thread
    api_thread = threading.Thread(target=start_api, daemon=True)
    api_thread.start()

    # 3. Start USB Monitor Thread
    usb_thread = threading.Thread(target=start_usb_monitor, daemon=True)
    usb_thread.start()

    # 4. Start Tray Icon (This blocks the main thread and keeps the app alive)
    # create_tray_icon will call stop_event.set() when the user clicks 'Exit'
    create_tray_icon(stop_event)
    
    # If the tray icon is closed/exited, the script ends here
    sys.exit(0)
