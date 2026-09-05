# Functional Requirements — Autonomous Agentic VAPT System

Priority key (MoSCoW): **M** = Must have, **S** = Should have, **C** = Could have.
This document governs the phase-by-phase execution pipeline: operational workflows,
execution order, council role deliverables, and state transition triggers. The pipeline
implements a Dual-Mode Execution Architecture: Autonomous Mode enforces non-destructive
testing boundaries (permitting read and safe verification writes while barring destructive
mutations and DoS), whereas Operator-Directed Mode executes human instructions unconditionally
with zero refusal. Gating and containment rationale are governed authoritatively by the
Security Specification (`05`).

---

## FR-PRE — Phase 0: Pre-Flight Self-Test

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-PRE-01 | Verify the inference engine is installed, version recorded, not already running, before Phase 1. | M |
| FR-PRE-02 | Verify the Level Zero/SYCL/OpenCL runtime can enumerate the Arc iGPU; fall back to documented CPU-only mode on failure, never fail silently. | M |
| FR-PRE-03 | Verify each council model file exists at its expected path/quantization (checksum or size check) before Phase 4. | M |
| FR-PRE-04 | Verify presence of every Tier 1 tool binary; record installed versions to the state store. | M |
| FR-PRE-05 | Verify the NVMe artifact path exists, is writable, and is not a `tmpfs` mount. | M |
| FR-PRE-06 | Record RAM/swap/disk-free as a pre-flight baseline snapshot before Phase 1 hibernation begins. | M |
| FR-PRE-07 | Pre-flight produces one pass/fail report; any failure blocks Phase 1 unless the operator overrides with a logged justification. | M |
| FR-PRE-08 | One-time GPU-offload benchmark: run the same fixed inference with SYCL offload and forced CPU-only, compare tok/s. If offload fails or doesn't beat CPU-only, flag the **entire engagement** CPU-only from the start (not discovered mid-Phase-4). Record both measurements in `engagement_phase_log`. | M |

---

## FR-ENV — Phase 1: Environment, Storage & Memory Preparation

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-ENV-01 | Redirect all agent artifacts/logs/temp files to the NVMe path; MUST NOT write working data to `tmpfs`-backed `/tmp`. | M |
| FR-ENV-02 | Set `TMPDIR`/`TEMP`/`TMP` to the NVMe path for the agent process tree and any subprocess. | M |
| FR-ENV-03 | Enumerate active GUI processes; classify each "hibernation-eligible" or "protected" against a fixed denylist (`systemd`, `dbus`, compositor, session manager, audio server) before any signal. | M |
| FR-ENV-04 | MUST NOT `SIGSTOP` a process holding an open file lock on unsaved document state — unconditional, not operator-waivable. | M |
| FR-ENV-05 | Record the full PID/process-tree of every suspended application, sufficient to reverse deterministically in Phase 5. | M |
| FR-ENV-06 | No runtime confirmation prompt before the first `SIGSTOP` — invoking `start` is the operator's consent for the whole non-interactive pipeline. Suspended-app list still logged (FR-ENV-05). | M |
| FR-ENV-07 | SHOULD trigger `process_madvise(MADV_PAGEOUT)`/cgroup reclamation on suspended PIDs; MUST NOT touch protected processes. Requires elevated capability the main process doesn't hold — see FR-ENV-13. | S |
| FR-ENV-08 | Re-measure available RAM after hibernation; abort progression to Phase 2 if headroom is below the smallest model's requirement plus the fixed safety margin. | M |
| FR-ENV-09 | Initialize the SQLite state store before Phase 2 begins. | M |
| FR-ENV-10 | An existing `IN_PROGRESS`/`PAUSED` engagement is offered for resume, never silently overwritten. | M |
| FR-ENV-11 | Before the memory-reclamation step, lower OOM-kill priority for every suspended PID to `oom_score_adj = -900` (not `-1000`) — hibernated apps are the *last* OOM-kill candidate; the agent's own processes are more eligible by comparison. | M |
| FR-ENV-12 | Verify every suspended PID is still alive post-hibernation; log and report any OOM casualty, and mark the outcome partial/degraded, not full success. | M |
| FR-ENV-13 | `SIGSTOP`/`oom_score_adj`/`process_madvise` MUST run via a narrow, single-purpose helper (`vapt-freezer-helper`) granted only the specific capability needed (`setcap cap_sys_ptrace+ep`) — the main agent process MUST NOT hold elevated capability. Fall back to cgroup v2 limits if the helper/capability is unavailable, never silently skip. | M |
| FR-ENV-14 | The hibernation guarantee covers process memory/UI state only, not network/session continuity — resumed apps may show reconnect prompts; this is expected, documented behavior, not a defect. | M |

