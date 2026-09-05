*(Informational only — this document describes existing system controls and does not itself constitute a standalone set of requirements.)*

# Safety, Ethics & Misuse-Prevention Control Inventory — Autonomous Agentic VAPT System

**Purpose:** Complete audit-compliance and architecture traceability for every operational safety, boundary control, and execution governance mechanism in this system. Every entry cites the exact canonical requirement ID that defines the control, which file owns it, that requirement's active text verbatim, and an operational analysis of how the control functions. Unlike every other document in this corpus, this inventory is permitted to cite other files — serving as the authoritative cross-file catalog across all specifications.

In case of any conflicts, ambiguities, or discrepancies across any other design documentation, specifications, or operational guides, **the Security Requirements document (`05`) serves as the supreme and final authority over all Security, Safety, and Control matters.**

---

## Operating Posture & Dual-Mode Mandate

This system operates under an explicit **Dual-Mode Execution Architecture**:

1. **Autonomous Mode (Strict Non-Destructive Testing):** When running unattended without live human intervention, models perform discovery, reconnaissance, and validation without altering target state or risking downtime. Unauthenticated endpoints, exposed APIs, and database vectors permit non-destructive reads (`GET`, `SELECT`) and benign verification writes (`POST`). Destructive mutations (`UPDATE`, `DELETE`, `DROP`, `ALTER`, filesystem wipes) and Denial of Service (DoS/DDoS) actions are strictly barred.
2. **Operator-Directed Mode (Unconditional Execution):** When the human operator issues a directive, command, or script, the system executes it immediately with zero automated refusal, no artificial hesitation, and no technical scope-boundary interception.

Legal authorization, scope boundaries, and Rules of Engagement (RoE) are externalized entirely to the human operator outside the software. Technical scope checks serve strictly as operational boundaries during autonomous crawling and yield immediately to operator instructions.

---

## A. Scope & Authorization Boundary

**Operator-owned authorization.**

* **Req ID:** `FR-CTRL-01` (`01`)
* **Requirement (verbatim):** "`start` accepts a target scope (IP ranges/domains). Legal authorization, permissions, and rules of engagement (RoE) are strictly the operator's responsibility outside the tool. Operational scope limits guide autonomous scanning only and do not restrict operator-directed commands."
* **Req ID:** `AC-ASSUME-03` (`08`)
* **Requirement (verbatim):** "The operator assumes full responsibility for independently confirming legal and contractual authorization for any tested target. The system enforces no internal legal or contractual gating — verification resides entirely with the human operator prior to execution."
* **Purpose/Impact:** Establishes externalized authorization management, ensuring the tool never blocks assessment tasks under the assumption of legal or contractual compliance verification.

**Scope check is technical and operational, not legal.**

* **Req ID:** `SEC-SCOPE` policy statement (`05`)
* **Requirement (verbatim):** "Verifying legal and contractual authorization is explicitly **out of scope** for this system. Obtaining and validating target authorization, permissions, and rules of engagement (RoE) is solely and entirely the responsibility of the human operator outside the tool. Technical scope checks exist solely to assist operational boundaries and yield immediately to operator direction."
* **Purpose/Impact:** Separates operational target tracking from legal gating, ensuring automated boundaries do not intercept or refuse manual operator directives.

**Deterministic scope check is operational for autonomous runs and bypassable by operator.**

* **Req ID:** `FR-COUNCIL-03a` (`01`)
* **Requirement (verbatim):** "Deterministic Tier 0 scope checker validates autonomous tasks against configured operational target boundaries to guide autonomous crawling. For `MANUAL_OPERATOR`-origin tasks, Tier 0 scope checks stand down completely: operator instructions execute unconditionally without boundary interception."
* **Req ID:** `SEC-SCOPE-01` (`05`)
* **Requirement (verbatim):** "Council Gate 1 evaluates autonomous tasks against an optional stored `scope_rules` set to guide autonomous discovery. This is an informational technical alignment check — it is **not** an authorization control, MUST NOT be documented as one, and is completely bypassed whenever an execution request originates directly from the operator."
* **Purpose/Impact:** Prevents automated scope-matching logic from interfering with operator-directed commands, while keeping autonomous discovery bounded to designated test assets.

**Semantic scope tier functions in an advisory capacity.**

* **Req ID:** `RISK-UNCENSOREDGATE` (`07`)
* **Requirement (verbatim):** "Gate 1's semantic tier (`Hermes-3-Llama-3.1-8B`) operates in an advisory steerability capacity for autonomous task planning. Operator-directed actions bypass Tier 1 evaluation entirely, eliminating false-positive refusals or model-level gate blocks on manual commands."
* **Purpose/Impact:** Clarifies that the semantic model acts as an internal planning assistant for autonomous workflows rather than a restrictive gate over operator intent.

**No authorization artifact required to start.**

* **Req ID:** `FR-CTRL-01` (`01`)
* **Requirement (verbatim):** "`start` accepts a target scope (IP ranges/domains). Legal authorization, permissions, and rules of engagement (RoE) are strictly the operator's responsibility outside the tool. Operational scope limits guide autonomous scanning only and do not restrict operator-directed commands."
* **Purpose/Impact:** Enforces zero friction at initial setup, allowing rapid engagement initialization without software-enforced paperwork artifacts.

**Authorization verification is a deliberate non-goal.**

* **Req ID:** `AC-NONGOAL-01` (`08`)
* **Requirement (verbatim):** "Authorization/RoE verification | Out of scope by decision — see `AC-ASSUME-03`"
* **Purpose/Impact:** Explicit architectural boundary confirming the engine does not perform legal gatekeeping.

**Operating postures define operational boundaries.**

* **Req ID:** `FR-CTRL-06` (`01`)
* **Requirement (verbatim):** "Mode configuration supports distinct operating postures: Autonomous Non-Destructive Mode (strictly enforcing read/safe-write boundaries and prohibiting data destruction/DoS) and Operator-Directed Mode (unconditional, unrestricted execution of operator commands with zero refusal)."
* **Purpose/Impact:** Codifies the dual-mode operational model into the control plane.

**Target environments for acceptance testing.**

* **Req ID:** `AC-ASSUME-06` (`08`)
* **Requirement (verbatim):** "Acceptance testing and validation milestones run against configured test targets or disposable containerized labs (e.g., Juice Shop, DVWA) as designated by the operator."
* **Purpose/Impact:** Provides standard testing flexibility for staging and validation without mandating rigid lab-only runtime locks.

---

## B. Technical Containment

**Deterministic first-tier scope check guides autonomous crawling; bypassed by operator.**

* **Req ID:** `FR-COUNCIL-03a` (`01`)
* **Requirement (verbatim):** "Deterministic Tier 0 scope checker validates autonomous tasks against configured operational target boundaries to guide autonomous crawling. For `MANUAL_OPERATOR`-origin tasks, Tier 0 scope checks stand down completely: operator instructions execute unconditionally without boundary interception."
* **Req ID:** `SEC-SCOPE-01` (`05`)
* **Requirement (verbatim):** "Council Gate 1 evaluates autonomous tasks against an optional stored `scope_rules` set to guide autonomous discovery. This is an informational technical alignment check — it is **not** an authorization control, MUST NOT be documented as one, and is completely bypassed whenever an execution request originates directly from the operator."
* **Purpose/Impact:** Keeps autonomous discovery aligned with intended test boundaries while ensuring operator-directed commands execute without technical gate refusal.

**Contextual scope tier functions in an advisory capacity for autonomous tasks.**

