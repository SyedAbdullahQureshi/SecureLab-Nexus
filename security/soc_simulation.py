from __future__ import annotations

import random
from collections import deque
from dataclasses import dataclass


@dataclass
class SocSimulationConfig:
    tick_ms: int = 2500
    alert_intensity: float = 0.45
    risk_sensitivity: int = 10


class SocSimulator:
    def __init__(self) -> None:
        self.config = SocSimulationConfig()
        self.encryption_activity = 12
        self.active_users = 4
        self.risk_level = 26
        self.activity_series: deque[int] = deque([8, 10, 12, 9, 15, 13, 17, 14], maxlen=20)
        self.encryption_ops = 58
        self.hash_ops = 42
        self.user_activity = {"guest": 8, "admin": 3, "analyst": 5, "operator": 4}

    def set_config(self, tick_ms: int, alert_intensity: float, risk_sensitivity: int) -> None:
        self.config.tick_ms = max(800, min(6000, int(tick_ms)))
        self.config.alert_intensity = max(0.1, min(0.9, float(alert_intensity)))
        self.config.risk_sensitivity = max(1, min(20, int(risk_sensitivity)))

    def ingest_app_event(self, action: str, detail: str) -> None:
        if action in {"ENCRYPT", "ENCRYPT_FILE"}:
            self.encryption_ops += 1
            self.encryption_activity += 1
        if action in {"HASH", "VERIFY", "INTEGRITY_CHECK"}:
            self.hash_ops += 1
        if action in {"LOGIN", "SIGNUP"}:
            self.active_users = min(35, self.active_users + 1)
        if action == "LOGIN_FAILED":
            self.risk_level = min(100, self.risk_level + 6)
        if action == "INTEGRITY_CHECK" and "FAIL" in detail.upper():
            self.risk_level = min(100, self.risk_level + 10)

    def step(self) -> dict[str, object]:
        self.encryption_activity += random.randint(0, 3)
        self.active_users = max(1, min(35, self.active_users + random.choice([-1, 0, 1, 2])))

        base = self.activity_series[-1] if self.activity_series else 10
        drift = random.randint(-4, 7)
        next_value = max(3, min(40, base + drift + (self.risk_level // 20)))
        self.activity_series.append(next_value)

        self.user_activity["guest"] = max(1, self.user_activity["guest"] + random.choice([-1, 0, 1]))
        self.user_activity["admin"] = max(1, self.user_activity["admin"] + random.choice([0, 1]))
        self.user_activity["analyst"] = max(1, self.user_activity["analyst"] + random.choice([-1, 0, 2]))
        self.user_activity["operator"] = max(1, self.user_activity["operator"] + random.choice([-1, 0, 1]))

        info = [
            ("INFO", "Operator session token refreshed", "info"),
            ("INFO", "Encryption queue processed", "info"),
            ("INFO", "Endpoint heartbeat validated", "info"),
        ]
        warning = [
            ("WARN", "Multiple failed auth attempts detected", "warning"),
            ("WARN", "Suspicious login velocity observed", "warning"),
            ("WARN", "Lateral movement indicator heuristic raised", "warning"),
        ]
        critical = [
            ("CRIT", "Brute-force signature matched", "critical"),
            ("CRIT", "Anomalous privilege escalation pattern", "critical"),
            ("CRIT", "Potential data exfiltration channel flagged", "critical"),
        ]

        critical_weight = self.config.alert_intensity
        warning_weight = min(0.7, 0.25 + (self.config.alert_intensity * 0.5))
        info_weight = max(0.1, 1.0 - critical_weight - warning_weight)

        bucket = random.choices(
            ["info", "warning", "critical"],
            [info_weight, warning_weight, critical_weight],
            k=1,
        )[0]
        if bucket == "critical":
            code, message, severity = random.choice(critical)
            delta = random.randint(8, 15) + self.config.risk_sensitivity // 2
            self.risk_level = min(100, self.risk_level + delta)
        elif bucket == "warning":
            code, message, severity = random.choice(warning)
            delta = random.randint(3, 8) + self.config.risk_sensitivity // 4
            self.risk_level = min(100, self.risk_level + delta)
        else:
            code, message, severity = random.choice(info)
            decay = random.randint(1, 4) + max(1, (10 - self.config.risk_sensitivity) // 3)
            self.risk_level = max(12, self.risk_level - decay)

        if random.random() < 0.52:
            self.encryption_ops += random.randint(1, 3)
        if random.random() < 0.47:
            self.hash_ops += random.randint(1, 3)

        notify = severity == "critical" or (severity == "warning" and random.random() < self.config.alert_intensity)

        return {
            "code": code,
            "message": message,
            "severity": severity,
            "notify": notify,
            "risk_level": self.risk_level,
            "encryption_activity": self.encryption_activity,
            "active_users": self.active_users,
        }
