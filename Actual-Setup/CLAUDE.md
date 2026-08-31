# Claude Bug Bounty — Plugin Guide

This repo is a Claude Code plugin for professional bug bounty hunting across HackerOne, Bugcrowd, Intigriti, and Immunefi.

## What's Here

### Skills (19 domains — load with `/bug-bounty`, `/web2-recon`, `/token-scan`, etc.)

| Skill | Domain |
|---|---|
| `skills/bug-bounty/` | Master workflow — recon to report, all vuln classes, LLM testing, chains |
| `skills/bb-methodology/` | **Hunting mindset + 5-phase non-linear workflow + tool routing + session discipline** |
| `skills/web2-recon/` | Subdomain enum, live host discovery, URL crawling, nuclei |
| `skills/web2-vuln-classes/` | 32 bug classes with bypass tables (SSRF, open redirect, file upload, Agentic AI, BFLA, NoSQLi, semantic confusion, header injection, XXE, WebSocket security, dependency confusion, padding oracle/crypto misuse) |
| `skills/security-arsenal/` | Payloads, bypass tables, gf patterns, always-rejected list |
| `skills/web3-audit/` | 10 smart contract bug classes, closure discipline for ruling candidates in/out, Foundry PoC template, pre-dive kill signals |
| `skills/meme-coin-audit/` | Meme coin rug pull detection, token authority checks, bonding curve exploits, LP attacks |
| `skills/report-writing/` | H1/Bugcrowd/Intigriti/Immunefi report templates, CVSS 3.1, human tone |
| `skills/triage-validation/` | Closure discipline (confirmed/ruled_out/open_proof_gap), 7-Question Gate, 4 gates, never-submit list, conditionally valid table, severity calibration |
| `skills/credential-attack/` | Password spray methodology — when/why, 4-stage pipeline, mode selection, lockout tactics, legal guardrails, pitfalls learned from live tests |
| `skills/mobile-pentest/` | Android/iOS app pentest — runtime-first proxy workflow, APK/IPA decompile for hidden endpoints + secrets, deeplink/exported-activity injection, WebView bridge, SSL pinning bypass |
| `skills/cicd-security/` | CI/CD pipeline hunting — GitHub Actions injection, secret exfil, self-hosted runner poisoning, OIDC abuse, supply chain attacks |
| `skills/graphql-audit/` | GraphQL hunting — introspection, field suggestions (clairvoyance), batching DoS, IDOR via aliasing, injection, auth bypass, depth bombs |
| `skills/diff-review/` | Diff-scoped PR/commit review — in-scope vs out-of-scope rules, how far to follow a change, validation without a live target |
| `skills/whitebox-code-recon/` | Source-first recon for engagements with code access — architecture/entry-point/schema mapping, then backward taint-hunts per vuln class before live testing |
| `skills/capability-chaining/` | Derive novel exploit chains when no known pattern fits — capability primitives (read/write/exec/ssrf/cred/idor), RCE-as-equation table, forward/backward state-space search |
| `skills/opt-in-advanced-techniques/` | ⚠️ **Opt-in only, not default** — broad-scope engagement framing, red-team anti-forensics (requires specific written authorization), narrow product-specific exploit patterns. Use only when explicitly invoked or an engagement's SOW/ROE explicitly authorizes it |
| `skills/argus/` | Six automated scanners for high-value web + LLM bug classes — CORS, CRLF/host-header, NoSQLi, JWT attacks, OOB confirmation (blind SSRF/XXE/SQLi/RCE/Log4Shell), LLM red-team corpus |
| `skills/client-reverse/` | Client-side request-signing / anti-bot token reversal — recover a sign/hmac/nonce field just enough to replay a request outside the client, packet-first staging, JS deobfuscation basics |

### Commands (39 slash commands)

> **Note:** All commands are prefixed to avoid conflicts with Claude Code's built-in commands.
> `/resume` is a reserved Claude Code command — use `/pickup` to continue a previous hunt.