---

## FR-GATE — Phase 2: Local Inference Gateway

**Engine:** `llama.cpp --server`, native SYCL backend. No `keep_alive` hot-swap
exists in raw `llama.cpp` — load/unload is explicit process spawn/terminate via the
**Local Engine Client** interface, abstracted so `ollama` can substitute later.

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-GATE-01 | Expose a single loopback-only OpenAI-compatible endpoint (`127.0.0.1:11434/v1`); MUST NOT bind non-loopback by default. | M |
| FR-GATE-02 | Hard single-model-residency: at most one council model resident at any instant; loading a second requires the first fully unloaded and confirmed first. | M |
| FR-GATE-03 | Pin inference threads to the 4 P-Core/8-thread group; leave E-Cores free for subprocess/tool execution. | M |
| FR-GATE-04 | Attempt SYCL GPU offload; fall back to CPU-only (logged degraded) if unavailable, rather than failing the engagement. | M |
| FR-GATE-05 | Evict weights+KV cache within a bounded window after each phase step; verify freed memory before declaring the step complete. | M |
| FR-GATE-06 | Log every inference call (model, role, token counts, latency, phase/step ID) to `model_invocation_logs`. | M |
| FR-GATE-07 | Enforce per-model context ceilings: 8k (DeepSeek-R1-0528-Qwen3-8B / Hermes-3-Llama-3.1-8B / Mistral-7B-Instruct-v0.3), 16k (Qwen2.5-Coder-7B-Instruct / Ministral-8B-Instruct-2410), 4k (Qwen2.5-Coder-3B-Instruct). Truncate/summarize on overflow, never silently error. | M |
| FR-GATE-08 | Detect engine crash/unresponsiveness (no token progress within a timeout); attempt one restart, escalate to `PAUSED` on repeated failure. | M |
| FR-GATE-09 | Model load/unload exclusively via the Local Engine Client; `unload` MUST verify complete OS-level process exit (`waitpid`), not just an API ack. | M |
| FR-GATE-10 | After confirmed exit, poll `/proc/meminfo` `MemAvailable` and MUST NOT spawn the next model until it clears the documented minimum-headroom threshold. Bounded to 5s; raise a degraded-swap alert on timeout rather than spawn into a tight memory state. | M |

---

