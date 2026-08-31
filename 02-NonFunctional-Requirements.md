# Non-Functional Requirements — Autonomous Agentic VAPT System

Quantitative targets below are derived directly from the base document's §1 (hardware)
and §4 (resource allocation table); where the base document did not specify a number,
a reasoned target is proposed and flagged **[PROPOSED]**.

---

## NFR-RES — Resource & Memory Constraints

| ID | Requirement |
|----|-------------|
| NFR-RES-01 | The system MUST NOT allow combined resident model weights + KV cache + agent process overhead to exceed the documented post-hibernation headroom of ~13.0 GiB at any point in Phase 4. |
| NFR-RES-02 | The system MUST maintain a minimum safety margin of **1.5 GB** free RAM above whatever the largest currently-loading model requires, aborting the load and pausing the engagement if the margin cannot be met. **[CONFIRMED]** |
| NFR-RES-03 | The system MUST NOT write working data to `tmpfs` (`/tmp`, 7.7 GB max) as a matter of policy, regardless of available capacity, per the storage-safety constraint in base §1.2. |
| NFR-RES-04 | The system MUST monitor NVMe root partition usage and MUST warn the operator at **85%** utilization and hard-block new artifact writes at **95%** utilization of the 185 GB root volume. **[CONFIRMED]** |
| NFR-RES-05 | The system MUST pin LLM inference threads to the 4 P-Cores (8 threads) and MUST NOT consume more than **4** of the 8 E-core-scheduled threads for concurrent tool subprocesses, to preserve responsiveness of the linter/orchestrator loop and leave headroom for OS/network/JSON parsing. **[CONFIRMED]** |
| NFR-RES-06 | Swap utilization used for application hibernation MUST NOT be allowed to grow unbounded; the system MUST track cumulative bytes paged to `/dev/nvme0n1p8` and `/swapfile` per session and flag abnormal growth (see NFR-REL-05 on SSD wear). |

## NFR-PERF — Performance & Latency

| ID | Requirement |
|----|-------------|
| NFR-PERF-01 | The Pre-Flight Linter (`Qwen2.5-Coder-3B`) MUST sustain at least the documented ~28.5 tok/s throughput on this hardware to keep command-validation latency sub-second per command. |
| NFR-PERF-02 | Model swap (unload N → load N+1) MUST complete, end-to-end, within a bounded time budget of **60 seconds** under normal conditions, else the phase transition is logged as degraded. **[CONFIRMED]** |
| NFR-PERF-05 | The Phase 4.2 tool-execution loop is bounded by a **global 12-hour wall-clock session budget** (FR-COUNCIL-11); the system MUST track elapsed session time from Phase 4 start and MUST trigger automatic transition to Phase 4.3 when the budget is reached, regardless of remaining queued tasks. **[CONFIRMED]** |
| NFR-PERF-03 | Tool subprocess execution MUST respect the default 180-second timeout (FR-TOOL-05); the orchestration loop MUST NOT block on a single hung subprocess beyond that window. |
| NFR-PERF-04 | The full 5-phase lifecycle (excluding arbitrarily long human review pauses) SHOULD complete a single-host, moderate-scope engagement within a session budget the operator can configure; the system MUST report elapsed time per phase for capacity planning. **[PROPOSED]** |

## NFR-REL — Reliability, Availability & Recoverability

| ID | Requirement |
|----|-------------|
| NFR-REL-01 | All engagement state (scope, task queue, findings, gate decisions) MUST be durably committed to SQLite after every discrete step, so that a process crash at any point loses at most the in-flight step, never the full engagement history. |
| NFR-REL-02 | The system MUST be resumable: restarting the agent process after an unclean termination MUST detect the `IN_PROGRESS`/`PAUSED` engagement and offer to continue from last-committed state (ties to FR-ENV-10). |
| NFR-REL-03 | A single model's inference failure (timeout, malformed output, crash) MUST NOT corrupt the state of other models' prior outputs already committed to SQLite. |
| NFR-REL-04 | The operator abort/kill-switch (FR-CTRL-04) MUST bring all subprocess trees and the inference engine to a fully stopped state within **20 seconds** of invocation. **[CONFIRMED]** |
| NFR-REL-05 | The hibernation mechanism (SIGSTOP + page-out) MUST be designed so that repeated daily use does not measurably shorten NVMe swap-partition lifespan beyond normal manufacturer endurance ratings; the system SHOULD log cumulative swap write volume for operator visibility. |
| NFR-REL-06 | The system MUST NOT deliberately terminate or force-close user applications to reclaim memory; freezing (`SIGSTOP`) plus OOM-kill deprioritization (FR-ENV-11) is the mandated mechanism. Per critical-analysis finding C-01 and operator decision, this is **best-effort, OOM-hardened hibernation, not an absolute zero-data-loss guarantee** — the original base document's "zero data loss" wording is superseded by this NFR and by FR-ENV-11/FR-ENV-12, which require detecting and reporting any hibernation casualty rather than assuming none can occur. |

