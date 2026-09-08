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

## Round 4 — Baseline Recon Pipeline, Efficiency Re-Check, Deferred-Gap Integration Points

**Status: 🔶 PENDING APPROVAL — nothing in this round applied to any binding doc.**
Drafted per `CLAUDE.md` §5.2 schema. Investigated directly against the actual scripts
(not just re-reading `ASSET-CLASSIFICATION.md`'s prior verdicts) before drafting.

---

### R4.1 — Efficiency Re-Check: `port_scanner.py`'s "redundant with nmap" verdict is WRONG

You asked the right question. I read the actual script instead of trusting the prior
summary — **the earlier "redundant with `nmap -sV`" verdict was too quick.**

`port_scanner.py` wraps ProjectDiscovery's `naabu` — an async SYN scanner purpose-built
for scanning thousands of ports/hosts fast, deliberately deferring deep service
fingerprinting to a second pass. `nmap -sV` (or even `nmap -p-`, this project's existing
"Deep-Full-Range" 1800s tier) does real version detection, which is inherently slower —
naabu-class scanners exist specifically *because* nmap's `-sV` is too slow for broad
discovery at scale. These are not the same tool doing the same job at different
verbosity; they're different points on a real speed/depth tradeoff. The script's own
stated purpose reinforces this isn't about ports `nmap` "also happens to cover" — it's
about surfacing non-HTTP services (SSH, Redis, admin panels on odd ports) *fast*, before
committing slower tools to a target.

**Recommendation, tied into R4.3 below:** rather than registering `naabu` as a standalone
Tier 1 tool competing with `nmap`, use it for exactly what it's good at — the **first
step** of the new baseline-recon pipeline (R4.3), where speed matters most and deep
version detection isn't the point yet. `nmap` remains the deep/targeted scanner for
specific ports once the baseline pass has narrowed things down.

**This does introduce a new external tool dependency** (`naabu`, a Go binary, not
currently in `01:FR-TOOL-01`'s Tier 1 roster or `FR-PRE-04`'s presence check) — flagging
this explicitly since adding a dependency has real provisioning implications. Alternative
if you'd rather not add a new binary: `nmap -T4 --min-rate 5000 -p-` gets meaningfully
closer to naabu's speed with tuning, at the cost of being slower and noisier than a
purpose-built async scanner. **Your call — noted as a decision point in R4.3.**

---

### R4.2 — Efficiency Re-Check: the other "redundant" verdicts hold up

Checked the actual scripts for these too — no corrections needed:

- **`lead_board.py`** — its real value is the status-tracking workflow (`new →
  investigating → killed → reported → parked`, idempotent re-ingestion that never resets
  progress). This project's SQLite schema (`task_queue`/`discovered_entities`/
  `verified_vulnerabilities`, each with their own status columns) already does the
  structured-equivalent of this, queried by the council instead of a human reading a
  board. SQL lookups are also mechanically more efficient than scanning a JSONL file
  for "what's still untouched." Verdict holds.
- **`memory_gc.py`** — rotates JSONL log files. This project's retention/disk-quota
  concern is already owned by `03:DR-RETENTION`/`06:OPS-MAINT-03` for a completely
  different storage medium (SQLite + artifact files, not free-standing JSONL logs).
  Verdict holds — nothing to port, the *concern* is already covered structurally.
- **`validate.py`** — an interactive human-walkthrough tool. Comparing it to the
  Adjudicator/Gate 3 (fully automated) isn't really an efficiency question — automating
  a manual checklist is strictly more efficient for a system designed to run unattended.
  Verdict holds.

---

### R4.3 — `16:TR-SCRIPT-06` (revised): Deterministic Baseline Recon Before Phase 4.1