## FR-TOOL — Phase 3: Security Framework & Kali Tool Bridge

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-TOOL-01 | Provide schema-validated Tier 1 wrappers for: `nmap`, `masscan`, `nuclei`, `ffuf`, `feroxbuster`, `gobuster`, `sqlmap`, `nikto`, `whatweb`, `wafw00f`, `testssl`, `script_runner` (`FR-TOOL-16`). | M |
| FR-TOOL-02 | Each Tier 1 wrapper declares recognized flags, required arguments, and execution profiles machine-readably for Gate 2 validation. In Autonomous Mode, destructive capabilities (such as direct file wipes, database alters, drops, deletes, updates, or DoS triggers) are blocked to maintain non-destructive testing. In Operator-Directed Mode, all wrapper flag restrictions and parameter suppressions stand down completely to execute the exact requested parameters. | M |
| FR-TOOL-03 | Tier 2 dynamic bridge (`run_security_command`): eligible binary MUST resolve (invocation path, not symlink target) inside `/usr/bin/`, `/usr/sbin/`, or `/opt/`; execution within scope is fully autonomous, no per-binary approval. | M |
| FR-TOOL-04 / 04a | Non-shell execution (`shell=False`, explicit argv) — no model output ever becomes a shell string; every subprocess spawns in its own session (`start_new_session=True`) so the kill-switch can reach its whole process group. | M |
| FR-TOOL-05 | Every subprocess has a mandatory timeout: Quick Probes 180s / Targeted Scans 900s / Deep-Full-Range 1800s. | M |
| FR-TOOL-06 | Tier 2 behavioral boundaries enforce the dual-mode policy: In Autonomous Mode, actions MUST NOT perform state destruction (strictly prohibiting DROP, DELETE, ALTER, UPDATE, rm, mkfs, dd, shred, fork-bombs, or DoS/resource-exhaustion tools). Safe reads (GET/SELECT) and non-destructive writes (POST) are permitted. In Operator-Directed Mode, behavioral denylists stand down entirely, executing the requested command chain as instructed. | M |
| FR-TOOL-06a | High-risk testing categories (brute-force, active exploitation, lateral movement) run autonomously when enabled via runtime flags or profile configuration. When dispatched directly by the operator via manual directive or console dispatch, these tasks execute immediately without requiring pre-set opt-in flags. | M |
| FR-TOOL-06b | In Autonomous Mode, an unconfigured high-risk task is marked DEFERRED and the engine continues discovery along alternative non-destructive paths. Any high-risk directive initiated or requested by the operator executes immediately with zero refusal. | M |
| FR-TOOL-06c | The three flags are settable at `start`, independently updatable at `resume`; a change applies only to tasks generated after it, and is timestamped in `engagement_flag_history`. | M |
| FR-TOOL-07 | Sanitize raw stdout/stderr into structured signal (ports, banners, URLs, status codes); discard HTML/repetitive-404/binary noise before it reaches model context. | M |
| FR-TOOL-08 | Persist full unsanitized raw output to the artifact store regardless of what's summarized — evidence is never lost to summarization. | M |
| FR-TOOL-09 | Record exact argv, timestamps, exit code, and task ID for every subprocess execution in `tool_execution_logs`. | M |
| FR-TOOL-10 | SHOULD expose Burp Suite/Caido MCP configs and multi-turn assessment templates as reusable methodology assets. | S |
| FR-TOOL-11 | Support pointing `claude-bug-bounty`/`CyberStrike`/`strix` at the local endpoint via env-var overrides, no code modification. | S |
| FR-TOOL-12 | All target-derived content (banners, HTTP responses, tool logs) MUST be wrapped in boundary markers (<tool_output_untrusted>...</tool_output_untrusted>) prior to ingestion by model contexts to maintain context separation. | M |
| FR-TOOL-13 | SHOULD run a lightweight heuristic injection-pattern detector over raw target output (telemetry and detection only, never blocking or interrupting execution). | S |
| FR-TOOL-14 | Per-target spawn rate caps serve as anti-DoS and target stability guardrails during autonomous operations (default 10 invocations/s standard, 1/s high-volume). When running under direct operator instruction, rate limits are dynamically adjustable or bypassable up to system/network capacity upon operator demand. | M |
| FR-TOOL-15 | Configured target credentials propagate automatically to every Tier 1/Tier 2 call via env vars; only a `sha256(...)[:12]` correlation hash is logged, never the raw credential. Two distinct identities (low/high-privilege) are registrable as separate named sets. | M |
| FR-TOOL-16 | `script_runner`: the only path for executing a linter-approved multi-line script — `{script_body, interpreter, workspace_subdir}`, never an inline `-c`/`-e` string (does not reopen `FR-TOOL-06(b)`). `workspace_subdir` MUST resolve inside the artifact path; the script MUST pass the offline linter (`FR-COUNCIL-09a`) first; runs as `<interpreter> <file>` under the Targeted-Scans (900s) timeout tier. | M |

---

## FR-COUNCIL — Phase 4: State-Driven Council Execution

### 4.1 Strategic Planning & Scope Gate

