# Historical State Inheritance & Deduplication Subsystem — Autonomous Agentic VAPT System

This specification prevents cross-engagement inefficiencies and evidentiary regressions:
the Strategist re-proposing already-explored hypotheses, the Operator duplicating prior
commands, and the Reporter re-reporting (or silently dropping) known vulnerabilities. It defines
the behavioral adaptations for Phase 4.1, Gate 2, Gate 3, and report generation when a target
has prior-engagement records in `state.db`.

This subsystem operates under the **Dual-Mode Execution Architecture**:
- In **Autonomous Mode**, deduplication optimizes execution by skipping identical commands,
  while regression checks are strictly constrained to non-destructive verification (read-only
  queries and benign verification writes, barring state drops, schema alterations, and DoS).
- In **Operator-Directed Mode**, deduplication gates stand down: manual commands to re-test,
  fuzz, or re-exploit a specific vector execute unconditionally with zero automated refusal.

Key design points: "explored" attack paths derive from existing `task_queue` rows
(`status IN ('EXECUTED','FOLLOWUP_GENERATED')`); `DUPLICATE_COMMAND` rejections apply only to
autonomous cycles; `command_hash` canonicalizes ordered flag/value pairs; cross-engagement
fingerprints link via `targets.host_or_domain`; and historical `CONFIRMED` findings are never
silently dropped.

---

## Assessment Mode: `INITIAL` vs `RETEST`

An explicit, CLI-selected operating mode (`engagements.assessment_mode`) so the
Strategist and report pipeline never have to infer intent from database contents
alone:

| Dimension | `INITIAL` (default) | `RETEST` |
|---|---|---|
| Primary objective | Explore untouched attack surface; historical paths are exclusion context only | Verify regression status of known findings *first*, then explore new surface |
| Historical `CONFIRMED` findings | Not actively re-tested | Seeded as priority `task_queue` rows before Strategist planning begins for that target |
| Report output | Standard fresh `VAPT_FINDING` reports (`finding_origin = 'NEW'`) | Regression reports for carried-forward/remediated findings (`finding_origin = 'REGRESSION_CHECK'`) **plus** fresh reports for anything newly discovered in the same pass |
| `DISMISSED` fingerprint matches | Used as a silent negative filter so Gate 3 doesn't re-litigate a known WAF/rate-limit block from scratch | Same treatment |

**Never silently omitted, in either mode**: a `RETEST`-mode regression check always
produces a visible outcome — either the finding is still present (individual
`VAPT_FINDING` report, explicitly marked as carried forward) or it's been remediated
(surfaced in the `INFO_REGISTER`, explicitly marked as a verified fix).

### Per-target sequencing in `RETEST` mode

For each target in a `RETEST`-mode engagement, **before** that target's normal Phase
4.1 Strategist invocation:

1. **Regression seeding (deterministic, no model)** — the orchestrator queries prior
   `CONFIRMED` findings for that target's `host_or_domain` across all engagements
   (query in `FR-DEDUP-04` below) and inserts one `task_queue` row per finding, each
   carrying the finding's stored reproduction command, `origin = 'HISTORICAL_REGRESSION'`,
   and `source_finding_id` set to the original finding being verified.
2. **Deterministic Scope & Syntax Verification** — The task is verified against the target's
   current scope rules and Gate 2 syntax validator. Autonomous regression tasks adhere to standard
   non-destructive constraints; operator-directed re-tests dispatch immediately without automated
   scope blocking.
3. **Execution via Tool Bridge** — Tasks dispatch through the resident Operator and Tier 1/2
   bridge. In Autonomous Mode, tasks run non-destructively and observe active engagement flags;
   when an operator explicitly directs regression execution, commands execute per supplied
   parameters with zero refusal.
4. **Gate 3 adjudication of the regression outcome** — evaluated against the same
   evidentiary rigor as any other candidate (impact-beyond-technically-possible,
   baseline/attack/diff), with the *original* finding's confirmed evidence serving as
   the baseline for comparison. Outcome is either `CONFIRMED` (still present — a
   fresh CVSS computation is still run, not a copy of the old score, since conditions
   may have changed) or `REMEDIATED` (new `status` value, only reachable from
   `HISTORICAL_REGRESSION` origin).
5. Only after all regression tasks for that target resolve does the normal Phase 4.1
   Strategist invocation run for that target's fresh exploration pass — which still
   receives the `<explored_attack_paths>` exclusion context so it doesn't re-propose
   what regression already re-tested or what prior engagements already exhausted.

