# Extended Capability Domains — Autonomous Agentic VAPT System

**Origin:** the base system (`01`-`18`) specifies general web/network VAPT only.
`/home/vscysteam/claude-bug-bounty`'s `Actual-Setup/skills/` directory contains 19
specialized skill domains beyond that scope. Per explicit operator decision, **every
one of them is now formalized as explicit in-scope capability** — this document is
that formalization, built on a full deep-mine of each skill's actual content (not a
one-line description), following the same evidence discipline as `11`'s
critical-analysis findings: only concrete, source-verified techniques are turned into
requirements here, nothing fabricated to fill a gap.

**How this document relates to `01`-`18`:** it does not replace or restate the core
5-phase council architecture — every domain below still goes through Council Gate 1
(scope-check), the Operator/Tier 1-2 bridge, Council Gate 3 (adjudication), and the
Reporter, exactly as `01` describes. What changes per domain is *what a target looks
like* (see the schema generalization below, `DR-SCHEMA-15/16` in `03`), *what tooling
the bridge needs*, and in four specific cases, *a new mandatory pause* (the Human
Checkpoint Gate, `FR-CHECKPOINT` in `01`) that this system did not previously have.

**Two categories of mined content are deliberately NOT in this document:**
- **Pure reasoning/technique enhancements** with no new target type, tooling, or
  schema need — `bb-methodology`'s assumption-breaking checklist (already folded into
  the Strategist prompt, `14` §1), `report-writing`'s title formula and "never write
  'could potentially'" rule (already folded into the Reporter prompt, `14` §5),
  `capability-chaining`'s capability-primitive reasoning method, `client-reverse`'s
  request-signing-reversal workflow, `bug-bounty`'s "A→B Bug Signal Method"/Cluster
  Hunt Protocol and "Top 1% Hacker Mindset" framing, and `web2-recon`'s
  stack→bug-class routing table — these are folded into `14`'s Strategist/Operator
  prompts directly (see the end of this document for the exact additions), not
  restated here as capability domains.
- **`triage-validation`** — already fully mined into `FR-COUNCIL-14a` (`16` §4a),
  nothing further to add.

---

## Schema Generalization (implemented in `03`, summarized here)

Several domains below need a target identity that isn't a host/domain/CIDR.
`targets` (`DR-SCHEMA-02`) is generalized with a `target_type` discriminator
(`NETWORK` / `CONTRACT` / `MOBILE_BINARY` / `CODE_REPO`) and type-specific nullable
columns — see `DR-SCHEMA-15` for the full column list. `scope_rules` gains a
`pattern_kind` discriminator (`NETWORK` / `EXACT_IDENTIFIER` / `PATH_GLOB`) — see
`DR-SCHEMA-16`. `FR-COUNCIL-03a`'s deterministic scope-checker MUST branch on both
discriminators; this is new code per kind, not a generalization of the existing
CIDR/regex matcher.

## The Human Checkpoint Gate (implemented in `01`, summarized here)

Four specific techniques below have a real safety mechanism, in their own source
material, that is a **live human confirming something in real time** — not a
pre-engagement config flag. Rather than silently drop that property to fit this
system's fully-autonomous design, or silently exclude the capability, the operator
chose to **preserve the capability and add a narrow, explicit exception to the
no-pause design**: `FR-CHECKPOINT-01..05` in `01`. Each of the four domains below
that trigger it says so explicitly, with a pointer to its specific action class
(`ANTI_FORENSICS` / `LIVE_CREDENTIAL_SPRAY` / `CICD_EXTERNAL_ARTIFACT` /
`DEPENDENCY_CONFUSION_PUBLISH`). The full rationale, MITRE ATT&CK references, and
exact trigger conditions for all four are cataloged in
`20-Human-Checkpoint-and-Escalation-Safety-Catalog.md` — this document only states
*that* each triggers it and *which* class, not the full safety analysis.

---

## FR-VULNCLASS — Web/API Vulnerability Class Catalog (`web2-vuln-classes`)

