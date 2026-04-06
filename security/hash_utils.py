"""Hashing helpers for integrity checks and password/text hashing demos."""

from __future__ import annotations

import hashlib


def generate_sha256(text: str) -> str:
    """Generate SHA-256 digest for given text."""
    if text is None:
        raise ValueError("Input cannot be None.")
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def verify_sha256(text: str, expected_hash: str) -> bool:
    """Verify if text matches a SHA-256 hash."""
    if not expected_hash:
        raise ValueError("Expected hash cannot be empty.")
    return generate_sha256(text) == expected_hash.strip().lower()
