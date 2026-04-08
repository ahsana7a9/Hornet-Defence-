import os
import math

# SWAT Intelligence: Metadata Signatures
suspicious_keywords = ["keylogger", "hack", "crack", "patch", "inject", "trojan", "miner", "ransom"]
suspicious_extensions = [".exe", ".bat", ".vbs", ".ps1", ".scr", ".cmd"]

def calculate_entropy(file_path):
    """
    Measures the randomness of a file. 
    High entropy (7.0 - 8.0) indicates encryption or compression (common in malware).
    """
    try:
        with open(file_path, "rb") as f:
            data = f.read()
        if not data:
            return 0
        
        entropy = 0
        for x in range(256):
            p_x = float(data.count(x)) / len(data)
            if p_x > 0:
                entropy += - p_x * math.log(p_x, 2)
        return entropy
    except Exception:
        return 0

def heuristic_scan(file_path):
    """
    INTERCEPTOR BEAST MODE: 
    Multi-layered behavioral and structural analysis.
    """
    score = 0
    reasons = []
    
    try:
        filename = os.path.basename(file_path).lower()
        file_size = os.path.getsize(file_path)

        # --- TIER 1: Metadata Analysis ---
        for word in suspicious_keywords:
            if word in filename:
                score += 2
                reasons.append(f"Suspicious keyword: '{word}'")

        for ext in suspicious_extensions:
            if filename.endswith(ext):
                score += 1
                reasons.append(f"Executable extension: {ext}")

        if filename.startswith("."):
            score += 1
            reasons.append("Hidden file attribute detected")

        # --- TIER 2: Masquerading Detection ---
        # Checks for files trying to look like Windows system processes
        system_names = ["svchost", "lsass", "wininit", "smss", "csrss"]
        if any(name in filename for name in system_names):
            score += 3
            reasons.append("Masquerading as a critical system process")

        # Double extension trick: e.g., "invoice.pdf.exe"
        if len(filename.split('.')) > 2:
            score += 2
            reasons.append("Suspicious double extension")

        # --- TIER 3: Structural Analysis (Entropy) ---
        entropy = calculate_entropy(file_path)
        
        # High entropy = Encrypted/Packed (High probability of malware 'Crypters')
        if entropy > 7.2:
            score += 4
            reasons.append(f"High Entropy ({entropy:.2f}): Possible Encrypted Malware")
        elif entropy > 6.5:
            score += 1
            reasons.append("Moderate Entropy: Compressed or packed data")

        # --- TIER 4: Behavioral Oddities ---
        # Very small executables are often 'Downloaders' or 'Droppers'
        if filename.endswith(".exe") and file_size < 50 * 1024: # Less than 50KB
            score += 2
            reasons.append("Small executable: Potential Malware Dropper")

    except Exception as e:
        reasons.append(f"Heuristic error: {str(e)}")

    return {
        "score": score,
        "reasons": reasons,
        "entropy": round(entropy, 2)
    }
