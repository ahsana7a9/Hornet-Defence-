import pystray
from PIL import Image
import threading
import os
import webbrowser
import requests # Used to trigger scans via the local API

def create_tray_icon(stop_event):
    """
    SWAT Command: TRAY_CONTROLLER
    Purpose: Manages the background lifecycle and user notifications.
    """
    
    # 1. Load the Hornet Icon
    icon_path = os.path.join(os.path.dirname(__file__), "icon.png")
    if os.path.exists(icon_path):
        image = Image.open(icon_path)
    else:
        # Fallback: Create a tactical yellow square if icon is missing
        image = Image.new('RGB', (64, 64), color=(255, 215, 0))

    def on_open_dashboard(icon, item):
        webbrowser.open("http://localhost:3000")

    def on_quick_scan(icon, item):
        # Notify user that Interceptor is deploying
        icon.notify("Interceptor Agent deployed for sector scan.", title="Hornet SWAT")
        try:
            # Trigger the actual scan via your FastAPI endpoint
            requests.get("http://localhost:8000/scan")
        except Exception as e:
            icon.notify(f"Scan failed: {str(e)}", title="Hornet Error")

    def on_quit(icon, item):
        # Signal the main thread and all agents to shut down
        print("🛡️ [SYSTEM]: Shutting down SWAT agents...")
        stop_event.set()
        icon.stop()

    # 2. Define the Tactical Menu
    menu = pystray.Menu(
        pystray.MenuItem("Command Dashboard", on_open_dashboard, default=True),
        pystray.MenuItem("Deploy Interceptor (Quick Scan)", on_quick_scan),
        pystray.Menu.Separator(),
        pystray.MenuItem("Protection: ACTIVE", lambda: None, enabled=False),
        pystray.Menu.Separator(),
        pystray.MenuItem("Exit Hornet SWAT", on_quit)
    )

    # 3. Initialize and Run
    icon = pystray.Icon(
        "HornetDefence", 
        image, 
        "Hornet SWAT (Active)", 
        menu
    )

    # Initial notification upon boot
    icon.run_detached() # Runs in background so we don't block the startup thread
    icon.notify("Vanguard & Interceptor agents are online.", title="Hornet Defence")

    # Keep the icon alive until stop_event is set elsewhere
    while not stop_event.is_set():
        stop_event.wait(timeout=1)
    
    icon.stop()