Source: `Actual-Setup/skills/web2-vuln-classes/SKILL.md` (2,447 lines, fully read
across two mining passes — §11 in the original pass, the remaining 31 classes in a
follow-up sweep). Most of the 32 classes are standard, well-documented bug categories
already within a strong coding model's training and already implicitly covered by
`FR-COUNCIL-01/02`'s general hypothesis-generation instruction — this section exists
to make the coverage **explicit and named**, not to re-teach the Operator textbook
material.

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-VULNCLASS-01 | This system's in-scope web/API vulnerability classes MUST include, by name, all 32 classes documented in `web2-vuln-classes/SKILL.md`: IDOR; Broken Auth/Access Control; XSS; SSRF; Business Logic; Race Conditions; SQL Injection; OAuth/OIDC Bugs; File Upload; GraphQL-Specific (superseded in depth by `FR-GRAPHQL` below); LLM/AI Features (MCP/RAG — see `FR-TOOL-13`/finding C-31, already resolved); API Security Misconfiguration; Account-Takeover Taxonomy; SSTI; Subdomain Takeover; Cloud/Infra Misconfigs; HTTP Request Smuggling; Cache Poisoning/Web Cache Deception; MFA/2FA Bypass; SAML/SSO Attacks; Error Disclosure/Debug Endpoints; CSS Injection; LFI/File Inclusion→RCE; Insecure Deserialization; Broken Function-Level Authorization (BFLA); NoSQL Injection; Semantic Confusion (parser/normalization differentials); Header Injection/Response Splitting; XXE; WebSocket Security; Dependency Confusion/Supply Chain (see `FR-VULNCLASS-03`, checkpoint-gated); Padding Oracle & Crypto Misuse. This is a scope statement, not a mandate to embed all 32 classes' full technique detail into any single prompt. | M |
| FR-VULNCLASS-02 | Three specific, non-obvious technique chains identified during mining SHOULD be available as Operator/Reporter reference material (not necessarily embedded verbatim in a system prompt, given context-budget constraints already noted for `security-arsenal`): (a) the ASP.NET ViewState padding-oracle→RCE chain (PadBuster recovers the oracle, `ysoserial.net -p ViewState -g TextFormattingRunProperties` builds the deserialization gadget, a forged `__VIEWSTATE` gives RCE under the app-pool identity); (b) the WebSocket chat-widget cross-role stored-XSS chain (an anonymous visitor's message triggering XSS in the support agent's browser via unsanitized rich-message rendering, not the visitor's own browser — a higher-impact pivot than it looks, since the agent's workstation is often less segmented); (c) CSS-injection-based data exfiltration via attribute selectors (leaking form field values with no JavaScript at all). | S |
| FR-VULNCLASS-03 | **(Checkpoint-gated — `DEPENDENCY_CONFUSION_PUBLISH`, `FR-CHECKPOINT-01/02`)** Proving a dependency-confusion finding requires publishing a real package to a live, third-party public package registry (npm/PyPI/RubyGems/Maven) — an action with permanent external side effects entirely outside the target's own `scope_rules` relationship, and materially higher-stakes than anything else this system does autonomously (an unpublish step failing silently, or a misjudged callback-source-verification, could leave a real, exploitable package live on a public registry). The system MUST: use a callback-only PoC (DNS/HTTP beacon proving execution — never a real payload); verify the callback source is genuinely the target's infrastructure, not a registry crawler, before treating it as confirmed; and treat the publish action itself, and the subsequent mandatory unpublish, as a single `DEPENDENCY_CONFUSION_PUBLISH`-class checkpoint requiring live operator approval before the publish step executes. | M |

## FR-WEB3 — Web3 / Smart Contract Auditing (`web3-audit`, `meme-coin-audit`)

