# Data & Storage Requirements — Autonomous Agentic VAPT System

All state, task queues, audit trails, and discovery ledgers persist locally in
`/home/mhj/.local/share/vapt_agent/state.db`. This specification defines the relational
schema, disk layouts, concurrency semantics, and evidence retention policies supporting
multi-target engagements under the Dual-Mode Execution Architecture.

In Autonomous Mode, the data store tracks non-destructive boundaries, task diminishing-returns
counters, and candidate triage states. In Operator-Directed Mode, the schema records immediate
operator command dispatches, overrides, and unhindered execution logs. Verifying legal/contractual
authorization is externalized entirely to the operator; all data remains strictly local.

---

## DR-SCHEMA — SQLite State Store

### DR-SCHEMA-01: `engagements`

| Column | Type | Notes |
|---|---|---|
| `engagement_id` | INTEGER PK | |
| `created_at` | TEXT (ISO8601) | |
| `status` | TEXT | `PENDING` / `IN_PROGRESS` / `PAUSED` / `COMPLETE` / `ABORTED` |
| `phase4_started_at` | TEXT (ISO8601, nullable) | set when Phase 4.2 begins |
| `session_budget_hours` | INTEGER | default **12**, the fixed global session budget |
| `session_deadline_at` | TEXT (ISO8601, nullable) | `phase4_started_at` + `session_budget_hours` |
| `allow_brute_force` / `allow_active_exploitation` / `allow_lateral_movement` | INTEGER (bool) DEFAULT 0 | opt-in flags for the three high-risk task categories |
| `max_auto_lockout_threshold` | REAL NOT NULL DEFAULT `5.0` | live-credential-spray checkpoint auto-approval threshold only; updatable at `resume`; value at evaluation time is captured per-event on `checkpoint_events`, not here |
| `orchestrator_pid` / `orchestrator_pid_started_at` | INTEGER / TEXT (ISO8601), nullable | set by `start`/`resume`; paired to detect PID reuse after a crash |
| `control_intent` | TEXT | `NONE` / `PAUSE_REQUESTED` / `ABORT` |
| `control_intent_at` | TEXT (ISO8601), nullable | |
| `engagement_lock_slot` | INTEGER, `GENERATED ALWAYS AS (CASE WHEN status IN ('IN_PROGRESS','PAUSED') THEN 0 END) VIRTUAL` | `0` while non-terminal, `NULL` otherwise; paired with `CREATE UNIQUE INDEX one_active_engagement ON engagements(engagement_lock_slot)` — SQLite ignores `NULL` in unique indexes, so this enforces **at most one non-terminal row system-wide**, while allowing unlimited `COMPLETE`/`ABORTED` history rows. |
| `notes` | TEXT | |
| `assessment_mode` | TEXT NOT NULL DEFAULT `'INITIAL'`, CHECK (`IN ('INITIAL','RETEST')`) | `RETEST` seeds regression-verification of prior `CONFIRMED` findings before fresh exploration |

### DR-SCHEMA-01a: `engagement_flag_history`

| Column | Type | Notes |
|---|---|---|
| `id` | INTEGER PK | |
| `engagement_id` | INTEGER FK → `engagements` | |
| `flag_name` | TEXT | one of the three opt-in flags |
| `old_value` / `new_value` | INTEGER (bool) | |
| `changed_at` | TEXT (ISO8601) | |
| `changed_via` | TEXT | `start` / `resume` |

### DR-SCHEMA-02: `targets`

One row per host/domain; carries the per-target diminishing-returns counters.

| Column | Type | Notes |
|---|---|---|
| `target_id` | INTEGER PK | |
| `engagement_id` | INTEGER FK → `engagements` | |
| `host_or_domain` | TEXT | |
| `added_at` | TEXT (ISO8601) | |
| `task_count` | INTEGER DEFAULT 0 | capped at a configurable value, default 30, **hard ceiling 100** (`--max-target-tasks`) |
| `consecutive_zero_yield_count` | INTEGER DEFAULT 0 | `STANDARD`-class only; resets on `novel_entities_count > 0`; **non-disableable** breaker at 3 |
| `consecutive_zero_yield_count_high_attempt` | INTEGER DEFAULT 0 | `HIGH_ATTEMPT`-class (brute-force/fuzzing) tracked independently; **non-disableable** breaker, default 15 (`--spray-zero-yield-limit`) |
| `consecutive_failure_count` | INTEGER DEFAULT 0 | resets when neither `network_error` nor `timeout_hit` set; breaker at 3, independent of the yield counters |
| `status` | TEXT | `PENDING` / `ACTIVE` / `CAPPED` / `CIRCUIT_BROKEN` / `UNREACHABLE` / `COMPLETE` |

