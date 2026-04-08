import os
import hashlib
import time  # NEW: For rate limiting
from core.virustotal import check_hash_virustotal
from core.quarantine import quarantine_file
from core.heuristics import heuristic_scan

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
    PROTECTED_DIRS = ["C:\\Windows", "C:\\Program Files", "C:\\Program Files (x86)"]

    for root, dirs, files in os.walk(scan_path):
        if any(root.startswith(p) for p in PROTECTED_DIRS):
            continue

        for file in files:
            full_path = os.path.join(root, file)
            if "Windows" in full_path or "System32" in full_path:
                continue

            file_hash = get_file_hash(full_path)
            if not file_hash:
                continue

            # TIER 1: Local
            if file_hash in known_malware_hashes:
                q_result = quarantine_file(full_path)
                results.append({
                    "file": full_path,
                    "status": "INFECTED (LOCAL)",
                    "threat": known_malware_hashes[file_hash],
                    "action": q_result.get("status", "QUARANTINED"),
                    "quarantined": q_result.get("quarantined"), # Important for Restore
                    "engine_hits": 0,
                    "reasons": []
                })
                continue 

            # TIER 2: Heuristics
            heuristic = heuristic_scan(full_path)
            if heuristic["score"] >= 3:
                results.append({
                    "file": full_path,
                    "status": "SUSPICIOUS",
                    "reasons": heuristic["reasons"],
                    "action": "FLAGGED",
                    "quarantined": None,
                    "engine_hits": 0
                })
                continue

            # TIER 3: VirusTotal
            try:
                vt_result = check_hash_virustotal(file_hash)
                
                # Check if API returned data (prevents crash on rate limit)
                if vt_result and vt_result.get("malicious", 0) > 0:
                    q_result = quarantine_file(full_path)
                    results.append({
                        "file": full_path,
                        "status": "INFECTED (VIRUSTOTAL)",
                        "engine_hits": vt_result["malicious"],
                        "action": q_result.get("status", "QUARANTINED"),
                        "quarantined": q_result.get("quarantined"),
                        "reasons": []
                    })
                else:
                    results.append({
                        "file": full_path,
                        "status": "SAFE",
                        "action": "NONE",
                        "quarantined": None,
                        "engine_hits": 0,
                        "reasons": []
                    })
                
                # VT FREE TIER: Sleep 15s to avoid 403/429 errors
                time.sleep(15)
                    
            except Exception as e:
                print(f"VT Error: {e}")

            if len(results) >= 50:
                return results

    return results
