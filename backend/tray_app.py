import pystray
from PIL import Image
import threading
import os
import webbrowser

def create_tray_icon(stop_event, start_scan_callback):
    # Load your Hornet icon (make sure you have an icon.png in your folder)
    # For now, we create a simple placeholder icon
    image = Image.open("icon.png") if os.path.exists("icon.png") else Image.new('RGB', (64, 64), color=(255, 215, 0))

    def on_open_dashboard(icon, item):
        webbrowser.open("http://localhost:3000")

    def on_quit(icon, item):
        stop_event.set()
        icon.stop()

    menu = pystray.Menu(
        pystray.MenuItem("Open Dashboard", on_open_dashboard),
        pystray.MenuItem("Execute Quick Scan", lambda: start_scan_callback()),
        pystray.Menu.Separator(),
        pystray.MenuItem("Exit Hornet Defence", on_quit)
    )

    icon = pystray.Icon("HornetDefence", image, "Hornet Defence SWAT", menu)
    icon.run()
