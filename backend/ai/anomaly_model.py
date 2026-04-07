import logging

logger = logging.getLogger(__name__)

_model = None
_model_loaded = False

def _load_model():
    global _model, _model_loaded
    if _model_loaded:
        return _model
    _model_loaded = True
    try:
        import numpy as np
        from sklearn.ensemble import IsolationForest
        rng = np.random.default_rng(42)
        X_train = rng.uniform(0, 0.4, size=(200, 3))
        model = IsolationForest(contamination=0.1, random_state=42)
        model.fit(X_train)
        _model = model
        logger.info("[AI] IsolationForest anomaly model ready")
    except Exception as e:
        logger.warning(f"[AI] Could not load ML model: {e} — using heuristic fallback")
        _model = None
    return _model

def predict(data: dict) -> bool:
    """
    Returns True if an anomaly is detected.
    Uses IsolationForest when scikit-learn is available,
    falls back to heuristic scoring otherwise.
    """
    score = float(data.get("anomaly_score", 0.0))
    failed = float(data.get("failed_attempts", 0))
    connections = float(data.get("connections", 0))

    model = _load_model()
    if model is not None:
        try:
            import numpy as np
            norm_failed = min(failed / 200.0, 1.0)
            norm_conn = min(connections / 50.0, 1.0)
            X = np.array([[score, norm_failed, norm_conn]])
            prediction = model.predict(X)
            return int(prediction[0]) == -1
        except Exception as e:
            logger.warning(f"[AI] Model prediction error: {e}")

    return score > 0.75 or failed > 100
