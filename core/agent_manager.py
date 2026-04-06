from agents.recon_agent import ReconAgent
from agents.brute_agent import BruteAgent

class AgentManager:
    def __init__(self):
        self.agents = [
            ReconAgent(1),
            BruteAgent(2)
        ]

    def get_agents(self):
        return self.agents

    def broadcast_threat(self, target):
        for agent in self.agents:
            agent.respond(target)