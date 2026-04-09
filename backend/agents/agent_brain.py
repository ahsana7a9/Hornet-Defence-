import logging
from ai.reasoning_engine import ReasoningEngine
from core.redis_client import get_best_action

logger = logging.getLogger(__name__)

class AgentBrain:
    def __init__(self):
        self.llm = ReasoningEngine()

    def decide(self, agent_name, observation_data):
        # 1. State Identification
        score = float(observation_data.get("anomaly_score", 0.0))
        severity = "LOW"
        if score >= 0.85: severity = "CRITICAL"
        elif score >= 0.65: severity = "HIGH"
        
        state_key = f"{agent_name}:{severity}"

        # 2. Check Redis for Learned Intelligence (Exploitation)
        best_action = get_best_action(state_key)
        if best_action != "NONE":
            return best_action

        # 3. If no intelligence exists, ask the LLM (Exploration)
        logger.info(f"[{agent_name}] Consulting LLM for unknown state...")
        decision_data = self.llm.analyze_threat(agent_name, observation_data)
        return decision_data.get("decision", "MONITOR")
