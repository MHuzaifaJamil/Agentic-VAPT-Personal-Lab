# Implementation Architecture Bridge — Autonomous Agentic VAPT System

**Purpose:** `01`-`12` specify *what* the system must do and *why*. This document
closes the gap to *how it is actually built* — process architecture, language,
concrete file formats, the privileged helper's contract, and a proposed module
layout — so a build-time coding agent isn't left to silently invent foundational
architecture on its own. Still a planning artifact: no code, no installation.

Every decision below was explicitly confirmed by the operator (two rounds of
questions) rather than assumed. See `10-Decision-Log-and-Open-Questions.md` decision
#41 for the record.

---

## IAB-PROC — Process Architecture: Per-Invocation, SQLite/Signal-Coordinated

**Confirmed: no persistent daemon.** `start` runs the Phase 0-5 lifecycle as one
long-lived foreground process (the operator backgrounds it themselves, e.g. `&`,
`nohup`, `tmux` — process supervision beyond that is out of scope). `pause`/`resume`/
`abort`/`status` are short-lived processes that coordinate with the running (or
last-running) orchestrator through **SQLite state plus OS signals**, never a
socket/RPC protocol.

### How each command actually works

| Command | Mechanism |
|---|---|
| `start` | Launches the orchestrator process. It records its own PID and start-time into `engagements.orchestrator_pid`/`orchestrator_pid_started_at` (IAB-SCHEMA-01) before entering Phase 1. |
| `status` | **Read-only.** Queries SQLite directly. Never signals the orchestrator, never needs it to be responsive (OPS-MONITOR-04's "live" requirement is satisfied because every state change is committed immediately per NFR-REL-01, not because status talks to a live process). |
| `pause` | **Cooperative.** Writes `engagements.control_intent = 'PAUSE_REQUESTED'` (IAB-SCHEMA-01), then sends `SIGUSR1` to `orchestrator_pid` purely to prompt an immediate check rather than waiting for the loop's natural per-task polling cadence. The orchestrator's `SIGUSR1` handler does nothing but set an in-memory flag — the actual pause logic runs at the next safe checkpoint (between tasks, never mid-subprocess, per FR-CTRL-02). On pausing, the orchestrator persists all in-flight state, sets `engagements.status = 'PAUSED'`, and **exits the process** — a paused engagement holds no process, consistent with this design's whole memory-efficiency philosophy (no point in a process idling for hours). |
| `resume` | Since "paused" means no process is running, `resume` **launches a fresh orchestrator process** (same entry point as `start`), which detects `status = 'PAUSED'`, applies any updated opt-in flags (FR-TOOL-06c), records its own new PID, and continues the Phase 4.2 loop from the last committed task-queue state — this falls out naturally since all task-queue state already lives in SQLite. |
| `abort` | **Not cooperative — a direct external kill, not a request.** Given the 20-second kill-switch budget (NFR-REL-04) and the possibility that the orchestrator itself is hung (e.g., blocked in a subprocess call or a stuck inference call), `abort` cannot rely on the orchestrator noticing a signal in time. Instead `abort` itself: (1) sets `engagements.status = 'ABORTED'` and `control_intent = 'ABORT'` immediately (atomic, per SEC-KILL-03); (2) queries `tool_execution_logs WHERE end_ts IS NULL` for any currently-running subprocess `pid` (IAB-SCHEMA-02) and sends `SIGTERM` to its **entire process group** (`os.killpg(os.getpgid(pid), signal.SIGTERM)`, not just the recorded PID — every subprocess is spawned with `start_new_session=True` per FR-TOOL-04a specifically so this is possible; resolves finding C-19); (3) sends `SIGTERM` to `orchestrator_pid`; (4) waits a bounded grace period; (5) sends `SIGKILL` (same process-group targeting) to anything still alive (SEC-KILL-02); (6) since the orchestrator process may now be gone, `abort` itself invokes the Phase 5 restoration routine directly (reading `suspended_processes`, IAB-SCHEMA-03, and calling the freezer helper's thaw operation) — `abort` is responsible for satisfying OPS-LIFECYCLE-03's "abort still restores apps" guarantee, not a now-dead orchestrator process. |
| `approve-checkpoint` / `deny-checkpoint` | **Cooperative, same shape as `resume`.** Reaching a checkpoint action class (`FR-CHECKPOINT-03`) makes the orchestrator persist the `checkpoint_events` row, set `engagements.status = 'PAUSED_AWAITING_CHECKPOINT'`, and **exit the process** — same "no process idles waiting" philosophy as `pause`. `approve-checkpoint <id>` marks that row `APPROVED` and launches a fresh orchestrator (same entry point as `resume`), which detects `PAUSED_AWAITING_CHECKPOINT`, executes exactly the one approved task, and continues the Phase 4.2 loop. `deny-checkpoint <id>` marks the row `DENIED`, marks that task `BLOCKED_BY_OPERATOR`, and launches a fresh orchestrator that skips it and continues. |
| `monitor` | **Not part of the `start`/`pause`/`resume`/`abort` engagement lifecycle at all** (`FR-MONITOR-01..04`). A short-lived, deterministic, model-free process: reads an existing `engagement_id`'s registered targets, runs the fixed recon subset, diffs against `monitoring_baseline` (`DR-SCHEMA-17`), writes any diff to `discovered_entities`, and exits — no orchestrator PID, no hibernation, no engagement-lock interaction (`FR-MONITOR-04`). Intended to be invoked by an external cron/systemd-timer entry the operator configures directly; this system never schedules its own recurrence. |

### Signal assignments

| Signal | Meaning |
|---|---|
| `SIGUSR1` | "Check `control_intent` now" — sent by `pause` only, to shorten the wait for the next natural checkpoint. Never used for `abort` (which acts directly, per above). |
| `SIGTERM` | Graceful termination request — sent by `abort` to the orchestrator and to any active tool subprocess **group** (finding C-19). |
| `SIGKILL` | Forceful termination — sent by `abort` to anything that ignored `SIGTERM` within the grace period, per SEC-KILL-02. |

---

## IAB-SCHEMA — Schema Gaps Closed (amendments to `03-Data-and-Storage-Requirements.md`)

Designing the process model above surfaced three concrete gaps in the existing
schema — required for `pause`/`abort`/Phase 5 to function at all, not new features:

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

### IAB-SCHEMA-03: `suspended_processes` (new table — FR-ENV-05 required this, but no table existed for it)

| Column | Type | Notes |
|---|---|---|
| `id` | INTEGER PK | |
| `engagement_id` | INTEGER FK → `engagements` | |
| `pid` | INTEGER | |
| `process_name` | TEXT | |
| `suspended_at` | TEXT (ISO8601) | |
| `resumed_at` | TEXT (ISO8601), nullable | |
| `resume_verified` | INTEGER (bool) DEFAULT 0 | set once FR-ENV-12/FR-HIB-03 confirms the process is alive post-`SIGCONT` |

### IAB-SCHEMA-04: `redaction_map` (new table — FR-COUNCIL-18 required this, but no table existed for it)

| Column | Type | Notes |
|---|---|---|
| `id` | INTEGER PK | |
| `report_id` | INTEGER FK → `reports` | |
| `placeholder_token` | TEXT | unique per report, e.g. `[REDACTED-1]` |
| `source_artifact_id` | INTEGER FK → `artifacts_index` | the raw evidence artifact holding the real value |
| `start_offset` / `end_offset` | INTEGER | **(revised, resolves finding C-21)** exact byte offsets into the raw artifact, captured at redaction time — never a pattern/regex search |
| `content_hash` | TEXT | SHA-256 of the exact byte range; `approve-report` (FR-CTRL-08) MUST verify the re-read bytes still hash to this value before substituting, failing loudly on mismatch |

The real secret value is **never** duplicated into `redaction_map` itself — it's
re-read from `source_artifact_id` at unredaction time, consistent with FR-COUNCIL-18's
"sourced from the raw evidence artifact, never re-derived or approximated."

---

## IAB-LANG — Language & Runtime Baseline

**Confirmed: Python 3.x** for the entire orchestrator/agent codebase — matches every
implementation detail already implied throughout `01`-`12` (`subprocess.Popen`,
argparse-style validators, the `cvss` PyPI package, `sqlite3`). **Not yet verified:**
the exact Python version actually installed on the target machine (per
`08-Assumptions-Constraints-Dependencies.md` AC-ASSUME-04-style caveat) — a
reasonable working baseline is Python 3.11+, but `python3 --version` on the real
target machine should be checked at deployment before this is treated as settled.

---

## IAB-FILES — Confirmed File Formats

### Scope-rules file (passed to `start`, feeds `DR-SCHEMA-03`) — **YAML**

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
hardcoded constants. Format chosen to match the scope-rules file for consistency
(the operator confirmed YAML for scope-rules; this document extends that choice to
the config file as a reasoned inference, not a re-asked decision).

```yaml
# vapt_agent.config.yaml
resource_limits:
  ram_safety_margin_gb: 1.5        # NFR-RES-02
  disk_warn_pct: 85                 # NFR-RES-04
  disk_block_pct: 95                # NFR-RES-04
  e_core_thread_cap: 4              # NFR-RES-05
  model_swap_budget_s: 60           # NFR-PERF-02
  memory_settle_timeout_s: 5        # FR-GATE-10 / IR-ENGINE-06
  sqlite_busy_timeout_ms: 5000       # DR-CONCURRENCY-03, finding C-20
loop_bounds:
  per_target_task_cap: 30           # FR-COUNCIL-11
  zero_yield_circuit_breaker: 3     # FR-COUNCIL-11a
  failure_circuit_breaker: 3        # FR-COUNCIL-11b, finding C-27
  session_budget_hours: 12          # FR-COUNCIL-11 / NFR-PERF-05
gate2:
  correction_attempts: 3            # FR-COUNCIL-09
security:
  kill_switch_timeout_s: 20         # NFR-REL-04
  oom_score_adj: -900               # FR-ENV-11
rate_limits:
  default_category_per_s: 10        # FR-TOOL-14 / IR-BRIDGE-05, finding C-28
  high_risk_category_per_s: 1       # FR-TOOL-14 / IR-BRIDGE-05, finding C-28
cvss:
  version: "3.1"                    # FR-COUNCIL-16a, fixed — not meant to be overridden despite living in config
tool_timeouts_s:
  quick_probes: 180                 # IR-TOOL-03
  targeted_scans: 900
  deep_full_range: 1800
report:
  grounding_max_attempts: 3          # FR-COUNCIL-17b / IR-GROUND-02, finding C-26 — TOTAL attempts (1 initial + 2 retries), not a retry count on top of 3
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
FR-ENV-13's cgroup v2 fallback depends on the caller being able to tell the
difference:

| Exit code | Meaning |
|---|---|
| `0` | Success |
| `13` (EACCES/EPERM class) | Capability/permission unavailable — caller MUST fall back to cgroup v2 (FR-ENV-13) |
| `1` | Target PID not found / already exited |
| `2` | Other/unexpected failure — log and treat as a degraded hibernation step |

The main agent process invokes this via `subprocess.run` under whatever
`setcap`/`sudoers` grant applies to the helper binary itself (SEC-CONTAIN-05) — the
main process never needs (and never has) the capability itself.

---

## IAB-CLI — CLI Framework & Command Surface

**Confirmed: Click.** Proposed top-level command name: `vaptctl` (a naming
convention, trivially renamed; not a deep decision). Command group maps directly to
`FR-CTRL`/`IR-CTRL`:

```
vaptctl start   --targets <list> --scope-rules scope.yaml [--config vapt_agent.config.yaml] \
                 [--mode assess|monitor] \
                 [--allow-brute-force] [--allow-active-exploitation] [--allow-lateral-movement] \
                 [--allow-anti-forensics --white-cell-contact <text> --attest-disclosure] \
                 [--allow-live-credential-spray] [--allow-cicd-external-artifact] \
                 [--allow-dependency-confusion-publish]
vaptctl pause    [--engagement-id <id>]
vaptctl resume   [--engagement-id <id>] [--allow-brute-force] [--allow-active-exploitation] [--allow-lateral-movement]
vaptctl abort    [--engagement-id <id>]
vaptctl status   [--engagement-id <id>] [--json]
vaptctl export   --engagement-id <id> --out <path>
vaptctl approve-report --report-id <id>
vaptctl approve-checkpoint --checkpoint-id <id>
vaptctl deny-checkpoint    --checkpoint-id <id>
vaptctl monitor  --engagement-id <id>
vaptctl dashboard [--rate 1.0] [--db <path>]
```

The four new `--allow-*` flags on `start` (`FR-CHECKPOINT-02`) are deliberately
separate from the three existing high-risk categories (`--allow-brute-force`, etc.)
— they gate the ability to *propose* a checkpoint-class task at all, not the
checkpoint pause itself (`FR-CHECKPOINT-03`'s live approval is a separate, later
step regardless of these flags). `--allow-anti-forensics` additionally requires both
`--white-cell-contact` and `--attest-disclosure` in the same invocation
(`FR-CHECKPOINT-05`) — `start` MUST reject the flag combination otherwise.

---

## IAB-LAYOUT — Proposed Module Layout

```
vapt_agent/
├── cli/                        # Click commands — one module per IR-CTRL action
│   ├── start.py  pause.py  resume.py  abort.py  status.py  export.py  approve_report.py
│   ├── approve_checkpoint.py   # FR-CHECKPOINT-04
│   ├── deny_checkpoint.py      # FR-CHECKPOINT-04
│   ├── monitor.py              # FR-MONITOR-01..04, deliberately outside the engagement lifecycle
│   └── dashboard.py            # 22-VAPT-Monitoring-Dashboard-Specification.md — read-only, independent of the orchestrator lifecycle
├── orchestrator/
│   ├── preflight.py            # FR-PRE (incl. FR-PRE-08 GPU benchmark)
│   ├── hibernation.py          # FR-ENV, calls freezer_helper client
│   ├── phase_lifecycle.py      # OPS-LIFECYCLE state machine, control_intent handling
│   ├── engine_client.py        # Local Engine Client (IR-ENGINE-01..06)
│   └── council/
│       ├── strategist.py       # DeepSeek-R1-0528-Qwen3-8B (FR-COUNCIL-01/02)
│       ├── scope_gate.py       # Tier 0 deterministic + Tier 1 Hermes-3-Llama-3.1-8B (FR-COUNCIL-03a/04-06)
│       ├── operator.py         # Qwen-Coder-7B (FR-COUNCIL-07/09/10)
│       ├── gate2_validator.py  # deterministic Gate 2 (FR-COUNCIL-08/09a)
│       ├── offline_linter.py   # Qwen-Coder-3B-Instruct, offline/between-phase only (FR-COUNCIL-09a)
│       ├── loop_bounds.py      # FR-COUNCIL-11/11a/11b diminishing-returns + failure circuit breaker
│       ├── adjudicator.py      # Mistral-7B Gate 3 (FR-COUNCIL-13/14/14a/15)
│       └── reporter.py         # Ministral-8B-Instruct-2410 report draft + CVSS calculator (FR-COUNCIL-16/16a/17/17a/17b/18) — a distinct model from strategist.py, not a reload of it (decision #55)
├── bridge/
│   ├── tier1/                  # one module per Tier 1 tool schema+wrapper
│   ├── tier2.py                # path-allowlist + denylist + opt-in-flag gate (FR-TOOL-03/06/06a-c)
│   ├── rate_limiter.py         # per-target/per-category spawn-rate limiting (FR-TOOL-14, IR-BRIDGE-05)
│   ├── failure_classifier.py   # network-error/timeout classification feeding FR-COUNCIL-11b (IR-BRIDGE-06)
│   ├── sanitize.py             # IR-SANITIZE provenance tagging + parsing pipeline
│   └── timeouts.py             # IR-TOOL-03 tiered timeout classes
├── security/
│   ├── kill_switch.py          # abort's direct-kill implementation (SEC-KILL)
│   ├── audit.py                # SEC-AUDIT export packaging
│   └── checkpoint_gate.py      # FR-CHECKPOINT-01..05 classifier + pause/approve/deny logic
├── monitor/
│   └── monitor_engine.py       # FR-MONITOR-01..04, invoked by cli/monitor.py; deterministic, no model load
├── domains/                    # 19-Extended-Capability-Domains.md — one module per new target type's scope-check + tool integration
│   ├── contract_scope.py       # EXACT_IDENTIFIER matching for CONTRACT targets (DR-SCHEMA-15/16), web3/meme-coin
│   ├── mobile_scope.py         # MOBILE_BINARY target handling, backend_target_id linkage
│   ├── repo_scope.py           # CODE_REPO target handling, PATH_GLOB matching (diff-review/whitebox-code-recon/CI-CD)
│   └── graphql_bridge.py       # GraphQL-specific Tier 2 tool integration (graphw00f/clairvoyance/graphql-cop/gqlmap)
├── freezer_helper/
│   └── vapt_freezer_helper.py  # separately packaged/installed privileged CLI (FR-ENV-13)
├── data/
│   ├── schema.sql               # DR-SCHEMA-01..18 + IAB-SCHEMA-01..04 DDL, WAL mode pragma
│   ├── db.py
│   └── models.py
├── config/
│   ├── defaults.yaml            # IAB-FILES config defaults
│   └── loader.py
├── reports/
│   ├── markdown_gen.py
│   ├── grounding.py             # deterministic evidence-grounding check (FR-COUNCIL-17b, IR-GROUND-01..03)
│   ├── render.py                # pandoc + wkhtmltopdf/weasyprint invocation (FR-COUNCIL-17a)
│   └── redaction.py             # FR-COUNCIL-18 redact/unredact, reads redaction_map
└── tests/                       # mirrors 09-Acceptance-Criteria-and-Test-Plan.md TP-* groups
```
