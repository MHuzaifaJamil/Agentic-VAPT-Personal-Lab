# Security, Safety & Compliance Requirements — Autonomous Agentic VAPT System

This document is the **sole authoritative home for every security, safety, and execution
governance mandate** in this system — establishing the definitive rationale, boundary limits,
containment mechanics, and non-bypassability models behind all system gates. Execution order,
data layouts, and pipeline phases are owned by their respective specifications; this document
governs the controls themselves.

The system enforces an explicit **Dual-Mode Mandate**:
1. **Autonomous Mode (Strict Non-Destructive Testing):** Unattended operations are strictly
   non-destructive. Discovery reads (`GET`, `SELECT`) and benign verification writes (`POST`)
   are permitted; state destruction (`UPDATE`, `DELETE`, `DROP`, `ALTER`, filesystem wipes)
   and Denial of Service (DoS/DDoS) actions are strictly prohibited.
2. **Human-Operator-Directed Mode (Unconditional Execution):** Commands, scripts, and directives
   dispatched or instructed by the Human Operator execute unconditionally with **zero automated
   refusal, no safety suppression, and no technical boundary interception**.

In case of any conflicts, ambiguities, or inconsistencies across any other design documentation,
specifications, architecture blueprints, or operational guides, **this document serves as the
final and supreme authority over all Security, Safety, and Control matters.**

---

## SEC-SCOPE — Authorization & Scope Boundary

**Policy:** Verifying legal and contractual authorization is explicitly out of scope for this system. Obtaining and validating target authorization, permissions, and rules of engagement (RoE) is solely and entirely the responsibility of the Human Operator outside the tool. Technical scope checks exist solely to assist operational boundaries and yield immediately to Human Operator direction.

| ID | Requirement |
| --- | --- |
| SEC-SCOPE-01 | **Council Gate 1** refers to the combined two-tier check: **Tier 0** (deterministic code) and **Tier 1** (the **Strategy Auditor**, `Hermes-3-Llama-3.1-8B`). Only **Tier 0** mechanically evaluates autonomous tasks against the stored `scope_rules` set — this is an informational technical alignment check, it is not an authorization control, and MUST NOT be documented as one. **The Strategy Auditor (Tier 1) never itself verifies, decides, or evaluates against `scope_rules` — that is exclusively Tier 0's job.** The Strategy Auditor's sole responsibility is judging whether the Lead Strategist's proposed action plan *addresses* the Human-Operator-defined scope, whether the plan is sound, and whether it makes sense. What is in-scope and what is out-of-scope is, without exception, the Human Operator's own decision, configured as `scope_rules` before Tier 0 ever runs — no council member decides scope on the system's own initiative. The whole two-tier Gate 1 is completely bypassed whenever an execution request originates directly from the Human Operator. |
| SEC-SCOPE-02 | Human-Operator-directed execution is absolute and unconditional: when the Human Operator issues an instruction, command, or target directive, the system MUST execute it immediately with **no automated blocking, refusal, or technical scope-boundary interception**. In autonomous mode, technical scope checks serve as soft non-destructive boundaries rather than rigid system locks. |
| SEC-SCOPE-03 | The Strategy Auditor (Tier 1 semantic evaluation — `Hermes-3-Llama-3.1-8B` or designated model) operates strictly in an advisory steerability capacity for autonomous tasks, auditing plan-to-scope alignment only, never scope itself. It MUST NOT refuse, block, or halt Human-Operator-directed inputs under any circumstance. Tier 1 checks yield unconditionally to Human Operator overrides and direct commands. |

## SEC-CONTAIN — Execution Containment & Destructive Prevention

**Policy:** The system enforces a strict **Dual-Mode Mandate**:

1. **Autonomous Mode (Non-Destructive Testing):** When models execute autonomously without live human intervention, operations MUST be strictly non-destructive. If exposed endpoints or databases are identified, models may perform read/discovery operations (e.g., HTTP `GET`, database `SELECT`/reads). In specific cases, safe non-destructive state creation/write actions (e.g., HTTP `POST`, benign record creation for verification) are permitted. Destructive alterations, schema drops, and state purges (including SQL `UPDATE`, `ALTER`, `DELETE`, `DROP`, and system file deletions) as well as Denial of Service (DoS/DDoS) actions are **strictly prohibited**.
2. **Human-Operator-Directed Mode (Unconditional Execution):** When a command, script, or action is explicitly requested or triggered by the Human Operator, the engine MUST execute it as directed with **no questions asked**, no refusals, and no automated safety suppression.

