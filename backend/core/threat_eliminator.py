import subprocess
import time
import logging
import os
from collections import OrderedDict

logger = logging.getLogger(__name__)

_blocked_ips: OrderedDict = OrderedDict()
_action_log: list = []
_MAX_LOG = 200


def _run(cmd: list) -> tuple:
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
        return result.returncode == 0, result.stdout + result.stderr
    except Exception as e:
        return False, str(e)


def block_ip(ip: str, reason: str = "threat detected") -> dict:
    """Block an IP via iptables (real server) or in-memory (demo/container)."""
    if ip in _blocked_ips:
        return {"success": False, "message": f"{ip} is already blocked"}

    timestamp = time.time()
    result = {"ip": ip, "reason": reason, "timestamp": timestamp}

    # Try real iptables first
    ok, out = _run(["iptables", "-A", "INPUT", "-s", ip, "-j", "DROP"])
    if ok:
        result["method"] = "iptables"
        result["success"] = True
        logger.info(f"[Eliminator] BLOCKED via iptables: {ip} ({reason})")
    else:
        # Fallback: in-memory block list (works in containers)
        result["method"] = "in-memory"
        result["success"] = True
        logger.info(f"[Eliminator] BLOCKED in-memory: {ip} ({reason}) [iptables unavailable]")

    _blocked_ips[ip] = result
    _log_action("BLOCK", ip, reason, result["method"])
    return result


def unblock_ip(ip: str) -> dict:
    """Remove an IP block."""
    if ip not in _blocked_ips:
        return {"success": False, "message": f"{ip} was not blocked"}

    # Try iptables removal
    ok, _ = _run(["iptables", "-D", "INPUT", "-s", ip, "-j", "DROP"])
    del _blocked_ips[ip]
    _log_action("UNBLOCK", ip, "manual unblock", "iptables" if ok else "in-memory")
    logger.info(f"[Eliminator] UNBLOCKED: {ip}")
    return {"success": True, "ip": ip}


def kill_process(pid: int, reason: str = "suspicious process") -> dict:
    """Terminate a process by PID."""
    try:
        import psutil
        proc = psutil.Process(pid)
        name = proc.name()
        proc.terminate()
        _log_action("KILL", f"PID:{pid} ({name})", reason, "psutil")
        logger.info(f"[Eliminator] KILLED process {pid} ({name}): {reason}")
        return {"success": True, "pid": pid, "name": name}
    except Exception as e:
        logger.warning(f"[Eliminator] Cannot kill PID {pid}: {e}")
        return {"success": False, "pid": pid, "error": str(e)}


def is_blocked(ip: str) -> bool:
    return ip in _blocked_ips


def get_blocked_ips() -> list:
    return list(_blocked_ips.values())


def get_action_log(limit: int = 50) -> list:
    return _action_log[-limit:]


def _log_action(action: str, target: str, reason: str, method: str):
    entry = {
        "action":    action,
        "target":    target,
        "reason":    reason,
        "method":    method,
        "timestamp": time.time(),
    }
    _action_log.append(entry)
    if len(_action_log) > _MAX_LOG:
        _action_log.pop(0)
