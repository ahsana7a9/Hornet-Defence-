import threading
import logging
import asyncio
import ctypes
import uvicorn
import sys
import winreg as reg 
from fastapi import FastAPI, WebSocket, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware

# Core Logic Imports
from core.scanner import scan_system
from core.quarantine import restore_file, delete_quarantined_file
from core.usb_monitor import monitor_usb_with_callback
from core.memory import learn_trust
from tray_app import create_tray_icon  
from core.memory import get_all_memory, learn_trust # Ensure these are imported 

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
    """Sends tactical updates to all connected Dashboards."""
    for client in clients:
        try: 
            await client.send_json(data)
        except Exception: 
            continue

async def agent_report(agent, message):
    """Allows agents to speak directly to the Tactical Terminal."""
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
    # Welcome message on successful uplink
    await websocket.send_json({"type": "agent_msg", "text": "🛡️ [SYSTEM]: SWAT Agents online. Uplink secure."})
    
    try:
        while not stop_event.is_set():
            # Wait for data or timeout to check stop_event
            try:
                await asyncio.wait_for(websocket.receive_text(), timeout=1.0)
            except asyncio.TimeoutError:
                continue
    except Exception:
        pass
    finally:
        if websocket in clients:
            clients.remove(websocket)

@app.get("/scan")
async def run_scan(background_tasks: BackgroundTasks):
    """Triggers Interceptor for a full sector sweep."""
    async def scan_wrapper():
        await agent_report("INTERCEPTOR", "Initiating area sweep. Standby for signature analysis.")
        # Perform the scan
        results = scan_system(broadcast_func=agent_report)
        # Send final results to the UI
        await broadcast({"type": "usb_scan", "results": results})
        await agent_report("INTERCEPTOR", "Sector sweep complete. Threats logged to Vault.")

    background_tasks.add_task(scan_wrapper) 
    return {"status": "started"}

@app.post("/restore")
async def run_restore(item: dict):
    """Warden: Moves file from Vault back to original location."""
    if "file_hash" in item:
        learn_trust(item["file_hash"])
    
    await agent_report("WARDEN", f"User override detected. Restoring target and updating intelligence.")
    res = restore_file(item["quarantined_path"], item["original_path"])
    return res

@app.post("/delete-quarantine")
async def run_delete(item: dict):
    """Warden: Permanent neutralization of a threat."""
    await agent_report("WARDEN", "Neutralizing threat permanently. Clearing vault space.")
    res = delete_quarantined_file(item["quarantined_path"])
    return res


@app.get("/intelligence")
async def get_intelligence():
    """Returns the agent's learned signature database."""
    return get_all_memory()

@app.post("/forget-signature")
async def forget_signature(item: dict):
    """Allows the user to remove a trusted hash from memory."""
    # Logic to remove hash from agent_memory.json
    await agent_report("WARDEN", "Signature purged from memory. Target is no longer trusted.")
    return {"status": "purged"}

def ensure_persistence():
    """Warden: Locks the SWAT team into the Windows boot sequence."""
    app_path = sys.executable
    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    try:
        key = reg.OpenKey(reg.HKEY_CURRENT_USER, key_path, 0, reg.KEY_SET_VALUE)
        reg.SetValueEx(key, "HornetSWAT", 0, reg.REG_SZ, app_path)
        reg.CloseKey(key)
        logger.info("🔒 [WARDEN]: Persistence established in Registry.")
    except Exception as e:
        logger.error(f"⚠️ [WARDEN]: Persistence failed: {e}")

# Call this before starting threads
ensure_persistence()    
 
# --- BACKGROUND THREADS ---
def start_api():
    """Runs the FastAPI server in a background thread."""
    # We use log_level 'error' to keep the background console clean
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="error", access_log=False)

def start_usb_monitor():
    """Vanguard Agent: Monitors USB ports in a background thread."""
    # Create a new event loop for this specific thread
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    def callback(results):
        if not stop_event.is_set():
            # Run the reporting in the thread's own loop
            loop.run_until_complete(agent_report("VANGUARD", "Perimeter breach! Intercepting data..."))
            loop.run_until_complete(broadcast({"type": "usb_scan", "results": results}))
    
    monitor_usb_with_callback(callback)

# --- ENTRY POINT ---
if __name__ == "__main__":
    # 1. Admin Check (Crucial for Quarantine/Shredding)
    if not ctypes.windll.shell32.IsUserAnAdmin():
        print("⚠️ [CRITICAL]: Admin rights missing. Protection levels reduced.")

    # 2. Start API Thread
    api_thread = threading.Thread(target=start_api, daemon=True)
    api_thread.start()

    # 3. Start USB Monitor Thread
    usb_thread = threading.Thread(target=start_usb_monitor, daemon=True)
    usb_thread.start()

    # 4. Start Tray Icon 
    # This keeps the main thread alive. Closing the tray will trigger stop_event.
    try:
        create_tray_icon(stop_event)
    except KeyboardInterrupt:
        stop_event.set()
    
    sys.exit(0)
