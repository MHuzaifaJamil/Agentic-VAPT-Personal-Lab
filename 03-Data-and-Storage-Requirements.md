# Data & Storage Requirements — Autonomous Agentic VAPT System

Traces to base doc §1.2 (storage geometry) and the SQLite tables named in base §Phase 1
step 3 and §Phase 4. Extends them for **multi-target engagements** (confirmed decision:
a single engagement supports a list of hosts/domains, not one target only).

---

## DR-SCHEMA — SQLite State Store

All tables live in `/home/mhj/.local/share/vapt_agent/state.db` (path kept verbatim
from the base document — it belongs to a different machine than this planning
session's host; see `08-Assumptions-Constraints-Dependencies.md`).

### DR-SCHEMA-01: `engagements` (new — required by multi-target support)

The top-level unit of work; a target list is scoped *within* one engagement, not the
other way around.

| Column | Type | Notes |
|---|---|---|
| `engagement_id` | INTEGER PK | |
| `created_at` | TEXT (ISO8601) | |
| `status` | TEXT | `PENDING` / `IN_PROGRESS` / `PAUSED` / `COMPLETE` / `ABORTED` |
| `phase4_started_at` | TEXT (ISO8601, nullable) | set when Phase 4.2 execution begins |
| `session_budget_hours` | INTEGER | confirmed default: **12** (FR-COUNCIL-11 / NFR-PERF-05) |
| `session_deadline_at` | TEXT (ISO8601, nullable) | `phase4_started_at` + `session_budget_hours`; computed once execution starts |
| `allow_brute_force` | INTEGER (bool) DEFAULT 0 | opt-in flag, FR-TOOL-06a |
| `allow_active_exploitation` | INTEGER (bool) DEFAULT 0 | opt-in flag, FR-TOOL-06a |
| `allow_lateral_movement` | INTEGER (bool) DEFAULT 0 | opt-in flag, FR-TOOL-06a |
| `orchestrator_pid` | INTEGER, nullable | **(new — IAB-SCHEMA-01)** set by `start`/`resume` on launch; cleared on clean exit |
| `orchestrator_pid_started_at` | TEXT (ISO8601), nullable | **(new — IAB-SCHEMA-01)** paired with the PID to detect PID reuse after a crash |
| `control_intent` | TEXT | **(new — IAB-SCHEMA-01)** `NONE` / `PAUSE_REQUESTED` / `ABORT` |
| `control_intent_at` | TEXT (ISO8601), nullable | **(new — IAB-SCHEMA-01)** |
| `engagement_lock_slot` | INTEGER, `GENERATED ALWAYS AS (CASE WHEN status IN ('IN_PROGRESS','PAUSED') THEN 0 END) VIRTUAL` | **(new — resolves critical-analysis finding, FR-CTRL-09)** always `0` while non-terminal, `NULL` otherwise. Paired with `CREATE UNIQUE INDEX one_active_engagement ON engagements(engagement_lock_slot);` — SQLite unique indexes ignore `NULL`, so this enforces **at most one row system-wide** with a non-terminal status, regardless of which one, without blocking unlimited `COMPLETE`/`ABORTED` history rows. A naive `UNIQUE(status) WHERE status IN (...)` would be wrong here — it would only prevent two simultaneous `IN_PROGRESS` rows (or two `PAUSED`), not one of each at once. |
| `notes` | TEXT | free-text operator notes |

### DR-SCHEMA-01a: `engagement_flag_history` (new — required by FR-TOOL-06c)

Every change to the three opt-in flags, whether set at `start` or updated via
`resume`, MUST be recorded here — the flags themselves (on `engagements`) only hold
current state; this table is the audit trail of *when* each changed.

| Column | Type | Notes |
|---|---|---|
| `id` | INTEGER PK | |
| `engagement_id` | INTEGER FK → `engagements` | |
| `flag_name` | TEXT | `allow_brute_force` / `allow_active_exploitation` / `allow_lateral_movement` |
| `old_value` / `new_value` | INTEGER (bool) | |
| `changed_at` | TEXT (ISO8601) | |
| `changed_via` | TEXT | `start` / `resume` |

### DR-SCHEMA-02: `targets`

One row per host/domain within an engagement. Carries the per-target autonomy-loop
counters used by FR-COUNCIL-11's diminishing-returns thresholds.

| Column | Type | Notes |
|---|---|---|
| `target_id` | INTEGER PK | |
| `engagement_id` | INTEGER FK → `engagements` | |
| `host_or_domain` | TEXT | |
| `added_at` | TEXT (ISO8601) | |
| `task_count` | INTEGER DEFAULT 0 | incremented per task executed against this target; capped at **30** (FR-COUNCIL-11a) |
| `consecutive_zero_yield_count` | INTEGER DEFAULT 0 | reset to 0 on any task whose `tool_execution_logs.novel_entities_count > 0`; circuit-breaks at **3** consecutive tasks with `novel_entities_count = 0` (FR-COUNCIL-11a) — **not** based on exit code or non-empty output alone |
| `consecutive_failure_count` | INTEGER DEFAULT 0 | **(new, resolves critical-analysis finding C-27)** reset to 0 on any task whose execution had neither `network_error` nor `timeout_hit` set; circuit-breaks at **3** consecutive tasks with either flag set (FR-COUNCIL-11b) — independent of `consecutive_zero_yield_count`, since a failed request and a successful-but-uninformative one are different conditions |
| `status` | TEXT | `PENDING` / `ACTIVE` / `CAPPED` / `CIRCUIT_BROKEN` / `UNREACHABLE` / `COMPLETE` |

### DR-SCHEMA-03: `scope_rules`

Scope-boundary data consumed by the Strategist and checked by Council Gate 1 (a
deterministic Python pre-check plus `Hermes-3-Llama-3.1-8B` as the semantic layer,
per the C-03 resolution as revised by decision #55) — see base §Phase 4.1. **Not an
authorization/RoE record** — per
explicit decision, this system does not verify authorization; this table only holds the
technical in/out-of-scope pattern data the scope-boundary check operates against.

| Column | Type | Notes |
|---|---|---|
| `rule_id` | INTEGER PK | |
| `engagement_id` | INTEGER FK → `engagements` | |
| `pattern` | TEXT | CIDR, domain, or domain wildcard |
| `rule_type` | TEXT | `allow` / `deny` |
| `notes` | TEXT | |

### DR-SCHEMA-04: `attack_paths`

| Column | Type | Notes |
|---|---|---|
| `path_id` | INTEGER PK | |
| `target_id` | INTEGER FK → `targets` | |
| `hypothesis_text` | TEXT | Strategist's rationale |
| `created_by_model` | TEXT | e.g. `DeepSeek-R1-0528-Qwen3-8B` |
| `created_at` | TEXT (ISO8601) | |
| `status` | TEXT | `PROPOSED` / `GATE1_APPROVED` / `GATE1_REJECTED` |

### DR-SCHEMA-05: `task_queue`

| Column | Type | Notes |
|---|---|---|
| `task_id` | INTEGER PK | |
| `target_id` | INTEGER FK → `targets` | |
| `path_id` | INTEGER FK → `attack_paths`, nullable | null for a follow-on task generated mid-loop (FR-COUNCIL-10) |
| `description` | TEXT | |
| `tool_name` | TEXT, nullable | Tier 1 tool name, or null for Tier 2 |
| `proposed_command` | TEXT | full argument vector as generated |
| `gate2_corrected_command` | TEXT, nullable | if the linter (Gate 2) corrected it |
| `status` | TEXT | `PENDING` / `GATE1_APPROVED` / `GATE1_REJECTED` / `GATE2_BLOCKED` / `EXECUTING` / `EXECUTED` / `FOLLOWUP_GENERATED` |
| `gate1_rationale` | TEXT | Stated reason from whichever Gate 1 tier acted — the deterministic pre-check (`FR-COUNCIL-03a`) or `Hermes-3-Llama-3.1-8B` |
| `gate2_rationale` | TEXT | The deterministic Gate 2 validator's stated reason on block/correct (not an LLM — see `FR-COUNCIL-08`) |
| `created_at` / `executed_at` | TEXT (ISO8601) | |

### DR-SCHEMA-06: `tool_execution_logs`

| Column | Type | Notes |
|---|---|---|
| `log_id` | INTEGER PK | |
| `task_id` | INTEGER FK → `task_queue` | |
| `argument_vector` | TEXT (JSON array) | exact argv, never a shell string (FR-TOOL-04) |
| `resolved_binary_path` | TEXT | absolute path the bridge resolved and allowlist-checked (FR-TOOL-03) |
| `pid` | INTEGER, nullable | **(new — IAB-SCHEMA-02)** the OS PID of the spawned subprocess; `end_ts IS NULL AND pid IS NOT NULL` is how `abort` finds a currently-running subprocess to kill |
| `start_ts` / `end_ts` | TEXT (ISO8601) | |
| `exit_code` | INTEGER, nullable | null if killed on timeout |
| `timeout_hit` | INTEGER (bool) | |
| `raw_output_artifact_id` | INTEGER FK → `artifacts_index` | full unsanitized stdout/stderr (FR-TOOL-08) |
| `sanitized_summary` | TEXT | what actually entered model context (FR-TOOL-07) |
| `suspected_injection_flag` | INTEGER (bool) DEFAULT 0 | set by the heuristic check in FR-TOOL-13 |
| `novel_entities_count` | INTEGER DEFAULT 0 | count of new rows this run inserted into `discovered_entities` (DR-SCHEMA-12); **0 here means this run counts toward the zero-yield circuit breaker (FR-COUNCIL-11a)**, regardless of `exit_code` or whether `sanitized_summary` is non-empty |
| `network_error` | INTEGER (bool) DEFAULT 0 | **(new, resolves critical-analysis finding C-27)** set when the bridge detects the process failed due to a network-level condition (connection refused/reset, DNS resolution failure, TLS handshake failure) rather than completing and simply finding nothing. Feeds `targets.consecutive_failure_count` (FR-COUNCIL-11b) alongside `timeout_hit`. |

### DR-SCHEMA-07: `verified_vulnerabilities`

| Column | Type | Notes |
|---|---|---|
| `finding_id` | INTEGER PK | |
| `target_id` | INTEGER FK → `targets` | |
| `task_id` | INTEGER FK → `task_queue` | originating task |
| `title` | TEXT | |
| `description` | TEXT | |
| `cwe_id` / `cve_id` | TEXT, nullable | |
| `cvss_version` | TEXT | fixed value: `3.1` (confirmed — no other version supported, FR-COUNCIL-16a) |
| `cvss_metrics_json` | TEXT (JSON) | the LLM-proposed per-metric values + justification (FR-COUNCIL-16a) |
| `cvss_vector` / `cvss_score` | TEXT / REAL | **computed by the deterministic calculator, never written by the LLM directly** |
| `status` | TEXT | `CANDIDATE` / `CONFIRMED` / `DISMISSED` |
| `gate3_rationale` | TEXT | Mistral-7B's stated reason |
| `evidence_artifact_ids` | TEXT (JSON array) | FKs into `artifacts_index` |
| `discovered_at` / `confirmed_at` | TEXT (ISO8601) | |

### DR-SCHEMA-08: `model_invocation_logs`

| Column | Type | Notes |
|---|---|---|
| `invocation_id` | INTEGER PK | |
| `engagement_id` | INTEGER FK → `engagements` | |
| `model_name` | TEXT | |
| `role` | TEXT | Strategist / Operator / Gatekeeper / Linter / Adjudicator |
| `phase` / `step_id` | TEXT | e.g. `4.1`, `4.2`, `4.3` |
| `prompt_tokens` / `completion_tokens` | INTEGER | |
| `latency_ms` | INTEGER | |
| `started_at` / `ended_at` | TEXT (ISO8601) | |
| `status` | TEXT | `OK` / `TIMEOUT` / `CRASHED` / `CONTEXT_TRUNCATED` |

### DR-SCHEMA-09: `engagement_phase_log`

Tracks phase transitions for resumability (NFR-REL-02).

| Column | Type | Notes |
|---|---|---|
| `id` | INTEGER PK | |
| `engagement_id` | INTEGER FK → `engagements` | |
| `phase` | TEXT | `0_PREFLIGHT` / `1_ENV` / `2_GATEWAY` / `3_TOOLBRIDGE` / `4.1` / `4.2` / `4.3` / `5_HIBERNATE` |
| `entered_at` / `exited_at` | TEXT (ISO8601), nullable | |
| `outcome` | TEXT | `OK` / `DEGRADED` / `FAILED` |

### DR-SCHEMA-10: `artifacts_index`

| Column | Type | Notes |
|---|---|---|
| `artifact_id` | INTEGER PK | |
| `engagement_id` | INTEGER FK → `engagements` | |
| `target_id` | INTEGER FK → `targets`, nullable | |
| `task_id` | INTEGER FK → `task_queue`, nullable | |
| `file_path` | TEXT | absolute NVMe path |
| `artifact_type` | TEXT | `raw_tool_output` / `report_markdown` / `report_html` / `report_pdf` / `log` |
| `created_at` | TEXT (ISO8601) | |
| `size_bytes` | INTEGER | |

### DR-SCHEMA-11: `reports` (revised, resolves critical-analysis finding C-25)

`12-Report-Formatting-Rules.md` establishes two distinct document types — an
individual VAPT report per `CONFIRMED` finding, and one consolidated informational
register per engagement — which the original version of this table couldn't
represent at all (no `finding_id`, no way to distinguish the two document types).

| Column | Type | Notes |
|---|---|---|
| `report_id` | INTEGER PK | |
| `engagement_id` | INTEGER FK → `engagements` | |
| `document_type` | TEXT | **(new)** `VAPT_FINDING` (one row per `CONFIRMED` finding) or `INFO_REGISTER` (one row per engagement, regenerated in place per `12-Report-Formatting-Rules.md` §9 rather than a new row per item) |
| `finding_id` | INTEGER FK → `verified_vulnerabilities`, nullable | **(new)** set for `VAPT_FINDING` rows; `NULL` for `INFO_REGISTER` |
| `format` | TEXT | `markdown` / `html` / `pdf` |
| `status` | TEXT | `DRAFT_PENDING_APPROVAL` / `BLOCKED_UNGROUNDED` / `APPROVED` / `REJECTED` — **(`BLOCKED_UNGROUNDED` new, resolves critical-analysis finding C-26)** set when the grounding check (FR-COUNCIL-17b) fails after its retry budget; requires operator review, not auto-resolved |
| `file_path` | TEXT | |
| `created_at` / `approved_at` | TEXT (ISO8601), nullable | |
| `approved_by` | TEXT | fixed value: `Muhammad Huzaifa Jamil` once approved (FR-CTRL-08) |

A partial unique index, `CREATE UNIQUE INDEX one_info_register ON reports(engagement_id) WHERE document_type = 'INFO_REGISTER';`,
enforces that an engagement has at most one `INFO_REGISTER` row (per document type,
same generated-column-free technique works here directly since the predicate
doesn't need a shared constant value — `engagement_id` itself is what must be
unique among `INFO_REGISTER` rows).

### DR-SCHEMA-13: `suspended_processes` (new — FR-ENV-05 required this; no table previously existed for it, closed by IAB-SCHEMA-03)

| Column | Type | Notes |
|---|---|---|
| `id` | INTEGER PK | |
| `engagement_id` | INTEGER FK → `engagements` | |
| `pid` | INTEGER | |
| `process_name` | TEXT | |
| `suspended_at` | TEXT (ISO8601) | |
| `resumed_at` | TEXT (ISO8601), nullable | |
| `resume_verified` | INTEGER (bool) DEFAULT 0 | set once FR-ENV-12/FR-HIB-03 confirms the process is alive post-`SIGCONT` |

### DR-SCHEMA-14: `redaction_map` (new — FR-COUNCIL-18 required this; no table previously existed for it, closed by IAB-SCHEMA-04)

| Column | Type | Notes |
|---|---|---|
| `id` | INTEGER PK | |
| `report_id` | INTEGER FK → `reports` | |
| `placeholder_token` | TEXT | unique per report, e.g. `[REDACTED-1]` |
| `source_artifact_id` | INTEGER FK → `artifacts_index` | the raw evidence artifact holding the real value |
| `start_offset` / `end_offset` | INTEGER | **(revised, resolves critical-analysis finding C-21)** exact byte offsets into the raw artifact file, captured at redaction time — never a pattern/regex search, which can match the wrong occurrence if a token repeats or fail under irregular line breaks |
| `content_hash` | TEXT | SHA-256 of the exact byte range `[start_offset, end_offset)`, computed at redaction time |

The real secret value is never duplicated into this table — it is re-read from
`source_artifact_id` at unredaction time, using `start_offset`/`end_offset`. Before
substituting it into the approved report, `approve-report` (FR-CTRL-08) MUST verify
the re-read bytes hash to `content_hash`; a mismatch (artifact truncated or modified
since redaction) MUST fail the approval loudly rather than silently insert a
possibly-wrong value.

### DR-SCHEMA-12: `discovered_entities` (new — required by FR-COUNCIL-11a, resolves critical-analysis finding C-17)

The state-delta ledger that makes "yield" a precise, code-checkable concept instead
of "non-empty output." A tool run's contribution to this table — not its exit code,
not whether its output was non-empty — is what the zero-yield circuit breaker reads.

| Column | Type | Notes |
|---|---|---|
| `id` | INTEGER PK | |
| `target_id` | INTEGER FK → `targets` | |
| `entity_type` | TEXT | `open_port` / `http_route` / `parameter` / `status_anomaly` (extensible) |
| `entity_value` | TEXT | the concrete discovered value (e.g. `443/tcp`, `/api/v2/users`, `debug=1`) |
| `first_seen_task_id` | INTEGER FK → `task_queue` | the task whose run first produced this row |
| `first_seen_at` | TEXT (ISO8601) | |

`(target_id, entity_type, entity_value)` MUST be a **unique constraint**. Inserting a
row for this triple is an `INSERT OR IGNORE` (or equivalent) — the number of rows
actually inserted (not attempted) by a given task's parsing step is exactly its
`tool_execution_logs.novel_entities_count`. A row that already exists for that triple
contributes 0 to `novel_entities_count`, correctly reflecting that the finding wasn't
novel, even if the tool run itself succeeded and returned data.

### DR-SCHEMA-15: `targets` generalized for non-network target types (revised — required by `19-Extended-Capability-Domains.md`)

**Confirmed decision (full schema design, not deferred):** several extended capability
domains (web3/smart-contract auditing, mobile app pentesting, CI/CD & source-code-access
auditing) need a target identity that isn't a host/domain/CIDR at all. Rather than a
parallel table per domain, `targets` (`DR-SCHEMA-02`) gains a discriminator column and
a set of nullable, type-specific columns — a single wide table, consistent with this
schema's existing style, not a fully normalized per-type design (revisit at
implementation time if the column count becomes unwieldy).

| Column | Type | Notes |
|---|---|---|
| `target_type` | TEXT NOT NULL DEFAULT `'NETWORK'` | `NETWORK` (existing host/domain/CIDR — default, fully backward compatible) / `CONTRACT` (web3/meme-coin) / `MOBILE_BINARY` (mobile-pentest) / `CODE_REPO` (CI/CD, diff-review, whitebox-code-recon) |
| `host_or_domain` | TEXT, **now nullable** | unchanged meaning for `NETWORK` rows; NULL for the other three types |
| `chain_id` | TEXT, nullable | `CONTRACT` only — e.g. `1` (Ethereum mainnet), `solana-mainnet`, or a local Anvil/Foundry fork identifier |
| `contract_address` | TEXT, nullable | `CONTRACT` only |
| `contract_abi_path` | TEXT, nullable | `CONTRACT` only — path to a verified ABI/source artifact, if supplied |
| `contract_investigation_mode` | TEXT, nullable | `CONTRACT` only — `CLIENT_OWNED` (a client's own contract, normal VAPT engagement posture) or `PUBLIC_RESEARCH` (public-token due-diligence mode, no client relationship — see `19`'s meme-coin-audit section); both modes kept per operator decision |
| `platform` | TEXT, nullable | `MOBILE_BINARY` only — `ANDROID` / `IOS` |
| `package_name` | TEXT, nullable | `MOBILE_BINARY` only |
| `binary_path` | TEXT, nullable | `MOBILE_BINARY` only — local path to the supplied APK/IPA artifact |
| `binary_hash` | TEXT, nullable | `MOBILE_BINARY` only — SHA-256 of the supplied binary, for provenance |
| `backend_target_id` | INTEGER FK → `targets(target_id)`, nullable | `MOBILE_BINARY` only — once the app's backend API is discovered (per the mobile-pentest methodology: "recover the backend, then test it like any web target"), it is registered as its own `NETWORK`-type row and linked here, rather than inventing a separate mobile-specific network-testing path |
| `repo_url_or_path` | TEXT, nullable | `CODE_REPO` only |
| `repo_ref` | TEXT, nullable | `CODE_REPO` only — branch, commit SHA, or PR number |
| `repo_diff_scope` | TEXT, nullable | `CODE_REPO` only — set for `diff-review`'s PR/commit-scoped mode; NULL for `whitebox-code-recon`'s full-checkout mode |

All existing `FR-COUNCIL-11`/`11a`/`11b` per-target counters (`task_count`,
`consecutive_zero_yield_count`, `consecutive_failure_count`) and `status` apply
identically regardless of `target_type` — the diminishing-returns loop bound is a
property of "a target," not of what kind of target it is.

### DR-SCHEMA-16: `scope_rules` extended with a pattern-kind discriminator (revised)

The existing `pattern`/`rule_type` (allow/deny) columns don't say *how* to match
`pattern` — for `NETWORK` targets this was always inferred (CIDR vs. domain vs.
wildcard). Non-network target types need genuinely different matching semantics, so
this gets an explicit discriminator rather than more inference:

| Column | Type | Notes |
|---|---|---|
| `pattern_kind` | TEXT NOT NULL DEFAULT `'NETWORK'` | `NETWORK` (existing CIDR/domain/wildcard inference, unchanged) / `EXACT_IDENTIFIER` (literal-match allow/deny — a `chain_id:contract_address` pair, a mobile `package_name`, or a `repo_url_or_path`) / `PATH_GLOB` (glob-style path pattern, `CODE_REPO` only — marks in-scope vs. out-of-scope directories *within* an already-in-scope repo, e.g. deny `**/node_modules/**`, `**/vendor/**` — per `whitebox-code-recon`'s finding that vendored/third-party dependency code is a different authorization posture than the client's own code) |

`FR-COUNCIL-03a`'s deterministic pre-check MUST branch on `pattern_kind`: CIDR/regex
matching for `NETWORK`, exact string equality for `EXACT_IDENTIFIER`, glob matching
for `PATH_GLOB`. This is a new code path per kind, not a generalization of the
existing CIDR/regex matcher — treat as a distinct implementation task at Milestone
time, not an incremental tweak to the existing checker.

### DR-SCHEMA-17: `monitoring_baseline` (new — required by `19`'s continuous-monitoring capability, `FR-MONITOR-01`)

Supports the scheduled/cron re-invocation mode (see `13`'s new `IAB-PROC` addendum) —
a lightweight, non-hibernating, discovery-only re-check against a baseline, distinct
from a full Phase 1-5 engagement run.

| Column | Type | Notes |
|---|---|---|
| `id` | INTEGER PK | |
| `target_id` | INTEGER FK → `targets` | |
| `baseline_type` | TEXT | `SUBDOMAIN_SET` / `REPO_COMMIT_HEAD` (extensible) |
| `baseline_value` | TEXT | e.g. a newline-joined sorted subdomain list, or a commit SHA |
| `last_checked_at` | TEXT (ISO8601) | |
| `last_diff_detected_at` | TEXT (ISO8601), nullable | set when a monitor run's value differs from `baseline_value`; NULL if never diffed |

A monitor run that detects a diff updates `baseline_value` to the new state, logs the
diff to `discovered_entities` (`entity_type = 'monitor_diff'`) the same way a live
scan would, and stops there — it does **not** autonomously escalate into active
testing of the new finding without a fresh, explicitly-started engagement (`FR-MONITOR-02`).

### DR-SCHEMA-18: `checkpoint_events` (new — required by the Human Checkpoint Gate, `FR-CHECKPOINT-01..05`)

The audit trail for the new hard-stop mechanism (see `01`'s `FR-CHECKPOINT` section
and the safety-mechanism catalog in `20-Human-Checkpoint-and-Escalation-Safety-Catalog.md`).
Distinct from `engagement_flag_history` (which logs pre-engagement config-time opt-in
flag changes) — this logs live, in-engagement pause/approval events.

| Column | Type | Notes |
|---|---|---|
| `id` | INTEGER PK | |
| `engagement_id` | INTEGER FK → `engagements` | |
| `task_id` | INTEGER FK → `task_queue`, nullable | the specific task that triggered the checkpoint, if applicable |
| `action_class` | TEXT | the specific named action class that triggered the pause — `ANTI_FORENSICS` / `LIVE_CREDENTIAL_SPRAY` / `CICD_EXTERNAL_ARTIFACT` / `DEPENDENCY_CONFUSION_PUBLISH` (fixed, closed list — see `20`) |
| `triggered_at` | TEXT (ISO8601) | |
| `status` | TEXT | `AWAITING_APPROVAL` / `APPROVED` / `DENIED` / `EXPIRED` (an operator may choose to deny rather than approve; unlike the resource-safety timeouts elsewhere in this system, there is no auto-approve-on-timeout — silence means the engagement stays paused) |
| `approved_at` | TEXT (ISO8601), nullable | |
| `approved_via` | TEXT, nullable | records the specific `vaptctl` invocation that approved it (`FR-CHECKPOINT-03`) |
| `rationale_shown_to_operator` | TEXT | the specific, human-readable reason this task was classified into `action_class`, logged verbatim so the approval decision is informed, not a blind rubber-stamp |

---

## DR-CONCURRENCY — Feasibility Check: Is SQLite Adequate?

Base doc §Phase 1 specifies SQLite without discussing concurrency. This deserves a
direct feasibility check rather than an assumption:

- **Write pattern:** because of the single-model-residency policy (FR-GATE-02), model
  invocations are inherently serialized — only one council model is ever producing
  output at a time. Tool subprocess execution can, however, run concurrently with the
  *next* model's output being parsed if the pipeline is built to overlap I/O with
  compute. SQLite's default rollback-journal mode serializes all writers and can block
  a reader during a writer's commit.
- **DR-CONCURRENCY-01:** the database MUST be opened in **WAL (Write-Ahead Logging)
  mode**, not the default rollback-journal mode, so that a long-running write (e.g., a
  large `tool_execution_logs` insert) does not block concurrent read access from a
  status query (FR-CTRL-05) or from a second process (e.g., a CLI `status` invocation
  running while the main engagement loop is active).
- **DR-CONCURRENCY-02:** every discrete state change (task status transition, gate
  decision, finding status) MUST be committed as its own transaction immediately, not
  batched, so that NFR-REL-01's "durable after every discrete step" guarantee actually
  holds — a batching strategy would silently reintroduce the crash-loses-more-than-one-step
  risk NFR-REL-01 is meant to close.
- **DR-CONCURRENCY-03:** **(New, confirmed — resolves critical-analysis finding
  C-20)** WAL mode alone does not prevent `sqlite3.OperationalError: database is
  locked` when two connections attempt to write at close to the same moment (e.g.,
  `pause`/`abort` writing `control_intent` while the orchestrator is mid-commit on a
  large `tool_execution_logs` insert). Every connection MUST also set
  `PRAGMA busy_timeout = 5000;` (5000ms), so a writer retries for up to 5 seconds
  before raising, rather than failing immediately on contention — critical
  specifically for `pause`/`abort`, which must not fail outright at the moment they
  matter most.
- **Conclusion:** SQLite in WAL mode is adequate for this workload's actual
  concurrency profile (low writer contention, occasional concurrent reads); a
  client-server database (Postgres, etc.) would be unjustified complexity for a
  single-host, single-operator tool. This is a **feasible** design choice, not merely
  an inherited one — but only if WAL mode and per-step commits (DR-CONCURRENCY-01/02)
  are actually implemented, which the base document did not specify.

---

## DR-ARTIFACT — Artifact Store Layout

| ID | Requirement |
|----|-------------|
| DR-ARTIFACT-01 | All artifacts MUST live under `/home/mhj/.local/share/vapt_agent/artifacts/`, organized as `artifacts/<engagement_id>/<target_id>/...` so multi-target engagements don't collide with each other's raw output files. |
| DR-ARTIFACT-02 | Raw tool output MUST be written before sanitization/summarization occurs (FR-TOOL-08), named deterministically (e.g. `<task_id>_<tool_name>_<timestamp>.raw`) so `artifacts_index.file_path` never goes stale. |
| DR-ARTIFACT-03 | Report artifacts MUST live under `artifacts/<engagement_id>/reports/pending-approval/` (Markdown, per FR-COUNCIL-17) and, after approval, under `artifacts/<engagement_id>/reports/approved/` (Markdown + HTML + PDF, per FR-COUNCIL-17a) — the pending and approved locations MUST be physically distinct directories, not just a status flag, so an accidental script pointed at "the reports folder" cannot pick up an unapproved draft. |
| DR-ARTIFACT-04 | The intermediate HTML source for every PDF MUST be retained alongside the PDF, never deleted after rendering, per `12-Report-Formatting-Rules.md` §10. |

## DR-RETENTION — Retention & Disk Quota Alignment

| ID | Requirement |
|----|-------------|
| DR-RETENTION-01 | Artifact growth MUST be checked against the thresholds in NFR-RES-04 (85% warn / 95% block of the 185 GB root volume) — this is a data-layer obligation, not just an operational one, since it determines whether a write to `artifacts_index` is even attempted. |
| DR-RETENTION-02 | Raw tool output for `DISMISSED` findings and non-yielding tasks MUST NOT be deleted automatically — it is required for the audit trail (NFR-SEC-04) and for a human to double-check a Gate 3 dismissal. Any future retention/pruning policy is explicitly **out of scope for this planning phase** and MUST be a separate, deliberate decision, not an automatic default. |
| DR-RETENTION-03 | The `state.db` file itself MUST be included in whatever the operator considers the durable record of an engagement — it is not disposable cache, since findings, gate rationale, and CVSS metric justifications live only there (the Markdown/HTML/PDF reports are a *derived* view, not the source of record). |

## DR-BACKUP — Backup

| ID | Requirement |
|----|-------------|
| DR-BACKUP-01 | **(Confirmed: MUST, not SHOULD)** Before Phase 5 hibernation-exit can be considered complete, the system MUST copy `state.db` to a timestamped backup file in the same artifact tree (e.g. `artifacts/<engagement_id>/state_backup_<timestamp>.db`) — this is a mandatory step, not best-effort, so a corrupted live database from an unclean future run does not destroy the only copy of a completed engagement's findings. |
| DR-BACKUP-02 | Backups are local-only (NVMe), consistent with the no-cloud-dependency design (NFR-SEC-02) — no remote/offsite backup is in scope for this planning phase. |