### DR-SCHEMA-03: `scope_rules`

Technical in/out-of-scope pattern data only — **not an authorization/RoE record**.

| Column | Type | Notes |
|---|---|---|
| `rule_id` | INTEGER PK | |
| `engagement_id` | INTEGER FK → `engagements` | |
| `pattern` | TEXT | CIDR, domain, or wildcard. Matching is **strict DNS-suffix/hierarchy anchoring**, never keyword matching — `aws.abc.com` is in-scope under `abc.com`, `abc.com.attacker.com` is not. |
| `rule_type` | TEXT | `allow` / `deny` |
| `notes` | TEXT | |

### DR-SCHEMA-04: `attack_paths`

| Column | Type | Notes |
|---|---|---|
| `path_id` | INTEGER PK | |
| `target_id` | INTEGER FK → `targets` | |
| `hypothesis_text` | TEXT | Strategist's rationale |
| `created_by_model` | TEXT | |
| `created_at` | TEXT (ISO8601) | |
| `status` | TEXT | `PROPOSED` / `GATE1_APPROVED` / `GATE1_REJECTED` |

### DR-SCHEMA-05: `task_queue`

| Column | Type | Notes |
|---|---|---|
| `task_id` | INTEGER PK | |
| `target_id` | INTEGER FK → `targets` | |
| `path_id` | INTEGER FK → `attack_paths`, nullable | null for a follow-on task |
| `description` | TEXT | |
| `tool_name` | TEXT, nullable | Tier 1 name, or null for Tier 2 |
| `proposed_command` | TEXT | full argv as generated |
| `gate2_corrected_command` | TEXT, nullable | | 
| `status` | TEXT | `PENDING` / `GATE1_APPROVED` / `GATE1_REJECTED` / `GATE2_BLOCKED` / `EXECUTING` / `EXECUTED` / `FOLLOWUP_GENERATED` |
| `gate1_rationale` | TEXT | Reason from whichever tier acted; for MANUAL_OPERATOR records direct operator dispatch with automated scope gates bypassed. |
| `gate2_rationale` | TEXT | Gate 2's stated reason (deterministic, not an LLM) |
| `origin` | TEXT NOT NULL DEFAULT `'AUTONOMOUS_COUNCIL'`, CHECK (`IN ('AUTONOMOUS_COUNCIL','MANUAL_OPERATOR','HISTORICAL_REGRESSION')`) | MANUAL_OPERATOR dispatches directly to Phase 4.2, bypassing Gate 1 Tier 0 and Tier 1 automated scope checks. HISTORICAL_REGRESSION follows standard non-destructive autonomous rules unless re-dispatched directly by the operator. |
| `source_command_id` | INTEGER FK → `operator_command_queue(command_id)`, nullable | set only when the operator's own text explicitly and specifically named the action |
| `source_finding_id` | INTEGER FK → `verified_vulnerabilities(finding_id)`, nullable | set only when `origin = 'HISTORICAL_REGRESSION'` |
| `created_at` / `executed_at` | TEXT (ISO8601) | |

### DR-SCHEMA-06: `tool_execution_logs`

| Column | Type | Notes |
|---|---|---|
| `log_id` | INTEGER PK | |
| `task_id` | INTEGER FK → `task_queue` | |
| `argument_vector` | TEXT (JSON array) | exact argv, never a shell string |
| `resolved_binary_path` | TEXT | allowlist-checked absolute path |
| `pid` | INTEGER, nullable | `end_ts IS NULL AND pid IS NOT NULL` is how `abort` finds a running subprocess |
| `start_ts` / `end_ts` | TEXT (ISO8601) | |
| `exit_code` | INTEGER, nullable | null if killed on timeout |
| `timeout_hit` | INTEGER (bool) | |
| `raw_output_artifact_id` | INTEGER FK → `artifacts_index` | |
| `sanitized_summary` | TEXT | what entered model context |
| `suspected_injection_flag` | INTEGER (bool) DEFAULT 0 | |
| `novel_entities_count` | INTEGER DEFAULT 0 | new `discovered_entities` rows this run; **0 counts toward the zero-yield breaker** regardless of exit code/non-empty output |
| `network_error` | INTEGER (bool) DEFAULT 0 | connection-level failure, distinct from a clean exit finding nothing; feeds `consecutive_failure_count` with `timeout_hit` |
| `command_hash` | TEXT | pair-aware canonical SHA256 of binary + flag/value pairs (grouped before sorting — a flat sort would falsely dedup `-p 80 -oN 443` vs `-p 443 -oN 80`); feeds Gate 2's `DUPLICATE_COMMAND` check |
| `yield_class` | TEXT NOT NULL DEFAULT `'STANDARD'`, CHECK (`IN ('STANDARD','HIGH_ATTEMPT')`) | `HIGH_ATTEMPT` for brute-force/fuzzing tools; set from the static tool schema, not the model |