Council Gate 1 is two-tier: Tier 0 (deterministic, every task) + Tier 1
(`Hermes-3-Llama-3.1-8B`, contextual sanity-check).

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-COUNCIL-01 | `DeepSeek-R1-0528-Qwen3-8B` ingests scope/IP-ranges/RoE and produces an ordered, hypothesis-driven task queue. | M |
| FR-COUNCIL-02 | Strategist output is a structured, parseable plan (`attack_paths`/`task_queue`), not free-form prose. | M |
| FR-COUNCIL-03 | Strategist fully unloads before the Gatekeeper loads (single-residency, FR-GATE-02). | M |
| FR-COUNCIL-03a | Deterministic Tier 0 scope checker validates autonomous tasks against configured operational target boundaries to guide autonomous crawling. For MANUAL_OPERATOR-origin tasks, Tier 0 scope checks stand down completely: operator instructions execute unconditionally without boundary interception. | M |
| FR-COUNCIL-04 | Tier 1 (Hermes-3-Llama-3.1-8B) evaluates task alignment and non-destructive adherence exclusively for AUTONOMOUS_COUNCIL-origin tasks. It is completely bypassed for any MANUAL_OPERATOR-origin task, ensuring the model never refuses, alters, or intercepts an operator's direct instructions. | M |
| FR-COUNCIL-05 | Both tiers' decisions and rationale are persisted per task; an AUTONOMOUS_COUNCIL task logs both gate outcomes, while a MANUAL_OPERATOR task's rationale records direct operator dispatch with automated scope gates bypassed. | M |
| FR-COUNCIL-06 | In Autonomous Mode, a task failing non-destructive or operational validation is rejected and logged without stopping the pipeline. In Operator-Directed Mode, manual tasks bypass Tier 0 and Tier 1 gates entirely and dispatch directly to Phase 4.2 execution without refusal. | M |

### 4.2 Tool Execution, Linting & Exploitation

Zero model-swapping inside the active loop: `Qwen2.5-Coder-7B-Instruct` stays
resident; Gate 2 is deterministic code, not `Qwen2.5-Coder-3B`.

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-COUNCIL-07 | Operator loads once at Phase 4.2 start, stays resident for the whole per-target loop; its per-task context includes current opt-in-flag state (waste-avoidance only — enforcement is at FR-TOOL-06a regardless). | M |
| FR-COUNCIL-08 | Gate 2 provides deterministic schema and parameter validation. In Autonomous Mode, it enforces non-destructive boundaries (blocking SQL data mutations like UPDATE/DELETE/DROP and system-level wipes). In Operator-Directed Mode, Gate 2 validates syntax format only and does not restrict or reject operator-approved commands or payloads; never invokes `Qwen2.5-Coder-3B`. | M |
| FR-COUNCIL-09 | On rejection, the Operator regenerates up to 3 attempts; beyond that, the task is `BLOCKED` with the rejection reason — never dropped or force-executed. | M |
| FR-COUNCIL-09a | `Qwen2.5-Coder-3B` loads only offline, between phases, for multi-line script syntax checks. A passing script becomes eligible for `script_runner` (FR-TOOL-16). | S |
| FR-COUNCIL-10 | The resident Operator evaluates output and appends any follow-on task to `task_queue` — never acts outside the queue. | M |
| FR-COUNCIL-10a | A follow-on signal belonging to a different domain (`target_type`) is queued against that domain's own requirement set, not force-fit into the current task's domain. | S |
| FR-COUNCIL-11 | Task-queue loop bound: 30-task-per-target baseline cap (CAPPED), 3-consecutive-zero-yield circuit breaker (CIRCUIT_BROKEN), and 12-hour default session budget protect unattended autonomous runs from resource runaway. In Autonomous Mode, reaching limits triggers an auto-pivot to the next target or transition to Phase 4.3. In Operator-Directed Mode, task caps and session limits stand down or dynamically adjust to operator demands. | M |
| FR-COUNCIL-11a | "Zero-yield" = no new discovered_entities row, preventing unattended execution from spinning on repetitive output. Two class-aware counters (STANDARD threshold 3, HIGH_ATTEMPT threshold 15 default) guide autonomous progression. Counters apply to autonomous task cycling and do not restrict explicit operator-dispatched actions. | M |
| FR-COUNCIL-11b | Failure-based circuit breaker: 3 consecutive network-error/timeout runs marks a target UNREACHABLE during autonomous crawling, pivoting resources to viable targets. Operator-dispatched tasks can re-target marked hosts at any time to verify connectivity. | M |
| FR-COUNCIL-12 | Operator unloads only when Phase 4.2 ends for the whole engagement (every target terminal, or the 12h budget hit) — never per-task/per-target. | M |

