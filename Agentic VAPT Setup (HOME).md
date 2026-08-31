# Autonomous Agentic VAPT System Architecture & Master Operational Plan

---

## 1. Target Hardware & Host Environment Specifications (Home PC)

### 1.1 Compute, Graphics & Kernel Infrastructure

* **Processor (CPU):** Intel Core Ultra 5 125H (Meteor Lake-P Architecture)
* **Core Topography:** 14 Physical Cores / 18 Execution Threads
* 4 Performance Cores (P-Cores) @ high-frequency AVX2/AVX-VNNI throughput
* 8 Efficient Cores (E-Cores) for background scheduling, tool parsing, and subprocess management
* 2 Low-Power Efficient Cores (LPE-Cores) for idle state OS maintenance


* **Vector Acceleration:** Full support for `avx2`, `fma`, `bmi1`, `bmi2`, `avx_vnni`, and `vaes`.


* **Graphics (Integrated GPU):** Intel Arc Graphics (Meteor Lake-P GT2, PCI ID `8086:7d55`, rev 08)
* **GPU Architecture:** 7 Xe Cores with dedicated vector matrix processing units.
* **Kernel Drivers:** `i915` and `xe` kernel modules active.
* **Acceleration Interfaces:** Intel oneAPI Level Zero and OpenCL compute runtimes.


* **Operating System:** Kali Linux (Debian 15.3 kernel environment, Rolling release).

### 1.2 Memory & Storage Geometry

* **Physical System RAM:** 15.3 GiB Total Shared LPDDR5/DDR5
* **Baseline Consumption:** ~5.8 GiB active desktop load (XFCE, background daemons, browser sessions).
* **Available RAM (Pre-Freezing):** ~9.5 GiB available for allocation.
* **Available RAM (Post-Application Hibernation):** ~13.0 GiB available.


* **Virtual Memory (Swap Architecture):** 15.3 GiB Total Active Swap
* Primary Swap Partition: `/dev/nvme0n1p8` (10.3 GiB, NVMe speed)
* Secondary Swap File: `/swapfile` (5.0 GiB)


* **Storage & File System Topography:**
* **Primary Root Mount:** `/dev/nvme0n1p7` (ext4) — 185 GB Total, 104 GB Used, **72 GB Available (60% utilization, 13% inode load)**.
* **Ephemeral Memory Mount:** `tmpfs` mounted at `/tmp` (7.7 GB Max capacity).
* **Storage Safety Constraint:** All agent working directories, vector stores, scan logs, and raw outputs are strictly bound to NVMe path `/home/mhj/.local/share/vapt_agent/artifacts/` to prevent `tmpfs` RAM starvation.



---

## 2. Multi-Model LLM Council Specifications

To balance cognitive accuracy against the 15.3 GiB shared memory constraint, models are deployed under a **Strictly Sequential Single-Residency Lifecycle**. Models are dynamically memory-mapped (`mmap`) into RAM/VRAM on demand and unloaded (`keep_alive: 0`) upon phase completion.

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                 THE LOCAL LLM COUNCIL                                  │
├───────────────────────────────┬─────────────────────────────┬──────────────────────────┤
│ Council Role                  │ Model Identifier            │ Quantization & Footprint │
├───────────────────────────────┼─────────────────────────────┼──────────────────────────┤
│ Lead Strategist & Architect   │ DeepSeek-R1-Distill-Qwen-8B │ Q4_K_M (~5.2 GB)         │
│ Lead Operator & Exploitation  │ Qwen2.5-Coder-7B-Instruct   │ Q5_K_M (~5.6 GB)         │
│ Scope Gate — Tier 0 (Det.)    │ Python scope checker        │ N/A (code, no model)     │
│ Scope Gate — Tier 1 (Semantic)│ Llama-3.1-8B-Instruct       │ Q4_K_M (~5.0 GB)         │
│ Offline Script Linter         │ Qwen2.5-Coder-3B            │ Q8_0   (~3.2 GB)         │
│ False-Positive Adjudicator    │ Mistral-7B-Instruct-v0.3    │ Q4_K_M (~4.7 GB)         │
└───────────────────────────────┴─────────────────────────────┴──────────────────────────┘

