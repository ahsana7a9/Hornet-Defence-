import psutil
import time
import logging
from collections import defaultdict, deque

logger = logging.getLogger(__name__)

# Standardizing status strings to match your previous logic
TCP_STATES = {
    psutil.CONN_ESTABLISHED: "ESTABLISHED",
    psutil.CONN_SYN_SENT: "SYN_SENT",
    psutil.CONN_SYN_RECV: "SYN_RECV",
    psutil.CONN_FIN_WAIT1: "FIN_WAIT1",
    psutil.CONN_FIN_WAIT2: "FIN_WAIT2",
    psutil.CONN_TIME_WAIT: "TIME_WAIT",
    psutil.CONN_CLOSE: "CLOSE",
    psutil.CONN_CLOSE_WAIT: "CLOSE_WAIT",
    psutil.CONN_LAST_ACK: "LAST_ACK",
    psutil.CONN_LISTEN: "LISTEN",
    psutil.CONN_CLOSING: "CLOSING",
}

SUSPICIOUS_PORTS = {22, 23, 21, 3306, 5432, 27017, 6379, 9200, 445, 3389, 4444, 1337}
SERVICE_PORTS    = {22: "SSH", 23: "Telnet", 21: "FTP", 80: "HTTP", 443: "HTTPS",
                    3306: "MySQL", 5432: "PostgreSQL", 27017: "MongoDB",
                    6379: "Redis", 9200: "Elasticsearch", 445: "SMB",
                    3389: "RDP", 4444: "Metasploit", 1337: "Backdoor"}

_connection_history = defaultdict(lambda: deque(maxlen=200))
_port_scan_tracker  = defaultdict(set)
_last_stats         = {}

def get_live_connections() -> list:
    """
    Windows-compatible connection monitoring using psutil.
    Replaces /proc/net/tcp parsing.
    """
    connections = []
    try:
        # 'inet' covers both IPv4 and IPv6
        for conn in psutil.net_connections(kind='inet'):
            # Only include connections with a remote address (active traffic)
            if conn.raddr:
                connections.append({
                    "local_ip":    conn.laddr.ip,
                    "local_port":  conn.laddr.port,
                    "remote_ip":   conn.raddr.ip,
                    "remote_port": conn.raddr.port,
                    "state":       TCP_STATES.get(conn.status, conn.status),
                })
    except (psutil.AccessDenied, Exception) as e:
        logger.warning(f"[NetMon] Permission denied or error fetching connections: {e}")
    return connections

def get_network_stats() -> dict:
    """
    Windows-compatible throughput monitoring.
    Replaces /proc/net/dev parsing.
    """
    global _last_stats
    stats = {}
    try:
        # Get I/O stats per network interface
        net_io = psutil.net_io_counters(pernic=True)
        now = time.time()

        for iface, data in net_io.items():
            rx_bytes = data.bytes_recv
            tx_bytes = data.bytes_sent
            
            if iface in _last_stats:
                elapsed = now - _last_stats[iface]["time"]
                rx_rate = (rx_bytes - _last_stats[iface]["rx"]) / max(elapsed, 0.1)
                tx_rate = (tx_bytes - _last_stats[iface]["tx"]) / max(elapsed, 0.1)
            else:
                rx_rate = tx_rate = 0
                
            _last_stats[iface] = {"rx": rx_bytes, "tx": tx_bytes, "time": now}
            
            stats[iface] = {
                "rx_bytes":    rx_bytes,
                "tx_bytes":    tx_bytes,
                "rx_rate_kbs": round(rx_rate / 1024, 2),
                "tx_rate_kbs":
