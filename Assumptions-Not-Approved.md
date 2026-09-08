# Assumptions Log (Resolved 2026-09-02)

Every entry here was something the requirements set (`01`-`18` in `../source/`)
left genuinely underspecified, where a concrete interpretation was picked to
keep building rather than stopping to ask. All 37 items below were reviewed
by the operator on 2026-09-02 — see the resolution table immediately below
for the verdict on each. The original write-ups are kept intact underneath
for their rationale, but every one is now a settled decision, not an open
question. New assumptions made after this date get appended as new numbered
items and are open again until reviewed.

Format per entry: **What I assumed** / **Why (spec basis)** / **Where it's used** / **What changes if disapproved**.

---

## Resolution Table (operator review, 2026-09-02)

| # | Decision | Notes |
|---|---|---|
| 1 | **Approved** | `sanitized_summary` prefix convention stands. |
| 2 | **Approved** | `[binary, *args]` JSON array stands. |
| 3 | **Approved** | Model directory location stands. |
| 4 | **Approved for Milestone 1** | Generic parser stands; tool-specific parsers deferred to acceptance hardening. |
| 5 | **Approved** | Representative flag catalogs stand; extend as needed during testing. |
| 6 | **Approved** | Output-flag heuristic list stands. |
| 7 | **Approved** | `disk_size + 512MB + 1.5GB margin` footprint formula stands. |
| 8 | **Approved** | `targeted_scans` (900s) default for unclassified Tier 2 commands stands. |
| 9 | **Approved** | `CAPPED > CIRCUIT_BROKEN > UNREACHABLE` priority stands. |
| 10 | **Approved** | `PENDING`→`ACTIVE` on first non-breaking outcome stands. |
| 11, 12, 14, 36, 37 | **Approved** | Standard sequencing ahead of full integration; no change needed. |
| 13 | **Approved as temporary** | `pause`/`resume` CLI-side state transitions stand until a real orchestrator loop owns them. |
| 15 | **Approved** | Provenance-tag wrapping boundary stands. |
| 16 | **Approved** | Plain-text user messages / JSON-only responses stands. |
| 17 | **Acknowledged** | Operator role wrapper — already completed (see `council/operator.py`). |
| 18 | **Approved — production correction** | `vapt-freezer-helper` needs `setcap cap_sys_ptrace,cap_sys_resource+ep`; documented in the helper's own docstring. |
| 19 | **Approved as placeholder** | `PENDING` section placeholders stand until Reporter schema is extended. |
| 20 | **Approved** | Caller-supplied CVSS/report metadata stands. |
| 21 | **Approved** | `INFO_REGISTER` candidate-record shape stands. |
| 22 | **Approved — Option 3** | Tier 1 gets its own binary-resolution path (bypasses the shared 3-dir allowlist; Tier 1's declarative schema is itself the trust boundary), Tier 2's `ALLOWED_PARENT_DIRS` is untouched. Implemented in `bridge/paths.py`/`bridge/tier1/wrapper.py`. |
| 23 | **Approved** | One `reports` row per format (`markdown`/`html`/`pdf`) stands. |
| 24 | **Approved** | Div-depth cover-footer validation fix stands over the doc's literal (broken) regex. |
| 25 | **Approved** | Generic `EVIDENCE` code-block label stands until per-block metadata exists. |
| 26 | **Approved** | `INFO_REGISTER`'s neutral dark cover band (`#1A1A2E`) stands. |
| 27 | **Approved** | Best-effort client label (first target's hostname) stands. |
| 28 | **Approved** | Two-pass Gate 1 architecture (semantic in 4.1, Tier 0 re-check in 4.2) stands. |
| 29 | **Approved** | `GATE2_BLOCKED` reused as the permanent terminal state stands. |
| 30 | **Approved** | Phase 4.2 loop itself marks an exhausted target `COMPLETE` stands. |
| 31 | **Approved** | Follow-up tasks skip the semantic tier, re-run Tier 0 only, stands. |
| 32 | **Approved — mechanism specified, implemented** | Deterministic tool-output parsing (nuclei `severity` field, sqlmap injection-point phrasing, nmap NSE `VULNERABLE` lines) replaces the original narrower placeholder heuristic. Implemented in `council/candidate_detection.py`, reading raw artifact text (not the generic sanitized summary). A first-pass build used the older placeholder rule instead of this mechanism — caught and corrected the same day. |
| 33 | **Approved — mechanism specified** | Deterministic regex scanner (password/token/bearer/apikey/secret, session-ID patterns, Basic-auth headers) populates `known_secrets`. Implemented in `bridge/secret_detection.py`, patterns aligned to the operator-specified set. |
| 34 | **Approved with optimization** | In-loop session-budget check stands as the actual enforcement; operator also requested a lightweight pre-flight check before loading the Operator model specifically, to avoid an unnecessary load/unload cycle on an already-expired budget — not yet implemented, tracked as a follow-up, not a blocker. |
| 35 | **Approved** | 2 GiB/session swap-growth threshold stands. |

---

## Resolution Table Addendum (operator review, 2026-09-03) — items 16, 17, 31-50

| # | Decision | Notes |
|---|---|---|
| 16 | **Approved** | Plain labeled-text user-message input (vs. strict-JSON model *output*) stands — minimizes prompt token overhead while keeping clear delimiter separation. |
| 17 | **Approved directive** | `vapt_agent/council/operator.py` — already built, wraps `Qwen2.5-Coder-7B-Instruct` against `validate_operator_command`/`validate_operator_followup`. |
| 31 | **Approved** | Follow-up tasks skip Phase 4.1's semantic Gate 1 tier, re-run Tier 0 only in Phase 4.2 — saves turn latency, preserves the hard scope invariant (the deterministic check, not the LLM tier, is the actual boundary). |
| 32 | **Approved — implemented** | Deterministic candidate-detection lives in `vapt_agent/council/candidate_detection.py` (nuclei `severity` field, sqlmap injection-point phrasing, nmap NSE `VULNERABLE` lines), reading raw artifact text. (Operator's write-up names `bridge/sanitize.py` — the actual location is `council/candidate_detection.py`; functionally identical to what was approved, noted here so the file/module name isn't a future point of confusion.) |
| 33 | **Approved — implemented** | Deterministic regex extractors live in `vapt_agent/bridge/secret_detection.py` (API tokens/bearer/apikey/secret, Authorization headers, session cookies, private keys) populating `known_secrets` before Reporter ingestion. (Same module-name note as #32 — operator's write-up says `bridge/sanitize.py`, actual file is `bridge/secret_detection.py`.) |
| 34 | **Approved with optimization** | Same as the 2026-09-02 table's #34 row above — in-loop check stands, pre-flight fast-path before Operator load is an accepted, not-yet-built optimization. |
| 35 | **Approved** | 2 GiB threshold reconfirmed (matches #35 above and `NFR-RES-06`'s later formal spec confirmation). |
| 36 | **Approved** | Swap-tracking baseline/growth-assertion wiring into real orchestrator start/termination sequences is valid sequencing, tracked for Milestone 8 acceptance — not yet wired as of this review. |
| 37 | **Approved / acknowledged** | The ≤4-of-8-E-core-thread constraint is currently vacuously satisfied under synchronous single-task execution; design retained for a future asynchronous execution loop, not re-architected now. |
| 38 | **Approved** | `EngineUnresponsiveError`'s forced `SIGTERM`→`SIGKILL` on client-side timeout stands — closes the real resource-leak finding (a stuck generation kept consuming CPU after client abandonment). |
| 39 | **Approved** | `jwt_scanner`/`oob_listener`/`dom_xss_harness` integration stands; `bundled: true` package-relative resolution and graceful exit-127 degradation when `interactsh-client`/`playwright` are absent both confirmed structurally sound. |
| 40 | **Approved** | `llm_redteam`/`cors_scanner`/`crlf_scanner`/`nosqli_scanner`/`visual_triage` integration and the `crlf_scanner.py` `http.client.InvalidURL` crash fix stand; `waf_response_analyzer.py` as a plain importable module (not a Tier 1 CLI tool) confirmed as the right shape for Gate 3's future WAF-block-page adjudication use. |
| 41 | **Approved** | `zero_day_fuzzer.py`'s new `--findings-dir` flag (avoiding writes into the installed package tree) stands. |
| 42 | **Approved** | `prompts.py`'s resync against doc 14 plus the non-doc-14 supplementary content (kept, not deleted) stands; the "hardware-gated domains degrade/defer gracefully" principle is confirmed as the standing rule for Web3/Mobile/CI-CD wherever a real dependency (Foundry, a physical device, `gh` auth) is genuinely unavailable. |
| 43 | **Approved** | The 15-prefix-candidate DNS-based subdomain baseline (a documented, narrower stand-in for full passive enumeration) and the "first run establishes baseline, never a spurious diff" semantics both stand. |
| 44 | **Approved** | The four-class deterministic Human Checkpoint Gate classifier stands; the `start.py` `PAUSED_AWAITING_CHECKPOINT`-missing-from-the-lock-query fix is confirmed as a real concurrency-safety bug fix, not just a judgment call. |
| 45 | **Approved** | The Strategist's 3-8 hypothesis bound and `decode_json_content`'s `json.loads(..., strict=False)` both stand — confirmed root-caused via live evidence (measured throughput, reconstructed token streams), not guessed. |
| 46 | **Approved** | `mobile_secrets_sweep.py`'s static-analysis-only implementation stands; deferring Frida/objection dynamic instrumentation given no physical test device is available on this machine is the correct default, not a gap. |
| 47 | **Approved** | The `code_grep_scan` (whole-repo sinks) / `diff_review_scan` (diff-scoped blast-radius) split stands; the enclosing-function-tracking fix (catching body changes, not just changed `def` lines) is confirmed as a real bug fix. |
| 48 | **Approved** | `PUBLIC_RESEARCH` mode's read-only closed-allowlist bypass of normal `scope_rules` stands; `web3_fork_poc.py`'s `--fork-url` restriction to `{127.0.0.1, localhost, ::1}` only (verified directly in the code, not just the write-up) stands as the mainnet-fork-only enforcement mechanism. |
| 49 | **Approved** | The native Python 7-phase GraphQL scanner (no unvetted shell-script dependency) and the new `flag_requires_opt_in` Tier 1 schema mechanism (verified directly in `bridge/tier1/schema.py`/`council/gate2_validator.py`) gating `--batching-dos`/`--alias-bomb`/`--depth-bomb` behind `allow_active_exploitation` both stand. |
| 50 | **Approved with critical enforcement noted** | HIBP SHA-1-prefix-only querying stands. Operator's critical boundary — all automated tests/default operations must stay scoped to placeholder (`owner/repo`) or explicitly-authorized real repos, with any live CI/CD PR/workflow/secret action gated behind the Human Checkpoint Gate — is already exactly how this was built (`cicd_external_action.py`'s three action names are wired into `checkpoint_gate.py`'s `CICD_EXTERNAL_ARTIFACT` class, and every test in `tests/test_tier1_cicd_external_action.py` deliberately targets the placeholder `owner/repo`, never a real repository, precisely because `gh` is confirmed live-authenticated on this machine). No further action needed — recorded here as explicit operator confirmation of an already-enforced boundary. |
| 51 | **Approved** | Anti-forensics' closed three-verb set (`clear-log-lines`/`timestomp`/`clear-shell-history`), each backup-then-revertible and never an arbitrary-command passthrough, stands; the Human Checkpoint Gate binding and the `FR-BROADSCOPE-03` criminal-infrastructure prohibition folded into the Strategist prompt both stand. |
| 52 | **Approved** | `vaptctl dashboard`'s `plotext>=5.2,<6` pin (avoiding the incompatible 6.0.0 rewrite), the compute/render split, the strict `mode=ro` (no `immutable=1`) connection, and the Operator-only `RESIDENT`/`IDLE` badge (every other role bounded to `RUNNING`/`COLD`) all stand. |
| 53 | **Approved** | `run_with_invocation_logging`'s non-invasive wrapping of `get_structured_completion` (kept pure/DB-free), the "one multi-attempt exchange = one turn, except Operator Gate-2-rejection retries" semantics, and the unfinalized-row-then-finalize write pattern all stand. |

---

## 1. Rejected Tier 2 calls are logged via a text-prefix convention, not a new column

**What I assumed:** `IR-BRIDGE-04` requires every rejected bridge call to be
tagged into `tool_execution_logs` with "which rule matched" — but
`DR-SCHEMA-06` has no `rejection_reason`/`decision` column. I record this in
the existing `sanitized_summary` TEXT column with a fixed prefix:
`REJECTED[<rule>]: <reason>`.

**Why:** Avoids a schema change the docs never asked for, while still
satisfying "auditable, not silently dropped."

**Where it's used:** `vapt_agent/bridge/pipeline.py::record_rejection`.

**What changes if disapproved:** Add a real column (e.g.
`tool_execution_logs.rejection_reason TEXT`) and stop overloading
`sanitized_summary`.

---

## 2. `task_queue.proposed_command` is stored as a JSON array `[binary, *args]`

**What I assumed:** `DR-SCHEMA-05` just says `proposed_command` is "full
argument vector as generated" (TEXT). I store it as a JSON-encoded list of
argv tokens (element 0 = binary/tool name), never a shell string — consistent
with `FR-TOOL-04`'s "never a shell string" principle applied one layer
earlier than the bridge itself.

**Where it's used:** `vapt_agent/council/task_runner.py`.

**What changes if disapproved:** Pick a different wire format (e.g. a
structured `{tool, args}` JSON object instead of a flat array) and update the
parsing in `task_runner.py` accordingly.

---

## 3. Model `.gguf` files live under `/home/mhj/.local/share/vapt_agent/models/`

**What I assumed:** Only `state.db` and `artifacts/` have a pinned path in
the docs (`03`/`13`). No path is given for the model weights themselves. I
put them in a sibling `models/` directory under the same pinned data root.

**Where it's used:** Model download location; will be referenced by
whatever config eventually points the Local Engine Client at each model's
path.

**What changes if disapproved:** Move the directory and update the download
script / eventual config.

---

## 4. Tier 1 sanitization uses one generic pattern-based parser, not 11 bespoke ones

**What I assumed:** `IR-SANITIZE-01` asks for "one pluggable parser per
tool/output-type." I built the plug-in architecture (`PARSERS` dict keyed by
tool name, falling back to `_generic_parser`) but only implemented the
generic one — a single regex-based extractor for ports/URLs/status
codes/banners that works reasonably across all 11 tools' typical output,
rather than a bespoke parser per tool.

**Why:** Scope/time tradeoff for Milestone 1; the extension point exists so
per-tool parsers can be dropped in later without touching call sites.

**Where it's used:** `vapt_agent/bridge/sanitize.py`.

**What changes if disapproved:** Write the 11 bespoke parsers (nmap XML/grepable
output, ffuf JSON, nuclei JSONL, etc.) and register them in `PARSERS`.

---

## 5. Tier 1 schema flag catalogs (`allowed_flags`/`forbidden_flags`) are representative, not exhaustive

**What I assumed:** The 11 YAML schema files under
`vapt_agent/bridge/tier1/schemas/` list a reasonable, commonly-used subset of
each tool's flags (plus known-destructive ones explicitly forbidden), not
every flag each tool actually supports.

**Why:** `IR-TOOL-01` requires the schema to exist and declare this
structure; it doesn't hand over an exhaustive flag catalog per tool, and
building one for all 11 tools from their man pages is a large, separate
effort.

**Where it's used:** Gate 2's enforcement (`council/gate2_validator.py`) will
reject any flag not in a schema's `allowed_flags` — so an incomplete catalog
means Gate 2 will currently reject some legitimate, safe flag choices the
real Operator model might propose.

**What changes if disapproved:** Expand each YAML file's `allowed_flags` against
each tool's actual documented flag set.

---

## 6. Tier 2's rule-(c) "output path" detection is a fixed heuristic flag-name list

**What I assumed:** `FR-TOOL-06(c)` requires rejecting a file write/delete/rename
outside the artifact path. Since there's no shell (`shell=False`), the only
way a tool writes to disk is via its own output flags — I check argv for a
fixed set (`-o`, `-O`, `-oA`, `-oN`, `-oX`, `-oG`, `-w`, `--output`, `--out`)
and validate the following token as a path.

**Why:** No exhaustive list of every tool's output-flag spelling exists in
the docs; `SEC-CONTAIN-02` already frames this whole denylist as
residual-risk-accepted, not a guarantee.

**Where it's used:** `vapt_agent/bridge/denylist.py::check_behavioral_denylist`.

**What changes if disapproved:** Extend/replace the flag-name set, or move to
a stricter model (e.g. only ever allow relative output paths, resolved
against a forced cwd).

---

## 7. Local Engine Client's memory-gate threshold = on-disk GGUF size + a fixed 512MB runtime allowance

**What I assumed:** `IR-ENGINE-06`/`FR-GATE-10` say wait for `MemAvailable` to
clear "the NFR-RES-02 safety threshold (baseline + 1.5 GB margin)" but never
define what "baseline" means for a *specific incoming model*. I treat
baseline as that model's own on-disk file size, plus a flat 512MB allowance
for KV-cache/runtime overhead, plus the 1.5GB margin.

**Where it's used:** `vapt_agent/engine/client.py::_model_footprint_kb`,
called from `LlamaCppEngineClient.load()`.

**What changes if disapproved:** Replace with a real measurement-based
approach (e.g. a per-model calibration pass during Milestone 3's actual live
testing, recording real RSS after load and reusing that number thereafter).

---

## 8. Tier 2's default timeout class defaults to `targeted_scans` when the caller doesn't specify one

**What I assumed:** `IR-TOOL-03`'s three timeout classes are defined for the
named Tier 1 tools; Tier 2 covers arbitrary binaries with no predefined
class. `run_security_command`'s `timeout_class` parameter defaults to
`"targeted_scans"` (900s) if the caller doesn't pass one.

**Where it's used:** `vapt_agent/bridge/tier2.py::run_security_command`.

**What changes if disapproved:** Pick a different default (e.g. always
require the caller to specify one explicitly, with no default at all).

---

## 9. When multiple loop-bound thresholds trip on the same run, priority is CAPPED > CIRCUIT_BROKEN > UNREACHABLE

**What I assumed:** `FR-COUNCIL-11/11a/11b` define three independent
thresholds (30-task cap, 3-zero-yield breaker, 3-failure breaker) but never
say which status wins if more than one trips on the same task. I check them
in that fixed order.

**Where it's used:** `vapt_agent/council/loop_bounds.py::record_task_outcome`.

**What changes if disapproved:** Pick a different priority order, or make it
configurable.

---

## 10. A target moves `PENDING` -> `ACTIVE` on its first recorded task outcome that doesn't itself trip a breaker

**What I assumed:** `DR-SCHEMA-02` defines the `PENDING`/`ACTIVE`/... status
values but never states exactly when a target transitions out of `PENDING`.

**Where it's used:** `vapt_agent/council/loop_bounds.py::record_task_outcome`.

**What changes if disapproved:** Pick a different trigger (e.g. transition
to `ACTIVE` the moment a task is queued against it, before execution).

---

## 11. `is_session_budget_exceeded()` / `next_pivot_target()` exist as standalone helpers, not yet called by any loop

**What I assumed:** These implement the 12h-budget and auto-pivot halves of
`FR-COUNCIL-11`, but there is no real Phase 4.2 orchestrator loop yet to
repeatedly execute tasks and act on their output — that's later integration
work. Built and tested in isolation now so whichever loop driver gets built
later can call them directly.

**Where it's used:** `vapt_agent/council/loop_bounds.py`.

**What changes if disapproved:** N/A — this is a sequencing note, not a
behavioral choice; flag if you want them wired into a stub loop now instead
of waiting for the real one.

---

## 12. `ensure_phase42_started()` is called idempotently on every task run, not from one single "Phase 4.2 begins" event

**What I assumed:** `engagements.phase4_started_at`/`session_deadline_at`
need to be set exactly once when Phase 4.2 begins, but no such single event
exists yet in the code (no live orchestrator loop). Calling it idempotently
at the top of every `run_gated_task` achieves the same effect (first call
sets it, later calls no-op) without inventing a fake "phase start" event.

**Where it's used:** `vapt_agent/council/task_runner.py::run_gated_task`.

**What changes if disapproved:** Move this call to a real, single Phase 4.2
entry point once the orchestrator loop exists, and remove it from
`task_runner.py`.

---

## 13. `pause`/`resume` directly set `status='PAUSED'`/`'IN_PROGRESS'` themselves, instead of a live orchestrator loop doing it

**What I assumed:** `IAB-PROC` specifies that `pause` only requests a pause
(`control_intent='PAUSE_REQUESTED'` + `SIGUSR1`) and the *orchestrator
process itself* persists state, sets `status='PAUSED'`, and exits at its next
safe checkpoint; `resume` similarly is supposed to hand off to a fresh
orchestrator process that picks the Phase 4.2 loop back up. No such
long-lived orchestrator loop exists yet in this codebase (Milestones 3-5
built the pieces a future loop will call — model role wrappers, loop-bound
counters — but not the loop itself that repeatedly drives Phase 4.2). Since
leaving an engagement permanently stuck `IN_PROGRESS` with no process left to
ever notice `PAUSE_REQUESTED` seemed clearly worse, `pause`/`resume`
themselves make the status transition directly, as a pragmatic stand-in.

**Where it's used:** `vapt_agent/cli/pause.py`, `vapt_agent/cli/resume.py`.

**What changes if disapproved:** Once a real Phase 4.2 loop exists, move the
`status='PAUSED'` transition into that loop's checkpoint logic (reacting to
`control_intent`) and have `pause` only ever write the intent + signal, per
IAB-PROC's literal division of responsibility.

---

## 14. `abort`'s orchestrator-kill step targets `engagements.orchestrator_pid`, which is usually already dead in this milestone state

**What I assumed:** Same root cause as #13 — `orchestrator_pid` today is set
by whichever CLI invocation (`start`/`resume`) last touched the row, and
that process already exited by the time anyone calls `abort` (no long-lived
loop yet). `security/kill_switch.py::abort_engagement` still implements the
SIGTERM/SIGKILL sequence against that PID faithfully per `SEC-KILL-01/02` —
it will just almost always hit `ProcessLookupError` (handled gracefully,
`orchestrator_killed=False`) until a real persistent orchestrator process
exists. The tool-subprocess-killing half of `abort` (querying
`tool_execution_logs` for a live `pid`) IS fully meaningful today.

**Where it's used:** `vapt_agent/security/kill_switch.py::abort_engagement`.

**What changes if disapproved:** N/A — this is a sequencing/honesty note
about current limits, not a behavioral choice to approve or reject; the
logic itself already matches spec and needs no change once a real loop
exists.

---

## 15. Provenance-tag boundary for council role wrapper inputs

**What I assumed:** `IR-SANITIZE-02`/doc 14's Shared Clause A require
`<tool_output_untrusted>` wrapping for content that "originates from the
target system." The role wrappers (`vapt_agent/council/{strategist,
gate1_semantic,adjudicator,reporter}.py`) wrap `existing_findings`,
`task_description`, `raw_evidence`, and `redacted_evidence` (since doc 14's
intro says these all "trace back to scanned content"), but do NOT wrap
`targets`/`scope_summary` (operator-supplied config) or the Offline Linter's
`script_text` (Operator-written, not target-derived).

**Where it's used:** `vapt_agent/council/strategist.py`,
`gate1_semantic.py`, `adjudicator.py`, `reporter.py`.

**What changes if disapproved:** Adjust which parameters get wrapped in
each role wrapper's message-building code.

---

## 18. `vapt-freezer-helper` needs `CAP_SYS_RESOURCE` in addition to `CAP_SYS_PTRACE`

**This is a correction to the spec, not a judgment call** — flagging for
your awareness/approval rather than something I decided. `FR-ENV-13`/
`SEC-CONTAIN-05` state the helper needs only `CAP_SYS_PTRACE` to cover
`SIGSTOP` + `oom_score_adj` + `process_madvise`. Verified live on this
sandbox: lowering `oom_score_adj` below 0 actually requires
`CAP_SYS_RESOURCE` — a different capability — and an unprivileged attempt
correctly hits `EACCES`, which the helper reports as its documented
capability-unavailable exit code (13), not a crash.

**Where it's used:** `vapt_agent/freezer_helper/vapt_freezer_helper.py`
(implementation already handles the unprivileged case correctly by falling
back/reporting exit 13 — this note is about the eventual production
`setcap` grant, not a code change).

**What changes if disapproved:** N/A to the code (it already degrades
correctly); this is about documenting the correct capability grant
(`setcap cap_sys_ptrace,cap_sys_resource+ep`) for deployment, superseding
`05`/`13`'s stated single-capability grant.

---

## 19. Reporter output schema doesn't yet carry all fields doc 12's report format needs

**What I assumed/found:** `validate_reporter_output` (locked, built in
Milestone 3) only carries `{finding_id, title, executive_summary, root_cause,
remediation, cvss_metrics}`. `12-Report-Formatting-Rules.md` §6 also expects
a CVE reference/affected-endpoints section, a steps-to-reproduce section, and
a tools-and-methodology table — none of which the current Reporter
output/prompt asks for. `vapt_agent/reports/markdown_gen.py` renders those
three sections as an explicit `PENDING — not yet available in this pipeline
version` placeholder rather than fabricating content.

**Where it's used:** `vapt_agent/reports/markdown_gen.py::generate_vapt_finding_markdown`.

**What changes if disapproved:** Extend `14-System-Prompt-Templates.md` §5's
Reporter output schema (and `validate_reporter_output` to match) with fields
for affected endpoints/CVE, reproduction steps, and tools used, then update
`markdown_gen.py` to render real content instead of the placeholder.

---

## 20. `generate_vapt_finding_markdown` takes `cvss_vector`/`cvss_score`/`severity`/`scope_statement`/`assessment_date`/`report_id` as caller-supplied inputs

**What I assumed:** These aren't things the Reporter model itself produces
(CVSS score/vector come from the separate deterministic calculator,
per `FR-COUNCIL-16a`; report numbering and severity-band labeling are never
assigned anywhere in `01`-`18`). Left as required parameters for whatever
future code wires the real `cvss` library and a report-numbering scheme
together — not yet built.

**Where it's used:** `vapt_agent/reports/markdown_gen.py`.

**What changes if disapproved:** Define an actual report-ID scheme
(`CLIENT-V-NNN` or otherwise) and severity-band thresholds somewhere
authoritative, and have the real caller compute them rather than leaving it
open-ended.

---

## 21. `generate_info_register_markdown`'s candidate-record shape is invented

**What I assumed:** Nothing in `01`-`18` defines what data a DISMISSED/
non-yielding candidate record looks like once it reaches the report layer.
I used `{info_id, target, title, what_was_found, why_informational,
recommendation}`.

**Where it's used:** `vapt_agent/reports/markdown_gen.py::generate_info_register_markdown`.

**What changes if disapproved:** Change the shape to match however
`verified_vulnerabilities` (status=`DISMISSED`) rows actually get mapped into
the `INFO_REGISTER` document once that wiring is built.

---

## 22. HIGH PRIORITY / VERIFIED BUG-CANDIDATE: `sqlmap` fails the Tier 1/Tier 2 shared path allowlist on real Kali

**This is a verified fact about this actual machine, not a judgment call —
needs a decision, not just an FYI.** `FR-TOOL-03` claims `/usr/bin/`,
`/usr/sbin/`, `/opt/` "cover the full `kali-linux-everything` toolset," and
`bridge/paths.py::resolve_binary` (shared by both Tier 1's wrapper and
Tier 2) enforces exactly those three as the only allowed *resolved* parent
directories — correctly following symlinks per `IR-BRIDGE-02`'s explicit
"resolving symlinks" instruction. But on this real Kali install:
```
/usr/bin/sqlmap -> ../share/sqlmap/sqlmap.py   (a symlink)
```
`sqlmap`'s resolved real path is `/usr/share/sqlmap/sqlmap.py`, whose parent
(`/usr/share/sqlmap/`) is NOT one of the three allowed directories. Right
now, **any real invocation of `sqlmap` — one of the 11 required Tier 1
tools — is refused by `resolve_binary` on this actual machine.** `FR-TOOL-03`'s
claim that the three paths cover the whole toolset is empirically false for
at least this one tool's actual Debian/Kali packaging (similar in kind to
item #18's `CAP_SYS_RESOURCE` finding — a factual spec error, not an
implementation gap).

**Where it breaks:** `vapt_agent/bridge/paths.py::resolve_binary`, called
from both `vapt_agent/bridge/tier1/wrapper.py` and `vapt_agent/bridge/tier2.py`.

**Options (not implemented — this is a security-boundary decision, not mine
to make unilaterally):**
1. Add `/usr/share/sqlmap` (and audit whether any other Tier 1 tool has the
   same Debian-packaging pattern — I have not checked the other 10) as an
   explicit, named exception to `ALLOWED_PARENT_DIRS`.
2. Broaden the rule to something like "the resolved path's parent is one of
   the three directories, OR the *symlink itself* (pre-resolution) lived in
   one of them" — i.e. trust `/usr/bin/sqlmap` as the allowlisted entry point
   even though its target lives elsewhere. This is a meaningfully looser
   security boundary than the current literal reading of `FR-TOOL-03` and
   should be a deliberate, explicit choice.
3. Leave it as-is and treat `sqlmap` as needing a different invocation path
   (e.g. always calling `/usr/share/sqlmap/sqlmap.py` directly via Tier 1's
   own declared "resolved absolute path" per `IR-TOOL-01`, bypassing the
   shared Tier 2-style allowlist check for Tier 1 tools specifically, on the
   theory that Tier 1's own declarative schema is itself the trust boundary
   for these 11 named tools — Tier 2's dynamic allowlist was designed for
   *arbitrary* binaries, not this fixed, pre-vetted list).

**What changes if disapproved / once you pick one:** Edit
`ALLOWED_PARENT_DIRS` (option 1/2) or change `bridge/tier1/wrapper.py` to
resolve Tier 1 binaries differently from Tier 2's `run_security_command`
(option 3) — I did not implement any of these myself, sqlmap is currently
non-functional as a Tier 1 tool on this machine until one is chosen.

---

## 23. `reports` table: one new row per rendered format (`html`/`pdf`), not one row holding all three

**What I assumed:** `DR-SCHEMA-11`'s `format` column is single-valued
(`markdown`/`html`/`pdf`), so representing "this finding now also has an
HTML and a PDF" means two new rows sharing the same `engagement_id`/
`document_type`/`finding_id` as the original Markdown row, not one row with
three file paths.

**Where it's used:** `vapt_agent/cli/approve_report.py`.

**What changes if disapproved:** Add a schema change (e.g. separate
`html_file_path`/`pdf_file_path` columns on one row) instead.

---

## 24. Doc 12 §12's own suggested cover-footer/cover-body nesting check is buggy — implemented the intended rule instead of the literal snippet

**What I assumed:** `12-Report-Formatting-Rules.md` §12 gives a literal
Python regex (`re.search('cover-body.*?cover-footer', ...)`) as "the" check,
but that regex flags every correctly-structured document as a false
positive (it can't distinguish "cover-footer appears later in the text,
correctly as a sibling" from "cover-footer is nested inside cover-body").
`render.py::_cover_footer_nested_in_cover_body` does real div-depth tracking
instead, to enforce what the rule clearly intends rather than its flawed
literal snippet.

**Where it's used:** `vapt_agent/reports/render.py::validate_rendered_html`.

**What changes if disapproved:** Revert to the literal (broken) snippet from
doc 12, which would then require every real report's HTML to be manually
exempted from a check it can never actually pass.

---

## 25. Code-block labels in rendered HTML are a generic fixed string, not doc 12 §11's per-block HTTP-specific labels

**What I assumed:** Doc 12 §11 wants labels like `HTTP REQUEST`/`RESPONSE —
HTTP 200 OK` per evidence block, but nothing upstream (the Reporter's output
schema, `markdown_gen.py`) carries per-block metadata distinguishing a
request from a response or its status code — that data doesn't exist yet
anywhere in the pipeline. `render.py::_wrap_code_blocks` uses one fixed
generic `EVIDENCE` label for every code block instead.

**Where it's used:** `vapt_agent/reports/render.py::_wrap_code_blocks`.

**What changes if disapproved:** This really needs fixing upstream first —
the Reporter's prompt/output schema (`14-System-Prompt-Templates.md` §5,
`engine/schemas.py::validate_reporter_output`) would need per-evidence-block
structure (request vs. response, status code) before `render.py` has
anything real to label with.

---

## 26. `INFO_REGISTER` documents get a fixed neutral dark cover band (`#1A1A2E`)

**What I assumed:** Doc 12 §9's consolidated register has no per-document
severity (it covers DISMISSED/non-yielding candidates collectively, not one
graded finding), so the severity-color cover-band logic used for
`VAPT_FINDING` reports doesn't apply — picked one fixed neutral color.

**Where it's used:** `vapt_agent/reports/render.py`.

**What changes if disapproved:** Pick a different fixed color, or add some
other visual treatment for the register's cover band.

---

## 27. `approve-report`'s running-footer client label is best-effort (first target's hostname)

**What I assumed:** Nothing upstream of `approve-report` threads a distinct
"client display name" concept through the system — `engagements`/`targets`
only ever record technical scope patterns, never an operator-facing client
name. Used the engagement's first `targets.host_or_domain` row as a stand-in.

**Where it's used:** `vapt_agent/cli/approve_report.py`.

**What changes if disapproved:** Add a real `client_name` field somewhere
(e.g. `engagements.notes` parsed, or a new column) and thread it through
instead.

---

## 28. Gate 1 runs twice, in two different senses, to resolve an FR-COUNCIL-03a/07 tension

**What I assumed:** `FR-COUNCIL-03a` says the deterministic scope check runs
on "every proposed task," but its own port-range/destructive-flag checks
need a real command to check against — and `FR-COUNCIL-07` says the Operator
only ever sees "each Gate-1-approved task," implying Gate 1 finishes before
a command exists at all. Resolved as a **two-pass** design: Gate 1 (Tier 0 +
the Hermes-3 semantic tier) runs once in Phase 4.1 against each Strategist
hypothesis with an empty argv (only the scope check is meaningfully
exercised there); Phase 4.2's `run_gated_task` runs Tier 0 again against the
Operator's actual generated command (this is where port-range/destructive-
flag checks get real data), but does NOT re-invoke the expensive Tier 1 LLM
call a second time — Gate 2 is the correct downstream check for the
command's specific shape.