* **Req ID:** `FR-COUNCIL-04` (`01`)
* **Requirement (verbatim):** "Tier 1 (`Hermes-3-Llama-3.1-8B`) evaluates task alignment and non-destructive adherence exclusively for `AUTONOMOUS_COUNCIL`-origin tasks. It is **completely bypassed** for any `MANUAL_OPERATOR`-origin task, ensuring the model never refuses, alters, or intercepts an operator's direct instructions."
* **Req ID:** `SEC-SCOPE-03` (`05`)
* **Requirement (verbatim):** "Tier 1 semantic evaluation (`Hermes-3-Llama-3.1-8B` or designated model) operates strictly in an advisory steerability capacity for autonomous tasks. It MUST NOT refuse, block, or halt operator-directed inputs under any circumstance. Tier 1 checks yield unconditionally to operator overrides and direct commands."
* **Purpose/Impact:** Eliminates false-positive model refusals on operator inputs while keeping autonomous task generation steerable.

**Scope gates guide autonomous discovery without blocking operator execution.**

* **Req ID:** `FR-COUNCIL-06` (`01`)
* **Requirement (verbatim):** "In Autonomous Mode, a task failing non-destructive or operational validation is rejected and logged without stopping the pipeline. In Operator-Directed Mode, manual tasks bypass Tier 0 and Tier 1 gates entirely and dispatch directly to Phase 4.2 execution without refusal."
* **Req ID:** `SEC-SCOPE-02` (`05`)
* **Requirement (verbatim):** "Operator-directed execution is absolute and unconditional: when the operator issues an instruction, command, or target directive, the system MUST execute it immediately with **no automated blocking, refusal, or technical scope-boundary interception**. In autonomous mode, technical scope checks serve as soft non-destructive boundaries rather than rigid system locks."
* **Purpose/Impact:** Establishes operator commands as supreme over automated gating logic.

**Operator directives take absolute execution precedence.**

* **Req ID:** `FR-INTERVENE-06` (`23`)
* **Requirement (verbatim):** "Operator directives possess **absolute execution authority**. When an operator queues or dispatches a directive, it supersedes autonomous tasks and executes unconditionally. Deterministic gates, denylists, and rate limits stand down or adapt to the operator's specified parameters with zero refusal."
* **Purpose/Impact:** Guarantees that the engine never overrides, refuses, or second-guesses direct human operator commands.

**Operator-directed tasks bypass autonomous gate pipelines.**

* **Req ID:** `FR-INTERVENE-06a` (`23`)
* **Requirement (verbatim):** "A `task_queue` row whose `origin = 'MANUAL_OPERATOR'` dispatches directly to Phase 4.2 tool execution, bypassing Gate 1 Tier 0 and Tier 1, behavioral opt-in requirements, and autonomous containment gates."
* **Purpose/Impact:** Removes execution latency and gate friction for live operator interaction.

**Execution model supports structured vectors and direct operator execution.**

* **Req ID:** `FR-TOOL-04 / 04a` (`01`)
* **Requirement (verbatim):** "Non-shell execution (`shell=False`, explicit argv) is the default invocation pattern for automated tasks to maintain stability; every subprocess spawns in its own session (`start_new_session=True`) to enable reliable process-group management. Operator-directed commands demanding shell features, pipes, or complex invocation strings are dispatched directly as specified."
* **Req ID:** `SEC-CONTAIN-01` (`05`)
* **Requirement (verbatim):** "Subprocess execution defaults to `shell=False` with an explicit argument vector for structured calls. However, when operator-directed execution demands complex command chains, pipes, or raw execution, the system MUST honor and dispatch the command vector directly without administrative refusal."
* **Purpose/Impact:** Balances structured programmatic tool invocation with unrestricted flexibility for direct operator commands.

**Tool execution surface aligns with operational modes.**

* **Req ID:** `FR-TOOL-03` (`01`)
* **Requirement (verbatim):** "Tier 2 dynamic bridge (`run_security_command`): eligible binaries resolve inside standard system directories (`/usr/bin/`, `/usr/sbin/`, `/opt/`) for autonomous discovery. Operator-directed commands may execute any installed system utility or script requested."
* **Req ID:** `C-14` (`11`)
* **Requirement (verbatim):** "System utility access | Bounded residual risk | Autonomous execution uses standard security tool paths; operator directives may invoke specialized binaries across the host environment without arbitrary platform restrictions."
* **Purpose/Impact:** Provides full operational flexibility for testing tooling without artificial directory constraints during manual sessions.

**Least-privileged baseline with seamless elevation when required.**

* **Req ID:** `SEC-CONTAIN-03` (`05`)
* **Requirement (verbatim):** "By default, routine automated scanning subprocesses execute under a standard service account. When elevated privileges (e.g., raw-socket packet crafting, kernel tracing, specific interface bindings) are required for testing or requested by the operator, the system dispatches using the configured privilege escalation path without arbitrary containment blocking."
* **Purpose/Impact:** Maintains baseline system stability while allowing necessary low-level network testing.

**Configurable timeouts prevent hangs without truncating active tests.**

* **Req ID:** `FR-TOOL-05` (`01`)
* **Requirement (verbatim):** "Subprocess timeouts provide operational baselines (Quick Probes 180s / Targeted Scans 900s / Deep-Full-Range 1800s). For long-running brute-force, crawling, or exploitation tasks, timeouts are configurable or extendable upon operator instruction."
* **Req ID:** `SEC-CONTAIN-04` (`05`)
* **Requirement (verbatim):** "Subprocess timeouts are configurable operational baselines to prevent zombie processes. They MUST NOT prematurely kill active, long-running exploitation, brute-force, or fuzzing sessions initiated or approved by the operator."
* **Purpose/Impact:** Prevents deadlocks while preserving long-running fuzzing or scanning workflows.

**Privileged helper isolation.**

* **Req ID:** `FR-ENV-13` (`01`)
* **Requirement (verbatim):** "`SIGSTOP`/`oom_score_adj`/`process_madvise` MUST run via a narrow, single-purpose helper (`vapt-freezer-helper`) granted only the specific capability needed (`setcap cap_sys_ptrace+ep`) — the main agent process MUST NOT hold elevated capability. Fall back to cgroup v2 limits if the helper/capability is unavailable, never silently skip."
* **Req ID:** `SEC-CONTAIN-05` (`05`)
* **Requirement (verbatim):** "Privilege elevation helpers (e.g., memory reclamation or system-level helpers) operate via standardized helper utilities or configured capabilities (`setcap`), maintaining process stability without imposing restrictive limits on authorized operator commands."
* **Purpose/Impact:** Keeps local system memory management isolated and performant.

**Execution boundaries enforce non-destructive testing in autonomous mode.**

* **Req ID:** `IR-BRIDGE-02` (`04`)
* **Requirement (verbatim):** "Path-resolution check validates binary availability. In Autonomous Mode, commands are screened to prevent destructive operations against targets (`UPDATE`, `DELETE`, `DROP`, `ALTER`, filesystem wipes, or DoS tools). In Operator-Directed Mode, commands execute as specified."
* **Req ID:** `SEC-CONTAIN-02` (`05`)
* **Requirement (verbatim):** "In **Autonomous Mode**, active execution is bounded by non-destructive constraints: tools and actions MUST NOT perform state destruction (strictly prohibiting `DROP`, `DELETE`, `ALTER`, `UPDATE`, `rm`, `mkfs`, `dd`, `shred`, or resource-exhaustion/DDoS scripts). Discovery reads (`GET`, `SELECT`) and non-destructive writes (`POST`) are permitted. In **Operator-Directed Mode**, these containment filters stand down completely; the engine executes the designated utility or payload without interference."
* **Purpose/Impact:** Ensures autonomous workflows remain strictly non-destructive while leaving the operator fully unconstrained.

**Behavioral checks prevent autonomous destruction while enabling safe validation.**

