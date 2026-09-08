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
