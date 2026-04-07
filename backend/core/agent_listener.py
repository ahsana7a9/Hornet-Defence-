# core/agent_listener.py
import threading
import json
from core.redis_client import subscribe

class AgentListener(threading.Thread):
    def __init__(self, agent_id, callback):
        super().__init__()
        self.agent_id = agent_id
        self.callback = callback  
        self.daemon = True        

    def run(self):
        # Ensure this matches the channel name used in SwarmEngine.publish
        pubsub = subscribe("threats") 
        print(f"[Listener] Agent {self.agent_id} is now listening for threats...")
        
        for msg in pubsub.listen():
            if msg["type"] == "message":
                try:
                    data = json.loads(msg["data"])
                    
                    # 1. Prevent an infinite loop where an agent reacts to its own message
                    if str(data.get("agent_id")) == str(self.agent_id):
                        continue
                    
                    # 2. Extract the 'source' to pass as 'target' to agent.respond(target)
                    target = data.get("source")
                    
                    if target:
                        self.callback(target)
                        
                except json.JSONDecodeError:
                    print(f"[Error] Agent {self.agent_id} received malformed JSON")
                except Exception as e:
                    print(f"[Error] Listener error: {e}")