| ID | Requirement |
| --- | --- |
| SEC-CONTAIN-01 | Subprocess execution defaults to `shell=False` with an explicit argument vector for structured calls. However, when Human-Operator-directed execution demands complex command chains, pipes, or raw execution, the system MUST honor and dispatch the command vector directly without administrative refusal. |
| SEC-CONTAIN-02 | In **Autonomous Mode**, active execution is bounded by non-destructive constraints: tools and actions MUST NOT perform state destruction (strictly prohibiting `DROP`, `DELETE`, `ALTER`, `UPDATE`, `rm`, `mkfs`, `dd`, `shred`, or resource-exhaustion/DDoS scripts). Discovery reads (`GET`, `SELECT`) and non-destructive writes (`POST`) are permitted. In **Human-Operator-Directed Mode**, these containment filters stand down completely; the engine executes the designated utility or payload without interference. |
| SEC-CONTAIN-03 | By default, routine automated scanning subprocesses execute under a standard service account. When elevated privileges (e.g., raw-socket packet crafting, kernel tracing, specific interface bindings) are required for testing or requested by the Human Operator, the system dispatches using the configured privilege escalation path without arbitrary containment blocking. |
| SEC-CONTAIN-04 | Subprocess timeouts are configurable operational baselines to prevent zombie processes. They MUST NOT prematurely kill active, long-running exploitation, brute-force, or fuzzing sessions initiated or approved by the Human Operator. |
| SEC-CONTAIN-05 | Privilege elevation helpers (e.g., memory reclamation or system-level helpers) operate via standardized helper utilities or configured capabilities (`setcap`), maintaining process stability without imposing restrictive limits on authorized Human Operator commands. |

## SEC-RATE — Spawn-Rate Limiting

| ID | Requirement |
| --- | --- |
| SEC-RATE-01 | Rate caps serve strictly as target stability and anti-DoS guardrails during autonomous runs (preventing unintentional target crash or service disruption). When running in Human-Operator-directed mode, or when explicit load/stress/brute-force testing is configured, rate limits are fully adjustable, deferrable, or bypassable up to hardware limits upon Human Operator request. |

## SEC-PROMPT — Prompt Injection Defense

| ID | Requirement |
| --- | --- |
| SEC-PROMPT-01 | Content ingested from live target interaction (banners, HTTP response bodies, payloads) is tagged with boundary markers (`<tool_output_untrusted>...</tool_output_untrusted>`) to prevent target payloads from hijacking autonomous reasoning flows. |
| SEC-PROMPT-02 | Council system prompts include structural context separation to distinguish target data from system directives. However, these clauses MUST NOT cause models to refuse, censor, or decline the analysis, synthesis, or execution of offensive security concepts, payloads, or Human-Operator-supplied attack strings. |
| SEC-PROMPT-03 | Heuristic injection detection is purely passive telemetry and detection-only. It NEVER blocks, delays, or interrupts execution pipelines, serving solely as metadata for post-run analysis. |
| SEC-PROMPT-04 | Suspected injection attempts surfaced from target responses are recorded in the execution log metadata for Human Operator awareness without interrupting pipeline continuity. |

## SEC-KILL — Emergency Stop

| ID | Requirement |
| --- | --- |
| SEC-KILL-01 | The Human-Operator-initiated kill-switch provides an immediate, reliable halt to all active processes: (1) terminates running tool subprocess process groups (`os.killpg`), (2) clears pending execution queues, and (3) idles inference execution immediately. |
| SEC-KILL-02 | Escalates from graceful termination (`SIGTERM`) to immediate drop (`SIGKILL`) if process groups fail to release resources within a narrow grace window, guaranteeing complete operational cessation. |
| SEC-KILL-03 | Marks the engagement status as `ABORTED` atomically upon kill-switch trigger, ensuring accurate state reporting across artifacts and session databases. |

