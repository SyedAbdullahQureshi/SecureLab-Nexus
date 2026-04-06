"""Playful notification sounds for user actions in the dashboard."""

from __future__ import annotations

import sys
import threading

if sys.platform == "win32":
    import winsound


class SoundManager:
    """Small non-blocking sound helper with action-specific tone patterns."""

    def __init__(self, enabled: bool = True) -> None:
        self.enabled = enabled

    def play(self, event: str) -> None:
        if not self.enabled:
            return

        threading.Thread(target=self._play_sync, args=(event,), daemon=True).start()

    def _play_sync(self, event: str) -> None:
        if sys.platform != "win32":
            return

        patterns = {
            "encrypt_success": [(880, 100), (1175, 130)],
            "decrypt_success": [(740, 110), (988, 130)],
            "hash_success": [(660, 90), (784, 100), (988, 120)],
            "verify_pass": [(784, 80), (988, 120)],
            "verify_fail": [(392, 170), (330, 180)],
            "keygen_success": [(988, 90), (1319, 130)],
            "login_success": [(523, 90), (659, 100), (784, 120)],
            "login_fail": [(349, 120), (294, 180)],
            "signup_success": [(659, 100), (784, 120)],
            "clipboard": [(988, 70)],
            "warning": [(440, 120)],
            "error": [(294, 180), (247, 220)],
        }

        tone_pattern = patterns.get(event, [(700, 90)])
        for freq, dur in tone_pattern:
            winsound.Beep(freq, dur)
