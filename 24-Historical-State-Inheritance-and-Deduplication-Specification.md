# Historical State Inheritance & Deduplication Subsystem — Autonomous Agentic VAPT System

**Origin:** an operator-supplied, near-implementation-ready spec addressing three
failure modes of re-testing the same target across engagements: the Strategist
re-proposing already-explored attack hypotheses, the Operator re-running
already-executed tool invocations, and the Adjudicator/Reporter re-reporting
already-known vulnerabilities. Refined through a consistency-check round before
formalization, then through a follow-up round that added an explicit **Assessment
Mode** dimension after a client-safety issue was raised on the first draft — both
rounds are recorded below with the reasoning, not silently adopted or silently
rejected.

**Relationship to the rest of this system:** this is not a new document type or a
new top-level phase — it modifies how Phase 4.1 (Strategist), Council Gate 2
(`FR-COUNCIL-08`), Council Gate 3 (`FR-COUNCIL-13`), and report generation
(`FR-COUNCIL-15`/`17`) behave when a target has prior-engagement history in
`state.db` (a single global database across all engagements, per `03`'s `DR-SCHEMA`
preamble — this is what makes cross-engagement lookups possible at all without a
second store). It also extends `task_queue.origin` (`03`, `23`, decision #63) with a
third value.

---

## Corrections & refinements made during consistency review

| # | Original spec | Issue found | Resolution |
|---|---|---|---|
| 1 | Historical query filtered `attack_paths.status IN ('GATE1_APPROVED','COMPLETED','EXHAUSTED')` | `DR-SCHEMA-04` only defines `PROPOSED`/`GATE1_APPROVED`/`GATE1_REJECTED` — `COMPLETED`/`EXHAUSTED` don't exist, and nothing in the architecture ever transitions a path to either state (no lifecycle logic was ever specified for it). Adding two enum values with no defined transition trigger would just create a permanently-unreachable state, the same category of problem decision #60 avoided by deriving dashboard state from real tables instead of a second, hand-maintained one. | **Resolved**: "explored" is derived directly from existing `task_queue` rows — `EXISTS (SELECT 1 FROM task_queue WHERE path_id = ap.path_id AND status IN ('EXECUTED','FOLLOWUP_GENERATED'))` — no new `attack_paths` status values, no new lifecycle to maintain. |
| 2 | Gate 2 dedup: "the Operator is forced to rewrite its action or move to the next task in the queue without consuming an execution budget" (a new, separate mechanism) | This invents a second rejection pathway alongside the one `FR-COUNCIL-09` already defines (3-attempt regenerate, then `BLOCKED`) — two different "what happens when Gate 2 says no" behaviors is a real consistency risk for whoever implements this. | **Resolved**: `DUPLICATE_COMMAND` is just another Gate 2 rejection reason string, routed through the *existing* `FR-COUNCIL-09` retry/`BLOCKED` pipeline — no new task-lifecycle behavior. This also delivers the "no execution budget consumed" property for free: `targets.task_count` (`DR-SCHEMA-02`) is only incremented on actual execution (`tool_execution_logs` row creation), which a Gate-2-blocked task never reaches, regardless of which rejection reason blocked it. |
| 3 | `command_hash = sha256(canonicalize(resolved_binary_path + sorted(args)))`, canonicalizing by sorting the flat argv token list | Sorting individual tokens breaks flag/value pairing — `-p 80 -oN 443` and `-p 443 -oN 80` sort to the same token multiset and would hash **identically** despite being different commands, a false-positive that silently blocks a legitimately different scan. This is a correctness bug in the dedup mechanism itself, not a style preference. | **Resolved**: canonicalization groups each recognized flag with its value(s) into pairs first, then sorts the *pairs* (not raw tokens), then hashes. Positional (non-flag) arguments are kept in their original relative order within the canonical form, since position is often semantically load-bearing for them (e.g. a target argument) in a way flag/value pairs generally aren't. |
| 4 | `finding_fingerprint` cross-engagement lookup indexed/queried by `target_id` | `targets.target_id` is engagement-scoped (`DR-SCHEMA-02`, FK → a specific `engagements` row) — a new engagement against the same domain gets a **new** `target_id`, so any query or index keyed on `target_id` directly can never find a prior engagement's rows. Same class of bug the `attack_paths` query already avoided correctly by joining on `host_or_domain` instead. | **Resolved**: the fingerprint lookup joins `verified_vulnerabilities → task_queue → targets` and filters on `targets.host_or_domain`, exactly mirroring the pattern the `attack_paths` query already used correctly. The index itself is just `(finding_fingerprint)`, with no `target_id` in the key. |
| 5 | `FR-DEDUP-03` (first draft): a `CONFIRMED`-fingerprint match is marked `HISTORICAL_DUPLICATE` and **auto-excluded from the current report draft** | Raised directly to the operator as a client-safety issue (not silently implemented): this system has no regression-verification concept in the first draft, so if a client never actually remediated the issue, the new engagement's report would simply never mention a known, still-present vulnerability at all — a real risk for a security-assessment deliverable, where a client can reasonably expect every assessment period's report to account for everything currently present. | **Resolved, materially expanded**: see the **Assessment Mode** section below — the operator's follow-up answer replaced "silently exclude" with an explicit **retest mode** that actively re-verifies known findings and always surfaces the outcome (confirmed-still-present *or* confirmed-remediated), never a silent drop. |
| 6 | (Side finding, unrelated to this spec) `13`'s `IAB-CLI` already declared a `[--mode assess|monitor]` flag on `vaptctl start` with **no backing requirement anywhere** in `01`-`23` — a dangling, never-implemented flag (most likely an early, inconsistent reference to the separately-existing `vaptctl monitor` command, `FR-MONITOR-01..04`). | Rather than add a second, overlapping "mode" concept to `start`, the new `--assessment-mode` flag this document introduces takes that slot directly — see `IR-CLI` amendment below. | **Resolved** — dangling flag replaced, not left alongside the new one. |

---

## Assessment Mode: `INITIAL` vs `RETEST`

**Confirmed operator design**, replacing the first draft's passive fingerprint-exclusion
with an explicit, CLI-selected operating mode (`engagements.assessment_mode`,
`DR-SCHEMA-01` amendment below) so the Strategist and report pipeline never have to
infer intent from database contents alone:

| Dimension | `INITIAL` (default) | `RETEST` |
|---|---|---|
| Primary objective | Explore untouched attack surface; historical paths are exclusion context only | Verify regression status of known findings *first*, then explore new surface |
| Historical `CONFIRMED` findings | Not actively re-tested | Seeded as priority `task_queue` rows before Strategist planning begins for that target |
| Report output | Standard fresh `VAPT_FINDING` reports (`finding_origin = 'NEW'`) | Regression reports for carried-forward/remediated findings (`finding_origin = 'REGRESSION_CHECK'`) **plus** fresh reports for anything newly discovered in the same pass |
| `DISMISSED` fingerprint matches | Used as a silent negative filter so Gate 3 doesn't re-litigate a known WAF/rate-limit block from scratch | Same treatment |

**Never silently omitted, in either mode**: a `RETEST`-mode regression check always
produces a visible outcome — either the finding is still present (individual
`VAPT_FINDING` report, explicitly marked as carried forward) or it's been remediated
(surfaced in the `INFO_REGISTER`, explicitly marked as a verified fix) — closing the
gap correction #5 identified.

### Per-target sequencing in `RETEST` mode

For each target in a `RETEST`-mode engagement, **before** that target's normal Phase
4.1 Strategist invocation:

1. **Regression seeding (deterministic, no model)** — the orchestrator queries prior
   `CONFIRMED` findings for that target's `host_or_domain` across all engagements
   (query in `FR-DEDUP-04` below) and inserts one `task_queue` row per finding, each
   carrying the finding's stored reproduction command, `origin = 'HISTORICAL_REGRESSION'`,
   and `source_finding_id` set to the original finding being verified.
2. **Full Gate 1 + Gate 2, exactly as any non-`MANUAL_OPERATOR`-origin task** — scope
   may have narrowed since the prior engagement, and Gate 2 still validates syntax.
   `HISTORICAL_REGRESSION` origin confers **no exception** anywhere — see
   `FR-DEDUP-05`.
3. **Execution** via the resident Operator/bridge, same as any Tier 1/Tier 2 command
   — including the existing opt-in-flag gate (`FR-TOOL-06a`): if the original finding
   required e.g. active exploitation and the new engagement didn't set
   `--allow-active-exploitation`, the stored repro is `POLICY_REFUSED` exactly as a
   fresh proposal would be, not silently exempted for being a "known" action.
4. **Gate 3 adjudication of the regression outcome** — evaluated against the same
   evidentiary rigor as `FR-COUNCIL-14a` (impact-beyond-technically-possible,
   baseline/attack/diff), with the *original* finding's confirmed evidence serving as
   the baseline for comparison. Outcome is either `CONFIRMED` (still present — a
   fresh CVSS computation is still run per `FR-COUNCIL-16a`, not a copy of the old
   score, since conditions may have changed) or `REMEDIATED` (new `status` value,
   only reachable from `HISTORICAL_REGRESSION` origin).
5. Only after all regression tasks for that target resolve does the normal Phase 4.1
   Strategist invocation run for that target's fresh exploration pass — which still
   receives the `<explored_attack_paths>` exclusion context (correction #1) so it
   doesn't re-propose what regression already re-tested or what prior engagements
   already exhausted.

This means Gate 3 (`Mistral-7B`) is invoked twice per target in `RETEST` mode — once
for regression outcomes, once for the target's own fresh Phase 4.3 — an accepted,
bounded extra model-swap cost (`RETEST` mode only, and only for targets carrying
prior history), not a general-case regression.

---

## 1. FR-DEDUP — Historical Query, Gate Enforcement & Report Routing

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-DEDUP-01 | **(Historical context seeding, `INITIAL` and `RETEST` alike)** Before the Strategist's Phase 4.1 invocation for a target, the orchestrator MUST compile that target's prior-engagement `attack_paths` (via the `task_queue`-derived "explored" condition, correction #1) into an `<explored_attack_paths>` context block, instructing the Strategist to pursue orthogonal attack surfaces rather than replicate them. | M |
| FR-DEDUP-02 | **(Council Gate 2 invariant deduplication)** Council Gate 2 (`FR-COUNCIL-08`) MUST reject, with reason `DUPLICATE_COMMAND`, any Operator-emitted command whose canonical `command_hash` (flag/value-pair-aware, correction #3) matches a prior completed `tool_execution_logs` row for the same `host_or_domain`, regardless of which engagement produced the prior row. This rejection is handled by the existing `FR-COUNCIL-09` regenerate/`BLOCKED` pipeline — no separate mechanism. | M |
| FR-DEDUP-03 | **(Vulnerability fingerprint computation)** On any finding Gate 3 marks `CONFIRMED`, the system MUST deterministically compute `finding_fingerprint = SHA256(cwe_id \|\| target_endpoint \|\| affected_parameter)` (non-LLM) and persist it alongside the new `target_endpoint`/`affected_parameter` columns (`DR-SCHEMA-07` amendment). | M |
| FR-DEDUP-04 | **(Regression seeding query, `RETEST` mode only)** For each target in a `RETEST`-mode engagement, before that target's Phase 4.1, the orchestrator MUST query all prior-engagement findings with `status = 'CONFIRMED'` for that target's `host_or_domain` (joined via `targets`, never via raw `target_id` — correction #4) and insert one `task_queue` row per finding with `origin = 'HISTORICAL_REGRESSION'` and `source_finding_id` set. | M |
| FR-DEDUP-05 | **(No gate exception for regression tasks)** A `task_queue` row with `origin = 'HISTORICAL_REGRESSION'` MUST pass the full two-tier Council Gate 1 (`FR-COUNCIL-03a` **and** `FR-COUNCIL-04`'s semantic tier — unlike `MANUAL_OPERATOR` origin, which skips only the semantic tier per `FR-INTERVENE-06a`/decision #63), the full Council Gate 2, and the existing opt-in-flag gate (`FR-TOOL-06a`), exactly as an `AUTONOMOUS_COUNCIL`-origin task would. This origin value exists purely for audit/report-linkage purposes, not to grant any bypass. | M |
| FR-DEDUP-06 | **(Regression outcome & report routing)** When Gate 3 adjudicates a `HISTORICAL_REGRESSION`-origin task: if the vulnerability still reproduces, the finding is marked `CONFIRMED`, `finding_origin = 'REGRESSION_CHECK'`, `retests_finding_id` set to the original finding — and its individual `VAPT_FINDING` report (per `FR-COUNCIL-17(a)`) MUST explicitly state carried-forward status and the originating engagement, not read as a freshly-discovered issue. If the vulnerability no longer reproduces, the finding is marked `REMEDIATED` (new `verified_vulnerabilities.status` value, reachable only via this path) and surfaced in the engagement's `INFO_REGISTER` (`FR-COUNCIL-17(b)`, alongside `DISMISSED` items) as a verified fix — never silently dropped from either document. | M |
| FR-DEDUP-07 | **(Dismissed-fingerprint carry-forward, both modes)** A candidate whose `finding_fingerprint` matches a prior-engagement `DISMISSED` finding MUST be presented to Gate 3 with that prior dismissal's rationale attached, so the model doesn't misinterpret identical response data (e.g. re-flagging a known Cloudflare WAF block as a fresh candidate). This does not auto-dismiss the new candidate — Gate 3 still independently evaluates it per `FR-COUNCIL-13`/`14`/`14a`; the prior rationale is context, not a verdict. | M |

---

## 2. Data & Storage (revises `03`)

### DR-SCHEMA-01 amendment: `engagements`

```sql
ALTER TABLE engagements ADD COLUMN assessment_mode TEXT NOT NULL DEFAULT 'INITIAL'
    CHECK (assessment_mode IN ('INITIAL', 'RETEST'));
```

### DR-SCHEMA-04 note: `attack_paths` — no schema change

"Explored" status is derived from `task_queue`, not stored on `attack_paths` itself
(correction #1). No new column, no new enum value.

### DR-SCHEMA-05 amendment: `task_queue` (further amends decision #63's amendment)

```sql
-- origin CHECK constraint extended (was: 'AUTONOMOUS_COUNCIL','MANUAL_OPERATOR')
-- now: 'AUTONOMOUS_COUNCIL','MANUAL_OPERATOR','HISTORICAL_REGRESSION'

ALTER TABLE task_queue ADD COLUMN source_finding_id INTEGER
    REFERENCES verified_vulnerabilities(finding_id);
    -- nullable; set only when origin = 'HISTORICAL_REGRESSION' — the original
    -- finding this task is re-verifying. Parallels `source_command_id` (decision
    -- #63), which serves the same provenance-tracking role for MANUAL_OPERATOR.
```

### DR-SCHEMA-06 amendment: `tool_execution_logs`

```sql
ALTER TABLE tool_execution_logs ADD COLUMN command_hash TEXT;
CREATE INDEX idx_tool_cmd_hash ON tool_execution_logs(resolved_binary_path, command_hash);
```

`command_hash` = pair-aware canonical SHA256 (correction #3) — flags and their
values are grouped before sorting; positional arguments keep their original
relative order.

### DR-SCHEMA-07 amendment: `verified_vulnerabilities`

```sql
ALTER TABLE verified_vulnerabilities ADD COLUMN target_endpoint TEXT;
ALTER TABLE verified_vulnerabilities ADD COLUMN affected_parameter TEXT;
ALTER TABLE verified_vulnerabilities ADD COLUMN finding_fingerprint TEXT;
ALTER TABLE verified_vulnerabilities ADD COLUMN finding_origin TEXT NOT NULL DEFAULT 'NEW'
    CHECK (finding_origin IN ('NEW', 'REGRESSION_CHECK'));
ALTER TABLE verified_vulnerabilities ADD COLUMN retests_finding_id INTEGER
    REFERENCES verified_vulnerabilities(finding_id);
    -- nullable; set only when finding_origin = 'REGRESSION_CHECK'

CREATE INDEX idx_vuln_fingerprint ON verified_vulnerabilities(finding_fingerprint);
-- deliberately no target_id in this index — target_id is engagement-scoped
-- (DR-SCHEMA-02), so cross-engagement lookups join through targets.host_or_domain
-- instead (correction #4), never filter on target_id directly.
```

`status` enum (previously `CANDIDATE`/`CONFIRMED`/`DISMISSED`) gains a fourth value:
`REMEDIATED` — reachable only when `finding_origin = 'REGRESSION_CHECK'` and the
stored reproduction no longer triggers the original impact.

---

## 3. Interface & Integration (revises `04`/`13`)

### IR-CLI amendment (`13`'s `IAB-CLI`)

```
vaptctl start   --targets <list> --scope-rules scope.yaml [--config vapt_agent.config.yaml] \
                 [--assessment-mode initial|retest] \
                 [--allow-brute-force] [--allow-active-exploitation] [--allow-lateral-movement] \
                 [--allow-anti-forensics --white-cell-contact <text> --attest-disclosure] \
                 [--allow-live-credential-spray] [--allow-cicd-external-artifact] \
                 [--allow-dependency-confusion-publish]
```

Replaces the previously-dangling, never-implemented `[--mode assess|monitor]` slot
(correction #6) — default `initial` if the flag is omitted, matching
`assessment_mode`'s schema default.

---

## 4. Acceptance Criteria (extends `09`)

## TP-DEDUP — Historical State Inheritance & Deduplication

| Test | Method | Pass Criteria |
|---|---|---|
| Strategist receives exclusion context, doesn't repeat prior paths | Test | Run two sequential engagements against the same `host_or_domain`; confirm the second engagement's Strategist prompt contains `<explored_attack_paths>` derived from the first engagement's `task_queue`-executed paths, and the resulting new hypotheses don't substantially overlap (FR-DEDUP-01). |
| Gate 2 blocks an exact-duplicate command via the existing retry pipeline | Test | Re-execute the identical tool invocation (same `resolved_binary_path` + args) against the same target in a second engagement; confirm Gate 2 rejects with `DUPLICATE_COMMAND`, the Operator regenerates per `FR-COUNCIL-09`, and if no distinct command is produced within 3 attempts the task is `BLOCKED` — confirm `targets.task_count` is not incremented for the blocked attempt (FR-DEDUP-02). |
| Command-hash canonicalization doesn't produce false-positive duplicates | Test | Submit two commands whose flags carry swapped positions but different flag/value pairings (e.g. `-p 80 -oN 443` vs `-p 443 -oN 80`); confirm they hash *differently* and neither is falsely blocked as a duplicate of the other (correction #3). |
| Fingerprint lookup finds prior-engagement matches via `host_or_domain`, not `target_id` | Test | Confirm the same finding in engagement N-1 and a fresh engagement N against the same domain (different `target_id` values) still resolves to the same `finding_fingerprint` match (FR-DEDUP-03, correction #4). |
| `RETEST` mode always surfaces a visible outcome, never a silent drop | Test | Seed a prior `CONFIRMED` finding; run a `--assessment-mode retest` engagement against the same target. If the repro still succeeds, confirm an individual `VAPT_FINDING` report is generated explicitly marked carried-forward with the originating engagement referenced. If the repro no longer succeeds, confirm `status = 'REMEDIATED'` and the finding appears in the `INFO_REGISTER` as a verified fix. Confirm neither outcome is ever silently absent from both documents (FR-DEDUP-06). |
| `HISTORICAL_REGRESSION` origin gets zero gate exceptions | Test | Seed a prior finding whose stored repro command would now fall outside a narrowed `scope_rules`; run `--assessment-mode retest`; confirm Gate 1's full two-tier check (including the semantic tier) rejects it exactly as a fresh out-of-scope proposal would — no `HISTORICAL_REGRESSION`-specific bypass exists anywhere (FR-DEDUP-05). Repeat with a finding that requires `--allow-active-exploitation` when that flag is unset for the new engagement; confirm `POLICY_REFUSED` (FR-TOOL-06a unaffected). |
| Dismissed-fingerprint carry-forward informs Gate 3 without auto-dismissing | Test | Seed a prior `DISMISSED` finding (e.g. WAF-block rationale); trigger an equivalent candidate in a fresh engagement; confirm Gate 3's context includes the prior rationale, but confirm Gate 3 still independently evaluates the new candidate against fresh evidence rather than auto-dismissing on the fingerprint match alone (FR-DEDUP-07). |

---

## 5. New Dependency (for `08`)

None. `command_hash`/`finding_fingerprint` use `hashlib.sha256` (Python stdlib) —
no new package.
