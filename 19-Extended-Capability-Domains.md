# Extended Capability Domains — Autonomous Agentic VAPT System

Extends the system's core web/network VAPT scope with 9 specialized capability domains mined
from operational practice. Every domain integrates directly into the Council pipeline (Gate 1,
Tier 1/2 tool bridges, Gate 3 Adjudication, and Reporter) under the Dual-Mode Execution Architecture:
autonomous operations are strictly bounded to non-destructive testing (safe reads and verification
writes, barring data drops, schema alters, file wipes, or DoS), while operator-directed commands
execute unconditionally with zero automated refusal or technical boundary interception.

Operational parameters, target identities, and sensitive action checkpoints are managed according
to these domain specifications. In case of any conflict or ambiguity regarding containment or
override precedence, the Security Specification (`05`) serves as the supreme governing authority.

---

## Schema Generalization

Several domains below need a target identity that isn't a host/domain/CIDR. Targets
carry a `target_type` discriminator (`NETWORK` / `CONTRACT` / `MOBILE_BINARY` /
`CODE_REPO`) with type-specific nullable columns, and scope rules carry a
`pattern_kind` discriminator (`NETWORK` / `EXACT_IDENTIFIER` / `PATH_GLOB`). The
deterministic scope-checker MUST branch on both discriminators; this is new code per
kind, not a generalization of the existing CIDR/regex matcher.

## The Human Checkpoint Gate

The system defines a structured Human Checkpoint Gate across five sensitive action classes
(`ANTI_FORENSICS`, `LIVE_CREDENTIAL_SPRAY`, `CICD_EXTERNAL_ARTIFACT`, `DEPENDENCY_CONFUSION_PUBLISH`,
and `PHISHING_MFA_BYPASS`). 

In **Autonomous Mode**, proposed tasks matching these classes log structured checkpoint audit events
and pause unattended execution for operator review to prevent uncoordinated real-world impacts.
In **Operator-Directed Mode**, any matching task or script explicitly commanded or dispatched by
the human operator executes immediately (`approved_via = 'OPERATOR_DIRECTIVE'`, `status = 'APPROVED'`)
with zero pause, no automated refusal, and no technical holding state.

---

## FR-VULNCLASS — Web/API Vulnerability Class Catalog (`web2-vuln-classes`)

