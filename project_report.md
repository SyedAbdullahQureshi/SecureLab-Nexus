# SecureLab Nexus Project Report

## Title Page

**Project Title:** SecureLab Nexus - Integrated Cybersecurity Desktop Platform  
**Report Type:** Academic Project Report  
**Course:** [Insert Course Name]  
**Department:** [Insert Department Name]  
**Institution:** [Insert University/Institute Name]  
**Submitted By:** [Insert Student Name]  
**Roll Number:** [Insert Roll Number]  
**Supervisor:** [Insert Supervisor Name]  
**Submission Date:** April 2026

---

## Table of Contents

1. [Abstract](#abstract)
2. [Keywords](#keywords)
3. [Introduction](#1-introduction)
4. [Problem Statement](#2-problem-statement)
5. [Objectives](#3-objectives)
6. [Scope and Delimitations](#4-scope-and-delimitations)
7. [Methodology](#5-methodology)
8. [System Architecture Summary](#6-system-architecture-summary)
9. [Implementation Highlights](#7-implementation-highlights)
10. [Testing and Validation](#8-testing-and-validation)
11. [Results and Outcomes](#9-results-and-outcomes)
12. [Discussion](#10-discussion)
13. [Conclusion](#11-conclusion)
14. [Recommendations and Future Work](#12-recommendations-and-future-work)
15. [References](#13-references)
16. [Appendix Guidance](#14-appendix-guidance)
17. [Extended Technical Appendices](#appendix-a-extended-technical-documentation)

---

## Abstract

SecureLab Nexus is a Python-based desktop cybersecurity platform developed to demonstrate applied information security concepts in a single integrated environment. The system combines cryptographic operations (AES-GCM encryption/decryption), integrity validation (SHA-256 hashing and file integrity checks), authentication controls (password policy, salted PBKDF2 hashing, account lockout), audit logging, and real-time SOC-style monitoring. The project was implemented using Tkinter for desktop GUI, modular Python security packages for maintainability, and JSON persistence for user/activity/settings data. A major enhancement phase introduced a Security Operations Center dashboard with simulated telemetry, risk posture modeling, alerting, chart visualization, profile-based behavior presets, and runtime tuning controls. The software includes executable build support through PyInstaller and quality validation via automated QA checks and CI workflow. The final system demonstrates how confidentiality, integrity, and access control can be operationalized with user-centered observability in an educational lab context.

## Keywords

Cybersecurity, SOC Dashboard, AES-GCM, PBKDF2, SHA-256, Audit Logging, Threat Monitoring, Python, Tkinter, Secure Desktop Application

## 1. Introduction

Cybersecurity education often separates cryptography, authentication, monitoring, and incident response into isolated exercises. This project addresses that gap by integrating these capabilities into one interactive platform. SecureLab Nexus is designed as a practical mini-SOC environment where users can perform secure operations and immediately observe operational security indicators.

The project targets both academic and practical outcomes: students can learn core security principles through direct interaction, and instructors can evaluate secure software design patterns in a demonstrable desktop system. The latest version extends the platform with real-time telemetry simulation and profile-driven monitoring behavior, making it suitable for security lab demonstrations and applied software engineering reports.

## 2. Problem Statement

Many student cybersecurity projects either focus only on cryptographic utilities or only on dashboard visualization, without providing a cohesive end-to-end workflow. This creates three key limitations:

1. Weak linkage between security operations and security monitoring.
2. Limited demonstration of secure coding controls in realistic operator workflows.
3. Lack of integrated auditability and report-ready outputs for academic validation.

SecureLab Nexus solves this by implementing secure operations, event logging, threat-style analytics, and SOC-oriented visualization in one unified desktop application.

## 3. Objectives

### 3.1 Primary Objective

Design and implement an integrated cybersecurity desktop platform that demonstrates secure operations and SOC-style monitoring with practical usability.

### 3.2 Specific Objectives

1. Implement authenticated encryption/decryption using modern cryptographic primitives.
2. Implement secure authentication with password policy, salted hashing, and lockout controls.
3. Implement integrity verification for text and files using SHA-256.
4. Implement structured activity logging with filtering and export functionality.
5. Implement a threat-monitoring view driven by local audit indicators.
6. Implement a real-time SOC dashboard with simulation, risk scoring, and alerting.
7. Provide configurable runtime settings and profile presets for SOC behavior.
8. Validate software reliability through repeatable QA checks.

## 4. Scope and Delimitations

### Scope

- Desktop security platform for local/offline lab usage
- User and role management with local persistent storage
- Cryptographic, hashing, and integrity-check workflows
- Local log-driven threat monitoring and SOC simulation
- CSV/PDF export for administrative and reporting purposes

### Delimitations

- Not an enterprise SIEM replacement
- No network packet capture or external SIEM integration
- Local JSON storage used instead of production-grade database/KMS
- Simulated telemetry is educational, not live threat intelligence ingestion

## 5. Methodology

The project followed an iterative implementation and validation approach:

1. Baseline system construction
2. Security module hardening
3. UI/UX enhancement into SOC-style command interface
4. Runtime behavior tuning and settings persistence
5. Regression validation through QA automation

### 5.1 Design Approach

- Modular architecture with separation between UI, security logic, and persistence
- Event-driven GUI updates using Tkinter scheduling callbacks
- Reusable manager components for auth, logging, and simulation

### 5.2 Development Workflow

- Python virtual environment for dependency isolation
- Scripted run/build automation for consistency
- CI workflow to run QA checks on code changes

## 6. System Architecture Summary

SecureLab Nexus follows a layered architecture:

1. Presentation Layer: Tkinter panels and widgets
2. Application Layer: App controller, navigation, notification, and state logic
3. Security Service Layer: encryption, hashing, authentication, activity logging, simulation
4. Persistence Layer: JSON files for users, logs, profile/settings metadata

Core modules and their responsibilities are documented in detail in later sections.

## 7. Implementation Highlights

### 7.1 Security Controls

- AES-GCM for confidentiality and authenticity of encrypted payloads
- PBKDF2-HMAC-SHA256 for key/password derivation and storage hardening
- SHA-256 hashing for integrity workflows
- Login lockout and role-based access for abuse resistance

### 7.2 SOC Dashboard Enhancements

- Real-time simulation loop with risk and severity outputs
- Profile presets (Blue Team, Incident Mode, Calm Mode)
- Visual status system with pulse behavior and badge updates
- Alert notifications with critical-first behavior

### 7.3 Operational Features

- Activity feed, filterable logs, and exportable reports
- Build scripts for executable delivery
- CI-backed QA testing path

## 8. Testing and Validation

### 8.1 Functional Validation

- Encryption/decryption success and failure paths verified
- Hash generation and verification validated
- Authentication workflows including lockout verified
- Activity logging and summary behavior validated
- Threat metric derivation functions validated

### 8.2 Automated QA

The project includes `qa_checks.py` with security and logic tests. The test suite confirms core module correctness and regression safety across updates.

### 8.3 Build and Runtime Validation

- Repeated local application runs verified stability
- Python compile checks used to catch syntax regressions
- Packaging support verified through PyInstaller configuration/scripts

## 9. Results and Outcomes

The project achieved the following measurable outcomes:

1. Complete integration of multiple security operations in one desktop interface.
2. Consistent event traceability via structured activity logs.
3. SOC-style visualization with configurable real-time behavior.
4. Modular source organization supporting maintainability and extension.
5. Repeatable quality checks with automated QA and CI workflow.

Overall, SecureLab Nexus satisfies both pedagogical and practical software-engineering goals for an applied cybersecurity project.

## 10. Discussion

This implementation demonstrates strong alignment with foundational security principles:

- Confidentiality is addressed through authenticated encryption.
- Integrity is addressed through cryptographic hashing and file checks.
- Availability and abuse resistance are partially addressed via lockouts and controlled workflows.
- Accountability is supported through persistent activity logging.

A key strength is the integration of operational visibility with security actions. Instead of isolated utilities, users can observe how actions affect posture and alerts in a centralized dashboard. The major trade-off is that data sources are local and simulated, which is appropriate for coursework but not equivalent to production SOC infrastructure.

## 11. Conclusion

SecureLab Nexus successfully demonstrates an end-to-end cybersecurity desktop platform with secure operations, auditability, and SOC-style monitoring. The project is academically valuable because it combines theory-backed controls with executable software artifacts and validation evidence. It is also extensible: future integration with live telemetry, stronger data stores, and advanced analytics can evolve this platform toward enterprise-like capability while preserving its educational clarity.

## 12. Recommendations and Future Work

1. Introduce MFA and stronger user-management policies.
2. Replace JSON persistence with secure database-backed storage.
3. Add tamper-evident log signing and retention controls.
4. Integrate optional live telemetry sources for hybrid real/simulated monitoring.
5. Expand automated testing to include GUI interaction scenarios.
6. Add release automation and code-signing for packaged binaries.

## 13. References

1. National Institute of Standards and Technology (NIST), Digital Identity Guidelines, SP 800-63.
2. NIST, Recommendation for Password-Based Key Derivation, SP 800-132.
3. Python Software Foundation, Python 3 Documentation.
4. Cryptography Project Documentation, cryptography.io.
5. OWASP Foundation, Authentication and Cryptographic Storage guidance.

## 14. Appendix Guidance

For formal submission, you can attach the following as appendices:

- Appendix A: Full source file listing
- Appendix B: QA test output screenshots
- Appendix C: UI screenshots (dashboard, auth, logs, settings)
- Appendix D: Build output and executable packaging evidence

## Appendix A. Extended Technical Documentation

### Appendix 1 - Project Overview

SecureLab Nexus is a desktop cybersecurity learning and demonstration platform built in Python with a Tkinter graphical interface. The application combines core information security operations into one interface, including:

- Authenticated encryption and decryption
- Hash generation and verification
- User authentication with password policy enforcement
- Account lockout protection
- File integrity checking
- Activity logging and filtering
- Threat-style monitoring from local audit signals
- Real-time SOC-style dashboard simulation with alerts and analytics
- Administrative reporting and export features

In simple terms, this project acts as a mini Security Operations Center dashboard for educational and practical lab use. It shows how common security controls work together in one system, while remaining easy to run on a normal Windows machine.

---

### Appendix 2 - Purpose

### 2.1 Why this project was created

The project appears to be created to solve two educational needs at once:

1. Demonstrate cybersecurity concepts with a practical, visual system.
2. Provide a single, integrated environment where confidentiality, integrity, and authentication can be exercised.

### 2.2 Academic and practical goals

- Teach how modern encryption (AES-GCM) protects confidentiality.
- Teach how SHA-256 supports integrity verification.
- Teach secure credential storage with PBKDF2 and salt.
- Teach threat awareness by analyzing log signals such as failed logins, lockouts, and integrity failures.
- Teach software quality discipline through automated QA tests and CI workflow.
- Teach software packaging and delivery through PyInstaller scripts.

### 2.3 Value of the SOC-style upgrade

The current version extends beyond a basic utility app and includes a command-center style interface:

- Real-time simulated telemetry
- Risk posture state management
- Profile-driven behavior settings
- Alert presentation with severity handling
- Visual analytics and operator quick actions

This turns the project from a simple tools dashboard into an integrated cyber-defense simulation platform.

---

### Appendix 3 - Complete Feature Breakdown

### Appendix 3.1 - Encryption Panel

### What it does

- Encrypts plaintext using passphrase-based key derivation and AES-GCM.
- Decrypts previously encrypted payloads.
- Supports encryption/decryption of selected files.

### Security design

- Uses a random salt and nonce per encryption operation.
- Uses PBKDF2-HMAC-SHA256 for key derivation.
- Uses authenticated encryption mode (AES-GCM), which provides both confidentiality and tamper detection.

### User workflow

1. User enters plaintext and passphrase.
2. User clicks Encrypt.
3. Output token appears.
4. User can copy output or move output back into input.
5. For file operations, user browses a file and encrypts/decrypts to output files with new suffixes.

### Operational logging

- Logs encryption/decryption actions into activity log.
- Triggers feedback status messages and optional sounds.

### Appendix 3.2 - Key Generator Panel

### What it does

- Generates cryptographically strong URL-safe random keys.
- Allows configurable output length.
- Provides a visual strength indicator.

### Why it matters

A weak key is a common security failure. This panel encourages stronger key generation and introduces secure randomness concepts.

### Appendix 3.3 - Hash Generator Panel

### What it does

- Generates SHA-256 hash values from input text.
- Verifies whether text matches an expected hash.

### Why it matters

Hashing demonstrates integrity checking, not secrecy. It helps detect content changes and supports trust validation workflows.

### Appendix 3.4 - Authentication Panel

### What it does

- Supports user signup and login.
- Enforces password policy.
- Supports role model (admin/user).
- Implements account lockout after repeated failed login attempts.

### Security controls implemented

- Password policy includes minimum length, uppercase, numeric, and special character requirements.
- Common weak passwords are blocked.
- Stored password values are hashed, not plaintext.
- Uses PBKDF2-HMAC-SHA256 with random salt.
- Failed attempts are counted and lock window is enforced.

### Role behavior

- First account is automatically assigned admin for system bootstrap.
- Additional admin creation is restricted to existing admins.

### Appendix 3.5 - Integrity Checker Panel

### What it does

- Computes baseline hash for a selected file.
- Recomputes current hash and compares with baseline.
- Reports pass/fail outcomes for tamper detection.

### Practical significance

This simulates file integrity monitoring in a controlled local context.

### Appendix 3.6 - Activity Log Panel

### What it does

- Displays logged actions with timestamp, user, action, and detail.
- Supports filters by user, action, and date range.
- Supports refresh and reset.
- Supports CSV export and PDF security report export.

### Access control

- Sensitive actions (clear view, export CSV, export PDF report) require admin role.

### Reporting details

PDF report includes:

- Generation timestamp
- User overview
- Activity summary metrics
- Validation status section

### Appendix 3.7 - Threat Monitor Panel

### What it does

- Derives threat indicators from local audit log.
- Shows rolling-window metrics (7 days by default):
  - Failed logins
  - Lockouts
  - Integrity failures
- Shows posture text based on indicator thresholds.
- Displays recent threat-relevant events in feed.

### Scope statement

This is local signal monitoring from audit data, not enterprise network SIEM telemetry.

### Appendix 3.8 - SOC Dashboard Panel

### What it does

- Provides real-time simulated SOC interface:
  - Security status metrics
  - Live activity feed
  - Threat/risk panel
  - Analytics charts (line, pie, bar)
  - Quick action shortcuts

### Real-time simulation

- Uses simulator engine in security.soc_simulation.
- Updates activity counters, user activity, and risk levels on timed intervals.
- Produces simulated info/warning/critical events.

### Alerting behavior

- Critical alerts are surfaced via notification function.
- Warning toast notifications were intentionally disabled in latest update (warning popups removed).
- Top bar shows profile and status state.

### Advanced UX currently included

- Collapsible sidebar
- Neon active states
- Tooltips
- Alert pulsing (profile and logo shell behaviors)
- Dynamic profile display and color coding
- Profile-dependent pulse speed with auto/manual mode

### Appendix 3.9 - Settings Panel

### What it does

- Toggles sound
- Applies themes
- Controls auto-clear status timing
- Configures SOC simulation parameters:
  - Tick interval
  - Alert intensity
  - Risk sensitivity
  - Incident pulse speed
  - Auto pulse by profile mode

### Profile controls

- Presets: Blue Team, Incident Mode, Calm Mode
- Last applied profile display
- Reset to defaults
- Reset to saved profile

### Persistence

SOC settings are persisted in data/soc_settings.json, including:

- timing and sensitivity values
- profile name
- pulse speed
- auto mode flag

### Appendix 3.10 - About Panel

### What it does

- Shows team/project identity information from JSON profile data.
- Supports member image rendering when available.
- Allows clickable GitHub link.

---

### Appendix 4 - Technologies and Libraries Used

### Appendix 4.1 - Python 3.11

### What it is

A high-level, general-purpose programming language.

### Why it is used

- Strong standard library for cryptography workflows, files, data, and testing.
- Fast prototyping for academic security projects.
- Good desktop app support through Tkinter.

### How it is used here

- Core app logic
- Security module implementation
- Testing and build scripts

### Appendix 4.2 - Tkinter and ttk

### What it is

Python standard GUI toolkit.

### Why it is used

- Native desktop UI without external frontend stack.
- Suitable for local educational dashboards.

### How it is used here

- Main window and panel architecture
- Custom controls (ModernButton, tooltips)
- Table views, labels, text areas, forms
- Real-time canvas charts and dynamic widgets

### Appendix 4.3 - cryptography library

### What it is

A widely used Python cryptography package.

### Why it is used

- Provides reliable implementations for AES-GCM and PBKDF2.
- Avoids insecure custom cryptographic code.

### How it is used here

- AESGCM for authenticated encryption/decryption
- PBKDF2HMAC key derivation
- Salting and nonce logic in crypto utilities

### Appendix 4.4 - hashlib and secrets (Python stdlib)

### What they are

- hashlib: standard hash algorithms
- secrets: secure random generation

### Why used

- SHA-256 hashing and verification
- cryptographically secure random salts and keys

### How used

- generate_sha256 and verify_sha256
- random salts/nonces
- URL-safe token key generation

### Appendix 4.5 - reportlab

### What it is

Python PDF generation library.

### Why it is used

Needed for admin security report export in PDF format.

### How it is used

- Builds a structured report with summary and validation information.

### Appendix 4.6 - PyInstaller

### What it is

Packaging tool to convert Python app to Windows executable.

### Why it is used

To distribute the app without requiring Python runtime setup for end users.

### How it is used

- Folder-based and one-file build scripts
- Icon integration
- cryptography hidden import collection

### Appendix 4.7 - Pillow

### What it is

Python imaging library.

### Why used

- Logo/icon handling
- Member image rendering in About panel
- Icon generation utility

### How used

- Resizing and rendering images in Tkinter
- Generating securelab.ico in tooling script

### Appendix 4.8 - winsound (Windows)

### What it is

Windows sound API wrapper in Python stdlib.

### Why used

Provides immediate audible feedback for key security actions.

### How used

Non-blocking thread-based beep patterns mapped to event categories.

### Appendix 4.9 - unittest

### What it is

Python standard testing framework.

### Why used

To ensure reliability of security logic and helper modules.

### How used

qa_checks.py validates encryption, auth, hashing, lockouts, and log metrics.

### Appendix 4.10 - GitHub Actions

### What it is

CI/CD automation platform.

### Why used

Automates QA checks on push and pull request.

### How used

Workflow sets Python 3.11, installs dependencies, executes qa_checks.py.

---

### Appendix 5 - File and Folder Explanation

### Appendix 5.1 - Root-level files

### app.py

Main application entry point and complete UI/controller logic. Contains:

- custom UI widgets
- main app shell
- all panel classes
- alert/notification system
- profile/settings behavior
- runtime dashboard simulation integration

### README.md

Project introduction, features, run instructions, and build notes.

### requirements.txt

Dependency definitions for runtime and packaging:

- cryptography
- reportlab
- pyinstaller

### qa_checks.py

Automated test suite validating core security modules and log metrics.

### SecureLabDashboard.spec

PyInstaller spec for controlled executable build with cryptography collection.

### build_exe.ps1 and build_exe.bat

Build folder-based executable distributions.

### build_onefile.ps1 and build_onefile.bat

Build one-file executable with icon integration and icon generation step.

### run_app.ps1 and run_app.bat

Convenience scripts to create venv (if needed), install dependencies, and run app.

### Appendix 5.2 - security folder

### security/crypto_utils.py

Encryption/decryption helpers with key derivation and payload serialization.

### security/hash_utils.py

SHA-256 generation and verification helpers.

### security/auth_manager.py

Authentication model with signup/login, policy, role control, and lockout logic.

### security/activity_logger.py

Persistent event logger and analytics helpers for filtering, summaries, and threat metrics.

### security/sound_utils.py

Optional sound notification manager with event-specific tone patterns.

### security/soc_simulation.py

SOC simulator engine that drives dashboard telemetry and risk behavior.

### security/__init__.py

Package marker and module-level description.

### Appendix 5.3 - data folder

### data/users.json

Persistent user records (salt, password_hash, role if present).

### data/activity_log.json

Persistent security activity events used by logs, reports, and threat monitor.

### data/about_profile.json

Configurable about/team metadata displayed in About panel.

### data/soc_settings.json

Persistent SOC dashboard behavior and profile settings.

### Appendix 5.4 - assets folder

### assets/securelab.ico

Application icon and branding asset used in UI and packaged executable.

### Appendix 5.5 - tools folder

### tools/generate_icon.py

Programmatically generates securelab.ico from drawn vector-like shape composition.

### Appendix 5.6 - .github/workflows

### .github/workflows/python-tests.yml

Continuous integration workflow executing QA checks.

### Appendix 5.7 - build and dist folders

Generated artifacts from PyInstaller builds. These are output directories, not primary source files.

---

### Appendix 6 - Code Logic Explanation

### Appendix 6.1 - Startup sequence

1. app.py initializes CyberSecurityApp.
2. Data paths and managers are created:
   - AuthManager
   - ActivityLogger
3. User-editable and SOC settings JSON files are loaded.
4. Tkinter styles are configured.
5. Layout is built (sidebar, top bar, content area).
6. Branding assets and icon are loaded.
7. Dashboard is shown and clock updates start.

### Appendix 6.2 - Panel architecture pattern

- BasePanel is a common parent class.
- Each feature panel is implemented as a class.
- Main app registers panel instances in a dictionary.
- show_panel method raises selected panel and triggers panel-specific refreshes.

### Appendix 6.3 - Action logging and cross-panel refresh

- Any security action calls app.log_action.
- log_action writes to activity_log.json via ActivityLogger.
- Activity log panel and threat monitor panel are refreshed.
- Dashboard feed can ingest important app events.

### Appendix 6.4 - Security operation logic

### Encryption path

- Validate input and passphrase length.
- Generate salt and nonce.
- Derive AES key from passphrase using PBKDF2.
- Encrypt via AES-GCM.
- Store payload as base64(salt + nonce + ciphertext).

### Decryption path

- Decode base64 payload.
- Parse salt, nonce, ciphertext.
- Derive key from same passphrase.
- Decrypt with AES-GCM and return plaintext.

### Authentication path

- Signup enforces policy and role constraints.
- Login checks lock state.
- Password hash comparison done using compare_digest.
- Failed attempts increase counter; lockout occurs at threshold.

### Integrity check path

- Read file content.
- Compute SHA-256 digest.
- Compare against baseline digest.

### Appendix 6.5 - SOC simulation logic

- SocSimulator keeps state:
  - risk level
  - activity time-series
  - operation counters
  - user activity buckets
- step method chooses event severity based on config weights.
- State mutates each tick and feeds dashboard visuals.
- Dashboard uses scheduled after callbacks for periodic updates.

### Appendix 6.6 - Alert and notification logic

- show_toast renders transient top-right overlays.
- notify routes severity and sound behavior.
- Warning notifications are currently disabled in notify.
- Critical notification and sounds remain active.

### Appendix 6.7 - Branding and visual state logic

- Icon and logo are loaded from assets/securelab.ico.
- Sidebar supports expanded and collapsed branding modes.
- Logo shell styling reacts to system state:
  - secure: cyan border
  - warning: amber border
  - under threat: pulsing red glow

---

### Appendix 7 - Data Flow and System Flow

### Appendix 7.1 - High-level data flow

Input events flow through this chain:

User input -> Panel handler -> Security/helper module -> App logger/state -> JSON persistence -> UI refresh/analytics

### Appendix 7.2 - Authentication data flow

1. User submits credentials.
2. AuthManager validates policy/lock status.
3. Password hashing and compare logic runs.
4. Success or failure is returned.
5. App updates status, role, and logs action.
6. Threat and activity views are updated.

### Appendix 7.3 - Encryption data flow

1. User enters text/passphrase.
2. crypto_utils encrypt_text/decrypt_text called.
3. Result displayed in panel output.
4. Action logged.
5. Dashboard and logs can reflect operation.

### Appendix 7.4 - Logging and monitoring data flow

1. app.log_action writes event to activity_log.json.
2. ActivityLogger summary and filter functions read same store.
3. Threat monitor derives indicators from same source.
4. Export features consume summarized and raw log data.

### Appendix 7.5 - Settings flow

1. User changes SOC settings.
2. app.apply_soc_settings applies runtime update.
3. Settings persisted in data/soc_settings.json.
4. On next startup, settings reload automatically.

### Appendix 7.6 - SOC profile and pulse flow

1. User applies preset, custom tuning, or reset action.
2. Active profile variable is updated.
3. Top bar profile badge updates text/color.
4. If pulse auto is enabled, pulse speed maps to profile.
5. Under Threat mode triggers pulsing visual behavior.

---

### Appendix 8 - Important Functions and Modules

### Appendix 8.1 - Module: security.crypto_utils

### generate_secure_key

Creates URL-safe random token with minimum length validation.

### _derive_key

PBKDF2 key derivation from passphrase + salt.

### encrypt_text

Validates plaintext, generates salt/nonce, derives key, encrypts with AES-GCM, serializes payload.

### decrypt_text

Validates token, decodes payload, derives key, decrypts and validates authenticity.

### Appendix 8.2 - Module: security.auth_manager

### signup

Validates username/password policy, applies role rules, hashes password, stores record.

### login

Checks lockout, verifies password hash, handles failed attempt counters and lock windows.

### _hash_password

PBKDF2-HMAC-SHA256 hashing with salt handling.

### get_role and list_users

Provide role lookup and user listing for access control/reporting.

### Appendix 8.3 - Module: security.activity_logger

### log

Appends timestamped event record to activity JSON.

### filter_logs

Filters events by user/action/date range for UI table view.

### summary

Computes aggregate metrics used in reports.

### threat_window_metrics and threat_posture

Derive local threat posture from login failures, lockouts, and integrity failures.

### recent_threat_events

Builds focused event feed for monitoring panels.

### Appendix 8.4 - Module: security.soc_simulation

### SocSimulationConfig

Stores simulation timing and sensitivity configuration.

### SocSimulator.set_config

Clamps and sets runtime simulation parameters.

### SocSimulator.ingest_app_event

Updates simulator state based on real app events.

### SocSimulator.step

Performs one simulation cycle and returns generated event payload for dashboard rendering.

### Appendix 8.5 - Main app controller highlights

### CyberSecurityApp.show_panel

Central panel navigation and conditional refresh logic.

### CyberSecurityApp.log_action

Single logging gateway that also triggers dependent panel updates.

### CyberSecurityApp.notify and show_toast

Notification delivery layer for top-right alert popups.

### CyberSecurityApp.apply_soc_settings

Applies SOC runtime settings and persists to JSON.

### CyberSecurityApp.set_system_state

Updates top status chip and logo shell visual behavior.

---

### Appendix 9 - Setup and Installation Steps

### Appendix 9.1 - Prerequisites

- Windows machine recommended for full feature parity (winsound and .bat/.ps1 scripts).
- Python 3.11 available (scripts target 3.11).

### Appendix 9.2 - Manual setup

1. Open terminal in project root.
2. Create virtual environment:

   python -m venv .venv

3. Activate environment (PowerShell):

   .venv\Scripts\Activate.ps1

4. Install dependencies:

   pip install -r requirements.txt

5. Run app:

   python app.py

### Appendix 9.3 - Script-based run

- PowerShell: run_app.ps1
- Batch: run_app.bat

These scripts auto-create venv if missing and install dependencies.

### Appendix 9.4 - QA test execution

Run:

python qa_checks.py

Expected result:

- All tests pass.

### Appendix 9.5 - Build executable

### Folder build

- build_exe.ps1 or build_exe.bat

### One-file build with icon

- build_onefile.ps1 or build_onefile.bat

Outputs are placed in dist folder.

---

### Appendix 10 - Challenges and Solutions

### Appendix 10.1 - Challenge: secure but user-friendly cryptography

### Risk

Cryptographic operations are easy to misuse.

### Solution

- Adopted cryptography package primitives (AES-GCM, PBKDF2).
- Enforced non-empty validation and passphrase checks.
- Added clear error messages and UI feedback.

### Appendix 10.2 - Challenge: password security and account abuse

### Risk

Weak passwords and brute-force attempts.

### Solution

- Strict password policy and common-password blocklist.
- PBKDF2 hashing with random salts.
- Login failure tracking and timed lockout.

### Appendix 10.3 - Challenge: integrating many features in one desktop app

### Risk

Tight coupling and inconsistent state updates.

### Solution

- Panelized architecture with central app controller.
- Shared logging entry point.
- Modular security package separation.

### Appendix 10.4 - Challenge: realistic SOC behavior without external telemetry

### Risk

No live enterprise data source.

### Solution

- Built configurable simulator engine.
- Combined simulated events with real local action ingestion.
- Added profile-based behavior and risk visualization.

### Appendix 10.5 - Challenge: visual complexity in Tkinter

### Risk

Tkinter can become rigid for advanced effects.

### Solution

- Custom canvas button widget.
- Custom toast overlays.
- Canvas-based chart rendering.
- Dynamic state styling and pulsing behaviors.

### Appendix 10.6 - Challenge: deployment for non-developer users

### Risk

Python dependency setup can be a barrier.

### Solution

- Added run/build scripts.
- Added PyInstaller config and one-file executable path.

---

### Appendix 11 - Future Improvements

### Appendix 11.1 - Security and architecture improvements

- Replace local JSON user store with encrypted storage or database.
- Add optional MFA for admin accounts.
- Add audit log signing for tamper-evidence.
- Add configurable retention and secure log rotation.

### Appendix 11.2 - SOC analytics improvements

- Add trend anomaly detection beyond random simulation.
- Add rule editor for custom detection logic.
- Add richer charting using dedicated plotting library.
- Add event drill-down views and timeline correlations.

### Appendix 11.3 - UI/UX improvements

- Add global accessibility options (font scaling, high contrast).
- Add keyboard shortcuts for core actions.
- Add localization support.
- Add guided onboarding for first-time operators.

### Appendix 11.4 - Testing and quality improvements

- Expand tests to include panel interaction tests.
- Add static type checking pipeline.
- Add packaging smoke tests in CI.

### Appendix 11.5 - Deployment and operations improvements

- Add signed builds and release automation.
- Add in-app version and update checker.
- Add configuration profiles for classroom/lab modes.

---

### Appendix 12 - End-to-End System Narrative (Report-Ready Summary)

SecureLab Nexus demonstrates a complete mini security platform lifecycle in one desktop application. The user starts with identity and role assignment through secure signup/login workflows. Once authenticated, the user can apply confidentiality controls through AES-GCM encryption, validate integrity with SHA-256 and file-baseline checking, and produce auditable traces of actions through persistent logging. The same data supports threat posture summarization and operational review, while a SOC-style dashboard translates security telemetry into a visual, near-real-time command interface.

The system combines practical security engineering and human-centered monitoring design. It is modular enough for code-level study, simple enough for classroom deployment, and rich enough to serve as a strong academic report case study for applied cybersecurity software engineering.

---

### Appendix 13 - Quick Reference Tables

### Appendix 13.1 - Core Security Mechanisms

| Mechanism | Implementation | Purpose |
|---|---|---|
| Authenticated Encryption | AES-GCM in crypto_utils | Confidentiality + integrity of encrypted payloads |
| Key Derivation | PBKDF2-HMAC-SHA256 | Derive strong key from passphrase |
| Password Storage | PBKDF2-HMAC-SHA256 + salt | Prevent plaintext password exposure |
| Integrity Check | SHA-256 | Detect data/file modification |
| Brute-force Resistance | Failed-attempt lockout | Slow abusive login attempts |
| Auditability | JSON activity log | Trace user actions and outcomes |

### Appendix 13.2 - SOC Runtime Controls

| Setting | Effect |
|---|---|
| tick_ms | Refresh speed of simulation updates |
| alert_intensity | Probability weighting toward higher severity events |
| risk_sensitivity | How aggressively risk score changes |
| profile | Active SOC behavior profile |
| pulse_speed | Tempo of incident visual pulse |
| pulse_auto | Whether pulse speed follows profile map |

### Appendix 13.3 - Operational Scripts

| Script | Purpose |
|---|---|
| run_app.ps1 / run_app.bat | Create venv if needed, install deps, run app |
| build_exe.ps1 / build_exe.bat | Build folder-based exe with PyInstaller |
| build_onefile.ps1 / build_onefile.bat | Build one-file exe and include icon |
| qa_checks.py | Execute unit-level QA checks |

---

### Appendix 14 - Suggested Report Chapter Mapping

This section helps convert this file into a long-form academic report.

1. Introduction
   - Use Sections 1 and 2.
2. Literature and Technical Background
   - Use Section 4 and security mechanism table.
3. System Design and Architecture
   - Use Sections 5, 6, and 7.
4. Implementation Details
   - Use Sections 8 and 13.
5. Validation and Testing
   - Use Section 9.4 and QA evidence from Section 10.
6. Discussion
   - Use Section 10 challenge-solution analysis.
7. Conclusion and Future Work
   - Use Sections 11 and 12.

---

### Appendix 15 - Final Academic Conclusion

SecureLab Nexus is a strong applied cybersecurity software project because it combines foundational controls, usability, monitoring, and operational practices in one coherent system. The design demonstrates practical engineering trade-offs: secure cryptographic primitives, role-based governance, persistent auditing, and simulation-driven observability. With automated QA and executable packaging support, it moves beyond conceptual demonstration and into reproducible, deployable software practice. This makes it well-suited for academic evaluation, lab demonstration, and future extension into more advanced security operations scenarios.
