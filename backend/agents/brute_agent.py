import time
import logging
import random
from collections import defaultdict, deque
from core.network_monitor import get_live_connections

logger = logging.getLogger(__name__)

BRUTE_PORTS  = {22: "SSH", 21: "FTP", 23: "Telnet", 3389: "RDP",
                80: "HTTP", 443: "HTTPS", 3306: "MySQL", 5432: "PostgreSQL"}
BRUTE_THRESH = 5   # connections from same IP to same port in 60s = brute force


class BruteAgent:
    """
    Brute-force detection agent — tracks repeated connections per IP/port.
    Uses real /proc/net/tcp data, falls back to simulation.
    """

    def __init__(self, agent_id: int):
        self.id      = agent_id
        self.name    = f"BruteAgent-{agent_id}"
        self._history: dict = defaultdict(lambda: deque(maxlen=500))
        self._use_real = self._check_real()

    def _check_real(self) -> bool:
        try:
            with open("/proc/net/tcp", "r"):
                logger.info(f"[{self.name}] Real brute-force detection enabled")
                return True
        except Exception:
            logger.warning(f"[{self.name}] /proc/net/tcp unavailable — using simulation")
            return False

    def collect_data(self) -> dict:
        if self._use_real:
            return self._collect_real()
        return self._collect_simulated()

    def _collect_real(self) -> dict:
        try:
            conns = get_live_connections()
            now   = time.time()
            ip_port_counts: dict = defaultdict(int)

            for c in conns:
                rip  = c["remote_ip"]
                lport = c["local_port"]
                if rip in ("0.0.0.0", "127.0.0.1", "::1", "") or lport not in BRUTE_PORTS:
                    continue
                key = (rip, lport)
                self._history[key].append(now)
                recent = [t for t in self._history[key] if now - t < 60]
                ip_port_counts[key] = len(recent)

            # Find brute-force candidates
            brute_attempts = [
                {
                    "ip":      k[0],
                    "port":    k[1],
                    "service": BRUTE_PORTS[k[1]],
                    "attempts": v,
                }
                for k, v in ip_port_counts.items() if v >= BRUTE_THRESH
            ]

            # Total failed attempts across all tracked pairs
            total_failed = sum(ip_port_counts.values())
            worst        = max(ip_port_counts, key=ip_port_counts.get) if ip_port_counts else None
            source       = worst[0] if worst else "network"
            service      = BRUTE_PORTS.get(worst[1], "unknown") if worst else "none"
            count        = ip_port_counts.get(worst, 0) if worst else 0

            anomaly = min(total_failed / 50.0, 1.0) if total_failed > 0 else 0.0

            return {
                "agent":           self.name,
                "source":          source,
                "timestamp":       now,
                "type":            "brute_force",
                "real_data":       True,
                "failed_attempts": total_failed,
                "targeted_service": service,
                "brute_attempts":  brute_attempts,
                "worst_offender":  source,
                "worst_count":     count,
                "anomaly_score":   round(anomaly, 4),
            }
        except Exception as e:
            logger.warning(f"[{self.name}] Real collection error: {e} — falling back")
            self._use_real = False
            return self._collect_simulated()

    def _collect_simulated(self) -> dict:
        sources = ["attacker-node-1", "attacker-node-2", "203.0.113.10", "198.51.100.42"]
        return {
            "agent":             self.name,
            "source":            random.choice(sources),
            "timestamp":         time.time(),
            "type":              "brute_force",
            "real_data":         False,
            "failed_attempts":   random.randint(0, 200),
            "targeted_service":  random.choice(["ssh", "http", "ftp", "rdp"]),
            "anomaly_score":     round(random.uniform(0, 1), 4),
        }

    def respond(self, target: str):
        from core.threat_eliminator import block_ip, is_blocked
        from core.alert_manager import add_alert

        if not is_blocked(target):
            logger.info(f"[{self.name}] Blocking brute-force source: {target}")
            block_ip(target, reason=f"brute-force detected by {self.name}")
            add_alert("CRITICAL", f"Brute-force source {target} blocked", source=self.name,
                      metadata={"ip": target, "action": "block"})
        else:
            logger.info(f"[{self.name}] {target} already blocked")
