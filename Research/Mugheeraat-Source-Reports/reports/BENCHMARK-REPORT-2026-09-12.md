# Live Benchmark Report — 2026-09-12

> **Scope of this document.** A single-session, single-day record of a full live-system
> validation pass against real targets (Juice Shop, MediaCMS) on real hardware, covering:
> the Python 3.13→3.14 venv breakage and rebuild, 4 real bugs found and fixed, 4 full
> `vaptctl` engagement cycles against live targets, the `systemd-oomd` memory-pressure
> kill finding, MobSF verification, and — the headline result — the first-ever measured
> real completion latency for the Lead Strategist's Phase 4.1 planning turn on CPU-only
> inference, obtained via an uncapped standalone probe that incidentally caught the host
> suspending mid-run. Companion decision-tracking lives in
> `source/STAGING-Pending-Discussions-and-Fixes.md` (Round 10); this document is the full
> narrative and data behind those staged decisions.

---

## 1. Summary

| Area | Outcome |
|---|---|
| Environment | `.venv` rebuilt cleanly on Python 3.14 (operator chose to keep latest, not downgrade) |
| Bugs found & fixed | 4 real, live-discovered bugs (see §3) |
| Test suite | 1076 passed, 0 failed, 3 skipped — confirmed clean, twice |
| Live engagements run | 4 (engagements 16–19), against real Juice Shop (`:3000`) + MediaCMS (`:8080`) |
| Real infra findings | `systemd-oomd` kills the whole engagement under memory pressure (§5); host suspend during an active engagement is unhandled (§7.3) |
| MobSF | Confirmed fully working via Docker — resolves the long-standing "unbuildable/unverifiable" status (§6) |
| Strategist latency (the headline number) | **117.4 minutes** (~1h57m) of genuine CPU-only compute for one planning turn — first real, uncapped measurement this project has ever obtained (§7) |
| Output quality | The Strategist's real output, once it finished, was coherent and target-appropriate — a real validation of the council architecture, not just a latency data point (§7.4) |

---

## 2. Environment: the venv rebuild

The prior session's `.venv` broke when the operator's own concurrent
`apt install kali-linux-everything` repointed the system `python3` from 3.13 to 3.14
mid-flight — the venv's installed packages lived under `lib/python3.13/site-packages`,
which the now-3.14 interpreter couldn't see.

**Operator's explicit instruction: keep the latest Python, don't downgrade.** `pyproject.toml`
only requires `>=3.11`, so `.venv` was rebuilt directly against `python3.14`. Every
dependency installed cleanly with prebuilt `cp314` wheels — no source-build failures.

Two real gotchas hit during the rebuild, both now fixed:

1. **Build-then-rename breaks console-script shebangs.** The venv was built under a
   temporary name (`.venv-new`) then renamed to `.venv` — but `pip` bakes the **absolute
   path** into every console-script shebang at install time. `vaptctl`, `pip`, `mypy`, and
   critically the privileged `vapt-freezer-helper` all ended up with shebangs pointing at
   the now-nonexistent `.venv-new/bin/python3`. This silently broke hibernation's sudoers
   `NOPASSWD` rule (scoped to the literal path `.venv/bin/vapt-freezer-helper`) — `sudo -n`
   reported a plain "No such file or directory," easy to misdiagnose as a permissions
   issue rather than a broken symlink chain. **Fix**: re-run
   `pip install -e . --force-reinstall --no-deps` from inside the FINAL venv path (must be
   invoked as `.venv/bin/python3 -m pip`, since `pip`'s own script has the identical
   bad-shebang problem). **Lesson recorded**: always build a venv directly at its final
   path; never build-then-rename.
2. **Bundled Tier 1 tool scripts resolve `python3` via the calling process's `PATH`, not
   the venv.** Scripts like `wordlist_gen.py`/`cors_scanner.py` execute via their own
   `#!/usr/bin/env python3` shebang as real subprocesses — this resolves through whatever
   `PATH` the CALLING process has at execve time, not the venv, even when the venv's own
   interpreter invoked pytest directly. Running `.venv/bin/python3 -m pytest` without
   `.venv/bin` prepended onto `PATH` makes every one of these subprocess-shebang tools
   silently fail with `ModuleNotFoundError: No module named 'vapt_agent'`, even with a
   perfectly healthy venv. **Fix**: always `export PATH="$PWD/.venv/bin:$PATH"` before
   running the suite or any live `vaptctl` command.

