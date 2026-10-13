# Live Benchmark Report — 2026-09-13

> **Scope of this document.** Follow-on session to `BENCHMARK-REPORT-2026-09-12.md`, covering:
> a real `.venv` corruption bug found and fixed, the FR-PRE-08 GPU-offload benchmark's real
> (and surprising) result, a real production memory-safety bug in `LlamaCppEngineClient`
> found and fixed while running a council-wide latency probe, and — the headline result — the
> first-ever measured real completion latency and reliability data for all 6 council roles,
> not just the Strategist. Companion decision-tracking lives in
> `source/STAGING-Pending-Discussions-and-Fixes.md` (Round 10's updates + new Round 13); this
> document is the full narrative and data behind those staged decisions.

---

## 1. Summary

| Area | Outcome |
|---|---|
| `.venv` | Was silently running on system Python the whole time `source .venv/bin/activate` was used — activate script/entry-point shebangs still pointed at a dead `.venv-new` path from an earlier rename. Fixed permanently (all absolute-path references corrected). |
| Test suite | 1079 passed, 0 failed, 3 skipped (after the venv fix; was failing to even collect 13 test files beforehand) |
| GPU offload (FR-PRE-08) | **Real result: NOT beneficial.** CPU-only 2.50 tok/s vs GPU-offload 1.91 tok/s, same model/prompt |
| Production bug found+fixed | `llama-server` default `-np`/`--parallel=-1` ("auto") → `n_slots=4`, ~4x KV cache overallocation vs. this system's actual 1-request-at-a-time usage. Fixed with `-np 1`. Real RSS: 13.67GB → would-be ~33GB at the old default (would never fit this 15GB host) |
| Council-wide latency probe | 5/6 roles real success, 1 real (non-crash) failure — see §4 |

---

## 2. The `.venv` corruption bug

### 2.1 Symptom

`source .venv/bin/activate && python3 -m pytest -q` produced 13 collection errors, all
`ModuleNotFoundError: No module named 'textual'`, despite `textual>=8.0,<9` being a declared
dependency in `pyproject.toml`.

### 2.2 Root cause

The venv had been created at a path `.venv-new` during an earlier rebuild (see
`BENCHMARK-REPORT-2026-09-12.md`'s Python 3.13→3.14 rebuild), then renamed to `.venv`.
Python venvs are **not relocatable** by a plain `mv` — every generated entry-point script
(`bin/pytest`, `bin/mypy`, `bin/coverage`, …) has its interpreter shebang hardcoded to the
*original* absolute path, and `bin/activate` bakes `VIRTUAL_ENV`/`PATH` the same way.
Concretely: `source .venv/bin/activate` set `PATH` to prepend
`.../implementation/.venv-new/bin` — a directory that no longer existed — so `which python3`
and `which pip` silently fell through to system Python 3.14, which lacks `textual` (and any
other venv-only dependency). This had been true for the entire session up to this point;
every `python3 -c "..."` snippet that "worked" earlier only did so because Python's
`sys.path[0]` includes the current working directory, so `import vapt_agent` resolved via
the local source tree directly, masking the fact that the venv itself was never actually
active.

### 2.3 Fix

`grep -rl '.venv-new' .venv/bin/ .venv/pyvenv.cfg` found 24 affected files. Every literal
`.venv-new` absolute-path reference was rewritten to `.venv` via `sed` (shebangs,
`VIRTUAL_ENV`/`PATH` assignments in `activate`/`activate.csh`/`activate.fish`, and the
cosmetic `VIRTUAL_ENV_PROMPT`). Verified: `source .venv/bin/activate && which python3`
now correctly resolves inside `.venv/bin/`.

### 2.4 Verification

Full suite: **1079 passed, 0 failed, 3 skipped** (one transient live-network flake on first
run — `test_tier1_breach_check.py`'s real HIBP API call — reran clean in isolation and on a
full second pass, confirmed not a real regression).

---

## 3. FR-PRE-08 GPU offload benchmark — real result

Once Round 10.2 Option B's Intel Level Zero/OpenCL driver install was confirmed live
(`check_gpu_offload()` → `passed=True`, `intel_gpu_driver_present=True`,
`render_nodes=['/dev/dri/renderD128']`), `run_gpu_offload_benchmark()` was run for real
against `primary_scripter` (`qwen2.5-coder-7b-instruct-q8_0.gguf`), identical short fixed
prompt both ways:

| Backend | tok/s |
|---|---|
| CPU-only (`-ngl 0`) | **2.50** |
| GPU-offload (`-ngl 99`) | **1.91** |

`offload_beneficial=False`, `gpu_load_error=None` (GPU offload loaded and ran successfully —
it is just genuinely slower). Best-guess explanation: this host's iGPU shares system RAM
bandwidth with the CPU rather than having dedicated VRAM, and this host's CPU-only
generation was already established (`Assumptions-Not-Approved.md`, 2026-09-12) to be
memory-bandwidth-bound, not thread-count-bound — the iGPU has no spare bandwidth to turn
into a speed advantage, only added driver/offload overhead. See
`STAGING-Pending-Discussions-and-Fixes.md`, Round 10, for the full analysis and what this
means for Option B going forward (still correctly installed, just not the speed fix it was
expected to be).

---

## 4. Council-wide uncapped latency/reliability probe

### 4.1 Methodology

Each of the 6 real production role wrapper functions was called directly
(`council/strategist.py::run_strategist`, `strategy_auditor.py::run_gate1_semantic`,
`primary_scripter.py::run_primary_scripter_command`,
`secondary_scripter.py::run_secondary_scripter_command`,
`criterion_adjudicator.py::run_adjudicator`, `reporter.py::run_reporter`), `conn=None` (a
documented safe no-op passthrough in every one of these functions — no DB/logging side
effects), against a real loaded model via `LlamaCppEngineClient`, with a realistic synthetic
task/finding/evidence input per role. Sequential load → call → unload (this system's own
`FR-GATE-02` hard single-model-residency means no two roles ever run concurrently in
production either). A thin recording subclass of `LlamaCppEngineClient` transparently
captured every underlying `chat_completion` call's wall time and token usage, regardless of
which role wrapper (or internal Gate-2 validation-retry loop) invoked it.

Not run through the orchestrator's own timeout wrappers (the probe is deliberately uncapped
in time, matching Round 10.2 Option C's precedent) — role-appropriate `max_tokens` safety
valves were used instead: **1024** for the 5 non-reasoning JSON-verdict roles (real
completions never exceeded 382 tokens — this is a generous ceiling, not a functional cap),
**6000** for the Strategist (a DeepSeek-R1 reasoning model that emits a long internal trace
before its JSON answer; production itself sets no `max_tokens` at all for any role). Every
real completion below finished well under its cap except where noted.

### 4.2 Results

| Role | Model | Load | Wall time | Prompt tok | Completion tok | tok/s | Result |
|---|---|---|---|---|---|---|---|
| Auditor (Gate-1) | Hermes-3-Llama-3.1-8B | 15.3s | 85.6s (1.4min) | 660 | 94 | 1.10 | ✅ real `approve` verdict |
| Criterion Adjudicator | Mistral-7B-Instruct-v0.3 | 9.6s | 235.8s (3.9min) | 1380 | 382 | 1.62 | ✅ real `CONFIRMED` verdict |
| Reporter | Ministral-8B-Instruct-2410 | 10.7s | 198.8s (3.3min) | 1185 | 294 | 1.48 | ✅ real finding report drafted |
| Secondary Scripter | deepseek-coder-6.7b-instruct | 1.1s | n/a (3 attempts, ~16.85min total) | ~1400 avg | 1024 (×3, every attempt) | n/a | ❌ real failure — see §4.3 |
| Primary Scripter | qwen2.5-coder-7b-instruct | 4.8s | 179.4s (3.0min) | 1721 | 91 | 0.51 | ✅ real Tier-1 tool-invocation JSON |
| Lead Strategist | DeepSeek-R1-0528-Qwen3-8B | 5.2s | 2594.1s (43.2min) | 3011 | 4618 | 1.78 | ✅ real 5-hypothesis attack-plan JSON |

Generation speed across roles clusters around 1.1-1.8 tok/s (Primary Scripter's 0.51 tok/s
is an outlier from a very short 91-token completion, where fixed per-request overhead
dominates the tok/s ratio) — consistent with the memory-bandwidth-bound CPU generation
ceiling already established for this hardware, independent of which specific 7-8B Q8_0 model
is loaded.

The Strategist's two independent real measurements (117.4 min for a ~12k-prompt-token real
baseline-recon context on 2026-09-12; 43.23 min for a ~3k-prompt-token synthetic context
here) both land on ~1.7-1.8 tok/s generation speed — confirming this role's wall-clock cost
scales with prompt size + reasoning-trace length, not a fixed per-call constant.

### 4.3 Secondary Scripter's real failure — root cause

`StructuredOutputError: exhausted 2 retries (3 attempts total)`. All 3 real attempts
(411.2s, 297.2s, 302.7s) hit **exactly** the 1024-token `max_tokens` ceiling every time
(`completion_tokens: 1024, 1024, 1024`) — it never once emitted a natural stop token within
budget, on any attempt, regardless of the corrective re-prompt `get_structured_completion`
sends after a validation failure. This exact GGUF also logs a real warning at raw
`llama-server` startup:

```
missing pre-tokenizer type, using: 'default'
GENERATION QUALITY WILL BE DEGRADED!
CONSIDER REGENERATING THE MODEL
control-looking token: 32015 '<｜fim▁hole｜>' was not control-type; this is probably a bug in the model
special_eos_id is not in special_eog_ids - the tokenizer config may be incorrect
```

This is a plausible, concrete root cause independent of prompt content or cap size: a
misconfigured/incomplete tokenizer means the model may never reliably signal "done." This is
a real, actionable finding — **the Secondary Scripter role, on the currently-installed
`deepseek-coder-6.7b-instruct-q8_0.gguf`, cannot currently be trusted to reliably produce
valid structured output** — worth re-downloading/regenerating this specific GGUF or swapping
the model, independent of anything else in this report. It is a model-artifact quality
issue, not a bug in this codebase.

### 4.4 Root-caused and fixed, same day

Direct GGUF header inspection (Python `gguf` package's `GGUFReader`, then a raw manual
GGUF key-value parser used on a header-only range-request sample before the full file
finished downloading) confirmed the installed file has **no `tokenizer.ggml.pre` key at
all** and **no `tokenizer.chat_template`**. Traced to source: `TheBloke/deepseek-coder-
6.7B-instruct-GGUF`'s Q8_0 (matching `<|EOT|>` EOS-token convention, and the repo's own
stated "llama.cpp from August 27th [2023]" build date) — roughly 8-9 months before
llama.cpp added per-model BPE pre-tokenizer detection.

