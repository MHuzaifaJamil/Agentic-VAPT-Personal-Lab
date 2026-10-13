# Test-lab re-run — 2026-09-08, hibernation disabled

**Engagement:** 7 (`vaptctl start --targets 127.0.0.1 --no-hibernation --no-run`,
then `vaptctl run --engagement-id 7 --no-hibernation --no-tmux`)
**Targets:** Juice Shop (`127.0.0.1:3000`), MediaCMS stack (`127.0.0.1:8080`) —
both confirmed `HTTP 200` before the run started.
**Hibernation:** disabled throughout, per your explicit choice for this
unattended window (`AskUserQuestion` earlier this session).

## Result: blocked by the memory-safety gate, as designed — not a crash, not a bug

The pipeline did not get past loading the first model (Strategist,
`DeepSeek-R1-0528-Qwen3-8B`, Phase 4.1). `engine/mem_gate.py`'s
`MemAvailableGate` (FR-GATE-10, NFR-RES-02) polls `/proc/meminfo`'s
`MemAvailable` for up to 5 seconds and refuses to proceed if it doesn't
clear the model's required footprint — exactly the behavior it's designed
for, working correctly:

```
MemAvailable did not reach 10602542 kB within 5.0s
```

**Real numbers, measured directly, before and after the attempt:**

| | |
|---|---|
| Required (Strategist's footprint + safety margin) | ~10.11 GiB (10,602,542 kB) |
| `MemAvailable` at attempt time | ~7.6 GiB |
| `MemAvailable` immediately after (nothing was loaded, so ~unchanged) | ~8.02 GiB (8,018,388 kB) |
| Shortfall | ~2.1–2.5 GiB |
| Total host RAM | 15 GiB |
| Swap | 15 GiB total, 0 used |

This is exactly the scenario Phase 1 hibernation exists to solve — freeing
that ~2.5 GiB by suspending non-essential apps (browsers, etc., per your
own stated eligibility list) — which is precisely what's disabled for this
run. There's no bug to fix here: the gate did its job (refused to load a
model into a host that couldn't actually hold it, rather than thrashing
into swap or getting OOM-killed mid-load).

**One real gap this exposed, fixed:** the failure reached the operator as
a raw Python traceback instead of a clean message — `cli/run.py` only
caught `ModelFileMissingError` before this, not `DegradedSwapAlert`. Both
are now caught the same way (`vapt_agent/cli/run.py`), verified with
`ruff`/`mypy`/`tests/test_cli_run.py` (8 passed).

**Also verified live, not just in tests:** the `orchestrator/driver.py`
`try/finally` fix from tonight's code-review pass actually fired correctly
on this real exception — `engagement_phase_log` for engagement 7 shows a
real `5_HIBERNATE` row (`outcome=OK`) written even though `run_phase_4_1`
raised mid-load, confirming the dashboard's Reporter-completion fix works
outside of test mocks too.

## What this means for the next attempt

Retrying right now would fail identically — `MemAvailable` hasn't moved
(nothing was loaded to begin with). Two ways forward, both your call, not
mine to decide unattended:

1. **Re-enable hibernation** (`--enable-hibernation`) — this is the
   mechanism actually built to solve exactly this gap, and everything
   flagged in tonight's code-review pass in that code path has been fixed
   and verified (dry-run tool, sandbox tests, full suite). Given the
   review's scope (this exact file), I'd consider this reasonably safer
   than it was this morning, but "reasonably safer" isn't the same
   guarantee as "proven" — three real incidents already happened in this
   exact code before tonight.
2. **Free ~2.5 GiB manually** (close some browser tabs/apps yourself) and
   re-run with hibernation still off — keeps tonight's "no hibernation
   while unattended" choice intact.

I did not take either action unilaterally — didn't re-enable hibernation
(that reverses your explicit choice for this unattended window) and didn't
close/kill any other host process to free memory myself (that's the same
class of action hibernation performs, just without its safety
classification logic, and not something to do to your desktop without
asking).

## Artifacts in this directory

- `metadata.txt` — pre-run host/Docker state.
- `start.log` — `vaptctl start` output (engagement creation).
- `run.log` — full `vaptctl run` output, including the traceback (raw, as
  captured — the clean-message fix above applies to the NEXT run, not
  retroactively to this log).
- `run.pid` — the (now-exited) pipeline process id.
