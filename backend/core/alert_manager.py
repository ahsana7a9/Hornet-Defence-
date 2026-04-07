import time
import logging
import os
from collections import deque

logger = logging.getLogger(__name__)

LEVELS = ("INFO", "WARNING", "HIGH", "CRITICAL")
_alerts: deque = deque(maxlen=500)


def add_alert(severity: str, message: str, source: str = "system", metadata: dict = None) -> dict:
    severity = severity.upper()
    if severity not in LEVELS:
        severity = "INFO"

    alert = {
        "id":        len(_alerts) + 1,
        "severity":  severity,
        "message":   message,
        "source":    source,
        "timestamp": time.time(),
        "metadata":  metadata or {},
    }
    _alerts.appendleft(alert)
    logger.info(f"[Alert] [{severity}] {source}: {message}")

    # Try Slack webhook if configured
    _try_slack(alert)
    return alert


def get_alerts(limit: int = 50, min_severity: str = "INFO") -> list:
    min_idx = LEVELS.index(min_severity.upper()) if min_severity.upper() in LEVELS else 0
    return [a for a in list(_alerts)[:limit] if LEVELS.index(a["severity"]) >= min_idx]


def get_alert_counts() -> dict:
    counts = {lvl: 0 for lvl in LEVELS}
    for a in _alerts:
        counts[a["severity"]] += 1
    return counts


def _try_slack(alert: dict):
    """Send to Slack if SLACK_WEBHOOK_URL env var is set."""
    webhook = os.getenv("SLACK_WEBHOOK_URL")
    if not webhook:
        return
    try:
        import requests
        emoji = {"INFO": "ℹ️", "WARNING": "⚠️", "HIGH": "🚨", "CRITICAL": "🔴"}.get(alert["severity"], "🔔")
        requests.post(webhook, json={
            "text": f"{emoji} *[{alert['severity']}]* {alert['source']}: {alert['message']}"
        }, timeout=3)
    except Exception as e:
        logger.warning(f"[Alert] Slack notification failed: {e}")
