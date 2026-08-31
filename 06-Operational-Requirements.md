# Operational Requirements — Autonomous Agentic VAPT System

Covers the day-to-day run lifecycle: startup, monitoring during a run, shutdown, and
maintenance — as distinct from the one-time architectural requirements in `01`-`05`.

---

## OPS-LIFECYCLE — Startup / Shutdown Sequence

| ID | Requirement |
|----|-------------|
| OPS-LIFECYCLE-01 | The operational sequence MUST be: `FR-PRE` (pre-flight) → Phase 1 (env/hibernate) → Phase 2 (gateway) → Phase 3 (tool bridge) → Phase 4.1/4.2/4.3 (council loop) → Phase 5 (restore). No phase may be skipped, and each MUST log its `entered_at`/`exited_at`/`outcome` to `engagement_phase_log` (DR-SCHEMA-09). |
| OPS-LIFECYCLE-02 | A `resume` action (FR-CTRL-03) MUST re-enter at the phase recorded as the last incomplete one in `engagement_phase_log`, not restart from Phase 0 — re-running pre-flight checks on resume is acceptable (cheap, safe) but re-running Phase 1 hibernation on an already-hibernated system MUST be detected and skipped. |
| OPS-LIFECYCLE-03 | Shutdown via normal completion (engagement reaches `COMPLETE`) and shutdown via `abort` (SEC-KILL) MUST both guarantee Phase 5 hibernation-exit runs — an aborted engagement MUST still restore the operator's suspended applications, not leave them frozen. Per the confirmed **MUST**-level backup requirement (DR-BACKUP-01), Phase 5 is not considered complete until the timestamped `state.db` backup has also been written — a restore that succeeds without that backup existing is a partial, not full, Phase 5 completion, and MUST be logged as such. |
| OPS-LIFECYCLE-04 | **(Clarification, confirmed)** "Hibernation" in this system refers strictly to the Phase 1/5 mechanism that freezes/resumes the *operator's own desktop applications* to reclaim RAM (FR-ENV-03..12) — it is unrelated to, and MUST NOT be confused with, the durability of the *engagement's own data*. Per NFR-REL-01, every engagement state change (task status, gate decision, finding, model-invocation record) is committed to the persistent SQLite store (`03-Data-and-Storage-Requirements.md`) and NVMe artifact files immediately, not held only in the agent process's own memory. Consequently, **a crash of the agent process itself — not just a frozen desktop app — MUST NOT lose engagement data**: at most the single in-flight step is lost (NFR-REL-01), and `resume` (OPS-LIFECYCLE-02) picks the engagement back up from the last committed state. These are two independent guarantees (desktop-app hibernation safety via FR-ENV-11/12, and engagement-data crash-safety via NFR-REL-01/02) and both must hold — one is not a substitute for the other. |

## OPS-MONITOR — Runtime Monitoring

| ID | Requirement |
|----|-------------|
| OPS-MONITOR-01 | While Phase 4 is active, the system MUST continuously track: available RAM (against NFR-RES-02's 1.5 GB margin), NVMe root usage (against NFR-RES-04's 85%/95% thresholds), elapsed session time (against the 12-hour budget, NFR-PERF-05), and per-target task/circuit-breaker counters (DR-SCHEMA-02). |
| OPS-MONITOR-02 | Breaching the RAM margin or the 95% disk hard-block MUST pause the engagement (distinct from the no-pause diminishing-returns loop bound in FR-COUNCIL-11, which governs task-queue progression, not resource exhaustion) — a resource-exhaustion pause is a safety stop, not a loop-bound decision, and MUST be logged with which threshold triggered it. |
| OPS-MONITOR-03 | **Feasibility check — thermal monitoring (critical-analysis finding C-10):** the base plan's implied sustained-throughput figures assume no thermal throttling, but no mechanism for detecting throttling is specified. Before this requirement can be implemented as a MUST, it MUST first be verified on the actual target hardware whether CPU/package thermal data is exposed via a readable sysfs thermal zone or via `lm-sensors` under the installed Kali kernel — this is a **feasibility check to perform during deployment, not an assumption to build on now.** **(Confirmed trigger condition)** If exposed, the system SHOULD monitor the CPU's own reported throttle/PROCHOT signal (not a guessed fixed temperature) during Phase 4 and log a degraded-performance flag whenever the kernel itself reports a throttling event; if neither thermal telemetry nor a throttle signal is exposed on this hardware, this requirement is downgraded to "not implementable as specified" and the phase-latency NFRs (`02`) should be read as best-effort rather than guaranteed. |
| OPS-MONITOR-04 | `status` (FR-CTRL-05, IR-CTRL-02) MUST surface all OPS-MONITOR-01 metrics live, not just at engagement start — a status check 6 hours into a 12-hour session must reflect current state, not a stale snapshot. |