### DR-SCHEMA-07: `verified_vulnerabilities`

| Column | Type | Notes |
|---|---|---|
| `finding_id` | INTEGER PK | |
| `target_id` | INTEGER FK → `targets` | |
| `task_id` | INTEGER FK → `task_queue` | |
| `title` / `description` | TEXT | |
| `cwe_id` / `cve_id` | TEXT, nullable | |
| `cvss_version` | TEXT | fixed `3.1` |
| `cvss_metrics_json` | TEXT (JSON) | LLM-proposed per-metric values + justification |
| `cvss_vector` / `cvss_score` | TEXT / REAL | computed by the deterministic calculator only |
| `status` | TEXT | `CANDIDATE` / `CONFIRMED` / `DISMISSED` / `REMEDIATED` (reachable only from `finding_origin = 'REGRESSION_CHECK'`) |
| `gate3_rationale` | TEXT | |
| `evidence_artifact_ids` | TEXT (JSON array) | |
| `target_endpoint` / `affected_parameter` | TEXT, nullable | structured fields feeding `finding_fingerprint` |
| `finding_fingerprint` | TEXT | `SHA256(cwe_id \|\| target_endpoint \|\| affected_parameter)`, computed non-LLM at Gate 3 confirmation. Indexed alone (not composite with `target_id`, which is engagement-scoped) — cross-engagement queries join via `targets.host_or_domain`. |
| `finding_origin` | TEXT NOT NULL DEFAULT `'NEW'`, CHECK (`IN ('NEW','REGRESSION_CHECK')`) | governs report routing |
| `retests_finding_id` | INTEGER FK → `verified_vulnerabilities(finding_id)`, nullable | set only when `finding_origin = 'REGRESSION_CHECK'` |
| `discovered_at` / `confirmed_at` | TEXT (ISO8601) | |

### DR-SCHEMA-08: `model_invocation_logs`

| Column | Type | Notes |
|---|---|---|
| `invocation_id` | INTEGER PK | |
| `engagement_id` | INTEGER FK → `engagements` | |
| `model_name` | TEXT | |
| `role` | TEXT | `Strategist` / `Operator` / `Gatekeeper` / `Linter` / `Adjudicator` / `Reporter` |
| `phase` / `step_id` | TEXT | |
| `turn_number` | INTEGER DEFAULT 0 | monotonic per `(engagement_id, role)`, `COALESCE(MAX(turn_number),0)+1` |
| `prompt_tokens` / `completion_tokens` | INTEGER | |
| `latency_ms` | INTEGER | |
| `started_at` / `ended_at` | TEXT (ISO8601) | an unfinalized row (`ended_at IS NULL`) is written at invocation start — this is how a read-only observer distinguishes "generating" from "finished" without a new table |
| `status` | TEXT | `OK` / `TIMEOUT` / `CRASHED` / `CONTEXT_TRUNCATED` |

### DR-SCHEMA-09: `engagement_phase_log`

Tracks phase transitions for resumability.

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
| `target_id` / `task_id` | INTEGER FK, nullable | |
| `file_path` | TEXT | absolute NVMe path |
| `artifact_type` | TEXT | `raw_tool_output` / `report_markdown` / `report_html` / `report_pdf` / `log` |
| `created_at` / `size_bytes` | TEXT (ISO8601) / INTEGER | |

### DR-SCHEMA-11: `reports`

Distinguishes the two report document types.

