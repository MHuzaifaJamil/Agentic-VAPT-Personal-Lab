# LLM Council Benchmarks

> **Purpose:** a lean, numbers-only tracker for council-role response timing, success/
> failure, and other varying system metrics — across every past and future engagement.
> Full narrative writeups live in this same `reports/` folder (`BENCHMARK-REPORT-*.md`,
> one per session); this file exists so the *numbers* don't require digesting those. See
> `source/Testing-Rules.md` for the reporting-conciseness rule this file exists to satisfy.
>
> **Update convention:** append new rows to the tables below after every real (non-mocked)
> council role invocation you have timing/outcome data for — engagement runs, standalone
> probes, retests alike. Never overwrite a past row. Recompute the rollup numbers in
> §2/§3 after appending.

---

## 0. Engagement Summaries (≤5 sentences / 50–80 words each — see `Testing-Rules.md`)

**2026-09-13.** Found the venv's `activate` script pointed at a stale renamed path, silently
running system Python all along. GPU offload proved slower than CPU (1.91 vs 2.50 tok/s) on
this host's iGPU. Found and fixed a real memory bug: `llama-server`'s default reserved 4x
the needed KV cache. Ran all 6 council roles live; 5 succeeded, Secondary Scripter failed 3x
from a broken GGUF's missing tokenizer metadata — root-caused, fixed, and retested
successfully. Also implemented Round 12's skill-ingestion feature.

**2026-09-12.** Rebuilt a broken Python 3.14 venv; ran 4 live engagements against
JuiceShop/MediaCMS. Found `systemd-oomd` killing engagements under memory pressure (default
50% threshold) and that MobSF was actually working, not unverifiable as previously assumed.
An uncapped probe measured the Strategist's real CPU-only latency at 117.4 minutes for a
12k-token prompt — previously unknown. Host also auto-suspended mid-probe, an undocumented
gap. Fixed the Strategist timeout to reflect the real measured ceiling.

**2026-09-13 (engagement 21, live).** Fixed 2 real Round 12 matcher bugs (stopword
false-positives, unclosed code fences) via external review + empirical corpus testing. Ran
engagement 21 live against JuiceShop: confirmed 4/36 real Strategist tasks matched a skill
reference (SSRF, template injection, auth weaknesses), one genuinely injected into a live
Primary Scripter call. Found the live journal (console) was fully built but never wired in —
fixed. Also added dashboard elapsed-time/ETA/%-done columns and fixed a stale `@gate1`-only
console tag.

**2026-09-13 (RCA, engagements 21+22 crash).** Root-caused the Secondary Scripter crash that
killed both live engagements: `StructuredOutputError` was never caught anywhere between
`phase_lifecycle.py` and `cli/run.py`, so an exhausted structured-output retry budget (a real,
occasional model miss the budget exists to absorb) crashed the whole orchestrator process
instead of just that one task. Ruled out prompt vagueness and context size via 18 real repeat
attempts (all clean). Fixed: the task is now marked `GATE2_BLOCKED` and the engagement
continues. Confirmed via 2 new real regression tests plus the 18-attempt reproduction data.

**2026-09-13/14 (engagement 23, live, post-fix).** First fully clean live engagement this
session: all 12 real invocations succeeded (Strategist, 4x Auditor, 3x Primary Scripter,
4x Secondary Scripter), no crash. The Secondary Scripter fix wasn't exercised by an actual
failure this run (all 4 of its calls succeeded on the first attempt), but this is the cleanest
end-to-end confirmation yet that the orchestrator itself is stable post-fix. Hit the same
MediaCMS-vs-MemAvailableGate recurrence once on launch (stopped `celery_worker`/`celery_beat`/
`web` again, restored after completion).

