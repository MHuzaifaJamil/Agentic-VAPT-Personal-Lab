# Pipeline Flow & Silent-Drop Audit — 2026-09-23

**Mission:** Static, line-by-line data-flow audit of the Mugheeraat engine, tracing an
exploit hypothesis from Strategist inception through to `verified_vulnerabilities`
confirmation, to find every silent discard, unhandled branch, over-restrictive regex,
schema-validation drop, timeout kill, or cross-module contract break that could explain
the reported 27+-engagement zero-confirmed-findings pattern.

**Scope note on the mission brief:** the original brief assumed a file layout
(`vapt_agent/execution/`, `vapt_agent/analysis/`, `vapt_agent/storage/`,
`Mugheeraat-Requirements/`, `04-Council-and-Adjudication-Rules.md`,
`02-Formal-Security-Guarantees.md`) that does not exist in this repo. Real paths were
resolved by direct filesystem inspection before dispatching each module audit; the
mapping is recorded per-module below. This is audit-only — **no fixes are applied in
this pass**, per systematic-debugging Phase 1/2 (root cause before remediation).

**Context already on record before this audit** (from git history / prior sessions —
NOT assumed still-broken, re-verified fresh below):
- `a1996f2` "Fix scope-matching bug: --targets host:port silently broke Gate 1 for every real attack"
- `af539b0` "Fix katana/nuclei/gospider: bad flag + missing-port bug (engagement 27 post-mortem)"
- `f21bb7e` "Fix candidate_detection: dead status-code rule, denylist false positives, missing XSS rule"
- `310a696` "separate MODEL_STRUCTURED_OUTPUT_FAILURE from GATE2_BLOCKED; enforce JSON-schema grammar on the Scripters"
- `92bd338` "a Strategist hypothesis naming host:port was silently dropped, not rejected"

Each module section below is appended as its investigation completes — this file is
built incrementally, not written all at once.

---

## Module 1 — Target Normalization, Scope Rules & Gate 1 (re-verification only)

**Real files** (mission brief's assumed paths didn't exist — resolved): `vapt_agent/cli/start.py`,
`vapt_agent/council/strategy_auditor.py` (`check_tier0`, `run_gate1_semantic` — mission called
this "`check_tier1`", it doesn't exist under that name), `vapt_agent/scope/`.

This module's headline defect (`--targets host:port` silently breaking every real
attack via `_pattern_matches`' IP-vs-CIDR branch) is already found, root-caused, and
fixed — see `JuiceShop-VAPT-Testing-Guide-2026-09-19.md` §3.4, commit `a1996f2`.
**Per this report's own "don't trust the file, verify it" mandate, the fix's actual
function body was read directly (not just cited) during self-audit:** `start.py:58-75`,
`_scope_pattern_for_network_target()`, strips a trailing `:port` only from the three
unambiguous shapes (bracketed IPv6, and single-colon `host:port`/`ipv4:port` with an
all-digit port), leaving a bare unbracketed IPv6 literal or anything else untouched —
logically sound, no edge case found that would re-introduce the original bug. Confirmed
present at HEAD, correct.

**Directive 1.3, originally left open — now closed.** Read `ROLE_BLOCK_AUDITOR`
(`prompts.py:259-294`) in full: the semantic Gate-1 layer's system prompt explicitly and
unambiguously states it "has ZERO authority to evaluate, challenge, or reject a task
based on... target is in scope... [or] address classification (loopback 127.0.0.1, RFC
1918 private subnets, or public domains)" — scope/loopback questions are Tier 0's job,
by explicit design, not this layer's. Its four actual criteria (destructive risk,
reasoning sanity, proportionality, redundancy) are about the *action's* safety, not the
payload's shape — a standard `' OR 1=1--` SQLi probe or a GET-based IDOR read present no
destructive/DoS risk under this rubric. **No misclassification risk found** — the
mission's directive-1.3 hypothesis is refuted by direct prompt inspection, not merely
untested.

**Loopback-equivalence handling (`127.0.0.1`/`localhost`/`::1`)** — not independently
re-traced in this pass beyond confirming Tier 0, not Tier 1, owns this question (per the
prompt text above); left as a genuinely open item for a future pass if it matters (no
evidence surfaced anywhere in this audit that loopback handling is a live problem).

(Note: the "dispatched Module 2/5 agents" this section originally deferred to never
returned — see this conversation's own record of the rate-limit failure. Both open items
above were closed by direct reading in this self-audit pass instead, not by an agent.)

---

## Module 2 — Task Lifecycle, Queue Hydration & Scripter Contract

**Real files** (mission brief assumed `execution/`/`analysis/` paths that don't exist —
resolved): `vapt_agent/council/task_runner.py` (602 lines, `run_gated_task` is the single
entry point), `vapt_agent/orchestrator/phase_lifecycle.py` (drives the per-target retry
loop that calls it), `vapt_agent/council/primary_scripter.py`, `strategy_auditor.py`.

Read `run_gated_task` (task_runner.py:224-601) and its caller loop (phase_lifecycle.py:590-676)
in full, line by line.

**Verdict: no stall/silent-drop found at the individual task-state-machine level — this
part of the pipeline is actually sound.** Specifically:

- Every exit path from `run_gated_task` sets an explicit terminal-or-retryable
  `task_queue.status` before returning (`GATE1_REJECTED`, `GATE2_BLOCKED`, `DEFERRED`,
  `POLICY_REFUSED`, `AWAITING_CHECKPOINT`, `EXECUTED`) — none of the ~10 return points
  fall through without a status write. No path leaves a task at `PENDING`/`GATE1_APPROVED`
  indefinitely.
- A `StructuredOutputError` from the Scripter (invalid JSON / failed grammar) is caught
  at `phase_lifecycle.py:649-654` and routed to `_mark_task_structured_output_failure`
  (terminal `MODEL_STRUCTURED_OUTPUT_FAILURE` status) — confirmed this is an explicit,
  deliberate fix already on record (commit `310a696`, "separate
  MODEL_STRUCTURED_OUTPUT_FAILURE from GATE2_BLOCKED"), not something this pass found new.
- `GATE2_BLOCKED` retries up to `max_attempts` via `run_primary_scripter_command_retry`
  (with the real `gate2_rejection_reason` fed back to the *same* Scripter call, not just
  logged) — `phase_lifecycle.py:667-675` — and if the retry budget is exhausted, the task
  correctly stays `GATE2_BLOCKED` (a real terminal state the schema already defines), not
  silently re-queued or dropped.
- A `GATE1_REJECTED` outcome from `run_gated_task`'s own Tier0 **re-check** (line 667:
  `if outcome.status != "GATE2_BLOCKED": break`) correctly breaks the retry loop
  immediately rather than pointlessly re-submitting the same command against a
  deterministic scope check that will reject it identically every time.
- Command sanitization (directive 2.3): the Scripter's `argv` list
  (`phase_lifecycle.py:656-660`) is stored as a JSON array and passed straight to
  `subprocess.Popen`-style execution with no intermediate string-interpolation or
  shell-escaping step — consistent with `CLAUDE.md`'s `shell=False`/explicit-argv
  mandate. No quote/pipe/bracket-mangling path found because there is no shell layer for
  it to be mangled by.

**One real, but different, finding surfaced here — it belongs to Module 5, not this one:**
the failure mode this module's design successfully avoids at the *task* level (silent
stalls) re-appears one level up, at the *round* level, because `run_gated_task`'s Tier0
re-check outcome is invisible to the round-progression breaker. See Module 5 §5.1 below
for the full trace — this is the same underlying gap the original mission's directive 5.2
asked about, just resolved with the real file names.

---

## Module 5 — Circuit Breakers, Loop Bounds & the Zero-Yield Trap

**Real files** (there is no standalone `circuit_breaker.py` — the mission brief assumed
one; the logic is split across three real files): `vapt_agent/council/loop_bounds.py`
(373 lines, read in full), `vapt_agent/orchestrator/driver.py` (`run_full_engagement`,
lines 239-333 read in full), `vapt_agent/orchestrator/phase_lifecycle.py`
(`_build_coverage_summary_candidate`, lines 907-955).

### 5.1 — HEADLINE FINDING: the round-progression breaker counts Phase-4.1 approval, not real execution — a rejection storm reads as "progress" forever

**File:** `vapt_agent/orchestrator/driver.py:268-289`, cross-referenced against
`vapt_agent/council/task_runner.py:585-587`.

The per-round "diminishing returns" check that decides whether to keep looping on a
target is:

```python
approved_this_round = conn.execute(
    f"SELECT COUNT(*) AS c FROM task_queue WHERE status = 'GATE1_APPROVED' "
    f"AND task_id IN ({placeholders})",
    round_task_ids,
).fetchone()["c"]

