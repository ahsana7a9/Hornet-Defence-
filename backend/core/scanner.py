# (Keep previous imports and get_file_hash)

def scan_system(scan_path="C:/"):
    results = []
    PROTECTED_DIRS = ["C:\\Windows", "C:\\Program Files", "C:\\Program Files (x86)"]

    for root, dirs, files in os.walk(scan_path):
        if any(root.startswith(p) for p in PROTECTED_DIRS):
            continue

        for file in files:
            full_path = os.path.join(root, file)
            file_hash = get_file_hash(full_path)
            if not file_hash: continue

            # Tier 1 & 3: Ensure 'quarantined' path is passed back
            # Example for TIER 1:
            if file_hash in known_malware_hashes:
                q_result = quarantine_file(full_path)
                results.append({
                    "file": full_path,
                    "status": "INFECTED (LOCAL)",
                    "action": q_result.get("status"),
                    "quarantined": q_result.get("quarantined"), # <--- MUST HAVE THIS
                    "reasons": [], "engine_hits": 0
                })
                continue
            
            # ... rest of tiers follow same logic ...