**Where it's used:** `vapt_agent/orchestrator/phase_lifecycle.py` (module
docstring has the full reasoning), `vapt_agent/council/task_runner.py`.

**What changes if disapproved:** Pick a different resolution — e.g. Gate 1
runs only once, after command generation (delaying all of Phase 4.1's task
creation until Phase 4.2 has a command), or Tier 1 also re-runs in Phase 4.2.

---

## 29. `GATE2_BLOCKED` is the permanent terminal state after 3 failed correction attempts (no separate "blocked-after-retries" status)

**What I assumed:** `FR-COUNCIL-09` says a task is marked `BLOCKED` after 3
failed attempts, but `task_queue.status`'s CHECK constraint (`DR-SCHEMA-05`)
has no `BLOCKED` value, only `GATE2_BLOCKED`. Used `GATE2_BLOCKED` for both
"this specific attempt was rejected" and "permanently blocked after 3
attempts" — there's no way to distinguish the two in the schema as it
stands.

**Where it's used:** `vapt_agent/orchestrator/phase_lifecycle.py::run_phase_4_2`.

**What changes if disapproved:** Add a distinct `BLOCKED` value to the
`task_queue.status` CHECK constraint in `schema.sql` and use it specifically
for the retries-exhausted case.

---

## 30. A target with no more actionable tasks (and not otherwise terminal) is marked `COMPLETE` by the Phase 4.2 loop itself

