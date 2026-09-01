# Implementation Milestone Roadmap — Autonomous Agentic VAPT System

A build order, not a schedule — no dates or effort estimates, since those depend on
who's building it. Each milestone is chosen to be independently testable before the
next begins, and ordered so that expensive/risky/privileged pieces (hibernation,
the freezer helper, the full council) come after the cheaper, safer pieces they
depend on are already proven. Traces every deliverable back to the requirement
cluster it satisfies, so "is this milestone done" has a concrete answer.

---

## Milestone 0 — Schema, Config, and CLI Skeleton (no LLM, no tools, no hibernation)

**Goal:** every other milestone has somewhere to read/write state and a command
surface to be invoked through, before any of the interesting logic exists.

- SQLite schema: all tables in `03-Data-and-Storage-Requirements.md` (`DR-SCHEMA-01`
  through `DR-SCHEMA-14`) plus the `IAB-SCHEMA` additions, with WAL mode and
  `PRAGMA busy_timeout=5000` set on every connection (`DR-CONCURRENCY-01/03`).
- The `engagement_lock_slot` generated column + unique index (`FR-CTRL-09`).
- Config loader reading `vapt_agent.config.yaml` with the confirmed defaults
  (`13-Implementation-Architecture-Bridge.md` IAB-FILES) baked in as fallback.
- Scope-rules YAML loader/parser (IAB-FILES) populating `scope_rules`.
- Click CLI skeleton: `start`, `pause`, `resume`, `abort`, `status`, `export`,
  `approve-report` (`IR-CTRL`) — at this stage `start` only validates inputs,
  writes an `engagements` row, enforces the single-engagement lock, and exits;
  no Phase 1-5 logic runs yet.

**Done when:** you can run `vaptctl start --targets ... --scope-rules scope.yaml`,
see a row appear in `engagements`, and a second concurrent `start` is refused by
the lock. `status`/`export` read real (if mostly empty) tables.

## Milestone 1 — Tool Bridge, No LLM Yet

**Goal:** prove the most security-critical subsystem in isolation, driven by
manually-inserted `task_queue` rows instead of a real Operator model.

- Tier 1 declarative schema files + wrappers (`IR-TOOL-01/02/03`, tiered timeouts).
- Tier 2 path-restricted allowlist + behavioral denylist + the three opt-in-flag
  categories (`FR-TOOL-03/06/06a-c`).
- Subprocess spawning with `start_new_session=True`; every invocation logged with
  its `pid` (`FR-TOOL-04a`, `IAB-SCHEMA-02`).
- Sanitization pipeline + `<tool_output_untrusted>` provenance tagging
  (`IR-SANITIZE-01/02/03`).
- `discovered_entities` population and the state-delta yield calculation
  (`FR-COUNCIL-11a`, `DR-SCHEMA-12`) — testable even without the loop-bound logic
  around it yet.
- Per-target rate limiting (`FR-TOOL-14`, `IR-BRIDGE-05`) and network-failure
  classification feeding the failure-based circuit breaker (`FR-COUNCIL-11b`,
  `IR-BRIDGE-06`) — both belong at the bridge level alongside the checks above,
  not bolted on later.
- **Before writing new Tier 1 wrappers from scratch**, check
  `16-Actual-Setup-Reuse-and-Integration-Map.md` §2 — several are already
  standalone, verified-portable scripts (`scope_checker.py` for `FR-COUNCIL-03a`'s
  reference implementation, `jwt_scanner.py`, `dom_xss_harness.py`, `oob_listener.py`
  as new Tier 1 candidates) rather than something to author fresh. This milestone
  is also where the full `tools/` classification pass from `16`'s §6 belongs.

**Done when:** a manually-queued task against a lab target actually executes,
produces sanitized + tagged output, logs a `pid`, and correctly increments/doesn't
increment `discovered_entities` depending on whether the result was novel.

## Milestone 2 — Deterministic Gates (still no LLM)

**Goal:** the two non-LLM gates, fully testable on their own since they're plain code.

- Council Gate 1 Tier 0: deterministic Python scope checker (`FR-COUNCIL-03a`).
- Council Gate 2: deterministic command/argument validator (`FR-COUNCIL-08`),
  consuming the same declarative schema files from Milestone 1.
- Wire both into the Milestone 0 CLI skeleton + Milestone 1 bridge so a queued task
  now actually passes through Tier 0 → (stub Tier 1 approval) → Gate 2 → execution.

**Done when:** an out-of-scope manually-queued task is rejected before any tool
runs, and a malformed manually-queued command is rejected by Gate 2 with a
specific, correct reason.

## Milestone 3 — Local Engine Client + Structured Output, One Model First

**Goal:** prove the LLM plumbing (load/unload, `response_format`, schema
validation, retry) against one real model before multiplying it by five.

- Local Engine Client (`IR-ENGINE-01..06`): `llama.cpp --server` process
  spawn/terminate, `MemAvailable` settle-poll gate.
- `IR-STRUCTURED-01..04`: `response_format={"type":"json_object"}` +
  per-output-type Python schema validator + bounded 2-retry loop.
- Load **only the Operator** (`Qwen2.5-Coder-7B-Instruct`) first — it's the most
  tool-execution-critical role and directly exercises Milestone 1's bridge.
  System prompt from `14-System-Prompt-Templates.md` §3.
- Wire the Operator's command-generation output into Milestone 2's Gate 2, so a
  real (not manually-queued) task can flow: Operator proposes → Gate 2 validates →
  Milestone 1 bridge executes.

**Done when:** the Operator, given one approved task, produces a schema-valid
command on the first or a corrected retry attempt, and it executes successfully
end-to-end against a lab target.

