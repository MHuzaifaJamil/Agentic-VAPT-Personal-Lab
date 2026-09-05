# Tool Reuse, Asset Adaptation & External Integration Requirements — Autonomous Agentic VAPT System

This document specifies the technical integration contracts, script porting rules, bridge implementations, and methodology adaptations derived from external reference assets (`Actual-Setup/`). It establishes binding requirements for adapting standalone utilities, refactoring coupled tools, configuring direct protocol adapters (REST, GraphQL, MCP), and enforcing the **Dual-Mode Execution Architecture** across all adapted tooling.

All security policies, execution boundaries, and operator-override guarantees governing these tools derive authoritatively from the **Security, Safety & Compliance Requirements (`05`)**.

---

## 1. TR-SCRIPT — Tool Scripts Adaptation & Deployment Contract

The system incorporates standalone utilities and refactors coupled tools from the reference toolkit into native Python execution wrappers deployed to the filesystem path allowlist (`/opt/vapt_agent/tools/`).

| ID | Requirement | Priority |
| --- | --- | --- |
| TR-SCRIPT-01 | **Standalone Script Integration:** The system MUST deploy the 28 verified standalone scripts (`auth_session.py`, `banner.py`, `breach_checker.py`, `credential_store.py`, `dashboard.py`, `dom_xss_harness.py`, `h1_mutation_idor.py`, `hai_payload_builder.py`, `hai_probe.py`, `jwt_scanner.py`, `lead_board.py`, `llm_redteam.py`, `mindmap.py`, `oob_listener.py`, `port_scanner.py`, `prompt_safety.py`, `recon_adapter.py`, `safe_http.py`, `sast_scan.py`, `scope_checker.py`, `sneaky_bits.py`, `_spray_http_form.py`, `_spray_oauth.py`, `target_selector.py`, `visual_triage.py`, `waf_encoder.py`, `zendesk_idor_test.py`, `zero_day_fuzzer.py`) directly to `/opt/vapt_agent/tools/` as Tier 2 executable utilities. | M |
| TR-SCRIPT-02 | **Coupled Script Refactoring:** The 15 coupled scripts (`cors_scanner.py`, `crlf_scanner.py`, `eol_check.py`, `h1_idor_scanner.py`, `h1_oauth_tester.py`, `h1_race.py`, `hunt.py`, `intel_engine.py`, `learn.py`, `memory_gc.py`, `multipart_mutator.py`, `nosqli_scanner.py`, `token_scanner.py`, `validate.py`, `waf_response_analyzer.py`) MUST be decoupled from external package imports (`memory.*`, `tools.*`) and refactored to interface natively with this system's SQLite state store and schema models. | M |
| TR-SCRIPT-03 | **Deterministic Scope Checker Engine:** The logic from `scope_checker.py` MUST be integrated into the Council Gate 1 deterministic engine (Tier 0). It MUST enforce strict DNS-suffix anchoring and validate against CIDR, IP, and port-range definitions for autonomous tasks. In Operator-Directed Mode, scope verification yields unconditionally to manual targets. | M |
| TR-SCRIPT-04 | **Tier 1 Structured Candidate Wrappers:** `jwt_scanner.py` (token decoding, signature validation, algorithm confusion tests), `dom_xss_harness.py` (headless browser DOM execution), and `oob_listener.py` (out-of-band interaction correlation) MUST be exposed with declarative Tier 1 JSON schemas defining typed arguments, timeout classes, and execution flags. | M |
| TR-SCRIPT-05 | **Source Code Static Analysis (SAST):** `sast_scan.py` MUST be integrated into the source-code-access domain (`CODE_REPO` target type) as a standalone Semgrep wrapper, executing deterministic AST queries within isolated local repository checkouts. | M |
| TR-SCRIPT-06 | **Reconnaissance & Pre-Filtering Pipeline:** The content-discovery and filtering pipeline modeled in `full_hunt.sh` and `dork_runner.py` (passive recon → crawling → parameter extraction → pattern-based candidate categorization prior to vulnerability-specific tool dispatch) MUST be implemented as the standard task-generation pattern for the Strategist and Operator roles. | M |
| TR-SCRIPT-07 | **Dual-Mode Execution Posture for Tools:** All integrated scripts MUST execute according to active operating mode: in **Autonomous Mode**, operations MUST be strictly non-destructive (discovery reads and benign verification writes only; data drops, schema modifications, and DoS are prohibited); in **Operator-Directed Mode**, scripts execute as parameterized with zero automated refusal or safety gating. | M |

---

## 2. TR-BRIDGE — Protocol Adapters & External Service Bridges

External platforms and intercepting proxies interface via minimal, direct transport adapters rather than heavy runtime dependencies.

