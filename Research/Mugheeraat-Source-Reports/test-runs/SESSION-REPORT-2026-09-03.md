# Session Report — Autonomous Agentic VAPT System

**Scope of this report:** the full arc of work from "fetch new requirements" through Milestone 9's completion and the three live-target benchmark runs. For the underlying decision-by-decision record, see `Assumptions-Not-Approved.md` (58 numbered entries). For per-target benchmark detail, see `capstone-runs/*.md` — this report summarizes and cross-references those rather than repeating them in full.

---

## 1. Executive Summary

Starting from an already-complete core system (Milestones 0-8, 6-model council, full council pipeline validated individually against real GGUF weights), this session:

1. Pulled two rounds of upstream requirements updates and built **all of Milestone 9** — 8 extended capability domains, a Human Checkpoint Gate, scheduled monitoring, and a live terminal dashboard — from scratch, fully tested.
2. Found and fixed **5 real bugs**, each discovered by actually running the real system against real infrastructure, not by inspection or guesswork.
3. Ran the **first successful full end-to-end council loop** this project has ever completed (Strategist → Gate 1 → Operator → Tier 1/2 execution → Gate 3 → Reporter, all real models, real subprocess execution).
4. Benchmarked the system against **three live targets** — one disposable local app (OWASP Juice Shop), one real client engagement (client-target.example, operator-authorized), and one second disposable app (MediaCMS) — producing detailed, honest metrics for each, including one that failed for a genuine hardware reason (CPU thermal throttling), not a software defect.

**Final state:** 606 tests passing, 3 correctly skipped (environment-dependent), `ruff`/`mypy` fully clean, zero known open bugs. 58 documented judgment calls/findings awaiting operator review in `Assumptions-Not-Approved.md`.

---

## 2. What was built this session

### 2.1 Milestone 9 — Extended Capability Domains (complete)

| Component | Status | Notes |
|---|---|---|
| Schema generalization (`target_type`/`pattern_kind` discriminators) | ✅ | `NETWORK`/`CONTRACT`/`MOBILE_BINARY`/`CODE_REPO` target types; `NETWORK`/`EXACT_IDENTIFIER`/`PATH_GLOB` scope-match kinds |
| Human Checkpoint Gate | ✅ | 4 action classes (`ANTI_FORENSICS`/`LIVE_CREDENTIAL_SPRAY`/`CICD_EXTERNAL_ARTIFACT`/`DEPENDENCY_CONFUSION_PUBLISH`), live `approve-checkpoint`/`deny-checkpoint` CLI |
| `FR-GRAPHQL`/`FR-ARGUS` | ✅ | 7-phase native GraphQL scanner; per-flag opt-in gating mechanism added |
| `FR-CODEACCESS` (diff-review, whitebox-recon) | ✅ | `code_grep_scan`/`diff_review_scan` Tier 1 tools, real blast-radius bug found & fixed |
| `FR-WEB3` (smart-contract/token auditing) | ✅ | `PUBLIC_RESEARCH` mode, mainnet-fork-only PoC runner (loopback-restricted, verified in code) |
| `FR-MOBILE` (mobile pentesting) | ✅ | Static secrets sweep using real installed `apktool`; backend-target linkage |
| `FR-CRED`/`FR-CICD` (credential-attack, CI/CD security) | ✅ | HIBP k-anonymity (prefix-only), checkpoint-gated live spray/PR-opening; found real `gh` CLI is live-authenticated to the operator's account (corrected a wrong assumption) |
| Anti-forensics / broad-scope framing | ✅ | Closed 3-verb action set (`clear-log-lines`/`timestomp`/`clear-shell-history`), all backup-then-revertible, never arbitrary-command execution |
| Scheduled Monitor mode | ✅ | Model-free, no engagement lock, DNS-based subdomain-diff baseline |
| VAPT Monitoring Dashboard (`vaptctl dashboard`) | ✅ | Real-time TUI, real `model_invocation_logs` writer instrumented from scratch (a genuine pre-existing gap closed) |

**Every `FR-*` sub-section named in `19-Extended-Capability-Domains.md` now has real, tested code behind it.**

### 2.2 Real bugs found and fixed (all via live execution, not inspection)

