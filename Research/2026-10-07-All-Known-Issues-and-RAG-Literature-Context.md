# What PentestAgent/VulnBot Actually Are, and the Full Issue History Behind This Session's "Honest Limits" Note

**Follow-up to:** `2026-10-07-Embedding-Based-Skill-Retrieval-Upgrade.md`, which cited
PentestAgent/VulnBot and flagged two "honest limits" (recon-input gaps, structured-output
reliability) without detail. This doc explains the two papers properly, then goes back
through Mugheeraat's **own real reports** (freshly pulled from GitHub, commit `f93747c`,
mirrored in `Mugheeraat-Source-Reports/` alongside this file) to catalog every real issue
found across its actual test history — not just the two flagged in passing.

---

## 1. PentestAgent and VulnBot, properly explained

### PentestAgent (ASIACCS 2025, peer-reviewed)

A **4-agent pipeline**: Reconnaissance agent → Search agent → Planning agent → Execution
agent. Its distinguishing feature is **RAG over CVE databases** specifically — it retrieves
real CVE records for discovered services and auto-configures public exploits against them,
rather than relying on the LLM's own memorized knowledge of a vulnerability. Reported
**74.2% overall success across a 67-target benchmark**. The key design lesson: narrow,
structured retrieval (a CVE lookup keyed on a discovered service/version) outperforms
general-purpose RAG, because the retrieval target is unambiguous.

### VulnBot (2025)

A **5-module architecture**: Planner, Memory Retriever, Generator, Executor, Summarizer —
operating across three phases (Reconnaissance → Scanning → Exploitation), with real tools
(Nmap/Dirb for recon, Nikto/WPScan for scanning, Metasploit/Hydra for exploitation). Its
distinguishing feature is the **Penetration Task Graph (PTG)** — an explicit dependency
graph between tasks, rather than a flat queue — plus a "Check and Reflection Mechanism"
that iteratively refines failed tasks. Tested with **Llama-3.3-70B, Llama-3.1-405B,
DeepSeek-v3, and GPT-4o** — all substantially larger than Mugheeraat's 7-8B council.

**Results, and why they matter for calibrating expectations here:** on AUTOPENBENCH,
VulnBot-Llama3.1-405B hit **30.3% overall task completion vs. 9.09% for the same bare model
with no scaffolding** — the multi-agent/RAG architecture roughly **tripled** the success
rate of the identical underlying model. That's the real, measured value of the scaffolding
pattern Mugheeraat already follows — but even with that uplift, on a **405-billion-parameter**
model, completion was still under a third. **Mugheeraat's actual architecture is not behind
this literature** (it already has the Planner/Executor split, and `01:FR-COUNCIL-07b`'s skill
injection is the same RAG pattern) — but it's running at roughly 1/50th the parameter count
of VulnBot's best-performing model, on a CPU-only host. The literature itself says even the
scaffolding pattern doesn't get you past single-digit-to-low-double-digit success rates
without a much bigger model behind it. Zero confirmed findings against a hardened target like
Juice Shop is a harsh outcome, but it is not an outlier relative to what comparable published
systems achieve at Mugheeraat's actual parameter scale.

---

## 2. The full issue catalog — pulled fresh from Mugheeraat's own reports, not reconstructed from memory

Read directly (2026-10-07, commit `f93747c`): `PIPELINE-FLOW-AUDIT-REPORT-2026-09-23.md`
(790 lines, a genuine line-by-line code audit — the single richest source),
`JuiceShop-VAPT-Testing-Guide-2026-09-19.md` (the ground-truth benchmark writeup),
`LLM-Council-Benchmarks.md` (every real timed invocation this project has ever logged). All
three are mirrored in `Mugheeraat-Source-Reports/` next to this file.

### 2.1 Recon-input gaps — the deepest, still-unresolved problem

- **Root finding (Testing Guide §5):** Juice Shop is an Angular SPA. Its real REST API
  (`/rest/...`, `/api/...`) exists only behind dynamic JS `fetch` calls — static crawling
  (`katana`) found exactly **5 URLs total**: the root page and 4 static asset files. Zero
  real endpoints. With nothing real to work from, the Strategist proposed plausible-sounding
  fictional paths (`/upload`, `/change-password`); the Angular SPA's catchall route returns
  HTTP 200 for literally any path, which the access-control detection rule correctly flagged
  as a *candidate* and the Adjudicator correctly *dismissed* as not real evidence.
