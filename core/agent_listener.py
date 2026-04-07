import threading
import json
from core.redis_client import subscribe

class AgentListener(threading.Thread):
    def __init__(self, agent_id, callback):
        super().__init__()
        self.agent_id = agent_id
        self.callback = callback  # Function to call when a threat is received
        self.daemon = True        # Ensures thread dies when main process exits

    def run(self):
        pubsub = subscribe("threats")
        print(f"[Listener] Agent {self.agent_id} is now listening for threats...")
        
        for msg in pubsub.listen():
            if msg["type"] == "message":
                data = json.loads(msg["data"])
                # Avoid agents reacting to their own broadcasts
                if data.get("agent_id") != self.agent_id:
                    self.callback(data)
