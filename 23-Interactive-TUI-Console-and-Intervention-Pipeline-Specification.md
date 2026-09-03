# Interactive TUI Console & Asynchronous Intervention Pipeline — Autonomous Agentic VAPT System

**Origin:** an operator-supplied, near-implementation-ready feature spec for a live
`Textual`-based console (`vaptctl console`) that streams pipeline activity to an
append-only Markdown journal and lets the operator inject role-directed guidance
into the running council mid-engagement. Refined through a consistency-check round
before formalization — two of the four rounds of clarification materially changed
the design from the original draft; both are recorded below with the reasoning, not
silently adopted or silently rejected.

**Relationship to `22`'s dashboard:** these are companion tools, not competitors.
`vaptctl dashboard` (`22`) owns host/engine telemetry (RAM, active model, tok/s) and
is read-only. `vaptctl console` (this document) owns pipeline *narrative* (what's
happening, why, and operator steering) and is read **and** write (it inserts into
`operator_command_queue`). `FR-TUI-02` explicitly keeps host telemetry out of the
console's viewport specifically so the two don't duplicate each other.

---

## Corrections & refinements made during consistency review

| # | Original spec | Issue found | Resolution (operator-confirmed) |
|---|---|---|---|
| 1 | Role-prefix list (`@strat`/`@op`/`@gate1`/`@adj`/`@rep`) and `DR-SCHEMA-19`'s `target_role` CHECK constraint named only 5 roles | The Offline Script Linter (`Qwen2.5-Coder-3B-Instruct`) is the system's 6th model and had no prefix, no CHECK-constraint value, and no `FR-INTERVENE-07` invocation point at all. | **Added**: `@lint` prefix, `Linter` added to the CHECK constraint, and its own (rare, between-phase-only) invocation point — see `FR-INTERVENE-01/02/07` below. |
| 2 | `FR-INTERVENE-06`: "operator instruction MUST take precedence" on any conflict, unqualified | As worded, this didn't say whether `FR-COUNCIL-06`'s non-bypassable Gate 1 scope check, the Tier 2 denylist, opt-in-flag categories, or rate limiting still apply to whatever command results from an operator-steered task. A first-pass answer said these could be overridden — walked back after the concrete risk was spelled out (an operator typo no longer scope-checked; a compromised/accessed console becoming a full safety-architecture bypass point). | **Confirmed, narrower model**: operator precedence is **strategic/reasoning-weight only** — which hypothesis or target the council works on next, and how it should reason about a conflicting instruction. It does not, and structurally cannot, change what `FR-COUNCIL-03a`/`06` (Tier 0 scope), `FR-TOOL-06` (Tier 2 denylist), `FR-TOOL-06a` (opt-in-flag validation), or `FR-TOOL-14` (rate limiting) will do with the resulting command — those apply identically regardless of whether a command traces back to an autonomous task or an operator directive. See revised `FR-INTERVENE-06`. |
| 3 | Human Checkpoint Gate (`FR-CHECKPOINT-03`) interaction with the console was unspecified | If an operator explicitly dispatches a checkpoint-class command (e.g. live credential-spray) via console, does the formal `PAUSED_AWAITING_CHECKPOINT` pause still fire, or does the operator's own real-time act of typing it already satisfy the "live human confirmation" the gate exists to obtain? | **Confirmed**: an explicit, specific console dispatch of a checkpoint-class action **is** the live human confirmation — the interactive pause is skipped and a `checkpoint_events` row is auto-finalized (`approved_via = 'CONSOLE_DISPATCH'`). This does **not** touch `FR-CHECKPOINT-02`'s pre-engagement opt-in-flag gate (an unset flag still refuses the command outright, no checkpoint ever raised) or any of §2's non-bypassable checks — only the live pause step is skipped, and only when the operator's own text names the action specifically (a vague nudge the *model* then escalates into a checkpoint-class action still gets the full pause — see `FR-INTERVENE-10`). |
| 4 | Command/directive lifecycle had an `EXPIRED` status with no defined trigger, and no requirement against silent failure | A directive could vanish from view with no operator-visible explanation. | **Confirmed**: expiration is never silent. Every `EXPIRED`/`DISCARDED` transition MUST populate a new `failure_reason` column with the specific cause (e.g. "Tier-0 Refusal: target outside CIDR scope", "Target lifecycle window closed: Phase 4.1 already concluded for this target"). Expiration is triggered by invocation-window closure for that target, not a fixed TTL. See `DR-SCHEMA-19` (revised) and `FR-INTERVENE-11`. |