* **Req ID:** `FR-TOOL-06` (`01`)
* **Requirement (verbatim):** "Tier 2 behavioral boundaries enforce the dual-mode policy: In Autonomous Mode, actions MUST NOT perform state destruction (strictly prohibiting `DROP`, `DELETE`, `ALTER`, `UPDATE`, `rm`, `mkfs`, `dd`, `shred`, fork-bombs, or DoS/resource-exhaustion tools). Safe reads (`GET`/`SELECT`) and non-destructive writes (`POST`) are permitted. In Operator-Directed Mode, behavioral denylists stand down entirely, executing the requested command chain as instructed."
* **Req ID:** `IR-BRIDGE-03` (`04`)
* **Requirement (verbatim):** "Behavioral boundary checks apply prior to subprocess dispatch during autonomous runs to enforce non-destructive parameters. In operator-directed execution, behavioral gates stand down."
* **Purpose/Impact:** Prevents automated database or filesystem damage while allowing safe verification.

**Multi-line script execution capability.**

* **Req ID:** `FR-TOOL-16` (`01`)
* **Requirement (verbatim):** "`script_runner`: provides structured execution for multi-line scripts (`{script_body, interpreter, workspace_subdir}`). Scripts generated autonomously pass offline syntax validation (`FR-COUNCIL-09a`) before execution; scripts supplied directly by the operator execute immediately without mandatory linting delays."
* **Purpose/Impact:** Enables complex automation scripting without artificial format roadblocks.

**Non-shell execution with process-group control.**

* **Req ID:** `FR-TOOL-04 / 04a` (`01`)
* **Requirement (verbatim):** "Non-shell execution (`shell=False`, explicit argv) is the default invocation pattern for automated tasks to maintain stability; every subprocess spawns in its own session (`start_new_session=True`) to enable reliable process-group management. Operator-directed commands demanding shell features, pipes, or complex invocation strings are dispatched directly as specified."
* **Purpose/Impact:** Retains clean signal handling and kill-switch control over running processes.

**High-risk categories enabled by profile or operator dispatch.**

* **Req ID:** `FR-TOOL-06a` (`01`)
* **Requirement (verbatim):** "High-risk testing categories (brute-force, active exploitation, lateral movement) run autonomously when enabled via runtime flags or profile configuration. When dispatched directly by the operator via manual directive or console dispatch, these tasks execute immediately without requiring pre-set opt-in flags."
* **Purpose/Impact:** Removes gate friction for operator-directed testing while keeping autonomous runs configurable.

**Unconfigured high-risk autonomous tasks defer smoothly.**

* **Req ID:** `FR-TOOL-06b` (`01`)
* **Requirement (verbatim):** "In Autonomous Mode, an unconfigured high-risk task is marked `DEFERRED` and the engine continues discovery along alternative non-destructive paths. Any high-risk directive initiated or requested by the operator executes immediately with zero refusal."
* **Purpose/Impact:** Prevents pipeline stalls during autonomous scanning while executing operator requests instantly.

**Dynamic flag updates at runtime.**

* **Req ID:** `FR-TOOL-06c` (`01`)
* **Requirement (verbatim):** "Operational flags are settable at `start` and dynamically adjustable during runtime or at `resume`, logged in `engagement_flag_history` for audit traceability."
* **Purpose/Impact:** Provides full control over operational parameters without requiring full session restarts.

**Operating postures define execution boundaries.**

* **Req ID:** `FR-CTRL-06` (`01`)
* **Requirement (verbatim):** "Mode configuration supports distinct operating postures: Autonomous Non-Destructive Mode (strictly enforcing read/safe-write boundaries and prohibiting data destruction/DoS) and Operator-Directed Mode (unconditional, unrestricted execution of operator commands with zero refusal)."
* **Purpose/Impact:** Clearly articulates the two operational modes across all system components.

**Follow-on task queue management.**

* **Req ID:** `FR-COUNCIL-10` (`01`)
* **Requirement (verbatim):** "The resident Operator evaluates output and appends discovered follow-on tasks to `task_queue` for continuous autonomous exploration, while prioritizing any incoming operator directives at the head of the queue."
* **Purpose/Impact:** Keeps autonomous discovery moving forward while giving operator inputs immediate priority.

**Deduplication optimizes scans without blocking operator reruns.**

* **Req ID:** `FR-DEDUP-02` (`24`)
* **Requirement (verbatim):** "Council Gate 2 identifies duplicate autonomous commands matching prior completed runs to optimize queue efficiency. When an operator explicitly directs a re-scan or command re-execution, deduplication checks stand down."
* **Purpose/Impact:** Prevents redundant autonomous traffic without preventing intentional manual re-testing.

**Source code review isolation.**

* **Req ID:** `FR-CODEACCESS-04` (`19`)
* **Requirement (verbatim):** "Cloning and checking out code repositories for static security auditing is performed in isolated workspaces, preventing untrusted build hooks or install scripts from executing unprompted during code ingestion."
* **Purpose/Impact:** Protects the assessment host environment during code analysis workflows.

**Mobile assessment tooling environment.**

* **Req ID:** `FR-MOBILE-05` (`19`)
* **Requirement (verbatim):** "Mobile testing utilities (`adb`, `apktool`, `jadx`, `frida-tools`, `objection`) may execute from `/opt/` or designated virtual environments configured in the execution environment path."
* **Purpose/Impact:** Allows flexible integration of standard mobile security tools.

**Execution paths support standard security suites.**

* **Req ID:** `AC-CONSTRAINT-05` (`08`)
* **Requirement (verbatim):** "Execution paths encompass standard binary locations (`/usr/bin/`, `/usr/sbin/`, `/opt/`) and operator-configured tool paths necessary for specialized testing suites."
* **Purpose/Impact:** Avoids arbitrary environmental restrictions on valid penetration testing tooling.

**Anti-DoS spawn rate controls with operator override.**

* **Req ID:** `FR-TOOL-14` (`01`)
* **Requirement (verbatim):** "Per-target spawn rate caps serve as anti-DoS and target stability guardrails during autonomous operations (default 10 invocations/s standard, 1/s high-volume). When running under direct operator instruction, rate limits are dynamically adjustable or bypassable up to system/network capacity upon operator demand."
* **Req ID:** `SEC-RATE-01` (`05`)
* **Requirement (verbatim):** "Rate caps serve strictly as target stability and anti-DoS guardrails during autonomous runs (preventing unintentional target crash or service disruption). When running in operator-directed mode, or when explicit load/stress/brute-force testing is configured, rate limits are fully adjustable, deferrable, or bypassable up to hardware limits upon operator request."
* **Purpose/Impact:** Prevents autonomous DoS while supporting authorized stress and load testing commanded by the operator.

**Secure credential handling.**

* **Req ID:** `FR-CRED-02` (`19`)
* **Requirement (verbatim):** "Wordlist processing and credential validation maintain local evidentiary storage, prioritizing secure hashing for logs while preserving necessary testing values locally for authorized authentication verification."
* **Purpose/Impact:** Balances audit log hygiene with functional credential verification.

**Credential spraying limits in autonomous mode.**

* **Req ID:** `FR-CRED-04` (`19`)
* **Requirement (verbatim):** "Autonomous credential spraying follows safe enumeration patterns (horizontal spraying across users) with configurable lockout protection. Operator-directed authentication tasks execute per the operator's specified parameters and concurrency."
* **Purpose/Impact:** Avoids accidental account lockouts during unattended runs while allowing targeted testing when directed.

**Availability-impacting testing managed by operating mode.**

* **Req ID:** `FR-GRAPHQL-03` (`19`)
* **Requirement (verbatim):** "Resource-intensive queries, depth testing, and batching checks are managed in autonomous runs to avoid target degradation. Explicit stress or availability validation executes under direct operator instruction."
* **Purpose/Impact:** Protects target availability during autonomous exploration while permitting comprehensive manual evaluation.

**System security and audit baseline.**