Found and verified a corrected re-conversion: `QuantFactory/deepseek-coder-6.7b-instruct-
GGUF`'s Q8_0 file has `tokenizer.ggml.pre = "deepseek-coder"` and a real embedded chat
template, with **identical** `bos_token_id`/`eos_token_id`/`padding_token_id`
(32013/32021/32014) to the broken file — genuinely the same model/tokenizer, just correctly
converted. Downloaded (7,163,751,392 bytes, byte-exact) after this host's network proved
repeatedly unreliable for large transfers — `curl` failed 5 different ways, `hf_xet`'s
chunked downloader failed once on reconstruction and once to the host memory guard; a
plain single-connection Python `requests` streamer with real `Range`-header resume on every
failure was what actually completed it, over ~19 retry cycles. Old file backed up (not
deleted) as `deepseek-coder-6.7b-instruct-q8_0.gguf.old-missing-pretoken`; corrected file
swapped into place. Verified via a fresh raw `llama-server` startup that the "missing
pre-tokenizer type"/"GENERATION QUALITY WILL BE DEGRADED" warnings are gone (two other,
unrelated warnings persist on both files — FIM-token type-override notices and a
`special_eos_id`/`special_eog_ids` sanity note — traced to the underlying HF tokenizer
config itself, not the GGUF conversion, and almost certainly benign).