| Command | Usage |
|---|---|
| `/recon` | `/recon target.com` — full recon pipeline |
| `/hunt` | `/hunt target.com` — start hunting |
| `/validate` | `/validate` — run 7-Question Gate on current finding |
| `/report` | `/report` — write submission-ready report |
| `/chain` | `/chain` — build A→B→C exploit chain |
| `/scope` | `/scope <asset>` — verify asset is in scope |
| `/scope-aggregate` | `/scope-aggregate <program>` — pull every in-scope asset across H1/Bugcrowd/Intigriti/YWH/Immunefi |
| `/triage` | `/triage` — quick 7-Question Gate |
| `/web3-audit` | `/web3-audit <contract.sol>` — smart contract audit |
| `/autopilot` | `/autopilot target.com --normal` — autonomous hunt loop |
| `/surface` | `/surface target.com` — ranked attack surface |
| `/pickup` | `/pickup target.com` — pick up previous hunt (was `/resume`) |
| `/remember` | `/remember` — log finding to hunt memory |
| `/intel` | `/intel target.com` — fetch CVE + disclosure intel |
| `/token-scan` | `/token-scan <contract>` — meme coin/token rug pull scanner |
| `/memory-gc` | `/memory-gc [--rotate|--purge-backups]` — inspect/rotate hunt-memory JSONL files (10MB cap, 3 backups) |
| `/secrets-hunt` | `/secrets-hunt --js-bundle <recon-dir>` — leaked-credential scan (trufflehog/noseyparker/gitleaks) |
| `/takeover` | `/takeover --recon <recon-dir>` — subdomain takeover candidates (dnsReaper/subjack) |
| `/cloud-recon` | `/cloud-recon --keyword <name>` — public S3/Azure/GCP + CloudFlare-bypass origin IPs |
| `/param-discover` | `/param-discover <url>` — find hidden HTTP parameters (Arjun/x8) |
| `/bypass-403` | `/bypass-403 <url>` — try header/method/encoding tricks against a 403/401 |
| `/arsenal` | `/arsenal [tool]` — list installed external tools or get an install hint |
| `/scan-cves` | `/scan-cves <host>` — focused nuclei CVE sweep (high/critical) + optional log4j-scan |
| `/wordlist-gen` | `/wordlist-gen <target>` — company-specific password wordlist (cewler + hashcat); requires `--with-credential-attack` |
| `/osint-employees` | `/osint-employees <target>` — employee names + emails (theHarvester + username-anarchy, opt-in LinkedIn); requires `--with-credential-attack` |
| `/breach-check` | `/breach-check <wordlist>` — HIBP k-anonymity rank wordlist by real-world breach count |
| `/spray` | `/spray <url> --mode http-form\|oauth\|o365\|okta --users <f> --passes <f>` — password spray with hard guards (typed-host confirm, lockout warn, audit log) |
| `/graphql-audit` | `/graphql-audit <url>` — full GraphQL audit: introspection, batching DoS, IDOR, injection, alias bomb, graphw00f fingerprint |
| `/diff-review` | `/diff-review [PR#\|sha\|base...head]` — diff-scoped security review of a PR/commit/branch, not a full repo audit |
| `/cors` | `/cors <url>` — CORS misconfig: origin reflection, null-origin, credentialed read, regex bypass |
| `/crlf` | `/crlf <url>` — CRLF/response-splitting + host-header injection (Set-Cookie canary) |
| `/nosqli` | `/nosqli <url>` — NoSQL injection: operator auth-bypass, `$where` time-based blind |
| `/jwt-scan` | `/jwt-scan <token>` — JWT alg:none, RS256→HS256 confusion, weak-secret crack (offline) |
| `/oob` | `/oob <url>` — out-of-band confirmation of blind SSRF/XXE/SQLi/RCE/Log4Shell (interactsh) |
| `/llm-redteam` | `/llm-redteam <endpoint>` — LLM red-team corpus: injection, jailbreak, prompt leak, exfil |
| `/domxss` | `/domxss "<url>" [--params q,name]` — headless-browser DOM XSS confirmation, only reports on actual execution |
| `/portscan` | `/portscan <host>` — non-HTTP service discovery (SSH, DBs, Redis, Docker API, RDP) |
| `/sast` | `/sast <path>` — Semgrep rulesets over fetched JS/source |
| `/screenshot` | `/screenshot -l urls.txt -o shots/` — self-contained HTML screenshot gallery for visual triage |