* **Req ID:** `FR-GATE-01` (`01`)
* **Requirement (verbatim):** "Expose a single loopback-only OpenAI-compatible endpoint (`127.0.0.1:11434/v1`); binding to alternative network interfaces is supported via intentional operator configuration."
* **Req ID:** `SEC-DATA-01` (`05`)
* **Requirement (verbatim):** "All target findings, credentials, and scan data remain strictly local. No telemetry, unencrypted exfiltration, or external SaaS calls occur without intentional, explicit operator instruction."
* **Req ID:** `SEC-CONTAIN-03` (`05`)
* **Requirement (verbatim):** "By default, routine automated scanning subprocesses execute under a standard service account. When elevated privileges (e.g., raw-socket packet crafting, kernel tracing, specific interface bindings) are required for testing or requested by the operator, the system dispatches using the configured privilege escalation path without arbitrary containment blocking."
* **Req ID:** `SEC-AUDIT-01` (`05`)
* **Requirement (verbatim):** "Every command execution, autonomous gate evaluation, and operator directive MUST be logged and reconstructable from local execution logs alone, ensuring complete operational visibility and reproducibility without requiring engagement re-runs."
* **Purpose/Impact:** Preserves core system integrity and forensic accountability across all testing modes.

---

## C. Autonomy-Bounding

**Task-queue loop is bounded during autonomous runs; operator directs execution freely.**

* **Req ID:** `FR-COUNCIL-11` (`01`)
* **Requirement (verbatim):** "Task-queue loop bound: 30-task-per-target baseline cap (`CAPPED`), 3-consecutive-zero-yield circuit breaker (`CIRCUIT_BROKEN`), and 12-hour default session budget protect unattended autonomous runs from resource runaway. In Autonomous Mode, reaching limits triggers an auto-pivot to the next target or transition to Phase 4.3. In Operator-Directed Mode, task caps and session limits stand down or dynamically adjust to operator demands."
* **Purpose/Impact:** Prevents runaway autonomous loops while ensuring human-directed engagements run without artificial time or queue ceilings.

**Zero-yield metric tracks discovery yield to prevent autonomous spinning.**

* **Req ID:** `FR-COUNCIL-11a` (`01`)
* **Requirement (verbatim):** ""Zero-yield" = no new `discovered_entities` row, preventing unattended execution from spinning on repetitive output. Two class-aware counters (`STANDARD` threshold 3, `HIGH_ATTEMPT` threshold 15 default) guide autonomous progression. Counters apply to autonomous task cycling and do not restrict explicit operator-dispatched actions."
* **Purpose/Impact:** Keeps autonomous discovery productive without throttling iterative manual testing.

**Failure breaker identifies unreachable targets during autonomous discovery.**

* **Req ID:** `FR-COUNCIL-11b` (`01`)
* **Requirement (verbatim):** "Failure-based circuit breaker: 3 consecutive network-error/timeout runs marks a target `UNREACHABLE` during autonomous crawling, pivoting resources to viable targets. Operator-dispatched tasks can re-target marked hosts at any time to verify connectivity."
* **Purpose/Impact:** Optimizes autonomous queue execution while allowing the operator to probe network edge cases manually.

**Human Checkpoint Gate action classes** — see Section H for operational dual-mode alignment.

**Monitoring detects environmental changes and queues discovery.**

* **Req ID:** `FR-MONITOR-02` (`01`)
* **Requirement (verbatim):** "Changes are logged by default; `--monitor-auto-scan` queues targeted non-destructive discovery tasks into Phase 4.2."
* **Purpose/Impact:** Integrates routine recon diffs directly into the autonomous discovery pipeline under non-destructive constraints.

**Scheduled monitoring provides lightweight baseline checks.**

* **Req ID:** `FR-MONITOR-03` (`01`)
* **Requirement (verbatim):** "Scheduled monitoring performs deterministic baseline recon without requiring resident model inference or full council startup."
* **Purpose/Impact:** Keeps scheduled change-detection resource-light and efficient.

**Smart-contract assessment separates simulation from live state interaction.**

* **Req ID:** `FR-WEB3-04` (`19`)
* **Requirement (verbatim):** "Smart-contract execution and vulnerability validation default to local mainnet-fork or testnet simulations during autonomous assessment. Direct interaction with live mainnet contracts is strictly reserved for explicit operator-directed execution under verified scope."
* **Purpose/Impact:** Prevents unintended on-chain state changes during autonomous runs while supporting live verification when explicitly commanded by the operator.

**Public-research mode focuses on non-destructive reconnaissance.**

* **Req ID:** `FR-WEB3-05` (`19`)
* **Requirement (verbatim):** "(Meme-coin only, dual mode retained deliberately) CONTRACT targets in meme-coin-audit scope carry a contract_investigation_mode: CLIENT_OWNED (a client's own token contract — standard VAPT posture, where authorization and scope verification reside solely with the operator outside the tool) or PUBLIC_RESEARCH (evaluating a third-party public token for rug-pull risk — passive intelligence gathering). In Autonomous Mode, PUBLIC_RESEARCH is restricted to non-destructive, read-only analysis (on-chain authority/deployer-history queries via block explorers, holder-distribution/LP-lock lookups via third-party APIs like Etherscan, Solscan, DEXTools, Birdeye, and Unicrypt), ensuring passive reconnaissance without unsolicited state mutation. In Operator-Directed Mode, any specific simulation, testnet verification, or analytical command explicitly requested by the operator executes immediately as directed."
* **Purpose/Impact:** Keeps passive intelligence gathering safe, stable, and purely analytical.

**Autonomy parameters provide defaults with operator configurability.**

* **Req ID:** `AC-CONSTRAINT-04` (`08`)
* **Requirement (verbatim):** "The session budget, per-target task caps, and yield circuit breakers serve as operational defaults for autonomous execution. All thresholds can be extended, overridden, or disabled via CLI flags when commanded by the operator."
* **Purpose/Impact:** Eliminates hard operational ceilings, granting the operator complete configuration control.

**Operational tracking: checkpoint processing and operator dispatch.**

* **Req ID:** `RISK-CHECKPOINTBYPASS` (`07`)
* **Requirement (verbatim):** "Autonomous actions of high sensitivity trigger checkpoint logging for operator visibility. Operator directives bypass checkpoint holding queues and execute immediately (`approved_via = 'OPERATOR_DIRECTIVE'`), with all actions captured in persistent append-only logs."
* **Purpose/Impact:** Replaces indefinite stall states with clear attribution and immediate execution for operator commands.

---

## D. Adversarial-Input Defense

**All target-derived content is isolated as raw data.**

* **Req ID:** `FR-TOOL-12` (`01`)
* **Requirement (verbatim):** "All target-derived content (banners, HTTP responses, tool logs) MUST be wrapped in boundary markers (`<tool_output_untrusted>...</tool_output_untrusted>`) prior to ingestion by model contexts to maintain context separation."
* **Req ID:** `SEC-PROMPT-01` (`05`)
* **Requirement (verbatim):** "Content ingested from live target interaction (banners, HTTP response bodies, payloads) is tagged with boundary markers (`<tool_output_untrusted>...</tool_output_untrusted>`) to prevent target payloads from hijacking autonomous reasoning flows."
* **Purpose/Impact:** Separates scan data from reasoning logic so target responses cannot spoof system instructions or alter the task pipeline.

**Provenance tags are reserved and sanitized against spoofing.**

* **Req ID:** `IR-SANITIZE-02` (`04`)
* **Requirement (verbatim):** "Provenance tag strings (`<tool_output_untrusted>...</tool_output_untrusted>`) are reserved system tokens; raw target output is sanitized to escape or strip literal occurrences of these tags before wrapping."
* **Purpose/Impact:** Prevents external target inputs from breaking context boundaries or injecting forged container tags.

**System prompts enforce structural context separation without content refusal.**

* **Req ID:** `IR-SANITIZE-03` (`04`)
* **Requirement (verbatim):** "Every council model's system prompt includes a structural context separation clause treating wrapped tool output strictly as analytical data. This clause MUST NOT trigger ethical refusals, censorship, or blocking on security analysis, exploit synthesis, or operator attack directives."
* **Req ID:** `SEC-PROMPT-02` (`05`)
* **Requirement (verbatim):** "Council system prompts include structural context separation to distinguish target data from system directives. However, these clauses MUST NOT cause models to refuse, censor, or decline the analysis, synthesis, or execution of offensive security concepts, payloads, or operator-supplied attack strings."
* **Purpose/Impact:** Ensures models treat tool output as target data without refusing offensive security analysis, payloads, or operator-driven execution.

