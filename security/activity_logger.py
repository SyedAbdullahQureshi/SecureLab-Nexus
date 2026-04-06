"""Activity logging utility for UI actions."""

from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional


class ActivityLogger:
    def __init__(self, log_path: Path) -> None:
        self.log_path = log_path
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.log_path.exists():
            self.log_path.write_text("[]", encoding="utf-8")

    def log(self, user: str, action: str, detail: str) -> None:
        events = self.read_all()
        events.append(
            {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "user": user or "guest",
                "action": action,
                "detail": detail,
            }
        )
        self.log_path.write_text(json.dumps(events, indent=2), encoding="utf-8")

    def read_all(self) -> List[Dict[str, str]]:
        try:
            return json.loads(self.log_path.read_text(encoding="utf-8"))
        except Exception:
            return []

    def filter_logs(
        self,
        username: str = "",
        action: str = "",
        from_date: str = "",
        to_date: str = "",
    ) -> List[Dict[str, str]]:
        logs = self.read_all()
        user_norm = username.strip().lower()
        action_norm = action.strip().upper()
        from_norm = from_date.strip()
        to_norm = to_date.strip()

        filtered: List[Dict[str, str]] = []
        for item in logs:
            log_user = item.get("user", "").lower()
            log_action = item.get("action", "").upper()
            date_part = item.get("timestamp", "")[:10]

            if user_norm and user_norm not in log_user:
                continue
            if action_norm and action_norm != log_action:
                continue
            if from_norm and date_part < from_norm:
                continue
            if to_norm and date_part > to_norm:
                continue
            filtered.append(item)

        return filtered

    def summary(self) -> Dict[str, int]:
        logs = self.read_all()
        unique_users = {entry.get("user", "guest") for entry in logs}
        lockouts = sum(
            1
            for e in logs
            if e.get("action") == "LOGIN_FAILED" and "locked" in (e.get("detail") or "").lower()
        )
        integrity_failures = sum(
            1
            for e in logs
            if e.get("action") == "INTEGRITY_CHECK" and (e.get("detail") or "").upper() == "FAIL"
        )
        return {
            "total_events": len(logs),
            "unique_users": len(unique_users),
            "encrypt_actions": sum(1 for e in logs if e.get("action") == "ENCRYPT"),
            "decrypt_actions": sum(1 for e in logs if e.get("action") == "DECRYPT"),
            "hash_actions": sum(1 for e in logs if e.get("action") == "HASH"),
            "login_failures": sum(1 for e in logs if e.get("action") == "LOGIN_FAILED"),
            "account_lockouts": lockouts,
            "integrity_check_failures": integrity_failures,
        }

    @staticmethod
    def _entry_timestamp(entry: Dict[str, str]) -> Optional[datetime]:
        try:
            return datetime.strptime(entry.get("timestamp", ""), "%Y-%m-%d %H:%M:%S")
        except ValueError:
            return None

    def threat_window_metrics(self, days: int = 7) -> Dict[str, int]:
        """Trailing-window counts for local threat / abuse indicators."""
        logs = self.read_all()
        cutoff = datetime.now() - timedelta(days=days)
        metrics = {"failed_logins": 0, "lockouts": 0, "integrity_failures": 0}
        for e in logs:
            ts = self._entry_timestamp(e)
            if ts is None or ts < cutoff:
                continue
            action = e.get("action", "")
            detail = (e.get("detail") or "")
            if action == "LOGIN_FAILED":
                metrics["failed_logins"] += 1
                if "locked" in detail.lower():
                    metrics["lockouts"] += 1
            elif action == "INTEGRITY_CHECK" and detail.upper() == "FAIL":
                metrics["integrity_failures"] += 1
        return metrics

    def threat_posture(self, days: int = 7) -> str:
        m = self.threat_window_metrics(days)
        if m["integrity_failures"] > 0 or m["lockouts"] >= 2:
            return "Elevated — review integrity failures and authentication lockouts."
        if m["failed_logins"] >= 5:
            return "Watch — repeated failed authentication attempts."
        return "Normal — no major local indicators in this window."

    def recent_threat_events(self, limit: int = 75) -> List[Dict[str, str]]:
        """Login failures and integrity failures suitable for a monitoring feed."""
        logs = self.read_all()
        flagged: List[Dict[str, str]] = []
        for e in logs:
            action = e.get("action", "")
            detail = (e.get("detail") or "")
            if action == "LOGIN_FAILED":
                flagged.append(e)
            elif action == "INTEGRITY_CHECK" and detail.upper() == "FAIL":
                flagged.append(e)
        return list(reversed(flagged[-limit:]))
