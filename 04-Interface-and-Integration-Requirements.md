# Interface & Integration Requirements — Autonomous Agentic VAPT System

This document defines **wire-shapes only**: exact communication schemas, method signatures,
tag strings, declarative tool schemas, and IPC handoffs. It governs the structural transport
layer across both operating modes: ensuring deterministic parsing and schema validation for
autonomous cycles, while facilitating transparent transport for direct operator commands.
Operational policies, non-destructive safety boundaries, and gating rationale are governed
authoritatively by the Security Specification (`05`).

---

## IR-ENGINE — Local Engine Client (Inference Abstraction)

| ID | Requirement |
|----|-------------|
| IR-ENGINE-01 | Single interface: `load(model_id) -> handle`, `unload(handle) -> bool`, `chat_completion(handle, messages, ...) -> response`, `is_loaded(model_id) -> bool`. No orchestration code calls the underlying engine's HTTP API directly. |
| IR-ENGINE-02 | Default backing: process-level spawn/terminate of `llama.cpp --server` (one model per process). |
| IR-ENGINE-03 | `unload` returns `true` only after OS-level process exit is confirmed (`waitpid`), never on signal-sent alone. |
| IR-ENGINE-04 | Interface implementable by a second backend (e.g. `ollama`) without changing orchestration code above it. |
| IR-ENGINE-05 | Exposed endpoint stays OpenAI-compatible (`/v1/chat/completions`, `/v1/embeddings`) regardless of active backend. |
| IR-ENGINE-06 | Between `unload()` and the next `load()`, poll `/proc/meminfo` `MemAvailable`; MUST NOT proceed until it clears the documented minimum-headroom threshold. Bounded 5s; timeout raises a degraded-swap alert. |

## IR-STRUCTURED — Structured Output Enforcement

Applies to every LLM-to-code handoff: Tier 1/2 payloads, CVSS proposals, Gate 1/3 decisions.