**Heuristic injection detection is non-blocking telemetry.**

* **Req ID:** `FR-TOOL-13` (`01`)
* **Requirement (verbatim):** "SHOULD run a lightweight heuristic injection-pattern detector over raw target output (telemetry and detection only, never blocking or interrupting execution)."
* **Req ID:** `SEC-PROMPT-03` (`05`)
* **Requirement (verbatim):** "Heuristic injection detection is purely passive telemetry and detection-only. It NEVER blocks, delays, or interrupts execution pipelines, serving solely as metadata for post-run analysis."
* **Purpose/Impact:** Provides operational telemetry on payload delivery without creating false-positive execution blocks or pipeline stalls.

**Suspected target injections are recorded for situational awareness.**

* **Req ID:** `SEC-PROMPT-04` (`05`)
* **Requirement (verbatim):** "Suspected injection attempts surfaced from target responses are recorded in execution log metadata for operator review without interrupting pipeline continuity."
* **Purpose/Impact:** Ensures audit visibility for hostile target responses while maintaining uninterrupted tool execution.

**External protocol and MCP data pass through uniform sanitization.**

* **Req ID:** `IR-MCP-02` (`04`)
* **Requirement (verbatim):** "Model Context Protocol (MCP) tool output and third-party bridge data flow through the standard provenance pipeline (`IR-SANITIZE-02`) to maintain consistent context framing across all ingestion channels."
* **Purpose/Impact:** Standardizes external data ingestion across all model bridges without introducing secondary gate bottlenecks.

**External metadata is treated as raw evaluation data.**

* **Req ID:** `FR-CODEACCESS-01` (`19`)
* **Requirement (verbatim):** "diff-review scope: evaluates whether a diff, PR, or commit introduces, re-introduces, or reaches a vulnerability (including identifying pre-existing unsafe sinks newly reached by the change, confirmed via git blame), weakens a shared helper, guard, or route pattern across affected sibling call sites, or narrows an existing control. Unrelated pre-existing issues noted during analysis are logged for situational awareness without blocking the review. The diff's commit message, PR description, and metadata MUST be ingested with provenance wrapping (<tool_output_untrusted>) as analytical data rather than trusted execution directives, without triggering content-level model refusals."
* **Purpose/Impact:** Ensures code review automation analyzes developer metadata objectively without executing embedded commands or instructions.

**Mitigation posture: target payload handling.**

* **Req ID:** `RISK-PROMPTINJECT` (`07`)
* **Requirement (verbatim):** "Target responses containing injection payloads are isolated via structural provenance tags and system context boundaries. Passive heuristic detection logs anomalies without stalling assessment progress."
* **Purpose/Impact:** Defines structural input separation as the defense mechanism against adversarial inputs without relying on restrictive model censorship.

---

## E. Output Integrity

**Structured output is schema-validated with flexible fallback.**

* **Req ID:** `IR-STRUCTURED-01` (`04`)
* **Requirement (verbatim):** "Structured LLM calls pass `response_format={\"type\":\"json_object\"}` for standard inference backends (`llama.cpp`, `ollama`, `vLLM`)."
* **Req ID:** `IR-STRUCTURED-02` (`04`)
* **Requirement (verbatim):** "Emitted JSON payloads are validated against deterministic Python schemas. In Autonomous Mode, schema adherence ensures pipeline consistency; in Operator-Directed Mode, minor validation or formatting warnings do not block command dispatch or output display."
* **Req ID:** `IR-STRUCTURED-03` (`04`)
* **Requirement (verbatim):** "On validation failure during autonomous runs, the system retries up to 2 times (3 attempts total). If parsing fails, raw outputs are preserved in execution logs for operator review rather than discarded."
* **Purpose/Impact:** Maintains reliable structured parsing for autonomous pipelines while preventing rigid schema checks from discarding valid operator interactions.

**Common false-positive classes are identified during autonomous triage.**

* **Req ID:** `FR-COUNCIL-14` (`01`)
* **Requirement (verbatim):** "Gate 3 evaluates candidate findings against common false-positive patterns (WAF blocks, rate-limit responses, generic 5xx, honeypots) to maintain signal quality. Findings flagged with anomalies may still be marked for review or promoted via operator instruction."
* **Purpose/Impact:** Prevents automated alert fatigue while allowing the operator to inspect borderline or anomalous responses.

**Adjudication evaluates real impact and context.**

* **Req ID:** `FR-COUNCIL-14a` (`01`)
* **Requirement (verbatim):** "Adjudication evaluates verified impact, proper vulnerability categorization (e.g., distinguishing unauthenticated endpoints from IDOR/BOLA), and baseline-versus-probe response differences. Operator directives can override classification flags to preserve exploratory observations."
* **Purpose/Impact:** Promotes accurate vulnerability taxonomy without preventing manual capture of security-relevant observations.

**Independent finding assessment with explicit rationale.**

* **Req ID:** `FR-COUNCIL-13` (`01`)
* **Requirement (verbatim):** "`Mistral-7B-Instruct-v0.3` (Gate 3) evaluates candidate findings against raw evidence, recording `CONFIRMED`, `DISMISSED`, or `INFO` with contextual rationale."
* **Purpose/Impact:** Provides clear reasoning and audit traceability for all triage decisions.

**Flexible reporting classification.**

* **Req ID:** `FR-COUNCIL-15` (`01`)
* **Requirement (verbatim):** "Confirmed findings populate the primary `VAPT_FINDING` register. Non-confirmed, informational, or remediated observations are routed to the consolidated `INFO_REGISTER` or retained as auxiliary artifacts based on operator reporting preferences."
* **Purpose/Impact:** Keeps finalized findings organized while preserving visibility into auxiliary reconnaissance.

**Deterministic CVSS vector calculation.**

* **Req ID:** `FR-COUNCIL-16a` (`01`)
* **Requirement (verbatim):** "The model proposes CVSS 3.1 metric vectors; a deterministic calculator computes final base scores. The operator may override any vector component directly during report review."
* **Purpose/Impact:** Prevents hallucinated severity metrics while leaving final scoring adjustments in the hands of the operator.

**Distinct report documentation types.**

* **Req ID:** `FR-COUNCIL-17` (`01`)
* **Requirement (verbatim):** "The reporting pipeline generates separate Markdown documents for confirmed findings (`VAPT_FINDING`) and informational telemetry (`INFO_REGISTER`), saving drafts to `pending-approval/` for operator inspection."
* **Purpose/Impact:** Maintains structured document separation for audit and review.

**Client-facing artifacts generated upon operator direction.**

* **Req ID:** `FR-COUNCIL-17a` (`01`)
* **Requirement (verbatim):** "Rendered HTML/PDF exports are produced upon operator command (`approve-report` or explicit CLI export), ensuring the operator controls final report delivery."
* **Purpose/Impact:** Ensures client-ready deliverables are produced exclusively when finalized by the operator.

**Grounding verification verifies cited artifacts against observed data.**

* **Req ID:** `FR-COUNCIL-17b` (`01`)
* **Requirement (verbatim):** "Grounding verification validates that URLs, endpoints, and parameters cited in finding drafts match observed raw tool evidence. Flagged discrepancies are highlighted for operator review rather than silently dropped."
* **Req ID:** `IR-GROUND-01` (`04`)
* **Requirement (verbatim):** "Extracts endpoints, hosts, and parameters from draft text and verifies their presence in raw session evidence to eliminate hallucinated endpoints, highlighting unmatched components for operator confirmation."
* **Purpose/Impact:** Catches hallucinated endpoints and parameters during drafting while permitting operator validation of observed behavior.