- **This is explicitly recorded as the actual, final verdict, not a guess:** *"The Council's
  reasoning was sound at every gate... It did not reproduce any of the 11 ground-truth
  findings — not because of a capability gap in the reasoning, but because it was never given
  the real endpoint data... This is a recon-input problem, not a council-reasoning problem."*
- **Staged, not yet resolved** as Round 26 — three options on the table (headless-browser
  crawling via Playwright/Puppeteer, manual endpoint seeding for this specific benchmark, or
  accepting the limitation), no decision made as of the last pull.
- **A second, compounding recon bug, independently found and fixed (§3.1):** `katana_args`
  used a non-existent flag (`-json` instead of `-jsonl`) and three Wave-3 crawlers
  (`katana`/`nuclei`/`gospider`) crawled the bare target string instead of the live
  scheme+port URL discovered by Wave 2 — meaning even where real endpoints existed, the
  crawl would have hit the wrong port. Fixed and verified.

### 2.2 Structured-output reliability — found at every council role, fixed at some, not others

- **Secondary Scripter** (2026-09-13): `StructuredOutputError` uncaught between
  `phase_lifecycle.py` and `cli/run.py` — an exhausted retry budget (a real, occasional model
  miss) crashed the *entire engagement*, not just the one task. Fixed: task marked
  `GATE2_BLOCKED`, engagement continues.
- **Strategist, Strategy Auditor, Reporter** (2026-09-28, per the requirements-repo sync two
  weeks ago): same bug class, found by a direct code audit of the remaining call sites after
  the Strategist crashed live mid-Engagement-31 following a genuine ~4h50m inference call.
  All three fixed the same way.
- **Criterion Adjudicator** — flagged by the Pipeline-Flow-Audit (2026-09-23) as the single
  **highest-severity open finding** at the time: the exact same unguarded call site, at the
  one stage that matters most (nothing can be confirmed if Gate 3 crashes). **Per the
  addendum appended 2026-09-24 ("Round 27"), this was fixed**: a new `ADJUDICATION_FAILED`
  terminal status was added via the existing schema-migration mechanism, and the call site
  now catches `StructuredOutputError` correctly (confirmed by direct diff review, not just
  trusting the commit message — the review caught that the original fix proposal would have
  raised a *second*, different crash via an invalid CHECK-constraint value, and verified the
  actual implementation avoided that trap).
- **Net state as of the last available report:** every council role's structured-output path
  is now guarded. This was reached via the same recurring pattern each time: found live by a
  real crash, root-caused by direct code reading, fixed, and — critically — **never
  generalized to the sibling call sites until each one crashed independently**. The
  Pipeline-Flow-Audit's own "Architectural Disconnects" section names this explicitly: *"The
  Scripter/Adjudicator retry-and-crash contract is inconsistent within the same codebase...
  only one of the two call sites was ever updated... a maintenance/consistency gap."*

### 2.3 Candidate-detection vocabulary gap — the other major open problem, larger than this session previously characterized it

The Strategist is instructed to choose from a **19-token vulnerability-class vocabulary**
(`SQLI, NOSQLI, IDOR, BROKEN_AUTH, BFLA, MASS_ASSIGNMENT, SSRF, SSTI, LFI,
INSECURE_DESERIALIZATION, RACE_CONDITION, JWT, SUBDOMAIN_TAKEOVER, XSS, SECURITY_MISCONFIG,
CSRF, RCE, PROMPT_INJECTION, OTHER`). The Pipeline-Flow-Audit's own line-by-line trace of
`candidate_detection.py` against this vocabulary found, at the time of the audit, **12 of 19
classes had zero detection path at all.** A self-correction within the same audit narrowed
this: ~4 of those 12 turn out to be deliberately deprioritized noise by the Primary
Scripter's own prompt (bare CORS wildcards, missing-header-only findings) rather than a real
gap — but that still left a confirmed, real gap of **9 classes genuinely undetectable by any
rule** (`SSRF, SSTI, LFI, INSECURE_DESERIALIZATION, RACE_CONDITION, JWT, SUBDOMAIN_TAKEOVER,
RCE, PROMPT_INJECTION`), plus — measured against this project's own 11-item ground truth —
**5 of the 11 real Juice Shop findings had no structural detection path**, including 2 of the
more severe ones (forced-browsing directory listings exposing a KeePass DB and a private
signing key).

