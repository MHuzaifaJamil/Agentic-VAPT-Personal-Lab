# Autonomous Agentic VAPT System — Master Operational Blueprint

A high-performance, fully local vulnerability assessment and penetration testing (VAPT) framework running on Kali Linux. The platform coordinates an ensemble council of dedicated language models alongside deterministic code gates to autonomously plan, execute, adjudicate, and report security assessments without cloud dependencies or telemetry egress.

---

## 1. System Topology & Hardware Target

Optimized for high-efficiency mobile and workstation silicon operating under constrained shared memory architectures.

* **Compute:** Intel Core Ultra 5 125H (14 Cores / 18 Threads: 4 P-Cores, 8 E-Cores, 2 LPE-Cores)
* **Graphics / Matrix Acceleration:** Intel Arc Graphics (7 Xe Cores) via Intel oneAPI Level Zero / SYCL
* **Host Operating System:** Kali Linux Rolling (x86_64)
* **Memory Architecture:** 15.3 GiB Shared LPDDR5/DDR5 + 15.3 GiB NVMe Swap
* **Memory Management Strategy:** Dynamic desktop hibernation and strict **single-model residency**. Active models are loaded sequentially via memory-mapped IO (`mmap`) and evicted immediately upon phase completion to clear the 1.5 GiB minimum safety buffer.

---

## 2. The Multi-Model Council

The reasoning pipeline divides responsibilities across specialized local models to prevent single-agent confirmation bias and parameter hallucination.

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                 THE LOCAL LLM COUNCIL                                  │
├───────────────────────────────┬─────────────────────────────┬──────────────────────────┤
│ Council Role                  │ Model Identifier            │ Quantization & Footprint │
├───────────────────────────────┼─────────────────────────────┼──────────────────────────┤
│ Lead Strategist               │ DeepSeek-R1-0528-Qwen3-8B   │ Q8_0   (~8.6 GB)         │
│ Lead Operator & Tool Runner   │ Qwen2.5-Coder-7B-Instruct   │ Q8_0   (~8.0 GB)         │
│ Scope Gate (Semantic Tier)    │ Hermes-3-Llama-3.1-8B       │ Q8_0   (~8.4 GB)         │
│ Offline Script Linter         │ Qwen2.5-Coder-3B-Instruct   │ Q8_0   (~3.3 GB)         │
│ False-Positive Adjudicator    │ Mistral-7B-Instruct-v0.3    │ Q8_0   (~7.6 GB)         │
│ Executive Technical Reporter  │ Ministral-8B-Instruct-2410  │ Q8_0   (~8.4 GB)         │
└───────────────────────────────┴─────────────────────────────┴──────────────────────────┘

```

* **Lead Strategist (`DeepSeek-R1-0528-Qwen3-8B`):** Employs extended reasoning tokens (`<think>`) to construct macro-level attack paths, hypothesize kill-chains, and map target trust boundaries.
* **Lead Operator (`Qwen2.5-Coder-7B-Instruct`):** Generates structured tool invocations, handles API schemas, and synthesizes target-specific exploit/automation scripts. Remains resident during Phase 4.2.
* **Scope Gate — Dual-Tier:**
* *Tier 0 (Deterministic):* Non-bypassable Python rule engine enforcing CIDR containment, domain regexes, port whitelists, and destructive syntax blocks.
* *Tier 1 (Semantic — `Hermes-3-Llama-3.1-8B`):* High-level contextual sanity checks on proposed attack plans to challenge logic drift.


* **Command Validator & Linter — Dual-Tier:**
* *Council Gate 2 (In-Loop):* Deterministic, zero-latency schema and flag verifier validating Operator tool syntax before execution.
* *Script Linter (Offline — `Qwen2.5-Coder-3B-Instruct`):* Invoked between phases to parse complex, multi-line custom scripts.


* **False-Positive Adjudicator (`Mistral-7B-Instruct-v0.3`):** Independent evidence gatekeeper reviewing raw HTTP streams, server headers, and return codes against an empirical 4-point impact checklist.
* **Executive Reporter (`Ministral-8B-Instruct-2410`):** Drafts vulnerability records, maps CWE/CVE indices, and proposes CVSS 3.1 vectors for automated calculation.

---

## 3. Operational Lifecycle

```
[ Phase 1: Environment Prep ]
  └── Freeze non-essential desktop GUI apps (SIGSTOP) -> Reclaim RAM to Swap (~13 GB free)
       │
       ▼
[ Phase 2: Runtime Engine Initialization ]
  └── Launch llama.cpp with Level Zero SYCL -> Pin to 8 P-Core threads on 127.0.0.1:11434
       │
       ▼
[ Phase 3: Toolset & Bridge Binding ]
  └── Initialize Tier 1 JSON schemas & Tier 2 dynamic CLI adapters across /usr/bin & /opt
       │
       ▼
