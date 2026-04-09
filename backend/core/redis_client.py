import redis
import json
import logging
from core.provenance import PROJECT_HASH  # The cryptographic seal

logger = logging.getLogger(__name__)

_redis_client = None

def get_redis():
    global _redis_client
    if _redis_client is None:
        try:
            # decode_responses=True ensures we get strings back from Redis
            client = redis.Redis(host='localhost', port=6379, decode_responses=True, socket_connect_timeout=2)
            client.ping()
            _redis_client = client
            logger.info("[Redis] Connected successfully")
        except Exception as e:
            logger.warning(f"[Redis] Not available: {e} — running without Redis")
            _redis_client = None
    return _redis_client

def publish(channel: str, data: dict):
    r = get_redis()
    if r:
        try:
            r.publish(channel, json.dumps(data))
        except Exception as e:
            logger.warning(f"[Redis] Publish failed: {e}")

def subscribe(channel: str):
    r = get_redis()
    if r:
        try:
            pubsub = r.pubsub()
            pubsub.subscribe(channel)
            return pubsub
        except Exception as e:
            logger.warning(f"[Redis] Subscribe failed: {e}")
    return None

# --- NEW: Reinforcement Learning & Swarm Intelligence Methods ---

def update_q_value(state_key: str, action: str, reward: float):
    """
    Updates the 'Value' of an action in a specific state.
    Formula: Q_new = Q_old + alpha * (reward - Q_old)
    The state_key now includes a cryptographic signature for ownership.
    """
    r = get_redis()
    if not r:
        return

    alpha = 0.1  # Learning rate
    # Ownership Shard: Using the first 8 chars of the Project Hash
    lookup_key = f"swarm_iq:{PROJECT_HASH[:8]}:{state_key}"
    
    try:
        # Get existing knowledge
        current_q = r.hget(lookup_key, action)
        current_q = float(current_q) if current_q else 0.0
        
        # Calculate new intelligence using Bellman-style update
        new_q = current_q + alpha * (reward - current_q)
        
        # Store back in Redis under the cryptographic namespace
        r.hset(lookup_key, action, new_q)
        logger.debug(f"[RL] Updated {lookup_key} -> {action}: {new_q:.2f}")
    except Exception as e:
        logger.error(f"[Redis] RL update failed: {e}")

def get_best_action(state_key: str):
    """
    Queries Redis for the action with the highest Q-value in the owner's namespace.
    """
    r = get_redis()
    if not r:
        return "NONE"

    try:
        # Querying specifically within our cryptographic namespace
        lookup_key = f"swarm_iq:{PROJECT_HASH[:8]}:{state_key}"
        actions = r.hgetall(lookup_key)
        
        if not actions:
            return "NONE"
        
        # Return the action with the highest score
        # Since hgetall with decode_responses=True returns strings, we convert to float
        return max(actions, key=lambda k: float(actions[k]))
    except Exception as e:
        logger.warning(f"[Redis] Action retrieval failed: {e}")
        return "NONE"

def set_pheromone(source_ip: str, strength: int = 100):
    """
    Sets a digital pheromone that 'evaporates' over time.
    Tethered to the owner's signature.
    """
    r = get_redis()
    if r:
        # Namespace pheromones to prevent overlap with other swarm versions
        key = f"pheromone:{PROJECT_HASH[:8]}:{source_ip}"
        # Pheromone lasts for 60 seconds (evaporation/decay)
        r.setex(key, 60, strength)
