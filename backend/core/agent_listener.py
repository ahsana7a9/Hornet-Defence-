import threading
import json
import logging
from core.redis_client import subscribe

logger = logging.getLogger(__name__)

class AgentListener(threading.Thread):
    def __init__(self, agent_id, callback):
        super().__init__()
        self.agent_id = agent_id
        self.callback = callback
        self.daemon = True

    def run(self):
        pubsub = subscribe("threats")
        if pubsub is None:
            logger.warning(f"[Listener] Agent {self.agent_id}: Redis unavailable — listener inactive")
            return

        logger.info(f"[Listener] Agent {self.agent_id} is now listening for threats...")
        try:
            for msg in pubsub.listen():
                if msg["type"] == "message":
                    try:
                        data = json.loads(msg["data"])
                        if str(data.get("agent_id")) == str(self.agent_id):
                            continue
                        target = data.get("source")
                        if target:
                            self.callback(target)
                    except json.JSONDecodeError:
                        logger.warning(f"[Listener] Agent {self.agent_id}: malformed JSON")
                    except Exception as e:
                        logger.warning(f"[Listener] Agent {self.agent_id} error: {e}")
        except Exception as e:
            logger.warning(f"[Listener] Agent {self.agent_id} disconnected: {e}")
