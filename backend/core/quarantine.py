import os
import shutil
import hashlib

QUARANTINE_DIR = os.path.abspath("backend/quarantine")

def ensure_quarantine_dir():
    if not os.path.exists(QUARANTINE_DIR):
        try:
            os.makedirs(QUARANTINE_DIR)
        except Exception as e:
            print(f"Folder Error: {e}")

def quarantine_file(file_path):
    ensure_quarantine_dir()
    if not os.path.exists(file_path):
        return {"file": file_path, "status": "FAILED", "error": "Missing"}

    try:
        path_hash = hashlib.sha256(file_path.encode()).hexdigest()[:12] 
        filename = os.path.basename(file_path)
        new_name = f"{path_hash}_{filename}.quarantine"
        dest_path = os.path.join(QUARANTINE_DIR, new_name)

        shutil.move(file_path, dest_path)
        os.chmod(dest_path, 0o444) 

        return {
            "original": file_path,
            "quarantined": dest_path,
            "status": "QUARANTINED"
        }
    except PermissionError:
        return {"file": file_path, "status": "FAILED", "error": "File Locked/In Use"}
    except Exception as e:
        return {"file": file_path, "status": "FAILED", "error": str(e)} 

def restore_file(quarantined_path, original_path):
    try:
        os.makedirs(os.path.dirname(original_path), exist_ok=True)
        shutil.move(quarantined_path, original_path)
        os.chmod(original_path, 0o666) 
        return {"status": "RESTORED", "path": original_path}
    except Exception as e:
        return {"status": "FAILED", "error": str(e)}

# --- NEW: Delete Logic ---
def delete_quarantined_file(quarantined_path):
    """Permanently deletes a file from the vault."""
    try:
        # Safety check: Prevent deleting files outside the quarantine directory
        if not quarantined_path.startswith(QUARANTINE_DIR):
            return {"status": "FAILED", "error": "Unauthorized path"}
            
        if os.path.exists(quarantined_path):
            os.remove(quarantined_path)
            return {"status": "DELETED"}
        return {"status": "FAILED", "error": "File not found"}
    except Exception as e:
        return {"status": "FAILED", "error": str(e)}
