import json
import os

MEMORY_FILE = "agent_memory.json"
 
def get_all_memory():
    if not os.path.exists(MEMORY_FILE):
        return {}
    with open(MEMORY_FILE, "r") as f:
        return json.load(f)
 
def load_memory():
    if not os.path.exists(MEMORY_FILE):
        return {"trusted_hashes": [], "user_overrides": 0}
    with open(MEMORY_FILE, "r") as f:
        return json.load(f)

def learn_trust(file_hash):
    memory = load_memory()
    if file_hash not in memory["trusted_hashes"]:
        memory["trusted_hashes"].append(file_hash)
        memory["user_overrides"] += 1
        with open(MEMORY_FILE, "w") as f:
            json.dump(memory, f)

def is_trusted(file_hash):
    memory = load_memory()
    return file_hash in memory["trusted_hashes"]