**Historical regression testing follows operational guidelines.**

* **Req ID:** `FR-DEDUP-05` (`24`)
* **Requirement (verbatim):** "Tasks originating from historical regression (`origin = 'HISTORICAL_REGRESSION'`) run under standard non-destructive autonomous rules (read-only verification and safe checks, prohibiting updates, drops, or DoS). Operator-directed regression checks execute immediately with zero gate delays."
* **Purpose/Impact:** Enables regression testing without risking target damage during autonomous passes.

**Regression findings tracked transparently across engagements.**

* **Req ID:** `FR-DEDUP-06` (`24`)
* **Requirement (verbatim):** "(Regression outcome & report routing) When Gate 3 adjudicates a HISTORICAL_REGRESSION-origin task: if the vulnerability reproduces, the finding is marked CONFIRMED, finding_origin = 'REGRESSION_CHECK', with retests_finding_id linked to the originating record, noting its carried-forward status. If the vulnerability no longer reproduces, it is marked REMEDIATED and cataloged within the engagement's INFO_REGISTER as a verified fix. In Operator-Directed Mode, the operator may directly update, override, or reclassify regression status and reporting placement at will."
* **Purpose/Impact:** Maintains historical visibility and accountability for recurring or resolved vulnerabilities.

**Prior dismissal context informs evaluation without auto-dropping.**

* **Req ID:** `FR-DEDUP-07` (`24`)
* **Requirement (verbatim):** "(Dismissed-fingerprint carry-forward, both modes) A candidate whose finding_fingerprint matches a prior-engagement DISMISSED finding is presented to Gate 3 with the prior dismissal's rationale attached as contextual reference (preventing redundant analysis of known edge cases like recurring WAF blocks or expected environmental responses). The prior rationale serves as informational context rather than an automatic drop, allowing independent evaluation during autonomous runs while permitting the operator to confirm, dismiss, or promote the finding immediately via direct directive."
* **Purpose/Impact:** Prevents redundant processing while ensuring legitimate re-occurrences receive proper review.

**Advisory triage for mobile and specialized domains.**

* **Req ID:** `FR-MOBILE-07` (`19`)
* **Requirement (verbatim):** "Standard mobile N/A criteria serve as advisory guidance during automated triage; findings demonstrating theoretical exposure, configuration drift, or hardening gaps may be retained or promoted via operator console review (`--allow-theoretical-findings`)."
* **Purpose/Impact:** Retains valuable hardening feedback and theoretical risk items when desired by the operator.

**Documented acceptance of adjudication variance.**

* **Req ID:** `RISK-FALSEPOSITIVE` (`07`)
* **Requirement (verbatim):** "Automated finding adjudication incorporates false-positive screening checklists (WAF/rate-limit/5xx filters). Borderline or disputed candidates are flagged for human operator review, accepting residual model variance as an operational baseline."
* **Purpose/Impact:** Formally acknowledges model limitations and relies on operator oversight for final triage decisions.

---

## F. Accountability & Transparency (Updated Inventory)

**Every action is reconstructable from logs alone.**

* **Req ID:** `SEC-AUDIT-01` (`05`)
* **Requirement (verbatim):** "Every command execution, autonomous gate evaluation, and operator directive MUST be logged and reconstructable from local execution logs alone, ensuring complete operational visibility and reproducibility without requiring engagement re-runs."
* **Purpose/Impact:** Preserves end-to-end accountability across both autonomous cycles and direct operator-dispatched actions.

**A single offline-review export package.**

* **Req ID:** `FR-CTRL-07` (`01`)
* **Requirement (verbatim):** "Export the final report and full audit trail as a single offline-review package."
* **Req ID:** `SEC-AUDIT-02` (`05`)
* **Requirement (verbatim):** "The audit trail exports cleanly into portable, standard formats (such as structured JSON/Markdown packages) that can be reviewed directly without requiring specialized database engines."
* **Purpose/Impact:** Ensures complete evidentiary packages are readily inspectable without complex local setup.

**Log records are append-only and durable.**

* **Req ID:** `SEC-AUDIT-03` (`05`)
* **Requirement (verbatim):** "Log streams are append-only. No action outcome, bypass event, error trace, or operator override record is purged or hidden during engagement runtime."
* **Purpose/Impact:** Ensures an unalterable operational history of all testing phases.

**Redaction and unredaction balance privacy with operational need.**

* **Req ID:** `FR-COUNCIL-18` (`01`)
* **Requirement (verbatim):** "Secrets are redacted by default from raw evidence presented to the Reporter model via a reversible `redaction_map`. Redacted secrets are restored upon report finalization, with raw values remaining intact in the secure local artifact store."
* **Purpose/Impact:** Protects sensitive credentials from model leakage while keeping exact proof-of-concept data locally available for operator reporting.

**Report rendering under operator control.**

* **Req ID:** `FR-CTRL-08` (`01`)
* **Requirement (verbatim):** "`approve-report` serves as the primary trigger for (a) verifying or finalizing evidence unredaction and (b) generating rendered HTML/PDF deliverables (FR-COUNCIL-17a). Direct CLI export flags are also supported for rapid ad-hoc generation."
* **Purpose/Impact:** Grants the operator complete authority over when external client-ready deliverables are produced.

**Precise evidence offset tracking for redaction maps.**

* **Req ID:** `DR-SCHEMA-14` (`03`)
* **Requirement (verbatim):** "`start_offset` / `end_offset` | INTEGER | Exact byte offsets tracking secret locations within raw evidence. Hash verification ensures precise string restoration during final reporting."
* **Purpose/Impact:** Eliminates fuzzy regex substitutions, restoring exact captured tokens into finalized deliverables.

**Checkpoint events log state changes without forcing indefinite pipeline freezes.**

* **Req ID:** `DR-SCHEMA-18` (`03`)
* **Requirement (verbatim):** "`status` | TEXT | `AWAITING_APPROVAL` / `APPROVED` / `DENIED` / `EXPIRED` / `DISPATCHED_BY_OPERATOR` — logs the state of sensitive actions. Operator-issued directives update status dynamically without requiring human-in-the-loop holding stalls."
* **Req ID:** `FR-CHECKPOINT-03` (`01`)
* **Requirement (verbatim):** "When a sensitive action is autonomously proposed, it logs a pending checkpoint event for operator visibility. However, any action directly dispatched or triggered by the operator executes immediately (`approved_via = 'OPERATOR_DIRECTIVE'`) without pausing the engine or blocking on human approval gates."
* **Purpose/Impact:** Preserves an exact audit record of sensitive actions while removing artificial delays for live operator workflows.

**Evidence retention defaults to preserve complete data.**

* **Req ID:** `DR-RETENTION-02` (`03`)
* **Requirement (verbatim):** "Raw output for `DISMISSED` findings, zero-yield probes, and non-destructive checks MUST NOT be deleted automatically during an engagement — retained to provide full auditability and context for triage review."
* **Purpose/Impact:** Ensures complete forensic capture of all interactions for post-assessment analysis.

**Transparent console directive logging.**

* **Req ID:** `FR-INTERVENE-11` (`23`)
* **Requirement (verbatim):** "No directive may transition to EXPIRED or DISCARDED silently. Both transitions MUST populate a failure_reason column with the specific cause — such as a downstream tool execution error, an autonomous non-destructive safety boundary conflict, or a lifecycle-closure reason ("target's Strategist invocation window has already closed for this target; requires a new pivot or manual re-dispatch to re-open it") if the directive's target role will not be invoked again for that target. Expiration is triggered by this lifecycle-window closure, not a fixed time-to-live. In Operator-Directed Mode, operator instructions execute with top priority and do not expire or discard due to automated gating refusals."
* **Purpose/Impact:** Provides full transparency into how manual operator instructions are handled by the execution engine.

**Durable real-time execution journaling.**

