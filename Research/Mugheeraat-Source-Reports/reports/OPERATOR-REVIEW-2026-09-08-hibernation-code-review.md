# Operator Review Needed — 2026-09-08 hibernation code review

> **UPDATE (2026-09-08, later same day): RESOLVED.** The operator approved both
> "Needs your decision" items below AND the architecture-level allowlist redesign
> ("Both Recommendations are accepted and Architecture Level Change is approved").
> All three are now implemented and verified (full real test suite + `ruff`/`mypy`
> clean). Full detail:
> - Pid-recycling fix (Recommendation #1): `start_time_ticks` column added to
>   `suspended_processes` (schema migration in `vapt_agent/data/db.py`); `thaw_all()`/
>   `verify_suspended_alive()` now detect a recycled pid and treat it as `missing`,
>   never `SIGCONT`ing the wrong process.
> - Docker-timeout fix (Recommendation #2): `container_managed_pids()` now retries
>   once on a transient timeout before giving up; largely superseded in importance by
>   the architecture change below (container processes were never allowlist-eligible
>   to begin with).
> - Architecture change: `orchestrator/hibernation.py` moved from a denylist
>   (`PROTECTED_PROCESS_NAMES`, "eligible unless known-dangerous") to an allowlist
>   (`HIBERNATION_ELIGIBLE_APP_NAMES`, "protected unless explicitly marked safe to
>   freeze" — browsers, Thunar, Mousepad only). The old denylist is retained as a
>   second, independent defense-in-depth filter, not removed. Full rationale and the
>   operator's explicit approval are recorded in `source/IMPLEMENTATION-DEVIATIONS-
>   FROM-REQUIREMENTS.md` (this is a deliberate deviation from `01-Functional-
>   Requirements.md`'s `FR-ENV-03` literal "fixed denylist" wording — not yet
>   reconciled into that document's own text, tracked there for the next
>   requirements-sync pass). A new `in_flight_tool_pids()` protection was added
>   alongside this change to cover a gap it would otherwise have introduced
>   (headless-browser-automation tool subprocesses, installed on this host, being
>   named "chrome"/"chromium"/"brave").

Context: `/code-review max` was run against this codebase (the whole
`implementation/` tree) while the operator was unavailable for ~10 hours.
It returned 15 correctness findings, all in the Phase 1 hibernation /
Phase 5 restoration code path — the same code that has already caused
three real forced-hardware-shutdown incidents this project. Per the
operator's own standing instruction ("fix all obvious issues, document the
rest where you need me"), every finding was triaged:

- **12 of 15 findings were fixed directly** (mechanical bugs, or fixes that
  mirror an existing pattern already established elsewhere in this
  codebase — no real design ambiguity in what "correct" looks like). See
  the "Fixed directly" section below for the full list, in case any of
  them turn out to need a second look.
- **2 findings need an operator decision** — real bugs, but the "correct"
  fix involves a genuine judgment call (a schema change, or a fail-open
  vs. fail-closed safety-policy choice) that shouldn't be made
  unilaterally. See "Needs your decision" below.
- **1 open architectural concern**, already flagged in a prior session's
  memory note, surfaced again here because this review is more evidence
  that it's real.

All fixes were verified with the full real test suite (`pytest`, real
`/proc` reads and real subprocesses throughout — nothing mocked away) plus
`ruff`/`mypy`, per the "no more live `vaptctl start`/`run` test runs, do
audits/dry-runs/sandbox tests instead" constraint still in force. **No
live engagement was run.**

---

## Needs your decision

### 1. `thaw_all()` can SIGCONT the wrong process after a pid gets recycled

**File:** `vapt_agent/orchestrator/hibernation.py`, `thaw_all()` (and
`suspended_processes` schema, `vapt_agent/data/schema.sql`).

**The bug:** a suspended pid is identified purely by its numeric value —
no start-time or identity check. If a suspended process is OOM-killed
while still stopped (exactly the scenario FR-ENV-12/`verify_suspended_
alive` exists to catch, but which isn't called anywhere in production —
see below) and the kernel later reuses that same pid for an unrelated new
process before `thaw_all()` runs, `thaw_all()` will SIGCONT the wrong
process and record it as successfully resumed. The real target is gone
for good and nobody is told.

**Why this needs your call, not just a fix:** the correct fix is to record
each process's `/proc/<pid>/stat` start-time field (field 22, after the
`)`) at suspend time, and compare it against the live process's start-time
at thaw time — a mismatch means "different process now owns this pid,"
which `thaw_all()` should then treat exactly like a "gone" pid (append to
`missing`, not `resumed`). That's a **schema change**
(`suspended_processes` needs a new column, e.g. `start_time_ticks`) plus a
migration. This project's migration history (see `data/db.py`'s
`_REBUILD_COLUMN_OVERRIDES` mechanism) has had real chicken-and-egg
CHECK-constraint bugs before — not something to take on unsupervised
during a 10-hour absence window on the exact file that's already caused
three hardware freezes this session.

**Recommendation:** worth doing — this is a real, if lower-probability,
correctness gap (mislabels a resume, doesn't cause a NEW freeze the way
the other 12 fixed findings could have). Say the word and I'll do the
schema migration + `hibernation.py` change with the same audit/dry-run
rigor as everything else in this file.

---

### 2. `container_managed_pids()` treats a Docker query timeout as "safe"

**File:** `vapt_agent/orchestrator/hibernation.py`, `container_managed_pids()`.

**The bug:** if `docker ps`/`docker top` times out (10s) or otherwise
fails, the function returns an empty set — the same value it returns when
Docker genuinely isn't installed. The function's own docstring justifies
that by saying "a host with no Docker at all is exactly as safe either
way" — true when Docker really isn't there, **false** when Docker IS
running the engagement's own test-lab targets (Juice Shop, MediaCMS) and
just failed to answer in time, plausible under the exact memory pressure
hibernation exists to relieve. In that case, `suspend_processes()` would
freeze the very containers being assessed — the specific outcome this
function's own 2026-09-07 incident note says it was built to prevent.

**Why this needs your call:** fixing the *symptom* is easy (retry once,
raise the timeout). Fixing the actual fail-open behavior means picking a
policy: should a Docker query failure make hibernation degrade/abort
entirely (fail closed — safer for the containers, but now one flaky
`docker top` call can block all of Phase 1 hibernation), or should it fall
back to name-based matching for known container process names (partial
mitigation, still has gaps), or something else? That's a real
safety-vs-availability tradeoff, not a bug with one obvious right answer.

**Recommendation:** given tonight's plan is to re-run against Juice Shop
**with hibernation disabled** (per your own choice earlier), this
specific bug can't bite during that run. Worth deciding before hibernation
is ever re-enabled against the test lab again.

---

## Open architectural concern (carried over, restated because this review is more evidence for it)

**The whole protected-process approach is a denylist** (freeze everything
except a growing list of known-dangerous names). This is now the
**fourth** review pass to find a new category of "must never be
hibernated" reactively — three real incidents (kernel threads, GUI/tmux
windows, USB/hotplug daemons) plus tonight's 15 more correctness bugs in
the mechanism itself. A denylist can't be proven complete against a host
it hasn't already broken on. The safer architecture (not yet decided) is
an **allowlist** instead — freeze only processes matching a small, curated
set of known-safe apps (browsers, Thunar, Mousepad — your own stated
list). Full detail in memory: `vapt_usb_hotplug_daemon_freeze_incident`.
Not re-litigating it here, just flagging that tonight's findings are
another data point in favor of raising it.

---

## Fixed directly (verified: full real test suite + ruff + mypy clean)

All in `vapt_agent/orchestrator/hibernation.py` unless noted.

1. **`thaw_all()` ignored the thaw helper's return code**, verifying
   success only via "is it alive and not a zombie" — which is equally true
   of a process still stuck in the stopped state. Added `_pid_thawed()`
   (checks the process actually left states `T`/`t`, not just `Z`) and now
   requires the helper's own exit code to be 0 too.
2. **`tmux_session_pids()`'s exception handling could abandon untried
   session names** on a transient timeout (conflated with "tmux not
   installed" at all) — the exact class of gap that caused the 2026-09-07/
   08 GUI-terminal-window incident. Now: `FileNotFoundError` (no tmux
   binary) still bails out entirely; a transient timeout/`OSError` on one
   session name now moves on to the next name instead of abandoning the
   scan. `list-panes`/`list-clients` calls, which previously had no
   exception handling at all, are now guarded too.
3. **`_sudo_available` was cached `False` forever after one transient
   probe failure**, permanently downgrading every later freeze/thaw/
   reclaim call for the rest of the engagement to an unprivileged (and
   guaranteed-to-fail) invocation. Now only a *successful* probe is cached
   permanently; a failure is retried on the next call.
4. **`thaw_all()` had no pid-identity check** — documented above as a
   judgment call for the schema-migration half; the *return-code* half of
   this same function is fixed (item 1).
5. **`_proc_stat_fields`/`_pid_alive_and_not_zombie` didn't catch
   `PermissionError`**, unlike sibling `/proc` readers in the same file. A
   `hidepid=1/2`-mounted `/proc` would crash `controlling_session_pids()`
   (called unguarded at the very start of `suspend_processes`) or abort
   `thaw_all()`'s restoration loop partway through, stranding the
   remaining pids frozen. Both now catch `PermissionError` and fail to a
   safe/conservative answer.
6. **`_run_helper`/`_sudo_n_works` had no `subprocess.run` timeout at
   all**, unlike every other subprocess call in this module — a hung
   helper call (plausible under the RAM pressure hibernation exists to
   relieve) would block a per-pid loop forever. Both now bounded (10s/30s)
   with `TimeoutExpired`/`OSError` converted to an ordinary failed
   `CompletedProcess`, matching every caller's existing contract.
7. **`run_full_engagement()` (`orchestrator/driver.py`) had no
   `try/finally` around Phase 4**, unlike `security/kill_switch.py`'s
   `abort_engagement()`, which explicitly wraps its own `thaw_all()` call
   for exactly this reason. Any exception in Phase 4.1-4.3 (real LLM calls,
   real tool subprocesses) used to skip `thaw_all()` entirely, permanently
   stranding every SIGSTOP'd process. Now wrapped in `try/finally`.
8. **`run_full_engagement()` never surfaced `hibernation_result.degraded`/
   `restoration_result.degraded`** — an engagement where hibernation
   silently failed to freeze anything proceeded exactly as if it had
   succeeded. `cli/run.py` now prints an explicit `WARNING:` line for
   either case (no control-flow change — see "Needs your decision" #2 for
   the harder question of whether degraded hibernation should ever block
   an engagement).
9. **`hibernation_preview.py --engagement-id` defaulted to `None`** instead
   of auto-resolving the active engagement the way every other CLI command
   (`abort`, `console`) does — so running the documented safety command
   (`vaptctl hibernation-preview`, no flags) right after `vaptctl start`/
   `run` showed the dashboard/console tmux panes and GUI windows as "WOULD
   BE FROZEN," even though a real run would always protect them. Now
   auto-resolves via `get_active_engagement_id`, same as `abort.py`.
10. **`enumerate_processes()`'s `comm` read had no `UnicodeDecodeError`
    handling**, unlike the `cmdline` read three lines below it. A process
    with a non-UTF-8 name (settable via `prctl(PR_SET_NAME)`) would crash
    enumeration for the *entire host*, failing Phase 1 outright. Now reads
    as bytes + `errors="replace"`, matching the `cmdline` handling.
11. **`compute_n_exp("Reporter")` (`dashboard/compute.py`) checked for a
    `'5_HIBERNATE'` phase-log row that no production code ever wrote** —
    confirmed via grep, only a test that manually inserted a fabricated row
    ever exercised the "done" branch. The Reporter completion indicator
    could never reach "done" for a real engagement. Added `phase_lifecycle.
    log_phase_5_hibernate()`, now called from `driver.py`'s `finally` block
    unconditionally (with or without hibernation enabled).
12. **`read_cumulative_pages_swapped_out()` had no exception handling**,
    and `cli/dashboard.py` called it live and unguarded both at startup and
    every refresh tick. An unreadable/malformed `/proc/vmstat` would crash
    the whole live monitoring dashboard. Both call sites in `dashboard.py`
    now degrade to a "0 GiB, not abnormal" reading on failure instead of
    crashing.

**Also fixed, flagged by the review as notable but not in its main 15:**

13. **`hibernation_preview.py` never called the file-lock check**
    (`pids_holding_file_locks`, renamed from `_pids_holding_file_locks` so
    the preview command can call it too), so a lock-held process (e.g. a
    database mid-transaction) could show up under "WOULD BE FROZEN" when a
    real run would route it to `skipped_locked` and never touch it. Preview
    output now has a separate "Skipped — file-locked" count and excludes
    those pids from "WOULD BE FROZEN."
14. **The `vapt-<id>`/`-dashboard-view`/`-console-view` tmux session-naming
    convention was independently duplicated in three places**
    (`hibernation.py`, `cli/hibernation_preview.py`, `cli/run.py`) with no
    shared helper — flagged as a silent-drift risk. Extracted to
    `hibernation.engagement_tmux_session_names()`, used by all three now.
15. **A regression test in `tests/test_cli_hibernation_preview.py` meant to
    guard "PID 1 never shown as frozen" could never actually fail**,
    regardless of whether that invariant held — its assertion string had
    the wrong amount of leading whitespace to ever match the command's real
    output format. Fixed to match the real format string (verified by
    reproducing it directly).

**Minor, unrelated to the review, noticed in passing:** `dashboard/
compute.py`'s `_PHASE_ORDER` tuple lists a bare `"4.2"` phase, but
`phase_lifecycle.py` only ever logs `"4.2A"`/`"4.2B"` — `_PHASE_ORDER`
itself isn't read anywhere else in the codebase (dead reference), so this
didn't cause a bug, but it's worth cleaning up or removing next time that
file is touched.

---

## Next steps in progress (per your instructions, still autonomous)

Unit/module/integration/sandbox tests (safe to abort/restart) are being
run as part of verifying the above. After that: a re-run against the Juice
Shop / test-lab Docker containers with hibernation **disabled**
(`--no-hibernation`, per your explicit choice), collecting logs/stats/
metrics — still no live hibernation-enabled run, per the standing "no more
test runs before your call" instruction.
