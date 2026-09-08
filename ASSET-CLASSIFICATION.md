# Asset Classification — `Actual-Setup/` and `Standalone-Engine-Reference/`

Answers "have we integrated the valuable parts of these two folders into this
open-source-model system yet?" Produced by reading both folders in full (skills)
or to the depth noted per-file (tools/scripts) and making a port/skip call on
each item. Companion to `16-Actual-Setup-Reuse-and-Integration-Map.md` and
`17-Standalone-Engine-Reuse-and-Comparison.md`, which did the first pass; this
document finishes it.

**Safety note:** every file examined for this pass contained only generic
methodology, placeholder examples (`example.com`, `attacker.example`, fake
tokens), or the operator's own prior tooling logic — no real hostname, secret,
credential, or client-engagement content was found anywhere. Nothing suspicious
to report.

**Scope boundary honored:** `vapt_agent/bridge/tier1/` was left untouched — a
separate, parallel effort owns adding new Tier 1 tools there (in progress:
`jwt_scanner.py`, `oob_listener.py`, `dom_xss_harness.py`). Several files below
are the *same kind* of asset (a scanner meant to become a declaratively-schema'd
Tier 1 tool) and are explicitly deferred to that effort rather than ported here
or duplicated elsewhere — see "Tier 1 candidates, deferred" below.

---

## Part 1 — Skills mined into `vapt_agent/council/prompts.py`

All four skills doc `16` flagged as "not yet mined" were read and mined this
pass (no files created — text inserted into existing `ROLE_BLOCK_*` constants,
embedded JSON "Output schema:" blocks left byte-identical):

| Skill | Read depth | Mined into | What was added |
|---|---|---|---|
| `skills/web2-vuln-classes/SKILL.md` (2447 lines) | Full: lines 1-200, 550-880 (IDOR, broken auth, file upload, GraphQL, LLM/ASI, API misconfig/mass-assignment/JWT). Headers only (all 32 sections) + ~8-line skim per section for 13-32. | `ROLE_BLOCK_STRATEGIST` | Bug-class vocabulary (IDOR, broken-auth sibling-endpoint rule, BFLA, mass assignment, SSRF, SSTI, LFI, deserialization, NoSQLi, race conditions, prompt-injection/OWASP ASI01-10 with "informational alone, must chain" caveat, JWT alg:none/confusion, subdomain takeover) + reasoning heuristics (developer-psychology reverse-engineering, trust-boundary probe, what-if test, chain-don't-stop). |
| `skills/security-arsenal/SKILL.md` (1668 lines) + `METHODOLOGY_CHEATSHEET.md` (112 lines, full) | Headers only for the main file, except lines 1230-1300 read in full. | `ROLE_BLOCK_OPERATOR` | "Always rejected as follow-up" list (missing headers alone, banner disclosure, GraphQL introspection alone, CORS wildcard w/o exfil PoC, open redirect alone, SSRF DNS-only callback, rate-limit gaps on non-critical forms, self-XSS) + the positive submit criterion. |
| `skills/bb-methodology/SKILL.md` (457 lines, full) | Full read. | (folded into Operator/Strategist reasoning heuristics above — no separate insertion needed, content overlapped what security-arsenal/web2-vuln-classes already supplied) | |
| `skills/report-writing/SKILL.md` (532 lines, full) | Full read. | `ROLE_BLOCK_REPORTER` | Writing rules: title formula, ban on "could potentially," executive-summary-leads-with-impact, concrete/actionable remediation rule. |

Verified via `pytest` after each edit (19/19 relevant tests passing at the time).

---

## Part 2 — `Actual-Setup/tools/` (36 scripts: 21 standalone + 15 coupled)

### Ported (new files, with tests)

| Source file | New location | Why |
|---|---|---|
| `tools/safe_http.py` (100 lines, full read) | `vapt_agent/bridge/safe_http.py` + `tests/test_bridge_safe_http.py` | SSRF-safe redirect-following wrapper around `urlopen` — validates every hop's hostname against private/loopback/link-local/metadata ranges before following it. Genuinely reusable hygiene utility. No current call site (every Tier 1/Tier 2 tool is an external subprocess, not a Python HTTP client) — kept ready for the first future code path that does make outbound HTTP calls directly. |
| `tools/sneaky_bits.py` (232 lines, full read) | `vapt_agent/bridge/sneaky_bits.py` + `tests/test_bridge_sneaky_bits.py` | Invisible-Unicode (U+2062/U+2064) encode/decode — the concrete mechanism behind the ASCII-smuggling / ASI08 agent-comms-exploitation risk just mined into the Strategist prompt. Ported functions only (`sneaky_encode/decode`, `variant_encode`, `tag_encode`, `wrap_payload`); dropped the original's standalone CLI (nothing in this project invokes bundled modules that way) and its canned injection-payload corpus (that's `llm_redteam`/`argus`-family scope, see below — deferred, not duplicated). No current call site — kept as a ready detector/encoder for whichever future code path inspects tool output for this technique. |
| `tools/waf_encoder.py` (231 lines, full read) | `vapt_agent/bridge/waf_encoder.py` + `tests/test_bridge_waf_encoder.py` | Pure multi-layer payload-encoding variants (URL/unicode/HTML-entity, SQL inline-comment splitting, case mixing, operator substitution, null-byte/whitespace tricks, base64-wrapped XSS) — no network calls. Ported as importable functions plus one `encode_variants()` aggregator, CLI dropped for the same reason as above. No current call site — kept for a future Operator capability or Tier 2 script that composes bypass variants programmatically. |

