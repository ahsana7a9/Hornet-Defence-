import logging
from agents.recon_agent import ReconAgent
from agents.brute_agent import BruteAgent
from core.agent_listener import AgentListener

logger = logging.getLogger(__name__)

class AgentManager:
    def __init__(self):
        self.agents = [
            ReconAgent(1),
            BruteAgent(2)
        ]
        self._start_listeners()

    def _start_listeners(self):
        for agent in self.agents:
            listener = AgentListener(
                agent_id=agent.id,
                callback=agent.respond
            )
            listener.start()
            logger.info(f"[Manager] Listener started for Agent {agent.id}")

    def get_agents(self):
        return self.agents

    def broadcast_threat(self, target: str):
        for agent in self.agents:
            try:
                agent.respond(target)
            except Exception as e:
                logger.warning(f"[Manager] Agent {agent.id} respond error: {e}")