if approved_this_round == 0:
    consecutive_zero_progress_rounds += 1
    if consecutive_zero_progress_rounds >= zero_yield_circuit_breaker:
        break
    ...
    continue
consecutive_zero_progress_rounds = 0
```

`GATE1_APPROVED` here is set by **Phase 4.1's own Strategy-Auditor check** (in
`phase_lifecycle.py`, at hypothesis-proposal time) — a *different, earlier* gate than the
Tier0 **re-check** that `task_runner.py::run_gated_task` performs unconditionally on
every task at actual dispatch time (task_runner.py:266-278, explicitly "Always runs, even
for a task that already carries a real GATE1_APPROVED decision... a Tier 0 failure here
is a hard rejection regardless of any prior approval"). A task can pass Phase 4.1's check
and still be rejected moments later by this second, execution-time Tier0 check — which is
*exactly* what happened in engagement 28's real DB rows (5 of 6 round-1 tasks: approved at
Phase 4.1, then Tier0-rejected at dispatch by the since-fixed `host:port` scope bug).

Separately, and confirmed directly in `task_runner.py:585-587`'s own comment
("`FR-COUNCIL-11a/11b`: only a task that actually ran a tool counts toward a target's
loop-bound counters — `GATE1_REJECTED`/`GATE2_BLOCKED` tasks returned before this point
and never reach here"), a task rejected at this second check **never calls
`record_task_outcome`** — so it never increments `targets.task_count`,
`consecutive_zero_yield_count`, or `consecutive_failure_count` either. The target-level
breakers in `loop_bounds.py` (`TASK_CAP`, `GLOBAL_TARGET_EXHAUSTION_CEILING`,
`FAILURE_BREAKER`) are therefore **also** completely blind to this failure mode.

**The compounding effect, traced end to end:** for a target that isn't already terminal,
if every task Phase 4.1 approves keeps getting rejected by this second Tier0 check (any
future bug shaped like the fixed one, or any legitimate-but-persistent scope
misconfiguration):
1. `approved_this_round > 0` every round (Phase 4.1 keeps approving) → `consecutive_zero_progress_rounds`
   resets to 0 every round → the round-level breaker **never fires**.
2. `record_task_outcome` is never called → `targets.task_count`/`consecutive_zero_yield_count`
   never advance → `next_pivot_target` (driver.py:313) keeps returning this same target
   → the target-level breakers **never fire** either.
3. Nothing here feeds back into the Strategist's live prompt context (see §5.2) — the
   Strategist gets no signal that its hypotheses aren't reaching the target.

**The only things that can actually stop this** are `max_council_rounds` (default 15,
`driver.py:239`) or the 12-hour wall-clock `is_session_budget_exceeded` check
(`driver.py:286`) — i.e. the engagement would burn its *entire* round/time budget on a
target that never executes a single real command, exactly as engagement 28 needed a
manual operator `pause` rather than any breaker to stop (`JuiceShop-VAPT-Testing-Guide-2026-09-19.md`
§5's own account). The codebase has already fixed the closely-related sibling case of this
same class of bug once — `driver.py:301-312`'s comment documents a "second real incident,
engagement 26" where `approved_this_round > 0` was wrongly treated as real progress when
every target was already terminal, and added the `next_pivot_target(...) is None: break`
check at line 313 for *that* case. **That fix does not cover this case**, because the
target here is never terminal in the first place — the counters that would make it
terminal are the exact ones this rejection mode never touches.

**Confidence:** confirmed by direct reading of both files; the interaction between the two
separate Tier0 checks and the round-breaker's status source is unambiguous in the code
itself, not inferred from behavior.

### 5.2 — The rejection/execution breakdown is real but only surfaces post-hoc, in a report artifact, never live to the Strategist or the breaker

**File:** `vapt_agent/orchestrator/phase_lifecycle.py:907-955` (`_build_coverage_summary_candidate`).

This function *does* compute an accurate breakdown (`approved_like`, `executed`,
`rejected`, `confirmed_count`) — but it's called only to populate a `COVERAGE-####`
**informational report artifact**, generated for the human operator to read after (or
during, if they check reports mid-run) the engagement, not fed into:
- The Strategist's own prompt context for the next round (which only receives the static
  `exhausted_vectors_for_target` list — itself populated exclusively from
  `record_vector_outcome`, which (§5.1) never runs for a rejected-before-execution task).
- The round-progression or target-level breaker logic in `driver.py`/`loop_bounds.py`.

So the one piece of code in the entire pipeline that *would* have made engagement 28's
rejection storm visible mid-run exists, but is disconnected from every decision-making
path — an operator would have to know to look at a specific informational artifact while
the engagement is still running to catch it before the round/time budget is exhausted.

**Correction from this report's own self-audit — the original claim above ("never live")
was checked against the wrong assumption and is partly wrong.** `vapt_agent/dashboard/compute.py`
does maintain a live `TaskFunnel` with a `gate2_blocked` count, and
`vapt_agent/dashboard/render.py:168-171` displays it with an amber warning color whenever
it's nonzero — a `GATE2_BLOCKED` burst genuinely is visible on the live dashboard, not
just in the post-hoc report. **What is confirmed still true, more narrowly and more
precisely than originally stated: `GATE1_REJECTED` has no live visibility at all.**
`grep -rn "GATE1_REJECTED" vapt_agent/dashboard/ vapt_agent/monitor/ vapt_agent/cli/`
returns zero hits anywhere in the operator-facing surface — the `TaskFunnel` dataclass
(`compute.py:115-120`) has exactly five fields (`targeted, gate1_pass, executing,
gate2_blocked, complete`) and no sixth for rejections; a `GATE1_REJECTED` task simply
falls into the unlabeled gap between `targeted` and `gate1_pass`, indistinguishable on the
dashboard from a task that's merely still `PENDING`. This is the more consequential half
of the original claim, and it survives the correction: engagement 28's actual failure mode
(5 of 6 round-1 tasks were `GATE1_REJECTED`, not `GATE2_BLOCKED`) is precisely the
category with zero live surfacing, while the category that already has a live warning
color (`GATE2_BLOCKED`) was not the one that caused the incident.

