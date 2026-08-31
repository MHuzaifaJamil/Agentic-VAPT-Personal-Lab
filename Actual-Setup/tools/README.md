# Tools

Python and shell scanner pipeline (~50 tools). Every tool checks whether its external dependency is installed — missing tools are skipped, never errors.

## Core Pipeline
| Tool | Purpose |
|:---|:---|
| `hunt.py` | Master orchestrator — wires all tools together |
| `recon_engine.sh` | Subdomain enum · live host probing · URL crawl · nuclei phase |
| `vuln_scanner.sh` | XSS · SQLi · SSTI · SSRF · MFA · SAML probe pipeline |
| `validate.py` | 4-gate finding validator with identity checks and curl PoC requirement |
| `scope_checker.py` | Deterministic scope safety check before any request |
| `lead_board.py` | Persistent recon→skill lead ledger (`ingest` / `show` / `next` / `touch` / `add`) |

## Vulnerability Scanners
| Tool | Purpose |
|:---|:---|
| `cors_scanner.py` | CORS misconfig — origin reflection, null-origin, credentialed read, suffix/prefix regex bypass |
| `crlf_scanner.py` | CRLF / response-splitting + host-header injection (Set-Cookie canary) |
| `nosqli_scanner.py` | NoSQL injection — operator auth-bypass, `$where` time-based blind |
| `jwt_scanner.py` | JWT alg:none, RS256→HS256 confusion, weak-secret crack (offline) |
| `oob_listener.py` | Out-of-band confirm of blind SSRF/XXE/SQLi/RCE/Log4Shell (interactsh) |
| `llm_redteam.py` | LLM red-team corpus — injection, jailbreak, prompt leak, exfil |
| `dom_xss_harness.py` | Headless-browser DOM XSS confirmation — only reports when a canary actually executes |
| `port_scanner.py` | Non-HTTP service discovery (SSH, DBs, Redis, Docker API, RDP) |
| `sast_scan.py` | Semgrep rulesets over fetched JS/source, mapped into this toolkit's severity/confidence model |
| `visual_triage.py` | Self-contained HTML screenshot gallery for fast visual triage across live hosts |
| `eol_check.py` | End-of-life / lifecycle intel from endoflife.date for fingerprint pairs |

## Recon & Discovery
| Tool | Purpose |
|:---|:---|
| `scope_aggregator.sh` | Multi-platform scope pull (bbscope + bounty-targets-data) |
| `recon_adapter.py` | Normalize recon output across tools |
| `param_discovery.sh` | Hidden HTTP parameters via Arjun · x8 |
| `cloud_recon.sh` | S3Scanner · cloud_enum · CloudFail for public bucket exposure |
| `takeover_scanner.sh` | Subdomain takeover via dnsReaper · subjack |
| `cve_scan.sh` | Focused nuclei CVE sweep (high/critical) + optional log4j-scan |
| `bypass_403.sh` | Header · method · encoding tricks against 403/401 |
| `secrets_hunter.sh` | trufflehog · noseyparker · gitleaks across FS/git/JS/GitHub org |

## Web3
| Tool | Purpose |
|:---|:---|
| `token_scanner.py` | Automated token red flag scanner (EVM + Solana) |

## Intelligence
| Tool | Purpose |
|:---|:---|
| `intel_engine.py` | CVE + disclosure intel with memory context |
| `learn.py` | On-demand target learning from disclosed reports |

## Memory & Session
| Tool | Purpose |
|:---|:---|
| `memory_gc.py` | Inspect and rotate hunt-memory JSONL files (10 MB cap, 3 backups) |
| `auth_session.py` | Auth header management across all tools |
| `credential_store.py` | Encrypted credential store for hunt sessions |

## Credential Attack (requires `--with-credential-attack`)
`wordlist_engine.sh` · `osint_employees.sh` · `breach_checker.py` · `spray_orchestrator.sh`

## Output Format

Scanner confidence states prepended to every finding:
- `[CONFIRMED]` — PoC-verified, real impact demonstrated
- `[POSSIBLE]` — strong signal, needs manual verification
- `[INFORMATIONAL]` — version/banner/config data, not a vulnerability
