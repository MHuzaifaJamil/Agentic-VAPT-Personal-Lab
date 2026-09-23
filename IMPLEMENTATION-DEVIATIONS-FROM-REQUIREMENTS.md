> ⚠️ **DO NOT INGEST THIS FILE AS A REQUIREMENT.** This is a factual record of where the
> REAL, RUNNING CODE on the Implementing PC (`../implementation/`) diverges from the literal
> text of the numbered requirement docs (`01`–`24`) on this Requirement-Specifying PC, and
> why — kept alongside them, not merged into them, per the operator's own instruction
> (2026-09-08): *"Make a New MD File Along Side Requirement Files in which document such
> changes that we have done during actual implementation (On Implementing PC) which conflict
> the original requirements (From other Requirement Specifying PC) and state the reason of
> such changes."* A build agent must still treat `01`–`24` as the binding spec; this file
> exists so the NEXT requirements-sync pass (like the 2026-09-08 GitHub pull earlier this
> project) has a ready-made list of what to reconcile, instead of the two sides silently
> drifting apart. Every entry below has already been implemented and operator-approved —
> this is not a staging/discussion log awaiting a decision (see `STAGING-Pending-
> Discussions-and-Fixes.md` for that kind of thing); it's the opposite: a decision already
> made in code, recorded here so the spec can catch up to it deliberately.

---

# Implementation Deviations From Requirements

**Ordering convention:** newest on top, same as `STAGING-Pending-Discussions-and-Fixes.md`.

---

> ✅ **2026-09-22 RECONCILIATION PASS (decision #78).** Every entry below dated 2026-09-08
> through 2026-09-16 has now been reconciled into the binding corpus — the narratives below
> are kept verbatim (incident detail has real value the reconciled requirement text doesn't
> restate), but the spec has caught up to them. Mapping: 2026-09-16 (round loop) →
> `01:FR-COUNCIL-19`/`19a`/`19b`/`19c`; 2026-09-14 (Gate 1 destination check) →
> `01:FR-COUNCIL-03a`, `14` §2/3/6 `TARGET` fields; 2026-09-13 `StructuredOutputError` →
> `01:FR-COUNCIL-09a`, `03`'s `task_queue.status`; 2026-09-13 knowledge ingestion →
> `01:FR-COUNCIL-07b`; 2026-09-13 `llama-server -np 1` → `02:NFR-RES-07`; 2026-09-12 suspend
> inhibition → `06:OPS-LIFECYCLE-05`; 2026-09-12 Strategist timeout → `02:NFR-PERF-06`;
> 2026-09-10 credential storage architecture → `01:FR-TOOL-15a`, `03:DR-SCHEMA-24`,
> `05:SEC-DATA-05`; 2026-09-09 `FR-GATE-10` widening → reflected directly in `01:FR-GATE-10`'s
> own text; 2026-09-08 hibernation allowlist → `01:FR-ENV-03`/`03b`; 2026-09-08
> `start_time_ticks` → `03:DR-SCHEMA-13`. Also reconciled from real fixes recorded only in
> `STAGING-Pending-Discussions-and-Fixes.md`'s Rounds 15/16/18/19/20/22 archive (never
> entered here as their own dated deviation entries): the Auditor's role-boundary rewrite
> (Round 15) → `01:FR-COUNCIL-04`, `14` §2; verified-open-ports threading (Round 16) →
> `01:FR-COUNCIL-07a`, `03`'s `targets.verified_open_ports`; unconditional `INFO_REGISTER`
> (Round 16) → `01:FR-COUNCIL-17`; CLI self-resume on engine-unresponsive (Round 18) →
> `01:FR-GATE-08a`; per-vector zero-yield breaker rescoping + ceiling raise (Round 20) →
> `01:FR-COUNCIL-11e`; candidate-detection widening (Round 22) → `01:FR-COUNCIL-12a`.
> Deliberately NOT reconciled into requirement text — judged cosmetic/edge-case, not worth
> their own requirement: Round 21's `host:port` target-resolution fallback (folded as one
> sentence into `01:FR-COUNCIL-03a` instead of its own ID) and Round 19/22's dashboard/
> console-only readability fixes (ETA-overrun display, unclipped journal text, stale-row
> exclusion — the last of these DID get `01:FR-COUNCIL-19c`/a `TP-ROUNDLOOP` row since it's a
> correctness fix, not cosmetic).

---

## 2026-09-24 — Baseline recon context-overflow: two live incidents (katana, then ffuf), plus a general defensive cap

**Status: ✅ IMPLEMENTED, ✅ unconditional correctness fix (no operator decision needed —
two real, verified-live bugs, each with a purpose-built upstream flag as its fix, plus an
obviously-necessary general backstop once the SAME failure mode hit twice in one night from
two different tools). Found live, first real engagement to run a genuinely fresh baseline
recon pass since the FR-BASELINE-06 tool arsenal grew to its current size — every prior
engagement tonight reused an already-completed `baseline_recon_runs` row (Round 26), which is
why neither of these ever surfaced before.

### What the requirement says

`01:FR-BASELINE-06` covers the Wave 3 crawling tool set (katana among them); nothing in the
numbered corpus addresses response-body volume from any Wave 3 tool, or a size/token cap on
`baseline_recon_findings`.

### What real code did before this fix, and the real incident that exposed it

Engagement 30 (target `127.0.0.1:3000`, a brand-new target row with no prior recon) ran a
full, genuinely fresh baseline recon pass — first time in a long while, since every other
recent engagement's target already had a completed row and skipped straight past it. katana's
default `-jsonl` output embeds the FULL response body (and a raw request/response dump) for
every crawled URL, not something `orchestrator/baseline_recon.py::katana_args` opted into —
katana just does this unless told not to. Against Juice Shop's real, large, minified Angular
bundle (`main.js`), this put its entire 2.5MB content into ONE JSONL record; katana's total
raw stdout for this single target came to 3,471,775 characters (~868,000 tokens). `to_context_
block()` feeds every Wave's raw tool stdout to the Strategist verbatim, by explicit design
("MUST NOT be re-summarized by a model first") — against this host's ~15,360-token context
window, the resulting prompt was ~56x over budget. `llama-server` rejected the Strategist's
very first request outright with HTTP 400; `engine_client.chat_completion`'s
`urllib.request.urlopen` call raised `urllib.error.HTTPError`, a type none of `cli/run.py`'s
existing except blocks (`ModelFileMissingError`/`DegradedSwapAlert`/`EngineUnresponsiveError`)
catch — it propagated uncaught, crashing the whole `vaptctl run` process before a single
hypothesis was ever proposed, and (the same class of gap as the already-fixed 2026-09-23
entry below, just a different exception type) left `engagements.status` stuck `IN_PROGRESS`
with a dead `orchestrator_pid` until manually cleaned up.

### What real code now does

`katana_args` (`orchestrator/baseline_recon.py`) now passes `-ob`/`-omit-body` and
`-or`/`-omit-raw` — katana's own purpose-built flags for exactly this; the Strategist only
ever needed the discovered URL (`request.endpoint`), never each page's full body. Verified
against the real live target, not just a mocked unit test: 2,973,806 bytes → 3,529 bytes, a
~842x reduction. New regression test `test_katana_omits_response_body_and_raw_dump`
(`tests/test_orchestrator_baseline_recon.py`).

**Second incident, same night, same root cause class:** relaunching Engagement 30 with the
katana fix in place still crashed the same way. Root-caused to ffuf: against Juice Shop's
client-side-routed SPA, every fuzzed path returns the identical 200 OK catchall shell page —
with no filtering, ffuf reported all 6,400 `common.txt` wordlist entries as "matches," none
real, contributing 317,312 raw characters (~79,300 tokens) on its own. `ffuf_args` now adds
`-ac`/`-auto-calibrate` — feroxbuster/gobuster in the same Wave already auto-filter
duplicate/wildcard-shaped responses by default; ffuf's own equivalent defaults to off and has
to be requested explicitly. Verified against the real live target: 6,400 reported matches →
0. New regression test `test_ffuf_auto_calibrates_against_spa_catchall_false_positives`.

