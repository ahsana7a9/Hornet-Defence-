import os
import shutil
import hashlib

# Best practice: Use an absolute path or ensure it's relative to the project root
QUARANTINE_DIR = os.path.abspath("backend/quarantine")

def ensure_quarantine_dir():
    if not os.path.exists(QUARANTINE_DIR):
        try:
            os.makedirs(QUARANTINE_DIR)
        except Exception as e:
            print(f"Critical Error: Could not create quarantine directory: {e}")

def quarantine_file(file_path):
    ensure_quarantine_dir()

    # Check if file exists before trying to move it
    if not os.path.exists(file_path):
        return {"file": file_path, "status": "FAILED", "error": "File not found"}

    try:
        # 1. Create a unique name 
        # Using path + timestamp or path + content hash is safer
        path_hash = hashlib.sha256(file_path.encode()).hexdigest()[:12] 
        filename = os.path.basename(file_path)
        new_name = f"{path_hash}_{filename}.quarantine"
        dest_path = os.path.join(QUARANTINE_DIR, new_name)

        # 2. Attempt to move the file
        # shutil.move works across different disk partitions better than os.rename
        shutil.move(file_path, dest_path)

        # 3. (Optional) Set permissions to Read-Only for extra safety
        os.chmod(dest_path, 0o444) 

        return {
            "original": file_path,
            "quarantined": dest_path,
            "status": "QUARANTINED"
        }

    except PermissionError:
        return {
            "file": file_path,
            "status": "FAILED",
            "error": "Permission Denied: File may be in use by another process."
        }
    except Exception as e:
        return {
            "file": file_path,
            "status": "FAILED",
            "error": str(e)
        } 
        def restore_file(quarantined_path, original_path):
    """Moves a file from the quarantine vault back to its original location."""
    try:
        # Ensure the original directory still exists before moving back
        os.makedirs(os.path.dirname(original_path), exist_ok=True)
        
        shutil.move(quarantined_path, original_path)
        # Remove read-only restrictions
        os.chmod(original_path, 0o666) 
        
        return {"status": "RESTORED", "path": original_path}
    except Exception as e:
        return {"status": "FAILED", "error": str(e)}