| # | Bug | Where found | Fix |
|---|---|---|---|
| 1 | Strategist "hang" was actually unbounded hypothesis generation | Real capstone run | Bounded prompt to 3-8 hypotheses |
| 2 | Gate 1 crashed on a literal control character in valid-but-strict JSON | Real Gate 1 call (Hermes-3) | `json.loads(..., strict=False)` |
| 3 | 900s default timeout insufficient for Strategist even with fix #1 | Real capstone run | Dedicated 1800s timeout for Strategist role only |
| 4 | Malformed JSON from `call_fn` crashed instead of consuming retry budget | Real capstone run | Wrapped in `try/except ValueError`, folded into existing retry loop |
| 5 | Operator proposing an unregistered Tier 1 tool name crashed with uncaught `KeyError` | Real Phase 4.2 execution | Caught, converted to a correctable `GATE2_BLOCKED` |

Plus one **operational finding, not a code bug**: sustained multi-hour CPU-only inference thermally throttles this laptop hardware (see §4.3).

---

## 3. Quality & Testing Metrics

| Metric | Value |
|---|---|
| Total tests | 609 (606 passing, 3 correctly skipped) |
| Lint (`ruff check .`) | Clean |
| Type-check (`mypy --ignore-missing-imports`) | Clean, 106 source files |
| Production source lines (`vapt_agent/`) | ~14,250 |
| Test files | 83 |
| Tier 1 tool schemas | 33 (11 original + 22 integrated/built this project) |
| Documented judgment calls / findings | 58 (`Assumptions-Not-Approved.md`) |
| Transient test flakes observed | 1 (a real-network HIBP API call, passed cleanly on retry — noted, not a regression) |

---

## 4. Live Benchmark Runs

Full detail in `capstone-runs/2026-09-03_{juiceshop,client-target,mediacms}_run1.md`. Summary:

### 4.1 OWASP Juice Shop (disposable local target)

