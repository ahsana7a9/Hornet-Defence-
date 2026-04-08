import os
import hashlib
from core.virustotal import check_hash_virustotal
from core.quarantine import quarantine_file
# Local database (fast, offline)
known_malware_hashes = {
    "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855": "Test Malware"
}

def get_file_hash(filepath):
    sha256 = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            while chunk := f.read(4096):
                sha256.update(chunk)
        return sha256.hexdigest()
    except Exception:
        return None

def scan_system(scan_path="C:/"):
    results = []

    for root, dirs, files in os.walk(scan_path):
        for file in files:
            full_path = os.path.join(root, file)
            file_hash = get_file_hash(full_path)

            if not file_hash:
                continue

            # --- TIER 1: Local Signature Check ---
            if file_hash in known_malware_hashes:
                results.append({
                    "file": full_path,
                    "status": "INFECTED (LOCAL)",
                    "threat": known_malware_hashes[file_hash]
                })
                continue # Skip VT if we already know it's bad locally

            # --- TIER 2: VirusTotal Check ---
            try:
                vt_result = check_hash_virustotal(file_hash)
                
                if vt_result and vt_result.get("malicious", 0) > 0:
                    results.append({
                        "file": full_path,
                        "status": "INFECTED (VIRUSTOTAL)",
                        "engine_hits": vt_result["malicious"]
                    })
                else:
                    results.append({
                        "file": full_path,
                        "status": "SAFE"
                    })
            except Exception as e:
                # Handle API errors (like rate limits or no internet)
                print(f"Error checking VT for {file}: {e}")

            # Stop after 50 files for safety during testing
            if len(results) >= 50:
                return results

    return results
