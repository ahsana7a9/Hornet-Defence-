import time
import logging
import random
from core.network_monitor import analyze_connections, get_network_stats
from agents.agent_brain import AgentBrain  # Import the new brain

logger = logging.getLogger(__name__)


class ReconAgent:
    """
    Reconnaissance agent — monitors real TCP connections via /proc/net/tcp.
    Now enhanced with MARL (Reinforcement Learning) and LLM Reasoning.
    """

    def __init__(self, agent_id: int):
        self.id   = agent_id
        self.name = f"ReconAgent-{agent_id}"
        self._use_real = self._check_real()
        # Initialize the AI Brain
        self.brain = AgentBrain()

    def _check_real(self) -> bool:
        try:
            with open("/proc/net/tcp", "r"):
                logger.info(f"[{self.name}] Real network monitoring enabled via /proc/net/tcp")
                return True
        except Exception:
            logger.warning(f"[{self.name}] /proc/net/tcp unavailable — using simulation")
            return False

    def collect_data(self) -> dict:
        """Collects data and appends a suggested_action from the AI brain."""
        if self._use_real:
            data = self._collect_real()
        else:
            data = self._collect_simulated()
        
        # --- NEW MARL STEP ---
        # Delegate decision making to the Brain (Redis Intelligence or LLM)
        suggested_action = self.brain.decide(self.name, data)
        data["suggested_action"] = suggested_action
        
        return data

    def _collect_real(self) -> dict:
        try:
            analysis    = analyze_connections()
            net_stats   = get_network_stats()
            eth_stats   = net_stats.get("eth0", {})

            source = "network"
            if analysis["port_scanners"]:
                source = analysis["port_scanners"][0]["ip"]
            elif analysis["burst_ips"]:
                source = analysis["burst_ips"][0]["ip"]
            elif analysis["suspicious_hits"]:
                source = analysis["suspicious_hits"][0]["ip"]

            return {
                "agent":              self.name,
                "source":             source,
                "timestamp":          time.time(),
                "type":               "recon",
                "real_data":          True,
                "total_connections":  analysis["total_connections"],
                "established":        analysis["established"],
                "syn_pending":        analysis["syn_pending"],
                "unique_remote_ips":  analysis["unique_remote_ips"],
                "port_scanners":      analysis["port_scanners"],
                "burst_ips":          analysis["burst_ips"],
                "suspicious_hits":    analysis["suspicious_hits"],
                "rx_rate_kbs":        eth_stats.get("rx_rate_kbs", 0),
                "tx_rate_kbs":        eth_stats.get("tx_rate_kbs", 0),
                "anomaly_score":      analysis["anomaly_score"],
            }
        except Exception as e:
            logger.warning(f"[{self.name}] Real collection error: {e} — falling back")
            self._use_real = False
            return self._collect_simulated()

    def _collect_simulated(self) -> dict:
        sources = ["192.168.1.1", "10.0.0.5", "172.16.0.20", "external-host-1", "external-host-2"]
        return {
            "agent":             self.name,
            "source":            random.choice(sources),
            "timestamp":         time.time(),
            "type":              "recon",
            "real_data":         False,
            "connections":       random.randint(1, 50),
            "suspicious_ports":  random.sample([22, 80, 443, 8080, 3306, 5432], k=random.randint(0, 3)),
            "anomaly_score":     round(random.uniform(0, 1), 4),
        }

    def respond(self, target: str):
        from core.threat_eliminator import block_ip, is_blocked
        from core.alert_manager import add_alert

        if not is_blocked(target):
            logger.info(f"[{self.name}] Responding to threat at: {target}")
            block_ip(target, reason=f"detected by {self.name}")
            add_alert("HIGH", f"IP {target} blocked by {self.name}", source=self.name,
                      metadata={"ip": target})
        else:
            logger.info(f"[{self.name}] Target {target} already blocked — skipping")