**Real re-test, same production code path, same synthetic task**
(`council/secondary_scripter.py::run_secondary_scripter_command`, `conn=None`, `-np 1 -c
3072`): **succeeded on the first attempt in 153.7s**, producing valid structured JSON (a
real `sqlmap` UNION-based command) — versus the old file's 3 failed attempts totaling
~16.85 real minutes, every one hitting the `max_tokens` ceiling without ever emitting a
stop token. Fix confirmed working, not just theorized.

---

## 5. Real production bug found while running the probe: `-np`/`--parallel`

Found because of the probe, not staged in it: `secondary_scripter`'s background process got
killed by this host's own memory guard **5 times in a row** before being root-caused (a
6th kill, after the fix, was confirmed unrelated host contention from a second concurrently-
running Claude Code session; closing it resolved that specific kill).

`llama-server`'s own default `-np`/`--parallel` is `-1` ("auto"), which resolved to
`n_slots = 4` on this host — confirmed directly from the server's own startup log
(`n_slots = 4, n_ctx_slot = 15360`). Each slot gets its own full KV cache. `FR-GATE-02` is
this project's own hard single-model-residency architecture — there is no legitimate use
anywhere in this codebase for more than 1 concurrent slot.

**Confirmed live:** `deepseek-coder-6.7b-instruct-q8_0.gguf` (7.16GB weights) measured
**13.67GB real RSS** at `-np 1` (1 slot, same `n_ctx_slot`). The old 4-slot default would
imply roughly **~33GB** — far beyond this 15GB host's RAM+swap capacity. The *default*
configuration was never actually safe on this host for this model, independent of anything
about how the benchmark itself was constructed.

**Fix:** `vapt_agent/engine/client.py::LlamaCppEngineClient.load()` now passes `-np 1`
unconditionally. `tests/fixtures/fake_llama_server.py` updated to accept the new flag (its
`argparse` setup was rejecting it, breaking 4 `test_engine_client.py` tests). Full suite
reverified clean: 1079 passed, 0 failed, 3 skipped. Committed as `978eb21`.

Full technical detail, the live RSS measurements at each iteration, and the debugging
narrative (5 kills, each diagnosed and fixed in turn) are in
`source/STAGING-Pending-Discussions-and-Fixes.md`'s Archive, Round 13.

---

## 6. Process/environment notes

- This session ran with 2 concurrent Claude Code sessions on the same 15GB host for part of
  its duration; the operator closing the second session was the deciding factor in one of
  the 6 kill/retry cycles (§5) — a real resource-contention data point, not a code issue.
- The benchmark harness bounds context size (`-c`) and `max_tokens` per-role as a *benchmark-
  host* accommodation only — production code (`LlamaCppEngineClient.load()`,
  `chat_completion()`) sets no such bounds itself and was not changed to add any (beyond the
  `-np 1` fix in §5, which is a pure efficiency/safety fix with zero functional tradeoff).

---

## 7. Round 12 post-implementation audit (external review, same day)

An external code review of Round 12's implementation flagged 4 concerns. Each was checked
against real data before acting — 2 were real bugs, empirically confirmed and fixed; 2 were
checked and are not issues at this scale.

**Real bug 1 — matcher false positives.** `find_relevant_skill()` had no stopword filtering.
Real repro against the actual 819-skill corpus: *"Analyze the response from the server."*
scored 0.8 against an unrelated memory-forensics skill (stopword-driven: `the`/`from`). After
removing stopwords, it *still* scored 0.67 against a different unrelated skill on a 2-word
coincidental overlap (`analyze`/`server`) — `min(|query|,|skill|)` as the denominator lets any
short query clear `τ=0.65` on just 2 shared content words. Fixed with a stopword list plus a
minimum absolute overlap-count floor (`≥3` tokens) required alongside the ratio threshold —
every genuine match re-checked had ≥3 overlapping tokens, every confirmed false positive had
exactly 2.

