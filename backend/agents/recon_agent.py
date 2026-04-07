import random
import time
import logging

logger = logging.getLogger(__name__)

class ReconAgent:
    def __init__(self, agent_id: int):
        self.id = agent_id
        self.name = f"ReconAgent-{agent_id}"

    def collect_data(self) -> dict:
        """Simulate reconnaissance data collection."""
        sources = [
            "192.168.1.1", "10.0.0.5", "172.16.0.20",
            "external-host-1", "external-host-2"
        ]
        return {
            "agent": self.name,
            "source": random.choice(sources),
            "timestamp": time.time(),
            "type": "recon",
            "connections": random.randint(1, 50),
            "suspicious_ports": random.sample([22, 80, 443, 8080, 3306, 5432], k=random.randint(0, 3)),
            "anomaly_score": round(random.uniform(0, 1), 4)
        }

    def respond(self, target: str):
        logger.info(f"[{self.name}] Responding to threat at: {target}")