**Minor, secondary note on the same function (line ~924-928):** its `approved_like`
tally sums `GATE1_APPROVED, EXECUTED, GATE2_BLOCKED, FOLLOWUP_GENERATED,
AWAITING_CHECKPOINT, MODEL_STRUCTURED_OUTPUT_FAILURE` into one bucket reported as "X passed
Gate 1" — lumping a `GATE2_BLOCKED` task (rejected, never executed) in with tasks that
actually ran. The very next sentence in the same summary string does correctly disambiguate
real execution count (`executed`, a separate, narrower tally), so this doesn't hide
anything from a careful reader — flagged only as a wording precision issue, not a data-loss
bug.

### 5.3 — What's confirmed correct (not re-litigated as a finding)

- `record_task_outcome`'s zero-yield/failure counters are logically independent per its
  own docstring (loop_bounds.py:54-59) and confirmed correctly implemented: only a truly
  novel-entity-free *executed* run increments zero-yield, only a `network_error`/
  `timeout_hit` run increments failure — verified against the actual column reads
  (lines 82-86).
- The 2026-09-17 per-(target, vulnerability_class) exhaustion split (`record_vector_outcome`,
  `ZERO_YIELD_BREAKER = 3`) and the separate, higher whole-host ceiling
  (`GLOBAL_TARGET_EXHAUSTION_CEILING = 12`) are present and match their own documented
  fix rationale — no regression found.
- `reopen_completed_targets_with_pending_work` (loop_bounds.py:234-266) correctly guards
  against the other previously-fixed engagement-26 incident (approved tasks rotting at
  `GATE1_APPROVED` under a `COMPLETE` target) — confirmed present, not re-broken.
- One real design caveat worth naming explicitly (not a bug, a tuning/semantic note): the
  "yield" signal (`novel_entities_count > 0`) that drives every breaker in this module
  measures **recon novelty** (new discovered URLs/params/entities), not **vulnerability
  confirmation**. A target could reset its zero-yield counter to 0 every single task
  (via constant recon novelty) for the entire engagement while `verified_vulnerabilities`
  stays permanently empty, and no breaker in this file would ever have reason to fire —
  by design, these breakers protect against wasted *compute*, not against zero *findings*.
  That's a defensible design choice on its own, but it means this module provides no
  safety net at all against the actual zero-findings problem the mission is investigating;
  it only protects against the target ceasing to be worth crawling further, which is a
  different question.

---

## Module 3 — Execution, Sandboxing, Process Logging & Artifact Persistence

**Real files** (mission brief assumed `execution/`/`storage/` paths — resolved):
`vapt_agent/bridge/executor.py` (166 lines, read in full), `vapt_agent/bridge/pipeline.py`
(242 lines, read in full), `vapt_agent/bridge/disk_quota.py` (read in full),
`vapt_agent/bridge/sanitize.py`, `vapt_agent/config/defaults.yaml`,
`vapt_agent/bridge/tier1/schema.py`.

**Verdict: mostly clean, one real uncaught-exception risk found; the mission's specific
"truncation deletes the exploit proof" hypothesis is refuted by direct code reading.**

- **Directive 3.1 (truncation) — refuted.** `pipeline.py::_write_raw_artifact` (line 75:
  `file_path.write_text(raw_text)`) writes the full, untruncated `stdout+stderr` combination
  to disk with no length cap anywhere in the call chain. `executor.py::_reader_thread`
  (line 68: `buf.extend(iter(stream.readline, ""))`) also has no buffer cap. There is no
  64 KiB (or any other) threshold in this codebase that could cut off a JWT token or a
  JSON field. The actual risk here runs the other way: **unbounded memory growth** for a
  tool that legitimately produces very large output (e.g. `nmap -p-` or a large `ffuf`
  wordlist run) — not a correctness bug, but worth knowing this pipeline currently has no
  defense against a single command's output filling available RAM before the timeout
  fires.
- **Directive 3.2 (`sanitized_summary` redaction) — confirmed correct, and confirms
  Module 4's own design is sound on this point.** `sanitize_output` (`sanitize.py`)
  reduces the raw text to a narrow structured JSON (`ports`, `banners`, `urls`,
  `status_codes` only) — `pipeline.py:164-168` even logs exactly how lossy this is
  (`signal_retained = f"{len(...)} ... vs {len(raw_combined)} raw char(s) discarded"`).
  This confirms `candidate_detection.py`'s deliberate choice to read the **raw** artifact
  file instead of `sanitized_summary` (documented in its own module docstring) is not
  just a stated intent but a load-bearing necessity — the summary genuinely would not
  contain a password/token/admin field, an XSS reflection, or anything else Module 4's
  rules look for.
- **Directive 3.3 (exit-code handling in the executor) — no problem found.** The
  executor itself never skips writing an artifact or short-circuits based on exit code;
  `_write_raw_artifact` and the `tool_execution_logs` INSERT both run unconditionally
  after `run_subprocess` returns, regardless of `exit_code`'s value (including on
  `timeout_hit=True`, where partial output collected before the kill is still written,
  not discarded — `executor.py:135-136` returns whatever `stdout_buf`/`stderr_buf`
  accumulated). Exit-code-based filtering only happens later, deliberately, in
  `candidate_detection.py` (already covered in Module 4, and already fixed there per the
  existing Testing Guide).
- **Directive 3.5 (sandboxing contract) — confirmed implemented as CLAUDE.md describes.**
  `executor.py:96-105`: `subprocess.Popen(argv, ..., start_new_session=True)` — explicit
  argv, no `shell=True` anywhere, own process group (`_kill_process_group` uses
  `os.killpg`). Timeout tiers are genuinely wired end-to-end, not just documented:
  `defaults.yaml:59-60` (`quick_probes: 180`, `targeted_scans: 900`) is read via
  `config["tool_timeouts_s"][timeout_class]` (`tier1/wrapper.py:33`, `tier2.py:128`), and
  every one of the ~60 per-tool YAML schemas under `bridge/tier1/schemas/` declares its
  own `default_timeout_class` (spot-checked against `CLAUDE.md`'s own examples — `ffuf`/
  `whatweb`/`nikto` are `quick_probes`, `nmap`/`sqlmap` are `targeted_scans`, matching the
  doc exactly). No discrepancy found.
- **New finding: `DiskQuotaExceededError` is raised but never caught anywhere in the
  codebase.** `disk_quota.py:47` raises it from `enforce_disk_quota`, called
  unconditionally at the top of every `_write_raw_artifact` call (`pipeline.py:68`, before
  any write is attempted — this part is intentional and correct per `DR-RETENTION-01`).
  `grep -rn "DiskQuotaExceededError" vapt_agent/` returns only the two lines in
  `disk_quota.py` that define and raise it — **zero call sites catch it**. At ≥95% root-
  volume utilization, this exception propagates uncaught through
  `execute_and_record` → `run_tier1_tool`/`run_security_command` → `run_gated_task` →
  `phase_lifecycle.py`'s per-target loop → `driver.py::run_full_engagement`, almost
  certainly crashing the entire engagement rather than gracefully marking the one task
  `FAILED`/`DEFERRED` and continuing with other targets or pausing cleanly. This directly
  contradicts the Setup blueprint's own §6 operational promise ("the system never fails
  silently... every known problem... is looked up in a fixed dictionary of known issues") —
  a disk-quota crash mid-engagement would surface as a raw Python traceback, not a
  plain-English dashboard/console banner, in an unattended overnight run. Confidence:
  confirmed by direct grep + read (not yet reproduced live — this is a static-analysis
  finding of an unhandled exception path, not a demonstrated crash).