**What I assumed:** `DR-SCHEMA-02` defines `COMPLETE` as one of a target's
possible statuses but never says who sets it. `run_phase_4_2` sets it when a
target has no remaining un-executed `GATE1_APPROVED` task and hasn't hit any
of the CAPPED/CIRCUIT_BROKEN/UNREACHABLE thresholds either.

**Where it's used:** `vapt_agent/orchestrator/phase_lifecycle.py::run_phase_4_2`.

**What changes if disapproved:** Move this responsibility elsewhere (e.g.
only Phase 4.3 or an explicit operator action marks a target COMPLETE).

---

## 31. Follow-up tasks (FR-COUNCIL-10) skip Phase 4.1's Gate 1 entirely, going straight to Phase 4.2's Tier 0 re-check

**What I assumed:** A follow-up task the Operator proposes mid-loop has no
natural place in Phase 4.1 (which has already finished for that target). It
gets inserted directly as `GATE1_APPROVED` with `path_id=NULL` (exactly the
case `DR-SCHEMA-05`'s note about null `path_id` anticipates), then still
receives a fresh Tier 0 check when `run_gated_task` processes it — it just
never goes through the Hermes-3 semantic tier a second time.

**Where it's used:** `vapt_agent/orchestrator/phase_lifecycle.py::run_phase_4_2`.

**What changes if disapproved:** Route follow-up tasks through
`run_gate1_semantic` too before they're eligible for command generation.

---

## 32. REAL GAP: nothing yet creates `verified_vulnerabilities` CANDIDATE rows for Gate 3 to adjudicate

**Not a judgment call — a missing piece, flagged not hidden.**
`FR-COUNCIL-13` assumes candidate findings already exist in
`verified_vulnerabilities` with `status='CANDIDATE'`; nothing in Milestones
1-7 (bridge, sanitize, discovered_entities, loop_bounds, or this new
orchestrator loop) ever inserts one. `run_phase_4_3` correctly does nothing
when there are zero candidates (tested as a valid no-op) — but this means
Phase 4.3 has nothing real to adjudicate until a candidate-detection step
exists somewhere upstream (likely Phase 4.2's follow-up/tool-output-review
logic, or its own dedicated step).

**Where it's used:** `vapt_agent/orchestrator/phase_lifecycle.py::run_phase_4_3`.

**What changes if disapproved:** Build the missing step — something that
looks at `discovered_entities`/tool output and decides "this looks like a
candidate vulnerability" and inserts the `verified_vulnerabilities` row.

---

## 33. `known_secrets` for FR-COUNCIL-18 redaction defaults to an empty list (no-op passthrough)

**What I assumed:** Redaction needs a list of known raw secret values to
find-and-replace, but nothing anywhere in this codebase yet detects "this
piece of tool output is a secret" (a credential, token, cookie value, etc.)
— that detection step doesn't exist. `run_phase_4_3` passes an empty list to
`redact_evidence`, so evidence currently passes through un-redacted (not
wrong, just doing nothing yet, since there's nothing to redact against).

**Where it's used:** `vapt_agent/orchestrator/phase_lifecycle.py::run_phase_4_3`.

**What changes if disapproved:** Build a secret-detection step (regex-based
credential/token/cookie pattern matching over raw tool output, most
naturally living in `bridge/sanitize.py` alongside the existing
provenance-tagging pipeline) that produces the `known_secrets` list this
function needs.

---

## 34. Session-budget check happens after the Operator loads for Phase 4.2, not before

**What I assumed:** `is_session_budget_exceeded` is checked inside the
Phase 4.2 loop, which only starts after the Operator model has already been
loaded — so an already-expired budget still costs one load/unload pair
before the loop notices and stops. Simpler than adding a special pre-load
budget check, and the cost is bounded (one model swap, not repeated).

**Where it's used:** `vapt_agent/orchestrator/phase_lifecycle.py::run_phase_4_2`.

**What changes if disapproved:** Add an explicit pre-load budget check so an
already-expired session never loads the Operator at all.

---

## 35. NFR-RES-06 swap-growth abnormal threshold defaults to 2 GiB/session

**What I assumed:** `NFR-RES-06` requires tracking cumulative swap bytes
paged during hibernation and flagging "abnormal growth," but names no
specific threshold. Defaulted `check_swap_growth`'s
`abnormal_threshold_bytes` to 2 GiB.

**Where it's used:** `vapt_agent/orchestrator/hibernation.py::check_swap_growth`.

**What changes if disapproved:** Pick a different number (or make it a
config value like the other thresholds in `vapt_agent.config.yaml`).

---

## 36. Swap-tracking functions are standalone, not yet wired into a session-start/session-end call site

**Sequencing note, not a behavioral choice** — same pattern as items #11/#12.
`read_cumulative_pages_swapped_out`/`swap_bytes_paged_since`/
`check_swap_growth` (`vapt_agent/orchestrator/hibernation.py`) are built and
tested, but nothing yet records a baseline at hibernation-start or checks
growth at hibernation-end — there's no single "session start" event to hang
that on yet (same gap as `ensure_phase42_started`). Ready for whichever code
ends up owning that lifecycle.

---

## 37. NFR-RES-05's "≤4 of 8 E-core threads for concurrent tool subprocesses" is currently vacuously satisfied

**Not a judgment call — a note on current applicability.** The Phase 4.2
loop as built (`orchestrator/phase_lifecycle.py::run_phase_4_2`) executes
one task at a time, synchronously — there is no concurrent tool subprocess
execution anywhere in this codebase yet. `NFR-RES-05`'s 4-thread cap on
concurrent tool subprocesses has nothing to violate yet (0 ≤ 4). If/when
true concurrent execution is ever built (the docs themselves note this as a
possible future direction — overlapping tool I/O with the next model's
output parsing), a real thread/process-count limiter enforcing this cap
will need to be added at that point; nothing to fix today.

---

## 16. Council role wrappers' user-message format is plain labeled text, not JSON

**What I assumed:** Doc 14 specifies each role's *system* prompt in full but
never gives a literal user-message template. The wrappers build a plain
text block (e.g. `"finding_id: {id}\n\nRAW EVIDENCE:\n{tagged}"`) rather than
a JSON-structured user message, on the reasoning that the system prompt
already mandates JSON-only *output* and doesn't require JSON-structured
*input*.

**Where it's used:** All five `vapt_agent/council/*.py` role wrappers.

**What changes if disapproved:** Change the user-message construction to
whatever format is preferred (e.g. a JSON object of the same fields).

---

## 17. The Operator role wrapper (`vapt_agent/council/operator.py`) does not exist yet

**Note (not an assumption to approve/reject, just a gap to be aware of):**
Milestone 4's role-wrapper batch covered Strategist, Gate 1 semantic tier,
Adjudicator, Reporter, and Offline Linter — five of the six prompted roles.
The Operator (`Qwen2.5-Coder-7B-Instruct`) is the most tool-execution-critical
role and per the roadmap is meant to be the *first* model wired in
end-to-end (Milestone 3), separately from this batch — it still needs its
own wrapper module following the same pattern as the other five, using
`validate_operator_command`/`validate_operator_followup` from
`engine/schemas.py` (already built) and the Operator role block already
stored in `council/prompts.py`.

---

## 38. REAL FINDING (fixed, not just flagged): a timed-out chat completion now forcibly kills the resident process

**What happened:** live-tested against the real Strategist model
(DeepSeek-R1-0528-Qwen3-8B) during capstone integration testing
(2026-09-02) — one call entered an abnormally long reasoning loop.
`chat_completion`'s client-side timeout (900s) fired and the Python call
raised, but the underlying `llama-server` process kept generating
server-side — confirmed still consuming ~480% CPU **89 minutes** later,
never stopped by the client abandoning its HTTP wait alone.

**Fix (already applied, not pending approval — this is a correctness/safety
bug fix, not a judgment call):** `chat_completion` now catches the timeout,
forcibly terminates the resident process via the existing `_terminate`
(SIGTERM, then SIGKILL after a grace period, verified OS-level exit — same
mechanism `unload()` uses), clears `_current`, and raises a new
`EngineUnresponsiveError` so the caller knows both "no answer" and "the
process is confirmed gone, not orphaned." Directly closes part of
`FR-GATE-08`'s "detect unresponsive engine" requirement — the "attempt one
restart, escalate to PAUSED on repeated failure" half of that requirement
still belongs to a real Phase 4 retry/pause loop, which doesn't exist yet
(no live orchestrator loop — see items #11-14).

**Where it's used:** `vapt_agent/engine/client.py::LlamaCppEngineClient.chat_completion`.
Regression test: `tests/test_engine_client.py::test_chat_completion_timeout_forcibly_kills_the_stuck_process`
(uses a fake server with an injectable response delay, not a real 900s wait).

**Not changed, flagged for awareness only:** all role wrappers call
`chat_completion` at `temperature=0.0` (greedy decoding) — the reasoning
loop above may be a known failure mode of greedy decoding on some reasoning
models (no stochastic escape from a repetition cycle). I did not change the
temperature default; that's a behavioral/determinism trade-off worth a
deliberate decision, not something to flip silently as a side effect of this
bug fix.

**Follow-up diagnostic (2026-09-03), ruling out one hypothesis:** re-tested
in isolation with `max_tokens=4096` explicitly capped (shipped code still
passes no `max_tokens` for any role — this was a read-only diagnostic call,
not a code change) and a shorter `timeout_s=420`. At this host's measured
throughput (~17-40 tok/s from the smoke-test log), 4096 tokens should
complete in well under 240s if the model were simply generating a very long
but *finite* response. **It still hit the full 420s timeout with zero
response.** This rules out "unbounded reasoning trace eventually finishes,
just slowly" as the explanation — a hard output-length cap alone does not
fix it. The remaining plausible causes are (a) `response_format:
json_object`'s grammar-constrained decoding interacting badly with this
model's `<think>...</think>` reasoning-then-answer output shape (grammar-
constrained sampling can be drastically slower per token, especially before
the grammar's start symbol is reached), or (b) a genuine hang/deadlock in
generation rather than a slow-but-live one — this diagnostic pass didn't
capture `llama-server`'s own stdout/stderr (client.py spawns it into
`DEVNULL`) or live CPU-utilization samples during the stuck window, so (a)
vs (b) is not yet distinguished. **Not silently patched** — see the open
question this raises, put to the operator directly rather than guessed at,
since every fix (drop `response_format` for this role and parse free-form
output instead, swap the Strategist model, raise the timeout further, or
accept periodic `GATE1`-adjacent retries as a first-class flow) is a real
architectural trade-off.

**Second follow-up diagnostic (2026-09-03), ruling out hypothesis (a) too:**
put the operator the question above via `AskUserQuestion` (recommended
option: investigate hang-vs-slow first); got no response after 600s, so
proceeded with the cheapest remaining test rather than block entirely — same
prompt, same model, `response_format` dropped completely (no JSON-mode
grammar at all), `max_tokens=2048`, `timeout_s=300`. **Still hit the full
300s timeout with zero response.** This rules out grammar-constrained
decoding as the cause too — the hang happens even on a plain, unconstrained
chat completion. Two independent hypotheses now falsified by direct testing
(unbounded generation length, and JSON-grammar interaction); a genuine
hang/deadlock in `llama-server` itself, or a pathological reasoning loop
triggered by this specific prompt *content* (system role-block + this
target/scope shape) rather than any sampling parameter, are the remaining
candidates — consistent with the original 2026-09-02 finding of this being
"a real, reproducible tendency... on this exact prompt shape" (this diagnostic
used a *different*, synthetic target/scope, and still reproduced the hang,
which weakens "this one exact prompt" as the trigger and strengthens "this
role's prompt shape / prompt length in general" as the trigger).

**Stopping further live-model diagnostic spend here** (2 real runs so far,
~13 minutes of full-RAM model residency between them, both ending in a
forced-kill with zero signal beyond "still no response") without further
operator direction — the next useful step (live CPU/log capture during a
stuck call to distinguish true hang vs. pathologically slow-but-live
generation; or a content change — shortening/restructuring the Strategist
system prompt; or accepting a much longer timeout; or swapping the
Strategist model) is a real trade-off, not a default I should pick unasked
a second time after the first attempt at asking went unanswered.

**Where it's used:** same prompt-construction call sites
(`vapt_agent/council/prompts.py::ROLE_BLOCK_STRATEGIST`/`build_system_prompt`,
`vapt_agent/council/strategist.py::run_strategist`) — nothing here changed
shipped code; both diagnostics were throwaway scripts under this session's
scratchpad, not committed to the repo.

**What changes if disapproved:** nothing to revert — no shipped code was
touched by either diagnostic. This entry is a record of a real, still-open
finding, not a pending code change.

---

## 39. Three new Tier 1 tools integrated from the prior Claude-Code toolkit (2026-09-03)

**What I did:** per operator request, integrated three scripts flagged as
"genuinely additive Tier 1 candidates" in `16-Actual-Setup-Reuse-and-
Integration-Map.md` §2c but never actually wired in: `jwt_scanner.py`
(pure-stdlib JWT alg:none/RS256→HS256-confusion/secret-crack/static
analysis), `oob_listener.py` (interactsh-based blind-vuln OOB payload
generation + correlation), `dom_xss_harness.py` (Playwright-driven real DOM
XSS execution confirmation). Logic ported verbatim (not rewritten) into
`vapt_agent/bridge/tier1/tools/*.py`, each with its own schema in
`vapt_agent/bridge/tier1/schemas/*.yaml`.

**New mechanism added:** `bridge/tier1/schema.py` now supports a `bundled:
true` YAML flag — when set, `binary` is resolved against
`BUNDLED_TOOLS_DIR` (`bridge/tier1/tools/`) at schema-load time instead of
being looked up on the system `PATH`. This is additive only; every existing
schema (nmap, sqlmap, etc.) is untouched and still resolves via `PATH` as
before.

**Confirmed at integration time (2026-09-03), not yet installed:**
- `interactsh-client` (Go binary) — needed only for `oob_listener.py
  --listen`; `--payloads`/`--correlate` are fully offline and work now.
- `playwright` (Python package) + Chromium — needed for
  `dom_xss_harness.py`'s actual browser run; without it, the tool correctly
  exits 127 with an install hint (verified live, not just claimed) rather
  than crashing.

**Where it's used:** `vapt_agent/bridge/tier1/schema.py` (the `bundled`
mechanism), `vapt_agent/bridge/tier1/tools/{jwt_scanner,oob_listener,
dom_xss_harness}.py`, `vapt_agent/bridge/tier1/schemas/{jwt_scanner,
oob_listener,dom_xss_harness}.yaml`. Real end-to-end tests (no mocking):
`tests/test_tier1_jwt_scanner.py`, `tests/test_tier1_oob_listener.py`,
`tests/test_tier1_dom_xss_harness.py`.

**What changes if disapproved:** Remove the three schemas/scripts and the
`bundled` loader mechanism; the rest of the Tier 1 catalog (nmap, sqlmap,
etc.) is completely unaffected either way.

**Not yet done, flagged for awareness:** `Actual-Setup/tools/port_scanner.py`
(overlaps existing nmap/masscan Tier 1 tools — doc 16 already flagged this as
likely-redundant, not integrated) and `sast_scan.py` (explicitly out of
scope — this is a black-box/grey-box network VAPT tool, no source-code-access
mode) were deliberately left out, matching doc 16's own analysis. The 15
"coupled" scripts (pull in that toolkit's own `memory`/`tools` package
internals) and the remaining not-yet-classified standalone scripts
(`banner.py`, `dashboard.py`, `mindmap.py`, `prompt_safety.py`, `safe_http.py`,
`waf_encoder.py`, `zero_day_fuzzer.py`) were out of this integration pass's
scope — a separate pass should classify those the same way doc 16 did for
the first batch, porting logic (not the coupled package) where genuinely
valuable.

---

## 40. Six more Tier 1-candidate scripts integrated, closing a gap between two prior passes (2026-09-03)

**What I did:** items #26/asset-classification's "Tier 1 candidates, deferred
to the parallel Tier1-integration effort" table listed six scripts
(`llm_redteam.py`, `cors_scanner.py`, `crlf_scanner.py`, `nosqli_scanner.py`,
`waf_response_analyzer.py`, `visual_triage.py`) on the assumption a separate
in-flight effort would fold them in alongside item #39's three. That effort's
scope had already been fixed to exactly those three and had already
finished — these six were never actually integrated. Per operator request
("have we integrated those files... if not, do it"), read all six in full
(confirmed no real client/engagement data — all placeholder domains) and
closed the gap.

**Five ported as Tier 1 tools**, following item #39's exact `bundled: true`
pattern verbatim: `llm_redteam.py`, `cors_scanner.py`, `crlf_scanner.py`,
`nosqli_scanner.py`, `visual_triage.py` — each with its own
`bridge/tier1/schemas/*.yaml` and a real end-to-end test
(`tests/test_tier1_*.py`, no mocking). `cors_scanner.py`/`crlf_scanner.py`/
`nosqli_scanner.py` each import `safe_urlopen` — a straight drop-in swap to
the already-ported `vapt_agent/bridge/safe_http.py` (same signature), no
other changes needed for that dependency.

**One judgment call — `waf_response_analyzer.py` ported as a plain
importable module instead** (`vapt_agent/bridge/waf_response_analyzer.py`,
no Tier 1 schema): its original CLI has three modes with fundamentally
different shapes — `--calibrate` touches a live URL, but `--classify`/
`--diff` only ever read local files, never the network. Tier 1's schema
model (one fixed argv shape, one timeout class per tool) doesn't cleanly fit
a tool where two-thirds of its modes aren't "run this against a target" at
all — it was designed as a library the old toolkit's `bypass_403.sh` shelled
out to, not a primary Operator-chosen scanning action. Ported as an
importable module instead (same treatment item #26 gave `safe_http.py`/
`sneaky_bits.py`/`waf_encoder.py`): CLI dropped, all classes kept including
the network-touching `BaselineSampler.calibrate()`. **No current call site,
but directly relevant to FR-COUNCIL-14's Gate 3 false-positive checklist**
(explicitly requires ruling out "a WAF/firewall block page" before accepting
a candidate finding) — `ResponseClassifier.classify()` is ready-made,
evidence-backed machinery for that exact check, for whichever future
Adjudicator/Gate3 code path wires it in. If disapproved: delete the file and
its test; nothing else references it.

**Real bug found and fixed during integration testing (not a judgment
call):** `crlf_scanner.py`'s `_send()` wraps its request in `except (...,
ValueError)`, written assuming urllib raises `ValueError` when a URL
contains a raw `\r\n` (one of its 9 CRLF payload variants embeds a literal
`\r\n`). On this Python it's actually `http.client.InvalidURL` — not a
`ValueError` subclass — so that one payload variant crashed the entire scan
instead of gracefully recording "no injection" and moving to the next
payload. Confirmed live (reproduced the traceback, then the fix). Now also
caught explicitly; comment added explaining why.

**Confirmed at integration time, relevant to `visual_triage.py`:**
`eyewitness` (the real Red Siege tool, and the script's default
highest-priority screenshotter) IS installed and works — verified via a real
~3s invocation against a closed local port. `aquatone` is NOT installed. The
`httpx` binary on this machine's PATH is **not** ProjectDiscovery's httpx
recon tool — it's the unrelated Python-httpx HTTP client's CLI, which
doesn't accept the flags `visual_triage.py --tool httpx` would pass it. This
doesn't affect the default (no `--tool` override) path, since `eyewitness`
wins priority, but an explicit `--tool httpx` on this deployment will fail;
documented prominently in the module docstring and the YAML schema's `--tool`
flag description rather than silently left as a trap.

**Where it's used:** `vapt_agent/bridge/tier1/tools/{llm_redteam,
cors_scanner,crlf_scanner,nosqli_scanner,visual_triage}.py`,
`vapt_agent/bridge/tier1/schemas/{llm_redteam,cors_scanner,crlf_scanner,
nosqli_scanner,visual_triage}.yaml`, `vapt_agent/bridge/
waf_response_analyzer.py`. Tests: `tests/test_tier1_{llm_redteam,
cors_scanner,crlf_scanner,nosqli_scanner,visual_triage}.py`,
`tests/test_waf_response_analyzer.py`. `ASSET-CLASSIFICATION.md` updated to
reflect the actual outcome (349 → 390 passing tests; `ruff check .` and
`mypy vapt_agent/ --ignore-missing-imports` both clean).

**What changes if disapproved:** remove the five new Tier 1 schemas/scripts/
tests and the `waf_response_analyzer.py` module/test; the rest of the Tier 1
catalog and the three item-#39 tools are completely unaffected either way.

## 41. `zero_day_fuzzer.py` integrated as an 11th `bundled: true` Tier 1 tool, with a new `--findings-dir` flag (2026-09-03)

**What I did:** `ASSET-CLASSIFICATION.md` (from item #26's original pass)
flagged this one file as "left honestly unclassified" — 597 lines, not read
in depth given that pass's time budget. Per the operator's standing request
to integrate every usable file from `Actual-Setup`/`Standalone-Engine-
Reference`, I read it in full myself (only generic placeholder domains
throughout — `example.com`/`evil.com`/`target.com` — no real client/
engagement data) and judged it genuinely valuable: it's the only integrated
tool that sweeps HTTP method tampering/XST, Host-header injection, CORS
misconfig, missing security headers, path traversal, CRLF injection,
open-redirect bypasses, and 403 bypass in one pass, plus (`--deep`) prototype
pollution and cache poisoning. Handled directly (one file) rather than
spawning another fork, following the exact `bundled: true` pattern items
#39/#40 already established.

**One functional change from the original, not just a hygiene fix:** the
original computed its on-disk findings directory as two `os.path.dirname()`
calls up from `__file__` — assuming a specific toolkit layout
(`<toolkit_root>/findings/<domain>/zero_day/`). As a project-bundled Tier 1
tool, `__file__` instead resolves inside this project's installed package
tree, which is both semantically wrong and may not be writable at all. Added
a new `--findings-dir` CLI flag (the `ZeroDayFuzzer` class already accepted
a `findings_dir` constructor argument; `argparse` just never exposed it),
defaulting to a tempfile-safe location
(`tempfile.gettempdir()/vapt_agent_zero_day_findings`). This is a
best-effort *secondary* copy either way — Tier 1's own raw-stdout capture
(DR-ARTIFACT-01/02) is the evidence of record regardless of whether this
script's own JSON/text files land anywhere useful.

**Ruff hygiene fixes only, no other logic changes:** `preexec_fn=os.setsid`
→ `start_new_session=True` (matches this project's own `bridge/executor.py`
convention); `datetime.now()` → `datetime.now(UTC)` at both call sites
(timestamp/scan_date); several unused tuple-unpack variables prefixed with
`_` (the original often unpacks `status, headers, body` from `curl_request`
but only reads one or two of the three per call site); three nested-`if`
pairs collapsed to single `if ... and ...:` statements; `list(headers.keys())
[0]` → `next(iter(headers.keys()))` in `test_403_bypass`. No behavioral
change from any of these.

**Where it's used:**
`vapt_agent/bridge/tier1/tools/zero_day_fuzzer.py`,
`vapt_agent/bridge/tier1/schemas/zero_day_fuzzer.yaml`,
`tests/test_tier1_zero_day_fuzzer.py` (9 tests). `tests/
test_bridge_tier1_schema.py` updated to expect 20 Tier 1 schemas total.
`ASSET-CLASSIFICATION.md` updated to move this file out of "left honestly
unclassified" into a proper Ported entry (390 → 399 passing tests; `ruff
check .` and `mypy vapt_agent/ --ignore-missing-imports` both clean).

**What changes if disapproved:** remove `zero_day_fuzzer.py`, its schema, and
its test file; drop it from `test_bridge_tier1_schema.py`'s expected-tools
set. Nothing else in the Tier 1 catalog references it.

---

## 42. Pulled a major source-repo update (decisions #56/#57) — `prompts.py` resynced verbatim against doc 14; Milestone 9 (8 new capability domains + Human Checkpoint Gate + Monitor mode) not yet started

**What happened:** per operator instruction ("fetch the new data from source
repo on GitHub... a lot has changed"), fetched and fast-forward-merged one
new upstream commit (`c367790`, "Formalize claude-bug-bounty mining sweep and
extended capability domains") into `source/`. Before pulling, found 3
uncommitted local deletions in `Standalone-Engine-Reference/report-
generators/` — restored them from git history as the safe default not
knowing if they were intentional; operator then clarified they were
deliberately deleted and should be removed from GitHub too, so re-deleted
and pushed that as a real commit (`a051df6`) at the operator's explicit
instruction. Read all 2 new docs (`19-Extended-Capability-Domains.md`,
`20-Human-Checkpoint-and-Escalation-Safety-Catalog.md`) and the diffs of
every changed doc (`00`, `01`, `03`, `07`-`11`, `13`-`17`) in full.

**Immediately reconciled (small, mechanical, zero external dependency):**
`vapt_agent/council/prompts.py`'s module docstring claims its role-block text
"is copied verbatim from" doc 14 — the new commit added substantial new
Strategist/Operator/Reporter prompt content (assumption-breaking checklist,
business-context lens, capability-primitive chain reasoning, sibling-endpoint
chaining, client-reverse replay-first technique, Reporter title-format + hard
anti-hedge rule) that wasn't in our prompts.py yet, so the claim had gone
stale. Inserted the new text at the same position doc 14 puts it (verified by
reading doc 14's full current file, not just the diff hunks in isolation).
**Also discovered while doing this:** the Strategist's existing "Reach for a
specific, testable bug class" vulnerability catalog, its "Reasoning
heuristics" list, and the Operator's noise-filter list (FR-COUNCIL-10) have
**never** existed in doc 14 at any point in its git history (checked via `git
log -p --all`) — they were authored directly from the same
`Actual-Setup/skills/` source material during an earlier mining pass, in
different wording, not paraphrased from doc 14. Judgment call: kept them
(genuine supplementary value, nothing contradicts doc 14) rather than
deleting to force strict verbatim-only status, and corrected the module
docstring to say so plainly instead of leaving the inaccurate "all text
below is copied verbatim" claim standing. `ruff`/`mypy`/full `pytest -q`
(399 tests) all still clean after this edit.

**NOT yet started — a genuinely large scope expansion, not a small
follow-up:** decision #57 adds a whole new Milestone 9 (`15`'s own new
section) on top of the already-complete core system (Milestones 0-8):
- A new **Human Checkpoint Gate** (`FR-CHECKPOINT-01..05`, `DR-SCHEMA-18`
  `checkpoint_events` table, new `PAUSED_AWAITING_CHECKPOINT` engagement
  status, new `approve-checkpoint`/`deny-checkpoint` CLI commands, new
  `security/checkpoint_gate.py` classifier) — a real architectural addition
  touching the orchestrator, CLI, and schema, not a bolt-on.
- A new **Monitor mode** (`FR-MONITOR-01..04`, `DR-SCHEMA-17`
  `monitoring_baseline` table, new `monitor` CLI command, new
  `monitor/monitor_engine.py`) — deliberately outside the engagement
  lifecycle, model-free.
- **Schema generalization** (`DR-SCHEMA-15/16`): `targets.target_type`
  discriminator (`NETWORK`/`CONTRACT`/`MOBILE_BINARY`/`CODE_REPO`) and
  `scope_rules.pattern_kind` discriminator (`NETWORK`/`EXACT_IDENTIFIER`/
  `PATH_GLOB`), each needing its own scope-check code path
  (`FR-COUNCIL-03a` must branch on both).
- **8 new capability domains** (`FR-VULNCLASS`/`FR-WEB3`/`FR-MOBILE`/
  `FR-GRAPHQL`/`FR-CICD`/`FR-CRED`/`FR-CODEACCESS`/`FR-ARGUS`), several with
  **real external dependencies not installed on this machine and, in some
  cases, not obtainable by me at all**: Foundry (`forge`/`cast`/`anvil`) +
  a third-party mainnet-fork RPC endpoint (`FR-WEB3-03`); `adb` + a
  **physical** Android device, and a **physical jailbroken** iOS device —
  no emulator path exists for iOS pinning bypass at all (`FR-MOBILE-05/06`);
  an authenticated `gh` CLI session for CI/CD testing (`FR-CICD-02`); a
  CDP-capable headless browser (Playwright/Puppeteer, `AC-DEPENDENCY-17`).
  Doc 15's own Milestone 9 section prescribes a specific build order
  (schema → checkpoint gate → GraphQL/Argus → code-access → web3 → mobile →
  CI/CD/credential-attack/anti-forensics → monitor), explicitly sequencing
  the checkpoint-gated, highest-stakes domains last.

**Why this wasn't started autonomously in the same turn:** unlike the
zero_day_fuzzer integration or the ruff/mypy fixups, several of the
above genuinely need operator-supplied resources I cannot provide or
substitute for (a physical Android device, a jailbroken iPhone, a funded RPC
API key, a `gh` account willing to have real PRs opened against a real
CI/CD test repo) — building code against them without operator input on
which are actually available would mean guessing at scope for a
multi-week-scale addition, not making a single documented judgment call.
Reported the full digest to the operator and asked how to scope/sequence
Milestone 9 before starting it.

**What changes if disapproved:** nothing destructive has happened —
`prompts.py`'s docstring correction and new text can be reverted with a
single edit if the operator disagrees with keeping the pre-existing
non-doc-14 content; no Milestone 9 code has been written yet at all.

---

## 43. Milestone 9 step 8 built ahead of sequence: Scheduled Monitoring Mode (`FR-MONITOR-01..04`, `DR-SCHEMA-17`) (2026-09-03)

**What I did:** built `vapt_agent/monitor/monitor_engine.py` +
`vapt_agent/cli/monitor.py` (new `vaptctl monitor --engagement-id <id>`
command). Doc 15 lists this as Milestone 9's *last* build step but explicitly
notes it's "independent of everything else in this milestone; can be built
any time after step 1 [schema]" — built now, in parallel with the Human
Checkpoint Gate (a separate fork), since both are genuinely independent of
each other and of the still-undecided domain-scoping question (which
hardware/API-gated domains to actually build).

**Judgment call — subdomain enumeration mechanism (the one real limitation
worth flagging):** `FR-MONITOR-01` names "subdomain-enumeration diff" for
`NETWORK` targets but doesn't specify a mechanism. A real passive-recon-grade
implementation (subfinder/crt.sh certificate-transparency lookups, in the
spirit of the `web2-recon` skill already mined into the Strategist prompt)
would be a genuinely new tool/network-dependency integration, out of scope
for what doc 15 frames as a small, "independent" build step. Implemented
instead: a fixed 15-entry candidate-subdomain-prefix list (`www`, `api`,
`admin`, `dev`, `staging`, `test`, `mail`, `vpn`, `portal`, `app`, `beta`,
`internal`, `gateway`, `auth`, `cdn`) resolved via real DNS
(`socket.gethostbyname`, injectable for tests) — real and deterministic, but
a materially narrower stand-in than full passive enumeration (it can only
ever detect a new/removed subdomain whose *name* is already on this fixed
list; it will miss e.g. `newfeature.target.com` entirely). Documented
prominently in the module docstring, not silently presented as equivalent to
a full recon pass. `REPO_COMMIT_HEAD` (for `CODE_REPO` targets) has no such
gap — it's a real `git ls-remote <repo> HEAD`, fully general.

**Judgment call — first-run baseline semantics:** `DR-SCHEMA-17` doesn't
state what happens on a target's very first `monitor` run (no existing
`monitoring_baseline` row). Decided: establish the baseline silently
(`diff_detected=False`), never report a diff against nothing — matches
`DR-SCHEMA-17`'s own note that `last_diff_detected_at` is "NULL if never
diffed," which only makes sense if a first observation isn't itself treated
as a diff.

**Judgment call — `discovered_entities.entity_value` format:** not specified
by `DR-SCHEMA-17`/`FR-MONITOR-01`. For `SUBDOMAIN_SET`, used
`+added.sub.com; -removed.sub.com` (only naming what actually changed, not
the full new set). For `REPO_COMMIT_HEAD`, used `old_sha..new_sha` (git's own
own range-diff convention). Both are just descriptive text in a single
`TEXT NOT NULL` column — trivially changeable if the operator wants a
different format (e.g. structured JSON) once a real consumer of this field
exists.

**Confirmed, not a judgment call — architectural constraints verified by
test, not just followed by convention:** `run_monitor`/`check_target` never
create an `engagements` row, never touch `task_queue`, never check
`engagement_lock_slot`, and `monitor_engine.py` imports nothing from
`vapt_agent.council`/`vapt_agent.engine`/`vapt_agent.orchestrator` — this
last one is verified by a real AST-based import-inspection test (not a
docstring claim), specifically checking `ast.Import`/`ast.ImportFrom` nodes
rather than raw substring search (a substring search falsely flags the
module's own docstring, which necessarily mentions "hibernation"/"engine" to
explain what the module must NOT do).

**Where it's used:** `vapt_agent/monitor/monitor_engine.py`,
`vapt_agent/cli/monitor.py`, registered in `vapt_agent/cli/main.py`. Tests:
`tests/test_monitor_engine.py` (14 tests — pure-function unit tests for
`enumerate_subdomains`/`get_repo_commit_head`; real-SQLite integration tests
for `check_target`/`run_monitor` covering every `TP-MONITOR` row from `09`,
including a real throwaway git repo for the `REPO_COMMIT_HEAD` path and a
real CLI invocation via `click.testing.CliRunner`). `ruff check` and `mypy
--ignore-missing-imports` both clean on every file this task touched;
`pytest -q` passes in full (422 tests, up from 408 after the schema-
generalization step — includes a concurrently-running parallel fork's
Human Checkpoint Gate work, not just this task's own 14).

**What changes if disapproved:** delete `vapt_agent/monitor/`,
`vapt_agent/cli/monitor.py`, its two-line registration in
`vapt_agent/cli/main.py`, and `tests/test_monitor_engine.py`. Nothing else
in the codebase references any of this yet (`FR-MONITOR` is independent of
every other Milestone 9 piece by design).

## 44. Milestone 9 step 2 built: the Human Checkpoint Gate (`FR-CHECKPOINT-01..05`, `DR-SCHEMA-18`) (2026-09-03)

**What I built:** `vapt_agent/security/checkpoint_gate.py` — a deterministic
classifier (`classify_checkpoint_action`) tagging a proposed task against the
fixed, closed four-class list (`ANTI_FORENSICS`/`LIVE_CREDENTIAL_SPRAY`/
`CICD_EXTERNAL_ARTIFACT`/`DEPENDENCY_CONFUSION_PUBLISH`); `raise_checkpoint`
(creates the `checkpoint_events` row, pauses the engagement, marks the task
`AWAITING_CHECKPOINT`); `approve_checkpoint`/`deny_checkpoint` (the
`FR-CHECKPOINT-04` decision logic); and `validate_anti_forensics_flags`
(`FR-CHECKPOINT-05`'s stricter `start`-time gate). Wired into the real
`council/task_runner.py::run_gated_task` call site — the same function that
already enforces `FR-TOOL-06a/b`'s three high-risk opt-in categories — right
after Gate 2 passes and before any subprocess spawns, using the task's
`tool_name` (Tier 1) or resolved-binary basename (Tier 2) as the
classification key. New CLI commands `approve-checkpoint`/`deny-checkpoint`
(mirroring `approve_report.py`'s structure), plus the six new `start` flags
(`--allow-anti-forensics`/`--white-cell-contact`/`--attest-disclosure`/
`--allow-live-credential-spray`/`--allow-cicd-external-artifact`/
`--allow-dependency-confusion-publish`) and `FR-CHECKPOINT-05`'s validation,
matching doc 13's CLI grammar exactly (these six are `start`-only, never on
`resume` — doc 13's own grammar table omits them from `resume`, unlike the
three `FR-TOOL-06a` flags, so I did not add them there or to
`engagement_flag_history`'s audit trail, which stays scoped to flags that
can actually change mid-engagement).

**Real, not-yet-resolved judgment call — placeholder tool-name conventions
for the four action classes.** None of the four classes has an actual
Tier 1/Tier 2 tool built yet (`FR-CRED`/`FR-CICD`/anti-forensics/
`FR-VULNCLASS-03`'s dependency-confusion publisher are separate, later
Milestone-9 sub-tasks — doc 15's own build order puts them last specifically
so this gate exists and is tested in isolation first). Rather than leave the
classifier abstract/untested against any real call site, I picked concrete
placeholder tool-name strings (`credential_spray`, `cicd_open_pr`/
`cicd_trigger_workflow`/`cicd_modify_secrets`, `dependency_confusion_publish`,
`anti_forensics_action`) as a fixed, closed matching list — a real decision
that **will** need revisiting once each domain's actual tool is named and
built; these are forward-looking placeholders, not verified against any real
binary or Tier 1 schema. Flagged explicitly rather than silently treated as
final.

**Real judgment call — the "current-milestone honesty" pattern, extended
here.** `cli/pause.py`/`cli/resume.py`/`security/kill_switch.py` already
document that no long-lived Phase 4 orchestrator loop exists yet — `pause`
sets `status='PAUSED'` and clears `orchestrator_pid` directly rather than
truly signaling a live process, and `resume` sets a fresh `orchestrator_pid`
directly rather than truly spawning one. I followed the exact same pattern
for `approve_checkpoint`/`deny_checkpoint`: both set the engagement back to
`IN_PROGRESS` with `orchestrator_pid = NULL` directly, and mark the task
`GATE1_APPROVED` (approve) or `BLOCKED_BY_OPERATOR` (deny) — there is no real
mechanism yet that "launches a fresh orchestrator that executes exactly the
one approved task," because no CLI command in this codebase launches a real
persistent orchestrator process at all yet. This is not a shortfall specific
to my task; it is the same, already-accepted gap the rest of `cli/` has.

**Real judgment call — a new `POLICY_REFUSED` task_queue status value,
additive to the schema.** `FR-CHECKPOINT-02` explicitly says to reuse
"the same pattern as `FR-TOOL-06b`," whose own `POLICY_REFUSED` concept
currently only exists at the `bridge/tier2.py::Tier2Result` level (`rule=
"policy_refused"`) — I found, while wiring my own code, that `task_runner.py`
does **not** currently persist a `POLICY_REFUSED` task_queue.status for that
pre-existing Tier 2 case at all (it unconditionally marks the task
`EXECUTED` after calling `run_security_command`, regardless of
`Tier2Result.allowed`). This looks like a pre-existing gap unrelated to my
task — I did **not** touch that existing Tier 2 code path (out of scope for
this directive, and risky to change without understanding why it was left
that way). I only added `'POLICY_REFUSED'` to `task_queue.status`'s CHECK
constraint and used it for my own new checkpoint-flag-unset early return, so
this new status value now exists but is only actually reachable via the
checkpoint gate today, not via ordinary Tier 2 policy refusal. Flagged for
the operator's awareness, not fixed, since fixing the pre-existing Tier 2
gap is a different, separate task.

**Adjacent fix, not a judgment call — `FR-CTRL-09`'s single-engagement lock
check in `cli/start.py` was missing the new `PAUSED_AWAITING_CHECKPOINT`
status.** The schema-generalization step (this same day, a different
concurrent task) added `PAUSED_AWAITING_CHECKPOINT` to `engagements.status`
and its `engagement_lock_slot` virtual column, but `start.py`'s own
hardcoded `WHERE status IN (...)` pre-check still only listed
`'IN_PROGRESS','PAUSED'` — a real bug that would have let a second `start`
succeed while an engagement was checkpoint-paused, silently breaking the
lock invariant this whole system depends on for hibernation safety. Fixed
directly (added the third status to both the pre-check and its error
message) since leaving it broken would have made my own new pause mechanism
unsafe.

**Where it's used:** `vapt_agent/security/checkpoint_gate.py`,
`vapt_agent/cli/{approve_checkpoint,deny_checkpoint}.py` (registered in
`vapt_agent/cli/main.py`), `vapt_agent/cli/start.py` (six new flags +
`FR-CHECKPOINT-05` validation + the `PAUSED_AWAITING_CHECKPOINT` lock fix),
`vapt_agent/council/task_runner.py` (the real `run_gated_task` wiring),
`vapt_agent/data/schema.sql` (six new `engagements` columns, the new
`POLICY_REFUSED` task_queue status). Tests: `tests/
test_security_checkpoint_gate.py` (21 tests covering every `TP-CHECKPOINT`
row from `09` — unset-flag refusal with no checkpoint row created,
matching-flag classification+pause, the no-auto-timeout structural check,
approve/deny, anti-forensics' two-field gate, the live-spray rationale's
hostname+lockout-percentage content, and CI/CD independence from the three
pre-existing flags), `tests/test_cli_checkpoint.py` (8 CLI-level tests via
`CliRunner`). `ruff check .` and `mypy vapt_agent/ --ignore-missing-imports`
both clean; full `pytest -q` passes (443 tests). One unrelated, pre-existing
environmental test failure was observed during this work
(`tests/test_preflight.py::test_check_inference_engine_reports_missing_
binary_as_documented_failure`) caused by a real `llama-server` process (from
a concurrent capstone/diagnostic task elsewhere in this session) occupying
port 11434 — confirmed unrelated to any file this task touched, not fixed
here since it isn't this task's process to manage.

**What changes if disapproved:** delete `vapt_agent/security/
checkpoint_gate.py`, the two new CLI command files and their `main.py`
registrations, revert `start.py`'s six new flags/validation (but keep its
`PAUSED_AWAITING_CHECKPOINT` lock-check fix — that's a real bug fix,
independent of whether the rest of this feature is approved), revert
`task_runner.py`'s checkpoint-gate wiring, and remove the six new
`engagements` columns and the `POLICY_REFUSED` status value from
`schema.sql`. Delete both new test files.

---

## 45. REAL FINDINGS (both fixed, root-caused with live evidence, not guessed): the Strategist "hang" was unbounded output length, not a bug — plus a real Gate 1 JSON-strictness bug found immediately after (2026-09-03)

**What happened:** per explicit operator instruction ("isolate the cause...
check logs... do a root cause analysis... search on web... keep retrying
until it succeeds"), root-caused item #38's still-open Strategist
hang/timeout finding using real, live diagnostics rather than continuing to
guess. Sequence of evidence, each diagnostic run against the real
`DeepSeek-R1-0528-Qwen3-8B` GGUF weights on this actual machine (not
mocked):

1. **Capped `max_tokens=4096`, `timeout_s=420`** — still zero response.
   Rules out "eventually finishes, just slowly" for a bounded generation.
2. **Dropped `response_format=json_object` entirely, `max_tokens=2048`,
   `timeout_s=300`** — still zero response. Rules out JSON-grammar-mode
   conflict with the model's `<think>` reasoning style (a real, web-search-
   confirmed llama.cpp/DeepSeek-R1 issue class — github.com/ggml-org/
   llama.cpp/issues/11336 — but not what's happening here, confirmed by
   testing rather than assumed from the search result alone).
3. **Captured `llama-server`'s own timing log directly** (previously
   discarded to `DEVNULL`) with a small `max_tokens=128` budget: real,
   measured throughput on this CPU (Intel Ultra 5 125H) for this exact
   model — **prompt eval ~11-16 tok/s, generation ~4.8-5.2 tok/s**. At that
   generation speed, 4096 tokens alone needs ~800s — explaining both prior
   timeouts as genuinely insufficient budget, not a hang. Also tested
   whether more threads help (`-t 18` vs. the mandated `-t 8` P-core pin,
   `FR-GATE-03`): prompt eval improved (~11→16 tok/s) but generation barely
   moved (~4.8→5.2 tok/s) — generation is memory-bandwidth-bound on this
   CPU, not thread-count-bound; did not change the P-core pinning policy
   given the marginal, uncertain benefit and the E-core-reservation
   rationale documented for `FR-GATE-03`.
4. **The actual smoking gun:** a clean, uncontended run with `max_tokens=4096`,
   `timeout_s=1200` (20 minutes) **still didn't finish**, but reconstructing
   the real generated token stream from `llama-server`'s verbose log showed
   the model was NOT stuck or repeating — it was still inside `<think>` at
   token 3517, making steady (if slowing, ~5→3.4 tok/s as context grew)
   forward progress. A second uncontended run confirmed the model *does*
   reach valid JSON eventually — reconstructing that run's token stream
   showed well-formed, on-topic, schema-correct `attack_paths` entries (SSRF,
   IDOR, mass-assignment hypotheses, real substance, not garbage) — the
   model was simply proposing an unbounded, very long list of hypotheses,
   one at a time, at ~5 tok/s, which is why no timeout tested was ever long
   enough.

**Fix applied (a prompt change, not a code/architecture change):**
`ROLE_BLOCK_STRATEGIST` (`vapt_agent/council/prompts.py`) now explicitly
bounds output to **3-8 hypotheses per call**, stated once in the intro and
reinforced once more immediately before the output schema (repetition aids
instruction-following in smaller models) — with an explicit rationale for
why a short list is fine (`FR-COUNCIL-01`'s task-queue loop calls the
Strategist again with updated findings; there's no benefit to front-loading
every idea into one response, and a real cost in generation time). This is
new prompt content beyond doc 14's own text (doc 14 doesn't specify a
hypothesis-count bound anywhere) — a judgment call grounded directly in
live measured behavior, not a guess. **Verified fixed**: a clean diagnostic
run with the bounded prompt completed in 763.8s (under the existing 900s
default `chat_completion` timeout) and produced valid, schema-conformant
JSON with exactly 4 hypotheses.

**Second real bug found immediately after, via the real shipped
`run_phase_4_1` orchestrator function (not a standalone diagnostic) run
against a fresh, current-schema SQLite DB:** the Strategist call itself now
succeeded end-to-end for the first time all session — but the *next* step,
Gate 1's semantic tier (`Hermes-3-Llama-3.1-8B`), then failed:
`decode_json_content` raised `ValueError: engine response was not valid
JSON despite response_format: Invalid control character at: line 4 column
194`. Root cause: Hermes-3 emitted a raw, literal control character (an
unescaped newline inside a JSON string value, not `\n`) — valid per RFC
8259's own permissive reading (control characters in strings MAY be literal
or escaped), but Python's `json.loads` defaults to strict mode and rejects
it. **Fix:** `vapt_agent/engine/structured.py::decode_json_content` now
calls `json.loads(candidate, strict=False)` — the standard library's own
documented option for exactly this case, not a hand-rolled sanitizer.
Verified with a direct unit reproduction (a literal `\n` embedded in a JSON
string value, previously raised, now parses correctly) plus the existing
`tests/test_engine_structured.py` suite still green.

**Also fixed in passing, a bug in my own diagnostic tooling, not shipped
code:** my `real_phase41_test.py` scratch script re-raised the Gate 1
failure without a `finally`-block cleanup, leaving an orphaned `llama-server`
process (Hermes-3) resident and holding port 11434 — manually terminated;
this transiently broke one preflight test
(`test_check_inference_engine_reports_missing_binary_as_documented_failure`,
which asserts nothing is listening on that port) until cleaned up. Not a
shipped-code issue; noted so a future reader isn't confused by a similar
transient failure during heavy diagnostic work.

**Where it's used:** `vapt_agent/council/prompts.py::ROLE_BLOCK_STRATEGIST`,
`vapt_agent/engine/structured.py::decode_json_content`. Re-running the real
`run_phase_4_1` end-to-end with both fixes in place is in progress as of
this entry.

**What changes if disapproved:** the 3-8 hypothesis bound could be loosened
to a different range (e.g. 5-12) if the operator wants more per-call
breadth at the cost of longer Strategist turns — a simple text edit, no
architecture impact. `strict=False` could be reverted, but doing so would
resurface a real, reproducible crash on legitimate (if RFC-permissively
literal) model output — not recommended without an alternative sanitizer in
its place.

---

## 46. Milestone 9 step 6 built: Mobile Application Pentesting (`FR-MOBILE-01..07`, `MOBILE_BINARY` target type) (2026-09-03)

**What I built:** `vapt_agent/domains/mobile_scope.py` (`check_mobile_tier0`
— a thin wrapper pinning `pattern_kind="EXACT_IDENTIFIER"` against the
target's `package_name`, matching the identity convention other Milestone 9
domains already use for their own EXACT_IDENTIFIER strings; and
`link_or_create_backend_target` — `FR-MOBILE-01`'s "recover the backend
once, then treat it exactly like a NETWORK target and stop reversing"
hand-off, reusing an existing `NETWORK` row for the same host within the
engagement rather than creating a duplicate each time recon touches the
same backend). A new Tier 1 tool, `bridge/tier1/tools/mobile_secrets_sweep.py`
+ its schema (`FR-MOBILE-02`'s static secrets/endpoint sweep — decompiles an
Android APK via `apktool` or extracts an iOS IPA as a plain zip, then greps
the result for the spec's own credential-pattern list and base-URL/endpoint
strings). `FR-MOBILE-03/04`'s pinning-bypass priority order and deeplink/
WebView-bridge injection chain, plus `FR-MOBILE-07`'s N/A criteria and its
near-verbatim "can a remote attacker with no physical device access do this
right now" framing, folded into the Operator role block in
`vapt_agent/council/prompts.py`.

**Real environmental constraint, handled explicitly rather than faked:**
this machine has `apktool`/`jadx`/`adb` installed (checked directly, not
assumed) but no Android device/emulator, no `frida-tools`/`objection`, and
no physical jailbroken iOS device — `FR-MOBILE-05/06`'s hardware/toolchain
requirements remain unmet for anything beyond the static-analysis step.
Since `apktool` genuinely is present, I used it for real in one test
(against a deliberately invalid `.apk`, proving the real subprocess
integration handles a garbage/non-APK file as a clean, reported failure —
not a crash — rather than mocking the binary or skipping the integration
point entirely). Dynamic instrumentation (`FR-MOBILE-03`'s Frida hooks,
`FR-MOBILE-04`'s live deeplink/WebView testing) has no buildable code
surface without a device at all — not attempted, not stubbed as fake-passing.

**Judgment call — `mobile_secrets_sweep.py`'s `--decompiled-dir` flag (not
in the spec text):** added so the tool's pattern-matching logic is fully
testable against a directory of planted-secret fixture files without
requiring a real, valid APK (which isn't constructible in this environment
— `apktool` needs a genuine binary manifest/resources.arsc, not just a zip
of text files) — also a genuine reuse path if a prior task in the same
engagement already decompiled the same binary. Two-fold rationale
documented directly in the tool's own module docstring.

**Where it's used:** `vapt_agent/domains/mobile_scope.py`,
`vapt_agent/bridge/tier1/tools/mobile_secrets_sweep.py`,
`vapt_agent/bridge/tier1/schemas/mobile_secrets_sweep.yaml`,
`vapt_agent/council/prompts.py::ROLE_BLOCK_OPERATOR`. Tests:
`tests/test_domains_mobile_scope.py` (5), `tests/test_tier1_mobile_secrets_
sweep.py` (10) — real SQLite throughout, real `apktool` subprocess exercised
for the graceful-failure path, real zip extraction for the IPA path, real
planted-secret grep fixtures. `tests/test_bridge_tier1_schema.py` updated
(`MOBILE_ADDITIONS = {"mobile_secrets_sweep"}`) — a parallel Milestone 9
fork (GraphQL/Argus) is editing this same shared file concurrently; its own
`graphql_scanner` addition may transiently make `test_all_twenty_tier1_
schemas_load` fail until both edits have landed — confirmed unrelated to
this task's own files, not fixed here since it isn't a real defect in
either fork's work, just a timing artifact of parallel edits to one shared
list. `ruff check` and `mypy --ignore-missing-imports` clean on every file
this task touched; the 15 new tests pass in isolation.

**What changes if disapproved:** delete `vapt_agent/domains/mobile_scope.py`,
`vapt_agent/bridge/tier1/tools/mobile_secrets_sweep.py` + its schema, both
new test files, and the `MOBILE_ADDITIONS` line in `test_bridge_tier1_
schema.py`; revert the Mobile paragraph in `ROLE_BLOCK_OPERATOR`. Nothing
else in the Tier 1 catalog or schema references any of this.

---

## 47. Milestone 9 step 4 built: source-code-access auditing (`FR-CODEACCESS-01..04`, `CODE_REPO` target type) (2026-09-03)

**What I built:** `vapt_agent/domains/repo_scope.py` (new `domains/` package,
per `13`'s module layout) — `check_code_repo_scope()` combines both required
scope checks for a `CODE_REPO` task (repo identity via
`is_target_in_scope(..., pattern_kind="EXACT_IDENTIFIER")`, and a specific
in-repo path via `is_path_in_scope()`, neither a substitute for the other,
per `FR-CODEACCESS-03`'s own framing); `filter_matches_by_scope()` — a
higher-layer scope filter applied to a Tier 1 tool's raw JSON output
(Tier 1 tools stay dumb, with no `scope_rules` access of their own, matching
this codebase's existing architecture where policy is applied by a layer
above the subprocess, not inside it); `checkout_repo_readonly()` —
`FR-CODEACCESS-04`'s read-only clone/checkout helper (only `git
clone --no-checkout` + `git checkout`, never any install/build/postinstall
step).

Two new Tier 1 tools: `code_grep_scan.py` (`FR-CODEACCESS-02`'s whitebox-
code-recon whole-repo sink-class scan) and `diff_review_scan.py`
(`FR-CODEACCESS-01`'s diff/PR-scoped review: new sink-pattern lines
introduced by a diff, plus "blast radius" — every sibling call site of a
shared helper function whose *body* the diff touches, not just its
signature line). Both share a new `_sink_patterns.py` module (five sink
classes: injection/xss/ssrf/data-exposure/authorization).

**Judgment call — concrete grep patterns, not specified by `19`:** the spec
names the five sink classes but gives no exact patterns. Wrote original,
deliberately broad-recall, language-agnostic regexes per class (documented
in `_sink_patterns.py`'s own docstring) — intentionally over-inclusive,
since this is a lightweight first pass for the Operator to triage, not a
replacement for `sast_scan.py`/Semgrep (`16`'s own adoption note says as
much). Real bug found and fixed while writing the diff-review blast-radius
test: the original implementation only detected a "modified" function when
its `def` line itself appeared as a diff `+`/`-` line — but the overwhelmingly
common real case is a change to a function's *body* with the signature
untouched (e.g. a validation check quietly disabled). Fixed by tracking the
enclosing function across both context and changed lines while walking the
diff, not just changed lines.

**Judgment call — diff-review vs. whitebox-recon as two separate tools, not
one tool with a mode flag:** their actual mechanics differ enough (whole-repo
grep vs. `git diff`/`git blame`-driven change analysis) that two small,
single-purpose tools seemed cleaner than one tool branching on a mode flag —
matches this codebase's existing pattern of several small, single-purpose
Tier 1 tools (e.g. `cors_scanner.py`/`crlf_scanner.py` are separate despite
overlapping in spirit) rather than one large multi-mode tool.

**Judgment call — no repo-cloning wired into a Tier 1 tool itself:**
`checkout_repo_readonly()` is a plain Python helper in `repo_scope.py`, not
a Tier 1 tool of its own — `FR-CODEACCESS-02`'s scope description reads as
"a repo already in hand," and neither `diff-review` nor `whitebox-code-recon`
source material describes cloning as part of the domain's own testing
methodology. Kept available for whichever orchestration layer wires this
domain's task flow together (not yet built — see below), rather than
building a Tier 1 wrapper around it that nothing calls yet.

**What's NOT done — explicitly out of this task's scope:** this builds the
domain's tools and scope-check glue, but does **not** wire a `CODE_REPO`
task all the way through `Council Gate 1 Tier 0`/`task_runner.py`'s existing
`check_tier0()` call site (which still assumes a single `target`/
`pattern_kind` pair per task, not the two-check `CODE_REPO` shape) — that
orchestrator-level wiring is a distinct, later integration step, consistent
with how `FR-WEB3`/`FR-MOBILE`'s own domain modules (built in parallel by
other forks this same session) are similarly tools-plus-scope-glue without
full orchestrator wiring yet.

**Where it's used:** `vapt_agent/domains/repo_scope.py`,
`vapt_agent/bridge/tier1/tools/{code_grep_scan,diff_review_scan,
_sink_patterns}.py`, `vapt_agent/bridge/tier1/schemas/{code_grep_scan,
diff_review_scan}.yaml`, `vapt_agent/council/prompts.py::ROLE_BLOCK_OPERATOR`
(CODE_REPO scope guidance appended). Tests: `tests/test_domains_repo_scope.py`
(6), `tests/test_tier1_code_grep_scan.py` (7), `tests/test_tier1_diff_review_scan.py`
(5) — all real, non-mocked (real throwaway git repos via `tmp_path`, real
subprocess execution, no mocking of git/grep). `tests/test_bridge_tier1_schema.py`
updated (`CODEACCESS_ADDITIONS`).

**What changes if disapproved:** delete `vapt_agent/domains/repo_scope.py`,
the two new Tier 1 tools/schemas, `_sink_patterns.py`, and the three new test
files; revert the `CODEACCESS_ADDITIONS` line in `test_bridge_tier1_schema.py`
and the CODE_REPO paragraph appended to `ROLE_BLOCK_OPERATOR`. Nothing else
in the codebase depends on any of this yet (no orchestrator wiring exists).

---

## 48. Milestone 9 step 5 built: `FR-WEB3` smart-contract/token auditing (`CONTRACT` target type) (2026-09-03)

**What I built:** `vapt_agent/domains/contract_scope.py` (`CONTRACT`-specific
scope-check glue, `FR-WEB3-05`'s `contract_investigation_mode` handling, and
`FR-WEB3-06`'s pre-dive kill-signal scoring as real deterministic code, not
prompt-only guidance); a new Tier 1 tool `vapt_agent/bridge/tier1/tools/
web3_fork_poc.py` + schema wrapping `forge test --fork-url` for mainnet-fork-
only PoC execution (`FR-WEB3-04`); Web3 bug-class/kill-signal/DEX-LP/Solana-
Token-2022/grep-triage guidance folded into `ROLE_BLOCK_STRATEGIST`
(`vapt_agent/council/prompts.py`).

**Real judgment call — `FR-WEB3-05`'s `PUBLIC_RESEARCH` mode is a genuinely
different code path, not a parameter tweak.** The requirement's own text says
this mode "has no `scope_rules` authorization boundary in the usual sense."
Rather than trying to force it through the same `EXACT_IDENTIFIER` scope
check every other domain/mode uses (which would either wrongly require
`scope_rules` rows for something with no engagement authorization, or
silently no-op the check), `check_contract_tier0` branches: `CLIENT_OWNED`
gets the ordinary EXACT_IDENTIFIER check against `"{chain_id}:
{contract_address}"`; `PUBLIC_RESEARCH` skips `scope_rules` entirely and
instead enforces a fixed, closed allowlist of read-only `action_kind` values
(`onchain_authority_query`/`holder_distribution_query`/
`block_explorer_lookup`) — anything else is refused outright, regardless of
`scope_rules` content, since `FR-WEB3-05` is explicit that this mode must
never reach anything equivalent to PoC execution. This is a real safety
design decision (a mode with no scope boundary needs its own hard-coded
positive list of allowed actions, not an absence of restriction), not a
minor implementation detail — flagged for explicit review.

**`FR-WEB3-04`'s mainnet-fork-only restriction is enforced inside the tool
itself, not the declarative Tier 1 schema** — a schema can validate flag
*presence*/combinations (Gate 2, `FR-COUNCIL-08`) but has no mechanism to
inspect a flag's *value* (e.g. "is this URL a loopback address"), and this
restriction is explicitly a MUST regardless of any opt-in flag, so it isn't
appropriate to route through the existing `FR-TOOL-06a` opt-in-flag
mechanism either (that system is for the operator choosing to *enable* a
risk category; this is a restriction nothing may ever disable).
`web3_fork_poc.py::validate_fork_url` hard-rejects any `--fork-url` whose
hostname isn't `127.0.0.1`/`localhost`/`::1` — a fixed *allowlist* of
loopback hosts, not a denylist of known-bad RPC providers (a denylist could
always miss a real public RPC hostname it's never heard of).

**Confirmed environmental fact, not guessed:** `forge`/`anvil`/`cast`/
`slither`/`echidna` are NOT installed on this machine (checked directly via
`which`); `/usr/bin/medusa` exists but is the Foofus Networks password
cracker, not the Solidity property-based fuzzer `FR-WEB3-09` means — a
false-positive `which` hit worth flagging so a future reader doesn't assume
the fuzzer is present. `web3_fork_poc.py` degrades gracefully (exit 127,
clear stderr message, no crash) when `forge` is absent, verified by a real
test, matching `visual_triage.py`'s existing precedent for an
optional-dependency Tier 1 tool. No real end-to-end PoC-against-a-fork test
is possible until Foundry + an RPC endpoint are actually provided
(`AC-DEPENDENCY-11`, still "nobody's job yet") — not attempted, not faked.

**Where it's used:** `vapt_agent/domains/contract_scope.py`,
`vapt_agent/bridge/tier1/tools/web3_fork_poc.py`, `vapt_agent/bridge/tier1/
schemas/web3_fork_poc.yaml`, `vapt_agent/council/prompts.py::
ROLE_BLOCK_STRATEGIST` (CONTRACT-target paragraph appended). Tests:
`tests/test_domains_contract_scope.py` (11), `tests/test_tier1_web3_fork_poc.py`
(8) — real, non-mocked (real subprocess execution against a missing binary,
real `shutil.which` check, no mocking of `forge` itself since there's nothing
to mock around, just a real absence). `tests/test_bridge_tier1_schema.py`
updated (`WEB3_ADDITIONS`).

**What changes if disapproved:** delete `vapt_agent/domains/contract_scope.py`,
`web3_fork_poc.py`/its schema, and the two new test files; revert the
`WEB3_ADDITIONS` line in `test_bridge_tier1_schema.py` and the CONTRACT-target
paragraph appended to `ROLE_BLOCK_STRATEGIST`. Nothing else in the codebase
depends on any of this yet (no orchestrator wiring exists — this domain, like
Code-Access/Mobile, is schema/tool/prompt work ready for a future Operator/
task-queue integration pass, not yet wired into the live Phase 4.1/4.2 loop).

---

## 49. Milestone 9 step 3 built: `FR-GRAPHQL`/`FR-ARGUS` (2026-09-03)

**`FR-ARGUS-01/02` — already fully complete, nothing new needed.** Verified
(not assumed) that all five scanner scripts `FR-ARGUS-01` names
(`cors_scanner.py`, `crlf_scanner.py`, `nosqli_scanner.py`, `jwt_scanner.py`,
`llm_redteam.py`) are already registered as Tier 1 tools with real schemas,
and `oob_listener.py` already wraps `interactsh-client` exactly per
`FR-ARGUS-01`'s OOB-confirmation clause and `FR-ARGUS-02`'s dependency note
(its own docstring already documents `interactsh-client` as not installed on
this machine, confirmed via `shutil.which` at integration time). No new work
was required for this half of the directive.

**`FR-GRAPHQL-01..04` — new Tier 1 tool built.** `Actual-Setup/tools/
graphql_audit.sh` (the reference implementation named in the spec) sources
toolkit-coupled helper scripts (`external_arsenal.sh`, `banner.sh`) that
don't fit this project's standalone-Python Tier 1 convention — **judgment
call: reimplemented the same 7-phase technique set natively in Python**
(`vapt_agent/bridge/tier1/tools/graphql_scanner.py`) rather than force-port
the bash script, following the same "write new, matching the mined
technique, don't force a bad port" precedent already used for
`zero_day_fuzzer.py`'s CLI fix and the codeaccess domain's tools. Phases
implemented directly, dependency-free, against real `curl` subprocess calls:
introspection + 3 bypass techniques (GET-method, `__type`-in-place-of-
`__schema`, embedded-newline), field-suggestion detection, engine
fingerprinting (graphw00f-style error-text heuristic when `graphw00f` itself
isn't installed — confirmed absent via `shutil.which`, same graceful-
degradation pattern as `oob_listener.py`), deprecated-field auth-bypass
candidate detection, `application/graphql` content-type WAF-bypass check,
a built-in SQL-error injection probe (falls back gracefully when `gqlmap`
isn't installed), and three availability-impacting DoS-proof phases
(array batching, 500-alias bombing, depth-15 bombing).

**Real architectural addition, not just a new tool: Tier 1 flag-level
opt-in-category gating.** `FR-GRAPHQL-03` requires the three DoS-proof
phases specifically (not the tool as a whole) to require
`allow_active_exploitation` — the existing `FR-TOOL-06a` mechanism
(`bridge/denylist.py::classify_high_risk`) only gates by whole-binary
identity for Tier 2, which doesn't fit a single multi-purpose Tier 1 tool
where most flags are passive. Added `ToolSchema.flag_requires_opt_in: dict[str,
str]` (empty for every existing tool — fully backward compatible) and
`council/gate2_validator.py::check_tier1_opt_in_flags`, wired into
`council/task_runner.py::run_gated_task` right after ordinary Gate 2
validation passes, using the same `POLICY_REFUSED` status Tier 2's own
opt-in check already uses. `--batching-dos`/`--alias-bomb`/`--depth-bomb`
each map to `allow_active_exploitation` in `graphql_scanner.yaml`.

**One nuance flagged, not force-fit into the schema:** the spec's text says
batching used *specifically* for OTP brute-force/password-reset bombing
additionally needs `allow_brute_force` — this is a judgment-call distinction
about *intent*, not a structural property of which flag was passed, so it
can't be expressed as a second static schema entry without conflating every
batching-DoS use with brute-force intent. Left as Strategist/Operator
reasoning guidance (implicit in the existing prompt content on opt-in
categories) rather than a second hard-coded schema rule — flagged here
rather than silently dropped.

**`FR-GRAPHQL-04`** (kill-signal guidance) folded into
`ROLE_BLOCK_OPERATOR` in `prompts.py`, matching the existing MOBILE_BINARY/
CODE_REPO domain-guidance paragraphs' style (added by parallel forks in the
same file — reconciled cleanly, no conflicts).

**Where it's used:** `vapt_agent/bridge/tier1/tools/graphql_scanner.py`,
`vapt_agent/bridge/tier1/schemas/graphql_scanner.yaml`,
`vapt_agent/bridge/tier1/schema.py` (`flag_requires_opt_in` field),
`vapt_agent/council/gate2_validator.py` (`check_tier1_opt_in_flags`),
`vapt_agent/council/task_runner.py` (wired in), `vapt_agent/council/
prompts.py::ROLE_BLOCK_OPERATOR`. Tests: `tests/test_tier1_graphql_scanner.py`
(11, real subprocess execution against a closed local port, no mocking),
`tests/test_bridge_tier1_schema.py` (`GRAPHQL_ADDITIONS`). `ruff check .`
and `mypy vapt_agent/ --ignore-missing-imports` both clean; full `pytest -q`
passing (exact count depends on which parallel Milestone-9 forks had already
landed at the time this was written — see the suite's own final count in the
session record, not restated here since it changes turn to turn).

**What changes if disapproved:** delete `vapt_agent/bridge/tier1/tools/
graphql_scanner.py`, its schema, and its test file; revert `schema.py`'s
`flag_requires_opt_in` field (unused by any other tool, so removing it is a
clean no-op elsewhere), `gate2_validator.py`'s `check_tier1_opt_in_flags`,
`task_runner.py`'s wiring, the `GRAPHQL_ADDITIONS` line in
`test_bridge_tier1_schema.py`, and the GraphQL paragraph in
`ROLE_BLOCK_OPERATOR`.

---

## 50. Milestone 9 step 7 built: `FR-CICD`/`FR-CRED` (2026-09-03) — plus a real environmental correction found while closing a gap the fork's interruption left

**Context:** this domain's build was interrupted mid-task by a session
rate-limit reset (the fork had already written all production code and most
tests, and was mid-way through writing `tests/test_tier1_cicd_recon.py` when
it was cut off, before ever reaching its own documentation/report step).
Verified directly (not assumed) that the interrupted work was actually
complete and correct: `ruff check .`/`mypy --ignore-missing-imports` clean,
full `pytest -q` green (543 passing) before I touched anything further —
the interruption cost only the fork's own final report and this log entry,
not any actual code quality.

**What was built (by the interrupted fork, verified by me):**
- `FR-CRED-01` stages 1-3 (no live-target interaction, not checkpoint-gated):
  `wordlist_gen.py` (a real, self-contained same-host crawler +
  hashcat-style rule mutation, standing in for the absent `cewler`
  dependency — documented as narrower, not equivalent); `breach_check.py`
  (real HIBP k-anonymity queries, SHA-1 **prefix-only**, enforcing
  `FR-CRED-02`'s "never transmit/store the full hash or plaintext" MUST
  structurally, not by convention).
- `FR-CRED-01` stage 4 / `FR-CRED-03`/`04`, checkpoint-gated:
  `credential_spray.py` — all 4 modes (`http-form`/`oauth`/`o365`/`okta`),
  `password[i] × all_users` spray order enforced by the iteration structure
  itself (not left to caller discipline), stops on first success by
  default, feeds a real lockout-percentage estimate into
  `checkpoint_gate.build_rationale`'s `estimated_lockout_percentage`
  parameter (previously accepted but never fed a real value by anything).
  Tool name `credential_spray` matches `checkpoint_gate.py`'s existing
  placeholder mapping for `LIVE_CREDENTIAL_SPRAY` exactly — no change
  needed there. Phishing-based MFA bypass excluded entirely per
  `FR-CRED-03`'s closing clause — not built, not stubbed.
- `FR-CICD-01`/`02`: `cicd_recon.py` — genuinely read-only static-pattern
  scan over on-disk workflow YAML (workflow injection via untrusted context
  expressions, `pull_request_target` misuse, broad/missing `permissions:`,
  self-hosted-runner + fork-PR-trigger poisoning precondition, unpinned
  mutable-tag action refs, and the AI-agent-security sub-class). Not
  checkpoint-gated — needs no `gh` auth, operates on an already-local
  checkout.
- `FR-CICD-03`/`04`, checkpoint-gated: `cicd_external_action.py` — three
  distinct Tier 1 schema names (`cicd_open_pr`/`cicd_trigger_workflow`/
  `cicd_modify_secrets`, one shared binary) matching `checkpoint_gate.py`'s
  existing placeholder mapping for `CICD_EXTERNAL_ARTIFACT` exactly.

**Gap the interruption left, found and closed by me:** `cicd_external_action.py`'s
own internal logic (the `gh`-wrapping helper, argument parsing, graceful
degradation) had no direct unit test at all — only the checkpoint-gate
*routing* around it (never reaching the script without approval) was
tested, in `test_security_checkpoint_gate.py`/`test_cli_checkpoint.py`.
Added `tests/test_tier1_cicd_external_action.py` (12 tests) to close this.

**Real, important correction found while writing that test (not a guess,
checked directly via `gh auth status`):** the interrupted fork's own
docstrings in `cicd_external_action.py` claimed *"this machine has none
[`gh` auth] configured"* — **this is factually wrong.** `gh` is both
installed and **authenticated as the operator's own real GitHub account**
(`MHuzaifaJamil`). This is not a cosmetic detail: it means the
`CICD_EXTERNAL_ARTIFACT` Human Checkpoint Gate protecting `open_pr`/
`trigger_workflow`/`modify_secret` is a **real, live safety boundary** here,
not a hypothetical one that happens to be inert because the dependency is
absent — an approved task would act against a real, reachable repository.
Corrected the false claim in `cicd_external_action.py`'s module docstring
and in the new test file's own docstring; deliberately kept every test
targeting the placeholder identifier `owner/repo` (which real, authenticated
`gh` correctly refuses with a 404/no-access error) rather than any real
repository — proving a real PR/workflow/secret action can complete
end-to-end would require the operator deliberately pointing this at a real
throwaway repo set up for that purpose, which is exactly the class of
decision the Human Checkpoint Gate's live-approval step exists to require,
not something an automated test should attempt on its own initiative.

**Where it's used:** `vapt_agent/bridge/tier1/tools/{wordlist_gen,
breach_check,credential_spray,cicd_recon,cicd_external_action}.py` +
their schemas; `tests/test_tier1_{wordlist_gen,breach_check,
credential_spray,cicd_recon,cicd_external_action}.py`;
`test_bridge_tier1_schema.py`'s `CRED_CICD_ADDITIONS`. Full suite: 552
passing, 3 skipped (the `gh`-not-installed variants, correctly skipped since
`gh` is actually present here). `ruff check .` and `mypy
--ignore-missing-imports` both clean.

**What changes if disapproved:** delete the five new Tier 1 tool/schema
pairs and their five test files; revert the `CRED_CICD_ADDITIONS` line in
`test_bridge_tier1_schema.py`. `checkpoint_gate.py`'s existing placeholder
tool-name mapping needs no reversion — it already matched these real names
without modification.

---

## 51. Milestone 9 step 7 completed: anti-forensics/broad-scope (`FR-ANTIFORENSICS-01`, `FR-BROADSCOPE-01..03`) — the one domain sub-section no fork was ever assigned

**What happened:** auditing doc 15's Milestone 9 build order against what
had actually been dispatched, found that step 7 ("`FR-CICD`/`FR-CRED`/
anti-forensics — build last") had only ever been split into two fork
prompts (CI/CD, Credential-Attack) — the anti-forensics/broad-scope-framing
sub-section of `19-Extended-Capability-Domains.md` (`FR-BROADSCOPE-01/02/03`,
`FR-ANTIFORENSICS-01`) was never assigned to anyone and had no code behind
it at all, only the `FR-CHECKPOINT-05` attestation-field validation
(`validate_anti_forensics_flags`, built earlier alongside the Checkpoint
Gate itself). Built directly by me, not delegated to a fresh fork — matching
the spec's own precedent that this specific section was "read directly, not
delegated to a research fork, given its sensitivity" during the original
mining pass.

**Built:**
- `broad_scope` column on `engagements` (`FR-BROADSCOPE-01`) + `--broad-scope`
  flag on `vaptctl start`, following the existing opt-in-flag pattern exactly.
  An ordinary config flag, no checkpoint involved — ordinary widening of what
  `scope_rules` MAY cover, verified by the operator against the actual RoE
  text, never inferred from attack-surface size.
- `vapt_agent/bridge/tier1/tools/anti_forensics_action.py` + schema —
  `ANTI_FORENSICS`-checkpoint-gated (tool name `anti_forensics_action`
  already matched `checkpoint_gate.py`'s existing placeholder mapping
  verbatim, no change needed there).

**Real design decision, not a straightforward port:** `FR-ANTIFORENSICS-01`
deliberately references MITRE ATT&CK T1070/T1564/T1622 *by technique ID*,
not as ready-to-run commands, specifically so this document set doesn't go
stale against ATT&CK's own evolving detail. Rather than accept an arbitrary
caller-supplied command for this tool (which would mean Gate 2's
declarative schema validation is rubber-stamping opaque, unauditable
execution — exactly the risk `FR-TOOL-06`(b)'s inline-interpreter denylist
exists to prevent everywhere else in this system), built a **fixed, closed
set of three concrete action verbs** instead (`clear-log-lines` /
`timestomp` / `clear-shell-history`, each ATT&CK-sub-technique-labeled:
T1070.002/.006/.003) — each one backs up the exact original state *before*
changing anything and is independently revertible via a single `revert`
action, directly implementing `FR-ANTIFORENSICS-01`'s own hard requirement
("any log/timestamp change made during testing MUST be disclosed and
reverted... never a permanent, undisclosed alteration") as a structural
guarantee rather than an operator-discipline convention. All three operate
only on an explicit `--target-path` the caller names — this tool never
discovers or guesses a path itself.

**Also folded into `ROLE_BLOCK_STRATEGIST`:** `FR-BROADSCOPE-02`'s two
narrow product-specific patterns (CDN/edge-config tenant-isolation gap,
CDN-to-cloud-storage credential escalation) and same-subnet ARP-MITM as an
ordinary technique; `FR-BROADSCOPE-03`'s explicit exclusion (gray-market/
criminal-infrastructure cataloguing is never a hypothesis, flag-and-stop
only); and `FR-ANTIFORENSICS-01`'s own framing (test whether detection
occurs, never permanently defeat it; only against explicitly-scoped
test-lab paths; every such hypothesis still passes through the Human
Checkpoint Gate regardless of engagement flags). Kept the embedded "Output
schema:" JSON block byte-identical.

**Tests:** `tests/test_tier1_anti_forensics_action.py` (12 tests — real
file operations in `tmp_path`, no mocking: clear-log-lines/timestomp/
clear-shell-history each proven to change state and then fully revert it
byte-for-byte, a `classify_checkpoint_action` routing check, Gate1/Gate2
sanity checks, and a `main()`/JSON-output round-trip). `ANTIFORENSICS_ADDITIONS`
added to `test_bridge_tier1_schema.py`'s expected-tools set. Full suite: 563
passing, 3 skipped (the `gh`-not-installed variants from item #50, correctly
skipped since `gh` is actually present on this machine). `ruff check .` and
`mypy vapt_agent/ --ignore-missing-imports` both clean.

**With this, every FR-* sub-section named in `19-Extended-Capability-
Domains.md` has real code behind it** — `FR-VULNCLASS`/`FR-WEB3`/
`FR-MOBILE`/`FR-GRAPHQL`/`FR-CICD`/`FR-CRED`/`FR-CODEACCESS`/`FR-ARGUS`/
anti-forensics+broad-scope-framing — completing Milestone 9's domain work.
Doc 15's own Milestone 9 build order (schema → checkpoint gate → GraphQL/
Argus → code-access → web3 → mobile → CI/CD/credential-attack/anti-forensics
→ monitor) is now fully built; only the Monitoring Dashboard
(`22-VAPT-Monitoring-Dashboard-Specification.md`, pulled from a later source
update) remains as the final piece before Milestone 9 is complete end to end.

**What changes if disapproved:** delete `anti_forensics_action.py`, its
schema, and its test file; revert the `ANTIFORENSICS_ADDITIONS` line in
`test_bridge_tier1_schema.py`; revert `broad_scope`'s column/flag/prompt
additions. `checkpoint_gate.py` needs no reversion — its placeholder mapping
already matched this tool's real name without modification.

---

## 52. Milestone 9's final piece built: the VAPT Monitoring Dashboard (`22-VAPT-Monitoring-Dashboard-Specification.md`, `vaptctl dashboard`) (2026-09-03)

**What I built:** a new `vapt_agent/dashboard/` package split deliberately
into a pure computation layer (`compute.py`) and a thin `rich`/`plotext`
rendering layer (`render.py`), specifically so `FR-DASHBOARD-05..12`'s dense
per-role state-derivation/`N_exp`-formula/EMA-forecasting logic is fully
unit-testable without a real terminal — plus `vapt_agent/cli/dashboard.py`
(the `vaptctl dashboard [--rate 1.0] [--db <path>]` entry point), registered
in `main.py` alongside the other Milestone 9 commands. Followed the four
corrections already baked into the doc I read (plain `mode=ro`, no
`immutable=1`; `vaptctl dashboard` not `vapt dashboard`; everything derived
from the real, revised `model_invocation_logs` table, no `engine_state`
table) rather than the "original spec" text quoted for contrast.

**Real, unplanned discovery — a genuine `plotext` API break, not a code
bug:** the spec's Live Graphical Elements section (§5) assumes `plotext`'s
long-standing functional API (`plot_size`/`plot`/`build`/`clear_figure`).
The latest published version, **`plotext` 6.0.0, is a from-scratch rewrite**
with a completely different primitive/canvas-object API (`figure`/`matrix`/
`image`/`pixel`/`square` — no `plot()`/`clear_figure()` at all). Verified
directly (not assumed) via `pip index versions plotext` and `help()` on the
installed package before concluding this, rather than guessing from an
import error. **Pinned `plotext>=5.2,<6`** in `pyproject.toml` (installed
`5.3.2`) rather than rewrite the graph code against the 6.0.0 API — the 5.x
functional API is what the spec's own usage assumes and is the far smaller,
lower-risk change. Documented in `pyproject.toml`'s own comment so a future
`pip install -U` doesn't silently reintroduce this breakage.

**Real design decisions, each one a judgment call beyond the spec's literal
text:**
- **Role naming**: `model_invocation_logs.role` uses `DR-SCHEMA-08`'s six
  canonical names (`Strategist`/`Operator`/`Gatekeeper`/`Linter`/
  `Adjudicator`/`Reporter` — `Gatekeeper` = Gate 1's semantic tier,
  `Adjudicator` = Gate 3). This is the naming convention the parallel
  model-invocation-logs-instrumentation fork (building the writer side at
  the same time) also needs to use for the two sides to actually connect —
  confirmed consistent by re-running the full suite after both landed.
- **Operator `RESIDENT`/`IDLE` inference**: nothing in `model_invocation_logs`
  records an explicit "model unloaded" event, so `RESIDENT` is inferred as
  "the Operator has completed >=1 turn this engagement, has no row
  currently in-flight, AND the engagement's own status is still
  `IN_PROGRESS`" — the third condition specifically so a `COMPLETE`/`ABORTED`
  engagement never shows a falsely-still-resident Operator. Every other
  role never qualifies for this badge at all (`FR-DASHBOARD-07`).
- **Offline Linter's `N_exp`**: `FR-DASHBOARD-09` specifies "real-time count
  of active Operator script submissions awaiting linting" — no table in
  this schema tracks a linter-submission queue (the Offline Linter has no
  live call site wired in at all yet, per its own existing module
  docstring). Returns a fixed `0` rather than guessing at a query against a
  queue that doesn't exist — a documented limitation, not a silent
  approximation.
- **Swap-growth baseline**: `NFR-RES-06`'s tracking primitives
  (`hibernation.py::read_cumulative_pages_swapped_out`/`check_swap_growth`,
  already real and tested, confirmed 2 GiB threshold) exist but were never
  wired to a persisted per-engagement baseline (that module's own docstring
  already flags this gap). The dashboard captures its *own* startup as a
  pragmatic session baseline — an honest proxy for "this monitoring
  session," not a claim that it matches the engagement's actual hibernation
  window exactly. Reused the existing functions directly rather than
  re-implementing swap tracking.
- **Read-only connection**: `sqlite3.connect(f"file:{path}?mode=ro",
  uri=True)`, exactly as corrected — verified for real (not just by
  inspection) that a concurrent real writer connection keeps writing
  successfully while the read-only connection is open, and that the
  read-only connection itself genuinely refuses an `INSERT` with a real
  `sqlite3.OperationalError`, not just a documented intention.

**Tests:** `tests/test_dashboard_compute.py` (17 — every `FR-DASHBOARD-05..12`
behavior: fresh-engagement cold-start fallback, `RUNNING`/`RESIDENT`/`COLD`
derivation including the complete-engagement edge case, real EMA/tok-per-sec
computation, the integrity-alert trigger, every role's exact `N_exp`
formula including the Operator's 0.10 retry-floor, the task-queue funnel),
`tests/test_dashboard_render.py` (5 — real rendering against a real `rich`
`Console` to catch actual crashes, not just return values), `tests/
test_cli_dashboard.py` (6 — CLI registration, the real concurrent-writer
non-blocking proof, the real write-refusal proof, the waiting-screen path).
Full suite: 591 passing, 3 skipped (the pre-existing `gh`-not-installed
skips from item #50). `ruff check .` and `mypy vapt_agent/
--ignore-missing-imports` both clean project-wide (confirmed after the
parallel instrumentation fork's work landed too).

**With this, Milestone 9 is fully complete** — every domain in
`19-Extended-Capability-Domains.md`, the Human Checkpoint Gate, Monitor
mode, and now the Monitoring Dashboard all have real, tested code behind
them, following doc 15's own build order end to end.

**What changes if disapproved:** delete `vapt_agent/dashboard/`,
`vapt_agent/cli/dashboard.py`, its three test files, and its `main.py`
registration; revert the `rich`/`plotext`/`psutil` dependency additions in
`pyproject.toml`. Nothing else in the system depends on this module (it is
read-only and architecturally independent, per the spec's own framing).

---

## 53. `model_invocation_logs` instrumented for real — the writer side the Monitoring Dashboard (#52) depends on (2026-09-03)

**What happened:** verified directly (not assumed) that, before this task,
**nothing in this codebase wrote to `model_invocation_logs` at all** — the
table existed in `schema.sql` and was read by `security/audit.py`/
`cli/export.py`, but no council role invocation ever inserted a row. This is
the load-bearing writer the parallel Monitoring Dashboard fork's reader/TUI
(#52) depends on to show "currently generating" state.

**Built `vapt_agent/council/invocation_log.py`** — `start_invocation`
(assigns `turn_number = COALESCE(MAX(turn_number), 0) + 1` per
`(engagement_id, role)`, inserts the unfinalized row per `FR-DASHBOARD-05`),
`finish_invocation` (updates it in place), and `run_with_invocation_logging`
(a thin wrapper a caller uses around its own call to
`get_structured_completion`).

**Real architectural decisions, not rote instruction-following:**
1. **`get_structured_completion` (`engine/structured.py`) was deliberately
   left untouched** — no new parameters, no DB dependency added to a
   function whose whole job is a pure retry loop. `run_with_invocation_
   logging` wraps *around* a caller's call to it instead.
2. **One "turn" spans the whole multi-attempt structured-completion call,
   not each individual HTTP round-trip.** `IR-STRUCTURED-03` allows up to 3
   attempts on schema-validation failure; `FR-DASHBOARD-06` says a row with
   `ended_at IS NULL` means "currently generating" — that needs to stay true
   for the *entire* multi-attempt exchange, not flicker between retries (a
   retry is the model correcting its own prior attempt, still the same
   logical turn). So the row opens once, before the first attempt, and
   closes once, after the last. **Exception, also decided and documented:**
   `Operator`'s Gate-2-rejection retries (`run_operator_command_retry`) ARE
   each their own distinct turn — unlike `get_structured_completion`'s
   internal schema-validation retries, each Gate-2 retry is a genuinely
   separate call the Phase 4.2 loop itself initiates against new evidence
   (a fresh rejection reason), not an implementation detail of one logical
   turn.
3. **Token/latency figures** come from `response["usage"]` (llama.cpp's
   OpenAI-compatible `prompt_tokens`/`completion_tokens`), previously
   discarded entirely by every role wrapper's `call_fn` closure. Rather than
   change `get_structured_completion`'s `call_fn` return contract (which
   would touch its own tests and every caller), each role wrapper's
   `call_fn` now stashes the last response's `usage` into a mutable dict the
   wrapper also holds — naturally ends up holding the *last* attempt's
   figures on a multi-attempt sequence, the correct one to report.
4. **Failure-status mapping** (`model_invocation_logs.status`'s fixed four
   values): `EngineUnresponsiveError` (the existing forced-kill-on-timeout
   path) maps exactly to `TIMEOUT`; everything else, including
   `StructuredOutputError` (retry budget exhausted), maps to `CRASHED` — the
   closest fit among the remaining values; `CONTEXT_TRUNCATED` is reserved
   for a real context-overflow signal this system doesn't yet detect
   distinctly.

**Backward compatible by construction, verified not just claimed:** `conn`/
`engagement_id`/`phase` are new, optional (default `None`) keyword
parameters on all 6 role wrapper functions (`run_strategist`,
`run_gate1_semantic`, `run_operator_command`/`_retry`/`run_operator_
followup`, `run_adjudicator`, `run_reporter`, `run_offline_linter`). First
pass introduced a real bug caught by the existing test suite immediately
(28 failures): `model_name=handle.model_id` was evaluated eagerly even when
`conn`/`engagement_id` were `None`, but several existing tests call these
functions with `handle=None` (a fake engine client that ignores the handle
entirely) — fixed by making the `handle.model_id` access conditional
(`handle.model_id if conn is not None and engagement_id is not None else
None`), confirmed by re-running the full suite (back to all passing).

**Wired into the real call sites**, not just left as opt-in dead code:
`orchestrator/phase_lifecycle.py`'s `run_phase_4_1`/`_4_2`/`_4_3` (all 8 call
sites: Strategist, Gate-1-semantic, Operator command/retry/followup,
Adjudicator, Reporter x2) and `council/task_runner.py`'s own
`run_gate1_semantic` call (the Phase-4.2 Tier-0-recheck path) all now pass
`conn=conn, engagement_id=engagement_id, phase="4.1"/"4.2"/"4.3"`.
`run_offline_linter` has no real call site anywhere in this codebase yet (a
pre-existing gap, not this task's to fix) — its new parameters are ready for
whenever it is wired in.

**Tests:** `tests/test_council_invocation_log.py` (10 tests — turn-number
sequencing, unfinalized-during/finalized-after semantics proven via a
mid-call introspection, TIMEOUT/CRASHED status mapping, passthrough
behavior with no `conn`, missing-`usage`-field graceful handling) plus two
new integration tests in `tests/test_orchestrator_phase_lifecycle.py`
proving the *real* `run_phase_4_1` orchestrator path (not just
`invocation_log.py` in isolation) writes real `Strategist`/`Gatekeeper` rows
with correct `turn_number` sequencing across multiple hypotheses. Full
suite: 603 passing, 3 skipped (unrelated pre-existing `gh`-not-installed
skips). `ruff check .` and `mypy vapt_agent/ --ignore-missing-imports` both
clean project-wide, confirmed after the parallel dashboard fork's work
(#52) had also landed.

**Where it's used:** `vapt_agent/council/invocation_log.py` (new);
`vapt_agent/council/{strategist,gate1_semantic,operator,adjudicator,
reporter,offline_linter}.py` (new optional params + wiring);
`vapt_agent/orchestrator/phase_lifecycle.py` and
`vapt_agent/council/task_runner.py` (real call-site wiring);
`vapt_agent/data/schema.sql`'s `turn_number` column (added earlier by the
orchestrating session, ahead of this task).

**What changes if disapproved:** delete `invocation_log.py` and its test
file; revert the `conn`/`engagement_id`/`phase` parameters and their
`run_with_invocation_logging` wrapping from all 6 role wrapper files back to
plain `get_structured_completion` calls; revert the 8+1 call-site wirings in
`phase_lifecycle.py`/`task_runner.py`; remove the two new integration tests
from `test_orchestrator_phase_lifecycle.py`. `model_invocation_logs` itself
and its `turn_number` column need no reversion — they're additive schema
that predates this task.

---

## 54. REAL FINDING: the Strategist's 900s default timeout is still sometimes insufficient even with #45's 3-8 hypothesis bound — given its own dedicated 1800s timeout (2026-09-03)

**What happened:** ran a real, full Milestone-8-style capstone pass
(Phase 4.1 → 4.2 → 4.3, all real GGUF models, real Tier 1/Tier 2 tool
execution) against a real, live, disposable Docker test-lab target (OWASP
Juice Shop, `bkimminich/juice-shop`, bound to `127.0.0.1:3000` only) — the
first real acceptance-style run against an actual reachable target this
session, at the operator's explicit direction. The Strategist call hit
`EngineUnresponsiveError` at exactly 900.0s and was force-killed, the same
failure class as item #38/#45's original finding — **even with the 3-8
hypothesis prompt bound already in place.**

**This does not contradict #45 — it sharpens it.** A separate real run
(documented in #45, same bounded prompt) completed in 763.8s, comfortably
under 900s. This run, against a different real target string
(`127.0.0.1`) and a shorter real scope summary (`allow: 127.0.0.1`, vs. the
earlier run's synthetic `capstone-target.example` text), took longer than
900s instead. At `temperature=0.0` (greedy decoding), the *shape* of the
prompt genuinely changes how long DeepSeek-R1 reasons before committing to
output — a shorter, differently-worded prompt is not guaranteed to produce
a shorter reasoning trace. The hypothesis bound narrows the *ceiling*
(unbounded-length output is ruled out) but doesn't tightly bound the
*variance* run-to-run. This is real, measured behavior, not a hypothesis.

**Fix:** added `STRATEGIST_TIMEOUT_S = 1800.0` (30 minutes) in
`vapt_agent/council/strategist.py`, passed explicitly to this role's own
`chat_completion` call via `timeout_s=`. Every other role keeps the shared
900s default in `engine/client.py` — they are non-reasoning models (Hermes-
3/Qwen2.5-Coder/Mistral/Ministral) with no equivalent `<think>`-block
variance observed. This is a judgment call on the specific number (1800s
doubles the observed 900s ceiling with real headroom above both the 763.8s
success and the >900s failure) — not empirically proven sufficient for
every possible future prompt shape, just a substantially more generous,
evidence-informed bound than the shared default. `pytest -q` (603 passing,
3 skipped), `ruff check .`, `mypy --ignore-missing-imports` all clean after
this change. Retrying the real Juice Shop capstone run with this fix in
place.

**Where it's used:** `vapt_agent/council/strategist.py::STRATEGIST_TIMEOUT_S`,
`run_strategist`'s `call_fn`.

**What changes if disapproved:** delete `STRATEGIST_TIMEOUT_S` and its
`timeout_s=` argument in `call_fn`, reverting the Strategist to the shared
900s default — re-exposes the same real, reproducible failure mode this
entry documents.

---

## 55. #54's optimization directive implemented: a reasoning-conciseness steer + dashboard cold-start prior recalibration (2026-09-03)

**Approved directive, implemented as specified:**
1. **`ROLE_BLOCK_STRATEGIST`** (`vapt_agent/council/prompts.py`) now carries
   an explicit conciseness instruction immediately above the 3-8 hypothesis
   bound: "Keep your internal deliberation concise and strictly focused on
   identifying primary attack vectors. Do not generate exhaustive
   permutations of edge cases in your reasoning before emitting the
   hypotheses below — reason enough to pick your best ideas, then commit to
   output." This does not remove the hypothesis-count bound (#45) — it's a
   second, complementary lever aimed at the *other* variable (reasoning-
   trace length before committing), not a replacement for it.
2. **`vapt_agent/dashboard/compute.py`**'s `ROLE_MODEL_DEFAULTS["Strategist"]`
   cold-start `prior_seconds_per_turn` changed from the original spec's
   placeholder `45.0` to `850.0` (within the directed 800-900s range) —
   the `45.0` figure was never calibrated against this system's actual
   Q8_0/CPU-only throughput; live capstone runs this session measured
   763.8s and >900s for real Strategist turns, `850.0` sits between them.
   `prior_tok_per_sec` (`10.7`) was left unchanged — it already
   approximately matches this session's real measured prompt-eval
   throughput (11.27-16.13 tok/s across several diagnostics), unlike the
   seconds-per-turn figure which was clearly never derived from a real
   measurement at all.

**Verification:** `ruff check .` and `mypy vapt_agent/ --ignore-missing-imports`
both clean; full `pytest -q` — 602 passing, 3 skipped, 1 failure
(`test_check_inference_engine_reports_missing_binary_as_documented_failure`,
the same pre-existing/well-documented transient flake from a concurrent
real `llama-server` process — in this instance, the live Juice-Shop capstone
retry run in progress at the time these two edits were made and verified —
not a regression from either change; confirmed unrelated by inspection, not
just assumed).

**Whether the conciseness steer actually shortens real reasoning traces has
not yet been independently re-measured** — the in-flight capstone retry
that prompted this whole finding was already running with the *pre-steer*
prompt when these edits landed (Python had already built and sent that
system-prompt string before the edit occurred), so it isn't a valid test of
this specific change. A future real Strategist call will be the first to
carry this instruction — worth watching whether it measurably reduces
completion time, not assumed to work just because it was directed.

**Where it's used:** `vapt_agent/council/prompts.py::ROLE_BLOCK_STRATEGIST`,
`vapt_agent/dashboard/compute.py::ROLE_MODEL_DEFAULTS`.

**What changes if disapproved:** revert the added paragraph in
`ROLE_BLOCK_STRATEGIST`; revert `prior_seconds_per_turn` back to `45.0` (or
any other value the operator prefers) — both are independent, low-risk
text/data changes with no architectural coupling to anything else.

---

## 56. REAL BUG FIXED: a malformed-JSON response from `call_fn` crashed immediately instead of consuming the retry budget (2026-09-03)

**What happened:** the retried capstone run (with #54's 1800s Strategist
timeout in place) got past the timeout this time — DeepSeek-R1 completed in
~1742s — but its response was malformed JSON (`Expecting ',' delimiter:
line 16 column 115`), a different failure mode than #45's already-fixed
literal-control-character issue. `get_structured_completion` immediately
raised, with none of `IR-STRUCTURED-03`'s "2 retries, 3 attempts total"
budget ever spent. Root cause: `call_fn` raising `ValueError` (via
`decode_json_content`'s malformed-JSON path) was never caught by the retry
loop at all — only a schema-validator returning error strings triggered a
retry. A structurally well-formed-but-wrong-schema response retried; a
not-even-valid-JSON response didn't, which is backwards from what
`IR-STRUCTURED-03` actually intends (any structured-output validation
failure gets a bounded retry).

**Fix:** `get_structured_completion` (`vapt_agent/engine/structured.py`) now
wraps the `call_fn` call in `try/except ValueError`, folding a decode
failure into the exact same retry mechanism a schema failure already uses
— same corrective-message-and-resend pattern, same shared `max_retries`
budget (not a second, parallel retry counter). Two new tests confirm both
directions: a malformed-JSON-then-valid sequence now succeeds on retry
(previously would have crashed on attempt 1), and an always-malformed
sequence still correctly exhausts the budget and raises
`StructuredOutputError` (not an uncaught `ValueError`).

**Verification:** `ruff check .`/`mypy --ignore-missing-imports` clean;
full `pytest -q` — 605 passing, 3 skipped. Relaunching the real Juice Shop
capstone run with this fix in place — this is the third real attempt this
session, each one surfacing and fixing a genuinely different real bug
(Strategist hang → hypothesis-count/timeout fix; Gate 1 control-character
JSON → `strict=False`; now this retry-budget gap) — none of them
hypothetical, all found via actually running the real system against a
real live target.

**Where it's used:** `vapt_agent/engine/structured.py::get_structured_completion`.

**What changes if disapproved:** revert to the bare `raw_obj =
call_fn(current_messages)` call with no `try/except` — reintroduces the
exact crash this entry documents.

---

## 57. REAL BUG FIXED: Operator proposing an invalid Tier 1 tool name crashed Phase 4.2 with an uncaught KeyError instead of a correctable Gate 2 rejection (2026-09-03)

**What happened:** the retried Juice Shop capstone run got past Phase 4.1
in full this time (2056.4s total, 5 hypotheses proposed, Gate 1 approved 1
of them — a real SSRF-test task) and entered Phase 4.2 for the first time
all session with real, live target execution. The Operator proposed
`{"tier": 1, "tool": "curl", ...}` — but `curl` was never registered as a
Tier 1 tool (it's a plain Tier 2-eligible system binary) — and
`run_gated_task`'s `get_schema(tool_name)` call raised an uncaught
`KeyError`, crashing the entire Phase 4.2 loop for the whole engagement,
not just that one task.

**Fix:** `vapt_agent/council/task_runner.py::run_gated_task` now catches
`KeyError` from `get_schema` and treats an unrecognized Tier 1 tool name
exactly like any other Gate 2 rejection — `GATE2_BLOCKED`, with a
rationale telling the Operator specifically what's wrong and how to
correct it ("`'curl'` is not a registered Tier 1 tool... resubmit with
`\"tier\": 2`..."). This flows into the existing Gate 2
retry-with-correction mechanism `run_phase_4_2` already has (up to
`FR-COUNCIL-09`'s 3 attempts) with zero changes needed there — the fix is
entirely in not letting an invalid tool name skip that mechanism via an
uncaught exception.

**Verification:** new test
`test_invalid_tier1_tool_name_rejected_by_gate2_not_a_crash` in
`tests/test_milestone2_end_to_end.py` reproduces the exact real scenario
(a `curl` Tier 1 task) and confirms `GATE2_BLOCKED` with no crash and no
tool execution. `ruff check .`/`mypy --ignore-missing-imports` clean; full
`pytest -q` — 606 passing, 3 skipped. Relaunching the Juice Shop capstone
run a 4th time with this fix in place — real progress each attempt (Phase
4.1 now completes reliably; this is the first bug found *inside* Phase
4.2's real tool-execution loop).

**Where it's used:** `vapt_agent/council/task_runner.py::run_gated_task`.

**What changes if disapproved:** remove the `try/except KeyError` block,
reverting to the uncaught crash this entry documents.

---

## 58. REAL FINDING (operational, not a code bug): sustained multi-hour CPU-only inference thermally throttles this laptop hardware, degrading throughput and causing repeated Strategist timeouts — no code fix, a genuine hardware/environment limit

**What happened:** the MediaCMS capstone run (a real, disposable, second
benchmark target, byte-identical prompt content to the Juice Shop run that
had already succeeded) failed the Strategist's 1800s timeout **4 times in a
row** — a run of bad luck far beyond anything explainable by the model-
reasoning-length variance already documented in items #45/#54. Ruled out
resource contention from the target's own Docker containers first
(`docker stats` showed under 2% combined CPU usage — MediaCMS's Postgres/
Redis/Django/Celery stack was genuinely idle). Then captured `llama-
server`'s own verbose log directly (previously discarded to `DEVNULL`, via
a one-off monkey-patched diagnostic script, not a shipped-code change) for
a 5th attempt and found the real cause: **generation throughput had dropped
to ~2.67 tok/s, roughly half the ~4.8-5.2 tok/s measured earlier in this
same session** (items #38/#54). Checked `sensors` and
`/sys/devices/system/cpu/cpu*/thermal_throttle/core_throttle_count`
directly: CPU package temperature **94°C** (one core at 95°C, both close to
this chip's throttle range), live per-core frequency samples ranging
3534 MHz down to **2223 MHz**, and the P-cores used for inference
(`FR-GATE-03`'s pinned cores) showing thermal-throttle event counts in the
**millions** — all real, measured, not inferred. After roughly 5-6 hours of
near-continuous heavy CPU-bound inference this session (many capstone
attempts, diagnostics, and the Milestone 9 build work's own test suite
runs), this laptop-class CPU (Intel Core Ultra 5 125H) is genuinely
overheating and self-throttling, which fully explains both the slower
throughput and the repeated timeouts — **not** the model "choosing" to
reason unusually long, and **not** a code defect anywhere in this system.

**Why this matters beyond just this one failed run:** this is a real,
previously-undocumented operational limit of the confirmed hardware profile
under genuinely sustained multi-hour autonomous operation — exactly the
scenario `FR-COUNCIL-11`'s 12-hour session budget is designed to run
unattended for. This system currently has **no thermal-awareness or
throttling-detection mechanism at all** — `NFR-RES-05`'s P-core/E-core
pinning manages *contention*, and the dashboard's memory bar
(`22-VAPT-Monitoring-Dashboard-Specification.md`) surfaces RAM/swap, but
nothing surfaces CPU temperature or throttle state to the operator, and
nothing in the timeout/retry logic accounts for "the hardware itself has
gotten measurably slower mid-engagement." A real 12-hour unattended run on
this exact hardware could plausibly hit this same degradation partway
through, with no visibility into why calls are suddenly taking longer.

**Not fixed here — deliberately, this is a hardware/environment finding, not
a software bug to patch around.** Options for a real fix, not decided here:
(a) add live CPU-temperature/throttle-state to the dashboard's telemetry
(a genuinely useful, scoped addition — `psutil`/`sensors`-equivalent data is
already available on this host); (b) add a pre-flight or in-loop thermal
check that pauses/slows the engagement if temperatures are already elevated
before a long Strategist call; (c) simply document this as a known
limitation of sustained CPU-only inference on laptop-class hardware,
recommending active cooling or a scheduled cooldown for genuinely long
sessions. None implemented — this entry exists to record the real,
measured cause, not to silently pick a mitigation.

**What was done:** stopped retrying MediaCMS blindly after this diagnostic
(per explicit operator instruction on a related question earlier in this
session, "don't keep retrying without checking in") — recommended a cooldown
period before any further attempts on this hardware.

**Where it's used:** no shipped code changed by this entry — the
instrumented diagnostic script lived only in the session scratchpad, never
merged into `vapt_agent/`.

**What changes if disapproved:** nothing to revert — this is a factual
record of a real hardware condition observed during this session, not a
code or design change.

---

## 59. Dashboard cold-start priors recalibrated using real data from the two successful capstone runs (2026-09-04)

**What happened:** per explicit operator instruction ("use the data from
Juice Shop and Myco runs, especially time data, for future calculations and
predictions"), recomputed `vapt_agent/dashboard/compute.py`'s
`ROLE_MODEL_DEFAULTS` cold-start priors for Strategist, Gatekeeper (Gate 1),
and Operator directly from `model_invocation_logs` in both successful real
capstone runs (`capstone-runs/2026-09-03_{juiceshop,myco}_run1.md`) —
replacing the earlier estimate-based figures (item #55's `850.0` midpoint
guess for Strategist; the original spec placeholders for Gatekeeper/
Operator, never previously calibrated at all).

**Method:** for each role, `prior_tok_per_sec = mean(completion_tokens /
latency_s)` and `prior_seconds_per_turn = mean(latency_s)`, across every
real, finalized turn recorded for that role in both runs combined — matching
`FR-DASHBOARD-10`'s own definition of per-turn `Speed`, so the prior is
computed the identical way the live EMA figure will be once real data
exists, not an arbitrarily different formula.

| Role | n (real turns) | New `prior_tok_per_sec` | New `prior_seconds_per_turn` | Old value |
|---|---|---|---|---|
| Strategist | 2 (Juice Shop 3578tok/1790.1s, myco 2776tok/1436.1s) | 1.97 | 1613.1s | 10.7 / 850.0 |
| Gatekeeper | 9 (5 Juice Shop + 4 myco Gate 1 calls) | 2.99 | 59.6s | 11.0 / 8.0 |
| Operator | 3 (Juice Shop only — myco never invoked it, 0 approved tasks) | 2.05 | 75.5s | 28.5 / 15.0 |

**Judgment call, documented:** Operator's 3 real turns include one real,
much-slower first call (184.3s, real cold-start/cache-warming cost) beside
two much faster follow-on calls (30.8s/11.5s) — used the plain mean across
all 3 rather than treating the first specially, since `FR-DASHBOARD-12`'s
own fallback is used specifically for a role's *very first* turn in a fresh
engagement, and a plain mean folds in exactly the kind of first-turn-heavy
variance a genuine "next call could be slow" prediction should reflect,
rather than only ever showing the faster steady-state number.

**Left unchanged:** Linter/Adjudicator/Reporter — neither successful run
ever reached Phase 4.3 or invoked the Offline Linter (both completed with
zero candidates), so no real data exists yet for those three roles; their
priors remain the original, uncalibrated spec placeholders, correctly
labeled `[ESTIMATING]` per `FR-DASHBOARD-12` until a real run actually
exercises them.

**Verification:** `ruff check .`/`mypy --ignore-missing-imports` clean;
full `pytest -q` — 606 passing, 3 skipped, no test hardcoded the old prior
values.

**Where it's used:** `vapt_agent/dashboard/compute.py::ROLE_MODEL_DEFAULTS`.

**What changes if disapproved:** revert the three changed tuples back to
item #55's values (`Strategist: 10.7, 850.0`) or the original spec
placeholders (`Gatekeeper: 11.0, 8.0`; `Operator: 28.5, 15.0`) — a
self-contained data change with no other coupling.
