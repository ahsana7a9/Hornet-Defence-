import time
import redis
import json
from core.agent_manager import AgentManager
from core.pheromone_system import PheromoneSystem
from core.anomaly_detector import detect_anomaly

class SwarmEngine:
    def __init__(self, redis_host='localhost', redis_port=6379):
        self.agent_manager = AgentManager()
        self.pheromones = PheromoneSystem()
        self.running = True
        
        # Initialize Redis connection
        self.redis_client = redis.Redis(
            host=redis_host, 
            port=redis_port, 
            decode_responses=True
        )

    def publish_event(self, channel, data):
        """Standardized method to push data to the Redis bus."""
        self.redis_client.publish(channel, json.dumps(data))

    def run(self):
        print("[Swarm] Engine started with Redis backbone...")
        while self.running:
            self.execute_cycle()
            time.sleep(2)

    def execute_cycle(self):
        agents = self.agent_manager.get_agents()

        for agent in agents:
            data = agent.collect_data()

            # AI anomaly detection
            if detect_anomaly(data):
                threat_info = {
                    "agent_id": agent.id,
                    "source": data["source"],
                    "timestamp": time.time(),
                    "severity": "high"
                }
                
                print(f"[Swarm] Threat detected by Agent {agent.id}")
                
                # 1. Local tagging
                self.pheromones.mark(data["source"])

                # 2. Global Broadcast via Redis
                self.publish_event("swarm_threats", threat_info)
                
                # 3. Traditional notify
                self.agent_manager.broadcast_threat(data["source"])