**Round 27 (2026-09-24) closed part of this** — added NoSQL-error patterns, a bulk-PII rule,
a directory-listing rule, and a properly-scoped CORS rule (credential-exfil shape only,
deliberately not bare wildcards) — reviewed diff-by-diff and confirmed correctly implemented,
including one place where the implementation was *more* careful than the audit's own
recommendation (the CORS scoping). **What remains genuinely open, per the audit's own
"Executive Defect Map":** `SSRF`, `SSTI`, `LFI`, `INSECURE_DESERIALIZATION`,
`RACE_CONDITION`, `JWT`, `SUBDOMAIN_TAKEOVER`, `RCE`, `PROMPT_INJECTION` — 9 of 19 vocabulary
tokens — still have no detection path at all, and this session's own ground-truth exercise
happened not to produce an example of any of them, so their real-world impact is confirmed
structurally but unverified in practice.

**A related, still-open finding:** `candidate_detection.py`'s Tier-1 SQL filter only reads
output from `nuclei`/`sqlmap`/`nmap` (plus, after Round 27, `nikto`/`testssl`/`wafw00f`) —
**`masscan`, `ffuf`, `feroxbuster`, `gobuster` output is never read by this module at all**,
by deliberate scope decision, not a bug — but this means tools likely to surface
`SECURITY_MISCONFIG`-class evidence are excluded before any pattern-matching even runs.

### 2.4 Loop/breaker blindness — a subtler class of bug, two confirmed instances

- **Headline finding (Pipeline-Flow-Audit §5.1):** the round-progression breaker that decides
  whether to keep looping on a target counts **Phase 4.1 approval** (`GATE1_APPROVED`), not
  real Phase-4.2 execution. A *second*, independent Tier-0 re-check happens at actual dispatch
  time (`task_runner.py::run_gated_task`) — and a task can pass the first check and still be
  rejected at the second. When that happens systematically (exactly what the `host:port`
  scope bug caused in Engagement 28 — 5 of 6 round-1 tasks), the round-level breaker **never
  fires**, because it never sees the second rejection — the engagement would burn its entire
  15-round/12-hour budget on a target executing zero real commands, with nothing surfacing to
  the operator short of reading a specific informational report artifact mid-run. **Fixed in
  Round 27**, confirmed by direct code review: the breaker now also checks whether tasks
  "survived" the Phase-4.2 re-check, not just whether Phase 4.1 approved them.
- **A related, narrower live-visibility gap, found during the same audit's self-correction:**
  `GATE2_BLOCKED` bursts *are* visible live on the dashboard (amber warning color) — but
  `GATE1_REJECTED` has **zero live visibility anywhere** in the operator-facing surface
  (confirmed by grep across the dashboard/monitor/cli code, zero hits). Engagement 28's actual
  failure mode (5 of 6 tasks `GATE1_REJECTED`, not `GATE2_BLOCKED`) was precisely the
  category with no live warning — not addressed by Round 27's fix, which closed the
  breaker-blindness consequence but not the dashboard-visibility gap itself.
- **A related design note, not a bug:** the "zero-yield" signal that drives every circuit
  breaker measures *recon novelty* (new discovered entities), not *vulnerability
  confirmation* — a target could reset its zero-yield counter every task via constant recon
  novelty while `verified_vulnerabilities` stays permanently empty, and no breaker would ever
  fire. Defensible (these breakers protect against wasted compute, not zero findings), but it
  means this whole module provides no actual safety net against the zero-findings problem —
  a different mechanism (Round 26's recon-input fix, or the candidate-detection vocabulary
  expansion) is what would actually move that number.

### 2.5 Lower-severity, still-open hygiene items (Pipeline-Flow-Audit's own priority-6 batch)

- `_read_raw_artifact_text` silently swallows `OSError`, returning `""` with no log line —
  a pruned/unreadable artifact file looks identical to "no signal found."
