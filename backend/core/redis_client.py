import redis
import json
import logging

logger = logging.getLogger(__name__)

_redis_client = None

def get_redis():
    global _redis_client
    if _redis_client is None:
        try:
            # Added decode_responses=True to handle strings easily
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
    """
    r = get_redis()
    if not r:
        return

    alpha = 0.1  # Learning rate
    lookup_key = f"swarm_iq:{state_key}"
    
    try:
        # Get existing knowledge
        current_q = r.hget(lookup_key, action)
        current_q = float(current_q) if current_q else 0.0
        
        # Calculate new intelligence
        new_q = current_q + alpha * (reward - current_q)
        
        # Store back in Redis
        r.hset(lookup_key, action, new_q)
        logger.debug(f"[RL] Updated {state_key} -> {action}: {new_q:.2f}")
    except Exception as e:
        logger.error(f"[Redis] RL update failed: {e}")

def get_best_action(state_key: str):
    """
    Queries Redis for the action with the highest Q-value for this state.
    """
    r = get_redis()
    if not r:
        return "NONE"

    try:
        actions = r.hgetall(f"swarm_iq:{state_key}")
        if not actions:
            return "NONE"
        
        # Return the action with the highest score
        return max(actions, key=actions.get)
    except Exception:
        return "NONE"

def set_pheromone(source_ip: str, strength: int = 100):
    """
    Sets a digital pheromone that 'evaporates' over time.
    """
    r = get_redis()
    if r:
        # Pheromone lasts for 60 seconds (evaporation)
        r.setex(f"pheromone:{source_ip}", 60, strength)
