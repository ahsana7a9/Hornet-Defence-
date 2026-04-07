import socket
import struct
import time
import logging
from collections import defaultdict, deque

logger = logging.getLogger(__name__)

TCP_STATES = {
    "01": "ESTABLISHED", "02": "SYN_SENT", "03": "SYN_RECV",
    "04": "FIN_WAIT1",   "05": "FIN_WAIT2", "06": "TIME_WAIT",
    "07": "CLOSE",       "08": "CLOSE_WAIT","09": "LAST_ACK",
    "0A": "LISTEN",      "0B": "CLOSING"
}

SUSPICIOUS_PORTS = {22, 23, 21, 3306, 5432, 27017, 6379, 9200, 445, 3389, 4444, 1337}
SERVICE_PORTS    = {22: "SSH", 23: "Telnet", 21: "FTP", 80: "HTTP", 443: "HTTPS",
                    3306: "MySQL", 5432: "PostgreSQL", 27017: "MongoDB",
                    6379: "Redis", 9200: "Elasticsearch", 445: "SMB",
                    3389: "RDP", 4444: "Metasploit", 1337: "Backdoor"}

_connection_history = defaultdict(lambda: deque(maxlen=200))
_port_scan_tracker  = defaultdict(set)
_last_stats         = {}

def _hex_to_ip(hex_str: str) -> str:
    try:
        addr = int(hex_str, 16)
        return socket.inet_ntoa(struct.pack("<I", addr))
    except Exception:
        return "0.0.0.0"

def _hex_to_port(hex_str: str) -> int:
    try:
        return int(hex_str, 16)
    except Exception:
        return 0

def _parse_proc_net_tcp(path: str = "/proc/net/tcp") -> list:
    connections = []
    try:
        with open(path, "r") as f:
            lines = f.readlines()[1:]
        for line in lines:
            parts = line.split()
            if len(parts) < 4:
                continue
            local_addr, local_port = parts[1].split(":")
            remote_addr, remote_port = parts[2].split(":")
            state_hex = parts[3]
            connections.append({
                "local_ip":    _hex_to_ip(local_addr),
                "local_port":  _hex_to_port(local_port),
                "remote_ip":   _hex_to_ip(remote_addr),
                "remote_port": _hex_to_port(remote_port),
                "state":       TCP_STATES.get(state_hex.upper(), state_hex),
            })
    except Exception as e:
        logger.warning(f"[NetMon] Cannot read {path}: {e}")
    return connections

def get_live_connections() -> list:
    """Returns all current TCP connections from /proc/net/tcp and /proc/net/tcp6."""
    conns = _parse_proc_net_tcp("/proc/net/tcp")
    conns += _parse_proc_net_tcp("/proc/net/tcp6")
    return conns

def get_network_stats() -> dict:
    """Reads /proc/net/dev for real interface throughput."""
    global _last_stats
    stats = {}
    try:
        with open("/proc/net/dev", "r") as f:
            lines = f.readlines()[2:]
        now = time.time()
        for line in lines:
            parts = line.split()
            if len(parts) < 10:
                continue
            iface = parts[0].strip(":")
            rx_bytes = int(parts[1])
            tx_bytes = int(parts[9])
            if iface in _last_stats:
                elapsed = now - _last_stats[iface]["time"]
                rx_rate = (rx_bytes - _last_stats[iface]["rx"]) / max(elapsed, 1)
                tx_rate = (tx_bytes - _last_stats[iface]["tx"]) / max(elapsed, 1)
            else:
                rx_rate = tx_rate = 0
            _last_stats[iface] = {"rx": rx_bytes, "tx": tx_bytes, "time": now}
            stats[iface] = {
                "rx_bytes":    rx_bytes,
                "tx_bytes":    tx_bytes,
                "rx_rate_kbs": round(rx_rate / 1024, 2),
                "tx_rate_kbs": round(tx_rate / 1024, 2),
            }
    except Exception as e:
        logger.warning(f"[NetMon] Cannot read /proc/net/dev: {e}")
    return stats

def analyze_connections() -> dict:
    """
    Analyse live connections and return threat-relevant metrics.
    Detects: port scans, connection bursts, suspicious ports, SYN floods.
    """
    conns = get_live_connections()
    now   = time.time()

    remote_ips     = defaultdict(list)
    established    = 0
    syn_pending    = 0
    suspicious_hit = []

    for c in conns:
        rip = c["remote_ip"]
        if rip in ("0.0.0.0", "127.0.0.1", "::1", ""):
            continue
        remote_ips[rip].append(c["local_port"])
        if c["state"] == "ESTABLISHED":
            established += 1
        if c["state"] in ("SYN_SENT", "SYN_RECV"):
            syn_pending += 1
        if c["local_port"] in SUSPICIOUS_PORTS and c["state"] == "ESTABLISHED":
            suspicious_hit.append({
                "ip":      rip,
                "port":    c["local_port"],
                "service": SERVICE_PORTS.get(c["local_port"], "unknown")
            })

    # Port-scan detection: one IP touching many different ports
    port_scanners = []
    for ip, ports in remote_ips.items():
        unique_ports = set(ports)
        _port_scan_tracker[ip].update(unique_ports)
        if len(_port_scan_tracker[ip]) >= 5:
            port_scanners.append({"ip": ip, "ports_probed": len(_port_scan_tracker[ip])})

    # Connection-burst detection
    for ip in remote_ips:
        _connection_history[ip].append(now)

    burst_ips = []
    for ip, times in _connection_history.items():
        recent = [t for t in times if now - t < 30]
        if len(recent) >= 10:
            burst_ips.append({"ip": ip, "connections_30s": len(recent)})

    top_talker = max(remote_ips, key=lambda ip: len(remote_ips[ip])) if remote_ips else "none"

    return {
        "total_connections":  len(conns),
        "established":        established,
        "syn_pending":        syn_pending,
        "unique_remote_ips":  len(remote_ips),
        "port_scanners":      port_scanners,
        "burst_ips":          burst_ips,
        "suspicious_hits":    suspicious_hit,
        "top_talker_ip":      top_talker,
        "anomaly_score":      _compute_score(established, syn_pending, port_scanners, burst_ips, suspicious_hit),
    }

def _compute_score(established, syn_pending, port_scanners, burst_ips, suspicious_hits) -> float:
    score = 0.0
    if syn_pending > 20:          score += 0.4
    elif syn_pending > 5:         score += 0.2
    if port_scanners:             score += 0.3 * min(len(port_scanners), 3) / 3
    if burst_ips:                 score += 0.2 * min(len(burst_ips), 3) / 3
    if suspicious_hits:           score += 0.3 * min(len(suspicious_hits), 3) / 3
    return round(min(score, 1.0), 4)