| Column | Type | Notes |
|---|---|---|
| `report_id` | INTEGER PK | |
| `engagement_id` | INTEGER FK → `engagements` | |
| `document_type` | TEXT | `VAPT_FINDING` (one per `CONFIRMED` finding) or `INFO_REGISTER` (one per engagement, regenerated in place) |
| `finding_id` | INTEGER FK → `verified_vulnerabilities`, nullable | set for `VAPT_FINDING` only |
| `format` | TEXT | `markdown` / `html` / `pdf` |
| `status` | TEXT | `DRAFT_PENDING_APPROVAL` / `BLOCKED_UNGROUNDED` / `APPROVED` / `REJECTED` — `BLOCKED_UNGROUNDED` set when the grounding check exhausts retries; **requires operator review, not auto-resolved** |
| `file_path` | TEXT | |
| `created_at` / `approved_at` | TEXT (ISO8601), nullable | |
| `approved_by` | TEXT | Dynamically populated from active runtime configuration (operator_identity), never a hardcoded schema constant |

`CREATE UNIQUE INDEX one_info_register ON reports(engagement_id) WHERE document_type = 'INFO_REGISTER';` — at most one `INFO_REGISTER` row per engagement.

### DR-SCHEMA-12: `discovered_entities`

The state-delta ledger that makes "yield" precise instead of "non-empty output."

| Column | Type | Notes |
|---|---|---|
| `id` | INTEGER PK | |
| `target_id` | INTEGER FK → `targets` | |
| `entity_type` | TEXT | `open_port` / `http_route` / `parameter` / `status_anomaly` (extensible) |
| `entity_value` | TEXT | e.g. `443/tcp`, `/api/v2/users` |
| `first_seen_task_id` | INTEGER FK → `task_queue` | |
| `first_seen_at` | TEXT (ISO8601) | |

`(target_id, entity_type, entity_value)` is a **unique constraint**; `INSERT OR IGNORE`. Rows actually inserted by a task = its `novel_entities_count`.

### DR-SCHEMA-13: `suspended_processes`

| Column | Type | Notes |
|---|---|---|
| `id` | INTEGER PK | |
| `engagement_id` | INTEGER FK → `engagements` | |
| `pid` / `process_name` | INTEGER / TEXT | |
| `suspended_at` / `resumed_at` | TEXT (ISO8601), latter nullable | |
| `resume_verified` | INTEGER (bool) DEFAULT 0 | set once liveness is confirmed post-`SIGCONT` |

### DR-SCHEMA-14: `redaction_map`

| Column | Type | Notes |
| --- | --- | --- |
| `id` | INTEGER PK | Primary key identifier |
| `report_id` | INTEGER FK → `reports` | Associated report draft identifier |
| `placeholder_token` | TEXT | Unique identifier per report, e.g. `[REDACTED-1]` |
| `source_artifact_id` | INTEGER FK → `artifacts_index` | Link to raw evidentiary output |
| `start_offset` / `end_offset` | INTEGER | Exact byte offsets tracking secret location within raw evidence |
| `content_hash` | TEXT | SHA-256 digest of slice `[start_offset, end_offset)` |

Raw captured credentials remain securely stored in the local evidence store under `source_artifact_id`. During report generation, `approve-report` restores redacted items into finalized deliverables by validating byte slices against `content_hash`. In Operator-Directed Mode, if offset shifts or formatting variations occur during manual editing, the operator may force unredaction or supply replacement evidence directly without blocking report compilation.

### DR-SCHEMA-15: `targets` — non-network target types

`target_type` discriminator + nullable type-specific columns (a single wide table, not a per-type normalized design).

| Column | Type | Notes |
|---|---|---|
| `target_type` | TEXT NOT NULL DEFAULT `'NETWORK'` | `NETWORK` / `CONTRACT` / `MOBILE_BINARY` / `CODE_REPO` |
| `host_or_domain` | TEXT, nullable | NULL for non-`NETWORK` |
| `chain_id` / `contract_address` / `contract_abi_path` | TEXT, nullable | `CONTRACT` only |
| `contract_investigation_mode` | TEXT, nullable | `CONTRACT` only — `CLIENT_OWNED` / `PUBLIC_RESEARCH` (both modes kept) |
| `platform` / `package_name` / `binary_path` / `binary_hash` | TEXT, nullable | `MOBILE_BINARY` only |
| `backend_target_id` | INTEGER FK → `targets(target_id)`, nullable | `MOBILE_BINARY` only — the app's discovered backend API, registered as its own `NETWORK` row |
| `repo_url_or_path` / `repo_ref` / `repo_diff_scope` | TEXT, nullable | `CODE_REPO` only |

