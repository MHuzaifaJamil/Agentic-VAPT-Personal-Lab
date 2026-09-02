# Assumptions, Constraints, Dependencies & Non-Goals — Autonomous Agentic VAPT System

---

## AC-ASSUME — Assumptions

| ID | Assumption |
|----|-------------|
| AC-ASSUME-01 | The hardware profile in the base document (§1) — Intel Core Ultra 5 125H, 15.3 GiB RAM, the specific NVMe partition layout, Kali Linux Debian 15.3 rolling release — describes a **different physical machine** than the one this planning session ran on. All paths and hardware-specific tuning in `01`-`07` inherit that assumption verbatim, per explicit operator decision. |
| AC-ASSUME-02 | The operator (Muhammad Huzaifa Jamil) is the sole user of this system. No multi-tenant, multi-operator, or shared-access scenario is assumed anywhere in this requirement set. |
| AC-ASSUME-03 | **The operator has already independently confirmed authorization to test any target given to this system.** The system itself does not verify this (per the explicit out-of-scope decision in `05-Security-Safety-and-Compliance-Requirements.md` §SEC-SCOPE) — but the requirement set only makes sense under the assumption that this precondition is being satisfied *outside* the tool, every time, by the operator. This is the load-bearing assumption behind `RISK-UNBOUNDEDAUTONOMY` in `07-Risk-Register.md`. |
| AC-ASSUME-04 | Kali's rolling-release kernel and driver stack are assumed adequate for sustained, multi-hour AI-inference + security-tool workloads. This is **not verified** by anything in this planning phase — see `RISK-GPUOFFLOAD` and `RISK-THERMAL`. |
| AC-ASSUME-05 | `kali-linux-everything` (or an equivalent install covering the Tier 1 tool list plus the broader arsenal referenced by the Tier 2 path-allowlist) is assumed installed on the target machine. This planning phase does not verify or install it. |
| AC-ASSUME-06 | **(Confirmed, resolves Open Item E)** `09`'s acceptance tests, and `15`'s Milestone 8 full pass, run against a **local, disposable, Docker-based intentionally-vulnerable test lab** — never real/third-party infrastructure. Composition (e.g. OWASP Juice Shop, DVWA, a throwaway network-service container for failure/rate-limit tests) is an implementation-time detail; the confirmed decision is the *category* (local/disposable/Docker), not a fixed app list. |

## AC-CONSTRAINT — Hard Constraints

| ID | Constraint |
|----|-------------|
| AC-CONSTRAINT-01 | Total system RAM is fixed at 15.3 GiB; the entire multi-model council design (single-residency, sequential swap) exists *because of* this constraint, not as a stylistic choice — relaxing it would change fundamental architecture decisions throughout `01`/`02`. |
| AC-CONSTRAINT-02 | All agent-writable state and artifacts are constrained to the NVMe path `/home/mhj/.local/share/vapt_agent/` — `tmpfs`/`/tmp` usage is a hard prohibition (NFR-RES-03), not a preference. |
| AC-CONSTRAINT-03 | The operator control surface is constrained to **CLI only** — no GUI/web dashboard is in scope for this requirement set (confirmed decision). |
| AC-CONSTRAINT-04 | The Phase 4.2 autonomous loop is constrained to a **12-hour global wall-clock budget**, a **30-task-per-target cap**, and a **3-consecutive-zero-yield circuit breaker** (FR-COUNCIL-11) — these are fixed thresholds, not tunable defaults, unless the operator revisits the decision. |
| AC-CONSTRAINT-05 | Tier 2 dynamic tool execution is constrained to binaries resolving inside `/usr/bin/`, `/usr/sbin/`, or `/opt/` (FR-TOOL-03) — this is a hard boundary, not a starting allowlist meant to be expanded ad hoc. |

## AC-DEPENDENCY — External Dependencies