## OPS-LOG — Logging

| ID | Requirement |
|----|-------------|
| OPS-LOG-01 | `tool_execution_logs` and `model_invocation_logs` MUST be structured (JSON-serializable rows, per NFR-USE-02) sufficient to reconstruct a timeline without cross-referencing source code. |
| OPS-LOG-02 | Log volume from a 12-hour, multi-target, 30-tasks-per-target session MUST be checked against the artifact disk-quota thresholds (NFR-RES-04) as part of OPS-MONITOR-01 — logs are artifacts too, not exempt from the quota. |
| OPS-LOG-03 | Degraded-mode events (GPU offload fallback to CPU per FR-GATE-04, hibernation OOM casualty per FR-ENV-12, thermal throttling per OPS-MONITOR-03, model-swap budget overrun per NFR-PERF-02) MUST all be logged at a distinguishable severity from routine informational events, so a post-engagement review can quickly find "what went wrong" without reading every line. |

## OPS-MAINT — Maintenance Procedures

| ID | Requirement |
|----|-------------|
| OPS-MAINT-01 | Tool signature freshness (`nuclei` templates, CVE feeds, wordlists) is **explicitly out of scope for this planning phase** (per `08-Assumptions-Constraints-Dependencies.md`) — no automatic update mechanism is required or assumed. This is a known limitation, not an oversight: see risk `07-Risk-Register.md` RISK-TOOLDECAY. |
| OPS-MAINT-02 | The Local Engine Client abstraction (IR-ENGINE-01) SHOULD be re-verified (a quick smoke test: load/unload/inference round-trip) after any Kali rolling-release kernel or driver update, since the SYCL/Level-Zero backend's maturity (finding C-05) makes it a plausible breakage point on an unpinned rolling release. |
| OPS-MAINT-03 | The `state.db` backup taken at Phase 5 (DR-BACKUP-01) SHOULD be periodically pruned by the operator manually — no automatic pruning is in scope for this planning phase, consistent with OPS-MAINT-01's stance on deferring maintenance automation. |

## OPS-DEGRADE — Degraded-Mode Behavior Summary

A single reference table of every degraded (non-fatal, non-abort) condition this
system's requirements define, since they're otherwise scattered across `01`/`02`/`05`:

| Condition | Triggering Requirement | Required Behavior |
|---|---|---|
| GPU offload unavailable | FR-GATE-04, finding C-05 | Fall back to CPU-only inference, log as degraded, continue |
| Model swap exceeds 60s | NFR-PERF-02 | Log as degraded, continue |
| Hibernated PID killed by OOM despite protection | FR-ENV-11/12 | Log as partial hibernation success, continue |
| Suspected prompt injection flagged | FR-TOOL-13, SEC-PROMPT-04 | Log prominently, continue (detection only, not a stop) |
| Thermal throttling detected (if measurable at all — OPS-MONITOR-03) | C-10 | Log degraded-performance flag, continue |
| RAM margin breached | NFR-RES-02, OPS-MONITOR-02 | **Pause** engagement (safety stop, not loop-bound) |
| Disk 95% hard-block hit | NFR-RES-04, OPS-MONITOR-02 | **Pause** engagement, block further artifact writes |
| Per-target task cap (30) or circuit breaker (3, state-delta-based) hit | FR-COUNCIL-11/11a | Auto-pivot to next target, no pause |
| 12-hour global session budget hit | FR-COUNCIL-11, NFR-PERF-05 | Auto-transition to Phase 4.3, no pause |
| Privileged hibernation helper/capability unavailable | FR-ENV-13, finding C-15 | Fall back to cgroup v2 memory limits, log as degraded, continue |
| Resumed application shows reconnect/re-auth prompt (network session lapsed) | FR-ENV-14, finding C-16 | Expected, not a fault — log as informational, not degraded |
| Post-swap `MemAvailable` poll exceeds 5s | FR-GATE-10, IR-ENGINE-06, finding C-18 | Log as degraded-swap alert (same handling as a slow swap under NFR-PERF-02), continue |