All three new modules + their tests pass `pytest`, `ruff check`, and `mypy --ignore-missing-imports` (see Verification below).

### Tier 1 candidates — integrated 2026-09-03 (follow-up pass)

These were originally flagged below as deferred "to the parallel Tier1-
integration effort" on the assumption another pass would fold them in
alongside `jwt_scanner.py`/`oob_listener.py`/`dom_xss_harness.py`. That
effort's scope had already been fixed to exactly those three tools and had
already finished by the time this was re-checked — these six were never
actually integrated. A follow-up pass read all six in full (none contained
real client/engagement data — all use placeholder domains: `example.com`,
`evil.example`, `attacker.example`, `target.com`) and closed the gap,
following the exact `bundled: true` Tier 1 architecture the prior effort
established.

| File | New location | Why |
|---|---|---|
| `tools/llm_redteam.py` (244 lines, full read) | `vapt_agent/bridge/tier1/tools/llm_redteam.py` + `bridge/tier1/schemas/llm_redteam.yaml` + `tests/test_tier1_llm_redteam.py` | Ported as a Tier 1 tool, same `argus` family as jwt/oob/domxss. `default_timeout_class: targeted_scans` (up to 11 sequential payloads * default 30s timeout = 330s worst case, exceeds `quick_probes`' 180s budget). |
| `tools/cors_scanner.py` (261 lines, full read) | `vapt_agent/bridge/tier1/tools/cors_scanner.py` + `bridge/tier1/schemas/cors_scanner.yaml` + `tests/test_tier1_cors_scanner.py` | Ported as a Tier 1 tool. Its only dependency beyond stdlib, `from tools.safe_http import safe_urlopen`, is a drop-in match for the already-ported `vapt_agent/bridge/safe_http.py` (same `safe_urlopen(req, timeout=..., max_redirects=...)` signature) — only the import path needed updating. One dead-code simplification in `classify()` (both branches of a weakness-based condition resolved to the same MEDIUM severity in the source — collapsed to a plain assignment, no behavior change). |
| `tools/crlf_scanner.py` (191 lines, full read) | `vapt_agent/bridge/tier1/tools/crlf_scanner.py` + `bridge/tier1/schemas/crlf_scanner.yaml` + `tests/test_tier1_crlf_scanner.py` | Ported as a Tier 1 tool, same `safe_http` drop-in fix as above. **Real bug found and fixed during integration testing**: `_send()`'s exception handling was written assuming urllib raises `ValueError` for a raw `\r\n` in a URL (one of the 9 CRLF payload variants uses a literal `\r\n`), but on this Python it's `http.client.InvalidURL` — not a `ValueError` subclass — so that payload variant crashed the whole scan instead of gracefully recording "no injection"; now also caught explicitly. |
| `tools/nosqli_scanner.py` (209 lines, full read) | `vapt_agent/bridge/tier1/tools/nosqli_scanner.py` + `bridge/tier1/schemas/nosqli_scanner.yaml` + `tests/test_tier1_nosqli_scanner.py` | Ported as a Tier 1 tool, same `safe_http` drop-in fix as above. `default_timeout_class: targeted_scans` (the `$where` time-based-blind confirmation deliberately sleeps the backend 5s, plus ~10 requests each budgeted by `--timeout`, default 20s). |
| `tools/visual_triage.py` (173 lines, full read) | `vapt_agent/bridge/tier1/tools/visual_triage.py` + `bridge/tier1/schemas/visual_triage.yaml` + `tests/test_tier1_visual_triage.py` | Ported as a Tier 1 tool. Unlike `dom_xss_harness.py`'s missing-Playwright case, its preferred (`eyewitness`) and third-choice (`httpx -screenshot`) screenshotters **are** present on this machine — but the installed `httpx` binary is confirmed to be the unrelated Python-httpx HTTP-client CLI, not ProjectDiscovery's httpx, so `--tool httpx` will fail here even though `shutil.which("httpx")` finds something; `eyewitness` (the real Red Siege tool, and the default highest-priority pick) works correctly and is what the real end-to-end test exercises. `aquatone` is not installed. |
| `tools/waf_response_analyzer.py` (920 lines, full read) | `vapt_agent/bridge/waf_response_analyzer.py` (plain module, **not** a Tier 1 tool) + `tests/test_waf_response_analyzer.py` | Judgment call, not a straightforward port: its 3-mode CLI (`--calibrate` against a live URL, `--classify`/`--diff` on local files only) doesn't fit Tier 1's one-schema-per-tool model, and 2 of its 3 modes never touch the network at all — it's an analysis library the old toolkit's `bypass_403.sh` shelled out to, not a scanning action the Operator would decide to "run against a target" the way it decides to run nmap or cors_scanner. Ported as an importable module (same treatment as `sneaky_bits.py`/`waf_encoder.py`): CLI dropped, all classes kept including the network-touching `BaselineSampler.calibrate()`. **No current call site, but directly relevant to FR-COUNCIL-14's Gate 3 false-positive checklist** ("rule out a WAF/firewall block page") — `ResponseClassifier.classify()` is ready-made evidence-backed machinery for that exact check, for whichever future Adjudicator/Gate3 code path wires it in. |

All six new/updated modules + their tests pass `pytest`, `ruff check`, and
`mypy --ignore-missing-imports` (390 tests total, up from 349 before this
pass — see Verification below).

### Ported (2026-09-03, second follow-up) — `zero_day_fuzzer.py`

Previously left "honestly unclassified" below (flagged rather than guessed at, given the earlier pass's time budget). Read in full (597 lines, only generic placeholder examples throughout — `example.com`/`evil.com`/`target.com`, no real client/engagement data) and judged genuinely valuable: it covers 6+ vulnerability classes (HTTP method tampering/XST, Host-header injection, CORS misconfig, missing security headers, path traversal, CRLF injection, open-redirect bypasses, 403 bypass, plus `--deep`-only prototype pollution and cache poisoning) that no other integrated tool covers as a single sweep.

| File | New location | Why |
|---|---|---|
| `tools/zero_day_fuzzer.py` (597 lines, full read) | `vapt_agent/bridge/tier1/tools/zero_day_fuzzer.py` + `bridge/tier1/schemas/zero_day_fuzzer.yaml` + `tests/test_tier1_zero_day_fuzzer.py` | Ported as a Tier 1 tool (10th `bundled: true` addition). Logic preserved verbatim; only functional change is `--findings-dir` (new, exposed from the class's existing `findings_dir` constructor param): the original computed its on-disk output path as two directories up from `__file__`, assuming a specific toolkit layout — as a project-bundled Tier 1 tool `__file__` resolves inside the installed package tree instead, the wrong (and possibly unwritable) place to write engagement artifacts. Now defaults to a tempfile-safe location; Tier 1's own raw-stdout capture (DR-ARTIFACT-01/02) is the evidence of record regardless, so the script's own JSON/text output is a best-effort secondary copy. `default_timeout_class: targeted_scans`, upgraded to `deep_full_range` on `--deep` (adds two more test passes, and 403-bypass alone can reach ~17 requests per candidate path across up to 8 paths). |

This module + its tests pass `pytest`, `ruff check`, and `mypy
--ignore-missing-imports` (399 tests total, up from 390 before this pass —
see Verification below).

### Skipped — not applicable to this project's architecture or engagement model

| File | Read depth | Why |
|---|---|---|
| `tools/prompt_safety.py` (24 lines, full) | Full | `delimit_untrusted()` duplicates this project's existing, more robust `bridge/sanitize.py::wrap_untrusted()` (IR-SANITIZE-03 provenance tagging). Redundant. |
| `tools/credential_store.py` (93 lines, full) | Full | `.env`-based `CredentialStore` class for authenticated multi-tool sessions. No integration point in this project's task/argv-based Tier 1/Tier 2 execution model (each tool invocation is a fresh subprocess, there's no persistent "session" concept to hand credentials to). |
| `tools/auth_session.py` (docstring) | Docstring | Session/credential plumbing for authenticated hunting across many of the old toolkit's tools, assuming a shared long-lived session. Same gap as `credential_store.py` above — **flagged as a genuine future feature gap** (authenticated-target testing) rather than force-ported without an integration point; would need an `orchestrator/`-level session concept, out of this pass's scope. |
| `tools/port_scanner.py` (docstring) | Docstring | Non-HTTP service discovery via naabu/smap. Redundant with nmap (`-sV`) already in Tier 1 — matches doc `16`'s prior flag. |
| `tools/target_selector.py` (docstring) | Docstring | HackerOne public bounty-program selector. Wrong engagement model — this project's targets are operator-provided at `vaptctl start`, not discovered from a bounty-platform directory. |
| `tools/hai_probe.py` (docstring) | Docstring | Fingerprints HackerOne's own "Hai" AI Copilot product specifically. Not applicable to an arbitrary VAPT target. |
| `tools/h1_mutation_idor.py` (docstring) | Docstring | One-off HackerOne report-mutation IDOR test tied to that platform's own report API. Too narrow/platform-specific to generalize. |
| `tools/zendesk_idor_test.py` (docstring) | Docstring | One-off Zendesk-specific IDOR tester. Same reasoning as above. |
| `tools/banner.py` (docstring) | Docstring | ASCII terminal branding for the old toolkit's CLI. This project's `vaptctl` has no such requirement anywhere in `01`-`18`; cosmetic, not applicable. |
| `tools/mindmap.py` (docstring) | Docstring | Mermaid mindmap generator for a human hunter's visual planning. This project's workflow is autonomous/model-driven, not a human reading a mid-session mindmap. |
| `tools/lead_board.py` (docstring) | Docstring | JSONL lead-tracking ledger tied to the old toolkit's `memory/leads` directory conventions. This project's SQLite schema (`discovered_entities`, `task_queue`, `verified_vulnerabilities`) already serves the same purpose. Redundant. |
| `tools/dashboard.py` (docstring) | Docstring | Live TUI dashboard. Directly conflicts with this project's own confirmed non-goal (no GUI/dashboard — `vaptctl status` is the CLI-only equivalent). |
| `tools/recon_adapter.py` (docstring) | Docstring | Normalizes the old toolkit's own `recon/<target>/` flat-file directory format. This project's Tier 1 tools write to the artifacts index / SQLite instead — no matching directory structure to adapt. |
| `tools/hai_payload_builder.py` (docstring) | Docstring | 726-line payload library (NoSQLi/SSTI/cmd-injection/MFA/SAML/smuggling/WebSocket) + an LLM-injection generator that itself wraps `sneaky_bits` (already ported above, no unique value left in this file beyond what's now covered). The payload-string half overlaps heavily with `security-arsenal`/`web2-vuln-classes`, already mined into prompts in Part 1; nothing in this project's typed/structured Tier 1/Tier 2 execution model consumes a bulk free-text payload library directly. Low marginal value given time budget — not ported. |
| `tools/_spray_http_form.py`, `tools/_spray_oauth.py` (docstrings) | Docstring | Bespoke credential-spray scripts. Redundant with this project's existing `FR-TOOL-06a` (`allow_brute_force`-gated hydra/medusa/etc. as recognized Tier 2 binaries) — a parallel Python reimplementation adds no capability. |

### `Actual-Setup/tools/` — 15 "coupled" scripts (doc `16`'s list; docstring-depth only, none previously examined)

| File | Verdict | Why |
|---|---|---|
| `cors_scanner.py`, `crlf_scanner.py`, `nosqli_scanner.py` | **Integrated as Tier 1 tools** | See table above — moved there to avoid duplication. |
| `waf_response_analyzer.py` | **Integrated as a plain importable module** (not Tier 1) | See table above — moved there to avoid duplication. |
| `eol_check.py` | Skip, low priority (not ported) | Pure-stdlib EOL/lifecycle lookup against endoflife.date for `product=version` fingerprint pairs. Genuinely useful (EOL software is a real severity argument) and self-contained, but has no current producer of `tech=version` fingerprints in this project's architecture and adds its own live-network-dependency test surface; not ported this pass given time budget — a reasonable future candidate. |
| `h1_idor_scanner.py`, `h1_oauth_tester.py`, `h1_race.py` | Skip, not applicable | All three are HackerOne-report/account-specific (Account A/B token pairs against H1's own GraphQL API, H1's own OAuth/2FA flows, H1 bounty-double-spend races). Wrong engagement model entirely — this project targets arbitrary authorized VAPT engagements, not the HackerOne platform itself. |
| `hunt.py` | Skip, not applicable | Master CLI orchestrator chaining the *old* toolkit's own target-selection/recon/scan/report scripts and directory conventions. This project already has its own orchestrator (out of my scope to touch) and `vaptctl` CLI; this file's logic doesn't transfer. |
| `intel_engine.py`, `learn.py` | Skip, redundant/not integrated | CVE/disclosure intel fetchers (GitHub Advisory DB, NVD, HackerOne Hacktivity) keyed to the old toolkit's `hunt-memory` directory and `/intel` command. The intel-fetching idea (map tech fingerprint → recent CVEs) is sound methodology, but wiring it in would need a new Tier 1/Tier 2-style tool registration and a fingerprint producer — same class of gap as `eol_check.py`, not ported this pass. |
| `memory_gc.py` | Skip, not applicable | Rotates/inspects the old toolkit's own hunt-memory JSONL files (`audit.jsonl`, `patterns.jsonl`, `journal.jsonl`). This project's persistent state is SQLite (`vapt_agent/data/schema.sql`, out of my scope to touch) with its own lifecycle — no JSONL files to garbage-collect. |
| `multipart_mutator.py` | Skip, not applicable | Generates parser-confusion multipart-upload variants against a fixed local file for a specific upload endpoint. A genuinely interesting fuzzing technique, but it's an interactive/manual-mutation tool built around a one-off `--file`/`--send` CLI, not a fit for the Tier 1 declarative-schema model or a clear Tier 2 binary equivalent. |
| `token_scanner.py` | Skip, not applicable | Solidity/Rust-Anchor meme-coin rug-pull static analyzer. Out of domain — this project is a web/infra VAPT system, not a smart-contract auditor (that's the separate `web3-auditor`/`token-auditor` toolkit lineage). |
| `validate.py` | Skip, redundant | Interactive 4-gate bug-validation assistant + skeleton HackerOne report generator. This project's Adjudicator/Reporter roles and Gate 1/Gate 2 validators already serve this exact purpose natively in the council architecture (out of my scope to touch — `orchestrator/`/`engine/`). |

### `Standalone-Engine-Reference/` (per doc `17`'s explicit warning: mine techniques, don't import code)

| File | Read depth | Verdict |
|---|---|---|
| `engine.py` (736 lines) | Function/class header survey | Skip — pure multi-provider (Ollama/OpenAI/Anthropic) CLI dispatcher (`cmd_setup`, `cmd_recon`, `cmd_hunt`, etc.) for the standalone toolkit's own config/provider model. Directly conflicts with this project's already-decided single-llama.cpp-engine architecture and existing `vaptctl` CLI. Nothing to mine beyond architecture already rejected in `10-Decision-Log-and-Open-Questions.md`. |
| `brain.py` (2435 lines) | Method-header survey + full read of `_is_noise_finding_line`/`_finding_score` (lines 756-874) | Skip beyond the grounding-check technique already mined (`_ground_report_output`, mined in an earlier pass per doc `17`). The other methods (`_is_noise_finding_line`, `_finding_score`, `_sanitize_exploit_command`, `watchdog_*`, `auto_triage_and_exploit`) are a large, brittle hardcoded noise-filter keyed to the *old* toolkit's exact tool-output strings (specific sqlmap CSV columns, Metasploit `RHOSTS =>` lines, specific nuclei/log4j output text) — not a generalizable technique, and even if it were, it lives in Gate/Adjudicator territory this pass doesn't touch. |
| `agent.py` (1823 lines) | Class/method-header survey only | Skip — ReAct-loop/LangGraph agent orchestration (`ReActAgent`, `ToolDispatcher`, `LoopDetector`, `race_analysis` multi-model racing) for the old toolkit's own multi-cloud-provider design. This is `orchestrator/`/`engine/`-level architecture, explicitly out of my scope to touch, and doc `17` already flags this file's design as conflicting with decisions made in `01`-`17` (this project uses single-model residency, not multi-model racing). No technique here that doesn't require an architecture change outside this pass's boundary. |

---

## Summary

- **3 new files ported** with full test coverage: `vapt_agent/bridge/safe_http.py`, `vapt_agent/bridge/sneaky_bits.py`, `vapt_agent/bridge/waf_encoder.py` (28 new passing tests).
- **1 skill-mining pass completed** (Part 1, prompts.py) — all 4 previously-unmined skills now folded into the Strategist/Operator/Reporter role blocks.
- **6 more files integrated in a follow-up pass** (2026-09-03), closing a gap where they'd been deferred to an effort whose scope had already been fixed elsewhere: `llm_redteam.py`, `cors_scanner.py`, `crlf_scanner.py`, `nosqli_scanner.py`, `visual_triage.py` as new Tier 1 tools; `waf_response_analyzer.py` as a plain importable module (its 3-mode CLI doesn't fit Tier 1's one-schema-per-tool model). One real bug found and fixed during integration testing (`crlf_scanner.py`'s raw-CRLF payload variant crashed on `http.client.InvalidURL`, not the `ValueError` its `except` clause assumed). 41 new passing tests (349 → 390).
- **2 genuine future feature gaps flagged** (not ported, would need architecture this pass doesn't touch): authenticated-session testing (`auth_session.py`/`credential_store.py`), tech-fingerprint-driven intel/EOL lookups (`eol_check.py`/`intel_engine.py`/`learn.py`).
- **1 more file integrated in a second follow-up pass** (2026-09-03): `zero_day_fuzzer.py` (597 lines, previously left unclassified pending a full read) — a multi-vulnerability-class Tier 1 tool covering method tampering/XST, Host-header injection, CORS misconfig, missing security headers, path traversal, CRLF injection, open-redirect bypasses, 403 bypass, and (`--deep`) prototype pollution/cache poisoning. 9 new passing tests (390 → 399). No real client/engagement data found.
- **Everything else** (~25 files across both standalone and coupled sets, plus all three `Standalone-Engine-Reference/` files) is skipped as not applicable to this project's engagement model, redundant with existing Tier 1/Tier 2/SQLite/council mechanisms, or architecture-level material explicitly out of this pass's scope (`orchestrator/`, `engine/`, `data/schema.sql`).
- **No real client/engagement data found anywhere** in either folder during this pass.
