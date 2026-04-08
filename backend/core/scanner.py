import os
import hashlib
import time
import asyncio
from core.virustotal import check_hash_virustotal
from core.quarantine import quarantine_file
from core.heuristics import heuristic_scan
from core.memory import is_trusted  # NEW: Agent Memory Access

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

def scan_system(scan_path="C:/", broadcast_func=None):
    """
    SWAT Agent: INTERCEPTOR
    Mission: Search and Neutralize. Now with Memory-based Learning.
    """
    results = []
    SYSTEM_SENSITIVE = ["C:\\Windows", "C:\\Program Files", "C:\\Program Files (x86)", "C:\\Boot"]

    for root, dirs, files in os.walk(scan_path):
        if any(root.startswith(p) for p in SYSTEM_SENSITIVE):
            continue

        for file in files:
            full_path = os.path.join(root, file)
            
            if "System32" in full_path or "syswow64" in full_path.lower():
                continue

            file_hash = get_file_hash(full_path)
            if not file_hash:
                continue

            # --- AI LEARNING TIER: Memory Check ---
            # Interceptor checks if he has seen and trusted this file before
            if is_trusted(file_hash):
                if broadcast_func:
                    asyncio.run(broadcast_func("INTERCEPTOR", f"Recognized trusted signature: {file}. Skipping deep scan."))
                results.append({
                    "file": full_path,
                    "status": "SAFE (TRUSTED)",
                    "action": "NONE",
                    "quarantined": None,
                    "engine_hits": 0,
                    "reasons": ["Agent remembered user override for this file."]
                })
                continue

            # --- TIER 1: Local Signature Check ---
            if file_hash in known_malware_hashes:
                if broadcast_func:
                    asyncio.run(broadcast_func("INTERCEPTOR", f"MATCH FOUND! {file} matches blacklisted hash."))
                q_result = quarantine_file(full_path)
                results.append({
                    "file": full_path,
                    "status": "INFECTED (LOCAL)",
                    "threat": known_malware_hashes[file_hash],
                    "action": q_result.get("status", "QUARANTINED"),
                    "quarantined": q_result.get("quarantined"),
                    "engine_hits": 0,
                    "reasons": ["Matched known malware signature"]
                })
                continue 

            # --- TIER 2: Heuristic Analysis ---
            heuristic = heuristic_scan(full_path)
            if heuristic["score"] >= 3:
                if broadcast_func:
                    asyncio.run(broadcast_func("INTERCEPTOR", f"Caution: {file} exhibiting suspicious traits."))
                results.append({
                    "file": full_path,
                    "status": "SUSPICIOUS",
                    "reasons": heuristic["reasons"],
                    "action": "FLAGGED",
                    "quarantined": None,
                    "engine_hits": 0
                })
                continue

            # --- TIER 3: VirusTotal Check ---
            try:
                if broadcast_func:
                    asyncio.run(broadcast_func("INTERCEPTOR", f"Requesting global intel for {file}..."))
                
                vt_result = check_hash_virustotal(file_hash)
                
                if vt_result and vt_result.get("malicious", 0) > 0:
                    q_result = quarantine_file(full_path)
                    results.append({
                        "file": full_path,
                        "status": "INFECTED (VIRUSTOTAL)",
                        "engine_hits": vt_result["malicious"],
                        "action": q_result.get("status", "QUARANTINED"),
                        "quarantined": q_result.get("quarantined"),
                        "reasons": [f"Flagged by {vt_result['malicious']} AV engines"]
                    })
                else:
                    results.append({
                        "file": full_path,
                        "status": "SAFE",
                        "engine_hits": 0,
                        "action": "NONE",
                        "quarantined": None,
                        "reasons": []
                    })
                
                # VirusTotal Free Tier Rate Limiting
                time.sleep(15)
                    
            except Exception as e:
                if broadcast_func:
                    asyncio.run(broadcast_func("INTERCEPTOR", f"Intel Link Failed: {str(e)}", type="error"))

            if len(results) >= 50:
                if broadcast_func:
                    asyncio.run(broadcast_func("INTERCEPTOR", "Sector sweep limit reached. Returning to base."))
                return results

    return results