```

### 2.1 Model Profiles & Operational Responsibilities

#### 1. Lead Strategist: `DeepSeek-R1-Distill-Qwen-8B`

* **Target Quantization:** `Q4_K_M` (Disk Footprint: ~5.2 GB | RAM with 8k Context: ~6.4 GB)
* **Primary Mandate:** Macro-phase strategic reasoning, pre-engagement attack surface modeling, multi-step kill-chain hypothesis formation, and post-engagement remediation synthesis.
* **Why Selected:** Utilizes explicit Chain-of-Thought (`<think>`) reasoning tokens to construct logical attack trees and deduce root causes without jumping blindly to tool execution.

#### 2. Lead Operator: `Qwen2.5-Coder-7B-Instruct`

* **Target Quantization:** `Q5_K_M` (Disk Footprint: ~5.6 GB | RAM with 16k Context: ~7.8 GB)
* **Primary Mandate:** Autonomous tool orchestration, structured JSON parameter generation, custom exploit script synthesis (Python, Bash), and parsing raw stdout/stderr streams.
* **Why Selected:** State-of-the-art coding fidelity at the 7B scale; exhibits exceptional adherence to structured tool-calling schemas with virtually zero parameter hallucination.

#### 3. Scope Gate — Two-Tier Council Gate 1

**Tier 0 — Deterministic Python Scope Checker (no model):**
* **Primary Mandate:** Non-bypassable, zero-LLM-dependence validation of target CIDR/domain-regex membership, port-range boundaries, and a fixed denylist of destructive flags. Runs first, before any LLM sees the task.
* **Why Selected:** A rule-based check cannot be persuaded, prompt-injected, or steered — it closes a reliability gap an LLM-only gate would have.

**Tier 1 — Semantic Scope Gate: `Llama-3.1-8B-Instruct`**
* **Target Quantization:** `Q4_K_M` (Disk Footprint: ~5.0 GB | RAM with 8k Context: ~6.2 GB)
* **Primary Mandate:** Devil's advocate and scope auditor. Evaluates attack plans generated by the Strategist — only for tasks that already passed Tier 0 — before any execution occurs.
* **Why Selected:** Restored conservative, refusal-capable instruction-following. *(This role was originally assigned to `Hermes-3-Llama-3.1-8B` for its "uncensored steerability" — the opposite property wanted from a role whose job is to refuse. Corrected per `11-Critical-Analysis-and-Design-Challenges.md`, finding C-03.)*

#### 4. Council Gate 2 (Command Linting) — Deterministic Code, Not a Model

* **Command/argument validation ("Council Gate 2") is performed by a deterministic, non-LLM Python validator** — argparse-style flag verifiers, regex sanitizers, per-tool schema — evaluated synchronously with zero model-load latency, not by an LLM.
* **`Qwen2.5-Coder-3B`'s role:** reserved for **offline, between-phase** use only — multi-line custom exploit script syntax checks that exceed what the deterministic validator can evaluate via flags/regex/schema alone.
* **Target Quantization:** `Q8_0` (Disk Footprint: ~3.2 GB | RAM with 4k Context: ~3.8 GB) — for its offline role only.
* *(This model was originally the in-loop Council Gate 2 linter, alternating with the 7B Operator per generated command. Corrected per `11-Critical-Analysis-and-Design-Challenges.md`, finding C-09.)*

#### 5. False-Positive Adjudicator: `Mistral-7B-Instruct-v0.3`

* **Target Quantization:** `Q4_K_M` (Disk Footprint: ~4.7 GB | RAM with 8k Context: ~5.9 GB)
* **Primary Mandate:** Independent vulnerability confirmation gatekeeper.
* **Why Selected:** Strict adherence to factual ground truth; assesses raw HTTP response dumps, headers, and error codes against strict vulnerability criteria to filter out WAF blocks, rate limits, and generic 500 server errors before a finding is marked verified.

---

## 3. Master Operational Blueprint (5-Phase Lifecycle)

```
[ Phase 1: Environment & Memory Prep ]
  ├── Enforce NVMe paths (bypass tmpfs)
  └── Freeze non-agent apps via SIGSTOP -> Flush to NVMe Swap (Available RAM: ~13 GB)
       │
       ▼
[ Phase 2: Gateway & Runtime Bridge ]
  ├── Initialize llama.cpp/Ollama with Level Zero SYCL Backend
  └── Pin LLM compute to 8 threads (P-Cores) & Expose OpenAI-compatible /v1 endpoint
       │
       ▼
[ Phase 3: Framework & Kali Tool Integration ]
  ├── Harvest skills & MCP definitions (claude-bug-bounty, CyberStrike, strix)
  └── Establish Dynamic Subprocess Bridge for /usr/bin/ security suite
       │
       ▼
