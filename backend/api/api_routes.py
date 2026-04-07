from fastapi import APIRouter, Depends, HTTPException, Query
from core.auth import verify_token
from core.elasticsearch_client import log_event, search_events
from core.threat_eliminator import (
    block_ip, unblock_ip, get_blocked_ips,
    get_action_log, kill_process, is_blocked
)
from core.alert_manager import get_alerts, get_alert_counts, add_alert
from core.network_monitor import analyze_connections, get_network_stats
from pydantic import BaseModel

router = APIRouter()


# ── Status ──────────────────────────────────────────────────────────────────
@router.get("/status")
def get_status():
    return {"status": "operational", "system": "Hornet-Defence"}


# ── Threat Logs ─────────────────────────────────────────────────────────────
@router.get("/logs/public")
def get_logs_public():
    """Recent threats — no auth required (for dashboard)."""
    try:
        return search_events("threats", size=50)
    except Exception:
        return []


@router.get("/logs", dependencies=[Depends(verify_token)])
def get_logs_secure():
    """Recent threats — JWT required."""
    try:
        return search_events("threats", size=100)
    except Exception as e:
        return {"error": str(e), "logs": []}


# ── Network Analysis ─────────────────────────────────────────────────────────
@router.get("/network/live")
def get_live_network():
    """Live connection analysis from /proc/net/tcp."""
    try:
        return analyze_connections()
    except Exception as e:
        return {"error": str(e)}


@router.get("/network/stats")
def get_net_stats():
    """Real-time network interface throughput."""
    try:
        return get_network_stats()
    except Exception as e:
        return {"error": str(e)}


# ── Blocked IPs ──────────────────────────────────────────────────────────────
@router.get("/blocked")
def get_blocked():
    """List all currently blocked IPs."""
    return get_blocked_ips()


class BlockRequest(BaseModel):
    ip:     str
    reason: str = "manual block"

@router.post("/block", dependencies=[Depends(verify_token)])
def manual_block(req: BlockRequest):
    """Manually block an IP."""
    if is_blocked(req.ip):
        raise HTTPException(status_code=409, detail=f"{req.ip} is already blocked")
    result = block_ip(req.ip, reason=req.reason)
    add_alert("HIGH", f"Manual block: {req.ip} — {req.reason}", source="admin")
    return result


@router.delete("/block/{ip}", dependencies=[Depends(verify_token)])
def manual_unblock(ip: str):
    """Unblock an IP."""
    result = unblock_ip(ip)
    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["message"])
    add_alert("INFO", f"IP {ip} unblocked by admin", source="admin")
    return result


# ── Process Control ──────────────────────────────────────────────────────────
@router.delete("/process/{pid}", dependencies=[Depends(verify_token)])
def terminate_process(pid: int):
    """Kill a suspicious process by PID."""
    result = kill_process(pid, reason="admin termination")
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result.get("error"))
    return result


# ── Alerts ───────────────────────────────────────────────────────────────────
@router.get("/alerts")
def get_alert_feed(
    limit: int = Query(50, ge=1, le=200),
    min_severity: str = Query("INFO")
):
    """Get recent alerts with optional severity filter."""
    return get_alerts(limit=limit, min_severity=min_severity)


@router.get("/alerts/counts")
def alert_counts():
    return get_alert_counts()


# ── Action Log ───────────────────────────────────────────────────────────────
@router.get("/actions")
def get_actions(limit: int = Query(50, ge=1, le=200)):
    """History of all block/unblock/kill actions."""
    return get_action_log(limit=limit)


# ── Auth test ────────────────────────────────────────────────────────────────
@router.get("/secure", dependencies=[Depends(verify_token)])
def secure_test():
    return {"msg": "Secure access granted to the Hornet Hive"}
