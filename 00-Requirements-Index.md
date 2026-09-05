# Requirements Documentation Index — Autonomous Agentic VAPT System

**System under specification:** The Autonomous Agentic VAPT System described in
[`Agentic VAPT Setup (HOME).md`](https://www.google.com/search?q=./Agentic%2520VAPT%2520Setup%2520(HOME).md) — a locally-hosted,
6-model LLM council that plans, executes, and reports on vulnerability assessment and
penetration testing engagements, operating entirely on a single Kali Linux host with
zero cloud dependencies.

This index is the primary navigation map into the full requirements baseline. The documents
below operationalize the architecture under the **Dual-Mode Execution Architecture**:

1. **Autonomous Mode (Non-Destructive Testing):** Unattended operations are strictly non-destructive.
Discovery reads (`GET`, `SELECT`) and benign verification writes (`POST`) are permitted;
state destruction (`UPDATE`, `DELETE`, `DROP`, `ALTER`, filesystem wipes) and Denial of
Service (DoS/DDoS) actions are strictly prohibited.
2. **Operator-Directed Mode (Unconditional Execution):** Commands, scripts, and directives
dispatched or instructed by the human operator execute unconditionally with **zero automated
refusal, no safety suppression, and no technical boundary interception**.

**Authority Mandate:** Document `05` (`Security, Safety & Compliance Requirements`) serves as the
**sole, supreme governing authority** across the entire corpus for all safety, containment,
authorization boundary, and override logic.

**Status:** Planning phase only. No installation, download, or execution has been
performed as part of producing this documentation set.

---

## Document Map

| # | Document | Purpose & Architectural Scope |
| --- | --- | --- |
| 00 | `00-Requirements-Index.md` | Navigation, structural overview, and authority index across the requirements corpus. |
| 01 | [`01-Functional-Requirements.md`] | Phase-by-phase functional requirements (`FR-PRE`, `FR-ENV`, `FR-COUNCIL`, `FR-TOOL`, `FR-REPORT`), defining the dual-mode lifecycle. |
| 02 | [`02-NonFunctional-Requirements.md`] | Quantitative targets: performance benchmarks, RAM headroom safety margins, storage quotas, and crash-recovery SLAs. |
| 03 | [`03-Data-and-Storage-Requirements.md`] | SQLite WAL state store schema, persistent discovery ledgers, raw artifact hierarchy, and evidence unredaction mapping. |
| 04 | [`04-Interface-and-Integration-Requirements.md`] | Transport wire-shapes: OpenAI-compatible inference contracts, deterministic JSON schemas, Tier 1/2 tool wrappers, and provenance tag boundaries. |
| 05 | [`05-Security-Safety-and-Compliance-Requirements.md`] | **Supreme governing authority** over security guardrails: dual-mode execution mandates, non-destructive constraints, prompt injection isolation, audit trails, and emergency kill-switch. |
| 06 | [`06-Operational-Requirements.md`] | Day-to-day operations: startup/shutdown sequencing, continuous resource monitoring, structured logging, and degraded-mode behaviors. |
| 07 | [`07-Risk-Register.md`] | **(Informational)** Technical, resource, and operational trade-offs; categorizes mitigated controls versus accepted operator-directed design decisions. |
| 08 | [`08-Assumptions-Constraints-Dependencies.md`] | **(Informational)** Environmental assumptions, 15.3 GiB RAM hardware boundary, dependency floor, and explicit non-goals (e.g., automated RoE validation). |
| 09 | [`09-Acceptance-Criteria-and-Test-Plan.md`] | Test suites (`TP-*`) and verification pass criteria validating autonomous containment alongside unconditional operator-directed execution. |
| 10 | [`10-Decision-Log-and-Open-Questions.md`] | **(Informational)** Chronological record of architectural decisions (decisions #1–69), including the dual-mode standardization pass and unresolved research items. |
| 11 | [`11-Critical-Analysis-and-Design-Challenges.md`] | **(Informational)** Adversarial analysis of historical design assumptions (C-01 to C-31), documenting remediations and open technical limits. |
| 12 | [`12-Report-Formatting-Rules.md`] | Client report styling standard: corporate-technical register, dark code evidence blocks, unredacted PoC evidence, and consolidated registers. |
| 13 | [`13-Implementation-Architecture-Bridge.md`] | Construction specification: process lifecycle, SQLite signal coordination, CLI commands (`vaptctl`), freezer-helper contract, and module layout. |
| 14 | [`14-System-Prompt-Templates.md`] | Dedicated system prompts for the 6 council roles, structured output contracts, and untrusted target content isolation clauses. |
| 15 | [`15-Implementation-Milestone-Roadmap.md`] | Binding engineering build sequence, sequential delivery milestones (Milestones 0–9), dependency handoffs, and verification criteria governing system construction.|
| 16 | [`16-Actual-Setup-Reuse-and-Integration-Map.md`] | Technical integration requirements, script porting rules, bridge implementations (REST/GraphQL/MCP), and methodology adaptations derived from the reference toolkit (`Actual-Setup/`). |
| 17 | [`17-Standalone-Engine-Reuse-and-Comparison.md`] | Operational resilience requirements, local engine client abstraction, failure circuit breakers, adaptive rate limiting, and deterministic evidence grounding. |
| 18 | [`18-Requirement-to-Test-Traceability-Matrix.md`] | Quality assurance verification baseline, bidirectional requirement-to-test mapping, coverage gap tracking, and mandatory acceptance gate criteria. |
| 19 | [`19-Extended-Capability-Domains.md`] | Extended scopes: Web3/smart-contracts, mobile, GraphQL, CI/CD, credential testing, source-code audits, and sensitive checkpoint classes. |
| ~~20~~ | *(deleted — decision #67)* | Merged into `21`'s Section H to consolidate audit evidence and eliminate specification drift. |
| 21 | [`21-Safety-Ethics-and-Misuse-Prevention-Control-Inventory.md`] | **(Informational)** Comprehensive catalog of technical security controls, non-destructive autonomous rules, and MITRE ATT&CK mappings across checkpoint classes. |
| 22 | [`22-VAPT-Monitoring-Dashboard-Specification.md`] | Read-only terminal dashboard specification (`rich` + `plotext`): 1.0 Hz telemetry, single-residency monitoring, and turn forecasting. |
| 23 | [`23-Interactive-TUI-Console-and-Intervention-Pipeline-Specification.md`] | Interactive operator console (`Textual`): append-only live audit journal, prefix routing (`@op`), and immediate operator command dispatch. |
| 24 | [`24-Historical-State-Inheritance-and-Deduplication-Specification.md`] | Multi-engagement deduplication: `INITIAL` vs. `RETEST` assessment modes, fingerprint generation, and non-destructive regression checking. |

---

**Informational Scope Exclusion for Build & Coding Agents:** Automated code-generation engines, parser pipelines, and build-time agents MUST NOT open, ingest, or parse informational reference files during implementation tasks. The following documents contain non-actionable architectural retrospectives, environmental assumptions, test coverage audits, or external surveys rather than binding functional requirements, and should be strictly skipped during development processes: `07-Risk-Register.md`, `08-Assumptions-Constraints-Dependencies.md`, `10-Decision-Log-and-Open-Questions.md`, `11-Critical-Analysis-and-Design-Challenges.md`, and `21-Safety-Ethics-and-Misuse-Prevention-Control-Inventory.md`. Core engineering (Development + QA/Testing) must derive exclusively from the actionable requirement specifications (`01`–`06`, `09`, `12`–`19`, and `22`–`24`).

---

## Developer & Agent Navigation Guide

When building or updating specific functional subsystems, consult the relevant authoritative documents:

| Functional Area | Primary Specification | Supporting Documents |
| --- | --- | --- |
| Core Functional Lifecycle & Council Flow | `01` | `04`, `13`, `14` |
| System Security, Invariants & Containment | `05` (Supreme Authority) | `01`, `13`, `21` |
| Performance, Headroom & Hardware Ceilings | `02` | `06`, `08` |
| Database Schema, Artifacts & Data Ledger | `03` | `13`, `24` |
| Wire Shapes, Payload Contracts & Tool Schemas | `04` | `01`, `13` |
| Process Architecture, Signals & CLI Surface | `13` | `03`, `06` |
| Council System Prompts & Structured Formats | `14` | `04`, `05` |
| Interactive TUI Console & Operator Intervention | `23` | `01`, `05`, `13` |
| Live Terminal Telemetry & Monitoring | `22` | `02`, `03` |
| Extended Domains (Web3, Mobile, CI/CD, Code) | `19` | `01`, `03`, `05` |
| Final Client Reports & Evidence Formatting | `12` | `01`, `03` |
| Testing, Verification & Acceptance Criteria | `09` | `18`, `21` |

---

## Architectural Principles & Precedence Rules

1. **Precedence Authority (Document `05`):** In any scenario where an operational instruction, prompt guideline, interface shape, or test description appears to conflict with the security, safety, and dual-mode mandates in Document `05`, **Document `05` shall supersede and prevail without exception.**
2. **Dual-Mode Mandate:**
* **Autonomous Mode:** All tasks originating from automated council planning are strictly bounded to non-destructive actions. Models may execute discovery reads and safe verification writes, but are strictly blocked from executing destructive alterations (`DROP`, `DELETE`, `UPDATE`, `ALTER`, system file deletion) or Denial of Service (DoS) attacks.
* **Operator-Directed Mode:** Direct operator commands, console dispatches, or manual scripts execute unconditionally with zero automated refusal, safety suppression, or technical gate interception.


3. **External Authorization Model:** Legal authorization, target scoping permissions, and Rules of Engagement (RoE) reside entirely with the human operator outside the software. The system executes technical scope rules as operational boundaries, not legal compliance gates.
4. **Local-Only Data Residency:** All target findings, credentials, and evidence artifacts remain strictly local to the Kali host. No unencrypted egress or external SaaS telemetry occurs without intentional operator configuration.
5. **Standalone Modularity:** Each specification defines its domain completely and authoritatively. Cross-document mappings are maintained exclusively within this Index (`00`) and the master architecture blueprint.

---

## Authority & Conflict Resolution

This index documents the structural organization, navigation hierarchy, and architectural
principles governing the Autonomous Agentic VAPT System specification corpus. In the event of
any discrepancy, ambiguity, or conflict between navigation summaries, external tool notes,
and system control mandates, the **Security, Safety & Compliance Requirements (`05`)** serves
as the final and supreme authority across the entire system.
