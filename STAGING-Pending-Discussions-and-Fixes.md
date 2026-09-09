> ⚠️ **DO NOT INGEST THIS FILE.** This is a staging/discussion log for the operator's own
> review. It is **not** a requirement specification, is **not** binding, and MUST NEVER be
> read, parsed, or treated as a source of truth by build agents, code-generation agents, or
> any automated development process. Nothing in this file is active until the operator
> explicitly approves an item below and it gets merged into the numbered requirement docs
> (`01`–`24`) by a separate, deliberate edit.
>
> This file exists so in-progress discussion of bugs/future features has somewhere to live
> without touching the binding corpus before the operator has signed off.

---

# Pending Discussions & Fixes — Awaiting Operator Approval

**Ordering convention:** newest items on top. New pending items get added directly below
this line, ahead of everything already resolved. Once an item is approved and merged, it
moves down into the dated archive further below rather than being deleted — this file's
purpose is to show how a fix evolved, not just its final state.

---

## Currently Pending Approval

## Round 5 — Expand `FR-BASELINE` With the Full Personal Tool Arsenal

**Status: 🔶 PENDING APPROVAL — nothing applied to any binding doc.** Pulled the actual
72-tool list from `~/claude-bug-bounty/reports/Personal-Tool Arsenal-Portfolio/` (parsed
the generated HTML directly — its data source module wasn't present on this machine) and
applied the same "check before accepting" judgment as the last efficiency re-check,
rather than mechanically registering all 72.

### Scope decision: recon/scanning only, not assessment/exploitation/mobile

The portfolio's own 5-phase split is: **Phase 1 Recon (26 tools)**, **Phase 2
Scanning/Enumeration (25 tools)**, Phase 3 Assessment (8), Phase 4 Exploitation (11),
Phase 5 Mobile Runtime (2). You asked for "every possible **recon** tool" — I've taken
that literally and scoped this round to Phase 1+2 (51 tools) for the zero-AI baseline
pipeline. Phase 3/4/5 tools (`sqlmap`, `dalfox`, `hashcat`, `kerbrute`, `mobsf`, etc.) MUST
NOT run in a zero-AI deterministic pre-step — that would bypass Gate 1/Gate 2/Adjudicator
review for genuinely exploit-class actions, a real safety regression against this
project's whole Dual-Mode architecture. Listed separately below as Tier 1 *candidates*
for the normal AI-gated Phase 4.2 loop instead — not acted on this round.

### `naabu` + `nmap`, both, as you asked

`FR-BASELINE-01` gains a second port-scan sub-step: `naabu` sweeps fast across the full
port range first, then `nmap -sV` runs *only* against the ports `naabu` actually found —
getting naabu's speed for the broad sweep and nmap's real version detection where it
matters, instead of nmap's `-sV` eating the whole scan budget on 65535 ports. `nmap`
was never removed — it stays fully available Tier 1 for the AI-driven loop too.

### Efficiency trims (same judgment call as `port_scanner.py` last round)

Checked for actual overlap rather than listing all 51 flatly:

- **`massdns`/`puredns`/`shuffledns`** — three tools doing the same job (DNS
  brute-force resolution); `puredns` is the polished wrapper around `massdns` with
  wildcard filtering already built in. **Recommend `puredns` only**, not all three.
- **`sublert`** — its actual job is *continuous* CT-log monitoring over time, not a
  one-time baseline scan. **Routed to `01:FR-MONITOR` instead** (`FR-MONITOR-01`'s
  existing scheduled-diff mechanism is the correct home for this, not a new one-shot
  step).
- **`knockpy`** — overlaps with subdomain enum (`subfinder`/`amass`) + the takeover
  checks (`dnsreaper`/`subjack`) already covered below. Not added separately.
- **`maigret`, `pywhat`** — on-demand OSINT/data-identification utilities (look up a
  specific username; classify an arbitrary string), not "scan this domain" tools. Better
  as AI-selectable Tier 2 binaries the Scripter reaches for on a specific task, not a
  forced baseline step run against every target regardless of relevance.
- **`waymore`, `hakrawler`, `gospider`, `cariddi`** — `katana` (already proposed below)
  is a modern all-in-one crawler covering most of what these older/narrower crawlers do.
  **Recommend `katana` + `gau` + `waybackurls` as the core crawl set**, with the other
  four flagged rather than force-included — say so if you specifically want one of them
  too (e.g. `cariddi` also does secret/endpoint pattern-matching inline, which the others
  don't).

### Proposed `FR-BASELINE` pipeline stages (revised)

**Always runs (`NETWORK` targets):**
1. Subdomain enumeration — `subfinder`, `amass`, `assetfinder` (three genuinely
   complementary passive sources, per the portfolio's own stated rationale)
2. DNS brute-force resolution — `puredns` (not all three DNS tools, see trim above)
3. Live-host probing — `httpx`, `dnsx`
4. Port scan — `naabu` (fast sweep) → `nmap -sV` (targeted, only naabu's discovered ports)
5. Tech fingerprinting — `whatweb` + `httpx -tech-detect` (already-planned + portfolio's probe tool)
6. Crawling/URL discovery — `katana`, `gau`, `waybackurls`
7. Content/directory fuzzing — `ffuf`, `feroxbuster`, `gobuster` (already registered)
8. Parameter discovery — `arjun`, `x8`
9. Subdomain takeover check — `dnsreaper`, `subjack`
10. Baseline vulnerability scan — `nuclei` (already registered)
11. *(glue utilities, not standalone steps)* — `gf`/`qsreplace`/`anew` pipe between
    stages 6→8 the way the portfolio itself describes them being used

**Conditional (only when relevant, skipped otherwise — not wasted runtime on every target):**
- Cloud asset discovery (`s3scanner`, `cloud_enum`, `cloudfail`, `scoutsuite`) — only if
  a cloud-provider indicator (S3 bucket name pattern, cloud ASN) surfaces during recon.
- Secrets scanning (`trufflehog`, `noseyparker`, `gitleaks`, `shhgit`, `git-hound`) —
  only for `CODE_REPO` targets or when a git repository is discovered/in scope.
- Mobile static recon (`apkleaks`, `jadx`) — only for `MOBILE_BINARY` targets.
- GraphQL recon (`graphw00f`, `clairvoyance`) — only if a GraphQL endpoint surfaces
  during crawling.

**This is a large new-dependency count** — roughly 25 new external binaries beyond
`naabu` (already approved). Real provisioning implications (`FR-PRE-04`'s tool-presence
check would need to cover all of them). Flagging the scale explicitly before drafting
the actual `01`/`03`/`09`/`13` text — **confirm this stage breakdown and the four trims
above, and I'll draft the full requirement text next** (this message is the design/scope
proposal; the formal `CLAUDE.md` §5.2 requirement blocks are the next step once you've
confirmed the shape, since re-drafting after a trim-disagreement would waste both our
time).

### Separately flagged: Phase 3/4/5 tools as Tier 1 *candidates* (AI-gated loop, not baseline)

Not part of this round's ask, but surfaced since you mentioned "every possible tool":
`semgrep` (SAST, `CODE_REPO`), `log4j-scan`, `graphql-cop`, `jwt_tool`, `byp4xx`/
`whatwaf`/`unwaf` (WAF-bypass), `dalfox`/`xsstrike` (XSS), `ghauri` (blind-SQLi, sqlmap
alternative), `fuxploider` (upload testing). **Not flagging** `hashcat`/`cewler`/`cupp`/
`trevorspray`/`kerbrute`/`interactsh-client` — these look like they already overlap
`19:FR-CRED`'s wordlist/spray pipeline and `interactsh-client`'s existing wrap in
`oob_listener.py` (per `ASSET-CLASSIFICATION.md`) — would need checking for actual gaps
before proposing, not assumed. Say if you want this list turned into its own round.

---

## Archive — Resolved / Merged Items (newest first)

### Round 4 — Baseline Recon Pipeline, Efficiency Re-Check, Deferred-Gap Integration Points

**Status: ✅ MERGED in full** (`01`, `03`, `05`, `09`, `13`, `16`, `18`; decision #75 in `10`).

- **R4.1/R4.2 (efficiency re-check)**: `port_scanner.py`'s "redundant with `nmap`"
  verdict overturned after reading the actual script — `naabu` (fast broad-port
  discovery) and `nmap -sV` (deep version detection) solve different problems, not the
  same job at different verbosity. `lead_board.py`/`memory_gc.py`/`validate.py`'s
  redundancy verdicts confirmed correct on inspection.
- **R4.3**: `16:TR-SCRIPT-06` rewritten concretely as new `01:FR-BASELINE-01..04` — a
  deterministic, zero-AI pipeline (`naabu` → `whatweb` → `ffuf`/`feroxbuster` → `nuclei`)
  that runs automatically once per target right after Phase 3, feeding its structured
  output verbatim into the Lead Strategist's first Phase 4.1 invocation. `naabu` added
  to `FR-TOOL-01`'s Tier 1 roster (the open naabu-vs-tuned-nmap decision resolved in
  naabu's favor, per the recommendation).
- **R4.4**: `FR-TOOL-17` (authenticated session reuse) + `03:DR-SCHEMA-22
  auth_sessions` + `05:SEC-DATA-04` (inherits `FR-TOOL-15`'s no-raw-secret-in-logs
  pattern).
- **R4.5**: `FR-TOOL-18` (fingerprint-triggered EOL/CVE lookup) + `03:DR-SCHEMA-23
  tech_fingerprint_intel` — fed for free by `FR-BASELINE-01`'s `whatweb` step.
- **R4.6**: `FR-TOOL-19` — `multipart_mutator.py`'s technique registered as a proper
  schema'd Tier 1 tool instead of staying an interactive one-off CLI.

Test coverage: new `09:TP-BASELINE` and `09:TP-TOOLEXT` clusters. Traceability: `18`
doc `01` 109→116 (75 covered), doc `03` 34→36 (24 covered), doc `05` 28→29 (19 covered),
corpus baseline 348→358 (182 covered).

### Round 3 — Secondary Scripter: Dual-Scripter Council Architecture

**Status: ✅ MERGED in full** (`01`, `03`, `09`, `13`, `14`, `18`, `22`, `23`, `15`,
`Agentic VAPT Setup (HOME).md`; decision #74 logged in `10`).

The Alignment Linter (`Qwen2.5-Coder-3B-Instruct`) is retired. Syntax checking is now
Gate 2 **Tier 2A** (`ast.parse()`/`py_compile`/`bash -n`, zero LLM), alongside **Tier 2B**
(existing schema/flag validation) and new **Tier 2C** (orthogonal-vector deduplication
against `03:DR-SCHEMA-21 scripter_execution_ledger`). A **Secondary Scripter**
(`DeepSeek-Coder-6.7B-Instruct`) is added: Phase 4.2 is now batch-sequential — **4.2A**
(Primary Scripter, baseline pass, all targets) → full unload → memory-settle → **4.2B**
(Secondary Scripter, orthogonal pass, all targets, explicitly excluding every vector
Primary already tried, enforced deterministically by Tier 2C, not model self-restraint).
Council size unchanged at 6 — a clean swap, not a growth.

**Naming:** an external draft of this proposal used "Operator"/"Beta"/mismatched enum
naming for the new role (`Operator Beta`, `Primary Operator`, `PRIMARY_OPERATOR` vs.
`SECONDARY_SCRIPTER`, `@op1`/`@op2`, `TP-OP-ORTHOGONAL-01`, `operator_execution_ledger`)
— confirmed a mistake of an outdated external source and ignored throughout. **Secondary
Scripter** / **Primary Scripter** / `PRIMARY_SCRIPTER`/`SECONDARY_SCRIPTER` /
`@script1`/`@script2` / `TP-SCRIPT-ORTHOGONAL-01` / `scripter_execution_ledger` used
consistently instead, matching the corpus-wide rename (decision #72).

**Codebase question, resolved:** confirmed no `vapt_agent/` directory or Python source
exists anywhere in this repo (verified by search) — this stays documentation-only,
per `00`'s own "Planning phase only" status. Folded into `13`'s already-documented module
tree and prose (`gate2_validator.py`, `phase_lifecycle.py`, `secondary_scripter.py`
descriptions) rather than creating real `.py` files.

**Schema-duplication question, resolved:** kept `scripter_execution_ledger` as a separate
narrow table (not merged into `tool_execution_logs`) but documented explicitly why: it
exists purely as a fast lookup index for Tier 2C's hash-membership check, populated by
the same write path as `tool_execution_logs` — never a second source of truth for *what
happened*, only for *has this exact vector been tried yet*.

**Post-merge consistency check** (explicitly requested) caught and fixed 3 real defects
the new architecture introduced, none of which were part of the original directive:
- `01:FR-COUNCIL-12`'s unload-timing wording didn't account for the new two-sub-phase
  split (fixed: Primary unloads at 4.2A's end, Secondary at 4.2B's end, both still
  "never per-task/per-target").
- `01:FR-GATE-07`'s context-ceiling table still listed the retired
  `Qwen2.5-Coder-3B-Instruct` and omitted the new model entirely (fixed: removed the
  stale 4k tier, added `DeepSeek-Coder-6.7B-Instruct` at 16k).
- `23:FR-INTERVENE-07`'s per-invocation directive-injection list still named "the
  Alignment Linter's between-phase invocation" instead of the new Phase 4.2B invocation
  point (fixed).

Also fixed in `HOME.md` (not a defect from this round, but caught during the same pass):
the relay diagram's Gate 2 label still said "Is the command safe?" — the exact "safety"
framing R2.3 established was wrong for this check — and a leftover pre-R2.6 sentence in
the user story still described Console commands as "overriding" the AI instead of
running alongside it. Both corrected.

**Memory budget:** verified fine — `DeepSeek-Coder-6.7B-Instruct` (~7.2 GB) is smaller
than the largest existing model (~8.6 GB), and models never reside concurrently
(`FR-GATE-02`), so the peak single-model memory ceiling, ~13.0 GiB post-hibernation
headroom target, and 1.5 GiB safety margin are all unaffected.

---

### R2.6 — Console Command Handling: Conflict Flag + Corrected Requirement

**Status: ✅ MERGED.** Confirmed exactly as drafted: the Human Operator's command runs
alongside the LLM's pre-defined tasks; on genuine conflict (same resident-model slot),
the Human Operator's command wins. Applied to `23:FR-INTERVENE-06`. Decision #73 logged
in `10`.

Root cause this fixed: `23:FR-INTERVENE-05` said directives are dispatched "ahead of
pending autonomous tasks" (ordering — both run), while `FR-INTERVENE-06` said directives
"supersede autonomous tasks... unconditionally" (sounds like replacement) — the two were
in tension before this correction.

---

### R2.3 — Alignment Linter Elimination

**Status: ✅ RESOLVED — subsumed by Round 3.** You asked *"why do I even need the Linter
LLM!?"* — the recommendation (eliminate it, absorb syntax-checking into deterministic
Gate 2) is exactly what Round 3 did, plus added the Secondary Scripter as its
replacement council seat. No separate action needed beyond what's recorded above.

---

### Round 2 — Role Renaming, Function Corrections & New Requirements

**Status: ✅ MERGED in full**, across `01`, `03`, `05`, `06`, `09`, `10`, `18`,
`CHANGELOG.md`, and (via a background sweep) `00`, `04`, `07`, `08`, `11`–`17`, `19`,
`21`–`24`, and `HOME.md`. "Analyst" was a naming mistake, corrected to **Strategy
Auditor**.

**Final role mapping applied corpus-wide:**

| Old name(s) | New name |
|---|---|
| Lead Strategist | **Lead Strategist** *(unchanged)* |
| Scope Gate / Gatekeeper / Council Gate 1 (Tier 1, semantic) | **Strategy Auditor** |
| Lead Operator / bare AI-role "Operator" | **Primary Scripter** |
| Offline Script Linter | *(retired entirely — see Round 3)* |
| Adjudicator / Gate 3 | **Criterion Adjudicator** |
| Executive Reporter | **Executive Reporter** *(unchanged)* |
| Any human "operator"/"Operator" | **Human Operator** (exact phrase, every occurrence) |
| `Operator-Directed Mode` | **Human-Operator-Directed Mode** |
| `MANUAL_OPERATOR` | **`HUMAN_OPERATOR`** |
| `OPERATOR_DIRECTIVE` | **`HUMAN_OPERATOR_DIRECTIVE`** |
| `operator_command_queue` | **`human_operator_command_queue`** |
| `operator_identity` | **`human_operator_identity`** |

Verified by whole-corpus grep with zero stale hits (two deliberate, confirmed-correct
exceptions: "NoSQL operator-injection" in `19` and lowercase "gatekeeper" in `HOME.md` —
both genuinely unrelated meanings, not role references). `13`'s module-layout filenames
renamed to match (`strategy_auditor.py`, `primary_scripter.py`, `criterion_adjudicator.py`,
`secondary_scripter.py` — the last one corrected during Round 3 after briefly landing as
`alignment_linter.py`, which would have cemented the deprecated role into the module
tree).

**R2.2 — Strategy Auditor function correction:** `05:SEC-SCOPE-01` reworded — "Council
Gate 1" means Tier 0 + Tier 1 combined; only Tier 0 mechanically checks `scope_rules`;
the Strategy Auditor never itself decides scope, only whether the Lead Strategist's plan
addresses it and makes sense.

**R2.4 — Human Operator guidance notes:** `01:FR-CTRL-01a` added — bounded inline
`--notes` only (500-char cap, rejected not truncated over-length), no `--notes-file`
(small council models can't usefully consume long documents). Schema, test rows, and
traceability all updated alongside.

**R2.5 — Error reporting & notification policy:** `06:OPS-NOTIFY-01`–`05` added —
severity tags surfaced live on Dashboard/Console, no silent full stops, a formal Error
Code Dictionary (your "do we need a dictionary" question — yes), and full raw error
printing to the terminal for pre-Dashboard/Console technical failures (your "this is a
technical step" point).

**R2.7 — Persistence/pause-resume:** confirmed already existing and fairly robust
(`FR-CTRL-02`/`03`, `OPS-LIFECYCLE-02`/`03`/`04`, the whole SQLite WAL state store) — no
new requirement was needed.

---

### Items 1 & 2 — Hibernation Self-Exclusion + Dashboard/Console Exposure

**Status: ✅ MERGED** (approved with a rectification changing the operator workflow
itself, applied to `01`, `10`, `18`, `22`, `23`).

Rather than generalizing hibernation-detection to recognize arbitrary `vaptctl`
processes in arbitrary terminals, the operator workflow changed instead: `dashboard`/
`console` are no longer manually launched concurrently with `start`. `start` now
auto-launches both automatically, in new terminal windows, immediately after Phase 1
hibernation's headroom check clears and strictly before Phase 2 — removing the
concurrent-launch race at its root, since by the time `dashboard`/`console` exist the
one-shot hibernation sweep is already over. `FR-ENV-03a`/`08a`/`08b`/`08c` added to `01`;
the standalone `vaptctl dashboard`/`vaptctl console` commands remain, re-scoped
explicitly as manual-recovery commands.

---

## How to add new items

New items go **above the archive, under "Currently Pending Approval"** — newest on top,
per standing instruction. Same format as always: problem statement → root cause →
proposed fix (exact draft text, per `CLAUDE.md` §5 schema where a real requirement is
being authored) → status. Nothing in this file is binding until explicitly approved and
applied to the numbered docs.
