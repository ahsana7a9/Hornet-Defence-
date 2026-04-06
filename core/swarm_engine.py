import time
from core.agent_manager import AgentManager
from core.pheromone_system import PheromoneSystem
from core.anomaly_detector import detect_anomaly

class SwarmEngine:
    def __init__(self):
        self.agent_manager = AgentManager()
        self.pheromones = PheromoneSystem()
        self.running = True

    def run(self):
        print("[Swarm] Engine started...")
        while self.running:
            self.execute_cycle()
            time.sleep(2)

    def execute_cycle(self):
        agents = self.agent_manager.get_agents()

        for agent in agents:
            data = agent.collect_data()

            # AI anomaly detection
            if detect_anomaly(data):
                print(f"[Swarm] Threat detected by Agent {agent.id}")
                
                # Tag threat
                self.pheromones.mark(data["source"])

                # Notify all agents
                self.agent_manager.broadcast_threat(data["source"])