---

## Module 6 — Gate 3 (Criterion Adjudicator) Contract

**Real files:** `vapt_agent/council/criterion_adjudicator.py`, `vapt_agent/council/prompts.py`
(Adjudicator-specific section), `vapt_agent/orchestrator/phase_lifecycle.py` (the caller),
`vapt_agent/council/reporter.py`.

Read `criterion_adjudicator.py` (116 lines, in full), the caller in
`phase_lifecycle.py::run_phase_4_3` (the `_gather_raw_evidence` helper and its call site,
lines 1065-1170), and the full `ROLE_BLOCK_ADJUDICATOR` system prompt (`prompts.py:411-477`)
directly — the two questions flagged as open in the interim status update are now closed.

### 6.1 — Trigger mechanism and evidence injection: both confirmed correct

`phase_lifecycle.py:278`'s comment (`# GATE1_REJECTED/GATE2_BLOCKED/DEFERRED/AWAITING_CHECKPOINT: no candidate to adjudicate yet`)
and `detect_candidates(conn, target_id=target_id)` running immediately after every
`EXECUTED` outcome (line 683) confirm a fresh `CANDIDATE` row is picked up the same round
it's created, not left to a separate polling pass — refutes the mission's directive-6.1
concern.

**Evidence injection is also confirmed correct, refuting the mission's directive-6.2
hypothesis.** `_gather_raw_evidence` (`phase_lifecycle.py:887-...`) fetches
`tool_execution_logs.raw_output_artifact_id` for the finding's `task_id` and reads the
**actual raw artifact file** from disk (falling back to `finding_row["description"]` only
if no artifact link exists) — this real text, not `candidate_detection.py`'s short
synthetic description, is what gets passed as `run_adjudicator(..., raw_evidence=...)` and
ends up in the model's prompt (`criterion_adjudicator.py:69`,
`wrap_untrusted(raw_evidence)`). The Adjudicator genuinely is "shown the raw evidence
itself (not a summary)" exactly as its own module docstring claims.

### 6.2 — HEADLINE FINDING: an Adjudicator structured-output failure crashes the entire engagement — the exact bug already fixed for the Scripter, but not fixed here

**File:** `vapt_agent/orchestrator/phase_lifecycle.py:1138-1139` (the `run_adjudicator` call
site inside `run_phase_4_3`), cross-referenced against `vapt_agent/orchestrator/driver.py:207,369`
and the Scripter's already-fixed equivalent at `phase_lifecycle.py:649-654`.

