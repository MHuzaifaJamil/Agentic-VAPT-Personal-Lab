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

*(nothing pending — Rounds 6, 7, 8 approved and merged; see Archive below.)*

---

## Archive — Resolved / Merged Items (newest first)

### Round 8 — Dynamic Domain-Based Tool Discovery (WiFi/Bluetooth, and the Wider Kali Catalog)

**Status: ✅ MERGED (decision #77).** `FR-DISCOVER-01..03` added to `01`, referencing
`KALI-TOOL-CATALOG.md`. The flagged wireless-checkpoint question was resolved by
proceeding with the recommended approach: `FR-DISCOVER-04` classifies actively
disruptive wireless/Bluetooth actions under a new `ACTIVE_WIRELESS_DISRUPTION`
checkpoint class, gated identically to `LIVE_CREDENTIAL_SPRAY` (`FR-CHECKPOINT-01`
extended from five to six classes). Passive wireless/Bluetooth tools stay ungated.

You asked for wireless/Bluetooth task support plus "every possible tool" from
`kali-linux-everything`, and pushed back (correctly) on "too many to enumerate" —
**the fix was simpler than I made it sound**: put the full list in a separate reference
file, not inside the requirements corpus. Done — `KALI-TOOL-CATALOG.md` (repo root) now
has the complete, current tool set for every one of Kali's ~29 official tool categories
plus everything else `kali-linux-everything` bundles directly, pulled straight from this
machine's own `apt-cache show` output (not reconstructed from memory). `FR-TOOL-03`'s
Tier 2 dynamic bridge already lets the AI invoke any resolvable binary — the missing
piece was purely *discoverability*, which the new file now solves directly.

> ### FR-DISCOVER-01: Consult `KALI-TOOL-CATALOG.md` for Undefined Task Domains
> * **Statement**: When a task falls in a domain with no dedicated Tier 1 schema (e.g.
>   wireless, Bluetooth, forensics, hardware), the system MUST consult
>   `KALI-TOOL-CATALOG.md` (repo root — a reference file, not a requirement doc, kept
>   current against `apt-cache show kali-linux-everything` and its category
>   metapackages) for candidate tool names in that category, rather than the Scripter
>   guessing at binary names or the corpus trying to enumerate every tool inline.
> * **Pre-conditions & Inputs**: A task is tagged with a domain that has no dedicated
>   Tier 1 tool already covering it.
> * **Post-conditions & State Mutations**: The matched category's candidate list is
>   surfaced to the Scripter as available options for that task, resolved through
>   `FR-DISCOVER-02`.
> * **Edge & Failure Behaviors**: An untagged/unknown domain, or one not found in the
>   catalog, falls back to `FR-TOOL-03`'s generic Tier 2 bridge unchanged — this is
>   additive, not a replacement. If the catalog file itself is missing/unreadable, log
>   degraded and fall back the same way — never block the task on a reference-file read.
> * **Target Verification**: *(new test row needed in `09`)*

> ### FR-DISCOVER-02: Presence Check Before Suggesting
> * **Statement**: Before a domain's candidate tools are offered to the Scripter, the
>   system MUST check each one's actual presence (`shutil.which`, the same pattern
>   `oob_listener.py`'s graceful-degradation already uses) — only present binaries are
>   offered as immediately callable; absent ones are reported as "known, not installed"
>   naming the Kali/apt package that provides them.
> * **Target Verification**: *(new test row needed in `09`)*

> ### FR-DISCOVER-03: No Autonomous Package Installation Without Explicit Opt-In
> * **Statement**: The system MUST NOT run a package-manager install (`apt install`,
>   etc.) autonomously by default when a candidate tool is missing — this is a
>   system-modifying action outside this project's read-only-discovery/Tier-1-2-execution
>   model, with real supply-chain-trust and host-state implications. A Human Operator MAY
>   explicitly pre-authorize auto-install via runtime configuration (e.g. a `start` flag);
>   only then does installation proceed, via the same non-shell/`setsid`/logged subprocess
>   rules as everything else, with the install itself recorded in the audit trail.
> * **Edge & Failure Behaviors**: No opt-in given, tool missing: report it and continue —
>   never block the engagement waiting for a tool that isn't there.
> * **Target Verification**: *(new test row needed in `09`)*

**Safety note on WiFi/Bluetooth specifically**: several candidate tools are actively
disruptive by design (`aireplay-ng --deauth`, jamming-style Bluetooth attacks) — these
aren't passive recon, they knock real clients off a real network. **Recommend**: gate
these specific *active* wireless actions the same way `LIVE_CREDENTIAL_SPRAY` is gated
today (`FR-CHECKPOINT-01`'s fixed class list, or a new class alongside it) — autonomous
use requires the same opt-in flag pattern as `FR-TOOL-06a`'s other high-risk categories;
Human-Operator-directed use runs unconditionally as always. Purely passive
scanning/monitoring tools in the same domain (e.g. `bluetoothctl` device enumeration)
would not need this gate. Flagging this distinction for your confirmation rather than
deciding it myself, since it's a genuine new checkpoint-class question.

---

### Round 7 — Phase 5 Mobile Runtime Tools as Tier 1 Candidates

**Status: ✅ MERGED (decision #77).** `19:FR-MOBILE-08` added exactly as drafted:
`objection` formally registered (closing the "named in prose, not schema-registered"
gap against `FR-MOBILE-03`/`05`); `mobsf` added as new static+dynamic analysis
capability. The flagged design question (spawned per-task vs. long-lived local
service) was resolved as per-task-spawned, consistent with this system's
single-residency posture for everything outside the council models themselves.

The arsenal's Phase 5 (2 tools): `mobsf`, `objection`. This project already has a full
Mobile domain (`19:FR-MOBILE-01..07`, `MOBILE_BINARY` target type) — `objection` is
already *named* there (`FR-MOBILE-03`'s cert-pinning bypass, `FR-MOBILE-05`'s utility
list) but not registered as a formal Tier 1 schema entry the way `01`'s tools are.
`mobsf` (Mobile Security Framework — static + dynamic analysis, its own local web UI/API)
isn't mentioned in `19` at all yet.

> ### FR-MOBILE-08 (new): `mobsf` and `objection` as Registered Tools
> * **Statement**: `objection` is formally registered as a Tier 1/Tier 2 tool matching
>   its existing use in `FR-MOBILE-03`/`05` (no functional change, just formal schema
>   registration closing the gap between "named in prose" and "actually callable via a
>   declared schema"). `mobsf` is added as a new Tier 1 tool for static+dynamic mobile
>   analysis, offered as an alternative/complement to the `apktool`/`jadx` + manual-Frida
>   path `FR-MOBILE-01`/`02` already specify — not a replacement for the
>   runtime-first-never-decompile-first methodology `FR-MOBILE-01` mandates.
> * **Edge & Failure Behaviors**: `mobsf` typically runs as a local service (own web
>   UI/API) rather than a one-shot CLI invocation — needs a design decision on whether
>   it's spawned per-task or kept as a longer-lived local service the Scripter calls
>   into; flagging this rather than assuming.
> * **Target Verification**: *(new test row needed in `09`)*

**Also touches**: `06:FR-MOBILE-06`'s hardware-constraint note (emulator RAM budget)
already covers `mobsf`'s likely resource footprint if it needs an emulator too — no new
constraint, just confirming it applies.

---

### Round 6 — Phase 4 Exploitation Tools as Tier 1 Candidates (AI-Gated Loop Only)

**Status: ✅ MERGED (decision #77), including the requested gap-check.** The 4
genuinely-new tools (`dalfox`, `xsstrike`, `ghauri`, `fuxploider`) registered exactly
as drafted. The gap-check against `19` (performed before merging, per explicit
instruction, rather than assuming redundancy either way) found: `cewler` and the
hashcat-rule-mutation technique were already named in `FR-CRED-01`'s prose —
**formally Tier 1 schema-registered now, not skipped as a duplicate** — same
treatment for `interactsh-client`, already an explicitly required dependency per
`FR-ARGUS-02`. `hashcat`, `cupp`, `trevorspray`, `kerbrute` were not named anywhere in
`19` — genuinely new registrations implementing `FR-CRED-01`'s existing 4-stage
framework (`kerbrute` closes a real gap: `FR-CRED-03`'s mode list had no Kerberos/AD
mode). All ten tools registered — per standing instruction, overlap with existing
mechanisms is documented accurately, never used as grounds to skip registration.

The arsenal's Phase 4 (11 tools). **Confirmed staying out of `FR-BASELINE`'s zero-AI
pipeline** — these are exploitation-class, gated through the normal Gate 1/Gate 2/
Adjudicator loop like any other Tier 2 action, same as `sqlmap` (already registered)
already works today.

**Genuinely new capability, no current overlap** — straightforward Tier 1 additions:
- `dalfox`, `xsstrike` — XSS scanning/confirmation (no dedicated XSS tool currently registered)
- `ghauri` — blind-SQLi specialist, complements rather than replaces `sqlmap`
- `fuxploider` — file-upload RCE testing (no current equivalent)

**Needs a gap-check before registering, not assumed redundant** — flagging these as
*likely* overlapping existing project mechanisms, rather than either registering or
skipping them without checking first:
- `hashcat`, `cewler`, `cupp`, `trevorspray`, `kerbrute` — `19:FR-CRED-01` already
  specifies a 4-stage credential-attack pipeline (wordlist gen, breach enrichment,
  employee OSINT, live spray). Worth checking whether these five tools are the
  *implementation* of stages `FR-CRED-01` already calls for, or genuinely new capability
  it's missing — my guess is the former (these look like exactly the tools that pipeline
  would use), meaning this is a "confirm it's built," not "register something new."
- `interactsh-client` — already wrapped by `oob_listener.py` per
  `ASSET-CLASSIFICATION.md`'s own finding. Almost certainly already covered; would need
  confirming `oob_listener.py` is actually wired to a Tier 1 schema, not just archived
  as reference material.

**Recommend**: approve the 4 genuinely-new tools now; treat the credential/OOB five as a
"verify existing coverage" task rather than a registration task, since duplicating an
already-built mechanism under a new name would be worse than doing nothing.

---

### Round 5 — Expand `FR-BASELINE` With the Full Personal Tool Arsenal

**Status: ✅ MERGED in full**, with a correction applied after initial merge (`01`, `09`,
`13`, `18`; decision #76 in `10`, amended by a same-session follow-up).

- Pulled the actual 72-tool arsenal from the operator's portfolio report; scoped to
  Phase 1+2+3 (recon, enumeration, **and assessment** — assessment folded in per
  operator correction, since those tools are detection/read-only probes, not
  exploitation) for the zero-AI `FR-BASELINE` pipeline. Phase 4/5 (exploitation, mobile
  runtime) confirmed excluded, spun into their own rounds below (6, 7).
- Trigger point moved: runs between Phase 1 and Phase 2 (before the first model loads
  at all), not after Phase 3 — resolved without renumbering any phase, since the
  pipeline's direct safe-subprocess dispatch doesn't need Phase 3's AI-facing schema
  registration.
- Execution model: 4 dependency waves, bounded parallel execution within each wave
  (default 8 concurrent) — `naabu` (fast sweep) → `nmap -sV` (targeted, naabu's ports
  only) satisfies "use both naabu and nmap."
- **Post-merge correction** (operator: "overlap is always welcome, even when purposes
  overlap"): the initial merge trimmed several overlapping-purpose tools for efficiency
  (a judgment call, not requested) — reversed on operator correction. Added back
  `bbot`/`theHarvester`/`knockpy`/`dnsrecon`/`massdns`/`shuffledns` (Wave 1) and
  `waymore`/`hakrawler`/`gospider`/`cariddi`/`aquatone`/`eyewitness` (Wave 3); `sublert`
  now runs in both `FR-BASELINE` (one-shot) and `FR-MONITOR` (continuous) rather than
  only the latter. Only `maigret`/`pywhat` stay Tier-2-only — not a trim, an input-shape
  mismatch (username/string input, not domain/IP, so a blind per-target pipeline has
  nothing to feed them).

Traceability: `18` doc `01` 109→119 (78 covered); corpus baseline 348→361 (185 covered).

---

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