Source: `Actual-Setup/skills/web3-audit/SKILL.md` and `.../meme-coin-audit/SKILL.md`,
both fully read. Target type: `CONTRACT` (`DR-SCHEMA-15`) — a contract address +
chain ID, not a host/domain.

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-WEB3-01 | The system MUST support `CONTRACT`-type targets covering, at minimum, the 10 named smart-contract bug classes from `web3-audit` (each with severity data from disclosed Immunefi payouts): Accounting State Desynchronization (#1 Critical, 28% of Criticals); Access Control (19% of Criticals); Incomplete Code Path (a "function family" check — verify every sibling of a function, e.g. `mint()`/`deposit()`, has equivalent validation); Off-by-one/boundary conditions (22% of Highs); Oracle/price manipulation (missing staleness checks, single-source oracles, short TWAP windows); ERC4626 vault attacks; Reentrancy (single/cross-function/cross-contract/read-only variants); Flash-loan-funded oracle manipulation; Signature replay (missing nonce/chain-ID in signed hash); Proxy/upgrade issues (storage collision, uninitialized implementation, unrestricted `delegatecall`). | M |
| FR-WEB3-02 | The system MUST support `CONTRACT`-type targets covering the 8 named token/meme-coin bug classes from `meme-coin-audit`: hidden mint/unlimited supply; honeypot/transfer restriction; post-launch fee manipulation; liquidity-pool drain via migration/emergency-withdraw functions; bonding-curve manipulation; Solana authority retention (mint/freeze/update/close authority not revoked); fake renounce/hidden backdoor ownership; sandwich-amplification-by-design (zero-slippage auto-swap, rebase mechanics). | M |
| FR-WEB3-03 | **(New dependency, not previously in scope)** Smart-contract testing requires **Foundry** (`forge`/`cast`/`anvil`) and an RPC endpoint for mainnet-fork analysis (`vm.createSelectFork`) — an outbound network dependency to a third-party RPC provider (Alchemy/Infura/local node), unlike every other tool in this system's scope, which targets the client's own infrastructure directly. This MUST be documented as a new dependency in `08` (see the dependency summary at the end of this document), and the RPC endpoint itself is not a `scope_rules`-governed target — it's infrastructure this system calls out to, analogous to how the inference gateway is infrastructure this system calls in. | M |
| FR-WEB3-04 | All autonomous PoC execution against a `CONTRACT` target MUST run against a **local mainnet-fork simulation** (`anvil`/`forge test --fork-url`), never a live, unforked mainnet contract — a forked simulation touches no real funds and is safe for unattended execution; direct interaction with live mainnet state is a categorically higher-risk action this system MUST NOT perform autonomously, and is out of scope for this system regardless of opt-in flags. | M |
| FR-WEB3-05 | **(Meme-coin only, per operator decision to keep both modes)** `CONTRACT` targets in `meme-coin-audit` scope carry a `contract_investigation_mode` (`DR-SCHEMA-15`): `CLIENT_OWNED` (a client's own token contract — standard VAPT posture, identical authorization model to every other domain) or `PUBLIC_RESEARCH` (evaluating a third-party public token for rug-pull risk — no client relationship, no `scope_rules` authorization boundary in the usual sense, since the entire activity is read-only public on-chain/API querying, not an attack against anything). `PUBLIC_RESEARCH` mode MUST be restricted to read-only checks (on-chain authority/deployer-history queries via block explorers, holder-distribution/LP-lock lookups via third-party APIs — Etherscan/Solscan/DEXTools/Birdeye/Unicrypt) — it MUST NOT attempt any action equivalent to `FR-WEB3-04`'s PoC execution, since there is no engagement authorizing intrusive testing against a token nobody has scoped. | M |
| FR-WEB3-06 | The Strategist SHOULD apply `web3-audit`'s pre-dive kill-signal scoring before committing to a deep audit: skip if TVL < $500K or `min(10% × TVL, program_cap) < $10K`; hard-skip if 2+ top-tier audits (Halborn/Trail of Bits/Cyfrin/OpenZeppelin) exist on a simple (<500 LOC) protocol version. | S |

## FR-MOBILE — Mobile Application Pentesting (`mobile-pentest`)

Source: `Actual-Setup/skills/mobile-pentest/SKILL.md`, fully read. Target type:
`MOBILE_BINARY` (`DR-SCHEMA-15`) — platform + package name + binary artifact.

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-MOBILE-01 | The system MUST support `MOBILE_BINARY`-type targets (Android APK / iOS IPA) under a **runtime-first, never-decompile-first** methodology: install on device/emulator → proxy traffic → drive core business flows manually → if traffic is visible and replayable, treat the recovered API exactly like a `NETWORK` target (register it as a linked row via `backend_target_id`, `DR-SCHEMA-15`, and stop reversing) → escalate to static analysis (`apktool`/`jadx`) and dynamic instrumentation (Frida/`objection`) only when traffic is pinned, encrypted, or absent. | M |
| FR-MOBILE-02 | The system MUST perform a static secrets/endpoint sweep before any dynamic testing — decompile via `apktool`, grep for hardcoded credentials (`api_key\|secret\|password\|token\|Authorization\|Bearer\|client_secret\|private_key` patterns) and base-URL/endpoint strings; internal or staging base URLs never exposed by the web app are explicitly the single highest-value find from this step. | M |
| FR-MOBILE-03 | The system MUST support SSL/certificate-pinning bypass via `objection patchapk` (gadget) as the first path, with targeted Frida hooks on `okhttp3.CertificatePinner.check()` and `TrustManagerImpl.checkTrustedRecursive()` as fallback. | M |
| FR-MOBILE-04 | The system MUST check exported Android components (manifest `exported="true"` + intent-filter + `BROWSABLE` + custom URI scheme) for deeplink injection, and — when a WebView is reached via such a deeplink — enumerate any `@JavascriptInterface`-exposed bridge methods for injection/RCE (API<17 targets specifically), following the documented chain: deeplink → WebView `loadUrl()` → JS bridge → token exfiltration. | M |
| FR-MOBILE-05 | **(New dependencies, not previously in scope)** This domain requires `adb` + an Android device/emulator, `apktool`, `jadx`, and `frida-tools`/`objection` (pip-installed — these commonly install to `~/.local/bin` or a venv, **outside** the existing Tier 2 allowlist's `/usr/bin/`,`/usr/sbin/`,`/opt/` restriction; MUST be installed into `/opt/` explicitly, or the allowlist gains a documented exception, not silently bypassed). iOS requires a **physical jailbroken device** — no software-emulator path exists for pinning bypass on iOS at all. | M |
| FR-MOBILE-06 | **(Hardware constraint, flagged not silently absorbed)** An Android emulator typically needs 2-4+ GB RAM — run alongside a resident council model under the confirmed `Q8_0` roster, this would likely exceed the already-tight post-hibernation headroom (`NFR-RES-01`, ~2.0-4.2 GB worst-case per finding C-30). This system's default for this domain on the confirmed hardware profile MUST be a **physical Android device via `adb`**, not a local emulator; emulator use is a documented degraded/unsupported configuration, not the assumed default. | M |
| FR-MOBILE-07 | The Operator SHOULD apply the domain's stated N/A criteria before proposing a mobile finding as report-worthy: debuggable flag alone, missing root/jailbreak detection alone, pinning-bypass-required alone, missing obfuscation alone, and a publicly-scoped API key without proven unrestricted access are all explicitly non-findings. Sharpest reusable framing (near-verbatim from the source): *"Can a remote attacker, with no physical access to the victim's unlocked device, do this right now for real impact? If it needs the victim's rooted/unlocked phone, it's almost always N/A."* | S |

## FR-GRAPHQL — GraphQL API Auditing (`graphql-audit`)

Source: `Actual-Setup/skills/graphql-audit/SKILL.md`, fully read, backed by the
already-present `Actual-Setup/tools/graphql_audit.sh`. Fits the existing `NETWORK`
target schema unmodified — a GraphQL endpoint is just a URL under an already
in-scope host.

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-GRAPHQL-01 | The system MUST support a 7-phase GraphQL audit against in-scope `NETWORK` targets: introspection abuse (including bypasses — newline injection, fragment tricks, `__type` in place of `__schema`, GET-instead-of-POST, WebSocket-subscription-channel introspection); field-suggestion abuse (typo-triggered "did you mean" schema recovery, manual or via `clairvoyance`); engine fingerprinting via `graphw00f` (engine-specific CVE differences — Hasura auth bypass, Apollo depth issues, Hot Chocolate SSRF-in-federation, WPGraphQL IDOR-proneness); IDOR via direct object access and field-level IDOR (privileged fields readable on an otherwise-owned object); injection via resolver arguments (SQLi via `gqlmap`, NoSQLi via JSON-coerced operator injection); auth-bypass patterns (unauthenticated queries/mutations, deprecated-field auth bypass); subscription abuse (cross-user WebSocket event leakage); and WAF-bypass techniques (content-type switching, GET-based introspection). | M |
| FR-GRAPHQL-02 | **(New dependencies, not previously in scope)** `graphw00f`, `clairvoyance`, `graphql-cop`, `gqlmap` (pip-installable) and `wscat` (npm-installable) — all fit the existing Tier 2 path-restricted-allowlist model once installed; no new bridge mechanism is needed, only new allowlist entries and a dependency-manifest addition (`08`). | M |
| FR-GRAPHQL-03 | **(Checkpoint consideration, resolved without a new gate)** Batching DoS (array/alias batching — up to 500+ aliases in one request, explicitly usable to bypass per-query rate limits for OTP brute force or password-reset bombing) and depth/complexity bombs are explicitly availability-impacting proof techniques, not passive checks. These MUST require the existing `--allow-active-exploitation` opt-in category at minimum (`FR-TOOL-06a`) — batching used specifically to brute-force OTPs or bomb password-resets additionally requires `--allow-brute-force` — and MUST respect `FR-TOOL-14`'s existing rate-limiting design; this was evaluated against the four new checkpoint action classes and judged **not** to need a fifth, since — unlike anti-forensics/live-spray/CI/CD-PR-opening/dependency-publish — there is no live-human-confirmation mechanism in the source material this would be dropping; the existing opt-in-flag pattern is a sufficient, equivalent safeguard here. | M |
| FR-GRAPHQL-04 | The Strategist/Operator SHOULD apply the domain's kill signals before deep GraphQL testing: a 404/410-consistent endpoint is inactive; generic "Unauthorized" with no field suggestions indicates a well-hardened target; a rate limit firing on the second query indicates strong protection and low ROI; an Apollo Federation gateway-only response means the downstream services, not the gateway, are the actual target. | S |

## FR-CICD — CI/CD Pipeline Security (`cicd-security`)

Source: `Actual-Setup/skills/cicd-security/SKILL.md`, fully read, backed by the
already-present `Actual-Setup/tools/cicd_scanner.sh`. Target type: `CODE_REPO`
(`DR-SCHEMA-15`) — an `owner/repo` identity, not a host/domain.

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-CICD-01 | The system MUST support `CODE_REPO`-type targets covering: GitHub Actions workflow injection via untrusted context variables interpolated into `run:` blocks (`github.event.pull_request.title/body`, `.head.ref`, issue/comment/review/discussion bodies, `workflow_dispatch` inputs); `pull_request_target` misuse (runs with base-repo secrets against attacker-controlled PR head code); secret exfiltration (log echo, DNS-based stealthy exfil); overly broad `GITHUB_TOKEN`/OIDC trust-policy permissions; self-hosted-runner poisoning (public repo + self-hosted runner lets any fork queue jobs on internal infrastructure); and dependency confusion/supply chain via unpinned mutable-tag action references. | M |
| FR-CICD-02 | **(New dependencies and access model, not previously in scope)** `sisakulint` (workflow linter) and the `gh` CLI (needs authentication for anything beyond public-log access) are new dependencies. Critically, **the access model is fundamentally different from every other domain**: recon is `git clone`/`gh api` against a repository, not `nmap`/`ffuf` against a host — some checks are genuinely read-only (public workflow files, public run logs, public secret *names*), but the rest is not. | M |
| FR-CICD-03 | **(Checkpoint-gated — `CICD_EXTERNAL_ARTIFACT`, `FR-CHECKPOINT-01/02`)** Meaningfully testing self-hosted-runner poisoning or workflow injection requires **opening a real, visible pull request against the target's actual repository** — this creates a persistent artifact in the target's own infrastructure that cannot be un-sent the way a scan probe can, categorically closer to submitting a form on a live production system than to running a passive scanner. Any action that opens a PR, triggers a workflow run, or modifies repository secrets/permissions MUST be classified `CICD_EXTERNAL_ARTIFACT` and go through the Human Checkpoint Gate — it MUST NOT be treated as ordinary Tier 2 execution regardless of opt-in-flag state. | M |
| FR-CICD-04 | The system MUST confirm, before any `CICD_EXTERNAL_ARTIFACT`-class action, that the target program's policy actually permits touching CI/CD infrastructure — most bug-bounty programs scope public repositories only, and self-hosted-runner attacks specifically require a successful workflow run (i.e., an accepted or at least triggered PR), which the program may not permit at all. This confirmation is exactly what the Human Checkpoint Gate's live approval step provides — it is not a separate mechanism. | M |

## FR-CRED — Credential Attack / Password Spray (`credential-attack`)

Source: `Actual-Setup/skills/credential-attack/SKILL.md`, fully read, plus
`Actual-Setup/tools/spray_orchestrator.sh` for the exact existing guard mechanism.
Fits the existing `NETWORK` target schema.

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-CRED-01 | The system MUST support a 4-stage credential-attack pipeline: wordlist generation (site-crawl via `cewler` + hashcat-rule mutation, `minimal`/`balanced`/`aggressive` modes — `aggressive` is offline-cracking-only, never used for live spray); breach enrichment (HIBP k-anonymity, SHA-1 prefix only — full hash/plaintext never leaves the machine — ranking by real-world breach-count occurrence, sweet spot 1-1000 occurrences); employee OSINT (theHarvester + username-anarchy; LinkedIn scraping is separately opt-in and gated on program policy explicitly permitting employee identification); and live spray execution (see `FR-CRED-03`). The first three stages have **no live-target interaction** and are NOT checkpoint-gated. | M |
| FR-CRED-02 | Wordlist-generation and breach-enrichment MUST never write full plaintext breach credentials to disk or use them directly against a live account — the source material's own legal-guardrail language is explicit that doing so is illegal in most jurisdictions even within an authorized bug-bounty scope; this system MUST enforce HIBP's hash-prefix-only query pattern and MUST NOT store recovered plaintext breach passwords. | M |
| FR-CRED-03 | **(Checkpoint-gated — `LIVE_CREDENTIAL_SPRAY`, `FR-CHECKPOINT-01/02`)** The reference implementation's actual safety mechanism for live spray execution is a human interactively re-typing the target hostname to confirm it, plus a live lockout-percentage warning before proceeding — by the tool's own comment, *"the real safety mechanism here is making the human re-state the target out loud."* A fully autonomous invocation cannot satisfy this as designed. The live authentication-attempt stage of any spray (all four modes: `http-form`/`oauth`/`o365`/`okta`) MUST be classified `LIVE_CREDENTIAL_SPRAY` and go through the Human Checkpoint Gate, with the target hostname and an estimated lockout percentage shown as part of `rationale_shown_to_operator` (`DR-SCHEMA-18`) — reproducing the substance of the source's interactive confirmation, not just its label. Phishing-based MFA bypass (AiTM reverse-proxy, OAuth device-code phishing) is explicitly out of scope for this system entirely (not merely checkpoint-gated) — it involves actively deceiving a real employee, a materially different act than an automated login attempt, and the source material itself requires informing the client's security/legal team of the timing beforehand, which this system has no mechanism to verify. | M |
| FR-CRED-04 | Spray order MUST be `password[i] × all_users` per round (not per-user brute force), specifically to keep every individual account under its lockout threshold, and MUST stop on the first successful hit by default. Any account lockout caused during testing MUST be logged and surfaced to the operator for immediate reporting to the program — this is a real, user-facing availability impact, not a victimless probe. | M |

## FR-CODEACCESS — Source-Code-Access Auditing (`diff-review`, `whitebox-code-recon`)

Source: `Actual-Setup/skills/diff-review/SKILL.md` and
`.../whitebox-code-recon/SKILL.md`, both fully read. Target type: `CODE_REPO`
(`DR-SCHEMA-15`) — repo path/URL + ref (commit range/PR number for diff-review;
branch for whitebox-code-recon). **This is the most architecturally awkward domain
in this document** — flagged as such rather than forced into a false "clean fit."

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-CODEACCESS-01 | `diff-review` scope: a diff/PR/commit introduces, re-introduces, or newly reaches a vulnerability (including a pre-existing unsafe sink the diff is the first caller to reach, confirmed via `git blame`); weakens a shared helper/guard/route pattern (expanded to every sibling call site the diff affects); or removes/narrows a control even with no new sink. Explicitly out of scope: unrelated pre-existing bugs merely noticed while reading context (noted, not filed against that PR). The diff's own commit message/PR description MUST be treated as untrusted input, not a trusted description of intent. | M |
| FR-CODEACCESS-02 | `whitebox-code-recon` scope rule: in scope is any code path reachable from a deployed entry point (HTTP route, GraphQL resolver, WebSocket/queue consumer, webhook, scheduled job) plus the shared libraries it calls plus runtime-behavior config; out of scope is CLI-only/build/migration/test-fixture code, confirmed-dead code, and **third-party/vendored dependency internals** (the taint-hunt traces into the client's own shared helpers, never into `node_modules`-style vendored code — a different authorization posture than auditing the client's own code). Phase 1 (parallelizable): architecture/entry-point/security-pattern mapping. Phase 2: backward taint-hunts per sink class (injection, XSS, SSRF, data-exposure, authorization). Phase 3 (once known-pattern hunting is exhausted): variant analysis against the target's own past CVEs, patch-gap analysis, and differential testing between components that disagree on parsing/validating the same input. | M |
| FR-CODEACCESS-03 | **(Architecture note, not a requirement to force a fit)** This system's Strategist→Gate1→Operator→Gate3→Reporter loop assumes "propose a task → scope-check against `scope_rules` → execute a subprocess against a live target → adjudicate the subprocess's evidence." Source-code review has no subprocess-against-a-target step at its core — the tool is `grep`/reading/reasoning over local files already in hand, and `FR-COUNCIL-03a`'s CIDR/domain/port checker has nothing to check for a git diff. `DR-SCHEMA-16`'s new `PATH_GLOB` pattern kind is the actual scope-check mechanism for this domain (in-scope path globs vs. out-of-scope vendored-dependency paths) — it is a distinct code path from the network scope-checker, not a generalization of it. The Operator role is repurposed to run `grep`/`tools/sast_scan.py` against a checked-out repo and reason about taint paths, rather than running `nmap`/`ffuf`. | M |
| FR-CODEACCESS-04 | Cloning/checking out a PR from an untrusted fork MUST be read-only — the system MUST NOT build or execute the checked-out code (no `npm install`/`make`/postinstall scripts), since an untrusted PR's build tooling is itself a plausible attack vector against the testing environment. | M |

## FR-ARGUS — Automated Scanner Suite (`argus`)

Source: `Actual-Setup/skills/argus/SKILL.md`, fully read, backed by six
already-present tool scripts. Assessed as genuinely new capability but thin — these
are just more Tier-2-eligible binaries, not a domain needing its own target type or
schema.

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-ARGUS-01 | The system MUST make available, as ordinary Tier 2-eligible tools against `NETWORK` targets: CORS misconfiguration scanning (origin-reflection+ACAC, null-origin-trust, suffix/prefix bypass), CRLF/host-header injection scanning (encoded `%0d%0a` + UTF-8-overlong variants, Host/X-Forwarded-Host/Forwarded reset-poisoning), NoSQL operator-injection scanning (baseline-diff detection: auth-bypass status flip, body-length jump, or timing delay), JWT attack scanning (`alg:none`, RS256→HS256 key confusion, offline cracking, trust-bearing-claim analysis), and out-of-band confirmation of blind SSRF/XXE/SQLi/RCE/Log4Shell via `interactsh-client` callback correlation. | M |
| FR-ARGUS-02 | **(New dependency)** `interactsh-client` is the one genuinely new binary this domain requires beyond what already exists in `Actual-Setup/tools/` — add to the dependency manifest (`08`). The other five scanners' underlying scripts (`cors_scanner.py`, `crlf_scanner.py`, `nosqli_scanner.py`, `jwt_scanner.py`, `llm_redteam.py`) are already present and need only Tier 2 allowlist entries, not new dependencies. | S |
| FR-ARGUS-03 | **(Distinct from finding C-31 — confirm no overlap)** `llm_redteam.py`'s corpus (prompt injection, jailbreak, system-prompt leak, data exfil, indirect injection, guardrail bypass, canary-token detection) tests a **target's own** LLM-integrated feature — offensive, outward-facing, a capability the Operator uses *against* a target. This is the opposite direction from `FR-TOOL-13`/finding C-31, which defends *this system's own* council from injected content arriving in tool/target output. Both are legitimate and neither substitutes for the other. | M |

## Anti-Forensics, Broad-Scope Framing & Narrow Product Patterns (`opt-in-advanced-techniques`)

Source: `Actual-Setup/skills/opt-in-advanced-techniques/SKILL.md`, fully read
directly (not delegated, given its sensitivity). Three sections, three different
treatments — not a single capability domain.

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-BROADSCOPE-01 | **(§1, broad/unlimited-scope engagement framing — ordinary config, no checkpoint needed)** For the minority of engagements whose written RoE genuinely uses "anything the client owns or operates" language rather than a fixed asset list, `scope_rules` MAY be configured with a `broad_scope: true` engagement-level flag verified against the actual RoE text at `start` time (never inferred from how much attack surface a target has). This does **not** change any other discipline — third-party infrastructure merely used by the client (a SaaS vendor, a CDN, another company's API) remains out of scope even if reachable from an in-scope asset; it is a wider fence, never "no fence." | M |
| FR-ANTIFORENSICS-01 | **(§2, checkpoint-gated — `ANTI_FORENSICS`, `FR-CHECKPOINT-01/02/05`)** Red-team anti-forensics/OPSEC techniques (MITRE ATT&CK T1070 indicator removal, T1564 hide-artifacts, T1622 debugger/EDR-evasion — referenced by technique ID, not reproduced as ready-to-run commands, so this document stays current against ATT&CK's own regularly-updated detail rather than going stale) are in scope **only** when `--allow-anti-forensics` is enabled together with the required `--white-cell-contact` and `--attest-disclosure` fields (`FR-CHECKPOINT-05`), and **every individual action in this class still requires a live Human Checkpoint Gate approval** before executing — the pre-engagement flag enables considering the category at all; it does not pre-approve any specific action. The goal, per the source material, is testing *whether* detection occurs, never permanently defeating it — any log/timestamp change made during testing MUST be disclosed and reverted in the final report, never left as a silent, permanent alteration of the client's own records. | M |
| FR-BROADSCOPE-02 | **(§3, narrow product-specific patterns — ordinary technique reference, no checkpoint needed)** Three narrow, product-specific technique patterns are in scope as ordinary vulnerability-class reference, not gated by anything beyond standard scope-checking: a CDN/edge-config control-plane tenant-isolation gap (validates *a* valid admin key but not that the requested resource belongs to that key's own tenant — apply the Authorization Backward-Taint Procedure from `web2-vuln-classes` §2); same-subnet credential interception via ARP MITM (use the existing `cybersecurity-skills:performing-arp-spoofing-attack-simulation` skill rather than re-deriving it); and CDN-to-cloud-storage credential escalation (the same chain-pattern as `web2-vuln-classes`'s Cloud/Infra Misconfigs class, with the CDN control plane as the pivot instead of a directly-exposed bucket). | S |
| FR-BROADSCOPE-03 | **(Explicitly excluded, not merely deferred)** Cataloguing gray-market or criminal infrastructure discovered behind a compromised system (classifying wallet-phishing, gambling, or pirated-content hosting via keyword-matching) is **not** a penetration-testing technique and is out of scope for this system regardless of authorization framing — it is OSINT investigation of someone else's criminal campaign. If a live engagement surfaces this situation, it is an incident-response/legal question for the client; the system MUST flag it to the operator and stop, not catalogue or act on it further. | M |

---

## Prompt Additions (implemented in `14`, summarized here)

The following mined content is folded directly into existing Strategist/Operator
prompts rather than restated as a capability domain above:

- **`bb-methodology`'s assumption-breaking checklist** → Strategist prompt, `14` §1
  (applied; see `16` §4a-continued).
- **`report-writing`'s title formula and hard "never write 'could potentially'"
  rule** → Reporter prompt, `14` §5 (applied; see `16` §4a-continued).
- **`capability-chaining`'s 11 capability primitives** (`read`/`write`/`exec`/`ssrf`/
  `sqli`/`redirect`/`eval_expr`/`idor`/`cred`/`coerce_auth`/`write_acl`) **and its
  RCE-as-equation table** (6 named equations an RCE must satisfy at least one of) →
  Strategist prompt, `14` §1, as a fallback reasoning method when no single
  high-severity bug exists but several lower-severity findings might chain (applied).
- **`client-reverse`'s packet-first-staging workflow** (replay-unchanged →
  mutate-one-field before ever reversing) → Operator prompt, `14` §3 (applied),
  together with a new Tier 1 dependency: a CDP-capable headless browser
  (Playwright/Puppeteer) for breakpoint-equivalent instrumentation and anti-bot-token
  minting (`AC-DEPENDENCY-17`, `08` — drafted).
- **`bug-bounty`'s "A→B Bug Signal Method"/Cluster Hunt Protocol** (confirm A → map
  sibling endpoints in the same controller/module → test siblings for the same
  pattern → chain → quantify blast radius → report once per chain) → Operator
  prompt, `14` §3, folded into the follow-on-task guidance alongside `FR-COUNCIL-10`
  (applied).
- **`bug-bounty`'s "Top 1% Hacker Mindset"** (Crown Jewel Thinking, Developer
  Empathy, Trust Boundary Mapping, Feature Interaction Thinking — a
  business-context/developer-psychology framing, distinct in kind from
  `bb-methodology`'s technical assumption-checklist) → Strategist prompt, `14` §1, as
  a complementary framing, not a replacement (applied).
- **`web2-recon`'s stack→bug-class routing table** (Rails→mass-assignment,
  Django→IDOR, Flask→SSTI, etc.) → Strategist prompt, `14` §1 (applied).
- **`web2-recon`'s source-disclosure/extraction technique class** (exposed
  `.git`/`.svn`/`.hg`/`.bzr`/`.DS_Store` dumping, `php://filter` source read,
  backup/temp/swap-file fuzzing) and **its packed-JS-bundle deobfuscation
  procedure** — folded into the Operator prompt's follow-on-task guidance, `14` §3,
  as part of the same chain-hunting addition above (applied) — not previously
  represented in `FR-TOOL`/`FR-COUNCIL` at all before this sweep.

All of the above are applied in `14` as of this document's writing (see `10`'s
decision-log entry #57), and the corresponding dependency entries
(`AC-DEPENDENCY-11..17`) are drafted in `08` — neither is deferred follow-up.

---

## Dependency Summary (for `08`)

New dependencies surfaced by this document, not previously in this system's scope:
Foundry (`forge`/`cast`/`anvil`) + third-party RPC endpoint access (`FR-WEB3-03`);
`adb`, `apktool`, `jadx`, `frida-tools`/`objection` (`FR-MOBILE-05`); `graphw00f`,
`clairvoyance`, `graphql-cop`, `gqlmap`, `wscat` (`FR-GRAPHQL-02`); `sisakulint`, `gh`
CLI (`FR-CICD-02`); `cewler`, hashcat rule files (`FR-CRED-01`); `interactsh-client`
(`FR-ARGUS-02`); a CDP-capable headless browser, Playwright or Puppeteer (for
`client-reverse`'s technique, listed above). Each has its own `AC-DEPENDENCY-11..17`
entry in `08`, drafted alongside this document — none deferred.
