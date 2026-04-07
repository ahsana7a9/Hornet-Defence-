import time
import logging
from core.agent_manager import AgentManager
from core.pheromone_system import PheromoneSystem
from core.anomaly_detector import detect_anomaly
from core.elasticsearch_client import log_event
from core.redis_client import publish
from core.threat_eliminator import block_ip, is_blocked
from core.alert_manager import add_alert

logger = logging.getLogger(__name__)

AUTO_BLOCK_THRESHOLD = 0.65


class SwarmEngine:
    def __init__(self):
        self.agent_manager = AgentManager()
        self.pheromones    = PheromoneSystem()
        self.running       = True

    def run(self):
        logger.info("[Swarm] Engine started — real network monitoring active")
        while self.running:
            try:
                self.execute_cycle()
            except Exception as e:
                logger.error(f"[Swarm] Cycle error: {e}")
            time.sleep(2)

    def execute_cycle(self):
        for agent in self.agent_manager.get_agents():
            try:
                data   = agent.collect_data()
                source = data.get("source", "unknown")
                score  = float(data.get("anomaly_score", 0.0))

                if detect_anomaly(data):
                    threat_info = {
                        "agent_id":     agent.id,
                        "agent_name":   agent.name,
                        "source":       source,
                        "timestamp":    time.time(),
                        "severity":     self._severity(score),
                        "anomaly_score": score,
                        "real_data":    data.get("real_data", False),
                        "details":      data,
                    }

                    logger.info(f"[Swarm] Threat detected by {agent.name} — source: {source} score: {score:.2f}")

                    # 1. Pheromone tag (local)
                    self.pheromones.mark(source)

                    # 2. Redis broadcast to peers
                    publish("threats", threat_info)

                    # 3. Persist to Elasticsearch / in-memory
                    try:
                        log_event("threats", threat_info)
                    except Exception as e:
                        logger.warning(f"[Swarm] Log error: {e}")

                    # 4. Auto-block high-confidence real threats
                    if score >= AUTO_BLOCK_THRESHOLD and data.get("real_data") and not is_blocked(source):
                        block_ip(source, reason=f"auto-block score={score:.2f} by {agent.name}")
                        add_alert(
                            self._severity(score),
                            f"Auto-blocked {source} (score={score:.2f})",
                            source=agent.name,
                            metadata={"ip": source, "score": score}
                        )

                    # 5. Alert for simulated threats (demo mode)
                    elif not data.get("real_data"):
                        add_alert(
                            self._severity(score),
                            f"Simulated threat from {source} (score={score:.2f})",
                            source=agent.name,
                            metadata={"ip": source, "score": score, "simulated": True}
                        )

                    # 6. Broadcast to all peer agents
                    self.agent_manager.broadcast_threat(source)

            except Exception as e:
                logger.warning(f"[Swarm] Agent {agent.id} error: {e}")

    @staticmethod
    def _severity(score: float) -> str:
        if score >= 0.85:  return "CRITICAL"
        if score >= 0.65:  return "HIGH"
        if score >= 0.40:  return "WARNING"
        return "INFO"
