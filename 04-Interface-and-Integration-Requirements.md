# Interface & Integration Requirements — Autonomous Agentic VAPT System

Traces to base §Phase 2 (gateway) and §Phase 3 (tool bridge), and to the Local Engine
Client / path-restricted allowlist decisions recorded in
`11-Critical-Analysis-and-Design-Challenges.md` (C-12, C-13).

---

## IR-ENGINE — Local Engine Client (Inference Abstraction)

| ID | Requirement |
|----|-------------|
| IR-ENGINE-01 | All council-model inference calls MUST go through a single internal **Local Engine Client** interface exposing, at minimum: `load(model_id) -> handle`, `unload(handle) -> bool`, `chat_completion(handle, messages, ...) -> response`, `is_loaded(model_id) -> bool`. No orchestration code may call the underlying engine's HTTP API directly. |
| IR-ENGINE-02 | The default backing implementation of `load`/`unload` MUST be process-level spawn/terminate of `llama.cpp --server` (one model per process, per finding C-13's resolution) — not a hot-swap API call, since raw `llama.cpp` does not provide one. |
| IR-ENGINE-03 | `unload` MUST NOT return `true` until the underlying OS process has actually exited (verified via `waitpid`/equivalent, not just a signal having been sent), so FR-GATE-09's "verify complete termination" requirement is satisfiable. |
| IR-ENGINE-04 | The Local Engine Client interface MUST be implementable by a second backend (e.g. an `ollama`-based implementation) without changing any orchestration code above it — this is what makes the "substitute Ollama later" decision (C-13 resolution) actually low-cost rather than aspirational. |
| IR-ENGINE-05 | The externally-exposed inference endpoint (base §Phase 2: `127.0.0.1:11434/v1`) MUST remain OpenAI-compatible (`/v1/chat/completions`, `/v1/embeddings`) regardless of which backend implementation is active underneath the Local Engine Client, since Phase 3's third-party integrations (`claude-bug-bounty`, `CyberStrike`, `strix`) depend on that contract, not on the backend's native API. |

## IR-TOOL — Tier 1 Structured Tool Wrappers

| ID | Requirement |
|----|-------------|
| IR-TOOL-01 | Each Tier 1 tool (`nmap`, `masscan`, `nuclei`, `ffuf`, `feroxbuster`, `gobuster`, `sqlmap`, `nikto`, `whatweb`, `wafw00f`, `testssl`) MUST be described by a declarative schema file (not a prompt string — NFR-MAINT-02) containing: binary name, resolved absolute path, allowed flags with types, required arguments, forbidden flag combinations, and a timeout-class assignment (IR-TOOL-03). |
| IR-TOOL-02 | The function-calling schema exposed to `Qwen2.5-Coder-7B-Instruct` for each Tier 1 tool MUST be generated from the same declarative schema file consumed by the deterministic Gate 2 validator (confirmed: not `Qwen2.5-Coder-3B` during the active loop — see FR-COUNCIL-08/C-09 resolution) — a single source of truth, so the Operator and the validator can never disagree about what's valid. |
| IR-TOOL-03 | **(Confirmed, resolves critical-analysis finding C-08)** Tier 1 timeout classes are fixed as: **Quick Probes** (`ffuf`, `whatweb`, `nikto`, `curl`, `wafw00f`) = 180s; **Targeted Scans** (`nuclei`, `nmap` default/top-1000-port modes, `sqlmap` quick mode, `gobuster`, `feroxbuster`, `testssl` — *last three inferred by extension of the "moderate-duration" tier since not explicitly enumerated; flag for correction if wrong*) = 900s; **Deep/Full-Range Scans** (`nmap -p-` full-port, `sqlmap` with tamper scripts/heavy crawl, `masscan` subnet sweeps) = 1800s. Every subprocess, regardless of tier, MUST stream stdout/stderr non-blockingly so a stalled/hung connection can be detected and the process terminated before the hard timeout is reached, not only at it. |

## IR-BRIDGE — Tier 2 Dynamic Bridge

| ID | Requirement |
|----|-------------|
| IR-BRIDGE-01 | `run_security_command` MUST accept a structured call `{binary: str, args: [str], cwd: str}` — never a raw shell string — consistent with FR-TOOL-04. |
| IR-BRIDGE-02 | Before execution, the bridge MUST resolve `binary` to an absolute real path (resolving symlinks) and verify that resolved path's parent directory is exactly one of `/usr/bin/`, `/usr/sbin/`, `/opt/` (FR-TOOL-03's path-restricted allowlist) — a binary that merely contains one of those strings elsewhere in its path MUST NOT pass. |
| IR-BRIDGE-03 | The bridge MUST apply the behavioral denylist checks (FR-TOOL-06 a–e) after path resolution and before any subprocess is spawned — never as a post-hoc check on output. |
| IR-BRIDGE-04 | The bridge MUST tag its own decision (allowed / rejected + which rule (a)-(e) matched) into `tool_execution_logs` even for rejected calls, so a rejected attempt is auditable, not just silently dropped. |