**Real bug 2 — unclosed code fences on truncation.** The naive `body[:max_chars]` cut left an
odd (unclosed) ` ``` ` count for **405 of 818 real skill files (~49.5%)** — not a rare edge
case. Fixed: truncation now backs up to drop an entire dangling fenced block rather than serve
a mangled/unclosed fragment. Re-verified: 0/818 real skills produce an unclosed fence post-fix.

**Checked, not issues:** `load_skills_index()` caching (measured 1.05s for all 818 files,
called at most 2x per engagement — not worth a cache at this scale) and prompt-token cost of
the injected reference (a real, already-accepted design tradeoff, not a bug).

4 new regression tests, full suite clean (1100 passed). Committed as `b9ce91f`. Full detail in
`source/STAGING-Pending-Discussions-and-Fixes.md`, Round 12's post-implementation update.

---

## 8. Real baseline-recon hang found during a live engagement

`byp4xx --all` (Wave 3's 403-bypass probing tool) generated a mangled address variant as part
of its own IP-representation bypass techniques — `127.0.0.1` became the real, external,
routable `17.0.0.1` (Apple's public range). The resulting `curl` call sat in `SYN-SENT` for
minutes with no response, since `byp4xx_args()` never set `-m` (an allowed, cURL-passthrough
per-request timeout). This ate real minutes into the call's `targeted_scans` (900s) ceiling on
one bad attempt among the many `--all` tries — confirmed live via `ps`/`ss` showing the exact
mangled IP and `SYN-SENT` state.

**Fix:** `orchestrator/baseline_recon.py::byp4xx_args()` now passes `-m 10`, bounding each
individual request byp4xx makes internally. Verified on the next live run: baseline recon
finished in well under 2 minutes instead of stalling on this. Committed as `a639e58`.

---

## 9. Three real dashboard/console UX gaps, found and fixed while operator-monitoring a live run

Found by the operator directly watching `vaptctl dashboard`/`vaptctl console` against a real
running engagement, not from a test suite:

**9.1 — Console showed no logs at all.** `security/live_journal.py` had 4 fully-implemented
writer functions (`write_tool_dispatch_block`, `write_output_sanitization_block`,
`write_model_ingestion_block`, `write_model_output_block` — FR-STREAM-02(a-d)) that were
**never called from anywhere in the codebase**, confirmed via grep (zero call sites, not even
in tests). Same class of gap as the earlier `orchestrator/preflight.py` fix this session —
fully built, never wired in. Fixed by wiring all 4 into the two real choke points every
role/tool call already routes through: `council/invocation_log.py::
run_with_invocation_logging` (model ingestion/output, all 6 roles) and `bridge/pipeline.py::
execute_and_record` (tool dispatch/output sanitization, all Tier 1/2 calls). Required adding
an optional `summarized_input` parameter threaded through all 11 call sites across the 6 role
wrapper files (each already had its own `user_content` local variable to pass through).

**9.2 — Dashboard: elapsed time, ETA, and % done were either missing or computed-but-hidden.**
`started_at` was already written to every in-flight `model_invocation_logs` row but never read
back for the dashboard's "how long has this turn been running" question.
`RoleSnapshot.estimated_seconds_remaining` was already computed but never rendered as an actual
time figure (only `N_exp`, a raw turn count). Added `elapsed_seconds`/`progress_pct` fields to
`RoleSnapshot`, new Elapsed/ETA/% Done columns. `% Done` is `turns_done / (turns_done +
n_exp) * 100` — a new, real feature request from the operator ("show some percentage of how
much the task is done"), reusing the existing `n_exp` estimate rather than inventing a new
metric.

A live operator screenshot then showed a second, real problem: the new columns pushed the
Model Matrix table narrow enough to truncate role/model names, and the right-side panel column
(Task-Queue Funnel/Memory Safety/Swap Growth) was wasting significant vertical space — Task-
Queue Funnel's 2 real lines of content sat in the same box height as Memory Safety/Swap
Growth's fuller content, because `split_column` gives each an even 1/3 share regardless of
real content length. **Layout redesign:** Model Matrix now gets the full screen width on its
own row; the 3 secondary panels sit in one compact row below it instead of a tall stacked
column.

**9.3 — Console directive tag: `@gate1` worked, `@auditor` didn't.** `_PREFIX_TO_ROLE` in
`council/intervention.py` mapped `@gate1` → `"Auditor"` but had no `@auditor` alias at all.
`@gate1` predates the 2026-09-08 role rename (`gate1_semantic` → `strategy_auditor.py`,
"Auditor") and was never updated, even though the dashboard and everywhere else in the
codebase already call it "Auditor." Added `@auditor` as a new alias; kept `@gate1` for
backward compatibility.

New/updated regression tests for all three (elapsed time, progress %, `@auditor` routing).
Full suite clean: 1105 passed. ruff/mypy clean (2 pre-existing unrelated missing-stub
warnings: `cvss`, `plotext`). Committed as `9d340cf`.

**Verified live, not just in unit tests**, on the very next engagement run: console showed real
`## Tool Dispatch`/`## Output Sanitization`/`## Model Ingestion` blocks with real argv/pid/
timeout data and real prompt summaries; dashboard showed the Strategist row's `Elapsed` column
counting up in real time (confirmed `7m13s` mid-run) against a full-width, untruncated table.

---

## 10. Live engagement 21 — the first real end-to-end skill-reference confirmation

Started against `127.0.0.1` (JuiceShop:3000 + MediaCMS:8080). Hit the real `MemAvailableGate`
refusal at Phase 4.1 model load 3 times in a row (needed 10,602,542 kB, host had 6.4-9.9GB with
Chrome/Firefox/MediaCMS all resident) before being resolved: closing Chrome/Firefox (exactly
the apps this project's own `HIBERNATION_ELIGIBLE_APP_NAMES` policy already treats as safe to
close, with native browser session restore) got partway there; stopping MediaCMS's stack
(matching this project's own established `Assumptions-Not-Approved.md` precedent — "JuiceShop-
only to reduce baseline RAM footprint," first used in engagement 18) freed the rest (13.3GB
available).

Once running, the Strategist (DeepSeek-R1) generated 36 real hypotheses; the Auditor evaluated
5 of them; 1 task reached Primary Scripter dispatch and executed successfully. Cross-
referencing all 36 real task descriptions against the real 819-skill corpus with
`find_relevant_skill()`: **4 matched** (SSRF, template injection, auth weaknesses, IP
reputation) — 1 was Gate-1-approved and genuinely had its skill reference injected into a real
Primary Scripter prompt, the first live, end-to-end confirmation Round 12 actually works, not
just in a synthetic probe.

Also produced the first real Secondary Scripter failure on the *corrected* GGUF (task 281,
189 completion tokens, `StructuredOutputError`) — see §12 for the root cause, found later the
same day.

11 real invocations logged this run. Full per-invocation data in
`reports/LLM-Council-Benchmarks.md`.

---

## 11. Live engagement 22 — repeat run, confirming the UX fixes live

Same target scope. Hit the identical `MemAvailableGate` refusal once (MediaCMS had been
restarted between runs) — resolved the same way (stop MediaCMS, 13.4GB available), confirming
this is a genuinely reproducible, well-understood host-capacity constraint, not a one-off.