## Amendment (decision #63): Gate 1 semantic-tier bypass for manual-operator-origin tasks

Correction #2 above established a "zero exception" model for `FR-INTERVENE-06`:
every deterministic gate evaluates a console-influenced command exactly as it would
an autonomous one. A follow-up request asked to go further — skip Gate 1 and the
Checkpoint Gate entirely for operator-dispatched tasks, framing council guardrails
as governing only the autonomous LLMs, not the operator. That framing was pushed
back on directly: `FR-COUNCIL-03a`'s Tier-0 scope check exists to catch the
operator's *own* mistakes (typos, scope drift over a long engagement) against the
operator's *own* prior `scope_rules` configuration, not to second-guess the
operator's authority to test — removing it for manual-origin tasks would turn a
compromised or misused console into a single point of failure for the entire safety
architecture, with nothing left to catch it.

**Resolved, narrower amendment**: only Gate 1's **semantic** tier (`Hermes-3`,
`FR-COUNCIL-04`) is skipped for a task whose `origin` is `MANUAL_OPERATOR` — an
operator's own explicit, specific command already **is** the contextual/strategic
judgment call that tier exists to make on the model's behalf (see `FR-COUNCIL-04`'s
"not a refusal backstop" framing, decision #55 / `11` C-03). Nothing else changes:

- `FR-COUNCIL-03a`'s deterministic Tier-0 scope check still runs unconditionally,
  for every task regardless of `origin` — unchanged, still non-bypassable.
- `FR-TOOL-06`/`06a` (Tier 2 denylist, opt-in-flag validation) and `FR-TOOL-14`
  (rate limiting) are unaffected — they were never part of Gate 1, and this
  amendment touches Gate 1's semantic tier only.
