# NEXUS AI OS
## Version 1.0.0 — Comprehensive System Architecture & Engineering Blueprint

This specification details the design principles, interface contracts, cryptographic structures, and integration boundaries for the user-facing intelligence subsystems of the NEXUS AI Operating System.

```
       +------------------------------------------------------------------------+
       |                         NEXUS UI / MOBILE DEV                          |
       +------------------------------------+-----------------------------------+
                                            | (Port 3000 REST/WebSockets API)
                                            v
+-------------------------------------------------------------------------------+
|                       INTELLIGENT INTERACTION KERNEL                          |
|                                                                               |
|  +---------------------------+  +--------------------------+  +------------+  |
|  |     1. VOICE RUNTIME      |  |   2. BROWSER RUNTIME     |  | 3. LOCAL AI|  |
|  | [WakeWord, TTS, ASR, VAD] |  | [Virtual Automations]    |  | [Ollama]   |  |
|  +-------------+-------------+  +------------+-------------+  +-----+------+  |
|                |                             |                      |         |
|                v                             v                      v         |
|  +-------------+-------------+  +------------+-------------+  +-----+------+  |
|  |   4. DEVICE SYNC ENGINE   |  |   5. MOBILE COMPANION    |  | 6. PLUG SDK|  |
|  | [LWW Conflict Merge, XOR]  |  | [Intent Delegation, QR]  |  | [Sandbox]  |  |
|  +-------------+-------------+  +------------+-------------+  +-----+------+  |
|                |                             |                      |         |
|                +-----------------------------+----------------------+         |
|                                              v                                |
|                        +---------------------+----------------------+         |
|                        |   7. IMMUTABLE SECURITY & AUDITING ENGINE    |         |
|                        |    [RBAC, Exec Sandbox, Chained Auditer]   |         |
|                        +---------------------+----------------------+         |
+----------------------------------------------|--------------------------------+
                                               v
                        +----------------------+----------------------+
                        |                    SQLite / PostgreSQL DB   |
                        +---------------------------------------------+
```

---

## 1. Subsystem Breakdowns & Technical Specs

### 1. Voice Runtime
Located in: `/backend/app/voice/`
Provides complete, high-fidelity hands-free interaction loop controls:
*   **Audio Routing (`/audio_router`):** Real-time moving average PCM amplitude filters executing active hardware Noise Suppression (attenuating high decibel spike sounds) and Acoustic Echo Cancellation (isolating loudspeaker feedback channels).
*   **Speech Recognition (`/speech_recognition`):** Transcribes audio frames directly into textual intents using localized speech decode paths.
*   **Text-to-Speech (`/text_to_speech`):** Procedural waveform synthesis with custom base pitch shifting, cadence envelope mapping, and adjustable play speed parameters over multi-voice profiles (`Zephyr`, `Aurora`, `Borealis`).
*   **Continuous Dialog Loop & Interruption (`/conversation_mode` & `/interruption`):** Employs Short Term Energy algorithms for Voice Activity Detection (VAD). Monopolizes system play state, and instantly silences TTS outputs when user interruption words (`"stop"`, `"cancel"`, `"hold"`, `"quiet"`) are detected.

### 2. Browser Runtime
Located in: `/backend/app/browser/`
Allows the agent to interact programmatically with complex target websites:
*   **Core Driver (`/playwright_engine` & `/navigation`):** Establishes virtual UI coordinates, virtual viewports, cookies parsing, and mock visual screenshots generation.
*   **Form Filler (`/form_filler` & `/captcha_handler`):** Injects field forms slowly to bypass bot detection software with specialized reCAPTCHA bypass hooks.
*   **Transactional Guards (`/booking_engine`, `/shopping_engine`, `/job_application`):** Implements travel booking and job application flows. **CRITICAL:** Intercepts checkout and application submits, forcing explicit verification prompts from `global_approval_manager` before any credit card or personal details can be transmitted.

### 3. Local AI Runtime
Located in: `/backend/app/local_ai/`
Grants localized smart capabilities without internet connection requirements:
*   **Hardware Accelerator (`/hardware`):** Runs CPU/GPU queries, checks CUDA registries on Linux or metal MPS processors on Apple Silicon (falling back gracefully to multi-thread processes).
*   **Ollama Controller (`/ollama`):** Integrates directly with self-hosted Ollama instances to manage local weight parameters (such as `llama3:8b`, `phi3:3.8b`).
*   **Hybrid Route Manager (`/router`):** Decides whether prompts go to the Cloud (Gemini) or a Local model based on network latency, link failures, or privacy rules (flagging keys, salaries, passwords).
*   **Offline Document Indexer (`/document_index` & `/embeddings`):** Embeds PDF text chunks locally to run localized vector-matching (cosine index) for RAG without external API roundtrips.

