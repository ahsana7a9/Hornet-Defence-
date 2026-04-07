import random
import time
import logging

logger = logging.getLogger(__name__)

class BruteAgent:
    def __init__(self, agent_id: int):
        self.id = agent_id
        self.name = f"BruteAgent-{agent_id}"

    def collect_data(self) -> dict:
        """Simulate brute-force detection data collection."""
        sources = [
            "attacker-node-1", "attacker-node-2",
            "203.0.113.10", "198.51.100.42"
        ]
        return {
            "agent": self.name,
            "source": random.choice(sources),
            "timestamp": time.time(),
            "type": "brute_force",
            "failed_attempts": random.randint(0, 200),
            "targeted_service": random.choice(["ssh", "http", "ftp", "rdp"]),
            "anomaly_score": round(random.uniform(0, 1), 4)
        }

    def respond(self, target: str):
        logger.info(f"[{self.name}] Blocking threat at: {target}")
