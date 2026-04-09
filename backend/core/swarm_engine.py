import time
import logging
import psutil  # Required for State observation
from core.agent_manager import AgentManager
from core.pheromone_system import PheromoneSystem
from core.anomaly_detector import detect_anomaly
from core.elasticsearch_client import log_event
from core.redis_client import publish, update_q_value  # Added update_q_value
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
        logger.info("[Swarm] Engine started — RL-enhanced network monitoring active")
        while self.running:
            try:
                # Capture State BEFORE agent actions
                state_before = self.get_system_state()
                
                self.execute_cycle(state_before)
                
            except Exception as e:
                logger.error(f"[Swarm] Cycle error: {e}")
            time.sleep(2)

    def get_system_state(self):
        """Captures the current Environment State for RL."""
        return {
            "cpu": psutil.cpu_percent(),
            "ram": psutil.virtual_memory().percent,
            "conn_count": len(psutil.net_connections()),
            "timestamp": time.time()
        }

    def calculate_reward(self, state_before, state_after, action_taken):
        """Standard Reward Function for the Swarm."""
        reward = 0
        
        # Reward for lowering CPU stress
        if state_after['cpu'] < state_before['cpu']:
            reward += 10
        
        # Penalty for 'Over-blocking' (killing connections too aggressively)
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
                        "source":       source,
                        "timestamp":    time.time(),
                        "severity":     self._severity(score),
                        "anomaly_score": score,
                        "real_data":    data.get("real_data", False),
                        "details":      data,
                    }

                    logger.info(f"[Swarm] Threat detected by {agent.name} — source: {source} score: {score:.2f}")

                    # --- RL ACTION LOGIC ---
                    action = "NONE"
                    
                    # 1. Pheromone tag (Stigmergy)
                    self.pheromones.mark(source)

                    # 2. Execute Defense Action
                    if score >= AUTO_BLOCK_THRESHOLD and data.get("real_data") and not is_blocked(source):
                        block_ip(source, reason=f"auto-block score={score:.2f}")
                        action = "BLOCK"
                        add_alert(self._severity(score), f"Auto-blocked {source}", source=agent.name)

                    # 3. Capture State AFTER action to calculate Learning Reward
                    time.sleep(0.5) # Short delay to let system stabilize
                    state_after = self.get_system_state()
                    
                    # 4. Update Global Swarm Intelligence (Redis Q-Table)
                    reward = self.calculate_reward(state_before, state_after, action)
                    
                    # We use a simplified state key based on severity and agent type
                    state_key = f"{agent.name}:{self._severity(score)}"
                    update_q_value(state_key, action, reward)

                    # --- STANDARD LOGGING ---
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