**General defensive backstop, now also implemented** (reversing the original plan to leave
this for a separate decision — the same failure mode hitting twice in one night from two
independent tools made waiting for a future design review the wrong call): `to_context_block()`
now caps any single tool's raw output at 2,000 characters (`_MAX_TOOL_OUTPUT_CHARS_IN_CONTEXT`),
with a clear truncation marker, so a future tool or a future katana/ffuf behavior change can't
reintroduce this failure mode from a third angle. This is a backstop, not a substitute for the
two root-cause fixes above — fixing the actual noisy invocation keeps real signal a Strategist
can use; the cap only bounds the worst case. Only `to_context_block()` (the Strategist-facing
text) is affected — `to_json()`/the stored `summary_json` (used by Wave 4's GraphQL/JWT
detection, Round 26's own artifact inspection) keeps the full, untruncated data. New regression
test `test_to_context_block_caps_a_single_tools_output_defensively`.

Also observed, unrelated to this codebase: the `vapt-test-lab` Juice Shop Docker container
OOM-crashed three times tonight (`FATAL ERROR: ... JavaScript heap out of memory`, exit 139)
under the load of a full baseline recon pass (ffuf wordlist fuzzing + katana crawling +
trufflehog git-history scan running across the same single Node.js process) — restarted every
time; a genuinely recurring target-environment fragility, not a Mugheeraat defect, flagged for
the operator's own attention (may warrant more Node heap headroom on container recreation).

---

## 2026-09-24 — Round 27 pipeline-flow audit: 4 correctness/robustness fixes

**Status: ✅ IMPLEMENTED, ✅ APPROVED (2026-09-24, operator directive: "Implement all staged
code remediations, verify them via the unit test suite, and halt.") — full suite: 1225
passed, 2 pre-existing unrelated gqlmap-install-drift flakes, 3 skipped. Full context and
per-item fix detail: `STAGING-Pending-Discussions-and-Fixes.md`'s Round 27 entry (Still Open
— items 5/6 of the original 6-item audit remain, one needs a live engagement to check
empirically, the other is low-priority hygiene).

### What the requirement says

`01:FR-COUNCIL-09a`/`03`'s `task_queue.status` cover the Scripter's own
`StructuredOutputError` crash guard (fixed 2026-09-13); nothing in the numbered corpus
extends that same guard to the Adjudicator role, addresses the round-progression breaker's
blind spot for a post-Phase-4.1 rejection, or addresses `DiskQuotaExceededError` propagation.
`01:FR-COUNCIL-12a` covers the 2026-09-18 candidate-detection widening; nothing in the
numbered corpus adds NoSQL/PII/directory-listing/CORS detection classes.

### What real code did before this fix, and the real gaps a direct code audit found

Four independent, previously-undiscovered gaps, all found by a full six-module line-by-line
static audit (`implementation/reports/PIPELINE-FLOW-AUDIT-REPORT-2026-09-23.md`), none
triggered by a live incident: (1) `phase_lifecycle.py::run_phase_4_3`'s `run_adjudicator(...)`
call site had no `try/except StructuredOutputError`, unlike the Scripter's identical,
already-fixed failure mode — the first real candidate to reach Gate 3 with an exhausted
structured-output retry budget would have crashed the entire engagement. (2)
`candidate_detection.py` had no detection path for `NOSQLI`, and no vocabulary-to-rule
mapping for `SECURITY_MISCONFIG`/PII-disclosure-flavored findings — 5 of this session's own
11 ground-truth Juice Shop findings (2 of them more severe) had no structural path to
`CANDIDATE` regardless of pipeline health. (3) `orchestrator/driver.py`'s round-progression
breaker (`consecutive_zero_progress_rounds`) reset to 0 the moment Phase 4.1's own
Strategy-Auditor check approved anything, blind to Phase 4.2's separate, non-bypassable
Tier0 re-check rejecting those same tasks moments later — exactly the shape of the
since-fixed `host:port` scope bug, which is what let engagement 28's first attempt run two
full rounds unflagged. (4) `DiskQuotaExceededError` (`bridge/disk_quota.py`) was raised but
caught nowhere in the codebase — would have crashed the whole engagement at ≥95% root-volume
utilization over one task's evidence write.

### What real code now does

1. `verified_vulnerabilities.status` gained a new terminal `ADJUDICATION_FAILED` value
   (`data/db.py`'s `_CHECK_CONSTRAINT_MIGRATIONS`, mirroring `MODEL_STRUCTURED_OUTPUT_FAILURE`'s
   precedent). `run_phase_4_3` now catches `StructuredOutputError` around the Adjudicator
   call and marks the finding `ADJUDICATION_FAILED` instead of letting the exception
   propagate — terminal, never re-queried back to `CANDIDATE`, no retry-count column needed.

2. `candidate_detection.py` gained NoSQL error patterns, a bulk-PII/sensitive-field rule
   (2+ emails or a genuinely sensitive field — not a bare single-email match), a
   directory-listing (autoindex) rule, and a CORS-misconfiguration rule deliberately scoped
   to the actual dangerous shape only (non-wildcard origin + `Allow-Credentials: true`) —
   **not** the generic "missing header"/"wildcard alone" shape the operator directive's
   literal wording suggested, since that would have reintroduced exactly the noise class the
   Primary Scripter's own system prompt (`prompts.py:332-336`) explicitly tells it to ignore.
   `nikto`/`testssl`/`wafw00f` are now admitted into the Tier 1 filter, routed through the
   same generic content rules. Judgment call recorded per CLAUDE.md's new Directive 5
   (mandatory critical analysis of every instruction) — see the STAGING entry for the full
   reasoning.

3. `driver.py`'s zero-progress-round reset is now deferred until after Phase 4.2 actually
   runs each round, gated on whether anything from that round survived Phase 4.2's own Tier0
   re-check.

4. `council/task_runner.py::run_gated_task` now catches `DiskQuotaExceededError` around
   tier1/tier2 execution and marks the task `DEFERRED` (mirroring the existing
   `policy_refused` precedent), with the reason recorded in `gate2_rationale` — the same
   column every comparable terminal status already uses for dashboard/console visibility.

All four fixes came with a regression test verified to fail against the pre-fix code and
pass against the fix (not just "added a test that happens to pass") — see the STAGING entry
for each test's name and file.

---

## 2026-09-23 — `vaptctl run`'s fatal exit paths left an orphaned `llama-server` process and a stale `IN_PROGRESS` status

**Status: ✅ IMPLEMENTED, ✅ unconditional correctness fix (no operator decision needed — a
resource leak and a state-inconsistency bug, not a design choice with a real counter-option).
Found live during engagement 28's resumed run.

### What the requirement says

`01:FR-GATE-08`/`FR-GATE-08a` cover `EngineUnresponsiveError`'s self-recovery path
specifically; nothing in the numbered corpus addresses `DegradedSwapAlert`
(`FR-GATE-10`'s own memory gate refusing a role's model load) or `ModelFileMissingError`
reaching `cli/run.py::run()`'s top level.

### What real code did before this fix, and the real incident that exposed it

Both `DegradedSwapAlert` and `ModelFileMissingError` called `sys.exit(1)` immediately, with
no cleanup and no DB update — unlike `EngineUnresponsiveError`, which
`orchestrator/driver.py` already marks the engagement `PAUSED` for before re-raising, these
two fire from OUTSIDE `run_full_engagement`'s own error handling entirely. Confirmed live,
twice in the same session, resuming engagement 28: a `MemAvailableGate` refusal loading the
next role's model left the PREVIOUSLY loaded role's `llama-server` (spawned with
`start_new_session=True`, so it survives its parent's exit as a genuine orphan — reparented
to init) running unsupervised for hours, consuming ~11-13GB RAM with nothing left to ever
unload it. Because each fresh `vaptctl run` invocation creates a brand-new
`LlamaCppEngineClient()` with no memory of any prior orphan, the SAME refusal (now with even
less headroom) recurred on the very next attempt — a self-reinforcing failure loop. Separately,
`engagements.status` stayed `IN_PROGRESS` indefinitely after either crash, indistinguishable
from "still actually running" via `vaptctl status`/`state.db` alone, even with the process
long dead.

### What real code now does

New `LlamaCppEngineClient.unload_current_if_any()` (`engine/client.py`) — a public,
safe-to-call-unconditionally wrapper around the existing `unload()`. `cli/run.py::run()`
gained an outer `try`/`finally` around its whole model-loading/engagement-loop region,
calling this on every exit path (a clean `break`, any of the three `sys.exit(1)` branches, or
a genuinely unexpected exception — `finally` runs on `SystemExit` too). `DegradedSwapAlert`
and `ModelFileMissingError` now also mark the engagement `PAUSED` (clearing
`orchestrator_pid`), mirroring `driver.py`'s own convention exactly.

**Verification:** 2 new `engine/client.py` tests (real fake-server subprocess, confirms
`unload_current_if_any` actually reaps the process — not just signals it — and is a clean
no-op when nothing is resident) and 3 new `cli/run.py` tests (both new `PAUSED` paths, plus
confirming the cleanup call fires on the success path too). Full suite clean: 1198 passed, 3
skipped (2 pre-existing, unrelated `gqlmap`-install-drift flakes).

### Why this deviates / where it should land in the corpus

Not a text conflict — a gap the spec never closed. `01:FR-GATE-08` (or a new adjacent ID)
could extend its self-recovery framing to name `DegradedSwapAlert`/`ModelFileMissingError`
explicitly as fatal-but-must-still-clean-up-and-record paths, matching
`EngineUnresponsiveError`'s already-specified treatment. Flagged for the next reconciliation
pass.

---

## 2026-09-23 — `FR-BASELINE-06`'s Wave 1 domain/DNS-enumeration group now skips IP-only targets

**Status: ✅ IMPLEMENTED, ✅ APPROVED (operator decision, Staging Round 25, 2026-09-23:
"Approved — Skip Wave 1 domain/DNS tools when the target host is an IPv4/IPv6 address.
Record this optimization in IMPLEMENTATION-DEVIATIONS-FROM-REQUIREMENTS.md against
FR-BASELINE-06."). Full write-up in `STAGING-Pending-Discussions-and-Fixes.md`'s Archive,
Round 25.

### What the requirement says

`FR-BASELINE-06`'s Wave 1 table lists `subfinder`/`assetfinder`/`knockpy`/`sublert`/
`puredns`/`shuffledns`/`theHarvester`/`dnsrecon` (alongside `naabu`) as an "Always" group —
dispatched unconditionally, with no target-shape condition in the literal text.

### What real code did before this fix, and the real incident that exposed it

All nine Wave 1 tools dispatched regardless of whether `targets.host_or_domain` was a domain
or a bare IP. Checked directly against real engagement 26/27 DB rows (tasks 596-605): 8 of
10 exited `0` (not errors) but every one of the eight domain/DNS-enumeration tools returned
empty, no-op output against `127.0.0.1` — subdomain/DNS enumeration has nothing to enumerate
against a bare IP by construction. This project's own real test targets (Juice Shop,
MediaCMS) are both IP-only, so this was wasted real tool-timeout-tier wall-clock on every
single engagement run to date, not a hypothetical.

### What real code now does

New `_is_ip_or_loopback_target()` helper (`orchestrator/baseline_recon.py`) strips a
trailing `:port` (or `[ipv6]:port`) the same way `cli/start.py`'s scope-pattern helper
already does, then checks via `ipaddress`. All eight domain/DNS args-builders
(`subfinder_args`/`assetfinder_args`/`knockpy_args`/`sublert_args`/`puredns_args`/
`shuffledns_args`/`theharvester_args`/`dnsrecon_args`) now return `None` (skip cleanly,
matching this file's own established gating convention — e.g. `httpx_args`, `ffuf_args`)
when the target is an IP/loopback address. `naabu_args` is untouched — port scanning is
exactly what an IP target needs, and stays in Wave 1 unconditionally.

**Verification:** 3 new tests (`test_orchestrator_baseline_recon.py`) covering an IP
target, an IP:port target, and the mirror-image domain-target-unaffected case; 1 updated
real-subprocess test (`test_orchestrator_baseline_recon_real_execution.py`) confirming only
`naabu` dispatches in Wave 1 against `127.0.0.1` end to end — that same update also fixed an
unrelated, pre-existing test-assertion gap found while touching this file (the Wave 3
katana/nuclei/gospider gating check only looked at `outcomes`, not `not_completed`, so a
real subprocess landing in `not_completed` under this test's tight 10s `wave_ceiling_s` read
as a gating inconsistency rather than the wave-ceiling mechanism working as designed — now
checks both, matching Wave 1's own already-correct convention). Full suite clean: 1192
passed, 3 skipped (3 pre-existing, confirmed-unrelated environmental flakes — HIBP/swap-
growth/gqlmap-install-drift, none touched by this change).

### Why this deviates / where it should land in the corpus

`FR-BASELINE-06`'s Wave 1 table could gain a target-shape condition column, or a footnote,
noting the domain/DNS-enumeration subset is IP-conditional while `naabu` remains
unconditional. Flagged for the next reconciliation pass.

---

## 2026-09-22 — Gate 2 denylist rule (c) false-positived on `/dev/null` and curl's `-w`, silently blocking the one probe shape needed for real access-control-class detection

**Status: ✅ IMPLEMENTED, ✅ unconditional correctness fix (no operator decision needed — no
real alternative reading exists: `/dev/null` cannot exfiltrate data by construction, and
curl's `-w`/`--write-out` is never a file destination for any tool in this project's
arsenal). Full write-up, including the two other bugs found in the same investigative pass,
in `Assumptions-Not-Approved.md` item #66 and `../implementation/reports/
JuiceShop-VAPT-Testing-Guide-2026-09-19.md` §3.5.

### What the requirement says

`01:FR-TOOL-06`(c)/`bridge/denylist.py`'s own docstring: "file write/delete/rename whose
target resolves outside the artifact path" is rejected — the requirement's intent is
preventing a tool from persisting data somewhere it could leak or survive engagement
teardown, never named `/dev/null` or curl's `-w` specifically.

### What real code did before this fix, and the real incident that exposed it

`check_behavioral_denylist`'s `output_flags` set bundled curl's `-w` alongside genuine
file-destination flags (`-o`/`-O`/nmap's `-oA`/`-oN`/`-oX`/`-oG`), and resolved EVERY such
flag's value as a candidate filesystem path via `Path(target).resolve()` with no exemption
for `/dev/null`. Confirmed on a real DB row (engagement 27, task 575):
`curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:3000/api/coupon/apply?code=TESTCOUPON`
— a well-formed, low-noise status-code-only probe, exactly the idiom
`council/candidate_detection.py`'s access-control-class rule needs to have any chance of
firing — was rejected `[c]: output flag '-o' points outside the artifact store: /dev/null`.

### What real code now does

`bridge/denylist.py`: `-w`/`--write-out` removed from `output_flags` entirely (curl's `-w`
is a stdout format string, never a file write, and no other tool in the arsenal uses a bare
`-w` for real file output — nmap's own file-output flags are the already-listed
`-oA`/`-oN`/`-oX`/`-oG`); `/dev/null` explicitly exempted from rule (c)'s resolution check
(it discards its input — the one destination that structurally cannot persist or exfiltrate
anything, making "outside the artifact store" the wrong framing entirely).

**Verification:** 2 new regression tests (`tests/test_bridge_denylist.py`) covering both
exemptions directly, plus the existing rule (c) tests re-verified still correctly block a
real outside-artifact-store write. Full suite clean (1188 passed, 3 skipped).

### Why this deviates / where it should land in the corpus

`01:FR-TOOL-06`(c)'s text (and `bridge/denylist.py`'s own docstring) could note both
exemptions explicitly — `/dev/null` as a standing safe destination, and that `-w` is
excluded from the output-flag set because its value is never a file path for any currently-
registered tool. Flagged for the next reconciliation pass.

---

## 2026-09-22 — `vaptctl start --targets host:port` silently broke Gate 1 scope matching for every real attack command

**Status: ✅ IMPLEMENTED, ✅ unconditional correctness fix (no operator decision needed — the
scope pattern must match what the real-destination check actually extracts; there is no
alternative reading where a port-carrying pattern is correct). Full write-up in
`../implementation/reports/JuiceShop-VAPT-Testing-Guide-2026-09-19.md` §3.4.

### What the requirement says

`01:FR-COUNCIL-03a` (as reconciled 2026-09-22, folding in the 2026-09-14 destination-check
fix below) requires Gate 1 Tier 0's scope check to validate a command's real network
destination, deterministically. It doesn't specify how `vaptctl start`'s own
`--scope-rules`-omitted auto-derived scope should handle a `--targets` value that itself
carries a port.

### What real code did before this fix, and the real incident that exposed it

`cli/start.py`'s auto-derived scope stored the raw `--targets` string verbatim as the
scope-rules `pattern` — `--targets 127.0.0.1:3000` produced pattern `"127.0.0.1:3000"`, port
included. But `check_tier0`'s real-destination check (`extract_destination_candidates`,
`urlparse(...).hostname`) always extracts a bare, port-stripped host from a proposed
command's argv. `_pattern_matches` then compared `"127.0.0.1"` against `"127.0.0.1:3000"`:
the target is a valid IP, the pattern (with the port attached) is not, so the IP-vs-domain
branch rejected the match outright. Confirmed live on engagement 28: 5 of its first 6 real
attack tasks (XSS/IDOR/SSRF/BROKEN_AUTH/nmap) were Gate-1-rejected by this, not by any real
safety concern. Engagements 26/27 never hit this — they used a bare `127.0.0.1` (no port)
throughout, which matches fine; this is the first engagement to use explicit `host:port`
targeting (needed to avoid the port-confusion problems `httpx_args`'s own 2026-09-11 finding,
and this session's katana/nuclei/gospider entry below, both document).

### What real code now does

New `_scope_pattern_for_network_target()` helper in `cli/start.py` strips a trailing
`:port` before it becomes a scope pattern — handles bare `host:port`, IPv4, and bracketed
`[ipv6]:port`; leaves anything else (a bare domain/IP, or an ambiguous multi-colon string
with no port) untouched. `targets.host_or_domain` itself, and the `targets` list passed to
everything else, keep the port — only the scope-rules pattern changes.

**Verification:** 3 new regression tests (`tests/test_engagement_lock.py`). Full suite clean
(1188 passed, 3 skipped).

### Why this deviates / where it should land in the corpus

`01:FR-COUNCIL-03a`'s text could note explicitly that an auto-derived scope pattern is
always the bare host/domain identity, never carrying a port, regardless of what shape
`--targets` was given in. Flagged for the next reconciliation pass.

---

## 2026-09-18 (fix landed 2026-09-22 session, backdated to match the incident) — `katana`/`nuclei`/`gospider` Wave 3 args used a non-existent flag and ignored the discovered live port

**Status: ✅ IMPLEMENTED, ✅ unconditional correctness fix (no operator decision needed — a
non-existent CLI flag and a missing-port bug both have exactly one correct fix). Root-caused
from engagement 27's real DB rows per the operator's own post-mortem request. Full write-up
in `../implementation/reports/JuiceShop-VAPT-Testing-Guide-2026-09-19.md` §3.1.

### What the requirement says

`01:FR-BASELINE-06`'s Wave 3 crawling group names `katana`/`gau`/`waybackurls`/`gospider`
as a set, without specifying exact CLI flags — those are an implementation detail, but the
existing `httpx_args` (2026-09-11 finding, already in this file) establishes the binding
precedent that a Wave 3/4 tool needing a concrete scheme+host+port MUST get it from Wave 2's
live-URL discovery, never a bare target string.

### What real code did before this fix, and the real incident that exposed it

`baseline_recon.py::katana_args` passed `-json`, which does not exist in real katana (only
`-j`/`-jsonl` do, confirmed against `katana -h`) — every real invocation exited immediately
with `flag provided but not defined: -json` and produced zero output, every round.
Separately, `katana_args`/`nuclei_args`/`gospider_args` all crawled the bare `target_value`
instead of Wave 2's live scheme+port URL — the same missing-port bug `httpx_args` was
already fixed for. Confirmed live on engagement 27's real `tool_execution_logs`/
`artifacts_index` rows: katana's raw artifact was the literal 38-byte error string above,
for every round of the engagement. This left the Strategist with no real crawl to work from
— it hallucinated generic REST-shaped endpoint guesses (`/blog`, `/api/webhook`,
`/api/users/1`) that don't exist on the real target instead of real, discovered ones.

### What real code now does

`katana_args`/`nuclei_args`/`gospider_args` (`orchestrator/baseline_recon.py`) all gated on
`_first_live_url_from_wave2`, matching the existing `ffuf`/`feroxbuster`/`gobuster`
convention exactly (skip cleanly if no live URL, never guess); `katana_args`'s flag
corrected to `-jsonl`.

**Verification:** 6 updated tests in `test_orchestrator_baseline_recon.py` (assertions that
previously expected these three to always dispatch now correctly expect them gated, matching
ffuf/feroxbuster/gobuster's existing pattern) and 1 in
`test_orchestrator_baseline_recon_real_execution.py`. Full suite clean (1188 passed, 3
skipped).

### Why this deviates / where it should land in the corpus

Not a text conflict — `01:FR-BASELINE-06` never specified the exact flags or the live-URL
gating requirement for these three tools specifically; the existing `httpx_args` precedent
already establishes the pattern these three should have followed from the start. No spec
change needed; flagged only so a future audit doesn't re-derive this from scratch.

---

## 2026-09-16 — Engagement lifecycle now loops council rounds until real coverage exists; Auditor loses all scope authority; Scripters get verified ports

**Status: ✅ IMPLEMENTED, ✅ APPROVED (explicit operator directives, same day, following
engagement 24's live results — the first real test of the 2026-09-14 target_host/Gate-1
fix).** Full write-up in `STAGING-Pending-Discussions-and-Fixes.md` Rounds 15/16 (Archive).

### What the requirements say, and where these diverge

- `FR-COUNCIL-11`/`11a` describe a per-target task cap and a "zero-yield circuit breaker" as
  loop-bound config values, but no code anywhere consumed either (confirmed by grep — both
  were dead config). `01`'s Council Roster never states the engagement-level stop condition
  for how many full Strategist→Scripter→Adjudicator→Reporter cycles a single engagement runs;
  every real engagement to date (including engagement 24) ran exactly one. This is now a
  bounded loop, config-driven (`loop_bounds.min_confirmed_reports`,
  `.max_council_rounds`, and `.zero_yield_circuit_breaker` — now actually wired) —
  see `orchestrator/driver.py::run_full_engagement`.
- The Gate 1 Tier 1 semantic prompt (`ROLE_BLOCK_GATE1_SEMANTIC`, doc 14 §2) described a
  "scope-and-risk auditor" that could reject on scope-creep grounds — but Tier 0 (the same
  requirement doc, same section) already deterministically settles scope membership before
  the semantic model ever runs. Doc 14 never explicitly forbade the semantic Auditor from
  re-litigating scope anyway, and it did, live (engagement 24: 6/7 hypotheses rejected/revised
  over loopback-address reasoning). The role is now explicitly, completely stripped of any
  scope/reachability/topology authority — renamed `ROLE_BLOCK_AUDITOR` for clarity.
- `01`'s baseline-recon requirements (`FR-BASELINE-01..06`) never state that naabu's
  discovered ports should reach the Scripter prompts directly — only that Wave 2's own nmap
  call consumes them. Live: a Secondary Scripter follow-up scanned 80/443 instead of the
  genuinely open 631/3000 baseline recon had found. New `targets.verified_open_ports` column
  now threads that same data into every Scripter prompt.
- `FR-COUNCIL-17`/`17b` (the Reporter/`INFO_REGISTER`) never require a markdown artifact when
  an engagement finds nothing — `_write_or_update_info_register` was gated behind
  `any_remediated` (regression-only). An engagement could reach `COMPLETE` with zero report
  files of any kind. It now always writes a coverage-summary `INFO_REGISTER` document.

### Why

Direct operator instructions, in order, following a review of engagement 24's real results:
"Engagements should loop between council models until a substantial amount of VAPT reports as
Markdown files, are generated... if it does NOT produce any reports, then it is useless";
"[Auditor's scope reasoning] should never Happen ever!! fix it"; "make sure that whenever a
task is dispatched to Primary or Secondary Scripters: The prompt explicitly injects the
verified active ports discovered during Phase 2 baseline recon... forbidding scans/requests
to closed default ports (80/443) when known open ports... are already mapped." The
`min_confirmed_reports` config default was set to 5 specifically for the operator's requested
JuiceShop confirmation run (a deliberately vulnerable app) — see `Assumptions-Not-Approved.md`
item #61 for the judgment calls made picking the surrounding bounds (`max_council_rounds`,
reusing `zero_yield_circuit_breaker`) that the operator did not specify numerically.

### Where used

`orchestrator/driver.py` (round loop), `council/prompts.py`
(`ROLE_BLOCK_AUDITOR`), `orchestrator/baseline_recon.py`
(`_record_verified_open_ports`), `council/primary_scripter.py`/`secondary_scripter.py`
(`verified_open_ports` param), `orchestrator/phase_lifecycle.py`
(`_write_or_update_info_register` now unconditional, `_fetch_verified_open_ports`).

### What changes if disapproved

Revert `min_confirmed_reports`/`max_council_rounds` to effectively 1 (single-round behavior,
the pre-2026-09-16 default); restore the Auditor's scope-judgment framing (not recommended —
directly caused the live regression this closes); stop persisting/injecting
`verified_open_ports` (Scripters return to guessing ports); re-gate `INFO_REGISTER` writes
behind `any_remediated` (engagements can again complete with zero report artifacts).

---

## 2026-09-14 — Gate 1 Tier 0 now checks a command's ACTUAL network destination, not just the task's static registered target

**Status: ✅ IMPLEMENTED, ✅ APPROVED (operator explicitly selected this exact design —
"Both: explicit host param + Gate 1 host-scope check" — after asking why OWASP Juice Shop
had produced zero confirmed vulnerabilities across every real engagement run to date). Full
write-up, the two reproduced real incidents, and the extraction-rule design are recorded in
`Assumptions-Not-Approved.md` item #60.

### What the requirement says

`01:FR-COUNCIL-03a` requires Gate 1 Tier 0 to be a "non-bypassable" deterministic scope
check, and lists scope-membership as one of its sub-checks, but its literal text never
specifies WHICH string that check validates. `FR-COUNCIL-07`/`09`/`10` describe the Primary/
Secondary Scripter turning a Gate-1-approved task into a concrete command, but never state
how the Scripter learns which host to actually send that command to.

### What real code did before this fix, and the real incident that exposed it

Gate 1 Tier 0's scope check (`council/strategy_auditor.py::check_tier0`) validated the
task's own STATIC registered `targets.host_or_domain` string against `scope_rules` —
trivially always true, since that string is literally where the scope rule came from.
Nothing anywhere checked a proposed command's own `argv` for what host it would actually
reach. Separately, neither Scripter's prompt (`council/primary_scripter.py`/
`secondary_scripter.py`) ever stated the real target host explicitly — a database audit
found only 3 of 25 real Strategist-authored task descriptions ever mentioned the target's IP
at all, leaving the model to infer a destination from context that usually wasn't there.

Confirmed live, twice, across the only real completed/near-completed engagements this
system has run: the Primary Scripter produced `curl http://example.com/api/users` (a real
outbound request to IANA's internet placeholder domain, not the target) and the Secondary
Scripter produced `nmap --script http-enum target_system_ip` (a literal unresolved
placeholder; nmap correctly resolved 0 hosts). Both were logged `EXECUTED`/`SUCCESS`. This
is the direct root cause behind "zero vulnerabilities found across 23 engagements" against
a deliberately vulnerable target — the tooling had barely ever actually reached it.

### What real code now does

`run_primary_scripter_command(_retry)`/`run_secondary_scripter_command(_retry)` gained a
required `target_host: str` parameter, injected as an explicit, imperative `TARGET` prompt
field ("every command below must resolve its network destination to ... never substitute a
placeholder, documentation example, or any other host"), reinforced in both role system
prompts (`council/prompts.py`). `orchestrator/phase_lifecycle.py` fetches it once per task
from `targets.host_or_domain` via a new `_fetch_target_host` helper.

`check_tier0` gained a new, NETWORK-pattern-kind-only check (deterministic, zero LLM
involvement, per `FR-COUNCIL-03a`'s own non-bypassable requirement) that inspects the
proposed command's real `argv` via `extract_destination_candidates` — three combined rules:
a URL-shaped token anywhere (excluding a small denylist of flags whose value can
legitimately carry an unrelated URL — headers, referer, proxy); the Tier 1 tool's own
declarative schema (`bridge/tier1/schema.py`, the same one Gate 2 validates against) walked
via its `takes_value` metadata to correctly isolate genuinely unconsumed positional
arguments, checking the tool's `required_positional_count` of them regardless of shape
(extracting a URL's host first when the positional is a full URL, not a bare host); and a
shape-match fallback (IP/CIDR/proper hostname) for a Tier 2 binary with no schema to lean
on. Restricted to autonomous council-origin tasks by construction — `check_tier0` is never
called on the `HUMAN_OPERATOR`-origin path at all (`FR-INTERVENE-06a`'s existing bypass),
satisfying the operator's explicit constraint that this must never intercept a direct
operator instruction.

A real regression was found and fixed during the same implementation pass: an early version
of the schema-driven positional check validated a required positional's raw string against
scope without first extracting the host from it, which broke 2 pre-existing tests for tools
whose required positional is a full URL rather than a bare host (`graphql_scanner`,
`credential_spray`) — fixed before merge, full suite re-verified clean.

**Verification:** both real historical incidents reproduced against the exact `argv`
recorded in `model_invocation_logs` and confirmed rejected; both real legitimate commands
(the same tools, correctly targeting the real host) confirmed still approved; 27 new/updated
regression tests; full suite 1126 passed, 0 failed, 3 skipped; `ruff`/`mypy` clean.

### Why this deviates / where it should land in the corpus

`01:FR-COUNCIL-03a`'s scope-check text would need to explicitly name the command's own
destination (not just the task's registered target) as what Tier 0 validates. `14-System-
Prompt-Templates.md`'s Primary/Secondary Scripter role-block excerpts would need a `TARGET`
field added to match the real prompt. Flagged for the next reconciliation pass.

---

## 2026-09-13 — `StructuredOutputError` (retry-budget exhaustion) now degrades one task instead of crashing the whole engagement

**Status: ✅ IMPLEMENTED, ✅ unconditional correctness fix (no operator decision needed —
the alternative was an engagement-ending crash, not a design choice with a real
counter-option). Full write-up and the real crash data are in `../implementation/reports/
BENCHMARK-REPORT-2026-09-13.md` §12.

### What the requirement says

`01:FR-COUNCIL-09` requires a Gate-2-rejection retry budget (3 attempts) and that an
exhausted task is "never dropped or force-executed" — silent on what happens when the
model's STRUCTURED-OUTPUT retry budget (`IR-STRUCTURED-03`, a different, inner 3-attempt
budget that absorbs a genuine schema-invalid-JSON miss, not a Gate-2-rejection) is the one
that exhausts instead.

### What real code did before this fix, and the real incident that exposed it

`StructuredOutputError` was not caught anywhere between `orchestrator/phase_lifecycle.py`
and `cli/run.py`. When a council role's structured-output budget genuinely exhausted (a
real, occasional, expected model miss — exactly the class of failure that retry budget
exists to absorb), the exception propagated unhandled and crashed the entire orchestrator
process, ending the whole engagement over one task. Confirmed live, twice, in real
engagements (2026-09-13): both crashes' `tmux` panes went dead immediately following this
exact exception.

### What real code now does

`orchestrator/phase_lifecycle.py` now catches `StructuredOutputError` around the Primary/
Secondary Scripter's command-generation calls (`run_phase_4_2a`/`run_phase_4_2b`) and marks
the single task `GATE2_BLOCKED` — `task_queue.status`'s CHECK constraint (`03:DR-SCHEMA-05`)
has no dedicated value for this distinct failure mode; reusing `GATE2_BLOCKED` is the
closest existing terminal state matching `FR-COUNCIL-09`'s own "never dropped or
force-executed" language (a different reuse than `Assumptions-Not-Approved.md` item #29's,
which covers Gate-2-rejection-retry exhaustion specifically — this is a structured-output
failure, distinguished by a `MODEL_STRUCTURED_OUTPUT_FAILURE:` rationale prefix) — and the
engagement continues to the next task instead of crashing.

**Verification:** 2 new real regression tests exercising the actual retry-exhaustion code
path (a fake engine client returns 3 real schema-invalid responses, driving
`get_structured_completion` to genuinely raise through its own real logic); 18 real
reproduction attempts against the exact prompt that crashed both live engagements, all
clean (consistent with a real, low-frequency, non-reliably-reproducible model miss, not a
deterministic bug); a subsequent live engagement (23) completed fully with 12/12 real
invocations succeeding, no crash. Full suite clean at the time (1108 passed, 3 skipped).

### Why this deviates / where it should land in the corpus

`01:FR-COUNCIL-09`'s text could be extended to explicitly cover a structured-output-budget
exhaustion (distinct from a Gate-2-rejection-budget exhaustion) reaching the same
`GATE2_BLOCKED` terminal state. Left unfixed for the other 4 council roles (Strategist,
Auditor, Adjudicator, Reporter) — the same theoretical gap likely exists there too, but none
have been empirically observed to crash, so intentionally left out of scope here to keep
this fix scoped to the confirmed, real failure; flagged as a follow-up.

---

## 2026-09-13 — New capability: task-dispatched knowledge ingestion from a local skill corpus

**Status: ✅ IMPLEMENTED, ✅ APPROVED (with constraints). Full design, the approval
constraints, and the two real-corpus/real-codebase corrections made during implementation
are in `STAGING-Pending-Discussions-and-Fixes.md`'s Archive, Round 12.**

### What the requirement says

Nothing — no numbered requirement doc (`01`–`24`) mentions a skill corpus, a matcher, or a
`<task_reference>` prompt block. This is a genuinely new capability, not a literal-text
conflict with an existing requirement.

### What real code now does

New `vapt_agent/knowledge/` package: `skills_index.py` walks `~/.agents/skills/*/SKILL.md`
(configurable via `config['skills']['paths']`, `defaults.yaml`), parses each file's YAML
frontmatter once, and matches a task description against the indexed corpus via a
Szymkiewicz-Simpson token-overlap coefficient (`τ = 0.65`) or a `≥2` explicit-tag-intersection
fallback — strict silence (no injection) below both. `skill_extractor.py` slices the matched
skill's operational section (real-corpus-derived anchor priority: `Workflow` → `Common
Scenarios` → `Steps` → `Instructions` → `Objectives` → `Core Concepts` → `Overview`),
truncated to `config['skills']['max_reference_chars']` (3000 chars / ~750 tokens). Wired into
`orchestrator/phase_lifecycle.py`'s real Phase 4.2A/4.2B dispatch loops
(`run_phase_4_2a`/`run_phase_4_2b`) — one index load per phase call, one match per task,
passed through a new `skill_reference` kwarg to
`run_primary_scripter_command(_retry)`/`run_secondary_scripter_command(_retry)`
(`council/primary_scripter.py`/`secondary_scripter.py`), appended to the prompt as a
`<task_reference>` block outside `wrap_untrusted` (trusted, system-curated content, not
target-derived — same treatment `bridge/tool_discovery.py::format_discovery_block`'s existing
CANDIDATE TOOLS block already gets). 17 new tests, full suite reverified clean (1096 passed,
0 failed, 3 skipped).

### Why this deviates / where it should land in the corpus

Same class as the suspend-inhibition and Strategist-timeout entries below — never had a
documented home in the numbered corpus at all. Candidate home:
`01-Functional-Requirements.md`, a new `FR-COUNCIL-1x` alongside the existing dispatch-flow
requirements (`FR-COUNCIL-07`/`09`/`10`), or `14-...md` §3 alongside the Scripter role
descriptions — flagged for the next reconciliation pass rather than invented unilaterally.

---

## 2026-09-13 — `LlamaCppEngineClient.load()` now pins `llama-server` to a single request slot (`-np 1`)

**Status: ✅ IMPLEMENTED, ✅ unconditional correctness fix (no operator decision needed).
Full writeup, the real host-memory incident that surfaced it, and the live RSS measurements
are in `STAGING-Pending-Discussions-and-Fixes.md`'s Archive, Round 13.**

### What the requirement says

Nothing names `llama-server`'s own `-np`/`--parallel` flag anywhere in the numbered corpus.
`FR-GATE-02` establishes hard single-model-residency (loading a second model unloads the
resident one first) and `01`'s Council Roster implies one role's call in flight at a time —
both consistent with 1 request slot being correct, but neither literally specifies the
server-launch flag.

### What real code now does

`vapt_agent/engine/client.py::LlamaCppEngineClient.load()`'s server-launch command now
includes `-np`, `1` alongside the existing `--model`/`--host`/`--port`/`-t` args.
`llama-server`'s own default (`-np -1`, "auto") had been resolving to `n_slots = 4` on the
reference host (confirmed via the server's own startup log), each slot getting its own full
KV cache — a real, live-confirmed ~4x RAM overallocation (13.67GB measured RSS for a
7.16GB model at 1 slot vs. an implied ~33GB at the old 4-slot default) that a real
background benchmark run tripped over repeatedly before being root-caused. `tests/
fixtures/fake_llama_server.py` updated to accept (and ignore) the new flag, matching its
existing `-t`/`--threads` handling. Full suite re-verified clean after the change (1079
passed, 0 failed, 3 skipped).

### Why this deviates / where it should land in the corpus

Not a conflict with existing spec text so much as a gap the spec never closed — `FR-GATE-02`
describes the *model*-residency contract (one model loaded at a time) but says nothing about
the *request-concurrency* contract for the engine process itself, which turned out to matter
a great deal for real memory safety on constrained hardware. Candidate home:
`05-Security-Safety-and-Compliance-Requirements.md` or `06-Operational-Requirements.md`
alongside `NFR-RES-02`'s existing 1.5GB safety-margin language, as an explicit statement
that the local inference engine MUST be launched with request concurrency bounded to what
this system's own architecture actually uses (1), not left to the binary's own default.

---

## 2026-09-12 — New capability: system suspend inhibited for the duration of an active engagement

**Status: ✅ IMPLEMENTED, ✅ APPROVED, unit-tested (real, live `systemd-inhibit` registration
confirmed via `systemd-inhibit --list`, not mocked). Full writeup, the live verification
that preceded it, and the options considered are in `STAGING-Pending-Discussions-and-
Fixes.md`'s Archive, Round 11.**

### What the requirement says

Nothing, currently — no numbered requirement doc (`01`–`24`) mentions system suspend/sleep
at all. This is a genuinely new capability, not a literal-text conflict with an existing
requirement.

### What real code now does

A real live probe this session (`STAGING` Round 10.2's Option C latency measurement) caught
the host suspending itself mid-engagement (`s2idle`, `xfce4-power-manager`-triggered idle
timeout) while a council model was actively computing — survived unharmed only because
Linux's monotonic clock stops advancing during suspend, uncounted against any timeout
budget. Nothing previously prevented this. `vapt_agent/cli/run.py::run()` now wraps its
`run_full_engagement(...)` call in a new `hold_system_inhibition()` context manager, which
holds a real `systemd-inhibit --what=sleep:idle --mode=block` lock (via a `sleep infinity`
child process, no new Python dependency) for exactly the duration of active orchestration —
covering both the tmux-relaunched auto-start path and a direct/manual invocation uniformly,
since both converge on that one call site. Releases automatically on any exit path (normal
completion, PAUSE escalation, exception) via a `finally:` block, and is orphan-safe under
`vaptctl abort`'s process-group kill and a `systemd-oomd` cgroup-wide kill (Round 10.1)
alike, since it's a child in the same process group/cgroup rather than its own session.
Degrades to holding no lock (never fails the engagement) on a non-systemd host.

### Why this deviates / where it should land in the corpus

Candidate home: `06-Operational-Requirements.md` (engagement lifecycle) or
`05-Security-Safety-and-Compliance-Requirements.md` (a "the system must not silently lose
progress to an OS-level event" framing) — not yet decided, flagged here for the next
requirements-sync pass rather than picked unilaterally.

---

## 2026-09-12 — Strategist role's dedicated inference timeout raised from 1800s to 9000s, backed by a real measured ceiling

**Status: ✅ IMPLEMENTED, ✅ APPROVED. Full writeup, the uncapped probe that produced the
real number, and the options considered are in `STAGING-Pending-Discussions-and-Fixes.md`,
Round 10.2.**

### What the requirement says

`IR-TOOL-03`/`FR-TOOL-05`'s fixed timeout tiers (Quick Probes 180s / Targeted Scans 900s /
Deep-Full-Range 1800s) govern TOOL subprocess timeouts (`nmap`, `sqlmap`, etc.) — a
completely separate mechanism from `STRATEGIST_TIMEOUT_S`, which is the Strategist
council-role's own dedicated AI-model inference-call timeout (`vapt_agent/council/
strategist.py`), already documented in that file's own comments as intentionally NOT
sharing the generic 900s tool-timeout default. No numbered requirement doc names this
constant or its value at all — it has never been part of the literal spec text.

### What real code now does

A standalone, uncapped probe (bypassing `STRATEGIST_TIMEOUT_S` entirely, real baseline-recon
context reused verbatim from a completed engagement) measured the TRUE completion latency
for a real Phase 4.1 Strategist turn on this CPU-only reference host: **7043.4s (117.4 min,
~1h57m)** for a 12,449-prompt-token / 5,207-completion-token real exchange, producing a
genuinely coherent, target-appropriate attack plan. `STRATEGIST_TIMEOUT_S`
(`vapt_agent/council/strategist.py:48`) raised from `1800.0` to `9000.0` (150 min, ~28%
headroom over the measured ceiling) — with `FR-GATE-08`'s existing one-shot restart+retry,
a single attempt at this budget should now suffice without ever needing the retry. Full
suite re-verified clean after the change (1079 passed, 0 failed, 3 skipped).

### Why this deviates / where it should land in the corpus

Same candidate home as the suspend-inhibition entry above — this constant has never had a
documented home in the numbered corpus at all (unlike the tool-timeout tiers, which are
explicitly speced); flagged for the same future reconciliation pass rather than invented a
new requirement ID unilaterally.

---

## 2026-09-11 — `FR-BASELINE-06`: 17 more tools installed, verified, and wired for real

**Status: ✅ IMPLEMENTED, unit/integration-tested, several real invocations confirmed
end-to-end. `STAGING-Pending-Discussions-and-Fixes.md`'s Round 9 has the full writeup
(including the one real design gap this surfaced -- `git-hound`'s third-party API key --
and the two items deliberately NOT attempted this pass, `OPS-NOTIFY` and `FR-TOOL-17`'s
autonomous-login-flow half); this entry is the short, code-focused version.**

### What the requirement says

`FR-BASELINE-06`'s tool-roster table names `knockpy`, `sublert`, `puredns`, `shuffledns`,
`bbot` (Wave 1 subdomain/OSINT-enum group), `byp4xx`, `whatwaf`, `unwaf`, `log4j-scan` (Wave
3 WAF/vuln probing), `x8` (Wave 4 parameter discovery, alongside `arjun`), `graphw00f`,
`clairvoyance`, `graphql-cop` (Wave 4's GraphQL-conditional branch), `jwt_tool` (Wave 4's
JWT-conditional branch), `noseyparker`, `shhgit`, `git-hound` (Wave 1's CODE_REPO-conditional
secrets-scanning group) -- none of these were installed on the implementing host as of the
2026-09-10 audit-fix pass, and were documented there as genuinely deferred.

### What the code actually does now

All 17 are installed for real (apt was blocked by a missing `sudo` password on this host --
`knockpy` went in via its real PyPI package `knock-subdomains` instead of the apt route;
the rest via `go install`/`pipx install`/prebuilt release binaries downloaded directly from
each project's real GitHub releases/`python3 -m venv`+`pip install`-isolated manual clones),
each verified against a real `--help` before any schema was written -- and, for the ones
with identically-named-but-unrelated PyPI packages (`graphw00f`, `graphql-cop`, `x8`),
cross-checked against the package's own PyPI author/homepage/repo metadata FIRST, catching
three confirmed decoys/squatted names before installing anything (`graphw00f`'s PyPI
description literally reads "NOT the real graphw00f tool"). New Tier 1 YAML schemas for all
17 (`vapt_agent/bridge/tier1/schemas/`), wired into `orchestrator/baseline_recon.py`'s
wave-builder functions:

- Wave 1 (NETWORK): `knockpy --recon`, `sublert` (one-shot, `-q true -r true`), `puredns`/
  `shuffledns` in `bruteforce` mode (self-contained -- domain + `DEFAULT_BASELINE_WORDLIST` +
  a new bundled `vapt_agent/data/resolvers.txt`, closing the "no resolvers file" gap
  `massdns.yaml`'s own comment had flagged since the original pull), `bbot -p subdomain-enum
  -y --no-deps` (never autonomously installs a module's own extra dependencies).
- Wave 3 (NETWORK): `byp4xx`/`whatwaf`/`log4j-scan` (need Wave 2's live URL, skip cleanly if
  none), `unwaf` (bare domain, no live-URL gating).
- Wave 4 (NETWORK): `x8` (same live-URL gating as `arjun`); `graphw00f`/`clairvoyance`/
  `graphql-cop` gated on a new `_discovered_graphql_endpoint_from_summary` heuristic (regex
  over Wave 3's crawl output for a `/graphql`-shaped path); `jwt_tool` gated on a new
  `_discovered_jwt_from_summary` heuristic (regex for a `eyJ...` JWT-shaped string in Wave
  2/3 output) -- `jwt_tool`'s schema only allows its `-M` read-only scan modes, forbidding
  the exploit/tamper/crack/sign flags (same AI-gated-only posture as `sqlmap`).
- CODE_REPO (local-path only, same constraint `semgrep` already had): `shhgit -local
  <path> -config-path <bundled config.yaml copy>` (its own `--help` confirms "No need to
  have GitHub tokens with local run"); `noseyparker scan` then, in a SEPARATE wave (so it
  never races `scan` within one wave's concurrent dispatch), `noseyparker report` reading
  back the same relative datastore path.

### A real, pre-existing bug this surfaced and fixed

`bridge/tier1/tools/graphql_scanner.py` (an existing Tier 1 tool from Milestone 9, unrelated
to this pull) had a `graphw00f`-invocation code path written when `graphw00f` was never
actually installed to test against -- it assumed a pip-importable package shape
(`python3 -m graphw00f.main`) and treated ANY non-empty subprocess output, including
`graphw00f`'s own connection-error text, as a valid fingerprint finding. Installing the real
`graphw00f` CLI activated this dead code path for the first time and immediately surfaced
both bugs via the full test suite (not missed) -- fixed to invoke the real resolved binary
with its actual CLI flags and only record a finding on a genuine `returncode == 0`.

### What's still a real, disclosed gap

`git-hound` is registered but NOT baseline-dispatched -- its global-GitHub-search input
shape doesn't fit this pipeline's "scan THIS target repo" model, and it needs a real GitHub
personal access token for practical use that this project has no credential-type concept
for yet (`target_credentials` is per-target-scoped, not a tool's own API key) -- a real,
scoped design question, not decided here (`STAGING-Pending-Discussions-and-Fixes.md`'s Round
9.2 has the recommendation).

---

## 2026-09-10 — Audit-fix pass: `FR-TOOL-15` hash truncation, `FR-TOOL-18` real queued trigger, `FR-DISCOVER-01` real wiring, `FR-BASELINE-07` real crt.sh CT-log check

**Status: ✅ IMPLEMENTED, ✅ APPROVED (operator's own "Check and Map Once Again" audit request
this same day surfaced these as real gaps, not "deliberately partial" as earlier summarized;
this entry documents the fixes made in the 2-hour follow-up window, and is itself an honest
account of what's still open — see the bottom of this entry).**

### `FR-TOOL-15` — `secret_sha256` truncation

Shipped as a full 64-char SHA-256 hex digest (`credential_manager.py`), not the literal
`sha256(...)[:12]` correlation hash `FR-TOOL-15`'s own text specifies. No code anywhere
actually queried `secret_sha256` for real deduplication (dedup is `UNIQUE(target_id,
identity_label)`, not hash-based) — the "full hash backs real dedup" framing in the original
schema comment was aspirational, not a real consumer. Fixed to `[:12]`, matching the literal
spec exactly; `auth_sessions.credential_ref` already used the same `[:12]` form.

### `FR-TOOL-18` — trigger was a direct call, not a queued task; baseline-only, not general

Originally: `orchestrator/baseline_recon.py::_record_tech_fingerprints` called
`check_tech_intel`/`record_tech_intel` directly, and was the ONLY place in the codebase that
ever wrote `discovered_entities.entity_type = 'tech_fingerprint'` — meaning a `whatweb`/
`httpx-toolkit`-shaped tech fingerprint surfaced by an ordinary Phase 4.2 Scripter-selected
tool run (not baseline's own pipeline) never triggered the EOL/CVE check at all, despite
`FR-TOOL-18`'s own wording ("whenever a new `tech_fingerprint` entity is written... including
by `FR-BASELINE-01`'s pipeline" — implying, not limited to it).

Now: `bridge/sanitize.py`'s generic parser (the one parser every Tier 1/Tier 2 tool's raw
output passes through, `PARSERS` being empty) recognizes the same httpx-toolkit-style
`{"tech":["Name:Version",...]}` JSON shape and populates a new `SanitizedRecord.
tech_fingerprints` field — tool-agnostic, not `httpx-toolkit`-name-gated. `bridge/
discovered_entities.py::record_entities` — the one shared call site every Tier 1/Tier 2
dispatch passes through (`bridge/pipeline.py::execute_and_record`) — writes the
`tech_fingerprint` entity and, on a genuinely NEW sighting, calls `bridge/tech_intel.py::
queue_and_run_tech_intel_check`, which inserts a real `task_queue` row (`origin =
'TECH_INTEL_ENRICHMENT'`, a new enum value) before running the check — matching the literal
"queue a follow-on Tier 2 task" wording with a real, auditable queue row, not just a
docstring claiming one exists. `tech_fingerprint_intel` gained a nullable `task_id` FK
linking back to that row.

**Still a deviation, disclosed, not fixed:** the queued task is executed inline,
synchronously, immediately after being created — not drained later by an async worker. This
pipeline has no task-queue-then-later-drain mechanism to plug into (same constraint the
original entry already named); the schema now at least carries a real audit trail
(`task_queue` row + `tech_fingerprint_intel.task_id`) that a future async drain loop could
pick up without another schema change.

`orchestrator/baseline_recon.py::_record_tech_fingerprints` still exists, now calling the
same `queue_and_run_tech_intel_check` — kept only because this module's own test harness
uses a pluggable fake `dispatch` that never touches `execute_and_record`/`record_entities`;
in a real run (`_real_dispatch`, the only path `vaptctl` ever takes) the general path above
already covers baseline's own Wave 2 `httpx-toolkit` output, making this a harmless,
`INSERT OR IGNORE`-deduped no-op re-check in production.

### `FR-DISCOVER-01` — `bridge/tool_discovery.py` had zero call sites (dead code)

Now reachable: `council/primary_scripter.py::run_primary_scripter_command`/`_retry` accept
an optional `domain: str | None` param; when given, `discover_tools(domain)` +
`format_discovery_block` append a "CANDIDATE TOOLS FOR THIS DOMAIN" block (installed vs.
known-not-installed, `FR-DISCOVER-02`) to the Scripter's prompt.

**Still a deviation, disclosed, not fixed:** no caller in the live Phase 4.2 loop
(`orchestrator/phase_lifecycle.py`) actually supplies a `domain` value yet — there is no
task-description-to-Kali-catalog-category classifier anywhere in this codebase, and building
one under this pass's time budget risked exactly the kind of fabricated, unverified behavior
this project already caught once (`s3scanner`'s first draft). The mechanism is real, wired,
and tested end-to-end; the trigger condition (an upstream domain hint) is operator/caller-
supplied, same honesty pattern as `FR-TOOL-15`/`17`'s credential architecture below.

### `FR-BASELINE-07` — `sublert`'s CT-log technique, not installed on this host

`sublert` is not installed (`shutil.which` fails) and its CLI shape is unverified against a
real `--help`/invocation. Rather than fabricate a schema for an unverified binary (again, the
`s3scanner` lesson), `monitor/monitor_engine.py` now queries crt.sh's public JSON API
directly (`enumerate_subdomains_via_crtsh`) — the same certificate-transparency log source
`sublert` itself watches — and merges real CT-log-discovered hostnames into `FR-MONITOR-01`'s
existing `SUBDOMAIN_SET` baseline/diff check. This is a genuine implementation of the
technique FR-BASELINE-07 describes ("continuous CT-log monitoring for new subdomains"), not
a renamed no-op; degrades to the pre-existing static-prefix-DNS-only behavior on any network
failure, per `FR-MONITOR-01`'s own "diff detection, not a hard gate" framing.

### `FR-BASELINE-06` — two more real, installed+verified tools added: `assetfinder`, `gospider`

While auditing the remaining roster gap, checked which of the still-named tools are actually
installed on this host (`command -v`): `amass`, `assetfinder`, `hakrawler`, `gospider` all
are. `assetfinder` (Wave 1, alongside `subfinder`) and `gospider` (Wave 3, alongside
`katana`/`gau`/`waybackurls`) were straightforward to verify against a real `--help` and wire
in cleanly — done. The other two were deliberately NOT wired, for real, specific reasons
(not just "not installed" this time):

- `amass`: this host's `/usr/bin/amass` is a wrapper shell script that unconditionally
  `sudo`s to download libpostal transliteration data on first run if it isn't already
  present (read the wrapper script directly to confirm this, not guessed). Under this
  pipeline's non-interactive subprocess model, that `sudo` fails immediately rather than
  hanging — but every invocation would then be a guaranteed no-op failure until an operator
  pre-provisions that data as root, outside this pipeline. Not wired until that's a
  documented setup step.
- `hakrawler`: verified its entire flag surface (`hakrawler -h`) — there is no `-u`/
  positional-target flag at all; its only input model is a URL piped via stdin.
  `bridge/executor.py::run_subprocess` has no stdin-pipe support today. Wiring it in as-is
  would run with no input and silently produce nothing, ever — worse than leaving it out.

### `FR-BASELINE-06` — multi-repo discovery (a pre-existing limitation, not part of the 2026-09-09 pull itself)

`_discovered_repo_url_from_summary` (now `_discovered_repo_urls_from_summary`) previously
returned only the FIRST github/gitlab/bitbucket URL found in Wave 3's crawl output — a
NETWORK target whose crawl surfaced several distinct repos only got the first one scanned.
Now scans for every distinct repo URL, deduped, and runs one follow-on trufflehog+gitleaks
wave per repo.

### `FR-TOOL-17` — real session establishment + invalidation-stops-propagation, built on the same 2-hour budget

Genuinely built, not deferred after all: `security/session_manager.py` (new) —
`establish_session()` marks an already-`register_credential()`-registered credential as the
active named session for a target (`auth_sessions`, `credential_ref` copied straight from
the backing credential's own `secret_sha256`, never recomputed); `invalidate_session()` marks
it invalid; `get_active_session()` reads the current one. At most one VALID session per target
is an application-level invariant (`auth_sessions` carries no `UNIQUE(target_id)` — a
re-establish supersedes the prior row rather than a schema constraint enforcing it).

The actual enforcement point is `credential_manager.py::get_env_for_target` — the single
FR-TOOL-15 propagation entry point every Tier 1/Tier 2 dispatch already calls — now refuses
(`{}`, its existing no-credential contract, never raises) once a credential's most recently
established session has been marked invalid. This is the concrete form "automatically
injecting that session's credentials... without re-authenticating per call" plus "MUST NOT
auto-retry login" take: no new call site needed, no retry logic exists to disable, and a
credential that was never wrapped in a session at all (the common FR-TOOL-15-only case) is
completely unaffected.

`vaptctl establish-session` / `vaptctl invalidate-session` (new, `cli/session.py`) are the
operator-facing entry points, mirroring `register-credential`'s own CLI pattern.

**Still a real deviation, disclosed, not fixed:**
- The "or an autonomous login-flow task succeeds" half of `FR-TOOL-17`'s text — genuinely
  separate, target-specific login-flow automation. A session's backing credential must
  already be registered (`register_credential`) before `establish_session` can mark it
  active; this module does not itself drive a login form or capture a fresh cookie.
- `OPS-NOTIFY` surfacing (`06:OPS-NOTIFY-01..05`) — a real, separate, cross-cutting subsystem
  (severity-tagged events, dashboard/console banners, an Error Code Dictionary, `vaptctl
  status`'s reason field) that doesn't exist anywhere in this codebase. Invalidation is now
  persisted for real and DOES stop propagation; nothing notifies anyone it happened.

### `FR-BASELINE-06` — multi-repo discovery (a pre-existing limitation, not part of the 2026-09-09 pull itself)

`_discovered_repo_url_from_summary` (now `_discovered_repo_urls_from_summary`) previously
returned only the FIRST github/gitlab/bitbucket URL found in Wave 3's crawl output — a
NETWORK target whose crawl surfaced several distinct repos only got the first one scanned.
Now scans for every distinct repo URL, deduped, and runs one follow-on trufflehog+gitleaks
wave per repo.

### What's still genuinely open after this pass (not fixed, not silently dropped)

- `FR-TOOL-17`'s two remaining pieces (see above): autonomous login-flow automation, and
  `OPS-NOTIFY` — both real, separate infrastructure work.
- `FR-BASELINE-06`'s remaining tool-roster gaps (GraphQL/JWT Wave 4 branches at 0%, most of
  Wave 1's "Always" OSINT/DNS-brute extras, Wave 3's crawler/WAF-probing extras) — see
  `orchestrator/baseline_recon.py`'s own module docstring for the current, honest list.
- `mobsf` — **UPDATE 2026-09-12: now confirmed fully working**, this line's prior
  "unbuildable/unverifiable" status is stale. Pulled the official Docker image
  (`opensecurity/mobile-security-framework-mobsf:latest`), ran it, and did real
  verification (not just a successful pull): Django migrations applied, superuser created,
  gunicorn bound to `0.0.0.0:8000`, `curl -L http://127.0.0.1:8000/` returns a genuine
  `<title>Sign In</title>` page (302→200), MobSF v4.5.2, REST API key issued. Zero
  mentions of `mobsf` were found anywhere in `implementation/` (not even a schema stub) —
  the prior attempt never got far enough to leave a trace, which is why this line existed
  with no further detail. Docker-image verification only — `mobsf` is still NOT yet
  schema-registered as a Tier 1 tool (`19:FR-MOBILE-08`'s design, approved in Round 7,
  remains unimplemented) or wired into any wave; this entry corrects the "can't even get
  it running" status, it does not close `FR-MOBILE-08` itself.

---

## 2026-09-10 — `FR-TOOL-15`/`FR-TOOL-17`: target-credential storage architecture, operator-supplied

**Status: ✅ IMPLEMENTED, ✅ APPROVED, unit/integration-tested (real AES-GCM round-trip,
real subprocess env-injection proven against `/proc/<pid>/environ` vs `/proc/<pid>/cmdline`,
real key-lifecycle tests). Not yet exercised in a live `vaptctl start`→`run` engagement.**

### What the requirement says

`01-Functional-Requirements.md`, `FR-TOOL-15`: "Configured target credentials propagate
automatically to every Tier 1/Tier 2 call via env vars; only a `sha256(...)[:12]`
correlation hash is logged, never the raw credential. Two distinct identities (low/high-
privilege) are registrable as separate named sets." `FR-TOOL-17` (session reuse) builds on
top of this same propagation mechanism. Neither requirement — nor `03:DR-SCHEMA-22`
(`auth_sessions`, `FR-TOOL-17`'s own schema entry) — specifies HOW a raw credential is
actually registered, stored at rest, or decrypted for reuse. `auth_sessions.credential_ref`
is explicitly documented as a one-way `sha256(...)[:12]` hash (`05:SEC-DATA-04`), which by
construction cannot be reversed to actually reuse a session — the corpus names the audit
requirement but never closes the loop on the real storage/decrypt mechanism a working
implementation needs.

### What the code actually does now

A concrete storage/propagation architecture, supplied directly by the operator (not
invented unilaterally by the build agent — an earlier implementation pass explicitly
deferred `FR-TOOL-15`/`17` for exactly this reason, see the prior entry this one replaces
the deferral of):

- **`vapt_agent/data/schema.sql`**: new `target_credentials` table — `encrypted_secret`
  (AES-256-GCM ciphertext, base64), `nonce` (base64), `secret_sha256` (`sha256(...)[:12]`,
  matching `FR-TOOL-15`'s literal wording exactly as of the 2026-09-10 audit-fix pass below
  — never reversible; originally shipped as a full 64-char digest, corrected the same day),
  `scope_domain_regex` (defaults to the
  target's own identifier), `identity_label` (`FR-TOOL-15`'s "separate named sets"),
  `UNIQUE(target_id, identity_label)`. `auth_sessions` gained a nullable `credential_id`
  FK, linking a session to the real encrypted secret backing it — `credential_ref` itself
  is untouched, still exactly the one-way hash `SEC-DATA-04` requires.
- **`vapt_agent/security/engagement_key.py`**: a fresh 256-bit key (`os.urandom(32)`) is
  generated once per engagement, at `vaptctl start` (`cli/start.py`), written ONLY to
  `/dev/shm/vapt_agent/<engagement_id>.key` (tmpfs, RAM-backed) with `0600`/`0700`
  permissions — never to `state.db` or any NVMe-backed path. Discarded at `vaptctl abort`
  (`security/kill_switch.py::abort_engagement`) — "expire cleanly": the encrypted rows
  themselves are untouched, just unusable without a fresh key.
- **`vapt_agent/security/credential_manager.py`**: `register_credential()` (encrypts,
  validates the target belongs to the stated engagement, defaults
  `scope_domain_regex` from the target's own identity) and `get_env_for_target()` (decrypts
  strictly in-memory, maps `credential_type` → env var names — `TARGET_PASSWORD`/
  `TARGET_USERNAME`, `TARGET_AUTH_TOKEN`/`TARGET_AUTH_HEADER`, `TARGET_COOKIE_HEADER`,
  `TARGET_API_KEY`, `TARGET_SSH_KEY`, `TARGET_CERTIFICATE`).
- **`vapt_agent/bridge/executor.py::run_subprocess`** gained an `extra_env` parameter,
  merged on top of a full copy of the process's own environment (never a bare replacement,
  which would strip `PATH`) — never placed in `argv`, so it never appears in
  `/proc/<pid>/cmdline`/`ps aux` (verified directly against a real process's own
  `/proc/<pid>/cmdline` vs `/proc/<pid>/environ` in a real test, not just code inspection).
- **`vapt_agent/bridge/pipeline.py::execute_and_record`** — the ONE function both Tier 1's
  wrapper and Tier 2's bridge route every dispatch through — now calls
  `get_env_for_target()` and passes the result as `extra_env`, satisfying `FR-TOOL-15`'s
  literal "every Tier 1/Tier 2 call" wording from a single injection point. Returns `{}`
  or the overwhelmingly common case of no credential registered for a target — a genuine
  no-op, not a new failure mode.
- New dependency: `cryptography>=42.0` (added to `pyproject.toml`) — AES-GCM has no
  reasonable hand-rolled implementation; this is the standard, actively-maintained,
  OpenSSL-backed choice.

### Why

The operator supplied this architecture directly (2026-09-10) specifically to unblock
`FR-TOOL-15`/`17`, which a prior implementation pass had deliberately left unimplemented
after concluding the requirements corpus itself doesn't specify a storage mechanism and
that inventing one unilaterally for live, possibly high-privilege target credentials was
too large a security-architecture call to make without explicit sign-off. This entry
records that sign-off and the resulting implementation, per this file's own stated purpose
("a decision already made in code, recorded here so the spec can catch up to it
deliberately").

### What would need to change in `01`/`03`/`05` to reconcile this

- `01:FR-TOOL-15` would need a concrete storage-mechanism clause (AES-256-GCM at rest,
  ephemeral per-engagement key, tmpfs-only key storage) instead of only describing the
  propagation/logging behavior.
- `03-Data-and-Storage-Requirements.md` would need a new `DR-SCHEMA` entry for
  `target_credentials`, and `DR-SCHEMA-22`'s `auth_sessions` text should note the new
  `credential_id` linkage column.
- `05-Security-Safety-and-Compliance-Requirements.md`'s `SEC-DATA-04` could be extended to
  name the ephemeral-key architecture explicitly as the mechanism satisfying "local-only,
  never the raw secret in any log or database row."

---

## 2026-09-09 — `FR-GATE-10`: MemAvailable gate widened from 5s to 20s

**Status: ✅ IMPLEMENTED, ✅ APPROVED, live-tested.**

### What the requirement says

`01-Functional-Requirements.md`, `FR-GATE-10`: "poll `/proc/meminfo` `MemAvailable`... **Bounded to 5s**; raise a degraded-swap alert on timeout rather than spawn into a tight memory state."

### What the code actually does now

`vapt_agent/engine/mem_gate.py`'s `MemAvailableGate` defaults `poll_timeout_s` to `20.0`, not `5.0`.

### Why

Direct, real evidence from four consecutive live `vaptctl run` attempts against the actual
Implementing PC host (16 GiB total RAM), each immediately after the new "Graceful Userland
Application Teardown" mechanism (see the 2026-09-08 entry below) had genuinely closed every
targeted app: `MemAvailable` fluctuated within ~20-40 kB of the ~10.1 GiB Strategist-model
threshold from one attempt to the next — sometimes above it, sometimes below, purely on
timing (ordinary page-cache churn during the new `vaptctl run` process's own Python
interpreter startup). This is not a case of the model genuinely not fitting, nor of the
kernel taking a long time to reclaim memory (a 20-second sampled trace of `MemAvailable`
immediately after app-teardown showed a stable reading, not a slow climb) — it's a case of a
5-second window giving the poll loop (already sampling every 0.1s) too few chances to land on
a favorable reading in a state that's already true most of the time. Widening the window
doesn't change what "cleared the threshold" means or weaken the safety check itself, only how
many chances it gets to observe a true state.

**Operator approval:** given explicitly, 2026-09-09, after being shown the exact fluctuation
evidence above and the FR-GATE-10 conflict directly.

---

## 2026-09-08 — Phase 1 Hibernation: Denylist → Allowlist Architecture

**Status: ✅ IMPLEMENTED on the Implementing PC, ✅ APPROVED by the operator. NOT YET
reconciled into `01-Functional-Requirements.md`'s own text** — that edit belongs to
whoever next does a requirements-sync pass on this repo, informed by this entry.

### What the requirement says

`01-Functional-Requirements.md`, `FR-ENV-03`:

> Enumerate active GUI processes; classify each "hibernation-eligible" or "protected"
> against a **fixed denylist** (`systemd`, `dbus`, compositor, session manager, audio
> server) before any signal.

A denylist means: every process is hibernation-eligible **by default**, EXCEPT the ones on
a maintained list of known-dangerous names.

### What the code actually does now

`vapt_agent/orchestrator/hibernation.py`'s `classify_processes()` (implementation PC) now
requires a process to be **explicitly allowlisted by app identity** before it's eligible at
all — everything else survives by default. A pid must satisfy ALL of:

1. Its `comm` (or the `comm` of an ancestor whose full descendant-process tree it belongs
   to) matches `HIBERNATION_ELIGIBLE_APP_NAMES` — currently browsers (Chrome, Chromium,
   Brave, Firefox, Firefox ESR, Tor Browser) plus Thunar and Mousepad, per the operator's
   own stated policy for what hibernation exists to reclaim RAM from.
2. It's **also** not on the ORIGINAL fixed denylist (`PROTECTED_PROCESS_NAMES` — every
   category built up across this project's three real forced-hardware-shutdown incidents:
   kernel threads, GUI terminal/tmux windows, USB/Bluetooth hotplug daemons) — kept as a
   second, independent gate for defense in depth, not removed.
3. It's not caught by any of the other orthogonal, identity-independent protections this
   module already had: `controlling_session_pids()`, `tmux_session_pids()`,
   `container_managed_pids()`, `pids_holding_file_locks()`, and a new one added alongside
   this change, `in_flight_tool_pids()` (see below).

This is a structural inversion of FR-ENV-03's literal mechanism, not an extension of it.

### Why this deviation was made

A code-review pass on 2026-09-08 (`/code-review max` against the real `implementation/`
codebase) found 15 correctness bugs in this exact hibernation/restoration code path, on top
of three real, already-fixed forced-hardware-shutdown incidents earlier in the same
project:

1. Kernel threads getting `SIGSTOP`'d (2026-09-05) — froze the host solid, hardware
   power-button shutdown required.
2. GUI terminal/tmux windows getting `SIGSTOP`'d within about a second of the dashboard/
   console auto-launching (2026-09-07/08) — same failure mode.
3. USB/Bluetooth hotplug-mediating daemons getting `SIGSTOP`'d, hanging the kernel's own
   USB subsystem (2026-09-08) — same failure mode again, a third distinct category.

Each was fixed reactively by expanding the denylist after the fact. The pattern across all
three, plus the 15 further bugs the code-review pass found in the SAME mechanism, is
structural: **a denylist can only ever be as complete as the incidents that have already
happened to it.** "Protect anything not already known-dangerous" is the wrong default for
an action this destructive (an unrecoverable-without-physical-access host freeze, three
times over) on a host whose exact process inventory (VAPT tooling, browser-automation
libraries, arbitrary tool subprocesses) is not fully enumerable in advance.

An allowlist inverts the risk: hibernation now only ever touches a process whose identity
is explicitly, deliberately marked safe to freeze. Everything else — including any category
nobody has thought of yet, the exact blind spot that caused all three incidents — survives
automatically. The cost is narrower coverage (only browsers/Thunar/Mousepad get frozen,
not "everything except a growing list"), which the operator's own stated policy this
session already scoped hibernation to in practice: *"Most of the Times, the Extra Apps
include Browsers (Chrome, Firefox, Tor, Brave), Thunar (File Manager), Mousepad (Text
Editor)."*

**Operator approval:** given explicitly, 2026-09-08 — *"Architecture Level Change is
approved"* — in the same message that accepted the two other code-review recommendations
below.

### A new gap this change would have introduced, and how it's closed

Allowlisting by app identity alone has a real edge case this project's own host exposes:
headless-browser-automation tooling (`playwright`, `pyppeteer`, `ferrum` — all installed on
the Implementing PC) spawns a real subprocess literally named `chrome`/`chromium`/`brave`
when a VAPT task uses it for JS-rendering/browser-automation recon. Under the new allowlist,
that in-flight tool subprocess would match `HIBERNATION_ELIGIBLE_APP_NAMES` by name — and
per `CLAUDE.md`'s own coding rule, every tool subprocess is spawned with
`preexec_fn=os.setsid` (its own new POSIX session, deliberately separate from the
orchestrator's), so `controlling_session_pids()` alone does not protect it. Freezing the
pipeline's own active work mid-task would be worse than the incident this change fixes.

Closed by a new function, `in_flight_tool_pids()` (`orchestrator/hibernation.py`), which
protects every pid (`tool_execution_logs.end_ts IS NULL` for the current engagement, joined
through `task_queue`/`targets` — the same join `security/kill_switch.py`'s `abort_engagement`
already uses) plus its full descendant-process closure. Not itself a requirement conflict
(nothing in `01`/`05` currently addresses tool-subprocess hibernation-safety one way or the
other) — recorded here only because it's a direct structural consequence of the deviation
above, not a standalone decision.

### What would need to change in `01-Functional-Requirements.md` to reconcile this

- `FR-ENV-03`'s own wording ("classify... against a fixed denylist") would need to become
  an allowlist description, naming `HIBERNATION_ELIGIBLE_APP_NAMES`'s actual scope
  (browsers, Thunar, Mousepad) as the eligibility criterion, with the current denylist
  categories re-described as a secondary, defense-in-depth filter rather than the primary
  mechanism.
- A new requirement covering `in_flight_tool_pids()`'s protection of in-flight tool
  subprocesses would be a reasonable, currently-missing addition to the `FR-ENV` cluster.

---

## 2026-09-08 — `thaw_all()`/`verify_suspended_alive()`: pid-recycling safety (additive, not a conflict)

**Status: ✅ IMPLEMENTED, ✅ APPROVED.** Not a requirement deviation in the same sense as the
entry above — recorded here for completeness since it landed in the same operator-approval
message, and it does touch `03-Data-and-Storage-Requirements.md`'s `suspended_processes`
shape (a new `start_time_ticks` column, additive/nullable, no existing requirement text
contradicted).

**Gap fixed:** `thaw_all()`/`verify_suspended_alive()` previously identified "the process I
suspended" purely by numeric pid, with no start-time/identity check. FR-ENV-12 already
requires detecting an OOM-killed suspended process ("mark the outcome partial/degraded"),
but if that pid was later reused by the kernel for a completely unrelated process before
Phase 5 restoration ran, the old code would `SIGCONT` the wrong process and record it as a
successful resume — the original target stays gone, silently.

**Fix:** `/proc/<pid>/stat` field 22 (`starttime`, verified directly against a real running
process on this host before trusting it) is recorded in `suspended_processes.start_time_ticks`
at suspend time and compared against the live process's own starttime at thaw/verify time. A
mismatch is now treated identically to "pid is gone" (FR-ENV-12's existing degraded-outcome
path), not as a successful resume. `NULL` for rows written before this column existed, which
correctly falls back to the pre-existing liveness-only check for those.

This is additive to `03`'s `suspended_processes` table shape (nullable column, no existing
row format broken) and doesn't contradict any requirement's literal text — included here
only because the operator's approval covered it in the same breath as the architecture
change above.

---

## How to add new entries

New entries go **above the existing ones**, newest on top, same convention as
`STAGING-Pending-Discussions-and-Fixes.md`. Only record something here once it is BOTH
implemented in `../implementation/` AND operator-approved — this file is a record of
settled divergence, not a place to propose one.
