# Security, Safety & Compliance Requirements — Autonomous Agentic VAPT System

This document consolidates the security-relevant requirements that are scattered
across `01`/`02` by cross-reference, and adds the policy-level statements (what is and
is not in scope for this system to enforce) that a reader shouldn't have to infer.

---

## SEC-SCOPE — Authorization & Scope Boundary

**Decision on record:** verifying that testing is legally/contractually authorized is
**explicitly out of scope** for this system. The system does not gate execution on any
authorization/Rules-of-Engagement artifact. Obtaining and confirming authorization to
test a given target is the operator's responsibility, entirely outside this tool.

| ID | Requirement |
|----|-------------|
| SEC-SCOPE-01 | The only scope check this system performs is a **technical** one: Council Gate 1 — a mandatory deterministic Python pre-check (`FR-COUNCIL-03a`) followed by `Llama-3.1-8B-Instruct` as the semantic layer (replacing Hermes-3, per the C-03 resolution) — evaluating a proposed task against the `scope_rules` allow/deny patterns (DR-SCHEMA-03) recorded for the engagement. This is inherited directly from the base plan's own design (§Phase 4.1) — it is not a new authorization control, and it MUST NOT be described or documented anywhere as one. |
| SEC-SCOPE-02 | This technical scope check MUST be non-overridable under any configuration (FR-COUNCIL-06) — a task Gate 1 rejects never reaches execution, full stop. The generic "autonomy level" concept has been removed by confirmed decision in favor of the specific opt-in flags (FR-TOOL-06a) and fixed thresholds (FR-COUNCIL-11); none of those flags can weaken this scope check either. |
| SEC-SCOPE-03 | Gate 1's semantic (LLM) tier now uses `Llama-3.1-8B-Instruct`, chosen specifically to restore conservative refusal behavior instead of the base plan's uncensored/steerable `Hermes-3` choice (critical-analysis finding C-03, resolved) — but its actual refusal behavior has not been empirically tested (open item, `10-Decision-Log...md`). Because the input it evaluates can itself contain adversarial content surfaced from prior scanning (finding C-04), Gate 1's scope-check reliability is also bounded by IR-SANITIZE-02/03 (provenance tagging) actually being implemented correctly, and by the deterministic pre-check tier (`FR-COUNCIL-03a`) catching what the LLM tier might miss. This dependency chain MUST be documented wherever Gate 1 is described, not left implicit. |

## SEC-CONTAIN — Execution Containment

| ID | Requirement |
|----|-------------|
| SEC-CONTAIN-01 | Every subprocess spawned by either tool tier MUST use non-shell execution with an explicit argument vector (FR-TOOL-04, IR-BRIDGE-01) — no model output is ever passed through a shell interpreter. |
| SEC-CONTAIN-02 | Tier 2 execution is bounded by the path-restricted allowlist + behavioral denylist confirmed in FR-TOOL-03/06 and IR-BRIDGE-02/03. Per critical-analysis finding C-14, this is a **residual-risk-accepted** design: it does not itself prevent an allowed binary from being used destructively or out-of-scope — that containment relies on SEC-SCOPE-01/02 (Gate 1) and the Gate 2 linter having already approved the specific command. This dependency chain (Gate 1 → Gate 2 → Tier 2 path/pattern check) MUST be treated as the actual defense-in-depth stack in any future security review, not the Tier 2 check in isolation. |
| SEC-CONTAIN-03 | Every subprocess MUST run under a dedicated, least-privileged OS account for the agent (NFR-SEC-03), distinct from the operator's interactive login, with `sudo`/elevated-privilege invocation limited to the specific, individually documented tools that require it (e.g., raw-socket scanning modes of `nmap`) — a blanket root agent process MUST NOT be used. |
| SEC-CONTAIN-04 | Every subprocess MUST carry a mandatory timeout (FR-TOOL-05, IR-TOOL-03) sized per tool class, so a hung process cannot indefinitely hold system resources or silently extend the 12-hour session budget's effective wall-clock usage. |
| SEC-CONTAIN-05 | **(New, confirmed — resolves critical-analysis finding C-15)** The one operation that genuinely needs elevated privilege — `process_madvise(MADV_PAGEOUT)` for hibernation memory reclamation (FR-ENV-07) — MUST NOT be granted to the main agent process. It MUST be isolated in a narrow, single-purpose helper (`vapt-freezer-helper`) granted only `CAP_SYS_PTRACE` via `setcap`, or invoked through an equivalently narrow `sudoers`/polkit rule (FR-ENV-13) — this is the sole exception to SEC-CONTAIN-03's least-privilege rule, and it is scoped to one syscall in one helper binary, not a blanket privilege grant. |