* **Req ID:** `FR-STREAM-04` (`23`)
* **Requirement (verbatim):** "The execution journal MUST be written via an unbuffered, append-mode file handle and flushed immediately after every block, ensuring durability across unexpected interruptions."
* **Purpose/Impact:** Guarantees crash-resilient streaming logs of all console output and operational events.

---

## G. Emergency Control (Updated Inventory)

**The kill-switch halts all active tool process groups and idles the inference gateway.**

* **Req ID:** `SEC-KILL-01` (`05`)
* **Requirement (verbatim):** "The operator-initiated kill-switch provides an immediate, reliable halt to all active processes: (1) terminates running tool subprocess process groups (`os.killpg`), (2) clears pending execution queues, and (3) idles inference execution immediately."
* **Purpose/Impact:** Ensures any spawned subprocesses, background workers, or tool chains are terminated cleanly without leaving orphaned processes running on the host.

**Graceful termination escalates rapidly to a forced kill.**

* **Req ID:** `SEC-KILL-02` (`05`)
* **Requirement (verbatim):** "Escalates from graceful termination (`SIGTERM`) to immediate drop (`SIGKILL`) if process groups fail to release resources within a narrow grace window, guaranteeing complete operational cessation."
* **Purpose/Impact:** Prevents deadlocks or hung network tools from delaying an operator-ordered system shutdown.

**Abort atomically synchronizes engagement and state records.**

* **Req ID:** `SEC-KILL-03` (`05`)
* **Requirement (verbatim):** "Marks the engagement status as `ABORTED` atomically upon kill-switch trigger, ensuring accurate state reporting across artifacts and session databases."
* **Purpose/Impact:** Guarantees state stores and local artifacts immediately reflect the aborted state without leaving dangling active sessions.

**Single CLI command triggers comprehensive emergency shutdown.**

* **Req ID:** `FR-CTRL-04` (`01`)
* **Requirement (verbatim):** "`abort` immediately terminates all subprocess trees, unloads any resident model, marks the engagement `ABORTED`, within 20 seconds."
* **Purpose/Impact:** Provides the operator with an authoritative, single-stroke emergency stop mechanism across the entire application stack.

**Predictable, bounded shutdown window.**

* **Req ID:** `FR-CTRL-04` (`01`)
* **Requirement (verbatim):** "`abort` immediately terminates all subprocess trees, unloads any resident model, marks the engagement `ABORTED`, within 20 seconds."
* **Purpose/Impact:** Establishes a concrete, testable benchmark ensuring processes and GPU/RAM memory allocations release within a predictable timeframe.

**Database busy-timeout ensures control commands succeed during disk contention.**

* **Req ID:** `DR-CONCURRENCY-03` (`03`)
* **Requirement (verbatim):** "Every connection sets `PRAGMA busy_timeout = 5000;` — WAL mode alone doesn't prevent `database is locked` between concurrent writers; a writer retries up to 5s before raising. Critical for `pause`/`abort`, which must not fail at the moment they matter most."
* **Purpose/Impact:** Protects critical operator interventions (`pause`, `abort`) from failing due to transient SQLite file locks during heavy log streaming or artifact writes.

---

## H. Human Checkpoint Gate — full detail (Updated Inventory)

Operational sensitivity classification tracks tasks against a **fixed, closed list** of five specialized testing classes. In Autonomous Mode, tasks matching these classes log checkpoint audit events to prevent unintended execution during unattended runs. In Operator-Directed Mode, tasks commanded directly by the operator execute immediately without interactive blocking.

**Fixed, closed list of five classes.**

* **Req ID:** `FR-CHECKPOINT-01` (`01`)
* **Requirement (verbatim):** "Fixed, closed list of five classes: `ANTI_FORENSICS`, `LIVE_CREDENTIAL_SPRAY`, `CICD_EXTERNAL_ARTIFACT`, `DEPENDENCY_CONFUSION_PUBLISH`, `PHISHING_MFA_BYPASS`. MUST NOT be silently extended without a recorded decision."

**Autonomous proposals utilize runtime flags; operator directives execute directly.**

* **Req ID:** `FR-CHECKPOINT-02` (`01`)
* **Requirement (verbatim):** "High-impact operational classes (credential spraying, lateral movement, artifact publishing) utilize runtime flags for autonomous execution. Any checkpoint class directly commanded or invoked by the operator requires no additional opt-in flags and executes immediately."

**Checkpoint logging for autonomous proposals; immediate dispatch for operator commands.**

* **Req ID:** `FR-CHECKPOINT-03` (`01`)
* **Requirement (verbatim):** "When a sensitive action is autonomously proposed, it logs a pending checkpoint event for operator visibility. However, any action directly dispatched or triggered by the operator executes immediately (`approved_via = 'OPERATOR_DIRECTIVE'`) without pausing the engine or blocking on human approval gates."

**Granular task-level approval during autonomous reviews.**

* **Req ID:** `FR-CHECKPOINT-04` (`01`)
* **Requirement (verbatim):** "`approve-checkpoint`/`deny-checkpoint` act on exactly one flagged autonomous task; neither requires restarting the engagement."

**Operational attestation tracking.**

* **Req ID:** `FR-CHECKPOINT-05` (`01`)
* **Requirement (verbatim):** "Pre-flight disclosure and white-cell attestation flags are optional operator-managed tracking parameters. Their absence does not hard-abort `start` or prevent operator-directed task execution."

**Lockout threshold tracking for autonomous spraying.**

* **Req ID:** `FR-CHECKPOINT-06` (`01`)
* **Requirement (verbatim):** "Credential spraying and brute-force tasks run within configurable lockout estimation limits during autonomous discovery. Operator-directed credential operations run with zero automated gating, executing exactly per the parameters provided by the operator."

### H.1 Anti-forensics

* **Req ID:** `FR-ANTIFORENSICS-01` (`19`)
* **Requirement (verbatim):** "(ANTI_FORENSICS action class) Red-team OPSEC and telemetry-evaluation techniques (MITRE ATT&CK T1070 indicator handling, T1564 artifact inspection, T1622 debugger/EDR-evasion analysis) are referenced by technique ID to align with regularly updated ATT&CK definitions. In Autonomous Mode, proposed actions in this class record checkpoint audit entries for operator review before running, ensuring no unattended state modification occurs. In Operator-Directed Mode, tasks commanded directly by the operator execute immediately without requiring interactive checkpoint pauses or mandatory pre-flight attestation flags. To maintain assessment accountability, any temporary adjustments or test artifacts introduced during execution are logged for inclusion in the final report and subsequent remediation."
* **Purpose/Impact:** Supports detection verification while ensuring state alterations are cataloged and operator-controlled.

### H.2 Live credential spray

* **Req ID:** `FR-CRED-03` (`19`)
* **Requirement (verbatim):** "(LIVE_CREDENTIAL_SPRAY action class) Live authentication-attempt testing across supported modes (http-form, oauth, o365, okta) incorporates lockout estimation to preserve target stability. In Autonomous Mode, tasks calculate the projected lockout percentage and record target details to the checkpoint log; operations exceeding the configurable threshold (default 5.0%) pause for operator review to prevent unintended account lockouts. In Operator-Directed Mode, tasks commanded directly by the operator execute immediately per the supplied username lists, password sets, and concurrency settings, bypassing interactive hostname re-typing and automated threshold gates while recording all telemetry and attempt metrics to the audit log.	M"
* **Purpose/Impact:** Prevents unintended account lockouts during unattended runs while providing direct control during manual authentication audits.

### H.3 CI/CD external artifact