[ Phase 4: State-Driven Council Execution (Relay Mode) ]
  ├── 4.1 Plan: DeepSeek-R1 -> Scope Check (Tier 0 Code + Tier 1 Hermes-3) -> SQLite Task Queue
  ├── 4.2 Execute: Qwen-Coder-7B (Resident) -> Gate 2 Validation -> Process-Group Subprocess Run
  └── 4.3 Adjudicate: Mistral-7B Evidence Review -> Ministral-8B Report Generation
       │
       ▼
[ Phase 5: Teardown & Workspace Restoration ]
  └── Evict model weights -> Resume desktop application trees (SIGCONT)

```

### Phase Details

* **Phase 1: Environment Prep & Memory Reclamation:** Suspends heavy user processes (`SIGSTOP`), reprioritizes OOM-kill safety (`oom_score_adj = -900`), and flushes inactive pages to NVMe swap via a dedicated helper binary (`vapt-freezer-helper`), increasing free memory from ~9.5 GiB to ~13.0 GiB.
* **Phase 2: Local Gateway & Core Pinning:** Boots the local inference backend on loopback, binding compute workloads to Performance Cores while reserving Efficient Cores for tool subprocesses and I/O polling.
* **Phase 3: Security Tooling Bridge:** Binds Tier 1 native JSON schemas (`nmap`, `ffuf`, `sqlmap`, `nuclei`) and Tier 2 binary bridges (`/usr/bin`, `/usr/sbin`, `/opt/`) with non-shell execution (`shell=False`) and tiered subprocess timeouts.
* **Phase 4: State-Driven Council Relay:** Coordinates iterative testing cycles through an append-only SQLite WAL state store. Tasks proceed through Plan $\rightarrow$ Gate $\rightarrow$ Tool Execution $\rightarrow$ Evidence Adjudication $\rightarrow$ Report Generation.
* **Phase 5: Teardown & State Restoration:** Flushes inference buffers, clears runtime caches, and signals desktop processes (`SIGCONT`) to restore user workflows cleanly.

---

## 4. Execution Posture & Safety Controls

The architecture implements a **Dual-Mode Execution Architecture** to balance autonomy with strict operational safety:

* **Autonomous Mode (Non-Destructive Testing):** Unattended runs are strictly constrained. Permitted actions are limited to discovery reads (`GET`, `SELECT`) and non-destructive verification writes (`POST`). Data mutation, table drops, file deletions, and Denial of Service (DoS) conditions are prohibited by code gates.
* **Operator-Directed Mode (Unconditional Execution):** Direct operator commands, interactive interventions, and manual scripts execute with top operational priority, bypassing automated heuristic gate refusals.

### Defense-in-Depth Safeguards

* **Untrusted Content Wrapping:** All target responses are tagged as `<tool_output_untrusted>` to prevent target data from overriding model instructions.
* **Deterministic Grounding Verification:** Draft finding narratives are mechanically verified against raw evidentiary artifacts before report finalization.
* **Circuit Breakers:** Automated loops trip on either 3 consecutive zero-yield runs (auto-pivoting target) or 3 consecutive network connection timeouts (marking target unreachable).
* **Human Checkpoint Gate:** Sensitive actions (e.g., live credential spraying, external CI/CD PRs, package registry verification) trigger real-time checkpoints requiring explicit operator authorization unless executed directly via operator command.

---

## 5. Control Interfaces

The system operates without external web dashboards or browser dependencies:

```bash
# Core Lifecycle Management
vaptctl start --targets <targets.txt> --scope-rules <scope.yaml> [--assessment-mode initial|retest]
vaptctl pause
vaptctl resume
vaptctl abort                      # Direct kill-switch: halts subprocess trees within 20s
vaptctl status [--json]
vaptctl export --engagement-id <id> --out <path>

# Checkpoints & Reports
vaptctl approve-checkpoint --checkpoint-id <id>
vaptctl deny-checkpoint --checkpoint-id <id>
vaptctl approve-report --report-id <id>

# Real-Time Telemetry & Console
vaptctl dashboard                  # 1.0 Hz read-only terminal performance dashboard (rich)
vaptctl console                    # Interactive TUI intervention stream (Textual)
vaptctl monitor --engagement-id <id> # Standalone model-free reconnaissance engine

```

---

## 6. Extended Capability Domains

Beyond standard network and web application penetration testing, modular bridges extend coverage to specialized target classes:

* **Smart Contracts (`CONTRACT`):** On-chain logic review, EVM simulation, and invariant testing via Foundry forks.
* **Mobile Binaries (`MOBILE_BINARY`):** Runtime-first traffic interception, Frida instrumentation hooks, and decompilation analysis.
* **GraphQL APIs:** Introspection recovery, schema field suggestion mining, and query depth analysis.
* **CI/CD Pipelines (`CODE_REPO`):** Workflow injection, runner exploitation, and supply-chain misconfiguration auditing.
* **Source Code Repositories (`CODE_REPO`):** Path-glob-scoped static analysis (SAST) and sink-to-source taint tracking.