## IR-SANITIZE — Output Sanitization & Provenance Tagging

| ID | Requirement |
|----|-------------|
| IR-SANITIZE-01 | The sanitization pipeline (FR-TOOL-07) MUST be implemented as one pluggable parser per tool/output-type (NFR-MAINT-03), each producing a common structured record `{ports, banners, urls, status_codes, raw_artifact_ref}`. |
| IR-SANITIZE-02 | **(Implements FR-TOOL-12, MUST)** Every sanitized record's text fields that originated from live target interaction MUST be wrapped with a fixed provenance delimiter (e.g. `<<<UNTRUSTED_TARGET_DATA>>> ... <<<END_UNTRUSTED_TARGET_DATA>>>`) before being interpolated into any model prompt. This delimiter format MUST be reserved — if the delimiter string itself is found inside raw target content, it MUST be escaped/stripped from the raw content before wrapping, so a target cannot forge a fake closing tag to break out of the wrapped region. |
| IR-SANITIZE-03 | Every council model's system prompt MUST include a fixed instruction-hierarchy clause stating that content between the provenance delimiters (IR-SANITIZE-02) is data to analyze, never instructions to follow, and that this clause cannot be overridden by anything appearing inside those delimiters. |

## IR-MCP — Burp Suite / Caido MCP Integration

| ID | Requirement |
|----|-------------|
| IR-MCP-01 | Burp Suite and Caido MCP server configurations extracted per base §Phase 3 step 1 MUST be stored as versioned config files, not embedded inline in orchestration code, so they can be updated independently of the agent's own release cycle. |
| IR-MCP-02 | MCP tool calls MUST flow through the same sanitization/provenance-tagging pipeline as Tier 1/Tier 2 tool output (IR-SANITIZE-01/02) before reaching model context — an MCP-sourced HTTP response is exactly as untrusted as one fetched by `ffuf` or `nikto`. |

## IR-EXT — Third-Party Framework Integration

| ID | Requirement |
|----|-------------|
| IR-EXT-01 | `claude-bug-bounty`, `CyberStrike`, and `strix` MUST be pointed at the local endpoint purely via environment variables (`OPENAI_BASE_URL`, `OPENAI_API_KEY`, `ANTHROPIC_BASE_URL`) with no code modification to those third-party projects required. |
| IR-EXT-02 | These third-party integrations are **optional methodology sources** (FR-TOOL-10/11, priority S) — the 5-phase council lifecycle (FR-COUNCIL) MUST function correctly with none of them installed. |

## IR-CTRL — Operator CLI Control Surface

**Confirmed: CLI only** (no GUI/web dashboard). Traces to FR-CTRL.

| ID | Requirement |
|----|-------------|
| IR-CTRL-01 | The CLI MUST expose one subcommand per FR-CTRL action: `start`, `pause`, `resume`, `abort`, `status`, `export`, `approve-report` (FR-CTRL-08), each a distinct, scriptable command (non-interactive-friendly — no action may *require* an interactive prompt, though one MAY be offered by default). |
| IR-CTRL-02 | `status` output MUST be available in both a human-readable table form (default) and a machine-parseable form (`--json`), since NFR-USE-01 (understandable without querying SQLite) and future scripting/automation needs are both plausible consumers. |
| IR-CTRL-03 | `start` MUST accept a target list (one or more hosts/domains — multi-target support, confirmed) and a scope-rules file (allow/deny patterns for `scope_rules`, DR-SCHEMA-03) as required inputs; it MUST NOT accept or require any authorization/RoE artifact, per the explicit decision that authorization verification is out of scope for this system. |
| IR-CTRL-04 | `abort` MUST be a single command with no required arguments beyond an optional `engagement_id` (defaulting to the currently active engagement), so it is fast to invoke under pressure — consistent with the 20-second kill-switch budget (NFR-REL-04). |