This replaces the current vague wording ("the pattern... MUST be implemented as the
standard task-generation pattern") with what you actually asked for: a real pipeline
that runs once per target, automatically, before the Lead Strategist's first invocation
— its output becomes the Strategist's starting context instead of a blank target.

> ### TR-SCRIPT-06 (revised): Baseline Reconnaissance Pipeline
> * **Statement**: Immediately after Phase 3 (Tool Bridge) completes for a target, the
>   system MUST automatically run a fixed, deterministic sequence of already-registered
>   tools against that target — no AI model invoked at any point — capture and structure
>   the combined output, and inject it into the Lead Strategist's first Phase 4.1
>   invocation as a pre-populated `<baseline_recon_findings>` context block. This
>   reimplements `full_hunt.sh`'s technique natively (per the same "write new, matching
>   the mined technique, don't force a bad bash port" precedent already used for
>   `zero_day_fuzzer.py`/`graphql_scanner.py`), not a literal port of the bash script.
> * **Pre-conditions & Inputs**:
>   * Initial State: Phase 3 has confirmed all required Tier 1 tool bridges are wired.
>   * Input / Trigger: A target completes Phase 3 for the first time this engagement
>     (skipped on `resume` if already run for that target — recorded, not re-executed).
> * **Post-conditions & State Mutations**:
>   * Mutation: Fixed pipeline order — (1) fast port sweep [see R4.1's open decision:
>     `naabu` or tuned `nmap`], (2) `whatweb` tech fingerprinting (feeds `discovered_entities`
>     with `entity_type = 'tech_fingerprint'` — also feeds R4.5 below), (3) `ffuf`/
>     `feroxbuster` content discovery, (4) `nuclei` baseline-template scan. Each step's
>     raw output persists via the existing `tool_execution_logs`/artifact-index path —
>     no new storage mechanism, this is ordinary Tier 1 execution, just sequenced
>     deterministically instead of AI-selected.
>   * Output: A structured summary (ports found, technologies fingerprinted, discovered
>     paths, any baseline nuclei hits) assembled from those same rows and handed to the
>     Strategist verbatim as context — not re-summarized by a model, to avoid
>     hallucinating detail into a deterministic result.
> * **Edge & Failure Behaviors**:
>   * Any individual step fails/times out: log it, continue to the next step — a partial
>     baseline (e.g. port sweep succeeded, content discovery timed out) is still handed
>     to the Strategist with the gap noted, never blocking Phase 4.1 entirely on one
>     slow/failed tool.
>   * `resume` after this already ran for a target: re-use the persisted results, don't
>     re-run the pipeline (matches `06:OPS-LIFECYCLE-02`'s existing "don't redo completed
>     work" pattern for Phase 1 hibernation).
> * **Target Verification**: *(new `TP-BASELINE` cluster needed in `09`)*

**Open decision carried from R4.1**: fast port sweep via new `naabu` dependency (real
speed win, new tool to provision) vs. tuned `nmap -T4 --min-rate 5000 -p-` (no new
dependency, slower). Recommend `naabu` given this is exactly the use case it's built
for, but it's your infrastructure to provision.

**Also touches, if approved**: `01` (new requirement referencing this pipeline's
Phase-3→4.1 trigger point), `13` (module tree — a new `baseline_recon.py`), `09`/`18`
(test coverage and counts, computed at merge time).

---

### R4.4 — Integration Point: Authenticated Session Testing (`auth_session.py` + `credential_store.py`)

**The gap, precisely:** every Tier 1/Tier 2 call today is a fresh subprocess — there's no
concept of "stay logged in across several tool calls." `FR-TOOL-15` already propagates
*credentials* (for brute-force) but not an *established session* (cookies/bearer tokens
obtained after a real login flow, reused across many subsequent calls against
authenticated areas of a target).

> ### FR-TOOL-17: Authenticated Session Reuse
> * **Statement**: The system MUST support establishing a named authenticated session
>   (cookie jar or bearer/token-based) against a target once, then automatically
>   injecting that session's credentials into every subsequent Tier 1/Tier 2 call
>   scoped to that session — without re-authenticating per call.
> * **Pre-conditions & Inputs**:
>   * Initial State: A target requires authentication to reach interesting surface.
>   * Input / Trigger: A Human Operator supplies login credentials/a pre-captured
>     session at `start` or via the Console; OR an autonomous login-flow task succeeds
>     (scope-gated the same as any other autonomous action).
> * **Post-conditions & State Mutations**:
>   * Mutation: New schema table `auth_sessions` (`session_id`, `target_id`, `auth_type`
>     [`cookie`/`bearer`/`basic`], `credential_ref` — same `sha256(...)[:12]` correlation-hash
>     pattern as `FR-TOOL-15`, never the raw secret in logs, `established_at`,
>     `last_validated_at`, `valid` bool).
>   * Output: Tier 1/Tier 2 calls scoped to a session get the session's auth material
>     injected via env var/header, the same mechanism `FR-TOOL-15` already uses.
> * **Edge & Failure Behaviors**:
>   * Session invalidated mid-engagement (logout, expiry): mark `valid = 0`, surface via
>     `OPS-NOTIFY` (not a silent failure — subsequent authenticated calls would otherwise
>     look like false-negative findings), do not auto-retry login without a fresh
>     Human-Operator-supplied or autonomously-re-validated credential.
> * **Target Verification**: *(new test row needed in `09`)*

**Also touches, if approved**: `03` (new `DR-SCHEMA-22: auth_sessions`), `05` (this
credential-handling should inherit `SEC-DATA`'s local-only/no-raw-secret-in-logs rules
explicitly).

---

### R4.5 — Integration Point: Tech-Fingerprint-Driven Intel/EOL Lookups (`eol_check.py`, `intel_engine.py`, `learn.py`)

**The gap, precisely:** these scripts need `tech=version` pairs to look up against
EOL/CVE databases, and nothing currently produces that fingerprint data in a queryable
form. **R4.3 closes exactly this gap as a side effect** — the baseline recon pipeline's
`whatweb` step already writes `entity_type = 'tech_fingerprint'` rows to
`discovered_entities`. This integration point is genuinely cheap once R4.3 exists.

> ### FR-TOOL-18: Fingerprint-Triggered EOL/CVE Lookup
> * **Statement**: Whenever a new `tech_fingerprint` row is written to
>   `discovered_entities` (by the baseline pipeline, `R4.3`, or any other tool), the
>   system MUST automatically queue a follow-on Tier 2 task that checks that
>   `tech=version` pair against an EOL database (`eol_check.py`'s technique — a plain
>   `endoflife.date` API lookup, no auth needed) and a CVE feed (`intel_engine.py`'s
>   technique — GitHub Advisory DB / NVD lookup by product+version).
> * **Pre-conditions & Inputs**:
>   * Initial State: A `tech_fingerprint` entity was just inserted (`INSERT OR IGNORE`
>     per `discovered_entities`' existing uniqueness rule — this task only queues for a
>     genuinely *new* fingerprint, not a repeat sighting).
> * **Post-conditions & State Mutations**:
>   * Mutation: Results (EOL status, known CVEs) attach to that fingerprint row (new
>     nullable columns, or a small companion table — implementer's call) for the
>     Reporter/Adjudicator to reference as supporting evidence, not as a finding by
>     itself (an EOL/CVE hit is corroborating evidence, not proof of exploitability).
> * **Edge & Failure Behaviors**:
>   * `endoflife.date`/CVE feed unreachable (offline environment): log degraded, don't
>     block the pipeline — this is enrichment, not a required gate.
> * **Target Verification**: *(new test row needed in `09`)*

---

### R4.6 — Integration Point: `multipart_mutator.py` as a Proper Tier 1 Tool

**The gap, precisely:** flagged as "doesn't fit Tier 1's one-schema-per-tool model"
because the original CLI is interactive/one-off (`--file`/`--send` against a single
local file). But its actual *technique* — a fixed, enumerable set of parser-confusion
multipart-upload variants — is exactly as schema-able as any other Tier 1 tool once the
interactivity is stripped out.

> ### FR-TOOL-19: Multipart Parser-Confusion Tool (Tier 1)
> * **Statement**: The system MUST register a Tier 1 tool wrapping
>   `multipart_mutator.py`'s variant set (boundary confusion, duplicate-field injection,
>   content-type mismatches, and whatever other fixed variants the original script
>   enumerates) with a declarative schema: `{target_upload_endpoint, file_path,
>   variant_name | "all"}` — no interactive prompts, no manual `--send` step.
> * **Pre-conditions & Inputs**:
>   * Initial State: A target has a discovered file-upload endpoint.
>   * Input / Trigger: Primary/Secondary Scripter selects this tool against that endpoint.
> * **Post-conditions & State Mutations**:
>   * Output: Standard Tier 1 output shape (response per variant, status codes) — same
>     evidence path as any other Tier 1 tool, no bespoke reporting format.
> * **Edge & Failure Behaviors**:
>   * `file_path` doesn't resolve inside the artifact workspace: rejected the same way
>     `script_runner`'s `workspace_subdir` check already works (`FR-TOOL-16`) — reuse
>     that existing boundary check, don't invent a new one.
> * **Target Verification**: *(new test row needed in `09`)*

---

## Archive — Resolved / Merged Items (newest first)

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