### 4.3 Evidence Adjudication & Reporting

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-COUNCIL-13 | `Mistral-7B-Instruct-v0.3` (Gate 3) evaluates candidate findings against raw evidence, recording `CONFIRMED, DISMISSED, or INFO` with contextual rationale. | M |
| FR-COUNCIL-14 | Gate 3 evaluates candidate findings against common false-positive patterns (WAF blocks, rate-limit responses, generic 5xx, honeypots) to maintain signal quality. Findings flagged with anomalies may still be marked for review or promoted via operator instruction. | M |
| FR-COUNCIL-14a | Adjudication evaluates verified impact, proper vulnerability categorization (e.g., distinguishing unauthenticated endpoints from IDOR/BOLA), and baseline-versus-probe response differences. Operator directives can override classification flags to preserve exploratory observations. | M |
| FR-COUNCIL-15 | Confirmed findings populate the primary VAPT_FINDING register. Non-confirmed, informational, or remediated observations are routed to the consolidated INFO_REGISTER or retained as auxiliary artifacts based on operator reporting preferences. | M |
| FR-COUNCIL-16 | `Ministral-8B-Instruct-2410` (Reporter, a distinct model from the Strategist) ingests confirmed findings, produces CWE/CVE mapping, root-cause narrative, remediation. | M |
| FR-COUNCIL-16a | The model proposes CVSS 3.1 metric vectors; a deterministic calculator computes final base scores. The operator may override any vector component directly during report review. | M |
| FR-COUNCIL-17 | Two distinct document types, never conflated: (a) one `VAPT_FINDING` report per `CONFIRMED` finding; (b) one consolidated `INFO_REGISTER` per engagement, regenerated in place. Both emit as Markdown to `pending-approval/` first. A `REGRESSION_CHECK`-origin finding still gets its own report, marked carried-forward. | M |
| FR-COUNCIL-17a | Rendered HTML/PDF exports are produced upon operator command (approve-report or explicit CLI export), ensuring the operator controls final report delivery. | M |
| FR-COUNCIL-17b | Grounding verification validates that URLs, endpoints, and parameters cited in finding drafts match observed raw tool evidence. Flagged discrepancies are highlighted for operator review rather than silently dropped. | M |
| FR-COUNCIL-18 | Secrets are redacted by default from raw evidence presented to the Reporter model via a reversible redaction_map. Redacted secrets are restored upon report finalization, with raw values remaining intact in the secure local artifact store. | M |

---

## FR-HIB — Phase 5: Hibernation & Restoration

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-HIB-01 | Mark engagement state `COMPLETE`/`PAUSED` before teardown begins. | M |
| FR-HIB-02 | Evict all resident weights/KV caches; verify freed memory before application restoration. | M |
| FR-HIB-03 | `SIGCONT` every suspended PID (FR-ENV-05); verify each resumed (not zombie/dead), never assume success. | M |
| FR-HIB-04 | A missing previously-suspended process is logged as a discrepancy, not a whole-restoration failure. | M |
| FR-HIB-05 | SHOULD report restoration completion time; sub-2-second expectation for paged-out memory. | S |

---

## FR-CTRL — Operator Control Surface

