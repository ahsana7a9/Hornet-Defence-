import os
import hashlib
from core.virustotal import check_hash_virustotal
from core.quarantine import quarantine_file
from core.heuristics import heuristic_scan

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
    
    # Define critical directories to skip
    PROTECTED_DIRS = ["C:\\Windows", "C:\\Program Files", "C:\\Program Files (x86)"]

    for root, dirs, files in os.walk(scan_path):
        # --- SAFETY FILTER ---
        if any(root.startswith(p) for p in PROTECTED_DIRS):
            continue

        for file in files:
            full_path = os.path.join(root, file)
            
            # Additional granular path safety
            if "Windows" in full_path or "System32" in full_path:
                continue

            file_hash = get_file_hash(full_path)
            if not file_hash:
                continue

            # --- TIER 1: Local Signature Check ---
            if file_hash in known_malware_hashes:
                q_result = quarantine_file(full_path)
                results.append({
                    "file": full_path,
                    "status": "INFECTED (LOCAL)",
                    "threat": known_malware_hashes[file_hash],
                    "action": q_result.get("status", "QUARANTINED")
                })
                continue 

            # --- TIER 2: Heuristic Analysis ---
            # Fast local check for suspicious patterns (code signing, hidden attributes, etc.)
            heuristic = heuristic_scan(full_path)
            if heuristic["score"] >= 3:
                results.append({
                    "file": full_path,
                    "status": "SUSPICIOUS",
                    "reasons": heuristic["reasons"],
                    "action": "FLAGGED"
                })
                # We continue to avoid redundant VirusTotal calls if it's already highly suspicious
                continue

            # --- TIER 3: VirusTotal Check ---
            try:
                vt_result = check_hash_virustotal(file_hash)
                
                if vt_result and vt_result.get("malicious", 0) > 0:
                    q_result = quarantine_file(full_path)
                    results.append({
                        "file": full_path,
                        "status": "INFECTED (VIRUSTOTAL)",
                        "engine_hits": vt_result["malicious"],
                        "action": q_result.get("status", "QUARANTINED")
                    })
                else:
                    results.append({
                        "file": full_path,
                        "status": "SAFE",
                        "action": "NONE"
                    })
                    
            except Exception as e:
                print(f"Error checking VT for {file}: {e}")

            # Safety limit for testing
            if len(results) >= 50:
                return results

    return results
