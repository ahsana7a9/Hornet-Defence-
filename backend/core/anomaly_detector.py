import logging
from ai.anomaly_model import predict

logger = logging.getLogger(__name__)

def detect_anomaly(data: dict) -> bool:
    try:
        return predict(data)
    except Exception as e:
        logger.warning(f"[Anomaly] Detection error: {e}")
        return False
