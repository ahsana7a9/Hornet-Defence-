import PyInstaller.__main__
import os
import shutil

# SWAT Deployment Configuration
APP_NAME = "HornetSWAT"
ENTRY_POINT = "main.py"
ICON_PATH = "icon.ico" # Ensure you have an .ico file or use icon.png

def build_exe():
    print(f"📦 [SYSTEM]: Initiating packaging for {APP_NAME}...")
    
    params = [
        ENTRY_POINT,
        f'--name={APP_NAME}',
        '--onefile',            # Single EXE output
        '--windowed',           # No console window
        '--uac-admin',          # Request Admin rights on start
        f'--icon={ICON_PATH if os.path.exists(ICON_PATH) else "NONE"}',
        '--collect-all=uvicorn', # Ensure webserver dependencies are caught
        '--add-data=icon.png;.', # Include the tray icon
        '--hidden-import=uvicorn.logging',
        '--hidden-import=uvicorn.loops.auto',
        '--hidden-import=uvicorn.protocols.http.auto',
        '--hidden-import=uvicorn.protocols.websockets.auto',
        '--hidden-import=uvicorn.lifespan.on',
    ]

    PyInstaller.__main__.run(params)
    print(f"🚀 [SYSTEM]: Deployment successful. Check the /dist folder.")

if __name__ == "__main__":
    build_exe()