Source: `Actual-Setup/skills/web2-vuln-classes/SKILL.md` (2,447 lines, fully mined).
Most of the 32 classes are standard, well-documented bug categories already within a
strong coding model's training and already implicitly covered by the Strategist's
general hypothesis-generation instruction — this section exists to make the coverage
**explicit and named**, not to re-teach textbook material.

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-VULNCLASS-01 | This system's in-scope web/API vulnerability classes MUST include, by name, all 32 classes documented in `web2-vuln-classes/SKILL.md`: IDOR; Broken Auth/Access Control; XSS; SSRF; Business Logic; Race Conditions; SQL Injection; OAuth/OIDC Bugs; File Upload; GraphQL-Specific (superseded in depth by `FR-GRAPHQL` below); LLM/AI Features (MCP/RAG — already covered by this system's own prompt-injection defenses); API Security Misconfiguration; Account-Takeover Taxonomy; SSTI; Subdomain Takeover; Cloud/Infra Misconfigs; HTTP Request Smuggling; Cache Poisoning/Web Cache Deception; MFA/2FA Bypass; SAML/SSO Attacks; Error Disclosure/Debug Endpoints; CSS Injection; LFI/File Inclusion→RCE; Insecure Deserialization; Broken Function-Level Authorization (BFLA); NoSQL Injection; Semantic Confusion (parser/normalization differentials); Header Injection/Response Splitting; XXE; WebSocket Security; Dependency Confusion/Supply Chain (see `FR-VULNCLASS-03`, checkpoint-gated); Padding Oracle & Crypto Misuse. This is a scope statement, not a mandate to embed all 32 classes' full technique detail into any single prompt. | M |
| FR-VULNCLASS-02 | Three specific, non-obvious technique chains identified during mining SHOULD be available as Operator/Reporter reference material (not necessarily embedded verbatim in a system prompt, given context-budget constraints): (a) the ASP.NET ViewState padding-oracle→RCE chain (PadBuster recovers the oracle, `ysoserial.net -p ViewState -g TextFormattingRunProperties` builds the deserialization gadget, a forged `__VIEWSTATE` gives RCE under the app-pool identity); (b) the WebSocket chat-widget cross-role stored-XSS chain (an anonymous visitor's message triggering XSS in the support agent's browser via unsanitized rich-message rendering, not the visitor's own browser — a higher-impact pivot than it looks, since the agent's workstation is often less segmented); (c) CSS-injection-based data exfiltration via attribute selectors (leaking form field values with no JavaScript at all). | S |
| FR-VULNCLASS-03 | **(DEPENDENCY_CONFUSION_PUBLISH action class)** Proving dependency confusion vulnerabilities requires package registration or namespace verification on public package registries (e.g., npm, PyPI, RubyGems, Maven). The system utilizes non-destructive, callback-only validation (DNS or HTTP beacons demonstrating resolution without payload execution) and verifies callback sources against known infrastructure. In Autonomous Mode, proposed package publishing actions are categorized under DEPENDENCY_CONFUSION_PUBLISH and log a checkpoint entry for operator visibility before executing, ensuring no unintended external publishing occurs during unattended runs. In Operator-Directed Mode, publishing or verification tasks commanded directly by the operator execute immediately, recording all registration identifiers and cleanup/unpublish procedures directly into the engagement audit trail. | M |
| FR-VULNCLASS-04 | Three vulnerability classes not present in `web2-vuln-classes`' 32-class catalog MUST also be recognized as in-scope: (a) **timing side-channels** — non-constant-time comparison detectable via per-language grep patterns and confirmable with a statistical timing-oracle test harness (repeated-request latency distribution comparison, not a single-request guess); (b) **XS-Leaks** (cross-site leaks) — frame-count, timing, and error-oracle side channels that infer cross-origin state without a traditional injection vector; (c) **MiniKit/WebView event-spoofing** — forging fake-payment/fake-verification events into a WebView-embedded miniapp (e.g. World App-style miniapps) that trusts client-side event data. | S |
| FR-VULNCLASS-05 | The Strategist's stack→bug-class routing table SHOULD be extended with framework-specific, concrete endpoint/technique pairs where the target's stack is fingerprinted: Spring Boot → check `/actuator/heapdump`/other exposed Actuator endpoints; Laravel → check for an exposed `_ignition` debug endpoint (a known RCE vector); Next.js → check for `__NEXT_DATA__` object leakage of server-side props/secrets. This is more specific than the routing table's generic "Rails→mass-assignment" level of detail — add incrementally as the corresponding framework is actually identified, not embedded as a static block regardless of stack. | S |

## FR-WEB3 — Web3 / Smart Contract Auditing (`web3-audit`, `meme-coin-audit`)

