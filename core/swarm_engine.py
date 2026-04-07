import time
import redis
import json
from core.agent_manager import AgentManager
from core.pheromone_system import PheromoneSystem
from core.anomaly_detector import detect_anomaly
from core.elasticsearch_client import log_event  # <--- NEW IMPORT

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
        print("[Swarm] Engine started with Redis & Elasticsearch logging...")
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
                    "severity": "high",
                    "details": data  # Optional: include raw agent data
                }
                
                print(f"[Swarm] Threat detected by Agent {agent.id}")
                
                # 1. Local tagging (Pheromones)
                self.pheromones.mark(data["source"])

                # 2. Global Broadcast (Redis)
                # Ensure the channel name matches your AgentListener ("threats")
                self.publish_event("threats", threat_info)
                
                # 3. Persistent Logging (Elasticsearch) <--- NEW LOGIC
                try:
                    log_event("threats", threat_info)
                except Exception as e:
                    print(f"[Error] Failed to log to Elasticsearch: {e}")

                # 4. Local traditional notify
                self.agent_manager.broadcast_threat(data["source"])
