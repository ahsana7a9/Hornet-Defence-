import os
import shutil
import hashlib

QUARANTINE_DIR = "backend/quarantine"


def ensure_quarantine_dir():
    if not os.path.exists(QUARANTINE_DIR):
        os.makedirs(QUARANTINE_DIR)


def quarantine_file(file_path):

    ensure_quarantine_dir()

    try:
        # create unique name using hash
        file_hash = hashlib.sha256(file_path.encode()).hexdigest()
        filename = os.path.basename(file_path)

        new_name = f"{file_hash}_{filename}.quarantine"

        dest_path = os.path.join(QUARANTINE_DIR, new_name)

        shutil.move(file_path, dest_path)

        return {
            "original": file_path,
            "quarantined": dest_path,
            "status": "QUARANTINED"
        }

    except Exception as e:
        return {
            "file": file_path,
            "status": "FAILED",
            "error": str(e)
        }
