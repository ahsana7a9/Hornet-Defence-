import time
import json
import logging
from core.redis_client import get_redis
from core.swarm_engine import SwarmEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Trainer")

def simulate_attack_sequence():
    engine = SwarmEngine()
    r = get_redis()
    
    if not r:
        logger.error("Redis is not running. Start Memurai/Valkey first!")
        return

    logger.info("--- Starting MARL Training Simulation ---")
    
    # 1. Clear previous intelligence to see fresh learning
    r.delete("swarm_iq:ReconAgent-1:HIGH")
    logger.info("Cleared Redis knowledge for a fresh start.")

    # 2. Run the engine for a few cycles
    # During the first 2-3 cycles, look for "Consulting LLM..." in the logs
    for i in range(5):
        logger.info(f"--- Training Cycle {i+1} ---")
        engine.execute_cycle(engine.get_system_state())
        time.sleep(3)

    # 3. Verify Learning
    # By cycle 4 or 5, you should see "Using learned intelligence..."
    iq = r.hgetall("swarm_iq:ReconAgent-1:HIGH")
    logger.info(f"Final Learned Intelligence in Redis: {iq}")

if __name__ == "__main__":
    simulate_attack_sequence()