| ID | Dependency | Notes |
|----|-------------|-------|
| AC-DEPENDENCY-01 | `llama.cpp --server` (primary inference engine) | Must support the oneAPI/SYCL backend for Arc iGPU offload — maturity unverified (finding C-05) |
| AC-DEPENDENCY-02 | `ollama` (optional substitute backend) | Only if `llama.cpp`'s SYCL path proves inadequate; requires independent verification of its own Intel backend support before substitution |
| AC-DEPENDENCY-03 | Intel oneAPI Level Zero / SYCL / OpenCL runtime, `i915`/`xe` kernel modules | Driver/module co-activity claim in the base plan should be verified against actual `lsmod` output on the target machine (finding C-06) |
| AC-DEPENDENCY-04 | SQLite3 (WAL-mode capable) | Standard, low-risk dependency |
| AC-DEPENDENCY-05 | `kali-linux-everything` tool suite (`nmap`, `masscan`, `nuclei`, `ffuf`, `feroxbuster`, `gobuster`, `sqlmap`, `nikto`, `whatweb`, `wafw00f`, `testssl`, plus the broader Tier 2 arsenal) | No install/version-pinning policy defined (OPS-MAINT-01) |
| AC-DEPENDENCY-06 | `pandoc` + `wkhtmltopdf` and/or `weasyprint` | Report Markdown → HTML/PDF conversion (FR-COUNCIL-17a); specific converter choice/config is an implementation-phase decision, not fixed here |
| AC-DEPENDENCY-07 | `claude-bug-bounty` toolkit (optional, for MCP configs and methodology templates per FR-TOOL-10/11) and its `CLAUDE.md` (source of `12-Report-Formatting-Rules.md`) | **Currently exists only on this planning session's machine** (`/home/vscysteam/claude-bug-bounty/`), not on the target machine described in `01-ASSUME-01` — see `RISK-CROSSMACHINE` in `07-Risk-Register.md`. This entire requirements document set itself has the same cross-machine gap and needs to be transferred. |
| AC-DEPENDENCY-08 | GitHub (`github.com/MHuzaifaJamil`) | Used for version-controlling this planning documentation, not a runtime dependency of the VAPT system itself. |
| AC-DEPENDENCY-09 | The six council model weight files themselves, per the roster confirmed in decision #55 (`DeepSeek-R1-0528-Qwen3-8B` Q8_0, `Qwen2.5-Coder-7B-Instruct` Q8_0, `Hermes-3-Llama-3.1-8B` Q8_0, `Qwen2.5-Coder-3B-Instruct` Q8_0, `Mistral-7B-Instruct-v0.3` Q8_0, `Ministral-8B-Instruct-2410` Q8_0) | **Nobody's job yet** — acquisition source and exact quantized `.gguf` file were never specified anywhere in `01`-`17`, despite being a hard prerequisite before `15-Implementation-Milestone-Roadmap.md` Milestone 3 can start. Flagged, not resolved — see `10-Decision-Log-and-Open-Questions.md` Open Item F. The roster was specifically chosen to avoid any Hugging Face gated/license-click-through model (the earlier `Llama-3.1-8B-Instruct` choice required one, which the operator does not hold) — but note `Hermes-3-Llama-3.1-8B` is itself a fine-tune derived from Meta's gated Llama 3.1 base weights; NousResearch's own redistribution is not gate-enforced on Hugging Face, which solves the practical download blocker, but Meta's Llama 3.1 Community License terms (attribution, acceptable-use policy) arguably still apply to the derivative regardless of which repo hosts it — a nuance worth a real legal read at acquisition time, not resolved here. |
| AC-DEPENDENCY-10 | Pinned Python dependency manifest (`requirements.txt`/`pyproject.toml`) for Click, PyYAML, the `cvss` library, and an OpenAI-compatible HTTP client | Not yet created — an installation-adjacent detail deliberately left for build time, per this planning phase's own no-install constraint. See `10-Decision-Log-and-Open-Questions.md` Open Item G. |
| AC-DEPENDENCY-11 | **(New — required by `19-Extended-Capability-Domains.md`)** Web3/smart-contract auditing needs **Foundry** (`forge`/`cast`/`anvil`) plus outbound access to a third-party mainnet-fork RPC endpoint (Alchemy/Infura/a local node) — the only tool dependency in this system that calls out to infrastructure not owned by either this system or the client (`FR-WEB3-03`). | Nobody's job yet — same "flagged, not resolved" status as `AC-DEPENDENCY-09`. |
| AC-DEPENDENCY-12 | **(New — required by `19`)** Mobile-app pentesting needs `adb`, `apktool`, `jadx`, and `frida-tools`/`objection` (pip-installed, likely outside the existing `/usr/bin/`,`/usr/sbin/`,`/opt/` Tier 2 allowlist unless installed explicitly into `/opt/`) — plus a physical Android device (preferred over an emulator, per `FR-MOBILE-06`'s RAM-headroom finding) and a physical jailbroken iOS device (no emulator path exists for iOS pinning bypass at all). | Nobody's job yet. |
| AC-DEPENDENCY-13 | **(New — required by `19`)** GraphQL auditing needs `graphw00f`, `clairvoyance`, `graphql-cop`, `gqlmap` (pip-installable) and `wscat` (npm-installable) (`FR-GRAPHQL-02`). | Nobody's job yet. |
| AC-DEPENDENCY-14 | **(New — required by `19`)** CI/CD pipeline security needs `sisakulint` and an authenticated `gh` CLI session (`FR-CICD-02`). | Nobody's job yet. |
| AC-DEPENDENCY-15 | **(New — required by `19`)** Credential-attack tooling needs `cewler` and hashcat rule files for wordlist generation (`FR-CRED-01`) — `theHarvester`/`username-anarchy`/HIBP access are already generic recon-category dependencies. | Nobody's job yet. |
| AC-DEPENDENCY-16 | **(New — required by `19`)** Argus's out-of-band confirmation scanner needs `interactsh-client` (`FR-ARGUS-02`) — its other five scanner scripts are already present in `Actual-Setup/tools/` and need no new dependency. | Nobody's job yet. |
| AC-DEPENDENCY-17 | **(New — required by `19`'s prompt-additions section)** The `client-reverse` technique (request-signing/anti-bot-token reversal) needs a CDP-capable headless browser — Playwright or Puppeteer — for breakpoint-equivalent instrumentation and anti-bot-token minting; a genuinely new Tier 1 tool category (browser instrumentation), not previously in this system's tool list. | Nobody's job yet. |
| AC-DEPENDENCY-18 | **(New — required by `19`'s `FR-WEB3-09`, a later mining sweep)** Smart-contract static/fuzz-testing needs **Slither** (static analysis) and **Echidna**/**Medusa** (property-based/coverage-guided fuzzers) — a distinct testing layer from `AC-DEPENDENCY-11`'s Foundry/RPC dependency, not redundant with it. | Nobody's job yet. |
| AC-DEPENDENCY-19 | **(New — required by `19`'s `FR-WEB3-10`)** `solidity-audit-mcp` (github.com/mariano-aguero/solidity-audit-mcp) — a genuine MCP server for smart-contract auditing, verified real (distinct from a REST-wrapper shortcut), analogous to the existing Caido MCP dependency treatment. | Nobody's job yet — only needed if this MCP integration is actually pursued, same conditional status as Caido's own MCP dependency (`16`). |

## AC-NONGOAL — Explicit Non-Goals for This Planning Phase

These were raised during planning and deliberately excluded, not overlooked:

| ID | Non-Goal | Rationale |
|----|-----------|-----------|
| AC-NONGOAL-01 | Authorization / Rules-of-Engagement verification | Explicit operator decision — out of scope for the system; see AC-ASSUME-03 |
| AC-NONGOAL-02 | GUI or web dashboard control surface | Explicit operator decision — CLI only |
| AC-NONGOAL-03 | Automatic tool-signature/template/CVE-feed freshness | Deferred — `RISK-TOOLDECAY` |
| AC-NONGOAL-04 | Remote/offsite backup of engagement state | Local-only design, consistent with no-cloud-dependency principle |
| AC-NONGOAL-05 | Automatic artifact retention/pruning policy | Deferred — evidence retained indefinitely by default until a deliberate policy decision is made |
| AC-NONGOAL-06 | Multi-tenant / multi-operator support | Single-operator system by assumption (AC-ASSUME-02) |
| AC-NONGOAL-07 | Installing, downloading, or executing any part of this system | This entire document set is a **planning-phase artifact** — no installation or execution has occurred or is in scope for it |
