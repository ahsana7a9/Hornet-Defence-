import time
import json
import logging
from core.agent_manager import AgentManager
from core.pheromone_system import PheromoneSystem
from core.anomaly_detector import detect_anomaly
from core.elasticsearch_client import log_event
from core.redis_client import publish

logger = logging.getLogger(__name__)

class SwarmEngine:
    def __init__(self):
        self.agent_manager = AgentManager()
        self.pheromones = PheromoneSystem()
        self.running = True

    def run(self):
        logger.info("[Swarm] Engine started")
        while self.running:
            try:
                self.execute_cycle()
            except Exception as e:
                logger.error(f"[Swarm] Cycle error: {e}")
            time.sleep(2)

    def execute_cycle(self):
        agents = self.agent_manager.get_agents()
        for agent in agents:
            try:
                data = agent.collect_data()
                if detect_anomaly(data):
                    threat_info = {
                        "agent_id": agent.id,
                        "source": data.get("source", "unknown"),
                        "timestamp": time.time(),
                        "severity": "high",
                        "details": data
                    }
                    logger.info(f"[Swarm] Threat detected by Agent {agent.id}")
                    self.pheromones.mark(data.get("source", "unknown"))
                    publish("threats", threat_info)
                    try:
                        log_event("threats", threat_info)
                    except Exception as e:
                        logger.warning(f"[Swarm] Elasticsearch log failed: {e}")
                    self.agent_manager.broadcast_threat(data.get("source", "unknown"))
            except Exception as e:
                logger.warning(f"[Swarm] Agent {agent.id} error: {e}")