This means Gate 3 (`Mistral-7B`) is invoked twice per target in `RETEST` mode — once
for regression outcomes, once for the target's own fresh Phase 4.3 — an accepted,
bounded extra model-swap cost (`RETEST` mode only, and only for targets carrying
prior history), not a general-case regression.

---

## 1. FR-DEDUP — Historical Query, Gate Enforcement & Report Routing

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-DEDUP-01 | **(Historical context seeding, `INITIAL` and `RETEST` alike)** Before the Strategist's Phase 4.1 invocation for a target, the orchestrator MUST compile that target's prior-engagement `attack_paths` (via the `task_queue`-derived "explored" condition above) into an `<explored_attack_paths>` context block, instructing the Strategist to pursue orthogonal attack surfaces rather than replicate them. | M |
| FR-DEDUP-02 | **(Council Gate 2 invariant deduplication)** Council Gate 2 identifies duplicate autonomous commands matching prior completed runs to optimize queue efficiency. When an operator explicitly directs a re-scan or command re-execution, deduplication checks stand down. | M |
| FR-DEDUP-03 | **(Vulnerability fingerprint computation)** On any finding Gate 3 marks `CONFIRMED`, the system MUST deterministically compute `finding_fingerprint = SHA256(cwe_id \|\| target_endpoint \|\| affected_parameter)` (non-LLM) and persist it alongside the new `target_endpoint`/`affected_parameter` columns. | M |
| FR-DEDUP-04 | **(Regression seeding query, `RETEST` mode only)** For each target in a `RETEST`-mode engagement, before that target's Phase 4.1, the orchestrator MUST query all prior-engagement findings with `status = 'CONFIRMED'` for that target's `host_or_domain` (joined via `targets`, never via raw `target_id`, which is engagement-scoped) and insert one `task_queue` row per finding with `origin = 'HISTORICAL_REGRESSION'` and `source_finding_id` set. | M |
| FR-DEDUP-05 | **(Regression tasks)** Tasks originating from historical regression (origin = 'HISTORICAL_REGRESSION') run under standard non-destructive autonomous rules (read-only verification and safe checks, prohibiting updates, drops, or DoS). Operator-directed regression checks execute immediately with zero gate delays. | M |
| FR-DEDUP-06 | **(Regression outcome & report routing)** When Gate 3 adjudicates a HISTORICAL_REGRESSION-origin task: if the vulnerability reproduces, the finding is marked CONFIRMED, finding_origin = 'REGRESSION_CHECK', with retests_finding_id linked to the originating record, noting its carried-forward status. If the vulnerability no longer reproduces, it is marked REMEDIATED and cataloged within the engagement's INFO_REGISTER as a verified fix. In Operator-Directed Mode, the operator may directly update, override, or reclassify regression status and reporting placement at will. | M |
| FR-DEDUP-07 | **(Dismissed-fingerprint carry-forward, both modes)** A candidate whose `finding_fingerprint` matches a prior-engagement `DISMISSED` finding MUST be presented to Gate 3 with that prior dismissal's rationale attached, so the model doesn't misinterpret identical response data (e.g. re-flagging a known Cloudflare WAF block as a fresh candidate). This does not auto-dismiss the new candidate — Gate 3 still independently evaluates it using its full adjudication criteria; the prior rationale is context, not a verdict. | M |

---

## 2. Data & Storage

Persisted in the state store: `assessment_mode`; `origin`'s third value plus
`source_finding_id`; `command_hash`; and the new
`target_endpoint`/`affected_parameter`/`finding_fingerprint`/`finding_origin`/
`retests_finding_id`/`REMEDIATED` status columns.

## 3. Interface & Integration

`--assessment-mode initial|retest` (default `initial`) is part of the `vaptctl
start` CLI syntax.

## 4. New Dependency

None. `command_hash`/`finding_fingerprint` use `hashlib.sha256` (Python stdlib) —
no new package.

---

## Authority & Conflict Resolution

This specification defines historical state queries, deduplication hashes, regression sequencing,
and re-test reporting workflows. In the event of any discrepancy, ambiguity, or conflict between
deduplication filters, regression execution rules, and system security mandates, the
**Security, Safety & Compliance Requirements (`05`)** serves as the final and supreme authority
across the entire system.