| ID | Requirement | Priority |
| --- | --- | --- |
| TR-BRIDGE-01 | **Burp Suite Direct REST Bridge:** The system MUST interact with Burp Suite (`cc-bridge` extension) via direct HTTP REST calls (`[http://127.0.0.1:1337](http://127.0.0.1:1337)`) using standard client libraries (`httpx`/`requests`). No intermediate Node.js MCP bridge client shall be deployed for Burp communication. | M |
| TR-BRIDGE-02 | **GraphQL Direct Endpoint Adapter:** Interfacing with platform GraphQL endpoints (such as public vulnerability disclosure metadata) MUST be implemented via native Python HTTP POST queries, eliminating redundant proxy layers. | M |
| TR-BRIDGE-03 | **Caido MCP Client Adapter:** If Caido integration is enabled via runtime configuration, the system MUST interface with `npx @caido/mcp-server` using the standard Model Context Protocol client specification over stdio/IPC. | S |
| TR-BRIDGE-04 | **Browser Automation Bridge:** Web-based dynamic interaction, anti-bot mitigation analysis, and DOM XSS verification MUST execute via direct Playwright/Puppeteer automation scripts utilizing the Chrome DevTools Protocol (CDP), without reliance on external MCP daemon processes. | M |
| TR-BRIDGE-05 | **Untrusted Content Wrapping on Bridges:** All telemetry, HTTP headers, payloads, and response bodies ingested through REST, GraphQL, MCP, or CDP bridges MUST be enclosed in `<tool_output_untrusted>...</tool_output_untrusted>` boundary tags before model ingestion. | M |
| TR-BRIDGE-06 | **Anti-Censorship Model Ingestion:** Ingestion of target data through bridge adapters MUST NOT trigger model refusals or censorship. Models analyze offensive security data, exploit structures, and vulnerabilities strictly as analytical input. | M |

---

## 3. TR-METHOD — Triage, Planning & Methodology Enforcement

Methodology patterns extracted from operational practice are codified into deterministic validation checklists and council reasoning protocols.

| ID | Requirement | Priority |
| --- | --- | --- |
| TR-METHOD-01 | **Gate 3 Evidentiary Verification Checklist:** Derived from triage validation standards, Gate 3 MUST evaluate candidate findings against mandatory checks: (1) ruling out false-positive patterns (WAF blocks, rate limits, generic 5xx errors, honeypots), (2) verifying proof of impact beyond technical possibility, (3) confirming cross-identity access for IDOR/BOLA, and (4) establishing a verified baseline/attack/diff evidence structure. | M |
| TR-METHOD-02 | **Strategist Assumption-Breaking Heuristics:** The Strategist system prompt MUST incorporate core assumption-testing routines: evaluating trust boundary bypasses, state/timing race conditions (TOCTOU), parsing/normalization order differentials, boundary value extremes, and incidental access capabilities. | M |
| TR-METHOD-03 | **Cluster Hunting & Sibling Mapping:** Upon confirming a vulnerability on an endpoint, the Operator MUST map sibling endpoints within the same module/controller and formulate targeted follow-on tasks to assess blast radius before concluding exploration of that vector. | M |
| TR-METHOD-04 | **Deterministic Report Structuring:** The Reporter MUST generate finding titles matching the deterministic formula: `[Bug Class] in [Exact Endpoint] allows [role] to [impact] [scope]`. Speculative hedging language ("could potentially", "may allow") is strictly prohibited in final findings. | M |
| TR-METHOD-05 | **Adversarial Threat Ingestion Defenses:** The heuristic injection detector MUST monitor ingested tool outputs for Unicode tag smuggling, MCP tool-description line-jumping, and delimiter injection, recording detected anomalies in execution logs without halting testing cycles. | M |

---

## 4. TR-EXCLUDE — Non-Portable Architecture Exclusions

| ID | Requirement | Priority |
| --- | --- | --- |
| TR-EXCLUDE-01 | **Interactive Copilot Commands:** Slash commands (`commands/*.md`) designed for interactive cloud-copilot runtimes are excluded from direct implementation; operator interaction is owned exclusively by the `vaptctl` CLI surface and interactive TUI console. | M |
| TR-EXCLUDE-02 | **Cloud Subagent Prompts:** Subagent prompt configurations (`agents/*.md`) designed for third-party cloud models are excluded; execution logic is owned exclusively by the 6-model dedicated local council. | M |

---

## Authority & Conflict Resolution

This document standardizes functional requirements for tool adaptation, protocol bridge integration, and methodology implementation. In the event of any discrepancy, ambiguity, or conflict between external script behaviors, integration contracts, and system governance mandates, the **Security, Safety & Compliance Requirements (`05`)** serves as the final and supreme authority across the entire system.
