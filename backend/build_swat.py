import PyInstaller.__main__
import os

def build():
    PyInstaller.__main__.run([
        'main.py',
        '--onefile',            # Bundle everything into one .exe
        '--windowed',           # Hide the black console window
        '--icon=icon.ico',      # Set the desktop icon
        '--name=HornetSWAT',    # Name of the output file
        '--add-data=icon.png;.', # Include the tray icon image
        '--hidden-import=uvicorn.logging',
        '--admin',              # Request admin privileges on launch
    ])

if __name__ == "__main__":
    build()
