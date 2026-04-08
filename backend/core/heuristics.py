import os

suspicious_keywords = [
    "keylogger",
    "hack",
    "crack",
    "patch",
    "inject",
    "trojan"
]

suspicious_extensions = [
    ".exe",
    ".bat",
    ".vbs",
    ".ps1"
]


def heuristic_scan(file_path):

    score = 0
    reasons = []

    filename = os.path.basename(file_path).lower()

    # rule 1: suspicious name
    for word in suspicious_keywords:
        if word in filename:
            score += 2
            reasons.append(f"suspicious name: {word}")

    # rule 2: suspicious extension
    for ext in suspicious_extensions:
        if filename.endswith(ext):
            score += 1
            reasons.append(f"suspicious extension: {ext}")

    # rule 3: hidden file
    if filename.startswith("."):
        score += 1
        reasons.append("hidden file")

    # rule 4: system-like name
    if "system" in filename or "svchost" in filename:
        score += 2
        reasons.append("masquerading system file")

    return {
        "score": score,
        "reasons": reasons
    }