### 4. Cross-Device Synchronization
Located in: `/backend/app/sync/`
*   **Encryption Layer (`/encryption`):** Implements pure-python end-to-end symmetric XOR ciphers utilizing SHA-256 blocks to encrypt states prior to device handshakes, verifying integrity during downloads.
*   **Conflict Resolver (`/conflict_resolver`):** Implements Last-Write-Wins (LWW) conflict merges, performing deep structural dictionary merges over nested user preference trees.

### 5. Mobile Companion Backend
Located in: `/backend/app/mobile/`
*   **Pairing Protocol (`/pairing`):** Emits short-lived PIN hash coordinates and QR payloads, enabling secure QR connection checkouts.
*   **Notification Engine (`/notifications`):** Integrates APNs and FCM routines for high-priority alerts.
*   **Intent Delegator (`/delegator`):** Safely handles remote task execution across active runtime channels.

### 6. Intelligence Dashboard
Located in: `/backend/app/intelligence_dashboard/`
*   **Metrics Compiler (`/metrics_aggregator`):** Telemetry aggregator compiling active logging counts, live hardware usage performance graphs (via `psutil`), average model initiation latencies, and total operator clearance statistics.

### 7. Plugin SDK
Located in: `/backend/app/plugins/`
*   **Standard Interface (`/plugin_base`):** Declares deep event handlers: `on_load()`, `on_session_start()`, `on_intent_intercept()`, `on_unload()`.
*   **Permission Auditor (`/permission_manifest` & `/manager`):** Grants declarative permission keys (`filesystem_read`, `microphone_access`, etc.) utilizing real-time prompt permissions.

### 8. Immutable Security Engine
Located in: `/backend/app/security/`
*   **Cryptographic Vault (`/credential_storage`):** Encrypts credentials and secret keys before storage.
*   **Chained Audit Logger (`/audit_logger`):** Implements a cryptographically chained block list of diagnostic system logs. Every log record contains a SHA-256 backlink to the previous entry log, rendering physical logs immutable to retro-active modifications.
*   **Exec Sandbox (`/sandbox`):** Blocks command chained sequences, shell operators, and enforces binary whitelists.
*   **Role Access Control (`/rbac`):** Defines granular clearance states (`Guest`, `Operator`, `KernelAdmin`) over API endpoints.

---

## 2. API Signature Specifications

| Method | Endpoint | Description | Scope Required |
| :--- | :--- | :--- | :--- |
| **POST** | `/api/intelligence/voice/transcribe` | Transcribes audio bytes into clean commands | `voice_input` |
| **POST** | `/api/intelligence/voice/synthesize` | Generates base64 WAV streams from strings | `voice_input` |
| **POST** | `/api/intelligence/browser/navigate` | Virtializes browser tabs and navigates URLs | `browser_navigate` |
| **POST** | `/api/intelligence/browser/book` | Arranges Paris booking with Approval checks | `browser_navigate` |
| **GET** | `/api/intelligence/local_ai/status` | Reports GPU parameters and Ollama states | `view_metrics` |
| **POST** | `/api/intelligence/sync/packet` | Unwraps and merges peer database segments | `pair_device` |
| **GET** | `/api/intelligence/mobile/challenge` | Generates 6-digit PIN / QR codes | `pair_device` |
| **POST** | `/api/intelligence/mobile/verify` | Registers a companion handheld client device | `pair_device` |
| **GET** | `/api/intelligence/dashboard/telemetry` | Outputs system usage and model speed lists | `view_metrics` |
| **GET** | `/api/intelligence/security/audits` | Verifies cryptographic chain authenticity | `read_logs` |

---

## 3. Production Deployment Topologies

NEXUS AI OS supports high-availability self-hosted setups via:
1.  **Docker Compose (`/backend/docker-compose.yml`):** Automatically mounts the standard FastAPI container, Postgres databases, Redis caching layers, and a **self-hosted Ollama container** mapped cleanly to local GPU hardware drivers (`nvidia`).
2.  **Scalable Resources:** Incorporates memory reserves and environment variables (`DATABASE_URL`, `REDIS_URL`, `NEXUS_ACCELERATOR=cuda/mps`) to run completely offline if needed, preserving local, secure, and isolated execution bounds appropriate for a next-generation AI operating system.