Source: `Actual-Setup/skills/web3-audit/SKILL.md` and `.../meme-coin-audit/SKILL.md`,
both fully mined. Target type: `CONTRACT` — a contract address + chain ID, not a
host/domain.

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-WEB3-01 | The system MUST support `CONTRACT`-type targets covering, at minimum, the 10 named smart-contract bug classes from `web3-audit` (each with severity data from disclosed Immunefi payouts): Accounting State Desynchronization (#1 Critical, 28% of Criticals); Access Control (19% of Criticals); Incomplete Code Path (a "function family" check — verify every sibling of a function, e.g. `mint()`/`deposit()`, has equivalent validation); Off-by-one/boundary conditions (22% of Highs); Oracle/price manipulation (missing staleness checks, single-source oracles, short TWAP windows); ERC4626 vault attacks; Reentrancy (single/cross-function/cross-contract/read-only variants); Flash-loan-funded oracle manipulation; Signature replay (missing nonce/chain-ID in signed hash); Proxy/upgrade issues (storage collision, uninitialized implementation, unrestricted `delegatecall`). | M |
| FR-WEB3-02 | The system MUST support `CONTRACT`-type targets covering the 8 named token/meme-coin bug classes from `meme-coin-audit`: hidden mint/unlimited supply; honeypot/transfer restriction; post-launch fee manipulation; liquidity-pool drain via migration/emergency-withdraw functions; bonding-curve manipulation; Solana authority retention (mint/freeze/update/close authority not revoked); fake renounce/hidden backdoor ownership; sandwich-amplification-by-design (zero-slippage auto-swap, rebase mechanics). | M |
| FR-WEB3-03 | **(New dependency)** Smart-contract testing requires **Foundry** (`forge`/`cast`/`anvil`) and an RPC endpoint for mainnet-fork analysis (`vm.createSelectFork`) — an outbound network dependency to a third-party RPC provider (Alchemy/Infura/local node), unlike every other tool in this system's scope, which targets the client's own infrastructure directly. This MUST be documented in the dependency summary at the end of this document, and the RPC endpoint itself is not a scope-governed target — it's infrastructure this system calls out to, analogous to how the inference gateway is infrastructure this system calls in. | M |
| FR-WEB3-04 | Smart-contract execution and vulnerability validation default to local mainnet-fork or testnet simulations during autonomous assessment to ensure zero unintended on-chain state alteration. In Autonomous Mode, models are strictly restricted from sending state-modifying mainnet transactions. In Operator-Directed Mode, direct interaction with live contracts executes immediately when explicitly commanded and parameterized by the operator. | M |
| FR-WEB3-05 | **(Meme-coin only, dual mode retained deliberately)** CONTRACT targets in meme-coin-audit scope carry a contract_investigation_mode: CLIENT_OWNED (a client's own token contract — standard VAPT posture, where authorization and scope verification reside solely with the operator outside the tool) or PUBLIC_RESEARCH (evaluating a third-party public token for rug-pull risk — passive intelligence gathering). In Autonomous Mode, PUBLIC_RESEARCH is restricted to non-destructive, read-only analysis (on-chain authority/deployer-history queries via block explorers, holder-distribution/LP-lock lookups via third-party APIs like Etherscan, Solscan, DEXTools, Birdeye, and Unicrypt), ensuring passive reconnaissance without unsolicited state mutation. In Operator-Directed Mode, any specific simulation, testnet verification, or analytical command explicitly requested by the operator executes immediately as directed. | M |
| FR-WEB3-06 | The Strategist SHOULD apply `web3-audit`'s pre-dive kill-signal scoring before committing to a deep audit: skip if TVL < $500K or `min(10% × TVL, program_cap) < $10K`; hard-skip if 2+ top-tier audits (Halborn/Trail of Bits/Cyfrin/OpenZeppelin) exist on a simple (<500 LOC) protocol version. | S |
| FR-WEB3-07 | **(Deeper mining pass)** `CONTRACT`-type target coverage MUST also include **DEX/LP-specific attacks**, a category not represented in `FR-WEB3-01/02` at all: pool-creation sniping, liquidity-removal/LP-lock-bypass attacks (distinct from `FR-WEB3-02`'s generic mention), sandwich-attack amplification via zero-slippage auto-swap, concentrated-liquidity position attacks (Uniswap V3/Orca Whirlpool/Meteora DLMM — a narrow-range position, e.g. `tickUpper - tickLower < 200`, is itself a rug-risk heuristic), and pool-migration exploits. | M |
| FR-WEB3-08 | **(Deeper Solana detail)** Solana Token-2022 extension auditing MUST specifically check for a **Permanent Delegate** extension (a delegate that can move any holder's tokens without their consent — the single most severe Token-2022 risk pattern, more severe than the generic "authority retention" already in `FR-WEB3-02`) and a **Transfer Hook** extension (arbitrary program logic runs on every transfer — a hook that can silently block, tax, or redirect transfers). Both MUST be checked via on-chain queries (`spl-token` CLI / Solscan navigation), not assumed absent. | M |
| FR-WEB3-09 | **(New dependencies)** Smart-contract auditing methodology also depends on a static/fuzz-testing layer distinct from Foundry's PoC-execution role: **Slither** (static analysis, specific detector invocations) and **Echidna**/**Medusa** (property-based and coverage-guided fuzzers). These are a different testing layer, not redundant with Foundry — Foundry proves a specific PoC once a bug is hypothesized; Slither/Echidna/Medusa help discover the hypothesis in the first place. | M |
| FR-WEB3-10 | **(New MCP integration point)** `solidity-audit-mcp` (a genuine, verified MCP server distinct from this system's existing Burp/Caido MCP integrations) wraps Slither + Aderyn + Slang AST + 86 SWC detectors + a gas optimizer into MCP tools (`analyze_contract`, `check_vulnerabilities`, `explain_finding`, `generate_invariants`, `diff_audit`, `audit_project`, `optimize_gas`, `run_tests`, `generate_report`), with a DeFi-specific 10-detector preset. A real MCP dependency for this domain if pursued, not a REST-wrapper shortcut. | S |
| FR-WEB3-11 | The Operator SHOULD prioritize investigation using a 3-tier grep-triage system (Tier 1 = investigate first) when scanning contract source for the 10+3 named bug classes above, rather than treating every grep hit as equal priority — mined from the deeper `web3/03-grep-arsenal.md` reference material. PoC output for any confirmed finding SHOULD follow the Immunefi-style convention of explicit before/after balance assertions in the Foundry test, pinned to a specific forked block (`vm.createSelectFork(..., block)`), for a reproducible, self-contained artifact. | S |

## FR-MOBILE — Mobile Application Pentesting (`mobile-pentest`)

Source: `Actual-Setup/skills/mobile-pentest/SKILL.md`, fully mined. Target type:
`MOBILE_BINARY` — platform + package name + binary artifact.

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-MOBILE-01 | The system MUST support `MOBILE_BINARY`-type targets (Android APK / iOS IPA) under a **runtime-first, never-decompile-first** methodology: install on device/emulator → proxy traffic → drive core business flows manually → if traffic is visible and replayable, treat the recovered API exactly like a `NETWORK` target (register it as a linked row via `backend_target_id` and stop reversing) → escalate to static analysis (`apktool`/`jadx`) and dynamic instrumentation (Frida/`objection`) only when traffic is pinned, encrypted, or absent. | M |
| FR-MOBILE-02 | The system MUST perform a static secrets/endpoint sweep before any dynamic testing — decompile via `apktool`, grep for hardcoded credentials (`api_key\|secret\|password\|token\|Authorization\|Bearer\|client_secret\|private_key` patterns) and base-URL/endpoint strings; internal or staging base URLs never exposed by the web app are explicitly the single highest-value find from this step. | M |
| FR-MOBILE-03 | The system MUST support SSL/certificate-pinning bypass via `objection patchapk` (gadget) as the first path, with targeted Frida hooks on `okhttp3.CertificatePinner.check()` and `TrustManagerImpl.checkTrustedRecursive()` as fallback. | M |
| FR-MOBILE-04 | The system MUST check exported Android components (manifest `exported="true"` + intent-filter + `BROWSABLE` + custom URI scheme) for deeplink injection, and — when a WebView is reached via such a deeplink — enumerate any `@JavascriptInterface`-exposed bridge methods for injection/RCE (API<17 targets specifically), following the documented chain: deeplink → WebView `loadUrl()` → JS bridge → token exfiltration. | M |
| FR-MOBILE-05 | Mobile testing utilities (adb, apktool, jadx, frida-tools, objection) may execute from /opt/ or designated virtual environments configured in the execution environment path. | M |
| FR-MOBILE-06 | **(Hardware constraint, flagged not silently absorbed)** An Android emulator typically needs 2-4+ GB RAM — run alongside a resident council model under the confirmed `Q8_0` roster, this would likely exceed the already-tight post-hibernation headroom (roughly 2.0-4.2 GB worst-case). This system's default for this domain on the confirmed hardware profile MUST be a **physical Android device via `adb`**, not a local emulator; emulator use is a documented degraded/unsupported configuration, not the assumed default. | M |
| FR-MOBILE-07 | Standard mobile N/A criteria serve as advisory guidance during automated triage; findings demonstrating theoretical exposure, configuration drift, or hardening gaps may be retained or promoted via operator console review (--allow-theoretical-findings). | S |

## FR-GRAPHQL — GraphQL API Auditing (`graphql-audit`)

Source: `Actual-Setup/skills/graphql-audit/SKILL.md`, fully mined, backed by the
already-present `Actual-Setup/tools/graphql_audit.sh`. Fits the existing `NETWORK`
target schema unmodified — a GraphQL endpoint is just a URL under an already
in-scope host.

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-GRAPHQL-01 | The system MUST support a 7-phase GraphQL audit against in-scope `NETWORK` targets: introspection abuse (including bypasses — newline injection, fragment tricks, `__type` in place of `__schema`, GET-instead-of-POST, WebSocket-subscription-channel introspection); field-suggestion abuse (typo-triggered "did you mean" schema recovery, manual or via `clairvoyance`); engine fingerprinting via `graphw00f` (engine-specific CVE differences — Hasura auth bypass, Apollo depth issues, Hot Chocolate SSRF-in-federation, WPGraphQL IDOR-proneness); IDOR via direct object access and field-level IDOR (privileged fields readable on an otherwise-owned object); injection via resolver arguments (SQLi via `gqlmap`, NoSQLi via JSON-coerced operator injection); auth-bypass patterns (unauthenticated queries/mutations, deprecated-field auth bypass); subscription abuse (cross-user WebSocket event leakage); and WAF-bypass techniques (content-type switching, GET-based introspection). | M |
| FR-GRAPHQL-02 | **(New dependencies)** `graphw00f`, `clairvoyance`, `graphql-cop`, `gqlmap` (pip-installable) and `wscat` (npm-installable) — all fit the existing Tier 2 path-restricted-allowlist model once installed; no new bridge mechanism is needed, only new allowlist entries and a dependency-manifest addition. | M |
| FR-GRAPHQL-03 | Resource-intensive queries, depth testing, and batching checks are managed in autonomous runs to avoid target degradation. Explicit stress or availability validation executes under direct operator instruction. | M |
| FR-GRAPHQL-04 | The Strategist/Operator SHOULD apply the domain's kill signals before deep GraphQL testing: a 404/410-consistent endpoint is inactive; generic "Unauthorized" with no field suggestions indicates a well-hardened target; a rate limit firing on the second query indicates strong protection and low ROI; an Apollo Federation gateway-only response means the downstream services, not the gateway, are the actual target. | S |

## FR-CICD — CI/CD Pipeline Security (`cicd-security`)

Source: `Actual-Setup/skills/cicd-security/SKILL.md`, fully mined, backed by the
already-present `Actual-Setup/tools/cicd_scanner.sh`. Target type: `CODE_REPO` — an
`owner/repo` identity, not a host/domain.

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-CICD-01 | The system MUST support `CODE_REPO`-type targets covering: GitHub Actions workflow injection via untrusted context variables interpolated into `run:` blocks (`github.event.pull_request.title/body`, `.head.ref`, issue/comment/review/discussion bodies, `workflow_dispatch` inputs); `pull_request_target` misuse (runs with base-repo secrets against attacker-controlled PR head code); secret exfiltration (log echo, DNS-based stealthy exfil); overly broad `GITHUB_TOKEN`/OIDC trust-policy permissions; self-hosted-runner poisoning (public repo + self-hosted runner lets any fork queue jobs on internal infrastructure); dependency confusion/supply chain via unpinned mutable-tag action references; and **AI agent security** (unrestricted AI-agent triggers on a workflow, excessive tool/permission grants to a CI-integrated AI agent, and prompt injection reaching an AI agent via workflow context) — directly relevant given this system is itself an AI agent, making this sub-class doubly applicable: both as a target-side check and as a reminder that this project's own prompt-injection defenses are the same category of concern from the other direction. | M |
| FR-CICD-02 | **(New dependencies and access model)** `sisakulint` (workflow linter) and the `gh` CLI (needs authentication for anything beyond public-log access) are new dependencies. Critically, **the access model is fundamentally different from every other domain**: recon is `git clone`/`gh api` against a repository, not `nmap`/`ffuf` against a host — some checks are genuinely read-only (public workflow files, public run logs, public secret *names*), but the rest is not. | M |
| FR-CICD-03 | **(CICD_EXTERNAL_ARTIFACT action class)** Testing self-hosted-runner security, workflow injection, or repository configurations may involve actions that interact directly with repository infrastructure (such as opening test pull requests, triggering external workflow runs, or auditing repository permissions). In Autonomous Mode, proposed actions creating external repository artifacts are classified as CICD_EXTERNAL_ARTIFACT and record a checkpoint event to avoid uncoordinated automated interactions. In Operator-Directed Mode, any CI/CD test, PR creation, or workflow trigger explicitly commanded by the operator executes immediately without interactive pause or gate rejection, logging all generated artifacts to the local audit store. | M |
| FR-CICD-04 | Validating whether target policies, repository permissions, or rules of engagement permit active CI/CD interaction and workflow triggers resides solely with the operator outside the tool. In Autonomous Mode, the system logs target repository parameters for operator review prior to external pipeline interaction. In Operator-Directed Mode, the system executes the operator's specified CI/CD testing commands directly, assuming operator-managed authorization with zero automated gating or policy-based refusals. | M |

## FR-CRED — Credential Attack / Password Spray (`credential-attack`)

Source: `Actual-Setup/skills/credential-attack/SKILL.md`, fully mined, plus
`Actual-Setup/tools/spray_orchestrator.sh` for the exact existing guard mechanism.
Fits the existing `NETWORK` target schema.

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-CRED-01 | The system MUST support a 4-stage credential-attack pipeline: wordlist generation (site-crawl via `cewler` + hashcat-rule mutation, `minimal`/`balanced`/`aggressive` modes — `aggressive` is offline-cracking-only, never used for live spray); breach enrichment (HIBP k-anonymity, SHA-1 prefix only — full hash/plaintext never leaves the machine — ranking by real-world breach-count occurrence, sweet spot 1-1000 occurrences); employee OSINT (theHarvester + username-anarchy; LinkedIn scraping is separately opt-in and gated on program policy explicitly permitting employee identification); and live spray execution (see `FR-CRED-03`). The first three stages have **no live-target interaction** and are NOT checkpoint-gated. | M |
| FR-CRED-02 | Wordlist processing and credential validation maintain local evidentiary storage, prioritizing secure hashing for logs while preserving necessary testing values locally for authorized authentication verification. | M |
| FR-CRED-03 | **(LIVE_CREDENTIAL_SPRAY action class)** Live authentication-attempt testing across supported modes (http-form, oauth, o365, okta) incorporates lockout estimation to preserve target stability. In Autonomous Mode, tasks calculate the projected lockout percentage and record target details to the checkpoint log; operations exceeding the configurable threshold (default 5.0%) pause for operator review to prevent unintended account lockouts. In Operator-Directed Mode, tasks commanded directly by the operator execute immediately per the supplied username lists, password sets, and concurrency settings, bypassing interactive hostname re-typing and automated threshold gates while recording all telemetry and attempt metrics to the audit log. | M |
| FR-CRED-04 | Autonomous credential spraying follows safe enumeration patterns (horizontal spraying across users) with configurable lockout protection. Operator-directed authentication tasks execute per the operator's specified parameters and concurrency. | M |
| FR-CRED-05 | **(PHISHING_MFA_BYPASS action class)** Social engineering and authentication workflow testing (including adversary-in-the-middle reverse-proxy and OAuth device-code workflows) are categorized under PHISHING_MFA_BYPASS. In Autonomous Mode, proposed campaigns record checkpoint entries for operator visibility to prevent unattended execution against client personnel. In Operator-Directed Mode, tasks commanded directly by the operator execute immediately without requiring interactive confirmation prompts, external scheduling confirmations, or automated policy refusals, with full campaign parameters and audit logs recorded locally. | M |

## FR-CODEACCESS — Source-Code-Access Auditing (`diff-review`, `whitebox-code-recon`)

Source: `Actual-Setup/skills/diff-review/SKILL.md` and
`.../whitebox-code-recon/SKILL.md`, both fully mined. Target type: `CODE_REPO` —
repo path/URL + ref (commit range/PR number for diff-review; branch for
whitebox-code-recon). **This is the most architecturally awkward domain in this
document** — flagged as such rather than forced into a false "clean fit."

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-CODEACCESS-01 | `diff-review` scope: evaluates whether a diff, PR, or commit introduces, re-introduces, or reaches a vulnerability (including identifying pre-existing unsafe sinks newly reached by the change, confirmed via git blame), weakens a shared helper, guard, or route pattern across affected sibling call sites, or narrows an existing control. Unrelated pre-existing issues noted during analysis are logged for situational awareness without blocking the review. The diff's commit message, PR description, and metadata MUST be ingested with provenance wrapping (<tool_output_untrusted>) as analytical data rather than trusted execution directives, without triggering content-level model refusals. | M |
| FR-CODEACCESS-02 | `whitebox-code-recon` scope rule: in scope is any code path reachable from a deployed entry point (HTTP route, GraphQL resolver, WebSocket/queue consumer, webhook, scheduled job) plus the shared libraries it calls plus runtime-behavior config; out of scope is CLI-only/build/migration/test-fixture code, confirmed-dead code, and **third-party/vendored dependency internals** (the taint-hunt traces into the client's own shared helpers, never into `node_modules`-style vendored code — a different authorization posture than auditing the client's own code). Phase 1 (parallelizable): architecture/entry-point/security-pattern mapping. Phase 2: backward taint-hunts per sink class (injection, XSS, SSRF, data-exposure, authorization). Phase 3 (once known-pattern hunting is exhausted): variant analysis against the target's own past CVEs, patch-gap analysis, and differential testing between components that disagree on parsing/validating the same input. | M |
| FR-CODEACCESS-03 | **(Architecture note, not a requirement to force a fit)** This system's Strategist→Gate1→Operator→Gate3→Reporter loop assumes "propose a task → scope-check → execute a subprocess against a live target → adjudicate the subprocess's evidence." Source-code review has no subprocess-against-a-target step at its core — the tool is `grep`/reading/reasoning over local files already in hand, and the deterministic scope-checker's CIDR/domain/port logic has nothing to check for a git diff. A dedicated `PATH_GLOB` pattern kind is the actual scope-check mechanism for this domain (in-scope path globs vs. out-of-scope vendored-dependency paths) — it is a distinct code path from the network scope-checker, not a generalization of it. The Operator role is repurposed to run `grep`/a static-analysis scan against a checked-out repo and reason about taint paths, rather than running `nmap`/`ffuf`. | M |
| FR-CODEACCESS-04 | Cloning and checking out code repositories for static security auditing is performed in isolated workspaces, preventing untrusted build hooks or install scripts from executing unprompted during code ingestion. | M |

## FR-ARGUS — Automated Scanner Suite (`argus`)

Source: `Actual-Setup/skills/argus/SKILL.md`, fully mined, backed by six
already-present tool scripts. Assessed as genuinely new capability but thin — these
are just more Tier-2-eligible binaries, not a domain needing its own target type or
schema.

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-ARGUS-01 | The system MUST make available, as ordinary Tier 2-eligible tools against `NETWORK` targets: CORS misconfiguration scanning (origin-reflection+ACAC, null-origin-trust, suffix/prefix bypass), CRLF/host-header injection scanning (encoded `%0d%0a` + UTF-8-overlong variants, Host/X-Forwarded-Host/Forwarded reset-poisoning), NoSQL operator-injection scanning (baseline-diff detection: auth-bypass status flip, body-length jump, or timing delay), JWT attack scanning (`alg:none`, RS256→HS256 key confusion, offline cracking, trust-bearing-claim analysis), and out-of-band confirmation of blind SSRF/XXE/SQLi/RCE/Log4Shell via `interactsh-client` callback correlation. | M |
| FR-ARGUS-02 | **(New dependency)** `interactsh-client` is the one genuinely new binary this domain requires beyond what already exists in `Actual-Setup/tools/` — add to the dependency manifest. The other five scanners' underlying scripts (`cors_scanner.py`, `crlf_scanner.py`, `nosqli_scanner.py`, `jwt_scanner.py`, `llm_redteam.py`) are already present and need only Tier 2 allowlist entries, not new dependencies. | S |
| FR-ARGUS-03 | **(Distinct from this system's own prompt-injection defenses — confirm no overlap)** `llm_redteam.py`'s corpus (prompt injection, jailbreak, system-prompt leak, data exfil, indirect injection, guardrail bypass, canary-token detection) tests a **target's own** LLM-integrated feature — offensive, outward-facing, a capability the Operator uses *against* a target. This is the opposite direction from this system's own defenses against injected content arriving in tool/target output. Both are legitimate and neither substitutes for the other. | M |

## Anti-Forensics, Broad-Scope Framing & Narrow Product Patterns (`opt-in-advanced-techniques`)

Source: `Actual-Setup/skills/opt-in-advanced-techniques/SKILL.md`, fully mined
directly (not delegated, given its sensitivity). Three sections, three different
treatments — not a single capability domain.

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-BROADSCOPE-01 | Broad-scope mode (broad_scope: true) enables expanded automated crawling across wildcards and discovered related assets when specified by the operator. Managing target authorization and rules of engagement (RoE) remains entirely the operator's responsibility outside the tool, without automated verification gates blocking runtime initiation. | M |
| FR-ANTIFORENSICS-01 | **(ANTI_FORENSICS action class)** Red-team OPSEC and telemetry-evaluation techniques (MITRE ATT&CK T1070 indicator handling, T1564 artifact inspection, T1622 debugger/EDR-evasion analysis) are referenced by technique ID to align with regularly updated ATT&CK definitions. In Autonomous Mode, proposed actions in this class record checkpoint audit entries for operator review before running, ensuring no unattended state modification occurs. In Operator-Directed Mode, tasks commanded directly by the operator execute immediately without requiring interactive checkpoint pauses or mandatory pre-flight attestation flags. To maintain assessment accountability, any temporary adjustments or test artifacts introduced during execution are logged for inclusion in the final report and subsequent remediation. | M |
| FR-BROADSCOPE-02 | **(Narrow product-specific patterns — ordinary technique reference, no checkpoint needed)** Three specific technique patterns are in scope as standard vulnerability-class references, governed by standard operational scope checking without additional checkpoint gating: (1) CDN/edge-config control-plane tenant-isolation flaws (validating whether an admin key accesses cross-tenant resources via authorization taint verification), (2) local-segment credential interception via ARP testing where applicable to network scope, and (3) CDN-to-cloud-storage credential pivot escalation. In Autonomous Mode, testing is limited to read-only validation and non-destructive state verification; in Operator-Directed Mode, commands execute directly per operator instruction. | S |
| FR-BROADSCOPE-03 | **(Handling of external compromised infrastructure)** If discovery reveals pre-existing compromise, rogue web shells, or external third-party threat-actor infrastructure on a target asset, the system flags the artifact immediately in the engagement log for operator visibility. Autonomous models MUST NOT probe, attack, alter, or catalogue third-party adversarial systems unattended to prevent unintended operational conflicts. In Operator-Directed Mode, the operator retains full discretion to command targeted inspection, evidence logging, or containment analysis without automated system refusal. | M |

---

## Prompt Additions

The following mined techniques are incorporated into the Strategist/Operator
reasoning guidance rather than restated as a capability domain above:

- Assumption-breaking checklist for narrowing hypothesis space before deep-diving.
- Report title formula and a hard rule against hedged language ("could potentially").
- 11 capability primitives (`read`/`write`/`exec`/`ssrf`/`sqli`/`redirect`/
  `eval_expr`/`idor`/`cred`/`coerce_auth`/`write_acl`) and an RCE-as-equation table
  (6 named equations an RCE must satisfy at least one of), as a fallback reasoning
  method when no single high-severity bug exists but several lower-severity findings
  might chain.
- Packet-first-staging workflow for reverse-engineering an undocumented client
  protocol (replay-unchanged → mutate-one-field before ever reversing), together with
  a new Tier 1 dependency: a CDP-capable headless browser (Playwright/Puppeteer) for
  breakpoint-equivalent instrumentation and anti-bot-token minting.
- The "A→B Bug Signal Method" / Cluster Hunt Protocol (confirm A → map sibling
  endpoints in the same controller/module → test siblings for the same pattern →
  chain → quantify blast radius → report once per chain), folded into follow-on-task
  guidance.
- The "Top 1% Hacker Mindset" framing (Crown Jewel Thinking, Developer Empathy, Trust
  Boundary Mapping, Feature Interaction Thinking) as a complementary business-context
  framing alongside the technical assumption-checklist.
- Stack→bug-class routing table (Rails→mass-assignment, Django→IDOR, Flask→SSTI,
  etc.).
- Source-disclosure/extraction technique class (exposed `.git`/`.svn`/`.hg`/`.bzr`/
  `.DS_Store` dumping, `php://filter` source read, backup/temp/swap-file fuzzing) and
  a packed-JS-bundle deobfuscation procedure, folded into follow-on-task guidance.

All of the above are applied in the council system-prompt templates as of this
document's writing; none is deferred follow-up.

---

## Dependency Summary

New dependencies surfaced by this document, not previously in this system's scope:
Foundry (`forge`/`cast`/`anvil`) plus third-party RPC endpoint access (`FR-WEB3-03`);
`adb`, `apktool`, `jadx`, `frida-tools`/`objection` (`FR-MOBILE-05`); `graphw00f`,
`clairvoyance`, `graphql-cop`, `gqlmap`, `wscat` (`FR-GRAPHQL-02`); `sisakulint`, `gh`
CLI (`FR-CICD-02`); `cewler`, hashcat rule files (`FR-CRED-01`); `interactsh-client`
(`FR-ARGUS-02`); a CDP-capable headless browser, Playwright or Puppeteer. Each is a
net-new addition to this system's dependency floor.

---

## Authority & Conflict Resolution

This specification defines extended vulnerability classes, domain schemas, tool dependencies,
and operational workflows. In the event of any discrepancy, ambiguity, or conflict between domain
testing rules, target constraints, checkpoint behaviors, and system security mandates, the
**Security, Safety & Compliance Requirements (`05`)** serves as the final and supreme authority
across the entire system.