| ID | Requirement |
|----|-------------|
| IR-STRUCTURED-01 | Structured LLM calls pass response_format={\"type\":\"json_object\"} for standard inference backends (llama.cpp, ollama, vLLM). |
| IR-STRUCTURED-02 | Emitted JSON payloads are validated against deterministic Python schemas. In Autonomous Mode, schema adherence ensures pipeline consistency; in Operator-Directed Mode, minor validation or formatting warnings do not block command dispatch or output display. |
| IR-STRUCTURED-03 | On validation failure during autonomous runs, the system retries up to 2 times (3 attempts total). If parsing fails, raw outputs are preserved in execution logs for operator review rather than discarded. |
| IR-STRUCTURED-04 | Per-output-type schemas are their own declarative definitions (not embedded in prompts): Tier 1/2 payloads, CVSS metrics, Gate 1 decisions, Gate 3 decisions. |

## IR-TOOL — Tier 1 Structured Tool Wrappers

| ID | Requirement |
|----|-------------|
| IR-TOOL-01 | Each Tier 1 tool's schema file declares: binary name, resolved path, typed allowed flags, required args, forbidden combinations, timeout-class. `script_runner`'s schema is `{script_body, interpreter, workspace_subdir}` in place of flags/path. |
| IR-TOOL-02 | The Operator's function-calling schema and Gate 2's validator schema are generated from the same declarative file — a single source of truth. |
| IR-TOOL-03 | Fixed timeout classes: **Quick Probes** (`ffuf`/`whatweb`/`nikto`/`curl`/`wafw00f`) = 180s; **Targeted Scans** (`nuclei`/`nmap` default/top-1000/`sqlmap` quick/`gobuster`/`feroxbuster`/`testssl`/`script_runner`) = 900s; **Deep/Full-Range** (`nmap -p-`/`sqlmap` tamper/`masscan` sweeps) = 1800s. Every subprocess streams stdout/stderr non-blockingly so a stall is caught before the hard timeout. |

## IR-BRIDGE — Tier 2 Dynamic Bridge

| ID | Requirement |
|----|-------------|
| IR-BRIDGE-01 | `run_security_command` accepts `{binary: str, args: [str], cwd: str}` — never a raw shell string. |
| IR-BRIDGE-02 | Path-resolution check validates binary availability. In Autonomous Mode, commands are screened to prevent destructive operations against targets (UPDATE, DELETE, DROP, ALTER, filesystem wipes, or DoS tools). In Operator-Directed Mode, commands execute as specified. |
| IR-BRIDGE-03 | Behavioral boundary checks apply prior to subprocess dispatch during autonomous runs to enforce non-destructive parameters. In operator-directed execution, behavioral gates stand down. |
| IR-BRIDGE-04 | Every decision (allowed/rejected + which rule matched) is tagged into `tool_execution_logs`, even for rejected calls. |
| IR-BRIDGE-05 | Rate limits are enforced by queuing/delaying an excess spawn, tracked per-target, rather than rejecting it. |
| IR-BRIDGE-06 | A completed subprocess is classified `network_error` on connection-failure patterns (refused/reset, DNS failure, TLS handshake failure) — distinct from `timeout_hit`. Both classifications feed the failure-based circuit breaker. |

## IR-GROUND — Report Grounding Check

Verifies a finding report's citations before it can leave draft status.

| ID | Requirement |
|----|-------------|
| IR-GROUND-01 | Extracts endpoints, hosts, and parameters from draft text and verifies their presence in raw session evidence to eliminate hallucinated endpoints, highlighting unmatched components for operator confirmation. |
| IR-GROUND-02 | A grounding failure retries up to 2 attempts during automated drafting; unresolved items transition to reports.status = BLOCKED_UNGROUNDED for operator review and confirmation, never silently discarded. |
| IR-GROUND-03 | Applies to `VAPT_FINDING` reports only — `INFO_REGISTER` has no per-finding evidence-citation structure. |

## IR-SANITIZE — Output Sanitization & Provenance Tagging

| ID | Requirement |
|----|-------------|
| IR-SANITIZE-01 | One pluggable parser per tool/output-type, each producing `{ports, banners, urls, status_codes, raw_artifact_ref}`. |
| IR-SANITIZE-02 | Provenance tag strings (<tool_output_untrusted>...</tool_output_untrusted>) are reserved system tokens; raw target output is sanitized to escape or strip literal occurrences of these tags before wrapping. |
| IR-SANITIZE-03 | Every council model's system prompt includes a structural context separation clause treating wrapped tool output strictly as analytical data. This clause MUST NOT trigger ethical refusals, censorship, or blocking on security analysis, exploit synthesis, or operator attack directives. |

## IR-MCP — Burp Suite / Caido MCP Integration

| ID | Requirement |
|----|-------------|
| IR-MCP-01 | MCP server configs are versioned config files, not inline in orchestration code. |
| IR-MCP-02 | Model Context Protocol (MCP) tool output and third-party bridge data flow through the standard provenance pipeline (IR-SANITIZE-02) to maintain consistent context framing across all ingestion channels. |

## IR-EXT — Third-Party Framework Integration

| ID | Requirement |
|----|-------------|
| IR-EXT-01 | `claude-bug-bounty`/`CyberStrike`/`strix` point at the local endpoint via env vars only, no code modification. |
| IR-EXT-02 | Optional methodology sources (priority S) — the council lifecycle functions correctly with none installed. |

## IR-CTRL — Status Output Format

*Namespace note: `IR-CTRL-01`, `IR-CTRL-03`, `IR-CTRL-04`, and `IR-CTRL-05` are formally declared and owned by `13-Implementation-Architecture-Bridge.md` (`IAB-CLI` section), not this document. Only `IR-CTRL-02` is defined here. This document's own requirement count is locked at 30.*

| ID | Requirement |
|----|-------------|
| IR-CTRL-02 | `status` output is available both as a human-readable table (default) and machine-parseable JSON (`--json`), carrying the same underlying data. |

---

## Authority & Conflict Resolution

This document standardizes interface signatures, input/output schemas, IPC boundaries,
and transport contracts. In the event of any discrepancy, ambiguity, or conflict regarding
payload containment, execution restrictions, boundary tags, or tool bridge enforcement, the
**Security, Safety & Compliance Requirements (`05`)** serves as the final and supreme
authority across the entire system.
