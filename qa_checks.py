from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from security.activity_logger import ActivityLogger
from security.auth_manager import AuthManager
from security.crypto_utils import decrypt_text, encrypt_text, generate_secure_key
from security.hash_utils import generate_sha256, verify_sha256


class SecurityProjectChecks(unittest.TestCase):
    def test_encrypt_decrypt_roundtrip_multiple_inputs(self) -> None:
        key = "StrongPassphrase123!"
        samples = [
            "hello",
            "Confidentiality test 123",
            "Symbols !@#$%^&*() and spaces",
            "Unicode sample: Pakistan India security",
            "Line1\nLine2\nLine3",
        ]

        for text in samples:
            token = encrypt_text(text, key)
            plain = decrypt_text(token, key)
            self.assertEqual(plain, text)
            self.assertNotEqual(token, text)

    def test_decrypt_with_wrong_key_fails(self) -> None:
        token = encrypt_text("secret", "CorrectKey123")
        with self.assertRaises(ValueError):
            decrypt_text(token, "WrongKey123")

    def test_malformed_payload_fails(self) -> None:
        with self.assertRaises(ValueError):
            decrypt_text("not-valid-base64", "Passphrase123")

    def test_key_generator_lengths(self) -> None:
        key_16 = generate_secure_key(16)
        key_48 = generate_secure_key(48)
        self.assertGreaterEqual(len(key_16), 16)
        self.assertGreaterEqual(len(key_48), 48)

    def test_hash_generator(self) -> None:
        text = "integrity"
        digest = generate_sha256(text)
        self.assertEqual(len(digest), 64)
        self.assertTrue(verify_sha256(text, digest))
        self.assertFalse(verify_sha256("tampered", digest))

    def test_auth_flow_and_password_hashing(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            db_path = Path(td) / "users.json"
            auth = AuthManager(db_path)

            ok, _ = auth.signup("student", "StrongPass9!")
            self.assertTrue(ok)
            self.assertEqual(auth.get_role("student"), "admin")

            user_ok, _ = auth.signup("member", "StrongPass9!", requested_role="user", created_by="student")
            self.assertTrue(user_ok)
            self.assertEqual(auth.get_role("member"), "user")

            dup_ok, _ = auth.signup("student", "StrongPass9!")
            self.assertFalse(dup_ok)

            login_ok, _ = auth.login("student", "StrongPass9!")
            self.assertTrue(login_ok)

            bad_login_ok, _ = auth.login("student", "wrongpass")
            self.assertFalse(bad_login_ok)

    def test_password_policy_hardening(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            db_path = Path(td) / "users.json"
            auth = AuthManager(db_path)

            weak_ok, weak_msg = auth.signup("weakuser", "password123")
            self.assertFalse(weak_ok)
            self.assertIn("common", weak_msg.lower())

            no_special_ok, no_special_msg = auth.signup("weakuser2", "StrongPass9")
            self.assertFalse(no_special_ok)
            self.assertIn("special", no_special_msg.lower())

    def test_login_lockout_after_three_failures(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            db_path = Path(td) / "users.json"
            auth = AuthManager(db_path)

            ok, _ = auth.signup("guard", "StrongPass9!")
            self.assertTrue(ok)

            self.assertFalse(auth.login("guard", "bad1")[0])
            self.assertFalse(auth.login("guard", "bad2")[0])
            lock_ok, lock_msg = auth.login("guard", "bad3")
            self.assertFalse(lock_ok)
            self.assertIn("locked", lock_msg.lower())

    def test_activity_log_filters(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            log_path = Path(td) / "activity.json"
            logger = ActivityLogger(log_path)
            logger.log("alice", "ENCRYPT", "done")
            logger.log("bob", "LOGIN_FAILED", "bad password")

            enc = logger.filter_logs(action="ENCRYPT")
            self.assertEqual(len(enc), 1)
            self.assertEqual(enc[0]["user"], "alice")

            user_only = logger.filter_logs(username="bob")
            self.assertEqual(len(user_only), 1)
            self.assertEqual(user_only[0]["action"], "LOGIN_FAILED")

    def test_activity_log_write_and_read(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            log_path = Path(td) / "activity.json"
            logger = ActivityLogger(log_path)
            logger.log("student", "ENCRYPT", "payload encrypted")
            events = logger.read_all()
            self.assertEqual(len(events), 1)
            self.assertEqual(events[0]["user"], "student")
            self.assertEqual(events[0]["action"], "ENCRYPT")

    def test_activity_logger_threat_metrics(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            log_path = Path(td) / "activity.json"
            logger = ActivityLogger(log_path)
            logger.log("alice", "LOGIN_FAILED", "wrong password")
            logger.log("alice", "LOGIN_FAILED", "Account temporarily locked. Try again in 40 seconds.")
            logger.log("bob", "INTEGRITY_CHECK", "FAIL")
            summary = logger.summary()
            self.assertEqual(summary["login_failures"], 2)
            self.assertEqual(summary["account_lockouts"], 1)
            self.assertEqual(summary["integrity_check_failures"], 1)

            recent = logger.recent_threat_events(10)
            self.assertEqual(len(recent), 3)
            self.assertEqual(recent[-1]["action"], "LOGIN_FAILED")

            window = logger.threat_window_metrics(7)
            self.assertEqual(window["failed_logins"], 2)
            self.assertEqual(window["lockouts"], 1)
            self.assertEqual(window["integrity_failures"], 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
