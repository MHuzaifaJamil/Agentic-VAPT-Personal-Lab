# Operational Requirements — Autonomous Agentic VAPT System

This document governs the operational lifecycle of the system: pre-flight checks, phase
sequencing, runtime environmental monitoring, logging fidelity, and maintenance procedures.
Operational controls are structured to ensure local host stability (RAM preservation, swap
monitoring, disk quotas, and desktop hibernation) while maintaining the Dual-Mode Execution
Architecture: autonomous cycles execute non-destructively within configured runtime bounds,
while operator-directed commands execute unconditionally under manual supervision.

Security invariants, operational boundaries, and non-bypassability mandates are owned
exclusively by the Security Specification (`05`).

---

## OPS-LIFECYCLE — Startup / Shutdown Sequence

| ID | Requirement |
|----|-------------|
| OPS-LIFECYCLE-01 | Sequence: pre-flight self-test → Phase 1 → Phase 2 → Phase 3 → Phase 4.1/4.2/4.3 → Phase 5. No phase skipped; each logs `entered_at`/`exited_at`/`outcome` to `engagement_phase_log`. |
| OPS-LIFECYCLE-02 | `resume` re-enters at the last incomplete phase, never restarts from Phase 0. Re-running pre-flight is fine; re-running an already-done Phase 1 hibernation MUST be detected and skipped. |
| OPS-LIFECYCLE-03 | Both normal completion and `abort` MUST guarantee Phase 5 runs — an aborted engagement still restores suspended apps. Phase 5 is not complete until the `state.db` backup is also written; a restore without it is partial, logged as such. |
| OPS-LIFECYCLE-04 | "Hibernation" (desktop-app freeze/resume) is unrelated to engagement-data durability — a crash of the agent process itself, not just a frozen app, MUST NOT lose engagement data beyond the single in-flight step. Both guarantees hold independently; neither substitutes for the other. |

## OPS-MONITOR — Runtime Monitoring

| ID | Requirement |
|----|-------------|
| OPS-MONITOR-01 | During Phase 4, continuously track: RAM margin, disk usage, elapsed session time, per-target counters. |
| OPS-MONITOR-02 | Breaching the RAM margin or the 95% disk block **pauses** the engagement — a safety stop, distinct from the task-queue loop's own no-pause auto-pivot/auto-transition bounds. Logged with the triggering threshold. |
| OPS-MONITOR-03 | Thermal throttling: a deployment-time feasibility check, not an assumption. If the kernel exposes a throttle/PROCHOT signal, log a degraded-performance flag on it; if not exposed at all, downgrade to "not implementable as specified" and treat any phase-latency targets as best-effort. |
| OPS-MONITOR-04 | `status` surfaces all OPS-MONITOR-01 metrics live, not a stale start-time snapshot. |

## OPS-LOG — Logging

| ID | Requirement |
|----|-------------|
| OPS-LOG-01 | `tool_execution_logs`/`model_invocation_logs` are structured (JSON-serializable), sufficient to reconstruct a timeline without reading source code. |
| OPS-LOG-02 | Log volume counts against the disk-quota thresholds as part of OPS-MONITOR-01 — logs are artifacts too. |
| OPS-LOG-03 | Degraded-mode events (GPU fallback, hibernation OOM casualty, thermal throttling, model-swap overrun) log at a severity distinguishable from routine events. |

## OPS-MAINT — Maintenance Procedures

| ID | Requirement |
|----|-------------|
| OPS-MAINT-01 | Tool-signature freshness (`nuclei` templates, CVE feeds, wordlists) is explicitly out of scope for this planning phase. |
| OPS-MAINT-02 | Re-verify the Local Engine Client (load/unload/inference smoke test) after any Kali kernel/driver update, given SYCL/Level-Zero's maturity risk. |
| OPS-MAINT-03 | `state.db` backups SHOULD be pruned manually by the operator — no automatic pruning in scope. |

## OPS-DEGRADE — Degraded-Mode Behavior Summary

| Condition | Behavior |
|---|---|
| GPU offload unavailable | CPU-only fallback, log degraded, continue |
| Model swap exceeds 60s | Log degraded, continue |
| Hibernated PID killed by OOM | Log partial hibernation success, continue |
| Suspected prompt injection | Log prominently, continue (detection only) |
| Thermal throttling (if measurable) | Log degraded-performance flag, continue |
| RAM safety margin breached | **Pause** (safety stop) |
| Disk 95% capacity hit | **Pause**, block further writes |
| Per-target task cap or zero-yield circuit breaker hit | Auto-pivot to next target, no pause |
| 12-hour session budget hit | In Autonomous Mode, auto-transition to the reporting phase, no pause; in Operator-Directed Mode, extend or continue per operator configuration |
| Privileged helper unavailable | cgroup v2 fallback, log degraded, continue |
| Reconnect/re-auth prompt on resume | Expected — log informational, not degraded |
| Post-swap `MemAvailable` poll exceeds 5s | Log degraded-swap alert, continue |

---

## Authority & Conflict Resolution

This document specifies day-to-day run procedures, host resource monitoring, and degraded-mode
operational fallbacks. In the event of any conflict, discrepancy, or ambiguity between operational
routines, runtime ceilings, and system control mandates, the **Security, Safety & Compliance
Requirements (`05`)** serves as the final and supreme authority across the entire system.
