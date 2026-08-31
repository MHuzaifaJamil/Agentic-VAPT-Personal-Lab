# Requirements Documentation Index — Autonomous Agentic VAPT System

**System under specification:** The Autonomous Agentic VAPT System described in
[`Agentic VAPT Setup (HOME).md`](./Agentic%20VAPT%20Setup%20(HOME).md) — a locally-hosted,
5-model LLM council that plans, executes, and reports on vulnerability assessment /
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
2. **No human-in-the-loop control surface** — the 5-phase blueprint runs end-to-end
   with only two internal LLM gates (Hermes-3, Mistral-7B); there is no operator
   pause/resume/abort control, no approval checkpoint before destructive actions, and
   no kill-switch. Addressed in `04` and `05`.
3. **No Phase 0 (pre-flight self-test)** — the blueprint assumes the inference engine,
   GPU drivers, and Kali tool suite are already verified working. Addressed as FR-PRE
   in `01`.
4. **No defined report deliverable format, evidence redaction policy, or CVSS/CWE
   mapping detail.** Addressed in `01` (FR-REPORT) and `05` (evidence handling).
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