- `detect_candidates`'s dispatch silently `continue`s on any Tier-2 command whose `argv[0]`
  isn't literally `curl`/`python3`/`python` (e.g. a Scripter-generated `wget` or a
  shell-wrapped one-liner) — no record anywhere that output existed and nothing looked at it.
- `executor.py`'s stdout/stderr buffer has no size cap — real risk is unbounded memory growth
  from a single legitimately-verbose tool (`nmap -p-`, a large `ffuf` wordlist), not
  truncation (the truncation hypothesis this audit was originally sent to check was directly
  refuted — the full raw output is always written, uncapped).
- The CORS/header-dependent detection rules only see headers if the Scripter's own `curl`
  command happened to include `-i`/`-D`/`-v` — a plain `curl` without those flags produces no
  headers to match against at all. (Status codes have a deterministic workaround already —
  `_curl_argv_with_status_marker` force-appends a status marker regardless of what the model
  remembered to ask for — headers have no equivalent yet.)

### 2.6 Infrastructure/performance findings, for calibration (from `LLM-Council-Benchmarks.md`)

- **CPU-only generation ceiling: ~1.1–1.8 tok/s**, consistent across 5 different 7-8B models —
  confirmed memory-bandwidth-bound, not thread-count-bound (`-t 18` vs `-t 8` barely moved
  generation speed).
- **GPU offload is slower than CPU-only on this host's iGPU** (1.91 vs 2.50 tok/s) — the iGPU
  shares system RAM bandwidth with no dedicated VRAM advantage, so there's no free performance
  win available from the hardware already present.
- **Council-wide real invocation success rate: 91.4% (53/58 logged attempts)** — most of the
  historical failures were a since-fixed broken-tokenizer GGUF file, not a fundamental model
  limitation; explicitly flagged by the report itself as "still small N... directional signal,
  not a statistically confident rate."
- **The existing skill-corpus RAG mechanism's real, measured trigger rate: 8.6% (6 of 70 real
  tasks across 2 engagements), and only 1 of those 6 matches actually reached a live Scripter
  prompt** (the other 5 were Gate-1-rejected before dispatch). This is a genuinely useful,
  concrete baseline for the embedding-based-retrieval upgrade proposed in the companion doc —
  any semantic-matching improvement should be measured against this real 8.6% figure, not an
  assumed one.

---

## 3. What this changes about the prior "honest limits" framing

The embedding-retrieval doc's two-line caveat undersold both problems:

- **Recon-input gaps** aren't a minor caveat — per Mugheeraat's own final verdict, it's *the*
  reason the entire ground-truth benchmark produced zero confirmed findings despite every
  other part of the pipeline working correctly, and it remains an open, undecided item
  (Round 26) as of the last pull.
- **Structured-output reliability** wasn't one bug — it was the same unguarded-exception
  pattern independently discovered and fixed **five separate times** (Scripter, Strategist,
  Auditor, Reporter, Adjudicator), each time only after a real live crash, because the fix was
  never generalized across call sites the first time it was found. As of the last pull, all
  five are now fixed — but the pattern of "fix one instance, miss the siblings" is itself a
  recurring process issue worth naming, not just the bug instances individually.

Separately, the candidate-detection vocabulary gap (9 of 19 classes with zero detection path)
is at least as consequential as either of the two originally flagged — and is the most
directly actionable of the three, since (per Round 27's own precedent) it's closed
incrementally, one rule at a time, with immediate test coverage, rather than needing an
architecture decision like Round 26 does.

## 4. Updated priority ordering (supersedes the two-item caveat in the prior doc)

1. **Round 26's recon-input decision** — still undecided, highest-leverage, blocks everything
   downstream of it from ever being exercised against a real finding.
2. **The remaining 9-of-19 candidate-detection vocabulary gap** — incrementally closeable,
   already has a working precedent (Round 27) to follow.
3. **`GATE1_REJECTED`'s missing live-dashboard visibility** — small, well-scoped, would have
   caught Engagement 28's actual failure mode in real time instead of requiring a full
   post-hoc audit to find.
4. Structured-output guards — **already closed** as of the last pull; worth only a
   process note (generalize a fix across all call sites with a shared contract the first
   time, not five times) rather than further engineering here.
