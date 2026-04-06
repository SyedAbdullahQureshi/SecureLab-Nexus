"""Simple local authentication manager with salted password hashing."""

from __future__ import annotations

import base64
import hashlib
import json
import secrets
import time
from pathlib import Path
from typing import Dict, List, Tuple, TypedDict, cast


class UserRecord(TypedDict):
    salt: str
    password_hash: str
    role: str


COMMON_PASSWORDS = {
    "password",
    "password123",
    "12345678",
    "qwerty123",
    "admin123",
    "letmein",
    "welcome123",
    "iloveyou",
}


class AuthManager:
    """Handle signup/login with PBKDF2-HMAC hashed passwords."""

    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._users: Dict[str, UserRecord] = self._load_users()
        self._failed_attempts: Dict[str, int] = {}
        self._locked_until: Dict[str, float] = {}
        self.max_attempts = 3
        self.lock_seconds = 45

    def _load_users(self) -> Dict[str, UserRecord]:
        if not self.db_path.exists():
            return {}

        try:
            raw_obj = json.loads(self.db_path.read_text(encoding="utf-8"))
            if not isinstance(raw_obj, dict):
                return {}
            raw = cast(Dict[str, object], raw_obj)

            users: Dict[str, UserRecord] = {}
            for username, value in raw.items():
                if not isinstance(value, dict):
                    continue
                value_dict = cast(Dict[str, object], value)
                salt = value_dict.get("salt")
                pw_hash = value_dict.get("password_hash")
                role = value_dict.get("role", "user")
                if isinstance(salt, str) and isinstance(pw_hash, str) and isinstance(role, str):
                    users[username] = cast(UserRecord, {"salt": salt, "password_hash": pw_hash, "role": role})
            return users
        except Exception:
            return {}

    def _save_users(self) -> None:
        self.db_path.write_text(json.dumps(self._users, indent=2), encoding="utf-8")

    @staticmethod
    def _hash_password(password: str, salt: bytes | None = None) -> Tuple[str, str]:
        if salt is None:
            salt = secrets.token_bytes(16)

        digest = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            210_000,
        )
        return (
            base64.b64encode(salt).decode("ascii"),
            base64.b64encode(digest).decode("ascii"),
        )

    @staticmethod
    def _password_strength(password: str) -> int:
        score = 0
        if len(password) >= 8:
            score += 1
        if any(ch.isupper() for ch in password):
            score += 1
        if any(ch.isdigit() for ch in password):
            score += 1
        if any(not ch.isalnum() for ch in password):
            score += 1
        return score

    @staticmethod
    def _password_policy_error(password: str) -> str | None:
        if len(password) < 8:
            return "Password must be at least 8 characters long."
        if password.lower() in COMMON_PASSWORDS:
            return "Password is too common. Choose a stronger one."
        if not any(ch.isupper() for ch in password):
            return "Password must include at least one uppercase letter."
        if not any(ch.isdigit() for ch in password):
            return "Password must include at least one digit."
        if not any(not ch.isalnum() for ch in password):
            return "Password must include at least one special character."
        return None

    def signup(self, username: str, password: str, requested_role: str = "user", created_by: str | None = None) -> Tuple[bool, str]:
        username = username.strip().lower()
        requested_role = requested_role.strip().lower()

        if len(username) < 3:
            return False, "Username must be at least 3 characters long."
        policy_error = self._password_policy_error(password)
        if policy_error:
            return False, policy_error
        if username in self._users:
            return False, "Username already exists."
        if requested_role not in {"admin", "user"}:
            return False, "Invalid role selected."

        # First registered account becomes admin to bootstrap the system.
        role = "admin" if not self._users else requested_role
        if role == "admin" and self._users:
            creator_role = self.get_role((created_by or "").strip().lower())
            if creator_role != "admin":
                return False, "Only an admin can create another admin account."

        salt, pw_hash = self._hash_password(password)
        self._users[username] = {"salt": salt, "password_hash": pw_hash, "role": role}
        self._save_users()
        return True, f"Signup successful. Role assigned: {role}."

    def login(self, username: str, password: str) -> Tuple[bool, str]:
        username = username.strip().lower()
        user = self._users.get(username)

        if not user:
            return False, "User not found."

        now = time.time()
        locked_until = self._locked_until.get(username, 0)
        if locked_until > now:
            wait_seconds = int(locked_until - now)
            return False, f"Account temporarily locked. Try again in {wait_seconds} seconds."

        salt = base64.b64decode(user["salt"].encode("ascii"))
        _, computed_hash = self._hash_password(password, salt=salt)

        if secrets.compare_digest(computed_hash, user["password_hash"]):
            self._failed_attempts[username] = 0
            self._locked_until[username] = 0
            return True, "Login successful. Welcome back."

        attempts = self._failed_attempts.get(username, 0) + 1
        self._failed_attempts[username] = attempts
        if attempts >= self.max_attempts:
            self._locked_until[username] = now + self.lock_seconds
            self._failed_attempts[username] = 0
            return False, f"Too many failed attempts. Account locked for {self.lock_seconds} seconds."

        return False, "Nice try! But this system is more secure than your crush's heart."

    def get_role(self, username: str) -> str:
        user = self._users.get(username.strip().lower())
        if not user:
            return "guest"
        return user.get("role", "user")

    def list_users(self) -> List[Tuple[str, str]]:
        return [(username, record.get("role", "user")) for username, record in self._users.items()]

    def password_strength_label(self, password: str) -> str:
        score = self._password_strength(password)
        if score <= 1:
            return "weak"
        if score == 2:
            return "medium"
        if score == 3:
            return "strong"
        return "very strong"
