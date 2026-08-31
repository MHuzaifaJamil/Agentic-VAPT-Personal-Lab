# Commands

39 slash commands installed into `~/.claude/commands/` by `install.sh`.

## Core Workflow
| Command | What It Does |
|:---|:---|
| `/recon` | Full recon pipeline — subdomain enum, live hosts, URL crawl, nuclei sweep |
| `/hunt` | Vulnerability testing — IDOR, SSRF, XSS, SQLi, auth bypass, logic flaws |
| `/validate` | 7-Question Gate + 4 pre-submission gates on the current finding |
| `/report` | Submission-ready report for H1 · Bugcrowd · Intigriti · Immunefi |
| `/autopilot` | Autonomous loop: scope → recon → hunt → validate → report |
| `/diff-review` | Diff-scoped security review of a PR/commit/branch |

## Recon & Enumeration
`/surface` `/scope-aggregate` `/cloud-recon` `/param-discover` `/secrets-hunt` `/takeover` `/scan-cves` `/bypass-403`

## Vulnerability Scanners
`/graphql-audit` `/cors` `/crlf` `/nosqli` `/jwt-scan` `/oob` `/llm-redteam` `/domxss` `/portscan` `/sast` `/screenshot`

| Command | What It Does |
|:---|:---|
| `/cors` | CORS misconfig — origin reflection, null-origin, credentialed read, suffix/prefix regex bypass |
| `/crlf` | CRLF / response-splitting + host-header injection (Set-Cookie canary) |
| `/nosqli` | NoSQL injection — operator auth-bypass, `$where` time-based blind |
| `/jwt-scan` | JWT alg:none, RS256→HS256 confusion, weak-secret crack (offline) |
| `/oob` | Out-of-band confirm of blind SSRF/XXE/SQLi/RCE/Log4Shell (interactsh) |
| `/llm-redteam` | LLM red-team corpus — injection, jailbreak, prompt leak, exfil |
| `/domxss` | Headless-browser DOM XSS confirmation — only reports when a canary actually executes |
| `/portscan` | Non-HTTP service discovery (SSH, DBs, Redis, Docker API, RDP) the HTTP-only pipeline misses |
| `/sast` | Semgrep rulesets over fetched JS/source, mapped into the toolkit's severity/confidence model |
| `/screenshot` | Self-contained HTML screenshot gallery for fast visual triage across live hosts |

## Smart Contract
`/web3-audit` `/token-scan`

## Credential Attack
`/wordlist-gen` `/osint-employees` `/breach-check` `/spray`

## Session & Utility
`/pickup` `/intel` `/chain` `/scope` `/triage` `/remember` `/memory-gc` `/arsenal`
