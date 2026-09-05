# Implementation Architecture Bridge — Autonomous Agentic VAPT System

**Purpose:** The requirements specifications define *what* the system must do and *why*.
This document bridges those requirements to *how the system is constructed* — process architecture,
language runtime, concrete file formats, the privileged helper contract, IPC semantics, and
the proposed module layout.

This architecture bridges the two execution postures of the Dual-Mode Execution Architecture:
providing structured state serialization, deterministic validation, and graceful pausing for
unattended, non-destructive Autonomous Mode loops, while providing direct, low-latency command
dispatch for Operator-Directed Mode without automated interception or technical gate refusals.

All security invariants, containment boundaries, and override models implemented across these
components derive authoritatively from the Security Specification (`05`).

---

## IAB-PROC — Process Architecture: Per-Invocation, SQLite/Signal-Coordinated

**Confirmed: no persistent daemon.** `start` runs the full engagement lifecycle as one
long-lived foreground process (the operator backgrounds it themselves, e.g. `&`,
`nohup`, `tmux` — process supervision beyond that is out of scope). `pause`/`resume`/
`abort`/`status` are short-lived processes that coordinate with the running (or
last-running) orchestrator through **SQLite state plus OS signals**, never a
socket/RPC protocol.

### How each command actually works

| Command | Mechanism |
|---|---|
| `start` | Launches the orchestrator process. It records its own PID and start-time into `engagements.orchestrator_pid`/`orchestrator_pid_started_at` (IAB-SCHEMA-01) before entering the lifecycle. |
| `status` | **Read-only.** Queries SQLite directly. Never signals the orchestrator, never needs it to be responsive — every state change is committed immediately on write, so a query always reflects live state without needing to talk to a live process. |
| `pause` | **Cooperative.** Writes `engagements.control_intent = 'PAUSE_REQUESTED'` (IAB-SCHEMA-01), then sends `SIGUSR1` to `orchestrator_pid` purely to prompt an immediate check rather than waiting for the loop's natural per-task polling cadence. The orchestrator's `SIGUSR1` handler does nothing but set an in-memory flag — the actual pause logic runs at the next safe checkpoint (between tasks, never mid-subprocess). On pausing, the orchestrator persists all in-flight state, sets `engagements.status = 'PAUSED'`, and **exits the process** — a paused engagement holds no process, consistent with this design's whole memory-efficiency philosophy (no point in a process idling for hours). |
| `resume` | Since "paused" means no process is running, `resume` **launches a fresh orchestrator process** (same entry point as `start`), which detects `status = 'PAUSED'`, applies any updated high-risk-category opt-in flags, records its own new PID, and continues the task-execution loop from the last committed task-queue state — this falls out naturally since all task-queue state already lives in SQLite. |
| `abort` | **Not cooperative — a direct external kill, not a request.** Given the tight kill-switch budget and the possibility that the orchestrator itself is hung (e.g., blocked in a subprocess call or a stuck inference call), `abort` cannot rely on the orchestrator noticing a signal in time. Instead `abort` itself: (1) sets `engagements.status = 'ABORTED'` and `control_intent = 'ABORT'` immediately (atomic); (2) queries `tool_execution_logs WHERE end_ts IS NULL` for any currently-running subprocess `pid` (IAB-SCHEMA-02) and sends `SIGTERM` to its **entire process group** (`os.killpg(os.getpgid(pid), signal.SIGTERM)`, not just the recorded PID — every subprocess is spawned in its own session specifically so this is possible); (3) sends `SIGTERM` to `orchestrator_pid`; (4) waits a bounded grace period; (5) sends `SIGKILL` (same process-group targeting) to anything still alive; (6) since the orchestrator process may now be gone, `abort` itself invokes the restoration routine directly (reading `suspended_processes`, IAB-SCHEMA-03, and calling the freezer helper's thaw operation) — `abort` is responsible for satisfying the "abort still restores apps" guarantee, not a now-dead orchestrator process. |
| `approve-checkpoint` / `deny-checkpoint` | **Cooperative checkpoint resolution.** In Autonomous Mode, an agent-proposed checkpoint action with no threshold exception persists the `checkpoint_events` row (`status = 'AWAITING_APPROVAL'`), sets `engagements.status = 'PAUSED_AWAITING_CHECKPOINT'`, and cleanly exits the process to release resources. `approve-checkpoint <id>` updates the status to `APPROVED` and re-spawns the orchestrator to execute the task. `deny-checkpoint <id>` sets `DENIED`, marks the task `BLOCKED_BY_OPERATOR`, and resumes the queue. **Exception:** Direct operator directives or console dispatches execute immediately (`status = 'APPROVED'`, `approved_via = 'OPERATOR_DIRECTIVE'`) without entering `PAUSED_AWAITING_CHECKPOINT` or exiting the process. |
| `monitor` | **Not part of the `start`/`pause`/`resume`/`abort` engagement lifecycle at all.** A short-lived, deterministic, model-free process: reads an existing `engagement_id`'s registered targets, runs the fixed recon subset, diffs against `monitoring_baseline`, writes any diff to `discovered_entities`, and exits — no orchestrator PID, no hibernation, no engagement-lock interaction. Intended to be invoked by an external cron/systemd-timer entry the operator configures directly; this system never schedules its own recurrence. |

### Signal assignments

| Signal | Meaning |
|---|---|
| `SIGUSR1` | "Check `control_intent` now" — sent by `pause` only, to shorten the wait for the next natural checkpoint. Never used for `abort` (which acts directly, per above). |
| `SIGTERM` | Graceful termination request — sent by `abort` to the orchestrator and to any active tool subprocess **group**. |
| `SIGKILL` | Forceful termination — sent by `abort` to anything that ignored `SIGTERM` within the grace period. |

---

## IAB-SCHEMA — Schema Gaps Closed

Designing the process model above surfaced three concrete gaps in the existing
schema — required for `pause`/`abort`/restoration to function at all, not new features:

### IAB-SCHEMA-01: `engagements` — new columns

| Column | Type | Notes |
|---|---|---|
| `orchestrator_pid` | INTEGER, nullable | set by `start`/`resume` on launch; cleared on clean exit |
| `orchestrator_pid_started_at` | TEXT (ISO8601), nullable | paired with the PID to detect PID reuse by an unrelated process after a crash |
| `control_intent` | TEXT | `NONE` / `PAUSE_REQUESTED` / `ABORT` |
| `control_intent_at` | TEXT (ISO8601), nullable | |

### IAB-SCHEMA-02: `tool_execution_logs` — new column

| Column | Type | Notes |
|---|---|---|
| `pid` | INTEGER, nullable | the OS PID of the spawned subprocess; `end_ts IS NULL AND pid IS NOT NULL` is how `abort` finds a currently-running subprocess to kill |

### IAB-SCHEMA-03: `suspended_processes` (new table, required for hibernation/restoration bookkeeping)

| Column | Type | Notes |
|---|---|---|
| `id` | INTEGER PK | |
| `engagement_id` | INTEGER FK → `engagements` | |
| `pid` | INTEGER | |
| `process_name` | TEXT | |
| `suspended_at` | TEXT (ISO8601) | |
| `resumed_at` | TEXT (ISO8601), nullable | |
| `resume_verified` | INTEGER (bool) DEFAULT 0 | set once liveness is confirmed post-`SIGCONT` |

### IAB-SCHEMA-04: `redaction_map` (new table, required for report redaction/unredaction)

| Column | Type | Notes |
|---|---|---|
| `id` | INTEGER PK | |
| `report_id` | INTEGER FK → `reports` | |
| `placeholder_token` | TEXT | unique per report, e.g. `[REDACTED-1]` |
| `source_artifact_id` | INTEGER FK → `artifacts_index` | the raw evidence artifact holding the real value |
| `start_offset` / `end_offset` | INTEGER | Exact byte offsets into the raw artifact, captured at redaction time — never a pattern/regex search |
| `content_hash` | TEXT | SHA-256 of the exact byte range; report approval MUST verify the re-read bytes still hash to this value before substituting, failing loudly on mismatch |

The real secret value is **never** duplicated into `redaction_map` itself — it's
re-read from `source_artifact_id` at unredaction time, sourced from the raw evidence
artifact, never re-derived or approximated.

---

## IAB-LANG — Language & Runtime Baseline

**Confirmed: Python 3.x** for the entire orchestrator/agent codebase — matches every
implementation detail already implied throughout the requirements set
(`subprocess.Popen`, argparse-style validators, the `cvss` PyPI package, `sqlite3`).
**Not yet verified:** the exact Python version actually installed on the target
machine — a reasonable working baseline is Python 3.11+, but `python3 --version` on
the real target machine should be checked at deployment before this is treated as
settled.

---

## IAB-FILES — Confirmed File Formats

### Scope-rules file (passed to `start`) — **YAML**

```yaml
# scope.yaml
allow:
  - "203.0.113.0/24"
  - "*.example-target.com"
deny:
  - "203.0.113.5"          # carve-out inside an otherwise-allowed range
  - "internal.example-target.com"
```

Each list entry becomes one `scope_rules` row (`pattern`, `rule_type` = `allow`/`deny`).

### Config file (thresholds) — **YAML**, confirmed as defaults-with-override, not
hardcoded constants. Format chosen to match the scope-rules file for consistency.

```yaml
# vapt_agent.config.yaml
resource_limits:
  ram_safety_margin_gb: 1.5        # minimum free-RAM safety margin
  disk_warn_pct: 85                 # disk-usage warning threshold
  disk_block_pct: 95                 # disk-usage hard-stop threshold
  e_core_thread_cap: 4              # efficiency-core allocation cap
  model_swap_budget_s: 60           # max time budgeted for a model load/unload cycle
  memory_settle_timeout_s: 5        # max wait for freed memory to be reflected before proceeding
  sqlite_busy_timeout_ms: 5000       # SQLite busy-retry window under write contention
loop_bounds:
  per_target_task_cap: 30           # per-target task-queue ceiling
  zero_yield_circuit_breaker: 3     # consecutive zero-yield tasks before auto-pivot
  failure_circuit_breaker: 3        # consecutive network-error/timeout runs before marking a target unreachable
  session_budget_hours: 12          # global session time budget
gate2:
  correction_attempts: 3            # max regenerate-and-retry attempts before a task is blocked
security:
  kill_switch_timeout_s: 20         # abort's full-teardown time budget
  oom_score_adj: -900               # OOM-kill priority applied to suspended processes
rate_limits:
  default_category_per_s: 10        # default-category per-target invocation rate limit
  high_risk_category_per_s: 1       # high-risk-category per-target invocation rate limit
cvss:
  version: "3.1"                    # fixed — not meant to be overridden despite living in config
tool_timeouts_s:
  quick_probes: 180
  targeted_scans: 900
  deep_full_range: 1800
report:
  grounding_max_attempts: 3          # TOTAL attempts (1 initial + 2 retries) for the report-grounding check, not a retry count on top of 3
```

Every value above is a **default** matching the confirmed decision — the file's
existence lets the operator override without touching source, but shipping without
this file should fall back to exactly these numbers, not fail to start.

---

## IAB-HELPER — Privileged Helper Contract (`vapt-freezer-helper`)

**Confirmed: one-shot subprocess call per operation** (no persistent helper process,
no IPC protocol to design/secure). The helper is a minimal, separately-packaged CLI:

```
vapt-freezer-helper freeze   --pid <PID> --oom-score -900
vapt-freezer-helper thaw     --pid <PID>
vapt-freezer-helper reclaim  --pid <PID>                 # process_madvise(MADV_PAGEOUT)
vapt-freezer-helper reclaim  --pid <PID> --fallback cgroup
```

Exit codes MUST distinguish "capability unavailable" from other failures, since
the cgroup v2 fallback path depends on the caller being able to tell the
difference:

| Exit code | Meaning |
|---|---|
| `0` | Success |
| `13` (EACCES/EPERM class) | Capability/permission unavailable — caller MUST fall back to cgroup v2 |
| `1` | Target PID not found / already exited |
| `2` | Other/unexpected failure — log and treat as a degraded hibernation step |

The main agent process invokes this via `subprocess.run` under whatever
`setcap`/`sudoers` grant applies to the helper binary itself — the
main process never needs (and never has) the capability itself.

---

## IAB-CLI — CLI Framework & Command Surface

**Confirmed: Click**, top-level command `vaptctl`. This section is the **sole owner
of CLI syntax**:

| ID | Requirement |
|----|-------------|
| IR-CTRL-01 | The CLI exposes exactly one subcommand per control-surface action, each scriptable and non-interactive-friendly (no action *requires* an interactive prompt). |
| IR-CTRL-03 | `start` requires a target list + scope-rules file, plus the optional flags below; MUST NOT accept an authorization/RoE artifact; MUST check the single-engagement lock first. |
| IR-CTRL-04 | `abort` is a single command with no required argument beyond an optional `engagement_id` — fast to invoke under the kill-switch time budget. |
| IR-CTRL-05 | `resume` accepts the same optional flags as `start`; omitting one leaves its current value unchanged (never resets to disabled). |

```
vaptctl start   --targets <list> --scope-rules scope.yaml [--config vapt_agent.config.yaml] \
                 [--assessment-mode initial|retest] \
                 [--max-target-tasks 30] [--spray-zero-yield-limit 15] \
                 [--allow-brute-force] [--allow-active-exploitation] [--allow-lateral-movement] \
                 [--allow-anti-forensics --white-cell-contact <text> --attest-disclosure] \
                 [--allow-live-credential-spray] [--max-auto-lockout-threshold <percent>] \
                 [--allow-cicd-external-artifact] \
                 [--allow-dependency-confusion-publish] [--allow-phishing-mfa-bypass]
vaptctl pause    [--engagement-id <id>]
vaptctl resume   [--engagement-id <id>] [--allow-brute-force] [--allow-active-exploitation] [--allow-lateral-movement] \
                 [--max-auto-lockout-threshold <percent>]
vaptctl abort    [--engagement-id <id>]
vaptctl status   [--engagement-id <id>] [--json]
vaptctl export   --engagement-id <id> --out <path>
vaptctl approve-report --report-id <id>
vaptctl approve-checkpoint --checkpoint-id <id>
vaptctl deny-checkpoint    --checkpoint-id <id>
vaptctl monitor  --engagement-id <id>
vaptctl dashboard [--rate 1.0] [--db <path>]
vaptctl console   [--engagement-id <id>] [--tail-lines <int>] [--no-stream]
```

Operational notes on CLI flags and execution posture: The `--allow-*` flags configure autonomous
discovery boundaries and tracking parameters. In Autonomous Mode, sensitive action proposals
log structured checkpoint events for operator review, and live sprays evaluate against the
`--max-auto-lockout-threshold` (default `5.0%`). In Operator-Directed Mode, commands, scripts,
or actions explicitly dispatched or invoked by the operator execute immediately with zero
refusal and zero automated gate stalls (`approved_via = 'OPERATOR_DIRECTIVE'`); pre-flight
attestation parameters (`--white-cell-contact`, `--attest-disclosure`) are optional tracking fields
whose absence does not hard-abort runtime execution.

---

## IAB-LAYOUT — Proposed Module Layout

```
vapt_agent/
├── cli/                        # Click commands — one module per CLI action
│   ├── start.py  pause.py  resume.py  abort.py  status.py  export.py  approve_report.py
│   ├── approve_checkpoint.py   # marks a checkpoint row approved, resumes the one task
│   ├── deny_checkpoint.py      # marks a checkpoint row denied, skips the one task
│   ├── monitor.py              # discovery-only diff run, outside the engagement lifecycle
│   ├── dashboard.py            # live terminal dashboard — read-only, independent of the orchestrator lifecycle
│   └── console.py              # interactive TUI console — read-write (operator_command_queue), also independent of the orchestrator lifecycle
├── orchestrator/
│   ├── preflight.py            # pre-flight self-test, including the one-time GPU-offload benchmark
│   ├── hibernation.py          # environment/hibernation prep, calls freezer_helper client
│   ├── phase_lifecycle.py      # engagement-lifecycle state machine, control_intent handling
│   ├── engine_client.py        # Local Engine Client abstraction over the inference backend
│   └── council/
│       ├── strategist.py       # scope/task-queue planning model
│       ├── scope_gate.py       # deterministic Tier 0 scope check (every task) + contextual Tier 1 sanity-check (non-manual-origin tasks only)
│       ├── operator.py         # tool-invocation planning model, per-task follow-on queuing
│       ├── gate2_validator.py  # deterministic tool-call validator, incl. duplicate-command hash check
│       ├── dedup.py            # command-hash canonicalization, historical-context queries, regression seeding
│       ├── offline_linter.py   # multi-line script syntax checker, offline/between-phase only
│       ├── loop_bounds.py      # task-cap/zero-yield/failure circuit-breaker enforcement
│       ├── adjudicator.py      # independent evidence-adjudication model
│       └── reporter.py         # report-draft generation + CVSS calculator — a distinct model from strategist.py, not a reload of it
├── bridge/
│   ├── tier1/                  # one module per Tier 1 tool schema+wrapper
│   │   └── tools/script_runner.py  # sandboxed-workspace script execution, gated on a passing offline-lint result
│   ├── tier2.py                # path-allowlist + denylist + opt-in-flag gate
│   ├── rate_limiter.py         # per-target/per-category spawn-rate limiting
│   ├── failure_classifier.py   # network-error/timeout classification feeding the failure circuit breaker
│   ├── sanitize.py             # provenance-tagging + output-parsing pipeline
│   └── timeouts.py             # tiered subprocess timeout classes
├── security/
│   ├── kill_switch.py          # abort's direct-kill implementation
│   ├── audit.py                # audit-trail export packaging
│   └── checkpoint_gate.py      # checkpoint-class classifier + pause/approve/deny logic
├── monitor/
│   └── monitor_engine.py       # discovery-only diff engine, invoked by cli/monitor.py; deterministic, no model load
├── domains/                    # one module per extended-capability target type's scope-check + tool integration
│   ├── contract_scope.py       # exact-identifier matching for smart-contract/on-chain targets
│   ├── mobile_scope.py         # mobile-binary target handling, backend-target linkage
│   ├── repo_scope.py           # source-repository target handling, path-glob matching
│   └── graphql_bridge.py       # GraphQL-specific Tier 2 tool integration
├── freezer_helper/
│   └── vapt_freezer_helper.py  # separately packaged/installed privileged CLI
├── data/
│   ├── schema.sql               # full schema DDL, WAL mode pragma
│   ├── db.py
│   └── models.py
├── config/
│   ├── defaults.yaml            # config defaults
│   └── loader.py
├── reports/
│   ├── markdown_gen.py
│   ├── grounding.py             # deterministic evidence-grounding check
│   ├── render.py                # pandoc + wkhtmltopdf/weasyprint invocation
│   └── redaction.py             # redact/unredact, reads redaction_map
└── tests/                       # mirrors the acceptance test plan's structure
```

Each `council/` module above MUST fetch its unconsumed `operator_command_queue` rows
before invocation — a change to all six existing modules, not just new code
introduced by the interactive-console capability itself.

---

## Authority & Conflict Resolution

This implementation bridge establishes the process model, filesystem layouts, IPC protocols,
and CLI contracts. In the event of any discrepancy, ambiguity, or conflict between
implementation mechanics, module interfaces, and system governance mandates, the
**Security, Safety & Compliance Requirements (`05`)** serves as the final and supreme authority
across the entire system.