[ Phase 4: State-Driven Council Execution (Relay Mode) ]
  ├── Step A: DeepSeek-R1 (Plan) ──► Scope Checker + Llama-3.1-8B-Instruct (Validate Scope) ──► SQLite
  ├── Step B: Qwen-Coder-7B (Payload, resident) ──► Deterministic Validator (Lint) ──► Subprocess Run
  └── Step C: Mistral-7B (Adjudicate Evidence) ──► DeepSeek-R1 (Report, CVSS via deterministic calculator)
       │
       ▼
[ Phase 5: Hibernation & State Restoration ]
  ├── Evict all model weights from RAM (Memory freed: ~7.8 GB)
  └── Send SIGCONT to desktop apps -> Fast page-in from NVMe Swap (<2s)

```

---

### Phase 1: Storage, Environment Hardening & Application Hibernation

1. **Storage Sandboxing:**
* Direct all agent-generated artifacts, cache databases, tool output XMLs, and temporary scripts to `/home/mhj/.local/share/vapt_agent/artifacts/`.
* Set runtime environment variables (`TMPDIR`, `TEMP`, `TMP`) within the agent process space to target the NVMe partition, strictly blocking ephemeral memory usage in `/tmp`.


2. **Application Hibernation Daemon (Memory Reclamation):**
* Identify all active desktop GUI applications using user session process tables (`firefox-esr`, `chrome`, `brave`, `code`, `discord`, terminal emulators).
* Exclude critical system daemons (`systemd`, `dbus`, `Xorg`, `xfce4-session`, `pulseaudio`/`pipewire`).
* Issue `kill -SIGSTOP` to target application process trees, halting CPU consumption instantly.
* Before triggering memory reclamation, lower each suspended PID's OOM-kill priority to **`oom_score_adj = -900`** (`/proc/<pid>/oom_score_adj`) so hibernated apps are the *last* candidates the kernel's OOM killer would select during the memory-pressure spike below. *(Added — see the Phase 5 correction note below and `11-Critical-Analysis-and-Design-Challenges.md`, finding C-01.)*
* **`process_madvise(MADV_PAGEOUT)` requires elevated capabilities (`CAP_SYS_PTRACE`) the main agent process does not hold.** This call (and the `oom_score_adj` write above) MUST be performed by a narrow, single-purpose helper process (`vapt-freezer-helper`) granted only that specific capability via `setcap`, or an equivalently narrow `sudoers`/polkit rule — never by a privileged main agent process. If the helper/capability is unavailable at runtime, fall back to cgroup v2 memory limits (`memory.high`/`memory.reclaim`) rather than silently skip reclamation. *(Added per `11-Critical-Analysis-and-Design-Challenges.md`, finding C-15.)*
* Trigger immediate kernel memory reclamation on paused PIDs via `process_madvise(MADV_PAGEOUT)` or cgroup memory limits, moving ~3.5 to 4.5 GB of application pages directly into `/swapfile` and `/dev/nvme0n1p8`.
* **Result:** System available memory increases from **9.5 GiB to ~13.0 GiB**.
* **Note:** freezing an application for 10-12 hours lapses its network/IPC sessions (TCP keepalives, TLS sessions, DBus heartbeats) regardless of memory handling — on resume, affected apps may show reconnect/re-auth prompts. This hibernation mechanism guarantees process memory and UI state, not network/session continuity. *(Added per `11-Critical-Analysis-and-Design-Challenges.md`, finding C-16.)*


3. **Database State Initialization:**
* Initialize local SQLite relational state store at `/home/mhj/.local/share/vapt_agent/state.db` with tables for `targets`, `attack_paths`, `task_queue`, `tool_execution_logs`, and `verified_vulnerabilities`.



---

### Phase 2: Local OpenAI-Compatible Inference Gateway & SYCL Acceleration

1. **Inference Engine Initialization:**
* Deploy **`llama.cpp --server`** (primary, confirmed production engine) utilizing the Intel oneAPI Level Zero / SYCL compute backend to offload matrix operations to the 7 Xe Cores of the Intel Arc iGPU. Model load/unload is handled via explicit controller-level process spawn/terminate, abstracted behind a Local Engine Client interface so `ollama` may be substituted later if its own Intel SYCL/Level-Zero support is independently verified. *(Earlier wording treated `llama.cpp --server` and `ollama` as interchangeable, but the `keep_alive` semantics used throughout this document are Ollama-specific and don't exist natively in raw `llama.cpp`. Corrected per `11-Critical-Analysis-and-Design-Challenges.md`, finding C-13.)*
* Expose standard local REST API on `[http://127.0.0.1:11434/v1](http://127.0.0.1:11434/v1)` (`/v1/chat/completions` and `/v1/embeddings`).


2. **Compute & Core Scheduling:**
* Set thread limits to **8 compute threads** (`-t 8`). This pins intensive token processing strictly to the 4 Performance Cores (8 threads), leaving the 8 Efficient Cores free to process network sockets, CLI tools, and JSON parsing.


3. **Memory Eviction Policy:**
* Enforce a hard **Single-Model Residency Policy** (`keep_alive: 0` or manual context teardown). No two models are permitted to reside in RAM/VRAM simultaneously.
* **Memory-settle gate between swaps:** after confirming the outbound model's process has fully exited (`waitpid`), poll `/proc/meminfo`'s `MemAvailable` and do not spawn the inbound model until available memory clears the safety margin (baseline + 1.5 GB) — bounded to 5 seconds, after which a degraded-swap alert is raised. This closes a transient double-allocation race where the kernel hasn't finished reclaiming the outbound process's pages before the inbound one starts allocating. *(Added per `11-Critical-Analysis-and-Design-Challenges.md`, finding C-18.)*



---

### Phase 3: Security Framework & Kali Toolset Bridge

1. **Open-Source Repository Integration:**
* Configure `shuvonsec/claude-bug-bounty`, `CyberStrikeus/CyberStrike`, and `usestrix/strix` to point directly to the local endpoint by setting:
* `OPENAI_BASE_URL="[http://127.0.0.1:11434/v1](http://127.0.0.1:11434/v1)"`
* `OPENAI_API_KEY="local-no-key-required"`
* `ANTHROPIC_BASE_URL="[http://127.0.0.1:11434/v1](http://127.0.0.1:11434/v1)"`


* Extract modular methodology templates:
* Burp Suite and Caido Model Context Protocol (MCP) server configurations.
* Structured multi-turn assessment prompts and vulnerability scoring heuristics.




2. **Dual-Tier Kali Execution Bridge:**
* **Tier 1 (Structured Native Wrappers):** Standard JSON function-calling schemas for high-frequency tools (`nmap`, `masscan`, `nuclei`, `ffuf`, `feroxbuster`, `gobuster`, `sqlmap`, `nikto`, `whatweb`, `wafw00f`, `testssl`).
* **Tier 2 (Dynamic CLI Binary Bridge):** A generic execution interface (`run_security_command`) allowing `Qwen2.5-Coder-7B` to invoke any binary resolving inside `/usr/bin/`, `/usr/sbin/`, or `/opt/` (a path-restricted dynamic allowlist covering the full `kali-linux-everything` toolset). Within this scope, execution is gated by a behavioral denylist (shell builtins, inline-interpreter/eval invocations, writes outside the artifact path, a fixed destructive-utility list) plus three curated high-risk categories — brute-force, active-exploitation, lateral-movement — each requiring its own pre-engagement opt-in flag before its listed binaries can run. *(The original "any installed binary, no further mechanism" description offered no containment beyond a flat denylist. Corrected per `11-Critical-Analysis-and-Design-Challenges.md`, findings C-12/C-14.)*


3. **Subprocess Sandboxing & Deterministic Sanitization:**
* Execute all external binaries using isolated `subprocess.Popen` handles with non-shell execution (`shell=False`), explicit argument vectors, and **tiered mandatory timeouts** by tool class: Quick Probes (`ffuf`, `whatweb`, `nikto`, `wafw00f`) = 180s; Targeted Scans (`nuclei`, standard `nmap`, `sqlmap` quick mode, `gobuster`, `feroxbuster`, `testssl`) = 900s; Deep/Full-Range Scans (`nmap -p-`, `sqlmap` with tamper scripts, `masscan` subnet sweeps) = 1800s — with non-blocking output streaming to detect stalls before the hard timeout. *(A flat 180s default for every tool didn't fit long-running scans. Corrected per `11-Critical-Analysis-and-Design-Challenges.md`, finding C-08.)*
* Run raw stdout/stderr through a local Python sanitization pipe:
* Extract open ports, service banners, responsive URLs, and HTTP status codes ($200, 301, 401, 500$).
* Discard HTML bodies, redundant 404 responses, and binary data before context ingestion to protect the 16k context window.





---

### Phase 4: State-Driven Council Execution (Relay Protocol)

#### Step 4.1: Strategic Attack Path Formulation & Scope Verification

1. **Load `DeepSeek-R1-Distill-Qwen-8B` (Q4_K_M):**
* Ingest target scope, IP ranges, and rules of engagement from the SQLite database.
* Model generates step-by-step attack hypotheses and an ordered task queue.
* Model outputs the plan to SQLite and completely unloads from RAM.


2. **Council Gate 1 — Two-Tier Scope Check:**
* **Tier 0 (deterministic, no model):** A Python scope checker validates the generated plan's tasks against target CIDR/domain-regex/port boundaries and a destructive-flag denylist — non-bypassable, runs first.
* **Tier 1 — Load `Llama-3.1-8B-Instruct` (Q4_K_M):** For tasks that passed Tier 0, strictly evaluates them against target scope boundaries and potential system risks.
* Approves valid tasks or writes revisions to the SQLite task queue.
* Model unloads completely from RAM.
* *(This step originally loaded `Hermes-3-Llama-3.1-8B` alone. Corrected per `11-Critical-Analysis-and-Design-Challenges.md`, finding C-03.)*



#### Step 4.2: Autonomous Tool Execution, Linting & Exploitation

1. **Load `Qwen2.5-Coder-7B-Instruct` (Q5_K_M):**
* Reads next executable task from SQLite.
* Formulates the concrete CLI command or custom exploit script.


2. **Fast Pre-Flight Linting — Council Gate 2 (deterministic, no model swap):**
* A deterministic Python validator — argparse-style flag verifiers, regex schema validation — checks generated CLI flags against tool syntax standards, evaluated synchronously with no model-load latency. `Qwen2.5-Coder-7B` (the Operator) stays resident throughout this loop; `Qwen2.5-Coder-3B` is not invoked here.
* If invalid, the Operator regenerates a corrected command (up to 3 attempts) before the task is marked blocked.
* *(This step originally alternated `Qwen2.5-Coder-3B` in and out of RAM per generated command. Corrected per `11-Critical-Analysis-and-Design-Challenges.md`, finding C-09.)*


3. **Execution & Log Parsing:**
* The Python bridge executes the tool, sanitizes output, writes full logs to NVMe artifacts, and commits parsed findings to SQLite.
* `Qwen2.5-Coder-7B` evaluates parsed outputs, determines if secondary exploitation or pivoting is required, and loops until the task queue is resolved — **bounded by a 30-task-per-target cap and a 3-consecutive-zero-yield circuit breaker (auto-pivot to the next target), plus a global 12-hour session budget (auto-transitions to Phase 4.3)** — no operator pause at any of these thresholds.
* Model unloads completely from RAM only once Phase 4.2 ends for the whole engagement, not per task.
* **"Zero-yield" is a precise, state-delta definition, not "non-empty output":** a run only counts as yielding if it adds at least one new row to a `discovered_entities` ledger (a previously-unseen port, route, parameter, or status-code anomaly for that target) — a noisy tool returning hundreds of repetitive `200 OK` responses with nothing new still counts toward the 3-run circuit breaker. *(Added per `11-Critical-Analysis-and-Design-Challenges.md`, finding C-17.)*
* *(This step originally had no stated bound. Corrected per `11-Critical-Analysis-and-Design-Challenges.md` and `01-Functional-Requirements.md` FR-COUNCIL-11.)*



#### Step 4.3: Evidence Adjudication & Final Reporting

*(Note on the step below: CVSS handling was corrected — see the numbered item.)*

1. **Load `Mistral-7B-Instruct-v0.3` (Q4_K_M) — Council Gate 3:**
* Reads reported vulnerability candidates from SQLite along with raw HTTP/log dumps.
* Evaluates evidence objectively to eliminate false positives (e.g., distinguishing real injections from generic server errors).
* Marks findings as `CONFIRMED` or `DISMISSED` in SQLite, then unloads.


2. **Reload `DeepSeek-R1-Distill-Qwen-8B` (Q4_K_M):**
* Ingests confirmed findings, maps CVE/CWE identifiers, deduces root causes, and drafts the technical penetration testing report.
* Proposes CVSS 3.1 per-metric values with justification — **a separate deterministic (non-LLM) calculator computes the final numeric score and vector string; the model never emits a final CVSS score itself.**
* Model unloads completely upon task completion.
* *(This step originally had the model calculate CVSS scores directly. Corrected per `11-Critical-Analysis-and-Design-Challenges.md`, finding C-07.)*



---

### Phase 5: Agent Hibernation & Desktop Workspace Restoration

1. **State Preservation & Engine Eviction:**
* The agent marks the engagement state as `COMPLETE` or `PAUSED` in SQLite.
* The local inference engine purges all active model weights and KV caches, freeing ~7.8 GB of physical RAM.


2. **Instant Desktop Application Wake-Up:**
* The process manager identifies all previously suspended PIDs and issues `kill -SIGCONT`, then verifies each one actually resumed (not reaped by the OOM killer despite the `oom_score_adj` deprioritization applied in Phase 1).
* The Linux virtual memory subsystem pages application memory back from NVMe swap (`/dev/nvme0n1p8`) into physical RAM on demand.
* **Outcome:** All browser sessions, tabs, IDEs, and user tools resume instantly (<2 seconds) in their exact prior working state, on a **best-effort, OOM-hardened basis — not an absolute guarantee.** Any suspended process not found alive at resume time is logged as a partial-hibernation-success event, not silently treated as full success.
* *(This step originally guaranteed "zero data loss" unconditionally, with no OOM-killer mitigation described. Corrected per `11-Critical-Analysis-and-Design-Challenges.md`, finding C-01.)*



---

## 4. Resource Allocation & Operational Thresholds

| Operational Phase | Active Model in RAM | RAM Allocation | Context Buffer | Available Headroom |
| --- | --- | --- | --- | --- |
| **Phase 1: Pre-Launch (Apps Frozen)** | *None* | 0.0 GB | 0 tokens | ~13.0 GB |
| **Phase 4.1: Strategy (DeepSeek-R1)** | `DeepSeek-R1-8B (Q4)` | ~5.2 GB | 8,192 tokens | ~6.6 GB |
| **Phase 4.1: Scope Gate (Tier 1 — Llama-3.1-8B-Instruct)** | `Llama-3.1-8B-Instruct (Q4)` | ~5.0 GB | 8,192 tokens | ~6.8 GB |
| **Phase 4.2: Execution (Qwen-Coder-7B)** | `Qwen-Coder-7B (Q5)` | ~5.6 GB | 16,384 tokens | ~5.2 GB |
| **Phase 4.3: Triage (Mistral-7B)** | `Mistral-7B (Q4)` | ~4.7 GB | 8,192 tokens | ~7.1 GB |
| **Phase 5: Post-Launch (Apps Resumed)** | *None* | 0.0 GB | 0 tokens | ~9.5 GB |

This operational blueprint maintains absolute memory safety on your 15.3 GiB Intel Core Ultra 5 system, **reduces (but does not eliminate) hallucination risk** through multi-agent validation gates, and provides seamless execution of the entire Kali Linux security suite without cloud API dependencies. *(This originally claimed the design "completely mitigates" hallucination — an unprovable absolute. Corrected per `11-Critical-Analysis-and-Design-Challenges.md`, finding C-11.)*

### Models and Their Usage

[ Phase: Strategy & Planning ]
  ├── DeepSeek-R1-Distill-8B (Lead Strategist) ──► Proposes Attack Vector / Chain
  └── Scope Gate: Python Checker (Tier 0) + Llama-3.1-8B-Instruct (Tier 1) ──► Challenges Assumptions & Scope Creep
       │
       ▼ (Consensus Written to SQLite Task Queue)
[ Phase: Tool Execution & Verification ]
  ├── Qwen2.5-Coder-7B       (Lead Operator, stays resident for the loop) ──► Generates Tool Call / Script Payload
  └── Deterministic Python Validator (Gate 2) ──► Instantly Validates CLI Flags & JSON Schema (Qwen2.5-Coder-3B: offline script checks only)
       │
       ▼ (Tool Dispatched to Subprocess)
[ Phase: Finding Triage & Verification ]
  ├── DeepSeek-R1-Distill-8B (Vulnerability Lead) ──► Assesses Raw Evidence & Deduces Root Cause (proposes CVSS 3.1 metrics; deterministic calculator computes final score)
  └── Mistral-7B-Instruct-v0.3 (Strict Adjudicator) ──► Adversarial False-Positive Gatekeeper
  (Corrected per 11-Critical-Analysis-and-Design-Challenges.md, findings C-03/C-07/C-09.)