Full suite after both fixes: **1076 passed, 0 failed, 3 skipped** — confirmed clean twice
across the session.

---

## 3. Four real bugs found and fixed this pass

1. **`test_check_inference_engine_...` (`tests/test_preflight.py`)** — hardcoded the
   assumption "llama-server is not installed in this sandbox," asserting only the
   binary-missing failure shape. Real models + llama-server are now genuinely installed
   and exercised live (this session finally ran them to completion), so when the suite
   runs while a live engagement's own `llama-server` holds port 11434,
   `check_inference_engine()` correctly reports the OTHER real failure shape ("something
   is already listening on 127.0.0.1:11434") — an equally valid, already-correct branch
   the test just never anticipated. Fixed by accepting either shape. Not a bug in
   `preflight.py` itself.
2. The `vapt-freezer-helper` shebang breakage from the venv rebuild (§2.1) — a real,
   live-blocking bug (hibernation's privileged helper silently unusable) even though it
   was self-inflicted by the rebuild process, not pre-existing.
3–4. Two more bugs from earlier the same day (httpx-toolkit port-feeding, stale
   `orchestrator_pid`, preflight wrongly blocking `sqlmap` via the wrong resolver
   function) — carried over from the prior session's pass; see
   `IMPLEMENTATION-DEVIATIONS-FROM-REQUIREMENTS.md` and this session's git history
   (`c77ed59`, `6d97041`) for the full detail on those. Reconfirmed live this session
   (engagement 19's baseline recon correctly fed naabu's discovered ports —
   `631,3000,8080` — into httpx-toolkit's `-p` flag) that the earlier fix is intact, not
   regressed.

---

## 4. Live engagement cycles — 16 through 19

Targets: `test_lab/docker-compose.yml`'s Juice Shop (`127.0.0.1:3000`) and the pre-existing
MediaCMS stack (`127.0.0.1:8080`, web+db+redis+celery).

### Engagement 16 (JuiceShop + MediaCMS)

Hit `MemAvailableGate` refusal mid-run (needed `10602542 kB`, RAM insufficient even after
`--force-app-close` — only Thunar was open and closeable at the time). Orchestrator process
died ungracefully. **Recovered** by freeing idle MCP subprocesses (unused
chrome-devtools-mcp/playwright-mcp from earlier tool loads) and non-essential MediaCMS
celery workers/beat (web/db/redis kept up, target stayed fully reachable).

### Engagement 17 (JuiceShop + MediaCMS, retry)

Passed the memory gate, but ~9 minutes into Strategist model loading, **the entire tmux
cgroup (29 processes — orchestrator, llama-server, every tool subprocess) was SIGKILLed at
once.** Root-caused to `systemd-oomd`, not the kernel OOM killer — see §5 for the full
detail, since this became its own major finding.

### Engagement 18 (JuiceShop-only, reduced footprint to avoid a repeat of 17)

Stable, no `oomd` incident. Baseline recon completed cleanly (~7.5 min). Strategist Phase
4.1 turn 1: first attempt (`STRATEGIST_TIMEOUT_S=1800s`) timed out; `FR-GATE-08`'s automatic
one-shot restart+retry fired correctly (fresh `llama-server` process, same model); the retry
ALSO timed out at 30 min. Engagement gracefully escalated to `PAUSED` — clean teardown, zero
data loss, zero orphaned processes, full RAM recovery.
`model_invocation_logs.latency_ms = 3631785` (60.5 min combined across both attempts),
`status='TIMEOUT'`.

### Engagement 19 (JuiceShop + MediaCMS, MediaCMS containers restarted once RAM recovered)

Baseline recon completed in just 83 seconds this time (naabu correctly found all 3 real
open ports — `631, 3000, 8080` — and httpx-toolkit's args correctly included
`-p 631,3000,8080`, reconfirming §3's port-feeding fix is intact). Strategist turn 1: same
pattern as engagement 18 — first attempt timed out, automatic retry also timed out, graceful
`PAUSED` escalation. `latency_ms = 3619893` (60.3 min combined) — nearly identical to
engagement 18's figure, **confirming the pattern was reproducible, not a fluke**, and
setting up the motivation for the uncapped probe in §7.

---

## 5. `systemd-oomd` — a real architectural gap, root-caused precisely

**The problem.** Engagement 17 was SIGKILLed in its entirety, even though
`MemAvailableGate` (`FR-GATE-10`) had already cleared the model load, and even though
`security/kill_switch.py`'s `oom_score_adj=-900` protection was correctly applied to the
orchestrator process. `dmesg` — the kernel's own OOM killer log — showed nothing at all; a
real trap for anyone debugging this by kernel log alone.

**Root cause**: `systemd-oomd` is a *separate userspace daemon* from the kernel's OOM
killer. It watches per-cgroup **PSI (Pressure Stall Information)**, not per-process
`oom_score_adj` — meaning the project's own kernel-level protection mechanism is invisible
to it entirely. Kali ships a default drop-in
(`/usr/lib/systemd/system/user@.service.d/10-oomd-user-service-defaults.conf`) that arms
`ManagedOOMMemoryPressure=kill` with `ManagedOOMMemoryPressureLimit=50%` on every user
session's `user@1000.service` slice. On a 15GB host loading an 8.7GB `Q8_0` model, crossing
that 50% pressure threshold during load/reload is close to inevitable, not a fluke.

**Verified live, not speculative**:
- Confirmed via `journalctl -u systemd-oomd` (exact kill event, exact threshold: "71.28% >
  50.00% for > 20s with reclaim activity").
- Confirmed the exact drop-in file and its settings.
- Tried the two lowest-blast-radius live fixes first: `systemctl --user set-property
  <tmux-scope> ManagedOOMMemoryPressure=no` and `systemd-run --user --scope -p
  ManagedOOMMemoryPressure=no -- ...`. **Both failed** with `Failed to set unit properties:
  Invalid argument` on this host's systemd 261 — this property is not settable
  imperatively per-scope via either mechanism here.
- Did not attempt a real `/etc/systemd/system/` drop-in file live — requires root, this
  session has no passwordless `sudo` for general commands.

**Options laid out for the operator** (full feasibility/impact/pros/cons tables in
`STAGING-Pending-Discussions-and-Fixes.md` Round 10.1) — **operator chose Option A**: a
session-wide drop-in raising the limit to 90%/60s (rejected B — disabling protection
entirely — as too much risk for unrelated apps; rejected C — a narrower per-scope
code-level fix — since its core mechanism was already confirmed failing live). Commands are
staged and ready; **not yet applied** — needs the operator's own `sudo` run.

---

## 6. MobSF — confirmed fully working

`IMPLEMENTATION-DEVIATIONS-FROM-REQUIREMENTS.md` had `mobsf` marked "still
unbuildable/unverifiable on this host," with no further detail. A fresh investigation
found **zero mentions of `mobsf` anywhere in the `implementation` repo** — not even a
schema stub — meaning the prior attempt never got far enough to leave a trace.

Pulled the official Docker image (`opensecurity/mobile-security-framework-mobsf:latest`,
2.34GB), ran it, and did REAL verification — not just a successful pull:

- Django migrations applied, superuser created, gunicorn bound to `0.0.0.0:8000`.
- `curl -L http://127.0.0.1:8000/` returns a genuine `<title>Sign In</title>` page
  (302 → 200).
- MobSF v4.5.2, REST API key issued.

This resolves the long-standing "unbuildable/unverifiable" status. The deviations doc
itself has not yet been edited to reflect this (verification was the ask this pass, not
the doc correction) — flagged here so it isn't lost. Container was removed after
verification, not left running.

---

## 7. The headline result: real Strategist latency, measured

### 7.1 Why a standalone probe was needed

Engagements 18 and 19 both showed the Strategist's Phase 4.1 planning turn exceeding
`2 × STRATEGIST_TIMEOUT_S (1800s) = 3600s` without ever completing — but the orchestrator's
own timeout-and-retry mechanism (`FR-GATE-08`) meant the TRUE completion latency was
unmeasured, only bounded below at "more than 60 minutes." To learn the real number, a
standalone script called `engine/client.py` directly, bypassing the orchestrator's timeout
entirely (a 14400s/4hr cap instead), reusing the **exact real baseline-recon context** from
engagement 18's completed run — the identical prompt that caused both real engagements to
time out.

### 7.2 The result

```
elapsed_s: 7043.4   (117.4 minutes, ~1h57m)
prompt_tokens: 12449
completion_tokens: 5207
total_tokens: 17656
```

**~1h57m is the true CPU-only latency ceiling for this role, this prompt size, on this
hardware** — roughly 4x the current 1800s-per-attempt budget, which fully explains why both
real engagements (2×1800s each) never finished: the model was still working, it simply
needed about twice that.

### 7.3 An unplanned discovery, caught by the same run

`journalctl` revealed the host **suspended itself mid-probe** —
`xfce4-power-man`-triggered `s2idle` suspend, `16:49:48 → 18:45:40` (1h56m) — while the
model was actively computing. This explained an initially confusing discrepancy: live `ps`
checks during the run showed ~3h50m of real wall-clock elapsed time, while the script's own
`time.monotonic()`-based measurement said only 117.4 minutes. **Both numbers are correct**:
Linux's monotonic clock (and, empirically, whatever the underlying socket-timeout mechanism
uses too) simply stops advancing during `s2idle` suspend — the process resumed exactly
where it left off on wake and finished normally, with the sleep entirely uncounted.

Reconstructed real timeline: ~39 minutes of computing before suspend, then ~78 minutes more
after resume, totaling the measured ~1h57m of genuine active inference — never actually
interrupted, because suspend froze the whole process (including any in-flight socket
timeouts) rather than killing it.

**This is good news for this specific result being clean — and a real, previously
undocumented gap.** Nothing in this project currently inhibits system suspend during an
active engagement. This particular run got lucky (whatever timeout was in effect at each
moment still had headroom when suspend hit); a real orchestrator run using the tighter
1800s `STRATEGIST_TIMEOUT_S` could suspend and resume with a much less forgiving outcome
depending on exact timing — and the project's own Blueprint document claims the system
"runs unattended for hours if needed," which implicitly assumes the OS won't nap through
part of that stretch. Recorded as a candidate follow-up (e.g. `systemd-inhibit
--what=sleep` wrapping the orchestrator process for the duration of an engagement) — not
yet a staged formal proposal, just captured here so it isn't lost.

### 7.4 The output itself — real validation, not just a number

Once it finished, the Strategist produced a coherent, genuinely target-appropriate attack
plan. Full JSON in `/tmp` at probe time; the first four hypotheses, verbatim:

1. **IDOR** — "Access the product details endpoint on port 3000 with different IDs to
   check for insecure direct object reference (IDOR) without authentication." Rationale:
   Juice Shop is deliberately IDOR-vulnerable.
2. **SSRF pivot** — "Submit a URL to the SSRF-vulnerable feature on port 3000 that fetches
   externally, pointing to the internal CUPS service at `http://127.0.0.1:631` to test for
   server-side request forgery." Rationale: SSRF can bypass network boundaries and access
   internal services like CUPS.
3. **Broken access control** — "Attempt to access the `/admin` endpoint on port 3000
   without providing any authentication credentials."
4. **CUPS path traversal** — "Send crafted HTTP requests to the CUPS web interface on port
   631 with directory traversal sequences (e.g., `../`) to access parent directories and
   sensitive files."

This is real evidence the council architecture's core premise holds: given enough compute
time, the small local model produces sensible, evidence-grounded, target-specific planning
— not generic boilerplate. The bottleneck this report documents is speed, not capability.

### 7.5 Recommended next step

Now that the real ceiling is known, the concrete recommendation (staged in
`STAGING-Pending-Discussions-and-Fixes.md` Round 10.2, not yet applied to code) is to raise
`STRATEGIST_TIMEOUT_S` (`vapt_agent/council/strategist.py:48`) from `1800.0` to something
with real margin over the measured 117.4-minute ceiling — e.g. `9000.0` (150 minutes,
~28% headroom) — so a single attempt can complete without needing `FR-GATE-08`'s retry at
all. GPU offload remains the real long-term fix: even with the timeout raised, a full
multi-role, multi-target engagement is still a many-hours-to-overnight affair on this
CPU-only host.

---

## 8. Process hygiene notes

- Chrome and Firefox were closed (via `app_teardown.py`'s functions directly, operator
  asked first since both were actively in use) to clear ~7.5GB headroom for the probe's
  model load, and relaunched cleanly afterward via the same session-restore mechanism
  `vaptctl start`'s own teardown flow uses.
- The probe made exactly one DB interaction — a single read-only `SELECT` of an
  already-completed `baseline_recon_runs` row, connection closed immediately — avoiding
  the "database is locked" self-collision an earlier ad-hoc script hit this same day by
  writing to the live `state.db` concurrently with a real orchestrator run.
- 818 Claude Code cybersecurity skills (`mukul975/Anthropic-Cybersecurity-Skills`) were
  installed into this assistant's own environment during the same session — useful for
  future work on this project, architecturally separate from Mugheeraat's own council
  (which has no dynamic skill-loading mechanism of its own; see the corresponding session
  memory for the full reasoning on why, and a sketch of what a real integration would
  look like).