## Milestone 4 — Remaining Council Roles, One at a Time

Add each role from `14-System-Prompt-Templates.md` in this order, verifying each
against the pipeline built so far before adding the next:

1. **Council Gate 1 Tier 1** (`Hermes-3-Llama-3.1-8B`) — wire in front of the
   Operator so tasks are actually gated before execution, not just Tier-0-checked.
2. **Strategist** (`DeepSeek-R1-0528-Qwen3-8B`, planning prompt) — now tasks can
   originate from real hypothesis generation instead of manual queueing.
3. **Council Gate 3** (`Mistral-7B-Instruct-v0.3`) — findings can now be adjudicated,
   using the triage-validation-mined checks (impact/identity/baseline-attack-diff,
   `FR-COUNCIL-14a`) in `14-System-Prompt-Templates.md` §4, not just the base
   pattern checklist.
4. **Reporter** (`Ministral-8B-Instruct-2410`, reporting prompt — a dedicated model,
   not a Strategist reload, per decision #55) + the deterministic Python
   `cvss`-library calculator (`FR-COUNCIL-16a`).
5. **Offline Script Linter** (`Qwen2.5-Coder-3B-Instruct`) — lowest priority, only
   exercised for multi-line custom scripts; fine to stub/skip until the others are solid.

**Done when:** a single target, single-hypothesis engagement runs Phase 4.1 →
4.2 → 4.3 end-to-end with real models at every gate, producing at least one
CONFIRMED-or-DISMISSED finding.

## Milestone 5 — Loop Bounds & Multi-Target

**Goal:** the diminishing-returns thresholds and multi-target scoping, now that a
single-target single-pass loop already works.

- Per-target 30-task cap, 3-zero-yield circuit breaker, 12-hour global budget,
  auto-pivot/auto-transition (`FR-COUNCIL-11`).
- Multi-target `targets` rows within one engagement (`DR-SCHEMA-02`).

**Done when:** a multi-target engagement correctly caps/circuit-breaks one target
and auto-pivots to the next without operator input.

## Milestone 6 — Hibernation & the Privileged Helper

**Goal:** deliberately last among the "core loop" milestones — this is the most
system-invasive, privileged part, and the one most worth testing in isolation
before it's allowed to touch the operator's real desktop session.

- `vapt-freezer-helper` as its own small, separately-testable CLI
  (`13-Implementation-Architecture-Bridge.md` IAB-HELPER): `freeze`/`thaw`/
  `reclaim`, exit-code contract (0/13/1/2), `setcap`/`sudoers` grant.
- `FR-ENV-01..14`: app enumeration, protected-process denylist, `SIGSTOP`,
  `oom_score_adj=-900` via the helper, `process_madvise`/cgroup v2 fallback,
  post-resume verification, `suspended_processes` tracking (`DR-SCHEMA-13`).
- Test against disposable/non-critical applications first, not your daily-driver
  browser session, until `FR-ENV-12`'s casualty-detection path is proven.

**Done when:** freezing and thawing a handful of test applications round-trips
cleanly, a simulated OOM-pressure scenario confirms `FR-ENV-12` correctly detects
and logs a casualty rather than reporting false success, and the capability
fallback to cgroup v2 works when the helper's grant is deliberately removed.

## Milestone 7 — Control Surface, Kill-Switch, and Report Pipeline

**Goal:** the remaining operator-facing pieces, now that there's a real engagement
loop to pause/abort/report on.

- `pause`/`resume`/`abort` per `13-Implementation-Architecture-Bridge.md` IAB-PROC
  (SQLite/signal-coordinated, `abort` as a direct process-group kill via
  `os.killpg`, not cooperative — `FR-TOOL-04a`, `SEC-KILL-01/02`).
- Markdown report generation for both document types — per-finding `VAPT_FINDING`
  reports and the one-per-engagement `INFO_REGISTER` (`FR-COUNCIL-17`, `DR-SCHEMA-11`)
  — with evidence redacted *before* the Reporter LLM call, never after
  (`FR-COUNCIL-18`), `redaction_map` with byte-offset + content-hash addressing
  (`DR-SCHEMA-14`).
- Deterministic grounding check (`FR-COUNCIL-17b`, `IR-GROUND-01..03`) on every
  `VAPT_FINDING` draft before it can leave `DRAFT_PENDING_APPROVAL` — bounded retry
  then `BLOCKED_UNGROUNDED`, not a silent pass-through.
- `approve-report` → unredaction + hash verification + HTML/PDF rendering
  (`FR-CTRL-08`, `12-Report-Formatting-Rules.md`).
- Audit export packaging (`SEC-AUDIT-02`, `FR-CTRL-07`).

**Done when:** `abort` reliably stops a running engagement (including any
child-process tool it spawned) within the 20-second budget, and a full
Markdown → operator-approval → PDF cycle produces a report matching
`12-Report-Formatting-Rules.md`'s validation checks.

## Milestone 8 — Full Acceptance Pass

Run every test in `09-Acceptance-Criteria-and-Test-Plan.md` end-to-end against the
confirmed test lab: one or more local, disposable, Docker-based intentionally
vulnerable applications (e.g. OWASP Juice Shop for broad OWASP-Top-10/API coverage,
DVWA for classic web vulns, plus a throwaway network-service container for the
failure-based-circuit-breaker and rate-limiting tests) — never real infrastructure
(`08-Assumptions-Constraints-Dependencies.md` AC-ASSUME-06; exact composition is an
implementation-time detail, not fixed by this planning phase). Anything that fails
here is a bug in the build, not a gap in the requirements —
by this point every requirement in `01`-`17` should already be traceable to code
written in a specific earlier milestone.