### Agents (9 specialized agents)

- `recon-agent` — subdomain enum + live host discovery
- `report-writer` — generates H1/Bugcrowd/Immunefi reports
- `validator` — 4-gate checklist on a finding
- `web3-auditor` — smart contract bug class analysis
- `chain-builder` — builds A→B→C exploit chains
- `autopilot` — autonomous hunt loop (scope→recon→rank→hunt→validate→report)
- `recon-ranker` — attack surface ranking from recon output + memory
- `token-auditor` — fast meme coin/token rug pull and security analysis
- `credential-hunter` — orchestrates wordlist-gen + osint-employees + breach-check; HARD STOPS at spray for human go/no-go

### Rules (always active)

- `rules/hunting.md` — 17 critical hunting rules
- `rules/reporting.md` — report quality rules
- `rules/vapt_report_format.md` — mandatory VAPT client PDF report format (cover page, sections, code blocks, prohibited content)

### Tools (Python/shell — in `tools/`)

- `tools/hunt.py` — master orchestrator
- `tools/recon_engine.sh` — subdomain + URL discovery (now with optional `nuclei` phase)
- `tools/vuln_scanner.sh` — XSS/SQLi/SSTI/MFA/SAML probe pipeline
- `tools/validate.py` — 4-gate finding validator
- `tools/learn.py` — CVE + disclosure intel
- `tools/intel_engine.py` — on-demand intel with memory context
- `tools/scope_checker.py` — deterministic scope safety checker
- `tools/scope_aggregator.sh` — multi-platform scope pull (bbscope + bounty-targets-data)
- `tools/secrets_hunter.sh` — trufflehog/noseyparker/gitleaks wrapper for FS/git/JS/GH-org
- `tools/takeover_scanner.sh` — dnsReaper/subjack subdomain-takeover scanner
- `tools/cloud_recon.sh` — S3Scanner + cloud_enum + CloudFail wrapper
- `tools/param_discovery.sh` — Arjun/x8 hidden-parameter discovery
- `tools/bypass_403.sh` — byp4xx + built-in 403/401 bypass matrix
- `tools/cve_scan.sh` — focused nuclei CVE-tag sweep + optional log4j-scan
- `tools/external_arsenal.sh` — installed-tool registry (~50 tools); other scripts source this for `_have <tool>`
- `tools/cicd_scanner.sh` — GitHub Actions workflow scanner (sisakulint wrapper, remote scan)
- `tools/token_scanner.py` — automated token red flag scanner (EVM + Solana)
- `tools/wordlist_engine.sh` — company-specific password wordlist generator (cewler + hashcat rules); requires `--with-credential-attack`
- `tools/osint_employees.sh` — employee names + email patterns for spray prep (theHarvester + username-anarchy, opt-in CrossLinked); requires `--with-credential-attack`
- `tools/breach_checker.py` — HIBP k-anonymity wordlist enrichment; ranks passwords by breach count (no API key, free)
- `tools/spray_orchestrator.sh` — password spray with typed-hostname guard + lockout warning + audit log; modes: http-form / oauth / o365 / okta (TREVOR); requires `--with-credential-attack` for TREVOR modes
- `tools/graphql_audit.sh` — 7-phase GraphQL audit: introspection + schema dump, graphw00f fingerprint, clairvoyance field discovery, batching DoS, alias bomb, gqlmap injection, graphql-cop checklist
- `tools/lead_board.py` — persistent recon→skill lead ledger (`ingest`/`show`/`next`/`touch`/`add`)
- `tools/cors_scanner.py` — CORS misconfig: origin reflection, null-origin, credentialed read, regex bypass
- `tools/crlf_scanner.py` — CRLF/response-splitting + host-header injection (Set-Cookie canary)
- `tools/nosqli_scanner.py` — NoSQL injection: operator auth-bypass, `$where` time-based blind
- `tools/jwt_scanner.py` — JWT alg:none, RS256→HS256 confusion, weak-secret crack (offline)
- `tools/oob_listener.py` — out-of-band confirmation of blind SSRF/XXE/SQLi/RCE/Log4Shell (interactsh)
- `tools/llm_redteam.py` — LLM red-team corpus: injection, jailbreak, prompt leak, exfil
- `tools/dom_xss_harness.py` — headless-browser DOM XSS confirmation, only reports on actual execution
- `tools/port_scanner.py` — non-HTTP service discovery (SSH, DBs, Redis, Docker API, RDP)
- `tools/sast_scan.py` — Semgrep rulesets over fetched JS/source, mapped into this toolkit's severity/confidence model
- `tools/visual_triage.py` — self-contained HTML screenshot gallery for visual triage
- `tools/eol_check.py` — end-of-life/lifecycle intel from endoflife.date for fingerprint pairs