**2026-09-14 (dashboard/console investigation).** Confirmed Adjudicator/Reporter never
appearing on the dashboard is correct, not a bug: both only load when `candidate_detection.py`'s
deliberately conservative nuclei/sqlmap/nmap-vuln-script raw-output match fires, and no real
engagement to date has produced one (engagement 23's nuclei artifact was empty; its nmap runs
used `http-enum`, not a vuln script — verified against the real raw artifacts, not assumed).
Separately, found and fixed a real console bug: `_refresh_stream_pane` cleared and rewrote the
whole journal tail every 1s tick, and `RichLog.write()`'s default scroll-to-bottom meant any
manual scroll-up reverted within a second. Now appends only new journal bytes
(`read_new_lines`, `security/live_journal.py`) and only follows the bottom when the operator
was already there. 6 new real regression tests; full suite clean (1113 passed, 3 skipped).

**2026-09-14 (root cause of zero findings, fixed).** Operator asked why JuiceShop — a
deliberately vulnerable app — produced zero confirmed findings across 23 engagements. Root
cause, found via code inspection: neither Scripter's prompt ever stated the real target
host (only 3/25 real task descriptions ever mentioned it), and Gate 1 Tier 0's scope check
validated the task's static registered target string, never the command's own `argv`.
Confirmed live: a Primary Scripter task hit `curl http://example.com/api/users` (real
internet request, not the target) and a Secondary Scripter task hit `nmap ...
target_system_ip` (unresolved placeholder, 0 hosts scanned) — both logged `SUCCESS`. Fixed:
both Scripters now get an explicit `TARGET` prompt field; `check_tier0` gained a
deterministic argv-destination check (schema-driven for Tier 1, URL/IP-shape fallback for
Tier 2), autonomous-tasks-only by construction. 27 new tests; full suite 1126 passed, 3
skipped. Not yet confirmed live (verified via deterministic tests only, per explicit
operator instruction not to test-run models this round).

**2026-09-14 (engagement 24, live — target_host fix confirmed).** First live test of the
target_host fix: Primary Scripter's task 382 correctly generated `curl -k -X GET
https://127.0.0.1:3000/admin` (real JuiceShop host:port, not a hallucinated one) — the first
correctly-targeted Scripter command in 24 engagements. Gate 1's new destination check never
fired (no wrong-host command was ever proposed, so nothing needed catching). A new,
unrelated issue surfaced: the Auditor rejected/revised 6 of 7 hypotheses, several reasoning
that 127.0.0.1 is "not reachable externally"/out of scope despite `scope_rules` explicitly
allowing it. Still 0 verified findings — candidate_detection never fired.

**2026-09-16 (Rounds 15/16, corrections + 4 fixes).** Corrected 3 misreads from the
09-14 entry above (28 "pending" tasks were baseline-recon bookkeeping, not backlog; two
different `nmap` calls got conflated; a `GATE2_BLOCKED` was a duplicate-command guard, not an
`-oA` safety rejection). Then: rewrote the Auditor's prompt to have zero scope/reachability
authority (operator-supplied text); made the engagement lifecycle loop council rounds until
`min_confirmed_reports` (5, for the upcoming JuiceShop run) is met instead of always running
once; threaded baseline recon's real open ports into every Scripter prompt; made
`INFO_REGISTER` generation unconditional so an engagement can't complete with zero reports.
1134 passed, 0 failed, 3 skipped.

---

## 1. Per-Role Response Log (every real invocation, newest first)

