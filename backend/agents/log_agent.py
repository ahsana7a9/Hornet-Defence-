import os
import time
import logging
import glob
import re
from collections import defaultdict

logger = logging.getLogger(__name__)

SUSPICIOUS_PROCS = {
    "nmap", "masscan", "hydra", "medusa", "john", "hashcat",
    "metasploit", "msfconsole", "sqlmap", "nikto", "gobuster",
    "netcat", "nc", "socat", "tcpdump", "wireshark", "ettercap"
}

LOG_PATHS = [
    "/var/log/auth.log",
    "/var/log/secure",
    "/var/log/syslog",
    "/var/log/messages",
    "/var/log/nginx/access.log",
    "/var/log/apache2/access.log",
]

FAIL_PATTERNS = [
    re.compile(r"Failed password for .+ from ([\d.]+)"),
    re.compile(r"Invalid user .+ from ([\d.]+)"),
    re.compile(r"authentication failure.*rhost=([\d.]+)"),
    re.compile(r"BREAK-IN ATTEMPT from ([\d.]+)"),
]


class LogAgent:
    """
    System log monitoring agent.
    - Reads real auth/system logs for intrusion patterns
    - Scans running processes for known attack tools
    - Monitors /proc/net/arp for ARP anomalies
    """

    def __init__(self, agent_id: int):
        self.id          = agent_id
        self.name        = f"LogAgent-{agent_id}"
        self._log_offsets: dict = {}
        self._readable_logs = self._find_readable_logs()
        logger.info(f"[{self.name}] Readable log files: {self._readable_logs}")

    def _find_readable_logs(self) -> list:
        readable = []
        for path in LOG_PATHS:
            try:
                with open(path, "r") as f:
                    f.read(1)
                readable.append(path)
            except Exception:
                pass
        return readable

    def collect_data(self) -> dict:
        failed_ips  = self._scan_logs()
        sus_procs   = self._scan_processes()
        arp_anomaly = self._scan_arp()

        total_failed = sum(failed_ips.values()) if failed_ips else 0
        worst_ip     = max(failed_ips, key=failed_ips.get) if failed_ips else "none"
        anomaly      = 0.0

        if failed_ips:      anomaly += 0.4 * min(total_failed / 20.0, 1.0)
        if sus_procs:       anomaly += 0.4
        if arp_anomaly:     anomaly += 0.2

        source = worst_ip if worst_ip != "none" else (
            sus_procs[0]["name"] if sus_procs else "system"
        )

        return {
            "agent":              self.name,
            "source":             source,
            "timestamp":          time.time(),
            "type":               "log_analysis",
            "real_data":          True,
            "failed_logins":      dict(failed_ips),
            "total_failed":       total_failed,
            "suspicious_procs":   sus_procs,
            "arp_anomalies":      arp_anomaly,
            "anomaly_score":      round(min(anomaly, 1.0), 4),
        }

    def _scan_logs(self) -> dict:
        """Read new lines from auth logs and extract attacker IPs."""
        failed: dict = defaultdict(int)
        for path in self._readable_logs:
            try:
                offset = self._log_offsets.get(path, 0)
                with open(path, "r", errors="replace") as f:
                    f.seek(offset)
                    new_lines = f.readlines()
                    self._log_offsets[path] = f.tell()
                for line in new_lines:
                    for pattern in FAIL_PATTERNS:
                        m = pattern.search(line)
                        if m:
                            failed[m.group(1)] += 1
            except Exception as e:
                logger.debug(f"[{self.name}] Log read error {path}: {e}")
        return dict(failed)

    def _scan_processes(self) -> list:
        """Check running processes for known attack tools."""
        found = []
        try:
            for pid_dir in glob.glob("/proc/[0-9]*/cmdline"):
                try:
                    with open(pid_dir, "r") as f:
                        cmdline = f.read().replace("\x00", " ").strip()
                    if not cmdline:
                        continue
                    proc_name = cmdline.split()[0].split("/")[-1].lower()
                    if proc_name in SUSPICIOUS_PROCS:
                        pid = int(pid_dir.split("/")[2])
                        found.append({"pid": pid, "name": proc_name, "cmdline": cmdline[:100]})
                except Exception:
                    pass
        except Exception as e:
            logger.debug(f"[{self.name}] Process scan error: {e}")
        return found

    def _scan_arp(self) -> list:
        """Read ARP table for duplicate MAC addresses (ARP spoofing indicator)."""
        anomalies = []
        try:
            with open("/proc/net/arp", "r") as f:
                lines = f.readlines()[1:]
            mac_to_ips: dict = defaultdict(list)
            for line in lines:
                parts = line.split()
                if len(parts) >= 4:
                    ip, mac = parts[0], parts[3]
                    if mac not in ("00:00:00:00:00:00", ""):
                        mac_to_ips[mac].append(ip)
            for mac, ips in mac_to_ips.items():
                if len(ips) > 1:
                    anomalies.append({"mac": mac, "ips": ips, "type": "ARP_SPOOF_SUSPECT"})
        except Exception as e:
            logger.debug(f"[{self.name}] ARP scan error: {e}")
        return anomalies

    def respond(self, target: str):
        from core.threat_eliminator import block_ip, is_blocked
        from core.alert_manager import add_alert

        if not is_blocked(target):
            logger.info(f"[{self.name}] Responding to log-detected threat: {target}")
            block_ip(target, reason=f"log pattern match by {self.name}")
            add_alert("HIGH", f"Log-detected attacker {target} blocked",
                      source=self.name, metadata={"ip": target})
