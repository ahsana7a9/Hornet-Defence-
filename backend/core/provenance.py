import hashlib
import json

def generate_project_fingerprint(owner_name="Ahsan I.S.", project_name="Hornet-Defence"):
    """
    Generates a unique cryptographic hash to prove ownership.
    """
    # This string is your 'Digital DNA'
    secret_salt = "Swarm-Intelligence-v1-2026" 
    identity_string = f"{owner_name}:{project_name}:{secret_salt}"
    
    # Generate SHA-256 Hash
    fingerprint = hashlib.sha256(identity_string.encode()).hexdigest()
    return fingerprint

# This is your static, immutable project hash
PROJECT_HASH = generate_project_fingerprint()
