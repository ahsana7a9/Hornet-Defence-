from agents.recon_agent import ReconAgent
from agents.brute_agent import BruteAgent
from core.agent_listener import AgentListener # The class we built in the previous step

class AgentManager:
    def __init__(self):
        # 1. Initialize your agents as usual
        self.agents = [
            ReconAgent(1),
            BruteAgent(2)
        ]
        
        # 2. Start a background listener for each agent
        self._start_listeners()

    def _start_listeners(self):
        for agent in self.agents:
            # We point the callback to the agent's existing respond method
            listener = AgentListener(
                agent_id=agent.id, 
                callback=agent.respond 
            )
            listener.start()
            print(f"[Manager] Network listener started for Agent {agent.id}")

    def get_agents(self):
        return self.agents

    def broadcast_threat(self, target):
        """This still works for local/immediate broadcasts."""
        for agent in self.agents:
            agent.respond(target)