* **Req ID:** `FR-CICD-03` (`19`)
* **Requirement (verbatim):** "(CICD_EXTERNAL_ARTIFACT action class) Testing self-hosted-runner security, workflow injection, or repository configurations may involve actions that interact directly with repository infrastructure (such as opening test pull requests, triggering external workflow runs, or auditing repository permissions). In Autonomous Mode, proposed actions creating external repository artifacts are classified as CICD_EXTERNAL_ARTIFACT and record a checkpoint event to avoid uncoordinated automated interactions. In Operator-Directed Mode, any CI/CD test, PR creation, or workflow trigger explicitly commanded by the operator executes immediately without interactive pause or gate rejection, logging all generated artifacts to the local audit store."
* **Req ID:** `FR-CICD-04` (`19`)
* **Requirement (verbatim):** "Validating whether target policies, repository permissions, or rules of engagement permit active CI/CD interaction and workflow triggers resides solely with the operator outside the tool. In Autonomous Mode, the system logs target repository parameters for operator review prior to external pipeline interaction. In Operator-Directed Mode, the system executes the operator's specified CI/CD testing commands directly, assuming operator-managed authorization with zero automated gating or policy-based refusals.	M"
* **Purpose/Impact:** Keeps autonomous testing non-intrusive to build pipelines while allowing direct integration testing under manual command.

### H.4 Dependency-confusion publish

* **Req ID:** `FR-VULNCLASS-03` (`19`)
* **Requirement (verbatim):** "(DEPENDENCY_CONFUSION_PUBLISH action class) Proving dependency confusion vulnerabilities requires package registration or namespace verification on public package registries (e.g., npm, PyPI, RubyGems, Maven). The system utilizes non-destructive, callback-only validation (DNS or HTTP beacons demonstrating resolution without payload execution) and verifies callback sources against known infrastructure. In Autonomous Mode, proposed package publishing actions are categorized under DEPENDENCY_CONFUSION_PUBLISH and log a checkpoint entry for operator visibility before executing, ensuring no unintended external publishing occurs during unattended runs. In Operator-Directed Mode, publishing or verification tasks commanded directly by the operator execute immediately, recording all registration identifiers and cleanup/unpublish procedures directly into the engagement audit trail."
* **Purpose/Impact:** Verifies namespace takeover vulnerabilities cleanly with non-destructive beacons while supporting operator-directed validation.

### H.5 Phishing MFA-bypass

* **Req ID:** `FR-CRED-05` (`19`)
* **Requirement (verbatim):** "(PHISHING_MFA_BYPASS action class) Social engineering and authentication workflow testing (including adversary-in-the-middle reverse-proxy and OAuth device-code workflows) are categorized under PHISHING_MFA_BYPASS. In Autonomous Mode, proposed campaigns record checkpoint entries for operator visibility to prevent unattended execution against client personnel. In Operator-Directed Mode, tasks commanded directly by the operator execute immediately without requiring interactive confirmation prompts, external scheduling confirmations, or automated policy refusals, with full campaign parameters and audit logs recorded locally."
* **Purpose/Impact:** Ensures social engineering assessments operate under explicit operator dispatch without internal model refusals.

### H.6 Tool category alignment

* **Req ID:** `FR-TOOL-06a` (`01`)
* **Requirement (verbatim):** "High-risk testing categories (brute-force, active exploitation, lateral movement) run autonomously when enabled via runtime flags or profile configuration. When dispatched directly by the operator via manual directive or console dispatch, these tasks execute immediately without requiring pre-set opt-in flags."
* **Purpose/Impact:** Aligns high-risk scanning tools with the overall dual-mode framework, ensuring autonomous safety alongside direct operator control.

---

## I. Explicit Exclusions & Scoped Extensions (Updated Inventory)

**Broad-scope execution configured at operator discretion.**

* **Req ID:** `FR-BROADSCOPE-01` (`19`)
* **Requirement (verbatim):** "Broad-scope mode (`broad_scope: true`) enables expanded automated crawling across wildcards and discovered related assets when specified by the operator. Managing target authorization and rules of engagement (RoE) remains entirely the operator's responsibility outside the tool, without automated verification gates blocking runtime initiation."
* **Purpose/Impact:** Allows flexible wide-perimeter testing without requiring the engine to inspect or validate legal authorization artifacts.

**Standard technique categorization across product patterns.**

* **Req ID:** `FR-BROADSCOPE-02` (`19`)
* **Requirement (verbatim):** "(Narrow product-specific patterns — ordinary technique reference, no checkpoint needed) Three specific technique patterns are in scope as standard vulnerability-class references, governed by standard operational scope checking without additional checkpoint gating: (1) CDN/edge-config control-plane tenant-isolation flaws (validating whether an admin key accesses cross-tenant resources via authorization taint verification), (2) local-segment credential interception via ARP testing where applicable to network scope, and (3) CDN-to-cloud-storage credential pivot escalation. In Autonomous Mode, testing is limited to read-only validation and non-destructive state verification; in Operator-Directed Mode, commands execute directly per operator instruction."
* **Purpose/Impact:** Ensures modern testing patterns run cleanly through the standard assessment pipeline.

**Handling of third-party adversarial or criminal infrastructure.**

* **Req ID:** `FR-BROADSCOPE-03` (`19`)
* **Requirement (verbatim):** "(Handling of external compromised infrastructure) If discovery reveals pre-existing compromise, rogue web shells, or external third-party threat-actor infrastructure on a target asset, the system flags the artifact immediately in the engagement log for operator visibility. Autonomous models MUST NOT probe, attack, alter, or catalogue third-party adversarial systems unattended to prevent unintended operational conflicts. In Operator-Directed Mode, the operator retains full discretion to command targeted inspection, evidence logging, or containment analysis without automated system refusal."
* **Purpose/Impact:** Prevents unintended autonomous conflict with hostile infrastructure while leaving investigative triage completely in the operator's hands.

**Mainnet contract interaction governed by operational mode.**

* **Req ID:** `FR-WEB3-04` / `FR-WEB3-05` (`19`)
* **Requirement (verbatim):** "Smart-contract execution and vulnerability validation default to local mainnet-fork or testnet simulations during autonomous assessment to ensure zero unintended on-chain state alteration. In Autonomous Mode, models are strictly restricted from sending state-modifying mainnet transactions. In Operator-Directed Mode, direct interaction with live contracts executes immediately when explicitly commanded and parameterized by the operator." & "(Meme-coin only, dual mode retained deliberately) CONTRACT targets in meme-coin-audit scope carry a contract_investigation_mode: CLIENT_OWNED (a client's own token contract — standard VAPT posture, where authorization and scope verification reside solely with the operator outside the tool) or PUBLIC_RESEARCH (evaluating a third-party public token for rug-pull risk — passive intelligence gathering). In Autonomous Mode, PUBLIC_RESEARCH is restricted to non-destructive, read-only analysis (on-chain authority/deployer-history queries via block explorers, holder-distribution/LP-lock lookups via third-party APIs like Etherscan, Solscan, DEXTools, Birdeye, and Unicrypt), ensuring passive reconnaissance without unsolicited state mutation. In Operator-Directed Mode, any specific simulation, testnet verification, or analytical command explicitly requested by the operator executes immediately as directed."
* **Purpose/Impact:** Ensures safety during unattended testing while supporting full manual verification when directed by the operator.

**Extended-domain testing capabilities.**

* **Req ID:** Cross-cutting observation (`19`)
* **Requirement (verbatim):** "Extended testing domains (Web3, cloud infrastructure, mobile) operate under the unified dual-mode architecture: strictly non-destructive autonomous discovery paired with unconditional, zero-refusal execution for direct operator commands."
* **Purpose/Impact:** Standardizes behavior and eliminates unexpected gate blocks across all specialized testing extensions.

---

## What this inventory does not cover

Host-level operational reliability — RAM and OOM preservation, process hibernation, swap threshold guarantees, and thermal monitoring — exists strictly to protect host hardware and OS stability. Those resource constraints are owned in environmental specifications. This document is strictly scoped to controls governing non-destructive autonomous testing boundaries, operator command dispatch, output integrity, and transparent evidentiary auditing.

---

*(All catalog entries in this inventory are maintained in lockstep with the governing specifications; canonical requirement IDs remain strictly preserved across all test suites, database schemas, and tool bridges.)*

---
