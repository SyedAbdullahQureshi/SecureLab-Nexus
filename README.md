# SecureLab Nexus — Information Security Desktop Dashboard

A modern GUI-based desktop application (**SecureLab Nexus**) built with Python and Tkinter to demonstrate key information security principles:

- Confidentiality through AES-GCM encryption/decryption
- Integrity through SHA-256 hashing and verification
- Authentication through signup/login with salted PBKDF2 password hashing
- Secure key generation using cryptographically strong randomness
- Activity auditing with a local action log
- Role-based access with admin-only sensitive actions
- Brute-force protection with temporary account lockout

## Features Overview

### 1) Encryption Panel

- Accepts user text and passphrase.
- Uses AES-GCM for authenticated encryption.
- Supports decrypting previously encrypted payloads.
- Shows clear success/failure feedback.
- Supports file encryption/decryption for txt/json/csv files.

### 2) Key Generator

- Generates random URL-safe keys with configurable length.
- Uses Python `secrets` module for strong randomness.
- Supports clipboard copy for usability.
- Includes a live key-strength meter and progress bar.

### 3) Hash Generator

- Produces SHA-256 hashes for text input.
- Verifies text against expected hashes for integrity checks.

### 4) User Authentication

- Signup/login system with local user database.
- Passwords are never stored in plaintext.
- Uses salted PBKDF2-HMAC-SHA256 for password storage.
- Enforces password policy: minimum length, uppercase, digit, special character.
- Rejects common weak passwords.
- Locks account temporarily after 3 failed login attempts.
- Supports admin and user roles.

### 5) Activity Log

- Records timestamp, user, action, and detail.
- Displays recent operations in a dashboard table.
- Includes search and filters (username, action, date range).
- Allows CSV export and PDF security report export (admin-only).

### 6) Threat Monitor (local indicators)

- Surfaces **local threat-style indicators** from the same audit log: failed logins, lockouts (derived from log text), and integrity check failures.
- Rolling 7‑day counts, a simple posture summary, and a focused event feed (not network-wide or enterprise SIEM monitoring).

### 7) Integrity Checker

- Generates baseline hash for a selected file.
- Compares current hash with baseline to detect tampering.

### 8) Settings Panel

- Toggle sound feedback.
- Theme switching.
- Auto-clear timeout for status messages.

## Security Practices Used

- Input validation and meaningful errors
- Authenticated encryption (AES-GCM)
- Strong password hashing with salt and high iteration count
- Cryptographically secure random generation (`secrets`)

## Project Structure

- `app.py`: Main GUI application and dashboard panels.
- `security/crypto_utils.py`: AES-GCM and key generation logic.
- `security/hash_utils.py`: SHA-256 hash generation and verification.
- `security/auth_manager.py`: Signup/login and secure password storage.
- `security/activity_logger.py`: Action logging utilities.
- `security/sound_utils.py`: Action sound feedback helper.
- `data/users.json`: Auto-created user database.
- `data/activity_log.json`: Auto-created activity events.
- `qa_checks.py`: Automated module-level QA tests.
- `.github/workflows/python-tests.yml`: CI pipeline for automated testing.

## Run Instructions

1. Install dependencies:
  ```bash
   pip install -r requirements.txt
  ```
2. Start the application:
  ```bash
   python app.py
  ```

## QA Validation

Run automated checks:

```bash
python qa_checks.py
```

## Build Windows EXE (PyInstaller)

Option 1 (PowerShell):

```powershell
./build_exe.ps1
```

Option 2 (Batch):

```bat
build_exe.bat
```

Output executable:

- `dist/SecureLabDashboard/SecureLabDashboard.exe`

## Build One-File EXE With Icon

Option 1 (PowerShell):

```powershell
./build_onefile.ps1
```

Option 2 (Batch):

```bat
build_onefile.bat
```

Output executable:

- `dist/SecureLabDashboard.exe`

Icon asset:

- `assets/securelab.ico`

## Notes for Evaluation

- The interface uses a dashboard layout with panel navigation, dark theme, animated mascot, and rotating security tips.
- The app intentionally includes humorous authentication/crypto feedback while preserving a professional tone.