All per-target diminishing-returns and failure counters apply identically regardless of `target_type`.

### DR-SCHEMA-16: `scope_rules` — pattern-kind discriminator

| Column | Type | Notes |
|---|---|---|
| `pattern_kind` | TEXT NOT NULL DEFAULT `'NETWORK'` | `NETWORK` (CIDR/domain/wildcard) / `EXACT_IDENTIFIER` (literal match — contract, package, repo) / `PATH_GLOB` (`CODE_REPO` only, e.g. deny `**/node_modules/**`) |

The deterministic scope checker branches on `pattern_kind` — a distinct code path per kind, not a generalization of the CIDR/regex matcher.

### DR-SCHEMA-17: `monitoring_baseline`

| Column | Type | Notes |
|---|---|---|
| `id` | INTEGER PK | |
| `target_id` | INTEGER FK → `targets` | |
| `baseline_type` | TEXT | `SUBDOMAIN_SET` / `REPO_COMMIT_HEAD` (extensible) |
| `baseline_value` | TEXT | |
| `last_checked_at` / `last_diff_detected_at` | TEXT (ISO8601), latter nullable | |

A diff updates `baseline_value`, logs to `discovered_entities` (`entity_type = 'monitor_diff'`), and stops — never auto-escalates into active testing.

### DR-SCHEMA-18: `checkpoint_events`

The audit trail for the Human Checkpoint Gate. Distinct from `engagement_flag_history` — this logs in-engagement checkpoint evaluations, operator approvals, and manual dispatches.

| Column | Type | Notes |
| --- | --- | --- |
| `id` | INTEGER PK | Primary key identifier |
| `engagement_id` | INTEGER FK → `engagements` | Active engagement identifier |
| `task_id` | INTEGER FK → `task_queue`, nullable | Associated task identifier, nullable for direct operator commands |
| `action_class` | TEXT | `ANTI_FORENSICS` / `LIVE_CREDENTIAL_SPRAY` / `CICD_EXTERNAL_ARTIFACT` / `DEPENDENCY_CONFUSION_PUBLISH` / `PHISHING_MFA_BYPASS` |
| `triggered_at` | TEXT (ISO8601) | Timestamp when task was proposed or queued |
| `status` | TEXT | `AWAITING_APPROVAL` / `APPROVED` / `DENIED` / `EXPIRED` / `OPERATOR_DISPATCHED` — autonomous tasks log review state; operator-directed actions resolve immediately without pipeline stalls |
| `approved_at` | TEXT (ISO8601), nullable | Timestamp of approval or direct command execution |
| `approved_via` | TEXT, nullable | `'OPERATOR_DIRECTIVE'` (direct console or CLI command), `'CONSOLE_DISPATCH'`, or `'AUTO_APPROVED_THRESHOLD_MET'` (`LIVE_CREDENTIAL_SPRAY` lockout check during autonomous passes) |
| `rationale_shown_to_operator` | TEXT | Contextual rationale for autonomous proposals or execution summary for direct operator tasks |
| `estimated_lockout_percentage` / `max_auto_lockout_threshold_at_time` | REAL, nullable | Autonomous credential spraying threshold metrics; nullable for operator-directed credential tasks |

In Autonomous Mode, tasks categorized under sensitive checkpoint classes record an audit row to provide visibility. In Operator-Directed Mode, any matching task directly commanded or invoked by the operator transitions immediately to `status = 'APPROVED'` or `'OPERATOR_DISPATCHED'` (`approved_via = 'OPERATOR_DIRECTIVE'`) and executes without pausing the engine or requiring interactive gate unblocking.


### DR-SCHEMA-19: `operator_command_queue`

Role-directed operator guidance and command queue for execution and context injection — operator directives execute with top priority and zero refusal.