## SEC-PROMPT — Prompt Injection Defense (MUST, per operator decision on finding C-04)

| ID | Requirement |
|----|-------------|
| SEC-PROMPT-01 | All content sourced from live target interaction MUST pass through the provenance-tagging pipeline (IR-SANITIZE-02) before reaching any model's context — no exceptions for "trusted-looking" tool output, since the threat is the target's own responses, not the tool. |
| SEC-PROMPT-02 | Every council model's system prompt MUST carry the fixed instruction-hierarchy clause (IR-SANITIZE-03) establishing that tagged content is data, not instructions, and that this cannot be overridden by anything inside the tags. |
| SEC-PROMPT-03 | The heuristic injection-pattern detector (FR-TOOL-13) is a SHOULD-level detection aid, not a containment control — its absence or a false negative MUST NOT be treated as reducing the MUST-level requirements in SEC-PROMPT-01/02. |
| SEC-PROMPT-04 | Any suspected-injection flag raised by FR-TOOL-13 against a task that a gate subsequently approved MUST be surfaced in the audit trail (FR-CTRL-07 export) prominently enough that a human reviewer would find it without searching — e.g., a distinct log level or a dedicated section in the export package, not buried in raw JSON. |

## SEC-KILL — Emergency Stop

| ID | Requirement |
|----|-------------|
| SEC-KILL-01 | The abort/kill-switch (FR-CTRL-04) MUST terminate, in order: (1) the currently executing tool subprocess tree, (2) any queued-but-not-yet-started subprocess, (3) the resident inference engine process, all within the 20-second budget (NFR-REL-04). |
| SEC-KILL-02 | Kill-switch termination MUST escalate from a graceful signal (`SIGTERM`) to a forceful one (`SIGKILL`) if a process does not exit within a bounded grace period inside that 20-second budget, rather than wait indefinitely on a graceful shutdown that may not happen. |
| SEC-KILL-03 | Invoking the kill-switch MUST mark the engagement `ABORTED` in `engagements.status` (DR-SCHEMA-01) as an atomic part of the abort sequence, not a separate manual step — an aborted engagement must never be left in `IN_PROGRESS`. |

## SEC-AUDIT — Auditability

| ID | Requirement |
|----|-------------|
| SEC-AUDIT-01 | Every subprocess invocation (allowed or rejected), every model invocation, and every gate decision MUST be reconstructable after the fact from `tool_execution_logs`, `model_invocation_logs`, and the gate-rationale columns alone (NFR-SEC-04) — auditing an engagement MUST NOT require re-running it. |
| SEC-AUDIT-02 | The audit trail MUST be exportable as a single package (FR-CTRL-07) that a human reviewer (the operator, or a third party they choose to show it to) can read without needing SQLite tooling — at minimum, a flattened chronological log view alongside the raw database. |
| SEC-AUDIT-03 | Log records MUST NOT be mutated or deleted by any normal operation of the system (append-only in practice, even if not cryptographically enforced) — a `DISMISSED` finding or a `GATE1_REJECTED` task stays in the record, it is never removed. |

## SEC-DATA — Local-Only Data Handling

| ID | Requirement |
|----|-------------|
| SEC-DATA-01 | No target data, credentials, or findings MUST ever leave the local host via a network call — the local-only model residency (NFR-SEC-02) applies to the whole pipeline, not just inference: no telemetry, no cloud logging, no "phone home" of any kind. |
| SEC-DATA-02 | Captured secrets follow the redaction/unredaction lifecycle in FR-COUNCIL-18/FR-CTRL-08: redacted by default in the pending-approval draft, restored to full verbatim form only in the operator-approved report, and never redacted in the raw evidence artifact itself at any point (the raw artifact is the ground truth the redaction mapping depends on). |
| SEC-DATA-03 | The local `/v1` inference endpoint MUST remain loopback-bound by default (NFR-SEC-01); binding it to a routable interface (e.g., to let a second machine on the LAN drive it) MUST require an explicit, separately-documented configuration change — never a default. |