| Date | Source | Role | Model | Load (s) | Wall (s) | Prompt tok | Completion tok | tok/s | Result |
|---|---|---|---|---|---|---|---|---|---|
| 2026-09-14 | Engagement 24 (live, target_host fix) | Secondary Scripter | qwen2.5-coder-7b-instruct-q8_0 | — | 47.4 | n/a | 137 | 2.89 | ⚠️ GATE2_BLOCKED (task 389, `-oA` file-write flag not in nmap schema — correctly blocked, no crash) |
| 2026-09-14 | Engagement 24 (live, target_host fix) | Secondary Scripter | qwen2.5-coder-7b-instruct-q8_0 | — | 198.2 | n/a | 85 | 0.43 | ✅ SUCCESS (task 386, `nmap -sV -p 80,443 127.0.0.1` — correct real host) |
| 2026-09-14 | Engagement 24 (live, target_host fix) | Primary Scripter | qwen2.5-coder-7b-instruct-q8_0 | — | 123.6 | n/a | 94 | 0.76 | ✅ SUCCESS (task 382 Tier 2, `curl -k -X GET https://127.0.0.1:3000/admin` — first correctly-targeted Scripter command in 24 engagements) |
| 2026-09-14 | Engagement 24 (live, target_host fix) | Auditor (Gate-1) | Hermes-3-Llama-3.1-8B-Q8_0 | — | 50.4 | n/a | 150 | 2.98 | ⚠️ SUCCESS but wrong reasoning (task 385 `revise`, cited 127.0.0.1 as unreachable/out of scope — it is in scope) |
| 2026-09-14 | Engagement 24 (live, target_host fix) | Lead Strategist | DeepSeek-R1-0528-Qwen3-8B-Q8_0 | — | 8328.4 | n/a | 5036 | 0.60 | ✅ SUCCESS — new real latency max (138.8 min), still within the 9000s/150min timeout with ~11min margin |
| 2026-09-14 | Engagement 23 (live, post-fix) | Secondary Scripter | deepseek-coder-6.7b-instruct-q8_0 | — | 47.9 | 1244 | 39 | 0.81 | ✅ SUCCESS (task 350, turn 4) |
| 2026-09-14 | Engagement 23 (live, post-fix) | Secondary Scripter | deepseek-coder-6.7b-instruct-q8_0 | — | 57.4 | 1284 | 151 | 2.63 | ✅ SUCCESS (task 350, turn 3) |
| 2026-09-14 | Engagement 23 (live, post-fix) | Secondary Scripter | deepseek-coder-6.7b-instruct-q8_0 | — | 39.5 | 1236 | 109 | 2.76 | ✅ SUCCESS (task 349, turn 2) |
| 2026-09-14 | Engagement 23 (live, post-fix) | Secondary Scripter | deepseek-coder-6.7b-instruct-q8_0 | — | 163.0 | 1261 | 94 | 0.58 | ✅ SUCCESS (task 349, turn 1) — all 4 real Secondary Scripter calls this engagement succeeded, none needed the `GATE2_BLOCKED` fix path |
| 2026-09-14 | Engagement 23 (live, post-fix) | Primary Scripter | qwen2.5-coder-7b-instruct-q8_0 | — | 14.4 | 1653 | 30 | 2.09 | ✅ SUCCESS (task 347, attempt 3/3) |
| 2026-09-14 | Engagement 23 (live, post-fix) | Primary Scripter | qwen2.5-coder-7b-instruct-q8_0 | — | 29.2 | 1770 | 84 | 2.88 | ✅ SUCCESS (task 347, attempt 2/3) |
| 2026-09-14 | Engagement 23 (live, post-fix) | Primary Scripter | qwen2.5-coder-7b-instruct-q8_0 | — | 207.8 | 1704 | 90 | 0.43 | ✅ invocation OK, command Gate-2-**rejected** downstream — `curl` not a registered Tier 1 tool (attempt 1/3, task 347) |
| 2026-09-14 | Engagement 23 (live, post-fix) | Auditor | Hermes-3-Llama-3.1-8B-Q8_0 | — | 56.5 | 652 | 184 | 3.26 | ✅ SUCCESS (task 348) |
| 2026-09-14 | Engagement 23 (live, post-fix) | Auditor | Hermes-3-Llama-3.1-8B-Q8_0 | — | 31.0 | 643 | 83 | 2.68 | ✅ SUCCESS (task 347) |
| 2026-09-14 | Engagement 23 (live, post-fix) | Auditor | Hermes-3-Llama-3.1-8B-Q8_0 | — | 60.3 | 639 | 205 | 3.40 | ✅ SUCCESS (task 346) |
| 2026-09-14 | Engagement 23 (live, post-fix) | Auditor | Hermes-3-Llama-3.1-8B-Q8_0 | — | 108.8 | 642 | 146 | 1.34 | ✅ SUCCESS (task 345) |
| 2026-09-14 | Engagement 23 (live, post-fix) | Lead Strategist | DeepSeek-R1-0528-Qwen3-8B-Q8_0 | — | 2041.0 | 3114 | 3545 | 1.74 | ✅ SUCCESS — real attack plan, uncapped, first fully clean engagement completion this session (12/12 invocations OK) |
| 2026-09-13 | RCA round 2 (real prod fn, `run_secondary_scripter_command`, no `-c` override) | Secondary Scripter | deepseek-coder-6.7b-instruct-q8_0 | 5.2 | 24.1–159.1 (8 attempts) | — | — | — | ✅ 8/8 SUCCESS — real production call path, matches production context exactly; rules out both prompt-vagueness and context-size hypotheses |
| 2026-09-13 | RCA round 1 (`get_structured_completion`, direct + `-c 4096` override) | Secondary Scripter | deepseek-coder-6.7b-instruct-q8_0 | — | — | — | — | — | ✅ 10/10 SUCCESS (5/5 with `-c 4096`, 5/5 no override) — flawed harness (bypassed real retry path), superseded by RCA round 2 |
| 2026-09-13 | Engagement 22 (live) | Secondary Scripter | deepseek-coder-6.7b-instruct-q8_0 (fixed) | — | 269.4 | 1357 | 189 | 0.70 | ❌ CRASHED (pre-fix) — `StructuredOutputError`, 2nd real occurrence of this exact pattern (189 vs task 281's 193 completion tokens, both well under any cap) — real root cause found: `StructuredOutputError` uncaught between `phase_lifecycle.py` and `cli/run.py`, crashing the whole engagement instead of just this task. Fixed: task now marked `GATE2_BLOCKED`, engagement continues (commit `463f4b0`) |
| 2026-09-13 | Engagement 22 (live) | Auditor | Hermes-3-Llama-3.1-8B-Q8_0 | — | 42.4 | 651 | 127 | 2.99 | ✅ SUCCESS (task 314) |
| 2026-09-13 | Engagement 22 (live) | Auditor | Hermes-3-Llama-3.1-8B-Q8_0 | — | 46.8 | 656 | 143 | 3.05 | ✅ SUCCESS (task 313) |
| 2026-09-13 | Engagement 22 (live) | Auditor | Hermes-3-Llama-3.1-8B-Q8_0 | — | 53.5 | 663 | 167 | 3.12 | ✅ SUCCESS (task 312) |
| 2026-09-13 | Engagement 22 (live) | Auditor | Hermes-3-Llama-3.1-8B-Q8_0 | — | 109.2 | 662 | 141 | 1.29 | ✅ SUCCESS (task 311) |
| 2026-09-13 | Engagement 22 (live) | Lead Strategist | DeepSeek-R1-0528-Qwen3-8B-Q8_0 | — | 1669.6 | 3088 | 2929 | 1.75 | ✅ SUCCESS — real attack plan, uncapped |
| 2026-09-13 | Engagement 21 (live) | Secondary Scripter | deepseek-coder-6.7b-instruct-q8_0 (fixed) | — | 302.3 | 1357 | 193 | 0.64 | ❌ CRASHED — `StructuredOutputError`, real schema-validation miss, **not** the old tokenizer bug (completion well under any cap, corrected model confirmed loaded) |
| 2026-09-13 | Engagement 21 (live) | Primary Scripter | qwen2.5-coder-7b-instruct-q8_0 | — | 13.4 | 1653 | 30 | 2.24 | ✅ SUCCESS — invocation OK, command Gate-2-accepted (attempt 3/3, task 275 — skill_reference `performing-ip-reputation-analysis-with-shodan` injected) |
| 2026-09-13 | Engagement 21 (live) | Primary Scripter | qwen2.5-coder-7b-instruct-q8_0 | — | 35.6 | 1856 | 83 | 2.33 | ✅ invocation OK, command Gate-2-**rejected** downstream (attempt 2/3, task 275) |
| 2026-09-13 | Engagement 21 (live) | Primary Scripter | qwen2.5-coder-7b-instruct-q8_0 | — | 219.5 | 1790 | 71 | 0.32 | ✅ invocation OK, command Gate-2-**rejected** downstream (attempt 1/3, task 275) |
| 2026-09-13 | Engagement 21 (live) | Auditor | Hermes-3-Llama-3.1-8B-Q8_0 | — | 35.5 | 637 | 115 | 3.24 | ✅ SUCCESS (task 280) |
| 2026-09-13 | Engagement 21 (live) | Auditor | Hermes-3-Llama-3.1-8B-Q8_0 | — | 53.1 | 640 | 194 | 3.65 | ✅ SUCCESS (task 279) |
| 2026-09-13 | Engagement 21 (live) | Auditor | Hermes-3-Llama-3.1-8B-Q8_0 | — | 59.4 | 645 | 227 | 3.82 | ✅ SUCCESS (task 278) |
| 2026-09-13 | Engagement 21 (live) | Auditor | Hermes-3-Llama-3.1-8B-Q8_0 | — | 38.1 | 648 | 129 | 3.38 | ✅ SUCCESS (task 277) |
| 2026-09-13 | Engagement 21 (live) | Auditor | Hermes-3-Llama-3.1-8B-Q8_0 | — | 41.0 | 648 | 136 | 3.32 | ✅ SUCCESS (task 276) |
| 2026-09-13 | Engagement 21 (live) | Auditor | Hermes-3-Llama-3.1-8B-Q8_0 | — | 89.9 | 650 | 89 | 0.99 | ✅ SUCCESS (task 275) |
| 2026-09-13 | Engagement 21 (live) | Lead Strategist | DeepSeek-R1-0528-Qwen3-8B-Q8_0 | — | 995.0 | 2998 | 2060 | 2.07 | ✅ SUCCESS — real 36-hypothesis attack plan |
| 2026-09-13 | Retest (fixed GGUF) | Secondary Scripter | deepseek-coder-6.7b-instruct-q8_0 | 1.1 | 153.7 | — | — | — | ✅ SUCCESS (1st attempt) |
| 2026-09-13 | Council-wide probe | Lead Strategist | DeepSeek-R1-0528-Qwen3-8B-Q8_0 | 5.2 | 2594.1 | 3011 | 4618 | 1.78 | ✅ SUCCESS |
| 2026-09-13 | Council-wide probe | Primary Scripter | qwen2.5-coder-7b-instruct-q8_0 | 4.8 | 179.4 | 1721 | 91 | 0.51 | ✅ SUCCESS |
| 2026-09-13 | Council-wide probe | Secondary Scripter | deepseek-coder-6.7b-instruct-q8_0 (broken tokenizer) | 1.1 | 411.2 | ~1332 | 1024 | — | ❌ FAILED (attempt 1/3, hit cap) |
| 2026-09-13 | Council-wide probe | Secondary Scripter | deepseek-coder-6.7b-instruct-q8_0 (broken tokenizer) | — | 297.2 | ~1397 | 1024 | — | ❌ FAILED (attempt 2/3, hit cap) |
| 2026-09-13 | Council-wide probe | Secondary Scripter | deepseek-coder-6.7b-instruct-q8_0 (broken tokenizer) | — | 302.7 | ~1457 | 1024 | — | ❌ FAILED (attempt 3/3, hit cap → StructuredOutputError) |
| 2026-09-13 | Council-wide probe | Reporter | Ministral-8B-Instruct-2410-Q8_0 | 10.7 | 198.8 | 1185 | 294 | 1.48 | ✅ SUCCESS |
| 2026-09-13 | Council-wide probe | Criterion Adjudicator | Mistral-7B-Instruct-v0.3-Q8_0 | 9.6 | 235.8 | 1380 | 382 | 1.62 | ✅ SUCCESS |
| 2026-09-13 | Council-wide probe | Auditor (Gate-1) | Hermes-3-Llama-3.1-8B-Q8_0 | 15.3 | 85.6 | 660 | 94 | 1.10 | ✅ SUCCESS |
| 2026-09-13 | GPU benchmark (FR-PRE-08) | Primary Scripter | qwen2.5-coder-7b-instruct-q8_0 | — | — | short | short | 1.91 (GPU) | ✅ SUCCESS, GPU offload slower than CPU |
| 2026-09-13 | GPU benchmark (FR-PRE-08) | Primary Scripter | qwen2.5-coder-7b-instruct-q8_0 | — | — | short | short | 2.50 (CPU) | ✅ SUCCESS, CPU baseline |
| 2026-09-12 | Uncapped latency probe (Round 10.2C) | Lead Strategist | DeepSeek-R1-0528-Qwen3-8B-Q8_0 | — | 7043.4 | 12449 | 5207 | ~0.74 | ✅ SUCCESS (real baseline-recon context) |
| 2026-09-02 | Live capstone run (historical) | Lead Strategist | DeepSeek-R1-0528-Qwen3-8B-Q8_0 | — | 763.8 | — | — | — | ✅ SUCCESS |
| 2026-09-02 | Live capstone run (historical) | Lead Strategist | DeepSeek-R1-0528-Qwen3-8B-Q8_0 | — | >900 (killed) | — | — | — | ⏱️ INFRA TIMEOUT (pre-dates the 9000s fix, not a model failure) |

---

## 2. Council Success Rate (cumulative, current-system rows only — excludes the 2026-09-02 historical pre-fix rows)

Counting `2026-09-12` onward (the system state after the Strategist-timeout fix, before which the 900s infra
ceiling makes older numbers not comparable):

| Metric | Value |
|---|---|
| Total real role-invocation attempts logged | 58 |
| Successful (invocation status `OK`) | 53 (91.4%) |
| Engagement 23 (post-fix, live) | 12/12 real invocations succeeded — first fully clean engagement completion this session; the fix path (`GATE2_BLOCKED`) wasn't exercised since no Secondary Scripter call needed it |
| Failed — old broken-tokenizer GGUF (root-caused + fixed same session) | 3 — all Secondary Scripter, §4.3 `BENCHMARK-REPORT-2026-09-13.md` |
| Failed — real schema-validation miss on the corrected model, pre-fix orchestrator crash | 2 — Secondary Scripter, engagement 21 task 281 (193 completion tok) and engagement 22 task 315 (189 completion tok), both `StructuredOutputError` after 3 real attempts, both well under any cap; root-caused and fixed 2026-09-13 (see below) — no longer crashes the engagement |
| Invocation-level success but Gate-2-rejected downstream (not a model failure) | 2 — Primary Scripter, task 275 attempts 1-2; the model call itself succeeded both times, a separate deterministic check rejected the proposed command |
| Successful **after** the tokenizer fix, same role/task | 1/1 standalone retest (100%) + 11/11 Auditor, 3/3 Primary Scripter invocations, 2/2 Strategist, across engagements 21+22 (live) |
| RCA reproduction attempts, Secondary Scripter (real prod call path) | 18/18 SUCCESS (10 via `get_structured_completion` direct, 8 via the real `run_secondary_scripter_command`) — could not reproduce the crash on demand; real root cause found via code inspection instead (see §12, `BENCHMARK-REPORT-2026-09-13.md`) |
| Roles with a 100% real invocation success rate to date | Strategist (5/5), Auditor (11/11), Primary Scripter (5/5 invocations, 1 command Gate-2-rejected downstream twice before acceptance), Adjudicator (1/1), Reporter (1/1) |
| Roles with a known historical failure mode, now fixed (tokenizer) | Secondary Scripter (0/3 → 1/1 post-fix standalone) |
| Secondary Scripter crash-handling fix (2026-09-13) | An exhausted structured-output retry (a real, occasional model miss the retry budget exists to absorb) previously crashed the whole orchestrator; now caught and the single task is marked `GATE2_BLOCKED` while the engagement continues. Confirmed via 2 new regression tests (`test_orchestrator_phase_lifecycle.py`) exercising the real retry-exhaustion path, plus 18/18 clean reproduction attempts, plus the full suite (1108 passed, 3 skipped). Commit `463f4b0` |

**Caveat:** N is still small (58 attempts). Treat this as a directional signal, not a statistically
confident rate, until more real engagements accumulate rows in §1.

**Skill-reference trigger rate (Round 12, live engagements):**
- Engagement 21: 4 of 36 real Strategist-generated tasks matched a skill reference (`τ=0.65`) —
  SSRF, template injection, auth weaknesses, and IP reputation. 1 of those 4 was Gate-1-approved
  and actually reached Scripter dispatch, genuinely injecting the matched skill's operational
  section as a `<task_reference>` block — the first live, end-to-end confirmation the feature
  works, not just in a synthetic probe.
- Engagement 22: 2 of 34 real tasks matched (directory traversal/LFI, mass assignment) — both
  strong, accurate matches; both were Gate-1-rejected before reaching Scripter dispatch, so no
  new live injection this run. Cumulative across 2 engagements: **6/70 real tasks matched
  (8.6%)**, 1/6 actually reached a live prompt.

---

## 3. Other Varying Metrics Worth Tracking

| Metric | Value | Source / Note |
|---|---|---|
| CPU-only generation ceiling (Q8_0, 7-8B class, this host) | ~1.1 – 1.8 tok/s | Consistent across 5 different models — memory-bandwidth-bound, not thread-count-bound (`-t 18` vs `-t 8` barely moved gen speed, 2026-09-12 finding) |
| GPU offload vs CPU-only (this host's iGPU) | CPU **wins**: 2.50 vs 1.91 tok/s | `BENCHMARK-REPORT-2026-09-13.md` §3 — iGPU shares system RAM bandwidth, no dedicated VRAM advantage |
| `llama-server` default KV-cache waste (pre-fix) | ~4x (n_slots=4 vs the 1 this system ever uses) | Fixed via `-np 1`, `vapt_agent/engine/client.py`, commit `978eb21` |
| Real RSS, deepseek-coder-6.7b @ `-np 1`, default `-c` (15360) | 13.67 GB | vs. an implied ~33GB at the old 4-slot default — would never fit this 15GB host |
| Real RSS, same model @ `-np 1 -c 8192` | 10.70 GB | Benchmark-host-only context bound, not a production change |
| Real RSS, same model @ `-np 1 -c 6144` | 9.70 GB | ″ |
| Real RSS, same model @ `-np 1 -c 3072` | ~8.9 GB (est.) | ″ |
| Host total RAM | 15 GB | Single-model residency (`FR-GATE-02`) — one model loaded at a time regardless |
| Strategist wall time vs prompt size | 43.2 min @ 3011 prompt tok · 117.4 min @ 12449 prompt tok | Scales with prompt + reasoning-trace length, not a fixed constant — see §1 |
| Model load time (cold, mmap) | 1.1 – 15.3 s across all 6 roles | Not a bottleneck relative to generation time |
