import PyInstaller.__main__
import os
from pathlib import Path

# ── Configuration ──────────────────────────────
APP_NAME = "HornetSWAT"
ENTRY_POINT = "main.py"
ICON_FILE = "icon.ico"
ASSETS = ["icon.png"]

# ── Utility ────────────────────────────────────
def file_exists(path):
    return Path(path).exists()

# ── Build प्रक्रिया ────────────────────────────
def build_exe():
    print("=" * 50)
    print(f"[SYSTEM]  Packaging {APP_NAME}")
    print("=" * 50)

    if not file_exists(ENTRY_POINT):
        print(f"[ERROR]  Entry point '{ENTRY_POINT}' not found.")
        return

    params = [
        ENTRY_POINT,
        f"--name={APP_NAME}",
        "--onefile",
        "--windowed",
        "--uac-admin",
        "--clean",
        "--noconfirm",
    ]

    # ── Icon handling ──────────────────────────
    if file_exists(ICON_FILE):
        params.append(f"--icon={ICON_FILE}")
    else:
        print("[WARN]  icon.ico not found — using default icon")

    # ── Include assets ─────────────────────────
    for asset in ASSETS:
        if file_exists(asset):
            params.append(f"--add-data={asset};.")
        else:
            print(f"[WARN]  Missing asset: {asset}")

    # ── Hidden imports (critical for FastAPI/Uvicorn) ──
    params.extend([
        "--collect-all=uvicorn",
        "--hidden-import=uvicorn.logging",
        "--hidden-import=uvicorn.loops.auto",
        "--hidden-import=uvicorn.protocols.http.auto",
        "--hidden-import=uvicorn.protocols.websockets.auto",
        "--hidden-import=uvicorn.lifespan.on",
    ])

    # ── Run build ──────────────────────────────
    try:
        PyInstaller.__main__.run(params)
        print("\n[SUCCESS]  Build complete!")
        print("[OUTPUT]  Check the 'dist/' folder")
    except Exception as e:
        print(f"[ERROR]  Build failed: {e}")


# ── Entry ─────────────────────────────────────
if __name__ == "__main__":
    build_exe()