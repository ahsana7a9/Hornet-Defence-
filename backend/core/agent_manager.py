import logging
from agents.recon_agent import ReconAgent
from agents.brute_agent import BruteAgent
from agents.log_agent import LogAgent
from core.agent_listener import AgentListener

logger = logging.getLogger(__name__)


class AgentManager:
    def __init__(self):
        self.agents = [
            ReconAgent(1),
            BruteAgent(2),
            LogAgent(3),
        ]
        self._start_listeners()

    def _start_listeners(self):
        for agent in self.agents:
            listener = AgentListener(agent_id=agent.id, callback=agent.respond)
            listener.start()
            logger.info(f"[Manager] Listener started for {agent.name}")

    def get_agents(self):
        return self.agents

    def broadcast_threat(self, target: str):
        for agent in self.agents:
            try:
                agent.respond(target)
            except Exception as e:
                logger.warning(f"[Manager] {agent.name} respond error: {e}")
