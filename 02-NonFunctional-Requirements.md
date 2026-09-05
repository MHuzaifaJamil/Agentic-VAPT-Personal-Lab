# Non-Functional Requirements — Autonomous Agentic VAPT System

Quantitative performance, resource, reliability, usability, maintainability, and
portability targets for the system. Every numeric target here establishes an operational
baseline enforced on live, runtime-measured values rather than theoretical specifications.
In Autonomous Mode, these thresholds govern automated tasks to prevent target degradation
and local host resource exhaustion; in Operator-Directed Mode, operational bounds, session
budgets, and tool timeouts adapt dynamically or yield to explicit operator instruction.

Security-of-the-tool properties (local-only data residency, non-destructive autonomous
boundaries, least privilege, auditability, and unconditional operator execution authority)
are owned exclusively by the Security Specification (`05`) and govern all downstream controls.

---

## NFR-RES — Resource & Memory Constraints

| ID | Requirement |
|----|-------------|
| NFR-RES-01 | Combined resident weights + KV cache + agent overhead MUST NOT exceed the documented post-hibernation headroom (~13.0 GiB) at any point in Phase 4. |
| NFR-RES-02 | Minimum safety margin: **1.5 GB** free RAM above the largest currently-loading model's requirement; abort the load and pause on shortfall. **[CONFIRMED]** |
| NFR-RES-03 | MUST NOT write working data to `tmpfs` (`/tmp`), regardless of available capacity. |
| NFR-RES-04 | Monitor NVMe root usage; warn at **85%**, hard-block new artifact writes at **95%** (of 185 GB). **[CONFIRMED]** |
| NFR-RES-05 | Pin inference threads to the 4 P-Cores (8 threads); MUST NOT consume more than **4** of 8 E-core-scheduled threads for tool subprocesses. **[CONFIRMED]** |
| NFR-RES-06 | Track cumulative swap-paged bytes per session; flag abnormal growth at **>2 GiB** within a session. **[CONFIRMED]** |

## NFR-PERF — Performance & Latency

| ID | Requirement |
|----|-------------|
| NFR-PERF-02 | Model swap (unload N → load N+1) completes within **60 seconds**; else log the phase transition as degraded. **[CONFIRMED]** |
| NFR-PERF-03 | Tool subprocess execution respects documented tiered timeouts as operational baselines; the autonomous orchestration loop MUST NOT block on a hung subprocess beyond that window. Timeouts for active operator-directed fuzzing, brute-force, or exploitation tasks are configurable and extendable on demand. |
| NFR-PERF-05 | Global **12-hour** wall-clock session budget acts as an autonomous unattended ceiling; auto-transitions to reporting when reached during autonomous runs. When operating under direct operator control, the session budget is extendable or deferrable via CLI configuration. **[CONFIRMED]**|

## NFR-REL — Reliability, Availability & Recoverability

| ID | Requirement |
|----|-------------|
| NFR-REL-01 | All engagement state durably commits to SQLite after every discrete step — a crash loses at most the in-flight step, never full history. |
| NFR-REL-02 | Resumable: restarting after an unclean termination detects the `IN_PROGRESS`/`PAUSED` engagement and offers to continue from last-committed state. |
| NFR-REL-03 | One model's inference failure MUST NOT corrupt other models' prior committed outputs. |
| NFR-REL-04 | The kill-switch brings all subprocess trees + the inference engine to a fully stopped state within **20 seconds**. **[CONFIRMED]** |
| NFR-REL-05 | Repeated daily hibernation MUST NOT measurably shorten NVMe swap-partition lifespan beyond normal endurance ratings; SHOULD log cumulative swap-write volume. |
| NFR-REL-06 | Hibernation is **best-effort, OOM-hardened — not an absolute zero-data-loss guarantee**. Any OOM casualty among suspended processes is detected and reported, never silently assumed absent. |

## NFR-USE — Usability & Observability

| ID | Requirement |
|----|-------------|
| NFR-USE-01 | `status` output MUST be understandable without querying SQLite directly. |
| NFR-USE-02 | Logs are structured (JSON Lines) at the tool/model-invocation layer; the final report stays human-prose. |
| NFR-USE-03 | Error states surface a plain-language reason, not just an internal exception trace. |

## NFR-MAINT — Maintainability & Extensibility

| ID | Requirement |
|----|-------------|
| NFR-MAINT-01 | Council model identities are configuration-driven, not hardcoded. |
| NFR-MAINT-02 | Tier 1 tool schemas are declarative files, not embedded in prompt strings. |
| NFR-MAINT-03 | The sanitization pipeline is modular per tool/output-type. |

## NFR-PORT — Portability

| ID | Requirement |
|----|-------------|
| NFR-PORT-01 | Kali-specific paths, kernel modules, and Debian-15.3-specific assumptions are isolated/documented so a future port is a config change, not a rewrite. |
| NFR-PORT-02 | Hardware-specific tuning (thread pinning, quantization choice) is expressed as configuration tied to the documented CPU/GPU profile — degrades to a logged fallback, never silently wrong, on different hardware. |

---

## Authority & Conflict Resolution

This non-functional specification defines physical performance ceilings, operational
timings, and system health baselines. In the event of any conflict, discrepancy, or
ambiguity between resource governance thresholds and operational execution mandates,
the **Security, Safety & Compliance Requirements (`05`)** serves as the final and supreme
authority across the system.