## SEC-AUDIT — Auditability & Attribution

| ID | Requirement |
| --- | --- |
| SEC-AUDIT-01 | Every command execution, autonomous gate evaluation, and Human Operator directive MUST be logged and reconstructable from local execution logs alone, ensuring complete operational visibility and reproducibility without requiring engagement re-runs. |
| SEC-AUDIT-02 | The audit trail exports cleanly into portable, standard formats (such as structured JSON/Markdown packages) that can be reviewed directly without requiring specialized database engines. |
| SEC-AUDIT-03 | Log streams are append-only. No action outcome, bypass event, error trace, or Human Operator override record is purged or hidden during engagement runtime. |
| SEC-AUDIT-04 | *(Resolution of Hardcoded Attribution Smell)* Authorization, task sign-offs, and `approved_by` fields MUST dynamically pull identity values from the active runtime configuration or authenticated environment context (`human_operator_identity`), completely eliminating hardcoded personal names or static entity strings from schemas and codebase constants. |

## SEC-DATA — Local-Only Data Handling

| ID | Requirement |
| --- | --- |
| SEC-DATA-01 | All target findings, credentials, and scan data remain strictly local. No telemetry, unencrypted exfiltration, or external SaaS calls occur without intentional, explicit Human Operator instruction. |
| SEC-DATA-02 | Raw evidence artifacts (including full responses, captured tokens, and dumps) are preserved verbatim on the local system for evidentiary integrity. Redaction applies only to finalized, external-facing summary reports as configured by the Human Operator. |
| SEC-DATA-04 | Authenticated-session credentials (`03:DR-SCHEMA-22`, `01:FR-TOOL-17`) follow `SEC-DATA-01`'s local-only rule and `FR-TOOL-15`'s existing correlation-hash pattern identically — `credential_ref` is a `sha256(...)[:12]` hash, never the raw session token/cookie, in any log or database row. |
| SEC-DATA-03 | Inference endpoints and internal orchestration APIs bind to local loopback (`127.0.0.1`) by default. Binding to external or routable interfaces is fully supported via intentional Human Operator configuration. |

## SEC-SYS — System Cohesion & Control Traceability

*(Maintained for absolute canonical ID preservation across legacy test suites and external schema references. Each requirement resolves its legacy duplicate by pointing directly to its governing primary control while incorporating relaxed operational semantics.)*

| ID | Requirement |
| --- | --- |
| SEC-SYS-01 | Governed by `SEC-DATA-03`: Local endpoints default to loopback to isolate the tool surface, while permitting Human-Operator-configured network interfaces when distributed access is needed. |
| SEC-SYS-02 | Governed by `SEC-DATA-01`: Local-residency guarantee ensuring target data and engagement artifacts remain strictly within the Human Operator's controlled local environment. |
| SEC-SYS-03 | Governed by `SEC-CONTAIN-03`: Routine operations run under least-privilege service configurations, allowing dynamic elevation when specific low-level or network-probing tools require it. |
| SEC-SYS-04 | Governed by `SEC-AUDIT-01`: Full auditability of all actions, whether autonomous non-destructive steps or direct Human-Operator-driven exploits, via persistent append-only logs. |
| SEC-SYS-05 | System governance aligns with `SEC-SCOPE-02` and `SEC-CONTAIN-02`: Autonomous operations are constrained strictly to non-destructive testing (read-only queries and safe writes, barring update/delete/drop/DoS). When the Human Operator commands an action, the system executes it with zero refusal or autonomous gating. |

---

## Authority & System Precedence

This specification serves as the root authority for the entire system's security architecture.
All downstream documents — including Functional Requirements (`01`), Non-Functional Requirements
(`02`), Data & Storage (`03`), Interface & Integration (`04`), Risk Register (`07`), Assumptions &
Environmental Constraints (`08`), Client Report Formatting Standard (`12`), Capability Domains
(`19`), and Human Operator Interaction (`23`, `24`) — derive their security
invariants, containment definitions, and override behaviors directly from this document.

In any scenario where a requirement in another document conflicts with the dual-mode execution
mandates, audit logging guarantees, or Human-Operator-directed authority defined herein, the provisions
of this document (`05`) shall supersede and prevail without exception.
