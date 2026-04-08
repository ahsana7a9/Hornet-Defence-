import os
import hashlib

# Example known malicious hashes (dummy for now)
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
    except:
        return None


def scan_system():

    results = []

    for root, dirs, files in os.walk("C:/"):

        for file in files:

            full_path = os.path.join(root, file)

            file_hash = get_file_hash(full_path)

            if not file_hash:
                continue

            if file_hash in known_malware_hashes:
                results.append({
                    "file": full_path,
                    "status": "INFECTED",
                    "threat": known_malware_hashes[file_hash]
                })
            else:
                results.append({
                    "file": full_path,
                    "status": "SAFE"
                })

            # limit results (avoid overload)
            if len(results) > 50:
                return results

    return results