```sql
CREATE TABLE IF NOT EXISTS operator_command_queue (
    command_id INTEGER PRIMARY KEY AUTOINCREMENT,
    engagement_id INTEGER NOT NULL REFERENCES engagements(engagement_id),
    target_role TEXT NOT NULL CHECK (
        target_role IN ('Strategist', 'Operator', 'Gatekeeper', 'Linter', 'Adjudicator', 'Reporter', 'GLOBAL')
    ),
    raw_command TEXT NOT NULL,
    parsed_intent TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'QUEUED' CHECK (
        status IN ('QUEUED', 'INJECTED', 'DISCARDED', 'EXPIRED')
    ),
    failure_reason TEXT,
    queued_at TEXT NOT NULL,
    consumed_at TEXT,
    consumed_by_invocation_id INTEGER REFERENCES model_invocation_logs(invocation_id),
    FOREIGN KEY (engagement_id) REFERENCES engagements(engagement_id)
);
CREATE INDEX IF NOT EXISTS idx_operator_queue_lookup
ON operator_command_queue (engagement_id, target_role, status);
```

`failure_reason` MUST be populated on every `DISCARDED`/`EXPIRED` transition — no directive vanishes silently.

### DR-SCHEMA-20: `live_audit_trail.md` layout

Per-engagement append-only Markdown journal at `<artifact_root>/<engagement_id>/live_audit_trail.md` (`DR-ARTIFACT-01`'s layout) — one block per pipeline transition (Tool Dispatch / Output Sanitization / Model Ingestion / Model Output). Not part of the report-redaction pipeline — same unredacted trust boundary as any raw artifact on disk.

---

## DR-CONCURRENCY — SQLite Adequacy

Single-model-residency inherently serializes model invocations; tool subprocesses can run concurrently with output parsing.

| ID | Requirement |
|----|-------------|
| DR-CONCURRENCY-01 | Database opened in **WAL mode**, not default rollback-journal — a long write MUST NOT block a concurrent `status` read. |
| DR-CONCURRENCY-02 | Every discrete state change commits as its own transaction immediately, never batched — required for per-step durability. |
| DR-CONCURRENCY-03 | Every connection sets PRAGMA busy_timeout = 5000; — WAL mode alone doesn't prevent database is locked between concurrent writers; a writer retries up to 5s before raising. Critical for pause/abort, which must not fail at the moment they matter most. |

**Conclusion:** WAL mode is adequate for this workload (low writer contention, occasional concurrent reads); a client-server DB would be unjustified complexity here — feasible only if DR-CONCURRENCY-01/02 are actually implemented.

---

## DR-ARTIFACT — Artifact Store Layout

| ID | Requirement |
|----|-------------|
| DR-ARTIFACT-01 | Artifacts live under `/home/mhj/.local/share/vapt_agent/artifacts/<engagement_id>/<target_id>/...`. |
| DR-ARTIFACT-02 | Raw output is written before sanitization, named deterministically (`<task_id>_<tool_name>_<timestamp>.raw`) so `artifacts_index.file_path` never goes stale. |
| DR-ARTIFACT-03 | Reports live under `.../reports/pending-approval/` and, post-approval, `.../reports/approved/` — **physically distinct directories**, not just a status flag. |
| DR-ARTIFACT-04 | The intermediate HTML source for every PDF is retained alongside it, never deleted after rendering. |

## DR-RETENTION — Retention & Disk Quota Alignment

| ID | Requirement |
|----|-------------|
| DR-RETENTION-01 | Artifact growth is checked against the documented 85%/95% disk-quota thresholds — a data-layer obligation, since it gates whether an `artifacts_index` write is even attempted. |
| DR-RETENTION-02 | Raw output for `DISMISSED` findings, zero-yield probes, and non-destructive checks MUST NOT be deleted automatically during an engagement — retained to provide full auditability and context for triage review. |
| DR-RETENTION-03 | `state.db` is the durable record of an engagement, not disposable cache — findings/rationale/CVSS justifications live only there; rendered reports are a derived view. |

## DR-BACKUP — Backup

| ID | Requirement |
|----|-------------|
| DR-BACKUP-01 | **MUST** (not best-effort): before Phase 5 hibernation-exit is considered complete, copy `state.db` to a timestamped backup in the same artifact tree. | 
| DR-BACKUP-02 | Local-only (NVMe) — no remote/offsite backup in scope. |

---

## Authority & Conflict Resolution

This document specifies data structures, relational schemas, storage layouts, and
persistence guarantees. In the event of any conflict, discrepancy, or ambiguity
between schema definitions, gate outcome representations, and system control mandates,
the **Security, Safety & Compliance Requirements (`05`)** serves as the final and supreme
authority across the entire system.
