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
| `autonomy_level` | TEXT | e.g. `normal` (per FR-CTRL-06) |
| `phase4_started_at` | TEXT (ISO8601, nullable) | set when Phase 4.2 execution begins |
| `session_budget_hours` | INTEGER | confirmed default: **12** (FR-COUNCIL-11 / NFR-PERF-05) |
| `session_deadline_at` | TEXT (ISO8601, nullable) | `phase4_started_at` + `session_budget_hours`; computed once execution starts |
| `notes` | TEXT | free-text operator notes |

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
| `consecutive_zero_yield_count` | INTEGER DEFAULT 0 | reset to 0 on any yielding task; circuit-breaks at **3** (FR-COUNCIL-11b) |
| `status` | TEXT | `PENDING` / `ACTIVE` / `CAPPED` / `CIRCUIT_BROKEN` / `COMPLETE` |

### DR-SCHEMA-03: `scope_rules`

Scope-boundary data consumed by the Strategist and checked by Council Gate 1
(Hermes-3) — see base §Phase 4.1. **Not an authorization/RoE record** — per explicit
decision, this system does not verify authorization; this table only holds the
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
| `created_by_model` | TEXT | e.g. `DeepSeek-R1-Distill-Qwen-8B` |
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
| `gate1_rationale` | TEXT | Hermes-3's stated reason |
| `gate2_rationale` | TEXT | Qwen-3B's stated reason on block/correct |
| `created_at` / `executed_at` | TEXT (ISO8601) | |

### DR-SCHEMA-06: `tool_execution_logs`

| Column | Type | Notes |
|---|---|---|
| `log_id` | INTEGER PK | |
| `task_id` | INTEGER FK → `task_queue` | |
| `argument_vector` | TEXT (JSON array) | exact argv, never a shell string (FR-TOOL-04) |
| `resolved_binary_path` | TEXT | absolute path the bridge resolved and allowlist-checked (FR-TOOL-03) |
| `start_ts` / `end_ts` | TEXT (ISO8601) | |
| `exit_code` | INTEGER, nullable | null if killed on timeout |
| `timeout_hit` | INTEGER (bool) | |
| `raw_output_artifact_id` | INTEGER FK → `artifacts_index` | full unsanitized stdout/stderr (FR-TOOL-08) |
| `sanitized_summary` | TEXT | what actually entered model context (FR-TOOL-07) |
| `suspected_injection_flag` | INTEGER (bool) DEFAULT 0 | set by the heuristic check in FR-TOOL-13 |

### DR-SCHEMA-07: `verified_vulnerabilities`

| Column | Type | Notes |
|---|---|---|
| `finding_id` | INTEGER PK | |
| `target_id` | INTEGER FK → `targets` | |
| `task_id` | INTEGER FK → `task_queue` | originating task |
| `title` | TEXT | |
| `description` | TEXT | |
| `cwe_id` / `cve_id` | TEXT, nullable | |
| `cvss_version` | TEXT | e.g. `4.0` |
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

### DR-SCHEMA-11: `reports`

| Column | Type | Notes |
|---|---|---|
| `report_id` | INTEGER PK | |
| `engagement_id` | INTEGER FK → `engagements` | |
| `format` | TEXT | `markdown` / `html` / `pdf` |
| `status` | TEXT | `DRAFT_PENDING_APPROVAL` / `APPROVED` / `REJECTED` |
| `file_path` | TEXT | |
| `created_at` / `approved_at` | TEXT (ISO8601), nullable | |
| `approved_by` | TEXT | fixed value: `Muhammad Huzaifa Jamil` once approved (FR-CTRL-08) |

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
| DR-BACKUP-01 | Before Phase 5 hibernation-exit completes, the system SHOULD copy `state.db` to a timestamped backup file in the same artifact tree (e.g. `artifacts/<engagement_id>/state_backup_<timestamp>.db`), so a corrupted live database from an unclean future run does not destroy the only copy of a completed engagement's findings. |
| DR-BACKUP-02 | Backups are local-only (NVMe), consistent with the no-cloud-dependency design (NFR-SEC-02) — no remote/offsite backup is in scope for this planning phase. |