### External tool references

- `wordlists/REFERENCES.md` — pointers to SecLists / OneListForAll / fuzz4bounty / PayloadsAllTheThings
- `skills/security-arsenal/REFERENCES.md` — methodology, writeup archives, dorks, key-verification, AI-security skill repos
- `skills/security-arsenal/METHODOLOGY_CHEATSHEET.md` — per-vuln quick-check tables distilled from HowToHunt + HolyTips + AllAboutBugBounty + KingOfBugBountyTips

### MCP Integrations (in `mcp/`)

- `mcp/burp-mcp-client/` — Burp Suite proxy integration
- `mcp/hackerone-mcp/` — HackerOne public API (Hacktivity, program stats, policy)

### Hunt Memory (in `memory/`)

- `memory/pattern_db.py` — cross-target pattern learning
- `memory/audit_log.py` — request audit log, rate limiter, circuit breaker
- `memory/rotation.py` — size-based JSONL rotation (10MB cap, keep 3 backups), auto-fired on append
- `memory/schemas.py` — schema validation for all data

## Start Here

```bash
claude
# /recon target.com
# /hunt target.com
# /validate   (after finding something)
# /report     (after validation passes)
```

## Install Skills

```bash
chmod +x install.sh && ./install.sh
```

## Critical Rules (Always Active)

1. READ FULL SCOPE before touching any asset
2. NEVER hunt theoretical bugs — "Can attacker do this RIGHT NOW?"
3. Run 7-Question Gate BEFORE writing any report
4. KILL weak findings fast — N/A hurts your validity ratio
5. 5-minute rule — nothing after 5 min = move on
6. NEVER redact evidence in a report, no matter how sensitive — see VAPT Standard §1.5

## VAPT Client Report Formatting Standard (Mandatory for All Future Reports)

Full spec: `rules/vapt_report_format.md` — the enforced format for every client-facing VAPT PDF report (myco.io, buypass.ai, and any future engagement): tone/typography, cover page + footer HTML/CSS, running footer, section/page-break rules, the six section playbooks, prohibited content, legacy formats to avoid, the informational-findings register, HTML retention, dark code-evidence-block spec, pre-render grep checks, and the canonical reference template. Read it in full before generating or editing any client VAPT report — do not improvise report formatting from memory.

Critical Rule #6 above (never redact evidence) is §1.5 of that file.
