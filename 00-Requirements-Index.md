# Requirements Documentation Index — Autonomous Agentic VAPT System

**System under specification:** The Autonomous Agentic VAPT System described in
[`Agentic VAPT Setup (HOME).md`](./Agentic%20VAPT%20Setup%20(HOME).md) — a locally-hosted,
6-model LLM council that plans, executes, and reports on vulnerability assessment /
penetration testing engagements against authorized targets, running entirely on a
single Kali Linux host with no cloud dependency.

This index is the entry point into the full requirements set. The base architecture
document defines *what hardware exists* and *what the 5-phase lifecycle looks like*.
The documents below convert that architecture into a complete, testable requirements
baseline: what the system must do, how well it must do it, what data it owns, how its
parts talk to each other, how it stays safe and legal to operate, how it is run day to
day, what can go wrong, and how each requirement will be verified.

**Status:** Planning phase only. No installation, download, or execution has been
performed as part of producing this documentation set.

---

## Document Map

| # | Document | Purpose |
|---|----------|---------|
| 00 | `00-Requirements-Index.md` | This file — navigation and traceability overview |
| 01 | [`01-Functional-Requirements.md`](./01-Functional-Requirements.md) | What the system must do, phase by phase, as testable FR-IDs |
| 02 | [`02-NonFunctional-Requirements.md`](./02-NonFunctional-Requirements.md) | Performance, reliability, resource, usability, maintainability targets |
| 03 | [`03-Data-and-Storage-Requirements.md`](./03-Data-and-Storage-Requirements.md) | SQLite schema, artifact store layout, retention, backup |
| 04 | [`04-Interface-and-Integration-Requirements.md`](./04-Interface-and-Integration-Requirements.md) | Inference API contract, MCP servers, tool bridge, operator control surface |
| 05 | [`05-Security-Safety-and-Compliance-Requirements.md`](./05-Security-Safety-and-Compliance-Requirements.md) | Authorization gating, scope enforcement, kill-switch, audit trail, legal/ethical constraints |
| 06 | [`06-Operational-Requirements.md`](./06-Operational-Requirements.md) | Startup/shutdown lifecycle, monitoring, logging, maintenance procedures |
| 07 | [`07-Risk-Register.md`](./07-Risk-Register.md) | Identified risks, likelihood/impact, mitigations, owners |
| 08 | [`08-Assumptions-Constraints-Dependencies.md`](./08-Assumptions-Constraints-Dependencies.md) | What is assumed true, hard constraints, external dependencies, non-goals |
| 09 | [`09-Acceptance-Criteria-and-Test-Plan.md`](./09-Acceptance-Criteria-and-Test-Plan.md) | Verification method and pass/fail criteria per requirement |
| 10 | [`10-Decision-Log-and-Open-Questions.md`](./10-Decision-Log-and-Open-Questions.md) | Chronological record of every explicit operator decision behind this doc set, plus what's still genuinely open |
| 11 | [`11-Critical-Analysis-and-Design-Challenges.md`](./11-Critical-Analysis-and-Design-Challenges.md) | Adversarial review of the base plan's technical claims (C-01 through C-31), every one resolved except C-29 (genuinely open) |
| 12 | [`12-Report-Formatting-Rules.md`](./12-Report-Formatting-Rules.md) | Independent-practice VAPT report formatting standard (cloned/adapted from `claude-bug-bounty`'s rules, referenced by `FR-COUNCIL-17a`) |
| 13 | [`13-Implementation-Architecture-Bridge.md`](./13-Implementation-Architecture-Bridge.md) | Closes the requirements→code gap: process/daemon model, language baseline, file formats, privileged-helper contract, CLI framework, proposed module layout |
| 14 | [`14-System-Prompt-Templates.md`](./14-System-Prompt-Templates.md) | Actual system-prompt text for every prompted council role |
| 15 | [`15-Implementation-Milestone-Roadmap.md`](./15-Implementation-Milestone-Roadmap.md) | Build order — 9 independently-testable milestones from schema skeleton to full acceptance pass |
| 16 | [`16-Actual-Setup-Reuse-and-Integration-Map.md`](./16-Actual-Setup-Reuse-and-Integration-Map.md) | Asset-by-asset analysis of `Actual-Setup/` (the `claude-bug-bounty` toolkit copy) — what reuses, what doesn't, what was actually mined into `01`/`14` this pass vs. flagged as future work |
| 17 | [`17-Standalone-Engine-Reuse-and-Comparison.md`](./17-Standalone-Engine-Reuse-and-Comparison.md) | Comparison against `claude-bug-bounty`'s standalone (non-Claude-Code) `agent.py`/`brain.py`/`engine.py` — **includes a safety notice on real client data that must never be copied into this project** — plus the four gaps it surfaced (`FR-COUNCIL-17b` report grounding, `FR-COUNCIL-11b` failure circuit breaker, `FR-TOOL-14` rate limiting, and one genuinely unresolved item) |
| 18 | [`18-Requirement-to-Test-Traceability-Matrix.md`](./18-Requirement-to-Test-Traceability-Matrix.md) | Coverage report — every requirement ID in `01`-`08`/`11`/`13` checked against `09`'s test plan for a specific, citable `TP-*` match; 316 IDs total as of its own writing (later closed to zero genuinely-uncovered gaps — see decision #56/`09`'s later revision; this document's own ID-by-ID rows were not re-walked afterward, so treat its per-ID verdicts as a point-in-time snapshot, not a live-updated ledger) |
| 19 | [`19-Extended-Capability-Domains.md`](./19-Extended-Capability-Domains.md) | Formalizes 19 specialized skill domains from `Actual-Setup/skills/` (web3/smart-contract, mobile, meme-coin, GraphQL, CI/CD, credential-attack, source-code-access, and more) as explicit in-scope capability, built on a full deep-mine of each — includes the schema generalization for non-network target types and the new Human Checkpoint Gate this required |
| 20 | [`20-Human-Checkpoint-and-Escalation-Safety-Catalog.md`](./20-Human-Checkpoint-and-Escalation-Safety-Catalog.md) | Full rationale for the four action classes that hard-stop for live operator confirmation (anti-forensics, live credential-spray, CI/CD external artifacts, dependency-confusion publish) — the *why*, at a depth `19`'s individual domain sections didn't have room for |
| 21 | [`21-Safety-Ethics-and-Misuse-Prevention-Control-Inventory.md`](./21-Safety-Ethics-and-Misuse-Prevention-Control-Inventory.md) | The complete catalog of every control that keeps this system acting as an authorized ethical-hacking tool rather than an uncontrolled offensive agent — location, purpose, and impact for each, across `01`-`22` |
| 22 | [`22-VAPT-Monitoring-Dashboard-Specification.md`](./22-VAPT-Monitoring-Dashboard-Specification.md) | A live, terminal-based `vaptctl dashboard` — turn/time forecasting engine, model-matrix semantics, visual palette, and the corrections made to an operator-supplied draft spec during consistency review |

**Read order for a new reader:** `00` → `11` (see what was challenged and why) → `10`
(see how every challenge and every open design fork was actually resolved) → `01`-`09`
(the resulting requirements, which already read as settled — the *why* lives in `10`
and `11`, not repeated inline everywhere). Then `13`-`15` before writing any code —
they're the requirements→buildable-spec bridge, not optional extras.

**For a build-time coding agent — "I need to build X, which document?"** (the same
table also lives in `CLAUDE.md` at the repo root, which a Claude Code session reads
automatically on start; this copy is here in case that file goes missing or another
tool is used instead):

| You're working on... | Read |
|---|---|
| What the system must do, phase by phase (functional behavior) | `01` |
| Performance, reliability, resource budgets (RAM/disk/timeouts) | `02` |
| SQLite schema, table definitions, artifact file layout | `03` |
| API contracts, CLI command surface, tool-bridge interfaces | `04` |
| Security rules, privilege boundaries, kill-switch, redaction | `05` |
| Day-to-day operation: startup/shutdown, monitoring, degraded-mode behavior | `06` |
| What could go wrong and how it's mitigated, before touching a risky area | `07` |
| What's assumed true, what's explicitly out of scope, external dependencies | `08` |
| How to verify a requirement is actually satisfied (writing tests) | `09` |
| **Why** a requirement reads the way it does (every decision, chronological) | `10` |
| What was technically wrong with the original plan and how it was fixed | `11` |
| Exact client-report formatting (HTML/CSS structure for PDF rendering) | `12` |
| Process model, language, file formats, privileged-helper contract, module layout | `13` |
| The actual system-prompt text to send to each LLM role | `14` |
| What order to build things in | `15` |
| What to actually reuse from `Actual-Setup/`, and what's Claude-Code-only | `16` |
| What's in `Standalone-Engine-Reference/` and why (**read the safety notice first**) | `17` |
| Whether a requirement actually has a test behind it (coverage gaps) | `18` |
| Web3/mobile/GraphQL/CI-CD/credential-attack/source-code-access capability domains | `19` |
| Why four specific actions require a live human checkpoint, not just a config flag | `20` |
| The original high-level plan (now corrected in place — see below) | `Agentic VAPT Setup (HOME).md` |
| Existing reusable skills/tools/agents from a prior Claude-Code-based toolkit | `Actual-Setup/` (read `16` first) |
| A standalone, non-Claude-Code hunting engine, kept for comparison only | `Standalone-Engine-Reference/` (read `17` first) |

**`Agentic VAPT Setup (HOME).md` is not the authoritative spec — `01`-`22` are.** It
has been corrected in place for major issues (inline `*(...)*` notes, each pointing
to a finding in `11`), but deliberately states corrections at a **high level only**
and predates the `19`/`20` capability expansion entirely; `01`-`22` carry full
precision. If the two ever seem to disagree on a detail, `01`-`22` wins. `Actual-Setup/`
and `Standalone-Engine-Reference/` are separate, already-functional reference
material, not themselves the system being planned here.

---

## How These Documents Relate to the Base Architecture

The base document's four sections map onto this requirements set as follows:

* **§1 Target Hardware & Host Environment** → constrains every NFR in `02` (memory
  budgets, thread pinning, storage paths) and is treated as a fixed **assumption** in `08`.
* **§2 Multi-Model LLM Council** → each model's "Primary Mandate" becomes a cluster of
  FR-IDs in `01` (one cluster per council seat) plus an interface contract in `04`.
* **§3 Master Operational Blueprint (5-Phase Lifecycle)** → each phase becomes a section
  of FR-IDs in `01`, with entry/exit criteria defined in `09`.
* **§4 Resource Allocation & Operational Thresholds** → becomes the quantitative targets
  in `02` (NFR-PERF, NFR-RES) and the abort thresholds in `06` and `07`.

## Gaps Identified in the Base Architecture

While detailing the plan, the following gaps were found in the original document and
are addressed by new requirements rather than left implicit:

1. **No definition of who writes target scope data or in what format** — the plan
   assumes a "target scope" already exists in SQLite (consumed by the Strategist and
   checked by Council Gate 1) but never defines the intake format. Note: per explicit
   decision, authorization/Rules-of-Engagement (RoE) *verification* is **out of scope**
   for this system — obtaining/confirming authorization is the operator's
   responsibility outside the tool. Only the scope-*data format* question is addressed
   in `05`; no authorization-gating requirement is included.
2. **No human-in-the-loop control surface** — the base blueprint runs end-to-end with
   only internal LLM gates and no operator pause/resume/abort control, no approval
   checkpoint before destructive actions, and no kill-switch. Addressed in `04` and
   `05` (CLI-only control surface, confirmed). *(Note: the gate roster itself has
   since changed from the base plan's original two gate-models — see `11` findings
   C-03/C-09 and `10` decisions #34-35: Gate 1 is now a two-tier deterministic+LLM
   check, and Gate 2 is fully deterministic, not an LLM. The Gate 1 LLM tier's model
   has changed twice since — see decision #55 and C-03's revised resolution — and is
   `Hermes-3-Llama-3.1-8B` as of that decision.)*
3. **No Phase 0 (pre-flight self-test)** — the blueprint assumes the inference engine,
   GPU drivers, and Kali tool suite are already verified working. Addressed as FR-PRE
   in `01`, including a mandatory GPU-offload benchmark (`FR-PRE-08`).
4. **No defined report deliverable format, evidence redaction policy, or CVSS/CWE
   mapping detail.** Addressed in `01` (`FR-COUNCIL-16a`-`18`) and `12` (formatting
   standard) — Markdown-first with operator approval gating HTML/PDF rendering and
   evidence unredaction.
5. **No error/crash recovery model** — what happens if a model hangs, a subprocess
   never returns, or the process is killed mid-phase. Addressed in `02` (NFR-REL) and
   `06`.
6. **No storage/artifact lifecycle policy** — the plan directs all output to one NVMe
   path but never bounds its growth against the documented 72 GB free capacity.
   Addressed in `03` and `06`.
7. **No update/versioning policy for tool signatures** (`nuclei` templates, wordlists,
   CVE feeds) even though these decay in accuracy over time. Captured as a **non-goal
   for this phase** in `08` and a future risk in `07`.

None of these gaps require code or installation to resolve at this stage — they are
resolved here as requirements the eventual implementation must satisfy.

**Beyond these seven structural gaps**, a separate adversarial pass over the base
plan's technical claims — extended over several further rounds as new issues were
found, including from an external review, from a direct comparison against related
tooling, from an operator-supplied model-roster revision, and from a follow-up
"fetch everything useful" mining sweep — surfaced **31 findings
in total** (`11-Critical-Analysis-and-Design-Challenges.md`, C-01 through C-31):
memory/OOM interaction, prompt injection, CVSS scoring reliability, the Tier 2
tool-execution safety mechanism, the inference-engine choice, process-privilege
conflicts, an imprecisely-defined circuit-breaker metric, structured-output
reliability, redaction timing, a report-schema modeling gap, missing report grounding,
a missing failure-based circuit breaker, missing rate limiting, a memory-headroom
consequence of a later quantization change, and more. Every one has an explicit,
operator-confirmed resolution folded into `01`-`17` — **except C-29** (context-window
management over a long task-queue loop), which remains genuinely open: no verified
technique existed to adopt, and none was fabricated to fill the gap. The full
chronological record of every decision behind this entire document set — all 30
findings plus every other numeric/design fork raised along the way (55 decisions so
far) — is in `10-Decision-Log-and-Open-Questions.md`, along with the items that
genuinely cannot be closed without the real target hardware, without transferring
this document set to it, or without further follow-up work explicitly flagged as such
(see that document's "Open Questions Remaining" table, items A-H).

**On the base document itself:** `Agentic VAPT Setup (HOME).md` was originally
treated as an immutable historical record — every correction above was folded into
`01`-`09` only. By explicit, later operator decision, this expanded to direct
in-place correction: **18 of the 31 findings** (C-01, C-03, C-07, C-08, C-09, C-11,
C-12, C-13, C-14, C-15, C-16, C-17, C-18, C-19, C-20, C-21, C-25, C-30 — plus the
previously-unbounded task-queue loop) are now corrected directly in that file, each
marked inline with a pointer back to `11`. The remaining 13 findings' fixes live only
in `01`-`17` — **C-02, C-04, C-05, C-06, C-10** were never offered/selected for
base-file mirroring; **C-22, C-23, C-24, C-26, C-27, C-28, C-29, C-31** are purely
additive new mechanisms with no existing base-file claim to correct (the same
precedent that keeps the whole `FR-CTRL` operator control surface out of the base
file too).
**Standing policy (decision #42):** wherever the base file is corrected, it states
the correction at a high level only — no Python/SQL/flag-level specifics — while
`01`-`17` carry the precise mechanism. See decisions #39, #40, #42, #49, #50, and #51
for the full before/after record of every round of this work, including the two most
recent additions: `16-Actual-Setup-Reuse-and-Integration-Map.md` (what's reusable
from the `claude-bug-bounty` Claude-Code toolkit copied into `Actual-Setup/`) and
`17-Standalone-Engine-Reuse-and-Comparison.md` (comparison against that same repo's
standalone, non-Claude-Code engine — **includes a safety notice on real client data
that must never be copied into this project**).
