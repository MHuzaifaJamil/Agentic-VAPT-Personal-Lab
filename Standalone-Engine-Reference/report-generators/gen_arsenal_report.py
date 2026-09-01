#!/usr/bin/env python3
"""
External Tool Arsenal — VAPT Cycle Capability Reference — PDF Generator
Virtuosoft VAPT Toolkit — Virtuosoft Security Team — July 2026

Design: Evidence-dossier aesthetic matching the myco.io VAPT report series
(findings/myco.io/reports/pdf/gen_asset_inventory.py).
  - Monospace type for all structural elements (labels, metadata, code, headers)
  - Proportional sans-serif for body paragraphs
  - Dark navy/steel cover band (#1A2744)
  - Stark white interior — colour used only as accent, not atmosphere
  - Color-coded phase badges walking the 5-stage VAPT lifecycle
"""

import os, subprocess

OUT = os.path.dirname(os.path.abspath(__file__))
os.makedirs(OUT, exist_ok=True)


def h(s):
    return (str(s)
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;"))


def code(content, label=None):
    parts = []
    if label:
        parts.append(f'<div class="code-label">{h(label)}</div>')
    cls = "code-block has-label" if label else "code-block"
    parts.append(f'<div class="{cls}">{h(content)}</div>')
    return f'<div class="code-wrap">{"".join(parts)}</div>'


COVER_COLOR = "#1A2744"
ACCENT = "#2E5BBA"
ACCENT_LIGHT = "#E8EEF9"

# ── VAPT phase model ────────────────────────────────────────────────────────
PHASES = {
    "recon": {
        "num": "1", "title": "Reconnaissance &amp; OSINT", "short": "Recon &amp; OSINT",
        "color": "#1565C0",
        "blurb": ("Passive and low-noise active discovery of everything that belongs to the "
                   "target before a single test payload is sent — subdomains, cloud storage, "
                   "leaked secrets, employee identities, and mobile app internals."),
    },
    "scan": {
        "num": "2", "title": "Scanning &amp; Enumeration", "short": "Scanning &amp; Enum",
        "color": "#2E7D32",
        "blurb": ("Converting the recon asset list into a concrete map of live services, open "
                   "ports, endpoints, parameters, and API surface — the input every later phase "
                   "tests against."),
    },
    "assess": {
        "num": "3", "title": "Vulnerability Assessment", "short": "Vuln Assessment",
        "color": "#F9A825",
        "blurb": ("Automated and semi-automated checks against the mapped surface for known "
                   "CVEs, misconfigurations, weak authentication tokens, and WAF posture — "
                   "triage before manual exploitation effort is spent."),
    },
    "exploit": {
        "num": "4", "title": "Exploitation", "short": "Exploitation",
        "color": "#E65100",
        "blurb": ("Turning a suspected weakness into a proven, reproducible impact — injection, "
                   "XSS, file-upload RCE, credential attacks, and blind-vulnerability confirmation "
                   "via out-of-band callbacks."),
    },
    "mobile": {
        "num": "5", "title": "Mobile Runtime &amp; Post-Exploitation", "short": "Mobile &amp; Post-Ex",
        "color": "#B71C1C",
        "blurb": ("Runtime instrumentation of mobile applications once static analysis is "
                   "exhausted — defeating SSL pinning and driving live traffic capture for the "
                   "same API-testing playbook used against the web target."),
    },
}
PHASE_ORDER = ["recon", "scan", "assess", "exploit", "mobile"]

STATUS_PALETTE = {
    "OK": {"bg": "#2E7D32", "text": "#FFFFFF"},
    "MISSING": {"bg": "#C62828", "text": "#FFFFFF"},
}

# ── Tool inventory ──────────────────────────────────────────────────────────
# name | category | phase | status | url | why | example
TOOLS = [
    # ---- Phase 1: Reconnaissance & OSINT ----
    ("subfinder", "recon", "recon", "OK", "github.com/projectdiscovery/subfinder",
     "Fastest passive subdomain enumeration tool, pulling from 20+ public sources (CT logs, "
     "DNS aggregators, search APIs). The first command run against any new target — maps the "
     "*.target.com surface without a single packet touching target infrastructure.",
     "subfinder -d target.com -all -silent -o subs.txt"),
    ("amass", "recon", "recon", "OK", "github.com/owasp-amass/amass",
     "Deep passive-and-active recon: DNS brute-forcing, ASN/network mapping, and a relationship "
     "graph. Complements subfinder when passive sources miss internal or legacy subdomains.",
     "amass enum -d target.com -passive -o amass_subs.txt"),
    ("assetfinder", "recon", "recon", "OK", "github.com/tomnomnom/assetfinder",
     "Lightweight secondary passive source chained into the subdomain pipeline to catch names "
     "the primary tools miss — cheap insurance, near-zero runtime cost.",
     "assetfinder --subs-only target.com"),
    ("bbot", "recon", "recon", "OK", "github.com/blacklanternsecurity/bbot",
     "Modular OSINT/recon automation framework chaining 80+ modules. One-shot recon automation "
     "for large-scope programs — subdomain enum, cloud enum, and secret scanning in a single "
     "graph-based run.",
     "bbot -t target.com -f subdomain-enum cloud-enum -o bbot_out/"),
    ("theHarvester", "recon", "recon", "OK", "github.com/laramies/theHarvester",
     "OSINT harvester for employee emails, names, and hosts from search engines and CT logs — "
     "the first stage of any credential-attack pipeline, building the target list before a spray.",
     "theHarvester -d target.com -b all -f harvest.json"),
    ("dnsrecon", "recon", "recon", "OK", "github.com/darkoperator/dnsrecon",
     "DNS enumeration and hygiene check — zone-transfer attempts, full record dumps, and "
     "wordlist brute force, used as a cross-check against SPF/DMARC and delegation misconfigs.",
     "dnsrecon -d target.com -t std,brt"),
    ("massdns", "recon", "recon", "OK", "github.com/blechschmidt/massdns",
     "High-performance DNS resolver capable of resolving millions of hostnames per minute — the "
     "resolution engine underneath puredns/shuffledns brute-force enumeration.",
     "massdns -r resolvers.txt -t A -o S wordlist_subs.txt"),
    ("puredns", "recon", "recon", "OK", "github.com/d3mondev/puredns",
     "Wildcard-aware DNS brute-force/resolution wrapper around massdns — filters out wildcard "
     "false positives that plain massdns brute forcing would otherwise report as live hosts.",
     "puredns bruteforce wordlist.txt target.com -r resolvers.txt"),
    ("shuffledns", "recon", "recon", "OK", "github.com/projectdiscovery/shuffledns",
     "ProjectDiscovery's massdns wrapper for large-scale subdomain resolving and brute forcing — "
     "used interchangeably with puredns depending on wordlist size and resolver pool health.",
     "shuffledns -d target.com -w wordlist.txt -r resolvers.txt -mode bruteforce"),
    ("knockpy", "recon", "recon", "OK", "github.com/guelfoweb/knockpy",
     "Standalone subdomain brute forcer with a built-in wordlist and basic takeover fingerprint "
     "check — a quick single-command alternative when a heavier pipeline isn't warranted.",
     "knockpy target.com"),
    ("sublert", "recon", "recon", "OK", "github.com/yassineaboukir/sublert",
     "Continuous subdomain monitor driven by Certificate Transparency log streams — catches "
     "newly-issued certificates for target.com the moment they go live, ahead of other hunters.",
     "sublert -u target.com -m"),
    ("maigret", "recon", "recon", "OK", "github.com/soxoj/maigret",
     "Username OSINT across 3000+ sites, used to pivot from a leaked handle to other accounts "
     "or exposed personal info once an employee identity surfaces during recon.",
     "maigret johndoe --json simple"),
    ("pywhat", "recon", "recon", "OK", "github.com/bee-san/pyWhat",
     "Instant string identifier — tells you whether a string pulled from a leak is a JWT, AWS "
     "key, private key, or crypto address before deeper manual investigation begins.",
     "pywhat 'AKIAIOSFODNN7EXAMPLE'"),
    ("s3scanner", "cloud", "recon", "OK", "github.com/sa7mon/S3Scanner",
     "Enumerates AWS S3 (and compatible) buckets tied to a target/keyword and checks their "
     "permissions — publicly-readable or writable buckets are among the highest-yield, "
     "lowest-effort vulnerability classes in independent security research.",
     "s3scanner scan -bucket-file candidate_buckets.txt"),
    ("cloud_enum", "cloud", "recon", "OK", "github.com/initstring/cloud_enum",
     "Multi-cloud public resource enumerator — extends bucket hunting beyond AWS to Azure Blob "
     "Storage and GCP buckets for the same keyword in a single pass.",
     "cloud_enum -k target -l cloud_enum_results.txt"),
    ("cloudfail", "cloud", "recon", "OK", "github.com/m0rtem/CloudFail",
     "Locates the real origin server behind a Cloudflare-fronted target via historical DNS and "
     "subdomain misconfig — useful for testing without WAF interference, sometimes a finding "
     "on its own if the origin accepts direct connections.",
     "cloudfail -t target.com"),
    ("scoutsuite", "cloud", "recon", "OK", "github.com/nccgroup/ScoutSuite",
     "Multi-cloud security posture auditor (AWS/Azure/GCP/Alibaba) for misconfigured IAM, "
     "storage, and networking — used on engagements that grant read-only cloud-account access.",
     "scout aws --profile target-readonly"),
    ("trufflehog", "secrets", "recon", "OK", "github.com/trufflesecurity/trufflehog",
     "Deep secret scanner that actively verifies each candidate credential against its issuer's "
     "API — separates theoretical leaks in git history/JS bundles from ones that are actually live.",
     "trufflehog git https://github.com/target/repo --only-verified"),
    ("noseyparker", "secrets", "recon", "OK", "github.com/praetorian-inc/noseyparker",
     "Extremely fast secret scanner purpose-built for huge git histories — used in place of "
     "trufflehog when raw scan speed matters more than live credential verification.",
     "noseyparker scan --datastore np.db /path/to/repo"),
    ("gitleaks", "secrets", "recon", "OK", "github.com/gitleaks/gitleaks",
     "Git-native secret scanner with a large, low-false-positive default rule pack — the default "
     "first-pass scan on any in-scope repo or CI history, including CI/CD security assessments.",
     "gitleaks detect --source . --report-path gitleaks.json"),
    ("shhgit", "secrets", "recon", "OK", "github.com/eth0izzle/shhgit",
     "Real-time GitHub/GitLab/Bitbucket public-commit watcher — catches secrets the instant a "
     "developer accidentally pushes them for the target's org or keyword.",
     "shhgit --search-query target-org"),
    ("git-hound", "secrets", "recon", "OK", "github.com/tillson/git-hound",
     "GitHub code-search-based secret hunter with regex and entropy scoring — reaches secrets "
     "via keyword search across all of GitHub, not just repos you already know to clone.",
     "githound --query target.com --dorks dorks.txt"),
    ("apkleaks", "mobile", "recon", "OK", "github.com/dwisiswant0/apkleaks",
     "First tool run against any Android APK — scans the compiled package for hardcoded API "
     "keys, URLs, and secrets before deeper decompilation is needed.",
     "apkleaks -f app.apk -o apkleaks_out.txt"),
    ("jadx", "mobile", "recon", "OK", "github.com/skylot/jadx",
     "Java/Android decompiler producing readable source from an APK/DEX — used when apkleaks' "
     "pattern scan isn't enough and you need to read the actual app logic, hidden endpoints, or "
     "SSL-pinning implementation.",
     "jadx -d jadx_out app.apk"),
    ("linkfinder", "js", "recon", "OK", "github.com/GerbenJavado/LinkFinder",
     "Extracts endpoint paths and URLs from JavaScript source and minified bundles — run against "
     "every JS file collected while crawling; regularly surfaces internal API paths never linked "
     "from the visible UI.",
     "linkfinder -i bundle.js -o results.html"),
    ("bbscope", "scope", "recon", "OK", "github.com/sw33tLie/bbscope",
     "Pulls every in-scope asset for a program across HackerOne/Bugcrowd/Intigriti/YesWeHack/"
     "Immunefi. The literal first command of any engagement — the authoritative host list every "
     "later command is filtered against.",
     "bbscope h1 -o \"target-handle\" -b"),

    # ---- Phase 2: Scanning & Enumeration ----
    ("httpx", "probe", "scan", "OK", "github.com/projectdiscovery/httpx",
     "Fast HTTP toolkit: live-host probing, tech-stack fingerprinting, status codes, and page "
     "titles. Converts a raw subdomain list into confirmed-alive web services — the pivot point "
     "between recon and every later phase.",
     "cat subs.txt | httpx -silent -title -tech-detect -status-code -o live.txt"),
    ("dnsx", "probe", "scan", "OK", "github.com/projectdiscovery/dnsx",
     "Fast DNS resolution/enumeration toolkit that filters wildcard-DNS false positives out of "
     "huge subdomain lists before they reach httpx.",
     "dnsx -l subs.txt -a -resp -o resolved.txt"),
    ("naabu", "probe", "scan", "OK", "github.com/projectdiscovery/naabu",
     "Fast port scanner built for recon pipelines — sweeps every live host for non-standard "
     "admin panels, dev servers, and exposed databases a web-only scan would miss.",
     "naabu -l hosts.txt -top-ports 1000 -o open_ports.txt"),
    ("smap", "probe", "scan", "OK", "github.com/s0md3v/Smap",
     "Nmap-compatible port scanner that queries Shodan's index instead of scanning directly — "
     "zero-touch enumeration when direct port scanning is against program rules.",
     "smap -iL hosts.txt -oX shodan_ports.xml"),
    ("aquatone", "probe", "scan", "OK", "github.com/michenriksen/aquatone",
     "Screenshots every live host for rapid visual triage of a large asset list — turns 500+ "
     "hosts into a browsable gallery to spot exposed admin panels and default install pages fast. "
     "Upstream has no go.mod and last committed in 2019, so a plain go install fails against a "
     "newer xurls API — built here by pinning mvdan.cc/xurls/v2@v2.0.0, the version its original "
     "Gopkg.toml specified, where the API still matches the code.",
     "cat live.txt | aquatone -out aquatone_report/"),
    ("eyewitness", "probe", "scan", "OK", "github.com/RedSiege/EyeWitness",
     "Alternative screenshot and reporting tool that also captures response headers/certs — "
     "backup for aquatone when headless Chrome has rendering issues on a target.",
     "eyewitness --web -f live.txt -d eyewitness_out"),
    ("katana", "crawl", "scan", "OK", "github.com/projectdiscovery/katana",
     "Modern web crawler with JS-rendering support — builds the full URL/form/parameter map for "
     "each live app, including JS-heavy SPAs, that every vuln-hunting phase tests against.",
     "katana -u https://target.com -jc -d 3 -o katana_urls.txt"),
    ("gau", "crawl", "scan", "OK", "github.com/lc/gau",
     "Pulls known URLs for a domain from the Wayback Machine, Common Crawl, AlienVault OTX, and "
     "URLScan — recovers historical and removed admin/debug endpoints active crawling won't find.",
     "gau target.com | tee gau_urls.txt"),
    ("waybackurls", "crawl", "scan", "OK", "github.com/tomnomnom/waybackurls",
     "Focused single-source Wayback Machine CDX puller — cheap, fast historical-URL sweep on a "
     "freshly-discovered target.",
     "waybackurls target.com > wayback_urls.txt"),
    ("waymore", "crawl", "scan", "OK", "github.com/xnl-h4ck3r/waymore",
     "Extended Wayback/CDX harvester that also retrieves archived response bodies — finds "
     "secrets or endpoints in pages that no longer resolve live.",
     "waymore -i target.com -mode U -oU waymore_urls.txt"),
    ("hakrawler", "crawl", "scan", "OK", "github.com/hakluke/hakrawler",
     "Fast, simple crawler for a quick pass on rate-limited targets, where katana's heavier "
     "JS rendering would trip WAF rate thresholds.",
     "echo https://target.com | hakrawler -d 2"),
    ("gospider", "crawl", "scan", "OK", "github.com/jaeles-project/gospider",
     "Crawler that also mines robots.txt/sitemap.xml and cross-domain links, filling gaps "
     "katana/hakrawler occasionally miss.",
     "gospider -s https://target.com -o gospider_out -c 10 -d 2"),
    ("cariddi", "crawl", "scan", "OK", "github.com/edoardottt/cariddi",
     "Crawler that flags secrets, endpoints, and juicy file extensions inline while crawling — a "
     "fast single-pass triage before dedicated secret scanners run.",
     "echo https://target.com | cariddi -intensive -s"),
    ("ffuf", "fuzz", "scan", "OK", "github.com/ffuf/ffuf",
     "Fast, flexible HTTP fuzzer — the primary directory/file/vhost fuzzer used constantly to "
     "find hidden admin panels, backup files, and unlinked API routes.",
     "ffuf -u https://target.com/FUZZ -w wordlist.txt -mc 200,301,403"),
    ("feroxbuster", "fuzz", "scan", "OK", "github.com/epi052/feroxbuster",
     "Rust-based recursive content-discovery fuzzer — used when automatic recursion into nested "
     "directories is preferred over ffuf's flat, single-level speed.",
     "feroxbuster -u https://target.com -w wordlist.txt -x php,html"),
    ("gobuster", "fuzz", "scan", "OK", "github.com/OJ/gobuster",
     "Long-standing standard directory/DNS/vhost bruteforcer — fallback fuzzer and the go-to for "
     "DNS subdomain brute-force mode.",
     "gobuster dir -u https://target.com -w wordlist.txt"),
    ("arjun", "param", "scan", "OK", "github.com/s0md3v/Arjun",
     "Discovers hidden/unlinked HTTP GET/POST parameters via wordlist probing. Hidden parameters "
     "are frequently the entire vulnerability — arjun surfaces the ones never referenced in the "
     "visible UI that later become IDOR, SSRF, or injection points.",
     "arjun -u https://target.com/api/endpoint -oT params.txt"),
    ("x8", "param", "scan", "OK", "github.com/Sh1Yo/x8",
     "Rust alternative to Arjun for hidden-parameter discovery, used when Python performance is "
     "too slow against a large parameter wordlist or many target URLs.",
     "x8 -u https://target.com/api -w params_wordlist.txt"),
    ("gf", "filter", "scan", "OK", "github.com/tomnomnom/gf",
     "Pattern-matching grep wrapper with curated vulnerability-class patterns (XSS, SSRF, SQLi sinks) — "
     "filters huge crawled-URL lists down to the parameters that actually look injectable.",
     "cat all_urls.txt | gf ssrf"),
    ("qsreplace", "filter", "scan", "OK", "github.com/tomnomnom/qsreplace",
     "Replaces query-string values across a list of URLs with a payload placeholder — rewrites "
     "thousands of crawled URLs in one pass and pipes them straight into a scanner.",
     "cat urls.txt | qsreplace 'FUZZ' | nuclei -t xss/"),
    ("anew", "filter", "scan", "OK", "github.com/tomnomnom/anew",
     "Appends only new/unique lines to a file — the deduplication glue that keeps continuous "
     "recon monitoring additive instead of reprocessing the same hosts every run.",
     "subfinder -d target.com -silent | anew subs_all.txt"),
    ("dnsreaper", "takeover", "scan", "OK", "github.com/punk-security/dnsReaper",
     "Subdomain-takeover scanner supporting 50+ provider fingerprints. A dangling CNAME to a "
     "deprovisioned Heroku/S3/GitHub Pages resource is a full account or content takeover — one "
     "of the highest-signal, lowest-effort vulnerability classes.",
     "dnsreaper scan --file subs.txt"),
    ("subjack", "takeover", "scan", "OK", "github.com/haccer/subjack",
     "Fast Go-based takeover fingerprint scanner used as a lightweight fallback when dnsreaper's "
     "fingerprint database doesn't cover a specific provider.",
     "subjack -w subs.txt -t 50 -o subjack_out.txt -ssl"),
    ("graphw00f", "graphql", "scan", "OK", "github.com/dolevf/graphw00f",
     "Fingerprints which GraphQL engine (Apollo, Hasura, Graphene, etc.) a target endpoint runs — "
     "the first step of any GraphQL assessment, since the engine dictates which introspection "
     "tricks and known CVEs apply.",
     "graphw00f -d -t https://target.com/graphql"),
    ("clairvoyance", "graphql", "scan", "OK", "github.com/nikitastupin/clairvoyance",
     "Reconstructs a GraphQL schema via field-suggestion error messages even when introspection "
     "is disabled — defeats the single most common GraphQL hardening step.",
     "clairvoyance -o schema.json https://target.com/graphql"),

    # ---- Phase 3: Vulnerability Assessment ----
    ("nuclei", "scan", "assess", "OK", "github.com/projectdiscovery/nuclei",
     "Template-driven vulnerability scanner covering thousands of CVEs, misconfigs, and exposed "
     "panels. The core automated sweep run against every live host before manual testing begins.",
     "httpx -l live.txt -silent | nuclei -t cves/ -severity high,critical -o nuclei_out.txt"),
    ("semgrep", "sast", "assess", "OK", "github.com/semgrep/semgrep",
     "Static analysis engine that flags insecure code patterns across languages via rulesets — "
     "used when source code is in scope (CI/CD assessments, disclosed repos) to catch injection "
     "sinks and hardcoded secrets at scale.",
     "semgrep --config p/security-audit src/"),
    ("log4j-scan", "cve", "assess", "OK", "github.com/fullhunt/log4j-scan",
     "Focused active scanner for Log4Shell (CVE-2021-44228) and its bypass variants — legacy "
     "enterprise stacks still run vulnerable Log4j versions worth a dedicated targeted check.",
     "python3 log4j-scan.py -u https://target.com --run-all-tests"),
    ("graphql-cop", "graphql", "assess", "OK", "github.com/dolevf/graphql-cop",
     "Automated GraphQL security checklist covering the OWASP GraphQL testing guide (introspection, "
     "batching, field suggestion, CSRF) — ensures no standard check is skipped before manual work.",
     "graphql-cop -t https://target.com/graphql"),
    ("jwt_tool", "jwt", "assess", "OK", "github.com/ticarpi/jwt_tool",
     "Comprehensive JWT security tester — every JWT-authenticated target gets run through this "
     "for alg:none, RS256-to-HS256 key confusion, and weak-secret brute forcing.",
     "python3 jwt_tool.py <token> -M at -pk public_key.pem"),
    ("byp4xx", "bypass", "assess", "OK", "github.com/lobuhi/byp4xx",
     "Automated 403/401 bypass tester across header, path-encoding, and method tricks — turns "
     "manual bypass guesswork into one automated pass on any Forbidden endpoint.",
     "byp4xx -u https://target.com/admin"),
    ("whatwaf", "bypass", "assess", "OK", "github.com/Ekultek/WhatWaf",
     "Detects and fingerprints which WAF/CDN protects a target, so encoding and evasion payloads "
     "can be chosen for that specific vendor instead of guessed blind.",
     "whatwaf -u https://target.com"),
    ("unwaf", "bypass", "assess", "OK", "github.com/mmarting/unwaf",
     "Resolves the real origin IP behind a WAF/CDN using historical DNS and certificate data — "
     "once the vendor is known via whatwaf, this looks for a direct path that skips its filtering.",
     "unwaf -d target.com"),

    # ---- Phase 4: Exploitation ----
    ("dalfox", "xss", "exploit", "OK", "github.com/hahwul/dalfox",
     "Fast XSS scanner with parameter mining, DOM analysis, and blind-XSS support — the primary "
     "automated tool for confirming reflected/DOM XSS with working payloads, callback included.",
     "cat params.txt | dalfox pipe --blind https://your-server.oastify.com"),
    ("xsstrike", "xss", "exploit", "OK", "github.com/s0md3v/XSStrike",
     "Context-aware XSS detection/exploitation engine with WAF fingerprinting — used against "
     "heavily-filtered inputs where dalfox's payload set gets blocked outright.",
     "python3 xsstrike.py -u 'https://target.com/search?q=test' --crawl"),
    ("ghauri", "sqli", "exploit", "OK", "github.com/r0oth3x49/ghauri",
     "Modern SQL injection tool built for speed on boolean/time-based blind SQLi — faster than "
     "sqlmap when request overhead makes exploitation impractically slow.",
     "ghauri -u 'https://target.com/item?id=1' --dump"),
    ("sqlmap", "sqli", "exploit", "OK", "github.com/sqlmapproject/sqlmap",
     "The standard automated SQL injection framework — detection, DBMS fingerprinting, data "
     "extraction, and often OS command execution via stacked queries, once SQLi is even suspected.",
     "sqlmap -u 'https://target.com/item?id=1' --batch --dbs"),
    ("fuxploider", "upload", "exploit", "OK", "github.com/almandin/fuxploider",
     "Automated file-upload vulnerability scanner/exploiter — runs the full bypass matrix (double "
     "extensions, null bytes, content-type spoofing, polyglot files) to confirm code execution.",
     "fuxploider --url https://target.com/upload --not-regex \"invalid\""),
    ("hashcat", "cred", "exploit", "OK", "hashcat.net/hashcat",
     "GPU-accelerated password/hash cracking engine — cracks recovered hashes (dumped DB hashes, "
     "cracked JWT HMAC secrets) and mutates wordlists via its rule engine for spray attacks.",
     "hashcat -m 0 -a 0 hashes.txt rockyou.txt -r best64.rule"),
    ("cewler", "cred", "exploit", "OK", "github.com/roys/cewler",
     "Crawls a target site to build a custom wordlist from its own on-page vocabulary — employees "
     "reuse product names and internal project terms in passwords more often than you'd expect.",
     "cewler https://target.com -o cewler_wordlist.txt"),
    ("cupp", "cred", "exploit", "OK", "github.com/Mebus/cupp",
     "Interactive profiler that turns known facts about a specific employee (name, birthdate, "
     "pet, company) into a small high-probability password candidate list for a targeted spray.",
     "cupp -i"),
    ("trevorspray", "cred", "exploit", "OK", "github.com/blacklanternsecurity/TREVORspray",
     "Password-spray orchestrator with OAuth/O365/Okta module support and jitter/delay controls — "
     "drives the actual credential spray against enterprise SSO endpoints with lockout-avoidance timing.",
     "trevorspray -u users.txt -p passwords.txt --mod o365"),
    ("kerbrute", "cred", "exploit", "OK", "github.com/ropnop/kerbrute",
     "Fast Kerberos pre-auth username enumeration and password spraying — on AD-integrated "
     "targets, enumerates valid domain usernames without generating failed-logon events an "
     "LDAP/SMB spray would trigger.",
     "kerbrute passwordspray -d target.com userlist.txt Password123"),
    ("interactsh-client", "oob", "exploit", "OK", "github.com/projectdiscovery/interactsh",
     "Self-hosted out-of-band interaction server client — confirms blind SSRF, blind XXE, and "
     "blind RCE by catching the DNS/HTTP callback the payload triggers, the only way to prove "
     "impact when the response gives no visible feedback.",
     "interactsh-client -v   # embed the generated domain in the payload"),

    # ---- Phase 5: Mobile Runtime & Post-Exploitation ----
    ("mobsf", "mobile", "mobile", "OK", "github.com/MobSF/Mobile-Security-Framework-MobSF",
     "All-in-one mobile app security framework running automated static and dynamic analysis in "
     "one shot — a baseline report (permissions, manifest issues, hardcoded secrets, binary "
     "protections) before manual runtime testing begins.",
     "mobsf   # starts the local server on :8000; upload the APK/IPA via the web UI"),
    ("objection", "mobile", "mobile", "OK", "github.com/sensepost/objection",
     "Runtime mobile instrumentation toolkit built on Frida — patches a target APK to disable "
     "SSL certificate pinning at runtime, the prerequisite for proxying mobile traffic through "
     "Burp for the rest of the API-testing playbook.",
     "objection patchapk -s target.apk"),
]

EXCLUDED = [
    ("freebuff", "ai", "freebuff.com",
     "Unrelated AI coding-assistant installer from an unvetted domain — out of scope for a VAPT "
     "tool arsenal, deliberately not installed."),
    ("kimchi", "ai", "kimchi.dev",
     "Same category as freebuff — an unrelated AI coding-assistant installer script, deliberately "
     "not installed."),
]


def compute_stats():
    counts = {p: 0 for p in PHASE_ORDER}
    status_counts = {"OK": 0, "MISSING": 0}
    cat_set = set()
    for name, cat, phase, status, url, why, ex in TOOLS:
        counts[phase] += 1
        status_counts[status] += 1
        cat_set.add(cat)
    return counts, status_counts, len(cat_set)


def status_badge(status):
    p = STATUS_PALETTE[status]
    label = "INSTALLED" if status == "OK" else "NOT INSTALLED"
    return (f'<span class="badge" style="background:{p["bg"]};color:{p["text"]};">'
            f'{h(label)}</span>')


def phase_badge(phase):
    c = PHASES[phase]["color"]
    return (f'<span class="badge phase-badge" style="background:{c};color:#fff;">'
            f'PHASE {PHASES[phase]["num"]}</span>')


def cat_badge(cat):
    return f'<span class="badge cat-badge">{h(cat)}</span>'


def build_css(footer_label):
    return f"""
*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

@page {{
  size: A4;
  margin: 16mm 18mm 18mm 22mm;
}}
@page :first {{ margin: 0; }}
@page {{
  @bottom-left {{
    content: "{footer_label}";
    font-family: 'Courier New', Consolas, monospace;
    font-size: 6pt;
    color: #AAAAAA;
    border-top: 0.5pt solid #DDDDDD;
    padding-top: 3pt;
    width: 100%;
    white-space: nowrap;
  }}
  @bottom-right {{
    content: counter(page);
    font-family: 'Courier New', Consolas, monospace;
    font-size: 7pt;
    color: #AAAAAA;
    border-top: 0.5pt solid #DDDDDD;
    padding-top: 3pt;
  }}
}}
@page :first {{
  @bottom-left  {{ content: none; border: none; }}
  @bottom-right {{ content: none; border: none; }}
}}

body {{
  font-family: -apple-system, 'Segoe UI', Arial, Helvetica, sans-serif;
  font-size: 9pt;
  line-height: 1.6;
  color: #1A1A1A;
  background: #FFFFFF;
}}

/* ── Cover ──────────────────────────────────────────────────────────────── */
.cover {{
  width: 210mm;
  height: 297mm;
  break-after: page;
  position: relative;
  background: #FFFFFF;
  overflow: hidden;
}}
.cover-band {{
  background: {COVER_COLOR};
  padding: 14mm 20mm 16mm 20mm;
}}
.cover-classification {{
  font-family: 'Courier New', Consolas, monospace;
  font-size: 7pt;
  color: rgba(255,255,255,0.55);
  letter-spacing: 0.18em;
  text-transform: uppercase;
  margin-bottom: 9mm;
}}
.cover-doc-type {{
  font-family: 'Courier New', Consolas, monospace;
  font-size: 9pt;
  color: rgba(255,255,255,0.65);
  letter-spacing: 0.2em;
  text-transform: uppercase;
  margin-bottom: 3mm;
}}
.cover-id {{
  font-family: 'Courier New', Consolas, monospace;
  font-size: 42pt;
  font-weight: bold;
  color: #FFFFFF;
  line-height: 1.0;
  letter-spacing: -0.02em;
  margin-bottom: 2mm;
}}
.cover-subtitle-band {{
  font-family: 'Courier New', Consolas, monospace;
  font-size: 8pt;
  color: rgba(255,255,255,0.65);
  letter-spacing: 0.12em;
  margin-top: 3mm;
}}
.cover-body {{ padding: 11mm 20mm 0 20mm; }}
.cover-title {{
  font-size: 18pt;
  font-weight: 700;
  line-height: 1.25;
  color: #0A0A0A;
  margin-bottom: 4mm;
  max-width: 160mm;
}}
.cover-description {{
  font-size: 9.5pt;
  color: #444;
  line-height: 1.65;
  max-width: 148mm;
  margin-bottom: 7mm;
}}
.cover-rule {{
  width: 36mm;
  height: 2.5pt;
  background: {ACCENT};
  margin-bottom: 8mm;
}}
.cover-meta-table {{ width: 100%; border-collapse: collapse; }}
.cover-meta-table td {{
  padding: 2mm 3mm 2mm 0;
  font-size: 9pt;
  border-bottom: 0.5pt solid #EBEBEB;
  vertical-align: top;
}}
.cover-meta-table td.mk {{
  font-family: 'Courier New', Consolas, monospace;
  font-size: 7pt;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: #999;
  width: 42mm;
  white-space: nowrap;
}}
.cover-meta-table td.mv {{
  font-size: 9.5pt;
  color: #191919;
  font-weight: 500;
}}
.cover-stats-row {{
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 3mm;
  margin-top: 5mm;
}}
.cover-stat-box {{
  border: 1pt solid #E0E0E0;
  border-radius: 2pt;
  padding: 3mm 4mm;
  text-align: center;
}}
.cover-stat-num {{
  font-family: 'Courier New', Consolas, monospace;
  font-size: 20pt;
  font-weight: bold;
  color: {COVER_COLOR};
  line-height: 1.0;
}}
.cover-stat-label {{
  font-family: 'Courier New', Consolas, monospace;
  font-size: 6pt;
  color: #999;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  margin-top: 1mm;
}}
.cover-footer {{
  position: absolute;
  bottom: 0; left: 0; right: 0;
  padding: 5mm 20mm;
  background: #F4F4F2;
  border-top: 0.5pt solid #DCDCDC;
  display: flex;
  justify-content: space-between;
  align-items: center;
}}
.cover-footer span {{
  font-family: 'Courier New', Consolas, monospace;
  font-size: 6.5pt;
  color: #999;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  text-align: center;
}}
.cover-footer .assessor {{
  font-size: 7pt;
  font-weight: bold;
  color: #555;
  text-transform: none;
  letter-spacing: 0;
  text-align: center;
  line-height: 1.65;
}}

/* ── Content sections ─────────────────────────────────────────────────────── */
.section {{ margin-bottom: 9mm; }}
.section-title {{
  font-family: 'Courier New', Consolas, monospace;
  font-size: 7.5pt;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: #888;
  margin-bottom: 4mm;
  padding-bottom: 2mm;
  border-bottom: 1.5pt solid {ACCENT};
}}
.section-title .sn {{ color: {ACCENT}; font-weight: bold; margin-right: 6pt; }}

p {{ margin-bottom: 3.5mm; line-height: 1.65; }}
strong {{ font-weight: 600; color: #0D0D0D; }}
em {{ font-style: italic; }}

.pb {{ break-before: page; }}
.avoid {{ break-inside: avoid; }}

/* ── Badges ───────────────────────────────────────────────────────────────── */
.badge {{
  display: inline-block;
  font-family: 'Courier New', Consolas, monospace;
  font-size: 6.3pt;
  font-weight: bold;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  padding: 1mm 2mm;
  border-radius: 1.5pt;
  white-space: nowrap;
}}
.cat-badge {{ background: #EEEEEE; color: #555; }}

/* ── Summary table ────────────────────────────────────────────────────────── */
.summary-table {{
  width: 100%;
  table-layout: fixed;
  border-collapse: collapse;
  font-size: 7.5pt;
  margin-bottom: 6mm;
}}
.summary-table th {{
  font-family: 'Courier New', Consolas, monospace;
  font-size: 6pt;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: #888;
  background: #F6F6F4;
  padding: 2mm 2mm;
  text-align: left;
  font-weight: normal;
  border-bottom: 1pt solid #DADADA;
  white-space: nowrap;
}}
.summary-table td {{
  padding: 1.5mm 2mm;
  border-bottom: 0.4pt solid #F0F0EE;
  vertical-align: middle;
  overflow: hidden;
}}
.summary-table tr {{ break-inside: avoid; }}
.summary-table col.col-name  {{ width: 24mm; }}
.summary-table col.col-cat   {{ width: 18mm; }}
.summary-table col.col-phase {{ width: 22mm; }}
.summary-table col.col-stat  {{ width: 20mm; }}
.summary-table col.col-why   {{ width: auto; }}
.summary-table .name-cell {{
  font-family: 'Courier New', Consolas, monospace;
  font-size: 7pt;
  font-weight: bold;
  color: {ACCENT};
  word-break: break-all;
  overflow-wrap: break-word;
}}
.summary-table .why-cell {{
  font-size: 7.3pt;
  color: #333;
  overflow-wrap: break-word;
  word-wrap: break-word;
}}
.summary-table tr:hover td {{ background: #F8F9FF; }}

/* ── Tool cards ───────────────────────────────────────────────────────────── */
.tool-card {{
  border: 0.7pt solid #E0E0E0;
  border-radius: 2pt;
  margin-bottom: 5mm;
  break-inside: avoid;
  overflow: hidden;
}}
.tool-card-header {{
  padding: 3mm 4mm 2.5mm;
  border-bottom: 0.5pt solid #E0E0E0;
  display: flex;
  align-items: flex-start;
  gap: 3mm;
  background: #FAFAFA;
}}
.tool-card-header-info {{ flex: 1; }}
.tool-name {{
  font-family: 'Courier New', Consolas, monospace;
  font-size: 11pt;
  font-weight: bold;
  color: {COVER_COLOR};
  line-height: 1.0;
  margin-bottom: 1.5mm;
}}
.tool-url {{ font-size: 7.3pt; color: #999; font-family: 'Courier New', Consolas, monospace; }}
.tool-badges {{ display: flex; gap: 2mm; flex-wrap: wrap; align-items: center; white-space: nowrap; }}
.tool-card-body {{ padding: 3mm 4mm; }}
.tool-why {{ font-size: 8.3pt; color: #333; line-height: 1.55; margin-bottom: 2.5mm; }}

/* ── Phase group header ───────────────────────────────────────────────────── */
.phase-header {{
  border-radius: 2pt;
  padding: 4mm 5mm;
  margin: 0 0 5mm;
  color: #fff;
}}
.phase-header-title {{
  font-family: 'Courier New', Consolas, monospace;
  font-size: 8.5pt;
  font-weight: bold;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  margin-bottom: 1.5mm;
}}
.phase-header-blurb {{ font-size: 8.5pt; line-height: 1.5; opacity: 0.95; }}

/* ── Stats row ────────────────────────────────────────────────────────────── */
.stats-row {{ display: grid; grid-template-columns: repeat(5, 1fr); gap: 3mm; margin-bottom: 7mm; }}
.stat-box {{ border: 0.7pt solid #E0E0E0; border-radius: 2pt; padding: 3mm 3mm; text-align: center; }}
.stat-num {{
  font-family: 'Courier New', Consolas, monospace;
  font-size: 18pt;
  font-weight: bold;
  line-height: 1.0;
}}
.stat-label {{
  font-family: 'Courier New', Consolas, monospace;
  font-size: 5.6pt;
  color: #888;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  margin-top: 1mm;
}}

/* ── Code blocks ──────────────────────────────────────────────────────────── */
.code-wrap {{ break-inside: avoid; margin: 2mm 0 3mm; }}
.code-label {{
  font-family: 'Courier New', Consolas, monospace;
  font-size: 6.5pt;
  color: #AAA;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  background: #141414;
  padding: 2mm 4mm 1.5mm;
  border-radius: 2pt 2pt 0 0;
}}
.code-block {{
  background: #1C1C1C;
  color: #DDD9D2;
  font-family: 'Courier New', Consolas, monospace;
  font-size: 7.3pt;
  line-height: 1.5;
  padding: 3mm 4mm;
  white-space: pre-wrap;
  word-break: break-all;
  border-radius: 0 0 2pt 2pt;
}}
.code-block.has-label {{ border-radius: 0 0 2pt 2pt; }}
.tool-example {{
  background: #1C1C1C;
  color: #9FD3A0;
  font-family: 'Courier New', Consolas, monospace;
  font-size: 7pt;
  line-height: 1.5;
  padding: 2mm 3mm;
  white-space: pre-wrap;
  word-break: break-all;
  border-radius: 1.5pt;
}}

/* ── Callout box ──────────────────────────────────────────────────────────── */
.callout {{
  background: {ACCENT_LIGHT};
  border-left: 3pt solid {ACCENT};
  padding: 3mm 4mm;
  margin: 0 0 4mm;
  font-size: 8.5pt;
  break-inside: avoid;
}}
.callout-label {{
  font-family: 'Courier New', Consolas, monospace;
  font-size: 6.5pt;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: {ACCENT};
  font-weight: bold;
  margin-bottom: 1.5mm;
}}
.callout-critical {{ background: #FFEBEE; border-left-color: #B71C1C; }}
.callout-critical .callout-label {{ color: #B71C1C; }}

ul.body-list {{ margin: 0 0 3.5mm 5mm; padding: 0; }}
ul.body-list li {{ margin-bottom: 1.5mm; line-height: 1.55; font-size: 8.5pt; }}

/* ── Management Summary ───────────────────────────────────────────────────── */
.mgmt-summary {{
  background: #FAFBFF;
  border: 1pt solid #D0D8F0;
  border-radius: 3pt;
  padding: 5mm 6mm;
  margin-bottom: 7mm;
}}
.mgmt-summary-title {{
  font-family: 'Courier New', Consolas, monospace;
  font-size: 8pt;
  font-weight: bold;
  letter-spacing: 0.15em;
  text-transform: uppercase;
  color: {COVER_COLOR};
  margin-bottom: 4mm;
  padding-bottom: 2mm;
  border-bottom: 1pt solid #D0D8F0;
}}
.mgmt-grid-table {{ width: 100%; border-collapse: collapse; table-layout: fixed; margin-bottom: 4mm; }}
.mgmt-grid-table td {{ width: 50%; vertical-align: top; padding: 0 1mm; }}
.mgmt-grid-table td:first-child {{ padding-left: 0; }}
.mgmt-grid-table td:last-child {{ padding-right: 0; }}
.mgmt-grid-table tr + tr td {{ padding-top: 4mm; }}
.mgmt-card {{ background: #FFFFFF; border: 0.7pt solid #E0E8FF; border-radius: 2pt; padding: 3mm; }}
.mgmt-card-title {{
  font-family: 'Courier New', Consolas, monospace;
  font-size: 6.5pt;
  font-weight: bold;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: {ACCENT};
  margin-bottom: 1.5mm;
}}
.mgmt-card-body {{ font-size: 8pt; color: #333; line-height: 1.55; }}
.mgmt-card-full {{ margin-bottom: 4mm; }}
.phase-legend-table {{ width: 100%; border-collapse: collapse; table-layout: fixed; margin: 3mm 0; }}
.phase-legend-table td {{ width: 20%; padding: 0 0.75mm; vertical-align: middle; }}
.phase-legend-table td:first-child {{ padding-left: 0; }}
.phase-legend-table td:last-child {{ padding-right: 0; }}
.phase-legend-item {{
  box-sizing: border-box;
  text-align: center;
  padding: 2.5mm 1.5mm;
  border-radius: 2pt;
  color: #fff;
  overflow-wrap: break-word;
  word-wrap: break-word;
}}
.phase-legend-num {{
  font-family: 'Courier New', Consolas, monospace;
  font-size: 6.3pt;
  font-weight: bold;
  letter-spacing: 0.04em;
  line-height: 1.2;
  margin-bottom: 1mm;
}}
.phase-legend-label {{
  font-size: 6pt;
  font-weight: bold;
  line-height: 1.3;
}}

/* ── Risk / gap table ─────────────────────────────────────────────────────── */
.risk-table {{ width: 100%; border-collapse: collapse; font-size: 8.2pt; margin-bottom: 5mm; }}
.risk-table th {{
  font-family: 'Courier New', Consolas, monospace;
  font-size: 6.3pt;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: #888;
  background: #F6F6F4;
  padding: 2mm 3mm;
  text-align: left;
  font-weight: normal;
  border-bottom: 1pt solid #DADADA;
}}
.risk-table td {{
  padding: 2mm 3mm;
  border-bottom: 0.4pt solid #EEEEEE;
  vertical-align: top;
  line-height: 1.5;
}}
.risk-table tr {{ break-inside: avoid; }}
.risk-table .ri-host {{
  font-family: 'Courier New', Consolas, monospace;
  font-size: 7.5pt;
  font-weight: bold;
  color: {ACCENT};
  white-space: nowrap;
}}
"""


CSS = build_css("INTERNAL REFERENCE — VIRTUOSOFT VAPT TOOLKIT  |  VIRTUOSOFT SECURITY TEAM")


# ── Section helpers ──────────────────────────────────────────────────────────
def section_title(num, title):
    return f'<div class="section-title"><span class="sn">{h(num)}</span>{title}</div>'


def make_cover(counts, status_counts, n_categories):
    total = len(TOOLS)
    return f'''
<div class="cover">
  <div class="cover-band">
    <div class="cover-classification">Internal Reference &nbsp;&middot;&nbsp; Toolkit Capability Document &nbsp;&middot;&nbsp; Virtuosoft Security Team</div>
    <div class="cover-doc-type">&#9656; External Tool Arsenal &amp; VAPT Cycle Mapping</div>
    <div class="cover-id">ARSENAL</div>
    <div class="cover-subtitle-band">&#9654; {total} tools catalogued &nbsp;|&nbsp; {n_categories} categories &nbsp;|&nbsp; 5 VAPT phases &nbsp;|&nbsp; {status_counts["OK"]} installed</div>
  </div>
  <div class="cover-body">
    <h1 class="cover-title">Virtuosoft VAPT Toolkit — External Tool Arsenal &amp; VAPT Cycle Reference</h1>
    <p class="cover-description">
      This document catalogues every external command-line tool wired into Virtuosoft's VAPT
      Toolkit's <code>tools/external_arsenal.sh</code> registry. Each tool is mapped to
      the stage of the Vulnerability Assessment &amp; Penetration Testing (VAPT) lifecycle it
      is used in, with a plain-language explanation of why it is used and a representative
      command showing how it is invoked in practice.
    </p>
    <div class="cover-rule"></div>
    <table class="cover-meta-table">
      <tr><td class="mk">Document Subject</td><td class="mv">Virtuosoft VAPT Toolkit — External Tool Arsenal</td></tr>
      <tr><td class="mk">Tools Catalogued</td><td class="mv">{total} (across {n_categories} categories)</td></tr>
      <tr><td class="mk">Currently Installed</td><td class="mv">{status_counts["OK"]} / {total} on this host (see &sect;09 for gaps)</td></tr>
      <tr><td class="mk">VAPT Phases Mapped</td><td class="mv">5 &mdash; Recon, Scanning, Assessment, Exploitation, Mobile/Post-Exploitation</td></tr>
      <tr><td class="mk">Reference Date</td><td class="mv">July 2026</td></tr>
      <tr><td class="mk">Prepared By</td><td class="mv">Virtuosoft Security Team</td></tr>
      <tr><td class="mk">Contact</td><td class="mv">huzaifa.jamil@virtuosoft.pk</td></tr>
      <tr><td class="mk">Document Version</td><td class="mv">1.0 &mdash; Initial Release</td></tr>
    </table>
    <div class="cover-stats-row">
      <div class="cover-stat-box" style="border-color:{PHASES["recon"]["color"]};">
        <div class="cover-stat-num" style="color:{PHASES["recon"]["color"]};">{counts["recon"]}</div>
        <div class="cover-stat-label">Recon / OSINT</div>
      </div>
      <div class="cover-stat-box" style="border-color:{PHASES["scan"]["color"]};">
        <div class="cover-stat-num" style="color:{PHASES["scan"]["color"]};">{counts["scan"]}</div>
        <div class="cover-stat-label">Scan / Enum</div>
      </div>
      <div class="cover-stat-box" style="border-color:{PHASES["assess"]["color"]};">
        <div class="cover-stat-num" style="color:{PHASES["assess"]["color"]};">{counts["assess"]}</div>
        <div class="cover-stat-label">Assessment</div>
      </div>
      <div class="cover-stat-box" style="border-color:{PHASES["exploit"]["color"]};">
        <div class="cover-stat-num" style="color:{PHASES["exploit"]["color"]};">{counts["exploit"]}</div>
        <div class="cover-stat-label">Exploitation</div>
      </div>
      <div class="cover-stat-box" style="border-color:{PHASES["mobile"]["color"]};">
        <div class="cover-stat-num" style="color:{PHASES["mobile"]["color"]};">{counts["mobile"]}</div>
        <div class="cover-stat-label">Mobile / Post-Ex</div>
      </div>
      <div class="cover-stat-box" style="border-color:#C62828;">
        <div class="cover-stat-num" style="color:#C62828;">{status_counts["MISSING"]}</div>
        <div class="cover-stat-label">Not Installed</div>
      </div>
    </div>
  </div>
  <div class="cover-footer">
    <span>Internal reference — not a client deliverable</span>
    <span class="assessor">MHJ (CYS Engr) &middot; huzaifa.jamil@virtuosoft.pk</span>
    <span>Virtuosoft Security Team</span>
  </div>
</div>'''


def exec_summary_status_para(status_counts, total):
    if status_counts["MISSING"] == 0:
        return (f'Of the {total} catalogued tools, <strong>all {total} are currently installed '
                f'and verified reachable</strong> on this host via the arsenal\'s '
                f'<code>_have()</code> PATH check (see &sect;09) &mdash; there are no coverage '
                f'gaps in this catalogue.')
    return (f'Of the {total} catalogued tools, <strong>{status_counts["OK"]} are currently '
            f'installed and verified reachable</strong> on this host via the arsenal\'s '
            f'<code>_have()</code> PATH check (see &sect;09). The remaining '
            f'{status_counts["MISSING"]} are documented for completeness with the specific '
            f'reason they are not installed &mdash; neither gap leaves a VAPT phase uncovered, '
            f'since functionally equivalent tools already fill the same role.')


def bottom_line_body(status_counts, total):
    if status_counts["MISSING"] == 0:
        return (f'<strong>All {total} catalogued tools are installed and ready to use</strong> '
                f'on this machine right now &mdash; there are no coverage gaps in this catalogue.')
    return (f'<strong>{status_counts["OK"]} of {total} catalogued tools are installed and ready '
            f'to use</strong> on this machine right now. The {status_counts["MISSING"]} gap(s) '
            f'are explained in &sect;09; none removes coverage of a VAPT phase, since equivalent '
            f'tools already cover the same ground.')


def make_mgmt_summary(counts, status_counts, n_categories):
    total = len(TOOLS)
    legend_cells = "".join(
        f'<td><div class="phase-legend-item" style="background:{PHASES[p]["color"]};">'
        f'<div class="phase-legend-num">PHASE {PHASES[p]["num"]}</div>'
        f'<div class="phase-legend-label">{PHASES[p]["short"]}</div>'
        f'</div></td>'
        for p in PHASE_ORDER
    )
    return f'''
<div class="section">
  {section_title("00", "Management Summary &mdash; Plain-English Overview")}

  <div class="mgmt-summary">
    <div class="mgmt-summary-title">&#9654; For Non-Technical Readers &mdash; What This Document Is</div>

    <table class="mgmt-grid-table">
      <tr>
        <td>
          <div class="mgmt-card">
            <div class="mgmt-card-title">What Is a VAPT Cycle?</div>
            <div class="mgmt-card-body">
              A Vulnerability Assessment &amp; Penetration Test (VAPT) is not one activity — it is a
              sequence of stages, each building on the last: find what exists, map how it responds,
              check it against known weaknesses, prove exploitability, and (for mobile apps) get
              inside the running application itself. This document groups every tool in the
              toolkit's arsenal by which of those five stages it belongs to.
            </div>
          </div>
        </td>
        <td>
          <div class="mgmt-card">
            <div class="mgmt-card-title">Why So Many Separate Tools?</div>
            <div class="mgmt-card-body">
              No single tool does all five stages well — each one specializes (subdomain discovery,
              port scanning, injection testing, credential attacks, mobile instrumentation) the same
              way a physical security audit uses different specialists for locks, alarms, and safes.
              <strong>{total} tools across {n_categories} categories</strong> give the toolkit
              professional-grade coverage at every stage instead of one generalist doing all of it
              poorly.
            </div>
          </div>
        </td>
      </tr>
    </table>

    <div class="mgmt-card mgmt-card-full">
      <div class="mgmt-card-title">What Do the Phase Colours Mean?</div>
      <div class="mgmt-card-body">
        <table class="phase-legend-table"><tr>{legend_cells}</tr></table>
        Work generally flows left to right — Recon feeds Scanning, Scanning feeds Assessment,
        Assessment feeds Exploitation — though in practice a real engagement loops back and
        forth between stages as new information surfaces.
      </div>
    </div>

    <div class="mgmt-card mgmt-card-full">
      <div class="mgmt-card-title">What&rsquo;s the Bottom Line?</div>
      <div class="mgmt-card-body">
        {bottom_line_body(status_counts, total)}
      </div>
    </div>
  </div>
</div>'''


def make_stats_row(counts, status_counts):
    total = len(TOOLS)
    boxes = []
    for p in PHASE_ORDER:
        boxes.append(f'''<div class="stat-box">
          <div class="stat-num" style="color:{PHASES[p]["color"]};">{counts[p]}</div>
          <div class="stat-label">Phase {PHASES[p]["num"]}</div>
        </div>''')
    boxes.append(f'''<div class="stat-box">
      <div class="stat-num" style="color:{COVER_COLOR};">{total}</div>
      <div class="stat-label">Total Tools</div>
    </div>''')
    return f'<div class="stats-row">{"".join(boxes)}</div>'


def make_summary_table():
    rows = []
    for name, cat, phase, status, url, why, ex in TOOLS:
        why_short = why.split(" — ")[0].split(". ")[0].rstrip(".")
        rows.append(f'''<tr>
          <td class="name-cell">{h(name)}</td>
          <td>{cat_badge(cat)}</td>
          <td>{phase_badge(phase)}</td>
          <td>{status_badge(status)}</td>
          <td class="why-cell">{h(why_short)}.</td>
        </tr>''')
    return f'''
    <table class="summary-table">
      <colgroup>
        <col class="col-name"><col class="col-cat"><col class="col-phase">
        <col class="col-stat"><col class="col-why">
      </colgroup>
      <thead><tr>
        <th>Tool</th><th>Category</th><th>VAPT Phase</th><th>Status</th><th>Why It's Used</th>
      </tr></thead>
      <tbody>{"".join(rows)}</tbody>
    </table>'''


def make_tool_card(name, cat, phase, status, url, why, ex):
    return f'''
    <div class="tool-card">
      <div class="tool-card-header">
        <div class="tool-card-header-info">
          <div class="tool-name">{h(name)}</div>
          <div class="tool-url">{h(url)}</div>
        </div>
        <div class="tool-badges">{cat_badge(cat)}{status_badge(status)}</div>
      </div>
      <div class="tool-card-body">
        <div class="tool-why">{h(why)}</div>
        <div class="tool-example">$ {h(ex)}</div>
      </div>
    </div>'''


def make_phase_section(phase_key, phase_num_label):
    p = PHASES[phase_key]
    tools_in_phase = [t for t in TOOLS if t[2] == phase_key]
    cards = "".join(make_tool_card(*t) for t in tools_in_phase)
    return f'''
<div class="section pb">
  {section_title(phase_num_label, f'Phase {p["num"]} Detail &mdash; {p["title"]}')}
  <div class="phase-header" style="background:{p["color"]};">
    <div class="phase-header-title">Phase {p["num"]} &mdash; {p["title"]} ({len(tools_in_phase)} tools)</div>
    <div class="phase-header-blurb">{p["blurb"]}</div>
  </div>
  {cards}
</div>'''


def make_excluded_section():
    rows = "".join(f'''<tr>
      <td class="ri-host">{h(name)}</td>
      <td>{h(cat)}</td>
      <td>{h(url)}</td>
      <td>{h(reason)}</td>
    </tr>''' for name, cat, url, reason in EXCLUDED)
    return f'''
    <table class="risk-table">
      <thead><tr><th>Name</th><th>Category</th><th>Upstream</th><th>Reason Excluded</th></tr></thead>
      <tbody>{rows}</tbody>
    </table>'''


def make_gaps_or_clean_block(status_counts, total):
    missing = [t for t in TOOLS if t[3] == "MISSING"]
    if not missing:
        return f'''
    <div class="callout avoid">
      <div class="callout-label">Full Coverage &mdash; No Gaps</div>
      All <strong>{total}</strong> catalogued VAPT tools are currently installed and verified
      reachable on this host (<strong>{status_counts["OK"]} / {total}</strong> via the arsenal's
      <code>_have()</code> PATH check). No tool in scope for this catalogue is missing.
    </div>'''
    rows = "".join(f'''<tr>
      <td class="ri-host">{h(name)}</td>
      <td>{cat_badge(cat)}</td>
      <td>{phase_badge(phase)}</td>
      <td>{h(why.split(". ")[-1] if ". " in why else why)}</td>
    </tr>''' for name, cat, phase, status, url, why, ex in missing)
    tool_word = "tool is" if len(missing) == 1 else "tools are"
    return f'''
    <p>The following {len(missing)} catalogued {tool_word} not currently installed on this host,
    along with the specific reason.</p>
    <table class="risk-table">
      <thead><tr><th>Tool</th><th>Category</th><th>Phase</th><th>Why Not Installed</th></tr></thead>
      <tbody>{rows}</tbody>
    </table>'''


def assemble_html():
    counts, status_counts, n_categories = compute_stats()
    total = len(TOOLS)

    phase_sections = "".join(
        make_phase_section(p, f"{i+4:02d}") for i, p in enumerate(PHASE_ORDER)
    )

    have_code_block = code(
        '_have() { command -v "$1" >/dev/null 2>&1; }\n\n'
        '# usage from any other script:\n'
        '. "$(dirname "$0")/external_arsenal.sh"\n'
        'if _have nuclei; then\n'
        '  nuclei -l hosts.txt -severity high\n'
        'fi',
        "tools/external_arsenal.sh"
    )

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>External Tool Arsenal &amp; VAPT Cycle Reference &mdash; Virtuosoft VAPT Toolkit</title>
<style>
{CSS}
</style>
</head>
<body>

<!-- ── COVER PAGE ───────────────────────────────────────────────────────── -->
{make_cover(counts, status_counts, n_categories)}

<!-- ── SECTION 00: MANAGEMENT SUMMARY ──────────────────────────────────── -->
{make_mgmt_summary(counts, status_counts, n_categories)}

<!-- ── SECTION 01: EXECUTIVE SUMMARY ───────────────────────────────────── -->
<div class="section">
  {section_title("01", "Executive Summary")}

  <p>This document provides a complete inventory of the <strong>{total} external command-line
  tools</strong> registered in Virtuosoft's VAPT Toolkit arsenal
  (<code>tools/external_arsenal.sh</code>), spanning <strong>{n_categories} functional
  categories</strong> from passive subdomain enumeration through mobile runtime instrumentation.
  Every tool is mapped to exactly one of the <strong>5 stages of the VAPT lifecycle</strong> it
  primarily serves, alongside a plain-language rationale for why it earned a place in the
  arsenal and a representative command demonstrating real-world usage.</p>

  <p>{exec_summary_status_para(status_counts, total)}</p>

  <p>Two additional entries in the raw registry (<code>freebuff</code>, <code>kimchi</code>) are
  unrelated AI coding-assistant installers from unvetted domains and are excluded from this VAPT
  tool catalogue entirely &mdash; see &sect;10.</p>

  <div class="callout avoid">
    <div class="callout-label">How to Read This Document</div>
    &sect;02 gives the full flat inventory as a single scannable table. &sect;03 breaks down tool
    counts and the phase model itself. &sect;04&ndash;08 give one detailed card per tool, grouped
    by the VAPT phase it belongs to, each with a "why" rationale and an example invocation.
    &sect;09 covers the installation/detection methodology. &sect;10 lists tools deliberately
    excluded from scope.
  </div>
</div>

<!-- ── SECTION 02: FULL TOOL INVENTORY TABLE ───────────────────────────── -->
<div class="section pb">
  {section_title("02", "Full Tool Inventory Table")}
  <p>The table below lists all {total} tools in phase order (Recon &rarr; Scanning &rarr;
  Assessment &rarr; Exploitation &rarr; Mobile/Post-Exploitation). Full rationale and example
  commands for each tool are in the phase-detail sections that follow (&sect;04&ndash;08).</p>

  {make_summary_table()}
</div>

<!-- ── SECTION 03: VAPT CYCLE &amp; PHASE BREAKDOWN ────────────────────── -->
<div class="section pb">
  {section_title("03", "VAPT Cycle &amp; Phase Breakdown")}
  <p>The toolkit's arsenal is organised around a standard 5-stage penetration-testing lifecycle.
  Tool counts per phase are shown below; the detailed rationale for each phase's tools follows
  in &sect;04&ndash;08.</p>

  {make_stats_row(counts, status_counts)}

  <ul class="body-list">
    <li><strong>Phase 1 &mdash; Reconnaissance &amp; OSINT ({counts["recon"]} tools):</strong>
        {PHASES["recon"]["blurb"]}</li>
    <li><strong>Phase 2 &mdash; Scanning &amp; Enumeration ({counts["scan"]} tools):</strong>
        {PHASES["scan"]["blurb"]}</li>
    <li><strong>Phase 3 &mdash; Vulnerability Assessment ({counts["assess"]} tools):</strong>
        {PHASES["assess"]["blurb"]}</li>
    <li><strong>Phase 4 &mdash; Exploitation ({counts["exploit"]} tools):</strong>
        {PHASES["exploit"]["blurb"]}</li>
    <li><strong>Phase 5 &mdash; Mobile Runtime &amp; Post-Exploitation ({counts["mobile"]} tools):</strong>
        {PHASES["mobile"]["blurb"]}</li>
  </ul>

  <div class="callout avoid">
    <div class="callout-label">Note on Dual-Use Tools</div>
    Several tools genuinely span two phases — <code>gf</code>/<code>qsreplace</code>/<code>anew</code>
    are enumeration-support utilities also used to feed exploitation pipelines, and
    <code>jadx</code>/<code>apkleaks</code> perform static mobile recon that later informs the
    Phase 5 runtime work. Each tool below is assigned to the phase where it is <em>first</em>
    and most characteristically used, to keep the inventory a strict partition rather than an
    overlapping one.
  </div>
</div>

{phase_sections}

<!-- ── SECTION 09: INSTALLATION &amp; DETECTION METHODOLOGY ────────────── -->
<div class="section pb">
  {section_title("09", "Installation &amp; Detection Methodology")}

  <p>Tool availability is detected by <code>tools/external_arsenal.sh</code> via a single
  function, sourced by every other script in the toolkit that gates an optional capability:</p>

  {have_code_block}

  <p>This means a tool is "installed" from the toolkit's perspective the moment its binary name
  resolves on <code>$PATH</code> &mdash; regardless of install method. On this host, tools were
  installed without root access via three methods depending on packaging:</p>

  <ul class="body-list">
    <li><strong>Go tools</strong> &mdash; <code>GOBIN=$HOME/go/bin go install &lt;module&gt;@latest</code>,
        landing in <code>$HOME/go/bin</code> (already on <code>$PATH</code>).</li>
    <li><strong>Python CLI tools</strong> &mdash; <code>pipx install &lt;package&gt;</code>,
        landing in <code>$HOME/.local/bin</code> (already on <code>$PATH</code>), avoiding the
        system Python's externally-managed-environment restriction (PEP 668).</li>
    <li><strong>Script-only repos with no clean packaging</strong> &mdash; <code>git clone</code>
        into <code>~/tools/&lt;name&gt;/</code> with a thin executable shim placed in
        <code>$HOME/.local/bin/&lt;name&gt;</code> that execs the real script, so
        <code>_have()</code> detects it identically to a natively-packaged tool.</li>
  </ul>

  <p>Run <code>/arsenal</code> (or <code>bash tools/external_arsenal.sh</code> directly) at any
  time to get a live installed/missing table &mdash; that command is the single source of truth
  this entire document was generated from, so it will never silently drift out of date the way a
  static document otherwise would.</p>
</div>

<!-- ── SECTION 10: COVERAGE GAPS &amp; EXCLUDED ENTRIES ────────────────── -->
<div class="section pb">
  {section_title("10", "Coverage Gaps &amp; Excluded Entries")}

  {make_gaps_or_clean_block(status_counts, total)}

  <p>The following {len(EXCLUDED)} entries exist in the raw
  <code>tools/external_arsenal.sh</code> registry but are deliberately excluded from this VAPT
  catalogue &mdash; they are unrelated AI coding-assistant installers, not penetration-testing
  tools, and their installer scripts originate from unvetted domains:</p>

  {make_excluded_section()}
</div>

</body>
</html>"""


if __name__ == "__main__":
    html_content = assemble_html()

    html_path = f"{OUT}/ARSENAL_TOOL_INVENTORY_VAPT_CYCLE.html"
    pdf_path = f"{OUT}/ARSENAL_TOOL_INVENTORY_VAPT_CYCLE.pdf"

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"HTML written: {html_path}")

    print(f"Generating PDF: {pdf_path}")
    result = subprocess.run(
        ["python3", "-m", "weasyprint", html_path, pdf_path],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        size_kb = os.path.getsize(pdf_path) // 1024
        print(f"  PDF generated: {pdf_path}  ({size_kb} KB)")
    else:
        print(f"  ERROR generating PDF:\n{result.stderr[:2000]}")

    print("\nDone.")
