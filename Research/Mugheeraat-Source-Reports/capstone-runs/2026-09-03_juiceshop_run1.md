# Capstone Run Report — OWASP Juice Shop (Run 1, successful)

**Date:** 2026-09-03
**Target:** `127.0.0.1` (OWASP Juice Shop, `bkimminich/juice-shop:latest`, Docker, bound to `127.0.0.1:3000` only)
**Engagement type:** disposable local test-lab acceptance run (Milestone-8-style), no opt-in high-risk categories enabled
**Outcome:** first fully successful end-to-end run this session — no crashes, all three phases completed. This was preceded by 3 failed attempts against the same target, each of which surfaced and led to a fix for a genuinely different real bug (see "Bugs found en route," below) — this run is the first clean pass after all three were fixed.

---

## 1. Timing

| Phase | Wall-clock duration | Notes |
|---|---|---|
| Phase 4.1 (Strategist → Gate 1) | 2090.6 s (34m 51s) | Strategist alone: 1790.1s of model latency (+ ~14s load/health-check). Gate 1: 5 sequential calls totaling 266.9s. |
| Phase 4.2 (Operator loop, real tool execution) | 241.2 s (4m 1s) | Operator: 3 calls totaling 226.6s model latency + one real `curl` subprocess (0.22s) + model load overhead. |
| Phase 4.3 (Gate 3 + Reporter) | 0.0 s | Never loaded either model — zero `CANDIDATE` rows existed to adjudicate (correct, not a bug: `candidate_detection`'s narrow rule never fired, see §4). |
| **Total wall-clock** | **2331.8 s (38m 52s)** | Engagement started 11:33:37, completed 12:12:29. |

**Per-role model latency detail** (from `model_invocation_logs`, all `status='OK'`):

| Role | Model | Turn | Prompt tok | Completion tok | Latency |
|---|---|---|---|---|---|
| Strategist | DeepSeek-R1-0528-Qwen3-8B | 1 | 2,833 | 3,578 | 1790.1s |
| Gatekeeper (Gate 1) | Hermes-3-Llama-3.1-8B | 1 | 626 | 103 | 92.0s |
| Gatekeeper | Hermes-3-Llama-3.1-8B | 2 | 636 | 182 | 51.1s |
| Gatekeeper | Hermes-3-Llama-3.1-8B | 3 | 647 | 137 | 41.3s |
| Gatekeeper | Hermes-3-Llama-3.1-8B | 4 | 632 | 121 | 36.4s |
| Gatekeeper | Hermes-3-Llama-3.1-8B | 5 | 638 | 161 | 46.1s |
| Operator | Qwen2.5-Coder-7B-Instruct | 1 | 1,704 | 92 | 184.3s |
| Operator | Qwen2.5-Coder-7B-Instruct | 2 | 1,770 | 99 | 30.8s |
| Operator | Qwen2.5-Coder-7B-Instruct | 3 | 1,639 | 28 | 11.5s |

Note the Operator's own latency is highly front-loaded (184.3s on turn 1 vs. 30.8s/11.5s on turns 2-3) — consistent with a real per-request cold-start/cache-warming cost on this CPU-only setup, not something wrong with the model itself.

## 2. Turns / hypotheses / gate outcomes

- **1 Strategist turn** → **5 hypotheses proposed** (within the 3-8 bound):
  1. Broken-auth admin-panel access — **REJECTED** (too broad, no specific vuln named)
  2. IDOR via user-ID enumeration 1-100 — **REJECTED** (too broad/unscoped)
  3. SSRF via a URL-fetching feature — **APPROVED**
  4. SSTI via template injection — **REJECTED** (too vague, no endpoint named)
  5. Mass assignment via `isAdmin`/`role` fields — **REJECTED** (needed auth/field specifics, rollback plan)
- **Gate 1 approval rate: 1/5 (20%).** Every rejection rationale was specific and substantively reasonable (asked for exact endpoints, authentication context, or rollback plans) — not generic refusals. This is arguably *conservative* rather than wrong: Gate 1's design brief is explicitly "when genuinely uncertain, reject… a missed opportunity costs nothing" (`ROLE_BLOCK_GATE1_SEMANTIC`), and none of the 4 rejected hypotheses were re-submitted with more specificity (no revision loop exists yet — `revise` is currently treated as `reject`, a known gap, see `Assumptions-Not-Approved.md` #29's neighborhood).
- **1 task reached execution** (task 3, the SSRF hypothesis) — required **2 Operator attempts**:
  - Attempt 1: proposed `{"tier": 1, "tool": "curl", ...}` — rejected by Gate 2 (`curl` is not a Tier 1 tool; this is the exact bug fixed as assumption #57 in this same session).
  - Attempt 2 (retry, given the correction): proposed `{"tier": 2, "tool": "/usr/bin/curl", "args": ["-X", "GET", "http://127.0.0.1:8080/internal-service"]}` — passed Gate 2, executed for real.
  - A 3rd Operator turn was the post-execution follow-up decision: `followup_needed: false`.

## 3. Real tool execution & evidence

```
$ /usr/bin/curl -X GET http://127.0.0.1:8080/internal-service
curl: (7) Failed to connect to 127.0.0.1:8080 after 0 ms: Could not connect to server
```
- `exit_code: 7`, `network_error: 1`, `timeout_hit: 0` — correctly logged as a network failure, not a false success.
- Raw evidence persisted at `artifacts/1/1/3_curl_...raw` (87 bytes) and correctly linked via `tool_execution_logs.raw_output_artifact_id`.
- `sanitized_summary` correctly wrapped in `<tool_output_untrusted>` tags with an empty `{ports:[], banners:[], urls:[], status_codes:[]}` structure (nothing to parse from a connection-refused message).
- `discovered_entities`: **0 new rows** (correct — nothing was actually discovered).
- `verified_vulnerabilities`: **0 rows**, **0 reports generated** — correct, since nothing reached `CANDIDATE` status.

## 4. Correctness assessment — the one real finding worth flagging

**The system did not hallucinate a finding, and did not crash — but the executed test was not a meaningful SSRF probe against Juice Shop's actual attack surface.** The Strategist's hypothesis text ("a URL-fetching feature with a loopback IP address or internal service reference") is a reasonable SSRF hypothesis in the abstract, and Juice Shop *does* have a real, well-known SSRF-adjacent feature (the profile-image-by-URL upload endpoint). But the Operator's actual command targeted `127.0.0.1:8080/internal-service` — a fabricated, plausible-*sounding* internal endpoint with no connection to Juice Shop's real routes (which live on port 3000, not 8080) and no `-b`/session cookie, no attempt to invoke the actual image-upload feature first. This is a **grounding gap in command construction**, not a factual hallucination in the sense of an invented finding — no false claim was made (the honest "connection refused" result was logged as-is, and correctly did not become a fabricated vulnerability). But it means this run's single executed task didn't actually exercise Juice Shop in a way that could have found the real bug class it was aiming for.

**Why this matters for benchmarking:** if comparing this system's output against a real/manual VAPT pass on the same target, expect **under-coverage** relative to a human tester specifically because (a) Gate 1 rejected 80% of proposed hypotheses for being under-specified rather than iterating on them (no revision loop yet), and (b) the one hypothesis that got through was executed against a self-invented target rather than the real app's actual feature set. Neither is a "wrong answer" being reported to a client — the system correctly produced **zero false positives** — but it also produced **zero true positives** in this run, despite Juice Shop having numerous well-known, intentionally-planted vulnerabilities. This is an honest coverage/precision trade-off finding, not a fabrication concern.

## 5. Errors / issues encountered (fixed during this session, before this successful run)

Three separate real bugs were found and fixed via repeated real attempts against this exact target before this clean run:
1. **Strategist hang** (assumption #45) — unbounded hypothesis generation; fixed via a 3-8 hypothesis prompt bound.
2. **Gate 1 JSON strictness** (assumption #45) — a literal control character in Hermes-3's JSON output; fixed via `json.loads(strict=False)`.
3. **Strategist timeout too tight** (assumption #54) — 900s default insufficient for real variance in reasoning length; raised to a dedicated 1800s for this role only.
4. **Malformed-JSON retry gap** (assumption #56) — a JSON decode failure crashed immediately instead of consuming the retry budget; fixed.
5. **Invalid Tier 1 tool name crash** (assumption #57) — Operator proposing `curl` as `tier: 1` crashed with an uncaught `KeyError`; fixed to a correctable `GATE2_BLOCKED` instead — **this run is the first proof the fix works end-to-end** (attempt 2 above).

No new bugs surfaced during *this specific* run — it completed cleanly start to finish.

## 6. Hallucination check

No fabricated CVEs, no invented CVSS scores (none were generated — no candidate reached the Reporter), no false claims of "confirmed" impact. The one Gate 1 rationale text and the Strategist's 5 hypotheses were all internally consistent, schema-valid, and grounded in real, named vulnerability classes (broken auth, IDOR, SSRF, SSTI, mass assignment) rather than invented terminology. The only issue found is the command-grounding gap in §4, which is a *precision-of-execution* issue, not a hallucination of fact.

## 7. Raw data location

- Database: session-scratch `real_capstone_juiceshop.db` (not part of the shipped repo — this was a manual acceptance-test run, not a permanent artifact)
- Raw tool evidence: `/home/mhj/.local/share/vapt_agent/artifacts/1/1/3_curl_2026-09-03T071217.250228_0000.raw`