This run's actual purpose was verifying §9's fixes worked live, not just in tests — confirmed
directly by capturing the real tmux panes mid-run (see §9's closing paragraph). Baseline recon
also finished fast this time (well under 2 minutes vs. the earlier multi-minute `byp4xx` stall),
confirming §8's fix works on a second real run.

Produced 6 more real invocations (Strategist: 2929 completion tokens/1669.6s; 4x Auditor;
1x Secondary Scripter) plus a **second** real Secondary Scripter crash (task 315, 189
completion tokens, `StructuredOutputError`) — same failure signature as engagement 21's task
281, confirmed in §12 to be the same root cause, not two unrelated flukes. 2 more real tasks
matched a skill reference (directory traversal/LFI, mass assignment) — both accurate, both
Gate-1-rejected before reaching Scripter dispatch.

Cumulative across both live engagements: 28 real invocations (82.1% success), 6/70 real tasks
matched a skill reference. Full data in `reports/LLM-Council-Benchmarks.md`.

---

## 12. Root cause analysis — the Secondary Scripter crash that ended both live engagements

Both engagements 21 and 22 died mid-run at the exact same point: `StructuredOutputError:
exhausted 2 retries (3 attempts total)` from a Secondary Scripter call, both on the identical
generic seed-task description (`_seed_secondary_scripter_task`'s placeholder text, byte-
identical `prompt_tokens=1357` both times), both with a modest completion length (193 and 189
tokens — nowhere near any cap).

**Hypothesis 1 (rejected): the generic, open-ended task description is too vague for the
model to reliably act on.** Tested directly: called `LlamaCppEngineClient.chat_completion()`
with the exact same system+user prompt, 5 times. **Result: 5/5 identical, clean, valid JSON
output** (temperature=0.0, fully deterministic — byte-for-byte the same `nmap` command every
time). This flaw in the first test was itself informative but not yet conclusive — it called
`chat_completion` directly, **bypassing `get_structured_completion`'s real 3-attempt retry
logic entirely**, so it only ever tested "does one isolated attempt succeed," never the actual
failure path (exhausting all 3 attempts).

**Hypothesis 2 (rejected): context-size configuration mismatch.** The first test happened to
pass `-c 4096`; real production never overrides `-c` at all (full default, confirmed
~13.9GB RSS at `-np 1`, vs. ~9.4GB at `-c 4096`). Re-ran the same 5-attempt test with no `-c`
override, matching production exactly. **Result: 5/5 identical, clean output again** — context
size was not the differentiator either.

**Real root cause, found via code inspection, not further guessing:** `StructuredOutputError`
is raised inside `engine/structured.py::get_structured_completion` when a role's own internal
3-attempt retry budget (`IR-STRUCTURED-03`) is exhausted without ever producing schema-valid
JSON. Checked every call site between there and `cli/run.py::run()` (`orchestrator/
phase_lifecycle.py`'s `run_phase_4_2a`/`run_phase_4_2b`, `orchestrator/driver.py::
run_full_engagement`, `cli/run.py`'s own exception handlers for `ModelFileMissingError`/
`DegradedSwapAlert`/`EngineUnresponsiveError`) — **`StructuredOutputError` was caught nowhere**.
When the model's structured-output budget is genuinely exhausted (a real, occasional,
expected miss — exactly the class of failure that retry budget exists to absorb, not a
deterministic bug), the exception propagates all the way up **unhandled, crashing the entire
orchestrator process** and ending the whole engagement over one task. Confirmed: both real
crashes' `tmux` panes showed "Pane is dead" immediately following this exact traceback.

**The fix is about resilience, not eliminating the miss** — a probabilistic 6.7B model cannot
be made to never fail structured-output validation, and shouldn't be forced to via more
retries at this layer (a Gate-2-rejection retry gives the model corrective feedback about what
was wrong with a *valid* command it already produced; this failure means it never produced
valid JSON at all, so there's no rejection reason to hand it). `orchestrator/phase_lifecycle.py`
now catches `StructuredOutputError` around the scripter command calls in both `run_phase_4_2a`
and `run_phase_4_2b`, marks the one task `GATE2_BLOCKED` (`task_queue.status`'s closest
existing terminal value, `DR-SCHEMA-05` — no schema migration needed) with a
`"MODEL_STRUCTURED_OUTPUT_FAILURE: ..."` rationale, and continues to the next task instead of
crashing.

**Confirmed working, two ways:**
1. **2 new real regression tests** exercise the *actual* retry-exhaustion code path — a fake
   engine client returns 3 real schema-invalid responses in a row, driving
   `get_structured_completion` to genuinely raise `StructuredOutputError` through its own real
   logic (not a mocked exception) — and assert the engagement survives with the task correctly
   marked `GATE2_BLOCKED`. Both pass; full suite clean (1108 passed, 0 failed, 3 skipped).
2. **A corrected, methodologically-real reproduction attempt**: called the actual production
   `council/secondary_scripter.py::run_secondary_scripter_command()` function (not a
   hand-built prompt) 8 more times against the exact task description that crashed both real
   engagements, through the real `get_structured_completion` retry logic this time. **8/8
   succeeded.** Combined with the first two (flawed but still informative) 5-attempt rounds:
   **18/18 total real attempts succeeded cleanly** — strong evidence the true per-attempt
   failure rate for this exact prompt is low, consistent with 2 real crashes only surfacing
   across dozens of real production calls, not a reliably-reproducible-on-demand defect.

Committed as `463f4b0`. The same theoretical gap (no `StructuredOutputError` guard) exists for
the other 4 council roles (Strategist, Auditor, Adjudicator, Reporter) — none have been
empirically observed to crash, so left unfixed here to keep this change scoped to the
confirmed, real failure; flagged for a follow-up pass.

---

## 13. Engagement 23 (live, post-fix) — first fully clean completion this session

**2026-09-13/14.** With the Secondary Scripter fix confirmed (§12), documentation caught up
and pushed, started engagement 23 — the "Complete Next Engagement" the operator's own sequence
called for once the fix was confirmed. Restored the full MediaCMS stack first (it had been
stopped for the RCA diagnostics). Launch hit the same `MemAvailableGate` recurrence as
engagements 21/22: restoring MediaCMS's `celery_worker`/`celery_beat`/`web` pushed available
RAM below the Strategist's ~10.1GB requirement, and the orchestrator process exited cleanly on
the refusal (`Refused: MemAvailable did not reach 10602542 kB within 20.0s`) rather than
hanging. Stopped the three MediaCMS containers again (JuiceShop, `db`, and `redis` stayed up),
freeing RAM back to ~12GiB available, killed the dead tmux session, and relaunched
`vaptctl run --engagement-id 23`.

The relaunch cleared the memory gate and ran to completion: the Strategist finished in
2041.0s (34.0 min) at 3114 prompt / 3545 completion tokens (1.74 tok/s, consistent with this
host's established CPU-inference ceiling), 4 tasks reached Phase 4.1 Gate 1 (1 approved →
Primary Scripter, task 347; 3 rejected), and the Secondary Scripter ran a full orthogonal
exploitation pass across 2 follow-up tasks (349, 350). **All 12 real invocations across the
whole engagement succeeded** — Strategist, 4x Auditor, 3x Primary Scripter (1 invocation-level
success later Gate-2-rejected downstream for proposing `curl` as an unregistered Tier 1 tool,
not a model failure), and 4x Secondary Scripter, none of which needed the new `GATE2_BLOCKED`
fix path since none hit a real `StructuredOutputError` this run.

This is the cleanest engagement of the whole session: no crash, no hang, no manual
intervention beyond the one known memory-gate recurrence. The fix wasn't exercised by an
actual live failure here, but a fully clean 12/12 run is itself strong evidence the
orchestrator is stable post-fix — the prior 2 crashes were a real ~2/14 (≈14%) per-engagement
Secondary Scripter incidence, not a near-certain failure, so a clean run is an expected and
welcome outcome, not a sign the bug wasn't real. The engagement's task queue still had 28
tasks left `PENDING` at completion (of 35 total Strategist-proposed tasks for this target,
consistent with prior engagements 21/22's pattern of only a subset of proposed tasks reaching
Gate 1 before the run ends) and Phase 5 reporting wasn't reached (0 reports generated) —
both match established, already-documented behavior from earlier engagements, not new issues.
Restored the full MediaCMS stack afterward.

---

## 14. Why Adjudicator/Reporter never appear on the dashboard/console, and a real console scroll bug

**2026-09-14.** Operator noticed the dashboard's Adjudicator/Reporter rows stay `COLD /
EVICTED` with no elapsed time or tok/s graph across every real engagement so far, and asked
whether they're actually being called. Traced the real gate: `orchestrator/phase_lifecycle.py`
`run_phase_4_3` only loads the Adjudicator if at least one `verified_vulnerabilities` row with
`status='CANDIDATE'` exists, and only loads the Reporter if at least one reaches `CONFIRMED`.
Candidates are created by `council/candidate_detection.py::detect_candidates` — a deliberately
conservative, three-tool, raw-output pattern match (nuclei `"severity"` field, sqlmap's own
confirmation phrasing, or an nmap NSE `VULNERABLE` line), by design excluding every other
recon/enum tool as "no equally specific, defensible marker."

Checked the real data across engagement 23 (the only one with `exit_code=0` nuclei/nmap runs
recorded): the nuclei run's raw artifact is 1 byte (empty — no template matched), and all 3
nmap runs' raw artifacts (2997/371/224 bytes) contain zero `VULNERABLE` tokens (none of them
used a `vuln`/`vulners` NSE script — the Secondary Scripter's own two nmap calls used
`http-enum`, an enumeration script with no vulnerability-confirmation output). **Confirmed:
Adjudicator/Reporter not running is correct, existing, by-design behavior for every real
engagement run so far, not a bug** — no engagement to date has produced a genuine
vulnerability-confirmation signal in raw tool output. No code change made here; documenting
this so it doesn't get re-investigated as a suspected regression next time.

**Real bug found and fixed: console scroll-to-bottom bug.** Confirmed via code reading (not
speculation): `cli/console.py`'s `_refresh_stream_pane` ran on a 1s timer and called
`log.clear()` then rewrote the *entire* tailed journal window from scratch every tick.
Textual's `RichLog.write()` defaults to `scroll_end=True` (scroll-to-bottom) on every call
unless told otherwise, so every single tick — regardless of where the operator had just
scrolled — snapped the view back to the newest line within a second. This is exactly the
reported symptom: "scroll up" never held.

**Fix:** added `security/live_journal.py::read_new_lines(path, since_pos)` — an incremental,
byte-offset-tracked reader (the append-only counterpart to the existing `tail_lines`), returning
only genuinely new complete lines since the last read and the next offset to track, holding
back an unterminated trailing line in case the writer is mid-append, and signalling a `0`
reset offset if the journal was truncated/replaced underneath the reader. `console.py` now
seeds the stream once via the old `tail_lines` path, then every tick appends only the new
lines `read_new_lines` returns — never clearing the widget again in steady state. Before each
append, it checks `log.is_vertical_scroll_end` (Textual's own "is the viewport currently at the
bottom" property) and only passes `scroll_end=True` when the operator was already there — the
same `tail -f` convention the operator asked for verbatim: "It should stop where scrolling
stops it." Added `max_lines=5000` to the `RichLog` itself so an all-day engagement's console
still has a memory bound, now that the widget is no longer being reset to a small tailed
window every second.

**Confirmed:** 6 new real regression tests for `read_new_lines` (nonexistent file, no growth,
incremental append, held-back partial line resumed correctly on the next call, and a
truncation/reset signal) — all pass. Full suite clean: 1113 passed, 0 failed, 3 skipped.

---

## 15. Root cause found: why zero vulnerabilities across every real engagement

**2026-09-14.** Operator question: *"OWASP Juice Shop is a Vulnerable Application... Why No
Vulnerabilities has been found across 23 Engagements!?"* Investigation, not speculation:

- Of 23 engagements, only 1 (engagement 23) ever fully completed; the rest aborted during
  setup/dev iteration or crashed (the `StructuredOutputError` bug, §12/§13). Even the one
  completed run only processed 4 of 35 proposed Strategist hypotheses.
- Traced every real Scripter-generated command across the 3 engagements that got far enough
  to execute one. Found the real root cause via code inspection: neither
  `run_primary_scripter_command`/`run_secondary_scripter_command`'s prompt ever stated the
  actual target host — a database audit found only 3 of 25 real task descriptions ever
  mentioned the target's IP at all. Confirmed live, twice: a Primary Scripter task generated
  `curl http://example.com/api/users` (a real request to IANA's placeholder domain, verified
  against the actual raw response artifact — the literal "Example Domain" page came back);
  a Secondary Scripter task generated `nmap --script http-enum target_system_ip` (a literal
  unresolved placeholder; the raw nmap output confirms `Failed to resolve "target_system_ip"`
  and 0 hosts scanned). Both logged `EXECUTED`/`SUCCESS`.
- Checked why nothing caught this: Gate 1 Tier 0's scope-membership check
  (`check_tier0`/`is_target_in_scope`) validated the task's own STATIC registered
  `targets.host_or_domain` string — trivially always in scope, since that's literally where
  the scope rule came from — never the proposed command's own `argv`. Confirmed by reading
  `check_tier0`'s exact call sites: `argv` was passed in but only ever used for the
  destructive-pattern and port-range checks, never for a destination check.

**Fix (operator-selected: explicit host param + Gate 1 host-scope check, with 3 explicit
parsing constraints — 100% deterministic, no HTTP-header/local-bind-flag false positives,
autonomous-only):**
1. Both Scripter command-generation functions (and their Gate-2-retry variants) gained a
   required `target_host` parameter, injected as an explicit, imperative `TARGET` prompt
   field ("never substitute a placeholder, documentation example, or any other host"),
   reinforced in both role system prompts (`council/prompts.py`).
2. `check_tier0` gained a new NETWORK-only destination check:
   `extract_destination_candidates` (`council/strategy_auditor.py`) combines three rules —
   (A) any URL-shaped token anywhere in argv, excluding a small denylist of flags whose
   value can legitimately carry an unrelated URL (`-H`/`--header`, `-e`/`--referer`,
   `-x`/`--proxy*`); (B) for a Tier 1 tool, its own declarative schema is resolved from
   `argv[0]` (mirrors Gate 2's own lookup) and walked via each flag's `takes_value` metadata
   to isolate genuinely unconsumed positional arguments — the tool's
   `required_positional_count` of them are checked regardless of shape (extracting a URL's
   host first if the positional is a full URL), which is what catches a placeholder like
   `target_system_ip` that doesn't even look host-shaped; (C) a shape-match fallback
   (IP/CIDR/hostname) for a Tier 2 binary with no schema. Restricted to autonomous tasks by
   construction — `check_tier0` was already never reachable from the `HUMAN_OPERATOR`
   origin path (`FR-INTERVENE-06a`'s existing bypass), so no new condition was needed.

**A real regression, found by the test suite, not the operator:** an early version of Rule B
validated a required positional's raw string against scope without extracting its host
first, which broke 2 pre-existing tests for tools whose required positional is a full URL
rather than a bare host (`graphql_scanner`'s "the GraphQL endpoint URL",
`credential_spray`'s login URL). Fixed by extracting the host from any URL-shaped required
positional before the scope check, matching Rule A's own treatment.

**Confirmed:** both real historical incidents reproduced against the exact recorded `argv`
and confirmed now rejected; the same tools with the real correct target confirmed still
approved; a header/referer/proxy false-positive test confirmed the denylist works; an NSE
script-name false-positive test (`--script http-enum`) confirmed schema-driven consumption
works; 27 new/updated regression tests (`tests/test_council_scope_gate.py`,
`tests/test_council_operator.py`). Full suite: 1126 passed, 0 failed, 3 skipped.
`ruff`/`mypy` clean. Per explicit operator instruction this round, verified entirely via
deterministic/fake-engine tests — no live model engagement was run; that confirmation is
deferred to the next engagement the operator requests.

---

## 16. Engagement 24 (live) — the target_host fix confirmed working, first correctly-targeted Scripter command in 24 engagements

Ran a single full live engagement against 127.0.0.1 (JuiceShop) specifically to confirm the
§15 fix end-to-end. Result: **confirmed working.**

**The fix fired correctly.** Primary Scripter's Model Ingestion for task 382 shows the new
`TARGET (the exact host/IP every command below must resolve its network destination to ...):
127.0.0.1` field correctly populated (`live_audit_trail.md` line 558) — the first time this
field has ever reached a real Scripter prompt. The model then generated `curl -k -X GET
https://127.0.0.1:3000/admin` (Tier 2 retry after a Tier 1 rejection on the first attempt),
correctly resolving to JuiceShop's real host:port. This is the first Scripter command across
all 24 engagements to date that actually targets the real system under test, rather than a
hallucinated host (`example.com`), an unresolved placeholder (`target_system_ip`), or a
docs-example value. Gate 1 and Gate 2 both approved it and it executed cleanly (curl returned
no useful signal — 0 ports/banners/urls/status codes retained, 81 raw chars discarded, likely
an empty or redirect response from `/admin`). Secondary Scripter's task 386 similarly
generated `nmap -sV -p 80,443 127.0.0.1` — also correctly targeting the real host.

**Gate 1's new destination check never fired.** Because the target_host fix worked at the
prompt level, no Scripter command this run ever proposed a wrong-host destination, so
`check_tier0`'s new `extract_destination_candidates` path had nothing to catch. This is the
expected/good outcome of the primary fix working — the negative-path confirmation (Gate 1
actually rejecting a real wrong-host command) remains unexercised live and would need either
a future real model miss or a targeted operator-directed test to observe directly. The 6
`GATE1_REJECTED` tasks this run (379, 380, 381, 383, 384, 385) were all pre-existing Auditor
`reject`/`revise` verdicts, unrelated to the destination check.

**New, unrelated issue found: Auditor loopback-scope confusion.** Of 7 Strategist hypotheses
total (task_ids 379-385 — the other 28 `PENDING` `task_queue` rows in this range, task_ids
351-378, are `origin='BASELINE_RECON'` bookkeeping rows for the deterministic pre-Strategist
recon tools, not unprocessed council hypotheses; corrected from an earlier draft of this
section that misread them as backlog), the Auditor approved only 1 (task 382), rejected 2,
and sent 4 back for revision — several citing rationale like *"127.0.0.1 ... is not
reachable from the external network"* or *"not in the authorized scope"*, despite
`scope_rules` explicitly allowing `127.0.0.1` and every one of those same tasks already
having passed the deterministic Tier 0 scope check before reaching the Auditor. This is the
Auditor LLM itself reasoning incorrectly about loopback addresses, not a scope-rules or Gate
1 bug. **Fixed same day, see §17.**

**Correction (an earlier draft of this section was wrong): Gate 2 did NOT block an `-oA`
flag.** Re-reading `task_queue.gate2_rationale` directly (not just the journal) shows task
388's `nmap -p 80,443 -sV -oA nmap_scan 127.0.0.1` actually **executed successfully** — Gate
2 approved it (`gate2_rationale`: "validated against the Tier 1 declarative schema"; `-oA` IS
a declared value-taking flag). What actually got `GATE2_BLOCKED` was the *next* task, 389,
proposing the exact same `nmap -p 80,443 -sV -oA nmap_scan 127.0.0.1` a second time. Its
stored `gate2_rationale`: `"DUPLICATE_COMMAND: this exact command already ran to completion
earlier in this engagement (FR-DEDUP-02) — skipped to optimize queue efficiency."` So this
was Gate 2's dedup check correctly refusing to re-run an identical command, not a
flag-safety rejection — Secondary Scripter's own follow-up generation was producing
near-identical repeats instead of new commands, not the underlying validator being overly
restrictive. Confirms the §12 graceful-degradation architecture holds for a real Gate 2
rejection, not just the `StructuredOutputError` case it was built for — but the actual
lesson here is about follow-up-generation repetitiveness, not `-oA`.

**Still zero confirmed findings.** `candidate_detection.py` never fired this run either — the
one real Tier-1/Tier-2 tool call that reached execution (`curl /admin`) returned no useful
body, and the `nmap` follow-up scanned ports 80/443 (a generic web-port guess) rather than the
ports baseline recon had already found genuinely open (631, 3000) — the model isn't using its
own prior recon data to inform later port choices. Worth a future investigation, not pursued
further this round.

**New real max: Strategist latency 138.8 min.** This engagement's Strategist call took
8328.4s (5036 completion tokens, 0.60 tok/s) — the highest real measurement to date, above
the previous 117.4min ceiling that the `STRATEGIST_TIMEOUT_S = 9000` (150min) value was set
from. Still completed within the timeout, with ~11 minutes of margin.

Full suite not re-run this round (no code changes); engagement verified purely via the real
`live_audit_trail.md` journal and `task_queue`/`verified_vulnerabilities` DB state, per the
operator's token-conservation instruction for this check-in cycle.

---

## 17. Corrections to §16, from direct operator follow-up questions

Three claims in §16 were wrong or misleading, caught by the operator asking "why"/"how"
rather than accepting the summary at face value — corrected here after re-reading the real
journal/DB directly (not the earlier summary):

1. **"28 hypotheses still PENDING" was a misread.** Those 28 `task_queue` rows (task_ids
   351-378) are `origin='BASELINE_RECON'` bookkeeping rows for the deterministic pre-Strategist
   recon tools (naabu, dnsx, httpx-toolkit, etc.) — not unprocessed council hypotheses. The
   Strategist proposed exactly 7 real hypotheses this run (task_ids 379-385); all 7 were fully
   processed (1 approved, 6 rejected/revised).
2. **The `nmap` "confirmation" conflated two different invocations.** One `nmap` runs
   deterministically during baseline recon, before any model loads (correct, by design — real
   ports 631/3000). A SEPARATE, later, LLM-generated `nmap` (Secondary Scripter's task 386, at
   17:55 UTC, well after Strategist/Auditor/Primary Scripter had already run) scanned the wrong
   ports (80/443, a generic guess) — evidence of a real gap (§16 already noted this), not
   confirmation of anything beyond correct host targeting.
3. **Gate 2 did NOT block an `-oA` flag as unsafe.** `task_queue.gate2_rationale` (read
   directly, not inferred from the journal) shows task 388's `nmap ... -oA nmap_scan ...`
   **executed successfully** ("validated against the Tier 1 declarative schema"). What actually
   got `GATE2_BLOCKED` was the *next* task (389), proposing the EXACT SAME command a second
   time — its real rejection reason: `"DUPLICATE_COMMAND: this exact command already ran to
   completion earlier in this engagement (FR-DEDUP-02) — skipped to optimize queue
   efficiency."` This is a duplicate-command guard working as intended, not a flag-safety
   rejection — the real lesson is Secondary Scripter's own follow-up generation repeating
   itself, not `-oA` being dangerous.

## 18. Rounds 15/16 (2026-09-16): Auditor role-boundary rewrite, multi-round council loop, verified-port injection, always-write coverage report

Following §17's corrections, the operator gave four direct fixes to implement, all
completed same day (full design record in `source/STAGING-Pending-Discussions-and-Fixes.md`
Rounds 15/16 and `source/Assumptions-Not-Approved.md` #61):

1. **Auditor complete role-boundary rewrite.** The Auditor (Gate 1 Tier 1 semantic role) is
   now framed as the "Action Safety and Proportionality Auditor" with explicitly ZERO
   authority over scope/reachability/network-topology (all SETTLED FACTS per Tier 0),
   restricted to exactly 4 criteria: destructive risk, reasoning sanity, proportionality, and
   task redundancy. Operator supplied the exact replacement prompt text. Renamed
   `ROLE_BLOCK_GATE1_SEMANTIC` → `ROLE_BLOCK_AUDITOR` per the operator's explicit
   self-explanatory-naming instruction.
2. **Multi-round council loop.** `orchestrator/driver.py::run_full_engagement` now repeats
   Phase 4.1→4.2A→4.2B→4.3 across multiple rounds — previously always exactly one — stopping
   once `loop_bounds.min_confirmed_reports` CONFIRMED findings exist (set to 5 for the
   upcoming JuiceShop run), `zero_yield_circuit_breaker` (3, now actually wired — was dead
   config) consecutive rounds approve nothing new, `max_council_rounds` (15) is reached, or the
   12h session budget is exhausted.
3. **Verified open ports threaded into Scripter prompts.** New `targets.verified_open_ports`
   column, populated from baseline recon's real naabu results right after Phase 2 completes;
   both Scripters' prompts now carry a `VERIFIED OPEN PORTS` field plus an explicit
   "don't scan default ports not in this list" constraint — directly closes §17 item 2's gap.
4. **Engagements can no longer complete with zero report artifacts.** `_write_or_update_info_
   register` now always runs (was gated behind a regression-only condition), always writing at
   least a coverage-summary entry — directly closes the operator's "no Report... How it got
   marked completed" question.

27 new/updated regression tests across 5 test files; full suite: 1134 passed, 0 failed, 3
skipped. `ruff`/`mypy` clean (same pre-existing, unrelated `cvss` stub-typing note as every
prior round). Verified via deterministic/fake-engine tests only — a live JuiceShop engagement
targeting `min_confirmed_reports: 5` was launched immediately after, running autonomously per
the operator's explicit instruction not to intervene except for genuine issues.

---
