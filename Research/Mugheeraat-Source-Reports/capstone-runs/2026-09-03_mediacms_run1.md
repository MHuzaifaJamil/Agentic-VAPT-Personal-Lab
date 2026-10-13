# Capstone Run Report — MediaCMS (5 attempts, all failed — thermal throttling root cause)

**Date:** 2026-09-03
**Target:** `127.0.0.1` (MediaCMS, a real open-source video/media CMS, `mediacms/mediacms:latest`, full Docker Compose stack — web/migrations/celery_beat/celery_worker/redis/postgres — bound to `127.0.0.1:8080` only)
**Engagement type:** disposable local test-lab benchmark, second target (chosen as a closer thematic match to a streaming-platform client profile than Juice Shop's e-commerce theme)
**Outcome:** **all 5 attempts failed at the Strategist's 1800s timeout.** Root cause identified via direct hardware diagnostics: genuine CPU thermal throttling after several hours of near-continuous heavy inference this session — not a code bug, not the target, and a materially different failure mode than the reasoning-length variance documented in items #45/#54.

---

## 1. Attempt history

| Attempt | Result | Notes |
|---|---|---|
| 1 | Strategist timeout @ 1800s | First attempt against this target. |
| 2 | Strategist timeout @ 1800s | Retry, identical setup. |
| 3 | Strategist timeout @ 1800s | Retry, identical setup — 3 consecutive failures on an otherwise-identical prompt to Juice Shop's (which had succeeded). |
| 4 | Strategist timeout @ 1800s | Operator confirmed continuing to retry. |
| 5 (instrumented) | Strategist timeout @ 1800s, **but real internal progress captured** | `llama-server`'s own verbose log captured directly (a one-off diagnostic, not shipped code) — see §2. |

## 2. Root cause (from attempt 5's captured internal log + live hardware sensors)

- **Prompt processing throughput measured directly:** `n_tokens = 2048, progress = 0.72, t = 221.59s / 9.24 tokens per second` — i.e. ~9.24 tok/s, well below the ~11.27-16.13 tok/s measured earlier in this same session for a similarly-sized prompt (items #38/#54).
- **Generation throughput measured directly:** settled at **~3.0-3.05 tok/s**, roughly half the ~4.8-5.2 tok/s measured earlier this session.
- **Live CPU sensors during the run:** package temperature **94°C** (one core at 95°C), live per-core frequency samples ranging as low as **2223 MHz** (down from a normal ~3534 MHz), and `/sys/devices/system/cpu/cpu*/thermal_throttle/core_throttle_count` showing **millions of accumulated throttle events** specifically on the P-cores this system pins inference threads to (`FR-GATE-03`).
- **Confirmed load-driven, not stuck:** immediately after the process was killed at the 1800s timeout, temperatures dropped to **52°C package / 46-47°C per-core within seconds** — the CPU cools fast once idle, consistent with active thermal throttling under load rather than any kind of runaway/stuck condition.
- **The model was very close to finishing** when killed: 3,477 tokens decoded (comparable to the 2,776-3,578 completion-token range of the two *successful* runs — Juice Shop and client-target.example — in this same session), mid-way through what was very likely the JSON output's `"rationale"` field (`next token: 'ale'`, i.e. spelling out "rationale"). Under normal (non-throttled) throughput this attempt would very plausibly have finished within budget.

**This is a different failure class than items #45/#54's documented reasoning-length variance** — those were about the model choosing to reason for a variable amount of time on different prompt content. This is the *hardware itself* running measurably slower mid-session, on an unchanged prompt, after ~5-6 hours of sustained heavy CPU-bound inference (many capstone attempts, diagnostics, and this same session's own Milestone 9 build/test work).

## 3. What this means for the system going forward

Logged as `Assumptions-Not-Approved.md` #58. Key implications:
- **No thermal-awareness exists anywhere in this system today.** Nothing surfaces CPU temperature/throttle state to the operator, and no timeout/retry logic accounts for "the hardware has gotten slower mid-engagement." A real, unattended 12-hour session (exactly what `FR-COUNCIL-11`'s session budget is designed for) could plausibly hit this same degradation partway through, with the operator having no visibility into why.
- **Not fixed in this session** — this is a hardware/environment finding, not a software defect to patch reflexively. Real options for later, deliberate decision (not decided here): surface CPU temp/throttle state in the dashboard's telemetry; add a pre-flight/in-loop thermal check; or simply document sustained-CPU-inference thermal limits as a known constraint of this hardware profile.
- **Practical fallout for this specific benchmark:** MediaCMS was not successfully run this session. Retrying immediately would very likely fail again for the same reason (heat doesn't dissipate instantly under continued load) — no further retry was attempted; the process was allowed to fail naturally and temperatures were confirmed dropping afterward.

## 4. No real tool execution or evidence

`tool_execution_logs`, `verified_vulnerabilities`, `reports`: all empty for this target — the Strategist never produced a usable result in any of the 5 attempts, so Phase 4.2/4.3 never ran.

## 5. Recommendation

Let the hardware cool (confirmed it drops from 94°C to ~52°C within seconds of the load stopping — likely fully idle-baseline within a few minutes) before attempting MediaCMS again. A retry after a genuine cooldown period would be a fair test of whether the *original* Juice-Shop-style success rate (variance-driven, not thermally degraded) applies here too.