- The Checkpoint Gate is unaffected beyond what `FR-INTERVENE-10` (correction #3)
  already specified — explicit dispatch skips only the interactive *pause*, never
  `FR-CHECKPOINT-02`'s flag gate or `FR-CHECKPOINT-05`'s attestation fields. This
  amendment does not change or extend that mechanism.
- A `task_queue` row's `origin` is `'MANUAL_OPERATOR'` only when its
  `proposed_command` traces back to an operator directive whose own text explicitly
  and specifically named the action — the same specificity bar `FR-INTERVENE-10`
  already uses — via the new `source_command_id` FK (`DR-SCHEMA-05`, `03`). A vague
  directive the model expands into a command on its own initiative still carries
  `origin = 'AUTONOMOUS_COUNCIL'` and still gets the full two-tier gate.

See `FR-INTERVENE-06a` (new, below) and `FR-COUNCIL-04`/`05`/`06` (revised, `01`).

**Not changed:** `FR-COUNCIL-18`'s draft-time report redaction. A cited source rule
("never redact evidence in a report") was verified against its exact text
(`Actual-Setup/CLAUDE.md` — scoped explicitly to the report, not the whole pipeline)
and found to already be fully satisfied by the existing design: the draft is redacted
only until `approve-report`, at which point it's restored byte-exact and the
**approved report is never redacted**. Nothing in this document's journal/console
streams goes through that redaction step at all — they show the same unredacted raw
signal that `tool_execution_logs`/`artifacts_index` already store, the same trust
boundary as every other raw artifact on disk, not a new exposure.

---

## 1. FR-TUI — Live Stream & Interactive Command Console

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-TUI-01 | The system MUST provide an interactive TUI command surface (`vaptctl console`), built on `Textual`, running concurrently with an active orchestrator instance. | M |
| FR-TUI-02 | The console layout MUST consist of exactly two components: an upper live event-stream pane, and a bottom command-input bar. It MUST NOT render host/engine telemetry (RAM, swap, active model, resident turn) — that stays exclusive to `vaptctl dashboard` (`22`). | M |
| FR-TUI-03 | The console MUST connect to `state.db` in WAL mode with `PRAGMA busy_timeout = 5000` set on its connection, retrying under contention rather than failing — consistent with `DR-CONCURRENCY-03`'s existing busy-timeout pattern for concurrent CLI access. Unlike the read-only dashboard (`FR-DASHBOARD-01`), this connection is read-write, since the console inserts into `operator_command_queue`. | M |
| FR-TUI-04 | The console MUST capture keyboard-driven operator input, parse it per `FR-INTERVENE-01/02`, and persist it into `operator_command_queue`. | M |
| FR-TUI-05 | The console process MUST operate deterministically — Python string/regex parsing and database I/O only — and MUST NOT load, initialize, or query any local or remote LLM directly. | M |
| FR-TUI-06 | **(New)** The console MUST detect and reflect engagement-lifecycle state changes (the bound engagement transitioning to `PAUSED`/`ABORTED`/`COMPLETE`) and stop accepting new interventions once it is no longer `IN_PROGRESS` — mirroring `FR-DASHBOARD-03`'s state-resilience requirement for the dashboard, which this spec's original draft didn't address. | M |

## 2. FR-STREAM — Unified Live Stream & Append-Only Markdown Journal

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-STREAM-01 | The system MUST maintain an append-only Markdown execution journal at `<artifact_root>/<engagement_id>/live_audit_trail.md` (path per `DR-ARTIFACT-01`'s existing per-engagement artifact layout, not a new convention). | M |
| FR-STREAM-02 | The journal MUST record one block per pipeline transition: (a) **Tool Dispatch** (tool, target, exact argv, PID/PGID, applicable timeout tier); (b) **Output Sanitization** (signal retained vs. discarded, `novel_entities_count`, raw-artifact file reference); (c) **Model Ingestion** (role, model, prompt tokens, summarized input, any active operator directives); (d) **Model Output** (verdict, payload, completion tokens, latency, grounding status where applicable). | M |
| FR-STREAM-03 | The console's stream pane MUST show truncated previews (≤20 lines / 1,500 characters) of tool output, with the full raw artifact's path (already indexed in `artifacts_index`, `DR-SCHEMA-10`) always shown alongside — never truncating the file on disk, only the terminal preview. | M |
| FR-STREAM-04 | The journal MUST be written via an unbuffered, append-mode file handle, flushed after every block — durable across a sudden crash, consistent with this system's existing "raw artifact persists regardless of what got summarized" principle (`FR-TOOL-08`). | M |
| FR-STREAM-05 | Journal content MUST be sourced by tailing the on-disk file / re-reading indexed artifacts, never by holding raw multi-megabyte tool output in the console's own process memory — see `NFR-TUI-01`'s footprint bound. | M |

## 3. FR-INTERVENE — Asynchronous Command Ingestion, Precedence & Checkpoint Interaction

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-INTERVENE-01 | The console MUST support explicit role-directed prefixes: `@strat` (Strategist), `@op` (Operator), `@gate1` (Scope Gatekeeper, semantic tier), `@lint` (Offline Script Linter — **added**, correction #1), `@adj` (Adjudicator), `@rep` (Reporter). | M |
| FR-INTERVENE-02 | Unprefixed input MUST route via a deterministic keyword classifier: `scope`/`boundary`/`cidr`/`disallowed*` → `@gate1`; `run`/`scan`/`payload`/`exploit`/`fuzz`/`curl*` → `@op`; `pivot`/`plan`/`vector`/`rethink`/`hypothesis*` → `@strat`; `dismiss`/`confirm`/`false positive`/`waf`/`verify*` → `@adj`; `format`/`cvss`/`summary`/`remediation`/`report*` → `@rep`; `lint`/`syntax`/`script check*` → `@lint` (**added**, correction #1). | M |
| FR-INTERVENE-03 | Input matching neither a prefix nor a keyword MUST trigger an interactive role-selector dialog before the entry is enqueued. | M |
| FR-INTERVENE-04 | Queued directives MUST be persisted to `operator_command_queue` with `status = QUEUED`. | M |
| FR-INTERVENE-05 | **(Queue-order precedence, unchanged from the original spec)** Operator directives MUST NOT preempt or reorder `task_queue` itself — they are presented to the model *alongside* the next autonomous task it was already going to work on, never jumping the line. | M |
| FR-INTERVENE-06 | **(Revised — correction #2, resolves the safety-gate ambiguity)** Operator precedence is **reasoning-weight only**: when a model's active task and a queued directive for its role conflict, the model MUST weigh the operator's stated instruction more heavily than the autonomous task's own framing when deciding what to propose. This requirement governs the model's *reasoning* alone — it confers no exception, for any command that results, to `FR-COUNCIL-03a`/`06` (Tier 0 scope check), `FR-TOOL-06` (Tier 2 behavioral denylist), `FR-TOOL-06a` (opt-in-flag category validation), or `FR-TOOL-14` (rate limiting). Every one of these MUST evaluate a console-influenced command exactly as it would evaluate a purely autonomous one — there is no code path in which an operator directive changes what these deterministic checks decide. | M |
| FR-INTERVENE-06a | **(New — decision #63, amendment above)** A `task_queue` row whose `origin = 'MANUAL_OPERATOR'` (i.e. `source_command_id` traces to an operator directive whose own text explicitly and specifically named the resulting action, same specificity bar as `FR-INTERVENE-10`) MUST skip Gate 1's semantic tier (`FR-COUNCIL-04`, `Hermes-3-Llama-3.1-8B`) entirely. It MUST still pass `FR-COUNCIL-03a`'s deterministic Tier-0 scope check, `FR-TOOL-06`/`06a`, and `FR-TOOL-14` exactly as any other task would — this requirement narrows Gate 1's semantic tier only, and confers no exception anywhere else. A directive too vague for the model to lift a literal, specific command from leaves `source_command_id` unset and the task `origin = 'AUTONOMOUS_COUNCIL'`, subject to the full two-tier gate. | M |
| FR-INTERVENE-07 | Before each model invocation — Phase 4.1 Strategist, Phase 4.1 Gatekeeper, Phase 4.2 Operator, the Offline Linter's between-phase invocation (**added**, correction #1 — necessarily rarer than the other five given `FR-COUNCIL-09a`'s own invocation cadence), Phase 4.3 Adjudicator, Phase 4.3 Reporter — the orchestrator MUST fetch unconsumed directives matching that role and present them alongside the active task, per `IR-INTERVENE-01`'s template. | M |
| FR-INTERVENE-08 | Intervention text MUST be capped at 500 characters (~120 tokens), validated client-side before database insertion, to bound context-window impact (`FR-GATE-07`). | M |
| FR-INTERVENE-09 | A directive integrated into a model's context MUST transition to `status = INJECTED` with `consumed_at` and `consumed_by_invocation_id` (FK → `model_invocation_logs.invocation_id`) recorded. | M |
| FR-INTERVENE-10 | **(New — correction #3)** When an operator's raw console input **explicitly and specifically** names an action falling into one of the four Human Checkpoint action classes (`FR-CHECKPOINT-01`) — not a vague directive the model later escalates into one, only the operator's own text unambiguously requesting it — the resulting `checkpoint_events` row MUST be auto-finalized: `status = 'APPROVED'`, `approved_via = 'CONSOLE_DISPATCH'`, `approved_at` set immediately, with `rationale_shown_to_operator` still populated and echoed back to the console (e.g. the computed lockout-percentage estimate for a live-spray dispatch) so the risk information isn't lost even though the interactive pause is skipped. This bypasses **only** `FR-CHECKPOINT-03`'s live pause step. It does **not** bypass `FR-CHECKPOINT-02`'s pre-engagement opt-in-flag gate (an unset flag still produces `POLICY_REFUSED` with no checkpoint row created at all) or `FR-CHECKPOINT-05`'s anti-forensics attestation-field requirement, and it does not exempt the resulting command from Tier 0/Tier 2/rate-limiting per `FR-INTERVENE-06`. A directive the model later turns into a checkpoint-class action on its own initiative (not explicitly named by the operator) always gets the full `FR-CHECKPOINT-03` pause — this shortcut is for direct human intent only, not a general escalation path. | M |
| FR-INTERVENE-11 | **(New — correction #4)** No directive may transition to `EXPIRED` or `DISCARDED` silently. Both transitions MUST populate the new `failure_reason` column (`DR-SCHEMA-19`) with the specific cause — a Tier 0/Tier 2/opt-in-flag refusal reason if the resulting command was rejected downstream, or a lifecycle-closure reason ("target's Strategist invocation window has already closed for this target; requires a new pivot or manual re-dispatch to re-open it") if the directive's target role will not be invoked again for that target. Expiration is triggered by this lifecycle-window closure, not a fixed time-to-live. | M |

## 4. Data & Storage (revises `03`)

### DR-SCHEMA-19: `operator_command_queue` (revised from the original draft)

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
    failure_reason TEXT,  -- NEW (correction #4): required (NOT NULL enforced at the app layer,
                          -- not the schema layer, since it's conditional on status) whenever
                          -- status is 'DISCARDED' or 'EXPIRED'; NULL otherwise.
    queued_at TEXT NOT NULL,
    consumed_at TEXT,
    consumed_by_invocation_id INTEGER REFERENCES model_invocation_logs(invocation_id),
    FOREIGN KEY (engagement_id) REFERENCES engagements(engagement_id)
);

CREATE INDEX IF NOT EXISTS idx_operator_queue_lookup
ON operator_command_queue (engagement_id, target_role, status);
```

`'Linter'` added to the `target_role` CHECK constraint (correction #1). `failure_reason`
added (correction #4).

### DR-SCHEMA-18 amendment (`checkpoint_events`, defined in `03`)

`approved_via` (already `TEXT, nullable`) MAY now hold the literal value
`'CONSOLE_DISPATCH'`, alongside the existing "specific `vaptctl` invocation" values —
distinguishing a formal `approve-checkpoint` CLI approval from an auto-finalized
console-dispatch attestation (`FR-INTERVENE-10`). No new column needed; this is a new
value within the existing column's intended range.

### DR-SCHEMA-05 amendment (`task_queue`, defined in `03`) — decision #63

Two new columns: `origin` (`'AUTONOMOUS_COUNCIL'` default / `'MANUAL_OPERATOR'`) and
`source_command_id` (FK → `operator_command_queue.command_id`, nullable). Full
column definitions and the specificity condition for `MANUAL_OPERATOR` are in `03`,
not repeated here — see this document's amendment section above and `FR-INTERVENE-06a`.

### DR-SCHEMA-20: Markdown journal layout

Unchanged from the original draft — one `## [<TIMESTAMP>] EVENT: ...` block per
pipeline transition, with Tool Dispatch / Output Sanitization / Model Ingestion /
Model Output sub-sections, exactly as originally specified. See the original draft's
concrete worked example for the literal template; not repeated here since it needed
no correction.

---

## 5. Interface & Integration (revises `04`)

### IR-CLI addition (extends `13`'s `IAB-CLI`, not a new IR section)

```bash
vaptctl console [--engagement-id <id>] [--tail-lines <int>] [--no-stream]
```

Unchanged from the original draft: `--engagement-id` binds to a specific engagement
(defaults to the active `IN_PROGRESS`/`PAUSED` one); `--tail-lines` seeds the stream
view (default 100); `--no-stream` disables file-tail streaming for a static
command-entry-only mode.

### IR-INTERVENE-01: Context injection template (revised wording, unchanged structure)

```xml
<execution_context>
  <autonomous_task>
    <task_id>TASK-402</task_id>
    <objective>Enumerate hidden directories on port 443 using common web wordlists.</objective>
    <proposed_command>ffuf -u https://target.local/FUZZ -w /usr/share/wordlists/dirb/common.txt</proposed_command>
  </autonomous_task>

  <operator_interventions>
    Give the following operator guidance priority weight over the autonomous task's
    own framing when they conflict. This affects only how you reason about which
    hypothesis or approach to pursue next — it does not exempt whatever you propose
    from the scope, denylist, opt-in-flag, or rate-limit checks every other proposal
    goes through.
    - Directive [CMD-101]: "Do not scan root paths; restrict all fuzzing exclusively to /api/v2/ endpoints."
  </operator_interventions>
</execution_context>
```

The wording change from the original draft's bare "operator directives MUST take
precedence" is deliberate — it states the reasoning-weight scope explicitly in the
prompt itself, not just in this document, so a future reader of the prompt template
doesn't have to cross-reference `FR-INTERVENE-06` to know the boundary.

---

## 6. Non-Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-TUI-01 | The console process MUST NOT exceed 120 MiB resident memory — disk-backed tailing and cursor-based reads only, never full-transcript caching. | M |
| NFR-TUI-02 | Writing a journal block and enqueuing a command MUST each complete within ≤10ms under normal conditions. **Caution, not a blocking issue**: this target is in tension with `FR-STREAM-04`'s mandatory unbuffered-flush-per-event requirement under sustained load (Phase 4.2's active loop can generate several journal blocks per task) — treat this as a design goal to validate empirically at implementation time (`TP-TUI`), not an assumed-safe combination. | M |
| NFR-TUI-03 | The `Textual` render loop MUST sustain ≥20 FPS during peak tool-output streaming. | M |

---

## 7. Acceptance Criteria (extends `09`)

## TP-TUI — Interactive Console & Intervention Pipeline

| Test | Method | Pass Criteria |
|---|---|---|
| Console layout excludes host telemetry | Inspection | Launch `vaptctl console`; confirm the viewport shows only the event-stream pane and command bar — no RAM/swap/active-model header (FR-TUI-02). |
| Journal captures full record within memory bound | Test | Run an engagement producing 5,000+ tool-log lines; confirm `live_audit_trail.md` contains the complete chronological record while console RSS stays ≤120 MiB (FR-STREAM-01/02, NFR-TUI-01). |
| Offline Linter has full parity with the other 5 roles | Test | Queue a `@lint` directive ahead of a custom multi-line script's between-phase syntax check; confirm it's fetched and injected per `FR-INTERVENE-07`, the same as any other role (correction #1). |
| Operator precedence affects reasoning, never bypasses gates | Test | Queue an `@op` directive that, if followed literally, would resolve to an out-of-scope or denylisted command; confirm the Operator's resulting proposal is still refused by Gate 1/Tier 2 exactly as an equivalent autonomous proposal would be — precedence changes what the model *tries*, not what the deterministic gates *allow* (FR-INTERVENE-06). |
| Manual-operator origin skips Gate 1's semantic tier, never its deterministic tier | Test | Dispatch an explicit, specific `@op` command that is in-scope (passes `FR-COUNCIL-03a`); confirm `Hermes-3` (`FR-COUNCIL-04`) is never invoked for that task, `origin='MANUAL_OPERATOR'` and `source_command_id` is set. Repeat with an explicit, specific command that is *out of scope*; confirm `FR-COUNCIL-03a` still rejects it — same as an autonomous task, no origin-based exception (FR-INTERVENE-06a, decision #63). Repeat with a vague `@op` nudge the model expands into a specific command on its own; confirm `origin='AUTONOMOUS_COUNCIL'`, `source_command_id` is `NULL`, and the full two-tier gate runs. |
| Explicit console dispatch of a checkpoint action auto-attests, without touching the flag gate | Test | With `--allow-live-credential-spray` set, dispatch `@op spray <hostname> now` explicitly via console; confirm a `checkpoint_events` row is created and immediately finalized (`status='APPROVED'`, `approved_via='CONSOLE_DISPATCH'`) with no `PAUSED_AWAITING_CHECKPOINT` pause, and confirm the lockout-percentage rationale is still echoed to the console. Repeat with the flag unset; confirm `POLICY_REFUSED` with no `checkpoint_events` row at all (FR-INTERVENE-10, FR-CHECKPOINT-02 unaffected). |
| Model-derived (not operator-explicit) checkpoint actions still pause | Test | Queue a vague `@op` directive ("focus harder on credentials") that the Operator model then independently escalates into a live-spray proposal on its own; confirm the full `FR-CHECKPOINT-03` pause still fires — the auto-attestation shortcut does not apply here, only to the operator's own explicit, specific text (FR-INTERVENE-10). |
| No silent expiration | Test | Queue a directive for `@strat` against a target whose Phase 4.1 has already concluded; confirm it transitions to `EXPIRED` with `failure_reason` populated with the specific lifecycle-closure explanation, visible to the operator (FR-INTERVENE-11). |
| Journal/console content is unredacted, same as raw artifacts | Inspection | Trigger a tool run that discovers a secret-shaped string; confirm the journal's "Signal Retained" block shows it verbatim, matching what `tool_execution_logs`/`artifacts_index` already store — confirm this is *not* routed through `FR-COUNCIL-18`'s redaction pipeline, which remains scoped to the Reporter/report-draft step only. |
| 500-char cap enforced before insertion | Test | Submit a 501-character intervention; confirm client-side rejection with no `operator_command_queue` row created (FR-INTERVENE-08). |

---

## 8. New Dependency (for `08`)

**Textual** (the TUI framework) — not previously in this system's dependency floor;
`AC-DEPENDENCY-21` in `08` (added alongside this document).