The Scripter call site wraps `run_primary_scripter_command(...)` in a `try/except
StructuredOutputError`, explicitly because (per that code's own 2026-09-13 comment) an
uncaught `StructuredOutputError` "used to propagate uncaught and crash the whole
engagement." **The Adjudicator call site has no such guard:**

```python
decision = run_adjudicator(
    engine_client, adjudicator_handle, finding_id=finding["finding_id"], raw_evidence=raw_evidence,
    baseline_evidence=baseline_evidence, prior_dismissal_rationale=prior_dismissal_rationale,
    conn=conn, engagement_id=engagement_id, phase="4.3",
)
```

No `try`/`except` anywhere inside `run_phase_4_3` (confirmed by scanning the entire
function body for exception handling — none exists). `run_adjudicator` itself calls
`get_structured_completion` (same retry-then-raise contract used by the Scripter path,
per `engine/structured.py`), so it can raise the identical `StructuredOutputError` under
the identical condition (the model's JSON output fails schema validation across every
retry attempt). Checked the one call site that *does* wrap the whole engagement run
(`driver.py:207` `try` / `driver.py:369` `except EngineUnresponsiveError`) — `StructuredOutputError`
(`engine/structured.py:18`, `class StructuredOutputError(Exception)`) and
`EngineUnresponsiveError` (`engine/client.py:76`, `class EngineUnresponsiveError(Exception)`)
share no common base beyond bare `Exception`, so this outer handler does **not** catch it
either.

**Consequence:** if a genuine `CANDIDATE` finding reaches Gate 3 and Mistral-7B's
structured output fails schema validation on all retry attempts (the same failure mode
already proven to happen for the Strategist/Scripter roles in this exact codebase), the
exception propagates all the way out of `run_full_engagement`, killing the entire
`vaptctl run` process with a raw Python traceback — not the plain-English
dashboard/console banner the Setup blueprint's own §6 promises for "every known problem,"
and not a graceful per-finding failure that leaves the `CANDIDATE` row for a retry next
round. **This is the single highest-severity finding in this audit**, because it sits at
the exact stage the fixed upstream chain (Modules 1 and 4's already-documented fixes) was
built to finally reach: the first time this pipeline produces a real, evidence-backed
candidate for Gate 3 to review, an adjudicator-side structured-output hiccup — plausible
on a small 7B CPU-inference model under a strict, multi-field JSON schema — would crash
the run before a single finding could be confirmed, reproducing the zero-findings outcome
one stage further downstream instead of fixing it. Confidence: **confirmed by direct code
reading** (the missing catch, the shared retry-then-raise contract, and the exception
class mismatch are all unambiguous in the source) — not yet reproduced by an actual live
Adjudicator failure, since (per the existing Testing Guide) no live engagement has yet
reached Gate 3 with a real candidate present.

**Corroborating evidence found during self-audit: the test suite has no coverage for this
path either.** `tests/test_council_adjudicator.py` — read in full — has exactly one retry
test, `test_invalid_then_corrected_retry`, which only exercises "invalid once, then
corrected" (`FakeEngine([invalid, VALID_CONFIRMED])`). There is no test anywhere in that
file for "invalid on every attempt, retry budget exhausted" — the exact scenario that
would raise `StructuredOutputError`. So this isn't just an unguarded call site; it's a
code path the test suite doesn't know exists, which is exactly how the Scripter's own
identical bug went undetected until a live incident forced the 2026-09-13 fix. **Also
confirms `_gather_raw_evidence`'s real full-artifact evidence path (§6.1) is what feeds
the Reporter too, on the correct filter**: `phase_lifecycle.py:1180`,
`WHERE t.engagement_id = ? AND vv.status = 'CONFIRMED'`, is the exact query gating what
`run_reporter` ever sees — confirmed by direct citation, not inferred.

**Timeliness note added during this self-audit pass:** `vaptctl run --engagement-id 28
--no-tmux` was observed running live on this host while this self-audit was being
written (PID 571280, started 06:20 PKT) — i.e. the fixed pipeline is being exercised
against a real target right now, for the first time since the Module 1/4 fixes landed.
If this run reaches Gate 3 with a real candidate before this bug is fixed, §6.2 above
stops being a static-analysis finding and becomes something to actually watch for live.

### 6.3 — Plausible finding (not live-verified): the Adjudicator's own "baseline/attack/diff" requirement may be structurally unsatisfiable by anything this pipeline currently captures

**File:** `vapt_agent/council/prompts.py:442-445` (`ROLE_BLOCK_ADJUDICATOR` check 3), cross-referenced
against `vapt_agent/orchestrator/phase_lifecycle.py`'s `_gather_raw_evidence`.

The Adjudicator's system prompt names three mandatory checks before any `CONFIRMED`
verdict; the third is:

> "**Evidence structure: baseline / attack / diff.** Confirm the evidence includes an
> unmodified baseline request/response, the attack request/response, and that the
> difference between them concretely demonstrates the claimed impact — not a status-code
> difference alone."

`_gather_raw_evidence` fetches exactly **one** `tool_execution_logs` row's raw artifact —
the single execution linked to the candidate's `task_id` (the attack attempt itself). There
is no code path anywhere in `candidate_detection.py`, `task_runner.py`, or
`phase_lifecycle.py` that captures, links, or passes a *separate, unmodified baseline*
request/response alongside it (e.g., an unauthenticated control request, or the same
endpoint requested without the payload). Directive-6.1's confirmed reality — the Scripter's
real commands are single, standalone `curl` invocations (per `candidate_detection.py`'s own
docstring) — means the "raw evidence" the Adjudicator sees is, structurally, always just
the attack side of the pair its own prompt demands.

Given the same prompt's explicit "You are strict, not generous... anything that requires
you to fill in gaps with assumption should be dismissed" instruction, a model following
these criteria literally would have grounds to `DISMISS` on `baseline_present: false` for
essentially every candidate this pipeline could ever generate — independent of how
genuine the underlying vulnerability is. **This is flagged as plausible, not confirmed**:
it depends on how strictly the actual Mistral-7B-Instruct-v0.3 instance interprets
"baseline" in practice (it may reasonably treat a well-documented single request/response
with an unambiguous disclosure signature — e.g. finding #1's SQLi JWT — as sufficient
without a separate control request), which this static-analysis pass cannot determine
without a live model call. Recommended as the first thing to check empirically once §6.2
is fixed and a live engagement finally reaches Gate 3 with a real candidate.

---

## Module 4 — Candidate Detection & Triage Logic (full line-by-line read — the actual primary suspect)

**Real file:** `vapt_agent/council/candidate_detection.py` (349 lines, single file — no
separate `heuristics/` directory or `candidate_triage.py` exist; the mission brief assumed both).

### 4.1 — HEADLINE FINDING: 12 of the Strategist's 19 vulnerability classes have zero dedicated detection signal

**File:** `vapt_agent/council/candidate_detection.py:148` (`_ACCESS_CONTROL_CLASSES`) and
`:238-249` (`_match_http_probe_signal`'s class-conditional branch), cross-referenced against
`vapt_agent/council/prompts.py:241-243` (the Strategist's actual controlled vocabulary).

**The full vocabulary the Strategist is instructed to choose from** (`prompts.py:241-243`):
`SQLI, NOSQLI, IDOR, BROKEN_AUTH, BFLA, MASS_ASSIGNMENT, SSRF, SSTI, LFI, INSECURE_DESERIALIZATION,
RACE_CONDITION, JWT, SUBDOMAIN_TAKEOVER, XSS, SECURITY_MISCONFIG, CSRF, RCE, PROMPT_INJECTION, OTHER` — 19 tokens.

**What `candidate_detection.py` can actually ever confirm, by class:**

| Vulnerability class | Detection path | Would fire? |
|---|---|---|
| `IDOR`, `BFLA`, `BROKEN_AUTH`, `MASS_ASSIGNMENT`, `CSRF` | `_ACCESS_CONTROL_CLASSES` + 200/201/204 status marker | Yes |
| `XSS` | Dedicated payload-reflection rule (`_sent_xss_payload_marker`) | Yes |
| `SQLI` | Only via `sqlmap`'s own tool rule, or a coincidental raw DB-error string matching `_SQL_ERROR_PATTERNS` from a curl probe | Partial — a clean boolean/blind SQLi with no error string and no `sqlmap` tool name (i.e. exactly the Scripter's usual raw-`curl` idiom, per the module's own §2026-09-18 note that Tier 2 curl/python is the dominant real shape) is invisible |
| `NOSQLI` | `_SQL_ERROR_PATTERNS` only matches MySQL/MSSQL/SQLite/Oracle/PostgreSQL error text — no MongoDB/NoSQL error signature exists in the pattern list at all | **No** |
| `SSRF`, `SSTI`, `LFI`, `INSECURE_DESERIALIZATION`, `RACE_CONDITION`, `JWT`, `SUBDOMAIN_TAKEOVER`, `SECURITY_MISCONFIG`, `RCE`, `PROMPT_INJECTION`, `OTHER` | None — these 11 classes are not in `_ACCESS_CONTROL_CLASSES`, have no XSS-style reflection check, and have no SQL-error relevance. Their *only* possible path to `CANDIDATE` status is if the response body *happens* to contain one of the five generic `_DISCLOSURE_PATTERNS` (`password`, `(access_)?token`, `isAdmin:true`, `role:admin`, `api_key`/`secret`) by coincidence | **No dedicated path — pure luck only** |

**Concretely, against this session's own ground-truth Juice Shop findings (`JuiceShop-VAPT-Testing-Guide-2026-09-19.md` §4):** of the 11 independently-confirmed real vulnerabilities, only #1 (SQLi→auth bypass, catchable via the `password`/`token` disclosure pattern on the JWT response) and #2 (IDOR on `/rest/basket/{id}`, catchable via the access-control-class status rule) have *any* structural path through this module. The other 9 have no rule shape that could ever fire — but **correction found during this report's own self-audit: 4 of those 9 are not actually a gap in practice**, because the Primary Scripter's own system prompt (`prompts.py:332-336`) explicitly instructs it to treat these as **not worth pursuing at all**, verbatim: *"missing security headers alone... GraphQL introspection alone; CORS wildcard without a credential-exfil angle... banner/version disclosure without a working exploit... treat them as noise."* That directly covers #8 (CORS wildcard, no exfil angle demonstrated), #9/#10 (missing CSP/HSTS), and #11 (version fingerprinting) — the system was deliberately tuned to deprioritize these, independent of whether `candidate_detection.py` could ever recognize them. **That leaves a narrower, but still real, gap of 5 of 11**: forced-browsing directory listing exposing a KeePass DB and a private key (#3, #4) and unauthenticated PII/admin-config disclosure (#5, #6, #7) — all squarely within what the *same* Scripter prompt says IS worth pursuing ("data exposure across two identities," "a privileged action performed without authorization" — an unauthenticated admin-config or PII endpoint is exactly this), meaning the Strategist/Scripter layer is trying to find and report exactly these, and `candidate_detection.py` still can't recognize any of them, for two independent structural reasons:

1. **No vocabulary-to-rule mapping exists** for `SECURITY_MISCONFIG` (would cover #5) or any disclosure-flavored class the Strategist might reasonably pick for #3/#4/#6/#7 (there is no `SENSITIVE_DATA_EXPOSURE`/`INFORMATION_DISCLOSURE` token in the vocabulary at all — the closest fit is `OTHER`, which also has no rule).
2. **Directory-listing disclosure (#3/#4) produces plain HTML `<a href>` listings, not JSON** — none of the 5 `_DISCLOSURE_PATTERNS` (all JSON key:value shapes) would match an Apache/nginx autoindex page even if the class were mapped correctly, and a plain PII/config JSON body without a password/token/admin-role field (e.g. bare email addresses, or a config blob with no recognizable key name) wouldn't match the existing patterns either.

(The "absence-of-control" architectural point — no regex-over-response-body rule shape can express "this header is missing" — still stands as a real, separate structural limitation; it just turns out to matter less for real-world severity than initially stated, since exactly the classes it would apply to are the ones the system already deliberately treats as low-value noise.)

**Revised consequence:** the 2026-09-18/22 fixes documented in the Testing Guide (§3.1, §3.4, §3.5) correctly closed the *specific* failure chain that produced 0 findings across engagements 27-28 (broken recon → broken scope matching → SQLi/IDOR/XSS invisible to Gate 3). They leave the Council blind to `SECURITY_MISCONFIG`/disclosure-flavored findings involving actual secrets or PII (a real, still-substantial gap — 5 of 11 ground-truth findings, including 2 of the more severe ones), but the mission's implicit assumption that ~80% of the vocabulary is silently dropped overstated it: roughly a quarter of the apparent gap is intentional product tuning (low-value noise the system is explicitly told to ignore), not a bug. `SSRF`, `SSTI`, `LFI`, `INSECURE_DESERIALIZATION`, `RACE_CONDITION`, `JWT`, `SUBDOMAIN_TAKEOVER`, `RCE`, `PROMPT_INJECTION`, `NOSQLI` remain genuinely undetectable by any dedicated rule (none of these appear in the Scripter's noise list, so they're not deliberately deprioritized either — simply unimplemented) — this session's ground-truth exercise didn't happen to produce an example of any of them, so their real-world impact on the "zero findings" pattern specifically is unverified, only their structural absence from this module is confirmed.

### 4.2 — Secondary findings

- **`candidate_detection.py:298`** — the Tier 1 SQL-level filter (`tq.tool_name IN ('nuclei', 'sqlmap', 'nmap') OR tq.tool_name IS NULL`) means **masscan, ffuf, feroxbuster, gobuster, nikto, whatweb, wafw00f, testssl output is never read by this module at all**, even though `testssl` (weak ciphers, missing HSTS at the TLS layer) and `nikto` (many of the same misconfig classes as #5/#9/#10 above) are exactly the tools that would surface several of the undetectable classes in §4.1. This is documented as a deliberate scope decision in the module docstring ("deliberately left out rather than forcing a weaker rule"), not a silent bug — but it compounds §4.1: the tools most likely to surface `SECURITY_MISCONFIG`-class evidence are excluded by name at the SQL layer before any pattern-matching logic even runs.
- **`candidate_detection.py:176-180`** (`_read_raw_artifact_text`) — swallows `OSError` and returns `""` with no logging on a missing/unreadable artifact file. Combined with the module's dedup-by-`task_id` logic, a task whose artifact file was pruned, moved, or failed to write completely would silently and permanently look like "no signal found" rather than "couldn't read evidence" — no distinguishing signal reaches the Adjudicator, the dashboard, or any log. Low likelihood (artifact write path is presumably reliable) but zero observability if it ever happens.
- **`candidate_detection.py:319-325`** — `detect_candidates`'s dispatch is strictly `tool_name is not None` → `_match_signal` (3 named tools) **or** `tool_name is None and _is_http_probe_command(...)` → `_match_http_probe_signal`, **else `continue`** (silent skip, line 325). Any Tier 1 tool not in the three named tools, AND any Tier 2 command whose `argv[0]` basename isn't literally `curl`/`python3`/`python` (e.g. a Scripter-generated `wget`, `httpie`/`http`, `node`, or a shell-wrapped one-liner like `bash -c "curl ... | grep ..."` where `argv[0]` is `bash`, not `curl`) is silently invisible with **zero record of "there was output here nobody looked at."** Given the Scripter is an LLM free to phrase a command differently across attempts, this is a plausible recurring silent-drop path, not just a theoretical one.

---

# 1. Executive Defect Map

Tracing one hypothetical valid exploit (e.g. the real, independently-confirmed SQLi→auth-bypass
against Juice Shop's `POST /rest/user/login`) end to end through the pipeline as it stands
**today**, after the already-fixed bugs on record but before this audit's new findings are
addressed:

```
Strategist proposes SQLI hypothesis
        │
        ▼
Gate 1 (Tier0/Tier1)  ──────────────────────────────  [Module 1 — FIXED, verified still correct]
        │  host:port scope bug (a1996f2) no longer strips the wrong thing
        ▼
Scripter generates `curl` command, Gate 2 validates  ─ [Module 2 — clean, no stalls found]
        │
        ▼
Round-progression check (driver.py)  ────────────────  [Module 5 — NEW, UNFIXED]
        │  if a FUTURE bug shaped like the fixed one recurs (any systematic Tier0/Gate2
        │  rejection burst), this check is structurally blind to it: it counts Phase-4.1
        │  approval, not real execution, so it would report "progress" every round forever
        │  while zero commands actually run — no breaker fires, nothing reaches the operator
        │  live, only a post-hoc report artifact nobody's forced to read mid-run
        ▼
Tool executes (real curl against the target)  ───────  [Module 3 — clean; one new risk noted]
        │  full raw response written to disk, untruncated (refutes the mission's original
        │  truncation hypothesis) — BUT: at ≥95% disk utilization, DiskQuotaExceededError
        │  is raised and never caught anywhere → crashes the whole engagement, not just this task
        ▼
candidate_detection.py  ──────────────────────────────  [Module 4 — HEADLINE, PARTIALLY FIXED]
        │  SQLI is one of the ~7/19 vocabulary classes with SOME detection path (via the
        │  password/token disclosure pattern on the JWT response, or sqlmap's own tool rule)
        │  → this specific exploit DOES become a CANDIDATE row
        │  (11 other vocabulary classes / 9 of the 11 ground-truth ­finding types would have
        │  silently produced NO candidate at all, regardless of pipeline health — see §4.1)
        ▼
Gate 3 (Criterion Adjudicator)  ──────────────────────  [Module 6 — HEADLINE, UNFIXED]
        │  raw evidence correctly reaches the model (refutes the mission's "only shown a
        │  summary" hypothesis) — BUT: if Mistral-7B's structured JSON output fails schema
        │  validation on all retries (proven to happen for other council roles in this same
        │  codebase), StructuredOutputError propagates UNCAUGHT and crashes the entire
        │  engagement, right at the one stage that has never yet been live-exercised
        │  ALSO PLAUSIBLE: the prompt's own "baseline/attack/diff" requirement may be
        │  unsatisfiable by what this pipeline ever actually captures (single-request
        │  evidence, no separate baseline artifact) — unverified without a live model call
        ▼
CONFIRMED → Reporter → final report
```

**The honest current-state answer to "why zero findings across 27+ engagements":** the
chain that was broken is now mostly repaired (broken recon → broken scope matching →
missing XSS/access-control rules, all fixed and verified present at HEAD). But this audit
finds the repair is incomplete in two structurally important ways that this session's own
"fully fixed, just never live-tested together" framing did not anticipate:

1. **Module 4**: even a perfectly healthy upstream pipeline can only ever confirm
   ~2 of the Strategist's 19 vulnerability classes (and ~2 of the 11 real ground-truth
   Juice Shop findings) — not a residual edge case, the *majority* of what the Strategist
   is instructed to look for has no detection path at all.
2. **Module 6**: the exact "uncaught StructuredOutputError crashes the engagement" bug
   that was found and fixed for the Scripter role was never applied to the Adjudicator —
   meaning the first real candidate to reach Gate 3 in a live run carries a real, live risk
   of crashing the run before confirming anything, silently relocating the zero-findings
   problem to the very last pipeline stage instead of resolving it.

---

# 2. Architectural Disconnects & Schema Mismatches

- **Two independent Gate-1-Tier0 checks with no shared failure signal (Modules 1/5).**
  Phase 4.1 (`phase_lifecycle.py`) and Phase 4.2 (`task_runner.py::run_gated_task`) each
  run their own Tier0 scope check on the same task, by design (the second is meant as a
  non-bypassable safety re-check). But the round-progression breaker in `driver.py` only
  ever reads the *first* check's result (`GATE1_APPROVED` from Phase 4.1). There is no
  schema column or code path that lets the round loop learn "Phase 4.1 approved N tasks,
  but the Phase 4.2 re-check rejected M of them" — that information exists only inside
  individual `task_queue.gate1_rationale` strings, never aggregated until the post-hoc
  coverage-summary report (§5.2's `_build_coverage_summary_candidate`).
- **`candidate_detection.py`'s vocabulary is disconnected from `prompts.py`'s vocabulary.**
  The Strategist's controlled vocabulary (`prompts.py:241-243`, 19 tokens) and the
  candidate-detector's recognized classes (`candidate_detection.py:148`, 6 tokens: 5
  access-control + implicit XSS) were evidently authored/updated independently — the
  2026-09-22 fix added an XSS-specific rule in direct response to a live incident, the
  right instinct, but nothing in either file cross-references the other's vocabulary to
  catch the next 11-class gap systematically. There is no single source of truth for
  "which vulnerability classes can this system actually confirm," which is exactly the
  question this audit had to answer by manually diffing two files against each other.
- **The Scripter/Adjudicator retry-and-crash contract is inconsistent within the same
  codebase.** `engine/structured.py::get_structured_completion`'s retry-then-raise
  contract is used identically by both roles, but only one of the two call sites
  (`phase_lifecycle.py`'s Scripter loop) was ever updated to catch the resulting
  exception. This is a maintenance/consistency gap, not a design flaw in the retry
  mechanism itself — the fix pattern already exists in the same file, it just wasn't
  applied to the second call site.
- **Two different "novelty" concepts share the name "yield."** `loop_bounds.py`'s
  zero-yield breaker measures recon novelty (`novel_entities_count`), while the
  mission brief (and, reasonably, an operator reading "zero-yield engagement") means
  "found zero vulnerabilities." These are legitimately different concepts serving
  different purposes, but the shared vocabulary invites exactly the kind of
  misunderstanding this audit had to untangle in Module 5.

---

# 3. Prioritized Surgical Remediation Plan

Ordered by (a) how directly the fix closes a path to zero live findings, (b) blast radius
of the current gap, (c) implementation cost. **No fixes have been applied in this pass —
this is a plan for a follow-up implementation pass, per systematic-debugging's
root-cause-before-remediation discipline.**

1. **Wrap the Adjudicator call site in `run_phase_4_3` with the same `try/except
   StructuredOutputError` pattern already used for the Scripter** (`phase_lifecycle.py`,
   mirroring lines 649-654). **Correction from self-audit — the original wording here was
   underspecified and, if implemented as literally written, would have traded one crash
   for another:** `MODEL_STRUCTURED_OUTPUT_FAILURE` is **not** a valid value for
   `verified_vulnerabilities.status` — `schema.sql`'s CHECK constraint for that column
   (confirmed by direct read) only allows `'CANDIDATE','CONFIRMED','DISMISSED','REMEDIATED'`
   (it's `task_queue.status`'s CHECK constraint, a different column on a different table,
   that includes `MODEL_STRUCTURED_OUTPUT_FAILURE`). Setting it anyway would raise a
   `sqlite3.IntegrityError` inside the exception handler meant to prevent a crash. The
   correct fix has two real parts: (a) add a new terminal value (e.g. `ADJUDICATION_FAILED`)
   to `verified_vulnerabilities.status`'s CHECK constraint via the migration mechanism this
   codebase already uses for exactly this purpose — `data/db.py`'s `_CHECK_CONSTRAINT_MIGRATIONS`
   list already has precedent for widening this exact table's exact constraint (`REMEDIATED`
   was added to it this way) — then (b) catch `StructuredOutputError` at the call site and
   set that new status rather than leaving the row at `CANDIDATE` forever (there is no
   retry-count column on `verified_vulnerabilities` today, so leaving it `CANDIDATE` risks
   the same finding being re-submitted and re-failing every subsequent round with no bound,
   unless the fix also adds one). **Still highest priority** — this is the one bug standing
   directly between "pipeline is fixed" and "pipeline has confirmed its first live finding
   since the fix chain landed" — but it's a small schema migration plus a code change, not
   a code-only change as originally stated.

2. **Expand `candidate_detection.py`'s rule set to cover the Strategist's actual
   vocabulary**, at minimum: (a) a NoSQL-error pattern list alongside the existing SQL one
   (covers `NOSQLI`); (b) a generic PII pattern (email regex) alongside the existing
   password/token/admin patterns (helps `SECURITY_MISCONFIG`/disclosure-flavored findings);
   (c) a header-presence rule shape distinct from the current body-content rules, so
   `CORS`/`missing-header`-class findings have *any* path to `CANDIDATE` status — this is
   a new rule *shape*, not a new pattern in the existing shape, and is the one item in this
   plan that isn't a small delta; (d) widen the Tier-1 SQL filter
   (`candidate_detection.py:298`) to include `nikto`/`testssl`/`wafw00f` output once (c)
   exists to actually use it. Do NOT attempt full 19-class coverage in one pass — prioritize
   `SSRF`, `SECURITY_MISCONFIG`, and `NOSQLI` first, since those map most directly onto this
   session's own ground-truth finding set.

3. **Give the round-progression breaker in `driver.py` visibility into Phase-4.2 rejection,
   not just Phase-4.1 approval.** Minimal version: after `run_phase_4_2a`/`4_2b` complete
   for the round, check whether any of `round_task_ids` ended the round still
   `GATE1_APPROVED`-and-uncommanded, or moved to `GATE1_REJECTED`/`GATE2_BLOCKED` at the
   Phase-4.2 re-check, and fold that into the same `consecutive_zero_progress_rounds`
   counter (or a sibling counter with its own, tighter threshold) — closing exactly the gap
   traced in Module 5 §5.1 that let engagement 28 run un-flagged for two full rounds on a
   scope bug.

4. **Catch `DiskQuotaExceededError` at the `execute_and_record`/`run_gated_task` boundary**
   and turn it into a `DEFERRED`-or-equivalent per-task outcome (with a loud dashboard
   banner, per the Setup blueprint's own §6 promise) rather than an uncaught crash of the
   whole engagement. Low implementation cost, addresses a real (if lower-probability)
   silent-death mode.

5. **Empirically verify §6.3** (the baseline/attack/diff prompt requirement) with a live
   Adjudicator call against a real, strong candidate (e.g. reproduce finding #1's SQLi JWT
   evidence through the actual pipeline once #1 above is fixed) before deciding whether the
   prompt needs a "single-request evidence is acceptable when the disclosure is
   self-evident" carve-out, or whether the pipeline instead needs a real baseline-capture
   step added to the Scripter/execution contract. Don't guess at a fix here — this is
   exactly the kind of question the existing Testing Guide's own methodology (real request/
   response evidence, not theoretical) would resolve in one live run.

6. **Lower-priority hygiene items** (real but low-severity/low-probability, safe to batch
   with other work rather than treat as urgent): `_read_raw_artifact_text`'s silent
   `OSError` swallow (add a log line distinguishing "no signal" from "couldn't read
   evidence"); the silent `continue` on an unrecognized Tier 2 binary in
   `detect_candidates` (log a "saw output, no matching rule" line so future gaps like §4.1
   are visible in telemetry instead of requiring another manual code audit to find); the
   unbounded stdout/stderr buffer in `executor.py` (a size cap with a documented truncation
   marker, now that we've confirmed none currently exists, is cheap insurance against a
   single runaway tool call).

---

*Audit complete for all six mission modules. Items 1-4 above are ready to implement
directly; item 5 requires one live engagement run to resolve empirically rather than
another static-analysis pass.*

---

# 4. Addendum (2026-09-24) — Audit of "Round 27," the implementation response to this report

A separate session ("Mugheeraat 1.0 Setup Implementation Main") staged uncommitted
working-tree changes implementing remediation items 1-4 above, explicitly labeled
"Round 27" and citing this report by name in its own code comments. This session
(audit-only, no code written by it) independently reviewed the actual diff rather than
trusting the labeling — findings below.

**Structural integrity (checked after a separate concurrent session reported a near-miss
`git stash`/`stash pop` in this same shared working tree):** every modified `.py` file
compiles clean (`py_compile`), `schema.sql` parses clean (`sqlite3 :memory: ".read"`), no
leftover conflict markers anywhere in the diff. Nothing was lost or corrupted.

**Item-by-item correctness review (read every diff hunk directly, not just the commit
message):**

- **Item 1 (Adjudicator crash, §6.2):** Fixed correctly, and better than this report's own
  original wording — which would have crashed differently (see the correction already
  folded into remediation item 1 above, which this implementation matches exactly): a new
  `ADJUDICATION_FAILED` terminal status was added to `verified_vulnerabilities.status`'s
  CHECK constraint via the existing `_CHECK_CONSTRAINT_MIGRATIONS` mechanism (following the
  `REMEDIATED` precedent), and `run_phase_4_3`'s call site now catches
  `StructuredOutputError` and marks the finding terminal. Correctly reasoned that no
  retry-count column is needed, since `run_phase_4_3`'s own query only ever selects
  `status = 'CANDIDATE'` — an `ADJUDICATION_FAILED` row is simply never re-selected.
- **Item 2 (candidate-detection vocabulary, §4.1):** Fixed thoroughly — added NoSQL-error
  patterns, a bulk-PII/sensitive-field rule (2+ distinct emails, or SSN/credit-card/DOB
  key:value shapes), an Apache/nginx directory-listing (`Index of /`) rule, admitted
  `nikto`/`testssl`/`wafw00f` into the Tier-1 SQL filter, and a CORS rule. **The CORS rule
  is more careful than what this report recommended**: it fires only on the actual
  credential-exfil-capable shape (non-wildcard `Access-Control-Allow-Origin` + `Access-
  Control-Allow-Credentials: true` in the same response), deliberately not on a bare
  wildcard — matching the Primary Scripter's own "CORS wildcard without a credential-exfil
  angle... treat as noise" prompt instruction (`prompts.py:332-336`), which this report's
  own self-audit had already surfaced as the reason to *not* chase CORS-alone. The
  implementation's own code comment explicitly records pushing back on a broader "any CORS
  header" version of the directive for this exact reason, per `CLAUDE.md` Directive 5 — the
  right call, independently arrived at.
  - **One residual limitation worth naming (not a bug in the new code, a scope note):** the
    new CORS rule (and any header-dependent signal reached via the Tier-2 curl path) only
    ever sees response headers if the raw artifact contains them — a plain `curl` command
    without `-i`/`-D`/`-v` won't produce any headers to match against, the same underlying
    gap the pre-existing status-marker fix (`tier2.py::_curl_argv_with_status_marker`)
    exists to work around for status codes specifically, but nothing analogous exists yet
    for headers in general. This mainly affects the Tier-2 curl path; the three newly-
    admitted Tier-1 tools (`nikto`/`testssl`/`wafw00f`) print headers as part of their
    normal output regardless, so they're unaffected.
- **Item 3 (round-progression breaker blindness, §5.1):** Fixed correctly. The
  `consecutive_zero_progress_rounds` reset was moved from immediately after Phase 4.1's own
  approval count to after Phase 4.2A/4.2B have actually run, gated on a new
  `survived_tier0_recheck` count (`status NOT IN ('GATE1_REJECTED', 'GATE2_BLOCKED')`)
  against that round's own task IDs — closing exactly the gap traced in this report.
  Independently re-verified the one theoretical edge case this report considered (a task
  left un-touched at `GATE1_APPROVED` when a target goes terminal mid-round, which would be
  miscounted as "survived"): confirmed by reading `run_phase_4_2a`'s loop structure
  directly that this can't meaningfully happen — it re-evaluates `next_pivot_target` every
  iteration and keeps draining approved tasks until none remain for any non-terminal
  target, so a task only stays `GATE1_APPROVED` past the round boundary if the *global*
  session budget was exceeded — a condition the round loop already checks and stops on
  separately, not a gap this fix introduces.
- **Item 4 (uncaught `DiskQuotaExceededError`, Module 3):** Fixed correctly in
  `task_runner.py::run_gated_task` — wrapped in `try/except`, mapped to `DEFERRED`
  (mirroring the existing `policy_refused` precedent), and correctly reasoned that
  `record_task_outcome`/`_record_scripter_ledger_row` must be skipped for this path since
  no `tool_execution_logs` row exists yet at the point this exception fires (would have
  introduced a second crash otherwise). A real regression test exists for this
  (`test_milestone2_end_to_end.py`, confirmed by grep — an initial assumption during this
  review that no test existed was checked and found wrong before being written down here).

**Test verification:** ran the real, targeted test files for every touched module directly
(`test_candidate_detection.py`, `test_orchestrator_driver.py`,
`test_orchestrator_phase_lifecycle.py`, `test_council_adjudicator.py`,
`test_milestone2_end_to_end.py`) — **90/90 passed**. Full-suite run not performed in this
pass (time/token budget; the targeted set directly covers every file this diff touches).

**Overall assessment: Round 27 is a correct, precise, well-reasoned implementation of this
report's own remediation items 1-4**, including two places where it improved on this
report's own wording rather than following it literally (the CORS-noise distinction, and
confirming no retry-count column was actually needed for item 1) — consistent with
`CLAUDE.md`'s own Directive 5 (verify before implementing, push back on a wrong premise
rather than complying literally or silently). Item 5 (the Adjudicator's baseline/attack/diff
prompt requirement, §6.3) remains unaddressed and still requires a live model call to
resolve, as originally noted.

