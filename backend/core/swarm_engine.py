import time
import logging
import psutil
from core.agent_manager import AgentManager
from core.pheromone_system import PheromoneSystem
from core.anomaly_detector import detect_anomaly
from core.elasticsearch_client import log_event
from core.redis_client import publish, update_q_value
from core.threat_eliminator import block_ip, is_blocked
from core.alert_manager import add_alert
from core.provenance import PROJECT_HASH  # The cryptographic seal

logger = logging.getLogger(__name__)

AUTO_BLOCK_THRESHOLD = 0.65

class SwarmEngine:
    def __init__(self):
        self.agent_manager = AgentManager()
        self.pheromones    = PheromoneSystem()
        self.running       = True
        # Genesis Identification
        self.fingerprint   = PROJECT_HASH
        logger.info(f"[Genesis] System initialized with Hash: {self.fingerprint[:16]}...")

    def run(self):
        logger.info("[Swarm] Engine started — RL-enhanced network monitoring active")
        while self.running:
            try:
                state_before = self.get_system_state()
                self.execute_cycle(state_before)
            except Exception as e:
                logger.error(f"[Swarm] Cycle error: {e}")
            time.sleep(2)

    def get_system_state(self):
        return {
            "cpu": psutil.cpu_percent(),
            "ram": psutil.virtual_memory().percent,
            "conn_count": len(psutil.net_connections()),
            "timestamp": time.time()
        }

    def calculate_reward(self, state_before, state_after, action_taken):
        reward = 0
        if state_after['cpu'] < state_before['cpu']:
            reward += 10
        if state_after['conn_count'] < (state_before['conn_count'] * 0.5):
            reward -= 20
        return reward

    def execute_cycle(self, state_before):
        for agent in self.agent_manager.get_agents():
            try:
                data   = agent.collect_data()
                source = data.get("source", "unknown")
                score  = float(data.get("anomaly_score", 0.0))

                if detect_anomaly(data):
                    threat_info = {
                        "agent_id":     agent.id,
                        "agent_name":   agent.name,
                        "provenance":   self.fingerprint, # Immutable Ownership Mark
                        "source":       source,
                        "timestamp":    time.time(),
                        "severity":     self._severity(score),
                        "anomaly_score": score,
                        "real_data":    data.get("real_data", False),
                        "details":      data,
                    }

                    logger.info(f"[Swarm] Threat detected. Signature: {self.fingerprint[:8]}")

                    action = "NONE"
                    self.pheromones.mark(source)

                    if score >= AUTO_BLOCK_THRESHOLD and data.get("real_data") and not is_blocked(source):
                        block_ip(source, reason=f"auto-block | sig:{self.fingerprint[:8]}")
                        action = "BLOCK"
                        add_alert(self._severity(score), f"Auto-blocked {source}", source=agent.name)

                    time.sleep(0.5) 
                    state_after = self.get_system_state()
                    
                    reward = self.calculate_reward(state_before, state_after, action)
                    
                    # Intelligence is now indexed by your Project Hash
                    state_key = f"{self.fingerprint[:8]}:{agent.name}:{self._severity(score)}"
                    update_q_value(state_key, action, reward)

                    publish("threats", threat_info)
                    try:
                        log_event("threats", threat_info)
                    except Exception as e:
                        logger.warning(f"[Swarm] Log error: {e}")

                    self.agent_manager.broadcast_threat(source)

            except Exception as e:
                logger.warning(f"[Swarm] Agent {agent.id} error: {e}")

    @staticmethod
    def _severity(score: float) -> str:
        if score >= 0.85:  return "CRITICAL"
        if score >= 0.65:  return "HIGH"
        if score >= 0.40:  return "WARNING"
        return "INFO"