## NFR-SEC — Security (of the tool itself)

*(Cross-referenced in depth in `05-Security-Safety-and-Compliance-Requirements.md`; the
non-functional properties are stated here.)*

| ID | Requirement |
|----|-------------|
| NFR-SEC-01 | The local inference `/v1` endpoint MUST bind to loopback only; exposing it on a routable interface MUST require an explicit, separately-documented operator action outside default configuration. |
| NFR-SEC-02 | No target credentials, session tokens, or discovered secrets MUST ever leave the local host (no cloud API calls, no telemetry) — consistent with the base design's all-local model residency. |
| NFR-SEC-03 | The agent process MUST run under a dedicated, least-privileged OS user/account rather than root, except for specific tool invocations that are individually documented as requiring elevated privilege (e.g., raw-socket scanning). |
| NFR-SEC-04 | Every destructive-capable action path (Tier 2 dynamic bridge, exploit script synthesis) MUST be independently auditable after the fact from the logs alone, without needing to re-run the engagement. |

## NFR-USE — Usability & Observability

| ID | Requirement |
|----|-------------|
| NFR-USE-01 | Status output (FR-CTRL-05) MUST be understandable by an operator without needing to query SQLite directly. |
| NFR-USE-02 | Logs MUST be structured (machine-parseable, e.g., JSON Lines) at the tool-execution and model-invocation layer, while the final report remains human-prose. |
| NFR-USE-03 | Error states (blocked task, degraded GPU fallback, aborted engagement) MUST surface a plain-language reason, not just an internal exception trace. |

## NFR-MAINT — Maintainability & Extensibility

| ID | Requirement |
|----|-------------|
| NFR-MAINT-01 | Council model identities (which model fills which role) MUST be configuration-driven, not hardcoded, so a model can be swapped (e.g., a future quantization or replacement model) without touching orchestration logic. |
| NFR-MAINT-02 | Tier 1 tool wrapper schemas (FR-TOOL-01/02) MUST be defined declaratively (schema files) rather than embedded in prompt strings, so adding a new tool does not require editing model prompts. |
| NFR-MAINT-03 | The sanitization pipeline (FR-TOOL-07) MUST be modular per tool/output-type so new tools can add a parser without modifying the core loop. |

## NFR-PORT — Portability

| ID | Requirement |
|----|-------------|
| NFR-PORT-01 | The system's hard dependencies on Kali-specific paths, kernel modules (`i915`/`xe`), and the Debian 15.3 rolling-release environment MUST be isolated/documented so a future port to another distribution is a configuration change, not a rewrite. |
| NFR-PORT-02 | Hardware-specific tuning (thread pinning, `Q4_K_M`/`Q5_K_M` quantization choices) MUST be expressed as configuration values tied to the documented CPU/GPU profile, not hardcoded assumptions, so the system degrades gracefully (not silently wrong) on different hardware. |

## NFR-COMPLIANCE — Legal & Ethical (summary; full detail in doc 05)

**Decision on record:** authorization / Rules-of-Engagement (RoE) verification is explicitly
**out of scope** for this system — it is not a gate the software enforces. Obtaining and
confirming authorization to test a target is the operator's responsibility outside this
tool. The one compliance-adjacent requirement that remains is the scope-boundary check
that was already part of the original plan's Council Gate 1 (Hermes-3), which is a
content/technical check against declared scope data, not an authorization/legal check.

| ID | Requirement |
|----|-------------|
| NFR-COMPLIANCE-01 | The system's autonomy MUST remain bounded by the non-overridable scope-boundary check performed by Council Gate 1 (FR-COUNCIL-06) regardless of configured autonomy level — this is a technical scope check inherited from the original plan, not an authorization/legal gate. |