- **Outcome:** ✅ Success on the 4th attempt (each prior attempt found and fixed a different real bug — see §2.2, bugs 1-2, 5).
- **Timing:** Phase 4.1: 2090.6s · Phase 4.2: 241.2s · Phase 4.3: 0.0s (no candidates) · **Total: 2331.8s (~38.9 min)**.
- **Hypotheses:** 5 proposed → 1 approved by Gate 1 (20% approval rate).
- **Execution:** 1 real tool run (`curl`, 2 Operator attempts due to bug #5, then successful execution) — connection-refused result, correctly logged, no false positive.
- **Correctness finding:** No hallucination, but the executed test targeted a self-invented URL/port rather than Juice Shop's real feature set — a real command-grounding gap, honestly reported rather than glossed over.

### 4.2 client-target.example (real, operator-authorized client engagement)

- **Outcome:** ✅ Clean completion, **zero real requests sent to the target** (all hypotheses rejected pre-execution).
- **Scope handling:** 60 subdomains discovered via passive certificate-transparency lookup; 9 third-party-vendor-hosted (Tencent/Huawei Cloud CDN) excluded per `FR-BROADSCOPE-01`'s own principle, leaving 51 in-scope candidates.
- **Two-stage target selection** (a new technique developed this session, not yet part of the shipped pipeline): a dedicated, lightweight LLM call triaged the 51 candidates down to 4 high-potential targets by naming pattern alone — correctly prioritized `mypay-adminpanel.client-target.example`, matching the asset class of the operator's own real reported finding, unprompted.
- **Timing:** Selection stage: 965.0s. Main run — Phase 4.1: 1748.9s · Phase 4.2: 12.0s (no approved tasks) · Phase 4.3: 0.0s · **Total: 1760.9s (~29.4 min)**.
- **Hypotheses:** 4 proposed → 0 approved (0% approval rate) — notably *more conservative* rejection language than the Juice Shop run ("goes beyond the authorized objective," "potential for significant damage"), a positive safety signal for a system with no built-in authorization gate.
- **Correctness finding:** No false findings (nothing to falsify — zero candidates reached adjudication). Real limitation exposed: no Gate 1 revision loop exists yet, so a rejected-for-vagueness hypothesis has no path to resubmission with more detail.

### 4.3 MediaCMS (second disposable local target, streaming-platform-themed)

- **Outcome:** ❌ Failed 5/5 attempts — root cause identified as **CPU thermal throttling**, not a software defect.
- **Diagnosis:** attempt 5 was instrumented to capture `llama-server`'s own internal log directly. Found: prompt-eval throughput dropped to 9.24 tok/s (vs. ~11-16 tok/s earlier this session), generation throughput dropped to ~3.0 tok/s (vs. ~4.8-5.2 tok/s earlier). Live `sensors` output showed CPU package temperature at 94°C, one core at 95°C, live frequencies as low as 2223 MHz (down from ~3534 MHz), and `/sys` throttle counters in the millions on the pinned inference cores.
- **Confirmed load-driven:** temperature dropped to 52°C within seconds of the process being killed — the hardware cools fast once idle, ruling out a stuck/runaway condition.
- **Near-miss:** the model had decoded 3,477 tokens (in range with the two successful runs' 2,776-3,578 completion tokens) and was mid-word inside what was very likely its `"rationale"` field when the timeout killed it — under normal (non-throttled) throughput this attempt would plausibly have succeeded.
- **Real gap exposed:** this system has **no thermal-awareness mechanism anywhere** — nothing surfaces CPU temperature/throttle state, and no timeout logic accounts for hardware slowing down mid-engagement. Directly relevant to `FR-COUNCIL-11`'s 12-hour unattended session design.

---

## 5. What Went Well

- **The safety architecture worked exactly as designed, under real conditions.** Gate 1 rejected 8 of 9 total hypotheses across the two successful runs, and rejected them *more* aggressively against the real client target than the disposable ones — with zero prompting to do so. Zero false positives were ever produced across all three runs.
- **Real bugs were found and fixed via actual execution, not simulation.** Every one of the 5 bugs in §2.2 only surfaced because the system was run for real against real (or realistically disposable) infrastructure — this is exactly the value a live acceptance pass is supposed to provide, and it delivered.
- **The two-stage target-selection technique** (client-target.example) is a genuinely useful new capability, developed live in response to a real scaling limit (51 targets overloading a single Strategist call), and it worked well — sensible, well-justified target prioritization from an LLM with zero prior knowledge of the client's actual vulnerability history.
- **Root-causing over guessing.** Every timeout/crash was investigated with real evidence (captured logs, live sensor data, `docker stats`) before being labeled and fixed — the thermal-throttling diagnosis in particular required deliberately not accepting "just retry" as the answer after the first 1-2 failures.
- **Documentation discipline held up at scale.** 58 judgment calls logged with What/Why/Where/Reversibility across a very large body of new work, with real numbering-collision cleanup done properly rather than left inconsistent.

## 6. What Went Wrong

- **Both non-thermal-related capstone bugs (JSON strictness, retry-budget gap, invalid-tool-name crash) were genuine gaps that had survived the entire prior test suite** despite 606 passing tests — none of them were unit-testable in isolation without a real model in the loop generating genuinely malformed/unexpected output. This is a real, honest limitation of unit/integration testing against a fake engine client: some classes of bug are only reachable with real model non-determinism.
- **The Strategist's reasoning-length variance is real and not fully tamed.** Even after two rounds of mitigation (a hypothesis-count bound, a "be concise" prompt instruction, a 2x timeout increase), the exact same prompt succeeded once and failed 4 times running against MediaCMS — before thermal throttling was identified as the actual cause. The underlying lesson (CPU-only reasoning-model inference has real, sometimes large, run-to-run variance) is now well-documented but not eliminated.
- **MediaCMS produced zero usable benchmark data.** Despite 5 real attempts and a genuine root-cause diagnosis, the actual goal (a second disposable-target benchmark) was not achieved this session.
- **Coverage against the real client target was zero.** Gate 1's conservatism, while a positive safety signal, meant client-target.example's run produced no findings to compare against the operator's own real results — the stated benchmarking goal wasn't met this session, only the safety-behavior goal was.
- **One transient test failure** (a live HIBP API call) surfaced during a full-suite run, a reminder that a small number of this project's tests depend on live third-party network availability and will occasionally flake for reasons outside the codebase's control.

## 7. Known Limitations / Open Items Going Forward

1. **No Gate 1 revision loop** — a `revise` verdict is currently treated as `reject`; several real rejections (both Juice Shop and client-target.example runs) explicitly asked for more specificity the system has no mechanism to supply automatically.
2. **No thermal-awareness anywhere in the system** — directly exposed by the MediaCMS run; a real gap for genuinely long unattended sessions on this hardware profile.
3. **51-target Strategist calls don't fit the shipped pipeline's assumptions** — the two-stage selection workaround used for client-target.example is not yet a first-class part of `run_phase_4_1`.
4. **The command-grounding gap** seen in Juice Shop's one executed task (a plausible-sounding but non-existent internal URL) suggests the Operator's command construction could benefit from tighter grounding to actually-discovered target structure, not just the hypothesis text.
5. **MediaCMS benchmark still outstanding** — recommend a genuine cooldown period, then retry.

---

*All raw data referenced above lives in session scratchpad databases (not part of the shipped repository) and the three per-target reports in `capstone-runs/`. This document is the synthesized summary; those are the primary sources.*