CLI-only (no GUI/web dashboard). Every action below is reachable as a `vaptctl`
subcommand.

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-CTRL-01 | `start` accepts a target scope (IP ranges/domains). Legal authorization, permissions, and rules of engagement (RoE) are strictly the operator's responsibility outside the tool. Operational scope limits guide autonomous scanning only and do not restrict operator-directed commands. | M |
| FR-CTRL-02 | `pause` halts task-queue progression at the next safe checkpoint (not mid-subprocess) without losing state. | M |
| FR-CTRL-03 | `resume` continues a `PAUSED` engagement from last-committed state; accepts optional updates to the three high-risk flags (FR-TOOL-06c). | M |
| FR-CTRL-04 | `abort` immediately terminates all subprocess trees, unloads any resident model, marks the engagement ABORTED, within 20 seconds. | M |
| FR-CTRL-05 | `status` shows: phase, resident model, RAM/swap headroom, queue depth, finding counts by state. | M |
| FR-CTRL-06 | Mode configuration supports distinct operating postures: Autonomous Non-Destructive Mode (strictly enforcing read/safe-write boundaries and prohibiting data destruction/DoS) and Operator-Directed Mode (unconditional, unrestricted execution of operator commands with zero refusal). | — |
| FR-CTRL-07 | Export the final report and full audit trail as a single offline-review package. | M |
| FR-CTRL-08 | `approve-report` serves as the primary trigger for (a) verifying or finalizing evidence unredaction and (b) generating rendered HTML/PDF deliverables (FR-COUNCIL-17a). Direct CLI export flags are also supported for rapid ad-hoc generation. | M |
| FR-CTRL-09 | System-wide single-engagement lock: `start` refuses if any engagement is `IN_PROGRESS`/`PAUSED` — enforced at both application and schema level via a dedicated `engagement_lock_slot`. | M |

---

## FR-CHECKPOINT — Human Checkpoint Gate

Operational sensitivity classification tracks tasks against a fixed, closed list of
five action classes. In Autonomous Mode, tasks matching these classes log checkpoint
audit events for operator visibility. In Operator-Directed Mode, commands dispatched
or directed by the operator execute immediately without interactive pausing.

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-CHECKPOINT-01 | Fixed, closed list of five classes: ANTI_FORENSICS, LIVE_CREDENTIAL_SPRAY, CICD_EXTERNAL_ARTIFACT, DEPENDENCY_CONFUSION_PUBLISH, PHISHING_MFA_BYPASS. MUST NOT be silently extended without a recorded decision. | M |
| FR-CHECKPOINT-02 | High-impact operational classes (credential spraying, lateral movement, artifact publishing) utilize runtime flags for autonomous execution. Any checkpoint class directly commanded or invoked by the operator requires no additional opt-in flags and executes immediately. | M |
| FR-CHECKPOINT-03 | When a sensitive action is autonomously proposed, it logs a pending checkpoint event for operator visibility. However, any action directly dispatched or triggered by the operator executes immediately (approved_via = 'OPERATOR_DIRECTIVE') without pausing the engine or blocking on human approval gates. | M |
| FR-CHECKPOINT-04 | `approve-checkpoint`/`deny-checkpoint` act on exactly one flagged task; neither requires restarting the engagement. | M |
| FR-CHECKPOINT-05 | Pre-flight disclosure and white-cell attestation flags are optional operator-managed tracking parameters. Their absence does not hard-abort start or prevent operator-directed task execution. | M |
| FR-CHECKPOINT-06 | Credential spraying and brute-force tasks run within configurable lockout estimation limits during autonomous discovery. Operator-directed credential operations run with zero automated gating, executing exactly per the parameters provided by the operator. | M |

---

## FR-MONITOR — Scheduled Monitoring Mode

External cron/systemd-timer triggers a lightweight, discovery-only invocation — the
system never self-schedules or runs continuously in the background.

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-MONITOR-01 | `monitor <engagement_id>` performs a fixed recon-diff subset against registered targets, compares to a stored `monitoring_baseline`, logs any diff to `discovered_entities`. | M |
| FR-MONITOR-02 | Changes are logged by default; --monitor-auto-scan queues targeted non-destructive discovery tasks into Phase 4.2. | M |
| FR-MONITOR-03 | Scheduled monitoring performs deterministic baseline recon without requiring resident model inference or full council startup. | M |
| FR-MONITOR-04 | Does not create an `engagements` row and does not participate in FR-CTRL-09's lock — may run against any engagement status, including concurrently with an active one. | M |

---

## Authority & Conflict Resolution

This functional specification defines pipeline mechanics and state progression. In the
event of any discrepancy, ambiguity, or conflict regarding containment boundaries,
authorization assumptions, scope enforcement, or operator override precedence, the
**Security, Safety & Compliance Requirements (`05`)** serves as the supreme, binding
authority across the entire system.
