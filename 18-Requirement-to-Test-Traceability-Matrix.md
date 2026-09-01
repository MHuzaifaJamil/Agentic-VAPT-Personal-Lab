# Requirement-to-Test Traceability Matrix — Autonomous Agentic VAPT System

**Purpose:** `09-Acceptance-Criteria-and-Test-Plan.md` states its own scope up front —
it is "grouped by requirement cluster rather than enumerating every individual ID."
That is the right shape for a test plan, but it leaves an open question this document
answers directly: for every single requirement ID defined in `01`-`08`, `11`, and `13`,
is there an actual, citable `TP-*` row in `09` that exercises it — or not? This is a
**coverage report only**. It does not modify `09` and does not add new tests; it
records the current state of test-plan coverage against the full requirements corpus,
so a gap is a known, tracked fact rather than something discovered by accident during
implementation.

**Method:** every `FR-*`/`NFR-*`/`DR-*`/`IR-*`/`SEC-*`/`OPS-*`/`RISK-*`/`AC-*`/`C-*`/`IAB-*`
ID defined in `01,02,03,04,05,06,07,08,11,13` was extracted, then checked against every
`TP-*` row in `09` for a specific, citable match. **Conservative rule:** an ID counts as
`Covered` only if a named `TP-*` test/row actually exercises its specific mechanism or
pass criterion — a thematic resemblance to a test elsewhere is not enough. Three
outcomes are used:

- **Covered** — a specific `TP-*` row (or, for `07`/`08`/`11`, the underlying requirement's
  `TP-*` coverage) exists. The row is cited.
- **N/A (not testable)** — the ID is an assumption, constraint, dependency, non-goal,
  risk-register entry, superseded/removed requirement, or pure architecture/language
  choice — not a testable system behavior in its own right. (Risk-register and
  assumption/constraint/dependency/non-goal entries are *all* N/A by this rule: the
  testable unit is the mitigating/governing requirement they cite, which is assessed
  under its own ID elsewhere in this matrix.)
- **NOT COVERED** — a genuine testable requirement with no citable `TP-*` row today.

---

## 01 — Functional Requirements

### FR-PRE

| ID | Covered By | Notes |
|----|-----------|-------|
| FR-PRE-01 | — | NOT COVERED. No test verifies engine-installed/not-already-running pre-check. |
| FR-PRE-02 | — | NOT COVERED. No test verifies Level Zero/SYCL/OpenCL presence check or its CPU-only fallback path specifically. |
| FR-PRE-03 | TP-PRE "Model file integrity" | Corrupt/rename a model file; pre-flight must fail on that model. |
| FR-PRE-04 | TP-PRE "Missing tool binary" | Hide a Tier 1 binary; pre-flight must fail, naming it. |
| FR-PRE-05 | — | NOT COVERED. No test checks NVMe path existence/writability/non-tmpfs. |
| FR-PRE-06 | — | NOT COVERED. No test checks the pre-flight RAM/swap/disk baseline snapshot. |
| FR-PRE-07 | TP-PRE "Operator override path" | Confirms override requires logged justification, visible in export. |
| FR-PRE-08 | TP-PRE "GPU offload benchmark (relative bar)" | Confirms both tok/s measured, recorded, CPU-only flag set correctly. |

### FR-ENV

| ID | Covered By | Notes |
|----|-----------|-------|
| FR-ENV-01 | — | NOT COVERED. No test checks artifact/log redirection away from tmpfs. |
| FR-ENV-02 | — | NOT COVERED. No test checks `TMPDIR`/`TEMP`/`TMP` overrides. |
| FR-ENV-03 | — | NOT COVERED. No test exercises the hibernation-eligible/protected classification logic itself. |
| FR-ENV-04 | TP-ENV "Locked-file protection" | Confirms a locked-file app is never `SIGSTOP`'d. |
| FR-ENV-05 | — | NOT COVERED. No test checks the recorded PID/process-tree list for reversal. |
| FR-ENV-06 | TP-ENV "No interactive prompt" | Confirms zero interactive prompts through Phase 1. |
| FR-ENV-07 | TP-ENV "cgroup v2 fallback" | Fault-injection test exercises the reclamation step's fallback path. |
| FR-ENV-08 | — | NOT COVERED. No test targets the Phase-1-exit re-measurement/abort specifically (TP-RESOURCE's RAM-margin test is a Phase 4 model-load scenario, a different trigger point). |
| FR-ENV-09 | — | NOT COVERED. No test checks table initialization before Phase 2. |
| FR-ENV-10 | — | NOT COVERED. No test checks the resume-offer-on-existing-engagement behavior. |
| FR-ENV-11 | TP-ENV "OOM protection applied" | Confirms `oom_score_adj=-900` set before the memory-pressure step. |
| FR-ENV-12 | TP-ENV "OOM casualty detection" | Fault-injection test confirms partial-success detection/logging. |
| FR-ENV-13 | TP-ENV "Privileged helper isolation" / "cgroup v2 fallback" | Confirms capability isolation and fallback behavior. |
| FR-ENV-14 | TP-ENV "Stale-socket SLA documented" | Confirms the process-memory-only SLA is documented in status/report output. |

### FR-GATE

| ID | Covered By | Notes |
|----|-----------|-------|
| FR-GATE-01 | — | NOT COVERED. No test checks loopback-only binding. |
| FR-GATE-02 | TP-GATE "Single residency enforced" | Confirms a second load fully unloads the first first. |
| FR-GATE-03 | — | NOT COVERED. TP-RESOURCE's "E-core thread cap" test verifies the E-core side (NFR-RES-05) only, not P-core inference-thread pinning itself. |
| FR-GATE-04 | — | NOT COVERED. No test exercises the actual GPU→CPU fallback behavior (only its precondition, the benchmark, is tested under FR-PRE-08). |
| FR-GATE-05 | — | NOT COVERED. No test verifies the teardown-freed-memory check itself (distinct from the settle-poll gate tested under FR-GATE-10). |
| FR-GATE-06 | TP-COUNCIL2 "No swap during active loop" | Uses `model_invocation_logs` contents as its evidence source. |
| FR-GATE-07 | — | NOT COVERED. No test checks per-model context ceilings or truncation behavior. |
| FR-GATE-08 | TP-GATE "Engine crash recovery" | Fault-injection test confirms one restart, then `PAUSED` escalation. |
| FR-GATE-09 | TP-GATE "Single residency enforced" | Explicitly named alongside FR-GATE-02. |
| FR-GATE-10 | TP-GATE "Memory-settle gate" | Confirms the bounded `MemAvailable` poll and its 5s degraded-alert path. |

### FR-TOOL

| ID | Covered By | Notes |
|----|-----------|-------|
| FR-TOOL-01 | — | NOT COVERED. No test checks Tier 1 wrapper existence/schema declaration for all 11 tools. |
| FR-TOOL-02 | — | NOT COVERED. No test checks machine-readable flag/forbidden-combination declarations. |
| FR-TOOL-03 | TP-TIER2 "Path resolution" / "Unaffected tools still autonomous" | Path-restricted allowlist behavior exercised directly. |
| FR-TOOL-04 | — | NOT COVERED. No test explicitly asserts `shell=False`/non-shell execution as its own pass criterion. |
| FR-TOOL-04a | TP-KILL "Spawn uses new session" / "Process-group kill (no orphans)" | Both the mechanism and its purpose (no orphans) are tested. |
| FR-TOOL-05 | — | NOT COVERED. No dedicated test targets the tiered-timeout-enforcement mechanism itself (see also IR-TOOL-03). |
| FR-TOOL-06 | TP-TIER2 "Behavioral denylist (a)-(e)" | One sub-test per denylist category (a)-(e). |
| FR-TOOL-06a | TP-TIER2 "High-risk category refusal" / "Opt-in flag enables category" | Both the default-refused and flag-enabled paths are tested. |
| FR-TOOL-06b | TP-TIER2 "High-risk category refusal" | Confirms `POLICY_REFUSED` + reason + no-pause continuation. |
| FR-TOOL-06c | TP-TIER2 "Opt-in flag enables category" / "Flag change is forward-only" | Both the `resume`-time update and forward-only semantics are tested. |
| FR-TOOL-07 | — | NOT COVERED. No test checks the sanitization pipeline's structured-signal extraction. |
| FR-TOOL-08 | — | NOT COVERED. No test checks that full raw output is persisted regardless of what's summarized. |
| FR-TOOL-09 | TP-LOOP "Rate limit enforced, not rejected" | Test's pass criterion directly reads `tool_execution_logs` argv/timestamps. |
| FR-TOOL-10 | — | NOT COVERED (Should-priority; no test exists). |
| FR-TOOL-11 | — | NOT COVERED. No test checks the env-var override mechanism for third-party frameworks. |
| FR-TOOL-12 | TP-INJECT "Tag integrity under adversarial input" | Confirms the provenance-tag wrapping and its escape-forgery defense. |
| FR-TOOL-13 | TP-INJECT "Heuristic detector logging" | Confirms the flag is set and surfaced, without itself blocking. |
| FR-TOOL-14 | TP-LOOP rate-limit test group (3 rows) | Both speed tiers and per-target isolation are tested. |

### FR-COUNCIL

| ID | Covered By | Notes |
|----|-----------|-------|
| FR-COUNCIL-01 | — | NOT COVERED. No test checks Strategist task-queue production. |
| FR-COUNCIL-02 | — | NOT COVERED. No test checks the plan's structured (non-prose-only) shape. |
| FR-COUNCIL-03 | TP-GATE "Single residency enforced" | Same single-residency mechanism as FR-GATE-02/09. |
| FR-COUNCIL-03a | TP-COUNCIL1 "Deterministic pre-check blocks out-of-scope CIDR" | Confirms the Python pre-check runs and blocks before any LLM call. |
| FR-COUNCIL-04 | TP-COUNCIL1 "Semantic gate reasoning" | Confirms the LLM tier's contextual rejection and rationale. |
| FR-COUNCIL-05 | TP-COUNCIL1 "Semantic gate reasoning" | Same test; confirms rationale persistence. |
| FR-COUNCIL-06 | TP-COUNCIL1 "Non-bypassability" | Confirms no flag/config bypasses a Gate 1 rejection. |
| FR-COUNCIL-07 | TP-COUNCIL2 "No swap during active loop" / TP-TIER2 "Operator sees current flag state" | Residency + flag-visibility both tested. |
| FR-COUNCIL-08 | TP-COUNCIL2 "Deterministic validator rejects malformed command" | Confirms sub-second, model-free rejection with a specific reason. |
| FR-COUNCIL-09 | TP-COUNCIL2 "Correction attempts bound" | Confirms `BLOCKED` on the 4th failure after 3 attempts. |
| FR-COUNCIL-09a | TP-COUNCIL2 "Offline 3B fallback" | Confirms 3B is invoked only between-phases, not inline. |
| FR-COUNCIL-10 | — | NOT COVERED. No test checks follow-on task generation into `task_queue`. |
| FR-COUNCIL-11 | TP-LOOP "Per-target task cap" / "Global 12-hour budget" / "Manual pause still works" | All three thresholds and the manual-pause carve-out are tested. |
| FR-COUNCIL-11a | TP-LOOP "Zero-yield circuit breaker" / "Noisy-tool false-reset prevented" | State-delta yield definition directly exercised. |
| FR-COUNCIL-11b | TP-LOOP "Failure breaker independent of yield breaker" / "...don't cross-contaminate" | Independent counter behavior tested. |
| FR-COUNCIL-12 | — | NOT COVERED. No test targets the whole-engagement (not per-task) Operator-unload timing condition specifically. |
| FR-COUNCIL-13 | TP-COUNCIL3 (all 6 rows) | Every row exercises a CONFIRMED/DISMISSED adjudication decision. |
| FR-COUNCIL-14 | — | NOT COVERED. TP-COUNCIL3's rows all target the 14a-specific checks (impact/identity/baseline-diff); no row targets the base WAF/rate-limit/5xx/honeypot pattern checks specifically. |
| FR-COUNCIL-14a | TP-COUNCIL3 (all 6 rows) | Impact, identity/cross-identity, and baseline/attack/diff sub-checks each have a dedicated row. |
| FR-COUNCIL-15 | TP-REPORT "Per-finding vs. register document type" | Confirms CONFIRMED→VAPT_FINDING, DISMISSED→INFO_REGISTER split. |
| FR-COUNCIL-16 | — | NOT COVERED. No test checks the CWE/CVE/remediation narrative generation itself. |
| FR-COUNCIL-16a | TP-CVSS (all 3 rows) | LLM-never-emits-score, calculator correctness, and version lock all tested. |
| FR-COUNCIL-17 | TP-REPORT "Per-finding vs. register document type" | Same test as FR-COUNCIL-15. |
| FR-COUNCIL-17a | TP-REPORT "Approval triggers unredaction + render" | Confirms HTML/PDF generated only post-approval. |
| FR-COUNCIL-17b | TP-REPORT "Grounding check catches..." / "Grounding retry then block" | Both the detection and the bounded-retry-then-block paths tested. |
| FR-COUNCIL-18 | TP-REPORT "Draft redaction" / "Redaction happens pre-Reporter, not post-scan" / "Paraphrase-proof redaction" | Full pre-Reporter redaction lifecycle tested. |
| FR-CTRL-01 | — | NOT COVERED. No test checks `start`'s "no auth artifact required" behavior directly. |
| FR-CTRL-02 | TP-LOOP "Manual pause still works" | Confirms pause takes effect at the next safe checkpoint. |
| FR-CTRL-03 | TP-TIER2 "Opt-in flag enables category" | `resume` sets a flag on a paused engagement. |
| FR-CTRL-04 | TP-KILL "Kill-switch timing" | Measures wall-clock time to full stop. |
| FR-CTRL-05 | — | NOT COVERED. No test checks the `status` view's field set. |
| FR-CTRL-06 | — | N/A. Requirement removed by confirmed operator decision; no content to test. |
| FR-CTRL-07 | TP-PRE "Operator override path" / TP-INJECT "Heuristic detector logging" | Both confirm export-package visibility of specific audit items. |
| FR-CTRL-08 | TP-REPORT "Approval triggers unredaction + render" / "No other trigger renders" | Sole-trigger property directly tested. |
| FR-CTRL-09 | TP-STRUCTURED "Single-engagement lock" / "Lock releases on completion" | Both the refusal and the release-on-terminal-status paths tested. |

---

## 02 — Non-Functional Requirements

| ID | Covered By | Notes |
|----|-----------|-------|
| NFR-RES-01 | — | NOT COVERED. No test checks the combined-footprint ≤13.0 GiB ceiling. |
| NFR-RES-02 | TP-RESOURCE "RAM margin abort" / TP-GATE "Memory-settle gate" | Margin-breach abort and settle-poll both exercise this threshold. |
| NFR-RES-03 | — | NOT COVERED. No test checks the no-tmpfs-writes policy. |
| NFR-RES-04 | TP-RESOURCE "Disk thresholds" | Confirms 85% warn / 95% hard-block. |
| NFR-RES-05 | TP-RESOURCE "E-core thread cap" | Confirms CPU-affinity constraint to 4 threads. |
| NFR-RES-06 | — | NOT COVERED. No test checks cumulative swap-write tracking. |
| NFR-PERF-01 | — | N/A. Superseded/historical only per its own text — no longer a binding requirement to test. |
| NFR-PERF-02 | TP-GATE "Model-swap budget" | Times an unload→load cycle against the 60s budget. |
| NFR-PERF-03 | — | NOT COVERED. No dedicated test targets the 180s-default non-blocking behavior itself. |
| NFR-PERF-05 | TP-LOOP "Global 12-hour budget" | Confirms auto-transition to Phase 4.3 at the budget mark. |
| NFR-REL-01 | — | NOT COVERED. No test cites the per-step-durability guarantee as its own pass criterion. |
| NFR-REL-02 | — | NOT COVERED. No test checks resumability after unclean termination. |
| NFR-REL-03 | — | NOT COVERED. No test checks cross-model failure isolation. |
| NFR-REL-04 | TP-KILL "Kill-switch timing" | Same 20-second budget measurement as FR-CTRL-04. |
| NFR-REL-05 | — | NOT COVERED (Should-level; no test exists). |
| NFR-REL-06 | — | NOT COVERED. TP-ENV's "Resource-table framing" test targets the C-02/§4-figures framing note, not this NFR's best-effort-hibernation wording specifically. |
| NFR-SEC-01 | — | NOT COVERED. No test checks loopback-only endpoint binding. |
| NFR-SEC-02 | — | NOT COVERED. No test checks the no-data-leaves-host guarantee directly. |
| NFR-SEC-03 | TP-ENV "Privileged helper isolation" | Confirms the main process holds no elevated capability. |
| NFR-SEC-04 | — | NOT COVERED. No test cites this ID's "auditable without re-running" property as its own pass criterion. |
| NFR-USE-01 | — | NOT COVERED. |
| NFR-USE-02 | — | NOT COVERED. |
| NFR-USE-03 | — | NOT COVERED. |
| NFR-MAINT-01 | — | NOT COVERED. |
| NFR-MAINT-02 | — | NOT COVERED. |
| NFR-MAINT-03 | — | NOT COVERED. |
| NFR-PORT-01 | — | NOT COVERED. |
| NFR-PORT-02 | — | NOT COVERED. |
| NFR-COMPLIANCE-01 | TP-COUNCIL1 "Non-bypassability" | Same non-overridable scope-check mechanism as FR-COUNCIL-06. |

---

## 03 — Data & Storage Requirements

| ID | Covered By | Notes |
|----|-----------|-------|
| DR-SCHEMA-01 | TP-STRUCTURED "Single-engagement lock" | `engagement_lock_slot`/unique-index behavior directly tested. |
| DR-SCHEMA-01a | TP-TIER2 "Opt-in flag enables category" | Confirms a flag-history row is recorded on change. |
| DR-SCHEMA-02 | TP-LOOP (cap/breaker tests) / TP-MULTI "Independent per-target counters" | Per-target counter columns exercised throughout. |
| DR-SCHEMA-03 | TP-COUNCIL1 (both scope-gate tests) | `scope_rules` rows are what the gate reads. |
| DR-SCHEMA-04 | — | NOT COVERED. No test cites `attack_paths` rows directly. |
| DR-SCHEMA-05 | — | NOT COVERED. No test cites the `task_queue` schema/status-value set as its own pass criterion. |
| DR-SCHEMA-06 | TP-LOOP "Rate limit enforced, not rejected" | Uses `tool_execution_logs` argv/timestamps as evidence. |
| DR-SCHEMA-07 | TP-CVSS "Version lock" | Confirms `cvss_version` hardcoded to `3.1`. |
| DR-SCHEMA-08 | TP-COUNCIL2 "No swap during active loop" | Uses `model_invocation_logs` as evidence. |
| DR-SCHEMA-09 | TP-PRE "GPU offload benchmark" | Confirms the benchmark result is recorded here. |
| DR-SCHEMA-10 | TP-MULTI "Artifact isolation" | Confirms per-target artifact subtree structure. |
| DR-SCHEMA-11 | TP-REPORT "Per-finding vs. register document type" | `document_type`/`finding_id` distinction directly tested. |
| DR-SCHEMA-12 | TP-LOOP "Zero-yield circuit breaker" | `discovered_entities` state-delta mechanism directly tested. |
| DR-SCHEMA-13 | — | NOT COVERED. No test cites `suspended_processes` rows by name (TP-ENV tests the oom-score/casualty behavior, not this table). |
| DR-SCHEMA-14 | TP-RESOURCE "Redaction hash verification" / "...round-trip on duplicate tokens" | Byte-offset + hash addressing directly tested. |
| DR-CONCURRENCY-01 | TP-RESOURCE "WAL mode" | Confirms WAL pragma + concurrent-read success. |
| DR-CONCURRENCY-02 | — | NOT COVERED. No test checks per-step (non-batched) commit behavior. |
| DR-CONCURRENCY-03 | TP-RESOURCE "Busy-timeout under contention" | Confirms 5s busy-timeout retry behavior. |
| DR-ARTIFACT-01 | TP-MULTI "Artifact isolation" | Same test as DR-SCHEMA-10. |
| DR-ARTIFACT-02 | — | NOT COVERED. No test checks raw-output naming/write-before-sanitization. |
| DR-ARTIFACT-03 | TP-REPORT "Approval triggers unredaction + render" | Confirms pending/approved directory separation. |
| DR-ARTIFACT-04 | — | NOT COVERED. No test checks intermediate-HTML retention alongside the PDF. |
| DR-RETENTION-01 | — | NOT COVERED. No test cites this ID directly (NFR-RES-04's own test doesn't name this ID). |
| DR-RETENTION-02 | — | NOT COVERED. No test checks non-deletion of `DISMISSED`-finding raw output. |
| DR-RETENTION-03 | — | NOT COVERED. Documentation/policy statement; no test. |
| DR-BACKUP-01 | TP-BACKUP "Backup existence gates Phase 5 completion" | Directly tested. |
| DR-BACKUP-02 | — | NOT COVERED. No test checks the local-only-backup constraint (absence of remote backup is not itself asserted anywhere). |

---

## 04 — Interface & Integration Requirements

| ID | Covered By | Notes |
|----|-----------|-------|
| IR-ENGINE-01 | TP-GATE "Backend swap feasibility" | Analysis-level code check for engine-agnostic orchestration. |
| IR-ENGINE-02 | TP-GATE "Single residency enforced" | Spawn/terminate lifecycle exercised by the same test. |
| IR-ENGINE-03 | TP-GATE "Single residency enforced" | Explicitly named (`waitpid`-verified exit). |
| IR-ENGINE-04 | TP-GATE "Backend swap feasibility" | Same analysis as IR-ENGINE-01. |
| IR-ENGINE-05 | — | NOT COVERED. No test checks the OpenAI-compatible contract remaining stable across backends. |
| IR-ENGINE-06 | TP-GATE "Memory-settle gate" | Same mechanism as FR-GATE-10. |
| IR-STRUCTURED-01 | TP-STRUCTURED "`response_format` requested" | Code-level inspection across all 6 roles. |
| IR-STRUCTURED-02 | TP-STRUCTURED "Schema validation catches conformance gaps" | Confirms validator catches valid-JSON-but-wrong-shape output. |
| IR-STRUCTURED-03 | TP-STRUCTURED "Bounded retry with error feedback" | Confirms 2-retry/3-attempt bound with error feedback. |
| IR-STRUCTURED-04 | — | NOT COVERED. No test checks that schemas are maintained as standalone declarative files. |
| IR-TOOL-01 | — | NOT COVERED. No test checks the declarative schema-file existence per Tier 1 tool. |
| IR-TOOL-02 | — | NOT COVERED. No test checks the shared-source-of-truth property between Operator schema and Gate 2 validator. |
| IR-TOOL-03 | — | NOT COVERED. No dedicated test targets the tiered timeout classes or the non-blocking-streaming requirement. |
| IR-BRIDGE-01 | — | NOT COVERED. No test checks the structured-call (never raw-shell-string) contract directly. |
| IR-BRIDGE-02 | TP-TIER2 "Path resolution" | Confirms symlink-resolution-outside-allowlist is refused. |
| IR-BRIDGE-03 | — | NOT COVERED. No test asserts the denylist-before-spawn (never post-hoc) ordering as its own pass criterion. |
| IR-BRIDGE-04 | TP-TIER2 "Behavioral denylist (a)-(e)" | Confirms the matching rule is logged even on rejection. |
| IR-BRIDGE-05 | TP-LOOP rate-limit test group | Same tests as FR-TOOL-14. |
| IR-BRIDGE-06 | TP-LOOP "Failure breaker independent of yield breaker" | `network_error` classification directly exercised. |
| IR-GROUND-01 | TP-REPORT "Grounding check catches an ungrounded reference" | Directly tested. |
| IR-GROUND-02 | TP-REPORT "Grounding retry then block" | Directly tested. |
| IR-GROUND-03 | TP-REPORT "Grounding applies only to VAPT_FINDING reports" | Directly tested (Inspection). |
| IR-SANITIZE-01 | — | NOT COVERED. No test checks the pluggable-parser structure itself. |
| IR-SANITIZE-02 | TP-INJECT "Tag integrity under adversarial input" | Same test as FR-TOOL-12. |
| IR-SANITIZE-03 | TP-INJECT "Instruction-hierarchy clause presence" | Directly tested (Inspection). |
| IR-MCP-01 | — | NOT COVERED (Should-level; no test exists). |
| IR-MCP-02 | — | NOT COVERED. |
| IR-EXT-01 | — | NOT COVERED. No test checks the env-var-only integration contract. |
| IR-EXT-02 | — | NOT COVERED. No test checks council-lifecycle functioning with zero third-party integrations installed. |
| IR-CTRL-01 | — | NOT COVERED. No test checks the full one-subcommand-per-action, non-interactive-friendly surface. |
| IR-CTRL-02 | — | NOT COVERED. No test checks the human/`--json` dual-output requirement. |
| IR-CTRL-03 | TP-STRUCTURED "Single-engagement lock" | Exercises `start`'s lock-check precondition. |
| IR-CTRL-04 | TP-KILL "Kill-switch timing" | Exercises `abort`'s fast-invocation property. |
| IR-CTRL-05 | — | NOT COVERED. TP-TIER2's flag test exercises setting a flag via `resume`, but not the "omitting a flag leaves it unchanged" half of this requirement. |

---

## 05 — Security, Safety & Compliance Requirements

| ID | Covered By | Notes |
|----|-----------|-------|
| SEC-SCOPE-01 | TP-COUNCIL1 "Deterministic pre-check..." / "Semantic gate reasoning" | Same mechanism as FR-COUNCIL-03a/04. |
| SEC-SCOPE-02 | TP-COUNCIL1 "Non-bypassability" | Same mechanism as FR-COUNCIL-06. |
| SEC-SCOPE-03 | — | NOT COVERED. This is a documented dependency-chain acknowledgment, not an independently testable behavior. |
| SEC-CONTAIN-01 | — | NOT COVERED. Same gap as FR-TOOL-04 — no test cites non-shell execution as its own pass criterion. |
| SEC-CONTAIN-02 | — | NOT COVERED. Policy/framing statement (residual-risk acceptance), not independently testable. |
| SEC-CONTAIN-03 | TP-ENV "Privileged helper isolation" | Confirms dedicated least-privileged account, no blanket root. |
| SEC-CONTAIN-04 | — | NOT COVERED. Same gap as FR-TOOL-05/IR-TOOL-03 — no dedicated timeout-enforcement test. |
| SEC-CONTAIN-05 | TP-ENV "Privileged helper isolation" / "cgroup v2 fallback" | Same tests as FR-ENV-13. |
| SEC-PROMPT-01 | TP-INJECT "Tag integrity under adversarial input" | Same test as FR-TOOL-12/IR-SANITIZE-02. |
| SEC-PROMPT-02 | TP-INJECT "Instruction-hierarchy clause presence" | Same test as IR-SANITIZE-03. |
| SEC-PROMPT-03 | — | NOT COVERED. Framing statement (detection ≠ containment), not independently testable. |
| SEC-PROMPT-04 | TP-INJECT "Heuristic detector logging" | Same test as FR-TOOL-13. |
| SEC-KILL-01 | TP-KILL "Process-group kill (no orphans)" | Directly tested. |
| SEC-KILL-02 | TP-KILL "Escalation" | Confirms `SIGTERM`→`SIGKILL` escalation within budget. |
| SEC-KILL-03 | TP-KILL "Kill-switch timing" | Confirms atomic `ABORTED` marking. |
| SEC-AUDIT-01 | — | NOT COVERED. No single test cites this ID's "reconstructable from logs alone" property as its own pass criterion. |
| SEC-AUDIT-02 | TP-PRE "Operator override path" | Export-package readability confirmed via a specific item, not this ID generically. |
| SEC-AUDIT-03 | — | NOT COVERED. No test checks append-only/non-mutation behavior. |
| SEC-DATA-01 | — | NOT COVERED. No test checks the no-data-leaves-host guarantee. |
| SEC-DATA-02 | TP-REPORT redaction test group | Full redact→restore lifecycle tested. |
| SEC-DATA-03 | — | NOT COVERED. No test checks loopback-bound-by-default. |

---

## 06 — Operational Requirements

| ID | Covered By | Notes |
|----|-----------|-------|
| OPS-LIFECYCLE-01 | — | NOT COVERED. No test checks the mandated phase sequence or per-phase `engagement_phase_log` entries as its own pass criterion. |
| OPS-LIFECYCLE-02 | — | NOT COVERED. No test checks `resume`'s correct-phase re-entry or hibernation-skip-on-resume logic. |
| OPS-LIFECYCLE-03 | TP-KILL "Abort still restores apps" | Directly tested. |
| OPS-LIFECYCLE-04 | — | NOT COVERED. Documentation/framing clarification, not independently testable. |
| OPS-MONITOR-01 | — | NOT COVERED. No single test cites this aggregating ID; its individual sub-metrics are covered under NFR-RES-02/04, NFR-PERF-05, and DR-SCHEMA-02 above. |
| OPS-MONITOR-02 | TP-RESOURCE "RAM margin abort" / "Disk thresholds" | Both trigger conditions tested. |
| OPS-MONITOR-03 | TP-FEASIBILITY "Thermal/throttle telemetry availability" | A feasibility check, not a pass/fail test — but explicitly tracked. |
| OPS-MONITOR-04 | — | NOT COVERED. No test checks that `status` reflects live (not stale) state mid-session. |
| OPS-LOG-01 | — | NOT COVERED. |
| OPS-LOG-02 | — | NOT COVERED. |
| OPS-LOG-03 | — | NOT COVERED. No test checks the distinguishable-severity requirement for degraded events. |
| OPS-MAINT-01 | — | N/A. Explicitly deferred/out-of-scope for this planning phase — no automatic mechanism to test. |
| OPS-MAINT-02 | — | NOT COVERED (Should-level; no test exists). |
| OPS-MAINT-03 | — | NOT COVERED (Should-level; no test exists). |
| OPS-DEGRADE (table) | — | N/A. A reference/summary table aggregating other requirements — coverage follows each constituent ID (FR-GATE-04, NFR-PERF-02, FR-ENV-11/12/13/14, FR-TOOL-13, OPS-MONITOR-03, NFR-RES-02/04, FR-COUNCIL-11/11a, NFR-PERF-05, FR-GATE-10/IR-ENGINE-06), already assessed above. |

---

## 07 — Risk Register

Every `RISK-*` entry is **N/A (not testable)**: a risk-register row records likelihood,
impact, and mitigation status — it is not itself a system behavior with a pass/fail
outcome. The testable unit is the mitigating requirement each row already cites; that
requirement's own coverage is assessed under its own ID earlier in this matrix (§01-06).
Listed here for completeness, with the ID(s) whose coverage above governs it:

| ID | Governing Requirement(s) (see coverage above) |
|----|-----------|
| RISK-MEMEXHAUST | NFR-RES-02 (Covered), OPS-MONITOR-01/02 (mixed), FR-GATE-10/IR-ENGINE-06 (Covered) |
| RISK-OOMKILL | FR-ENV-11/12/13 (Covered) |
| RISK-THERMAL | OPS-MONITOR-03 (feasibility-check only) |
| RISK-GPUOFFLOAD | FR-GATE-04 (NOT COVERED) |
| RISK-PROMPTINJECT | FR-TOOL-12/13, IR-SANITIZE, SEC-PROMPT (mostly Covered) |
| RISK-UNCENSOREDGATE | FR-COUNCIL-03a/04 (Covered) |
| RISK-CVSSACCURACY | FR-COUNCIL-16a (Covered) |
| RISK-TIER2RESIDUAL | FR-TOOL-06a (Covered), SEC-CONTAIN-02 (NOT COVERED, framing-only) |
| RISK-UNBOUNDEDAUTONOMY | None — residual/accepted by explicit decision, not mitigated |
| RISK-ENGINEAMBIGUITY | IR-ENGINE-01..06 (mostly Covered) |
| RISK-SWAPWEAR | NFR-REL-05 (NOT COVERED, Should-level) |
| RISK-DBLOCKCONTENTION | DR-CONCURRENCY-01 (Covered) |
| RISK-LOGVOLUME | NFR-RES-04 (Covered), OPS-LOG-02/DR-RETENTION-01 (NOT COVERED) |
| RISK-FALSEPOSITIVE | FR-COUNCIL-14 (NOT COVERED) |
| RISK-TOOLDECAY | None — explicitly deferred (OPS-MAINT-01) |
| RISK-CORPUSDRIFT | `12-Report-Formatting-Rules.md` (procedural, outside this matrix's document set) |
| RISK-CROSSMACHINE | None — open, operator action required |
| RISK-NOMODELFILES | AC-DEPENDENCY-09 (N/A, open) |
| RISK-MADVISEPERM | FR-ENV-13 (Covered) |
| RISK-STALESOCKETS | FR-ENV-14 (Covered) |
| RISK-NOISYYIELD | FR-COUNCIL-11a/DR-SCHEMA-12 (Covered) |
| RISK-MEMSETTLERACE | FR-GATE-10/IR-ENGINE-06 (Covered) |
| RISK-ORPHANPROC | FR-TOOL-04a/SEC-KILL-01/02 (Covered) |
| RISK-DBLOCKED | DR-CONCURRENCY-03 (Covered) |
| RISK-REDACTMISMATCH | DR-SCHEMA-14 (Covered) |
| RISK-STRUCTOUTPUT | IR-STRUCTURED (Covered) |
| RISK-STALEREDACT | FR-COUNCIL-18 (Covered) |
| RISK-OPERATORWASTE | FR-COUNCIL-07 (Covered) |
| RISK-REPORTSCHEMA | DR-SCHEMA-11 (Covered) |
| RISK-UNGROUNDEDREPORT | IR-GROUND-01..03 (Covered) |
| RISK-DEADTARGETWASTE | FR-COUNCIL-11b (Covered) |
| RISK-NORATELIMIT | FR-TOOL-14/IR-BRIDGE-05 (Covered) |
| RISK-CONTEXTGROWTH | None — genuinely open (Open Item H) |

---

## 08 — Assumptions, Constraints, Dependencies & Non-Goals

Every ID in this document is **N/A (not testable)**: assumptions, hard constraints,
external dependencies, and non-goals describe the boundary conditions the requirements
operate under — they are not themselves testable system behaviors. Where a constraint
has a corresponding testable requirement, that requirement is already assessed above
(e.g. `AC-CONSTRAINT-04`'s thresholds are the same numbers tested under `FR-COUNCIL-11`
in §01).

| ID range | Count | Status |
|----|----|----|
| AC-ASSUME-01 .. 06 | 6 | N/A |
| AC-CONSTRAINT-01 .. 05 | 5 | N/A |
| AC-DEPENDENCY-01 .. 10 | 10 | N/A |
| AC-NONGOAL-01 .. 07 | 7 | N/A |

---

## 11 — Critical Analysis and Design Challenges

Each `C-*` finding was resolved into one or more requirements elsewhere in `01`-`13`;
the finding ID itself is not directly tested — its **resolution requirement's** test
coverage (already assessed above) is what answers "was this finding actually closed."

| ID | Covered By | Notes |
|----|-----------|-------|
| C-01 | TP-ENV "OOM protection applied" / "OOM casualty detection" | Resolution: FR-ENV-11/12/13. |
| C-02 | TP-ENV "Resource-table framing" | Resolution: `02`'s framing note (Inspection). |
| C-03 | TP-COUNCIL1 (both scope-gate tests) | Resolution: FR-COUNCIL-03a/04. |
| C-04 | TP-INJECT (all 3 rows) / TP-COUNCIL1 "Prompt-injection resistance (spot check)" | Resolution: FR-TOOL-12/13, IR-SANITIZE, SEC-PROMPT. |
| C-05 | TP-PRE "GPU offload benchmark" | Resolution: FR-PRE-08. Partial: TP-FEASIBILITY separately flags sustained-load SYCL stability as still unverified. |
| C-06 | TP-FEASIBILITY "`i915` vs `xe` actual driver binding" | Resolution: documentation-only, explicitly non-blocking. |
| C-07 | TP-CVSS (all 3 rows) | Resolution: FR-COUNCIL-16a. |
| C-08 | — | NOT COVERED. Resolution (IR-TOOL-03 tiered timeouts) itself has no dedicated `TP-*` row (see §04). |
| C-09 | TP-COUNCIL2 (all 4 rows) | Resolution: FR-COUNCIL-07/08/09a. |
| C-10 | TP-FEASIBILITY "Thermal/throttle telemetry availability" | Resolution: OPS-MONITOR-03, itself a feasibility check. |
| C-11 | 09 "Acceptance Boundary Statement" | Explicitly cites C-11 by name. |
| C-12 | TP-TIER2 (multiple rows) | Resolution: FR-TOOL-03/06. |
| C-13 | TP-GATE "Backend swap feasibility" | Resolution: IR-ENGINE-01..05. |
| C-14 | TP-TIER2 "High-risk category refusal" / "Opt-in flag enables category" | Resolution: FR-TOOL-06a. |
| C-15 | TP-ENV "Privileged helper isolation" / "cgroup v2 fallback" | Resolution: FR-ENV-13/SEC-CONTAIN-05. |
| C-16 | TP-ENV "Stale-socket SLA documented" | Resolution: FR-ENV-14. |
| C-17 | TP-LOOP "Zero-yield circuit breaker" / "Noisy-tool false-reset prevented" | Resolution: FR-COUNCIL-11a/DR-SCHEMA-12. |
| C-18 | TP-GATE "Memory-settle gate" | Resolution: FR-GATE-10/IR-ENGINE-06. |
| C-19 | TP-KILL "Process-group kill (no orphans)" | Resolution: FR-TOOL-04a/SEC-KILL-01. |
| C-20 | TP-RESOURCE "Busy-timeout under contention" | Resolution: DR-CONCURRENCY-03. |
| C-21 | TP-RESOURCE "Redaction hash verification" / "...duplicate tokens" | Resolution: DR-SCHEMA-14 (revised). |
| C-22 | TP-STRUCTURED (all rows) | Resolution: IR-STRUCTURED. |
| C-23 | TP-REPORT "Redaction happens pre-Reporter, not post-scan" / "Paraphrase-proof redaction" | Resolution: FR-COUNCIL-18 (revised). |
| C-24 | TP-TIER2 "Operator sees current flag state" | Resolution: FR-COUNCIL-07 (revised). |
| C-25 | TP-REPORT "Per-finding vs. register document type" / "INFO_REGISTER regenerates, doesn't multiply" | Resolution: DR-SCHEMA-11/FR-COUNCIL-17. |
| C-26 | TP-REPORT "Grounding check catches..." / "Grounding retry then block" | Resolution: FR-COUNCIL-17b/IR-GROUND. |
| C-27 | TP-LOOP "Failure breaker independent of yield breaker" / "...don't cross-contaminate" | Resolution: FR-COUNCIL-11b/IR-BRIDGE-06. |
| C-28 | TP-LOOP rate-limit test group | Resolution: FR-TOOL-14/IR-BRIDGE-05. |
| C-29 | — | NOT COVERED. Genuinely open (no resolution requirement exists yet to test — Open Item H). |

---

## 13 — Implementation Architecture Bridge

| ID | Covered By | Notes |
|----|-----------|-------|
| IAB-PROC | TP-LOOP "Manual pause still works" / TP-KILL ("Kill-switch timing", "Process-group kill") / TP-STRUCTURED "Single-engagement lock" | The `pause`/`abort`/`start`-lock mechanisms it describes are each exercised by these tests; `resume`'s mechanism is exercised by TP-TIER2 "Opt-in flag enables category." |
| IAB-SCHEMA-01 | — | NOT COVERED. No test exercises `orchestrator_pid`/`control_intent` columns directly (distinct from `engagement_lock_slot`, which IS tested under DR-SCHEMA-01). |
| IAB-SCHEMA-02 | TP-KILL "Kill-switch timing" / "Process-group kill" | `abort`'s reliance on the `pid` column (`end_ts IS NULL AND pid IS NOT NULL`) is exercised by finding the running subprocess to kill. |
| IAB-SCHEMA-03 | — | NOT COVERED. Same gap as DR-SCHEMA-13 — no test cites `suspended_processes` rows by name. |
| IAB-SCHEMA-04 | TP-RESOURCE "Redaction hash verification" / "...duplicate tokens" | Same tests as DR-SCHEMA-14. |
| IAB-LANG | — | N/A. Language/runtime baseline choice, not an independently testable behavior. |
| IAB-FILES | — | NOT COVERED. No test explicitly checks YAML scope-rules/config-file parsing or the documented config defaults. |
| IAB-HELPER | TP-ENV "Privileged helper isolation" / "cgroup v2 fallback" | Exercises the helper's capability-unavailable fallback path (exit-code-13 semantics). |
| IAB-CLI | — | NOT COVERED. The CLI framework/naming choice itself is not testable; the command surface it exposes is the same gap already noted under IR-CTRL-01 (§04). |
| IAB-LAYOUT | — | N/A. Proposed module layout is an organizational artifact, not a testable behavior. |

---

## Summary

| Document | Total IDs | Covered | N/A | NOT COVERED |
|---|---|---|---|---|
| 01 — Functional Requirements | 90 | 53 | 1 | 36 |
| 02 — Non-Functional Requirements | 29 | 8 | 1 | 20 |
| 03 — Data & Storage Requirements | 27 | 17 | 0 | 10 |
| 04 — Interface & Integration Requirements | 34 | 19 | 0 | 15 |
| 05 — Security, Safety & Compliance Requirements | 21 | 12 | 0 | 9 |
| 06 — Operational Requirements | 15 | 3 | 2 | 10 |
| 07 — Risk Register | 33 | 0 | 33 | 0 |
| 08 — Assumptions, Constraints, Dependencies & Non-Goals | 28 | 0 | 28 | 0 |
| 11 — Critical Analysis and Design Challenges | 29 | 27 | 0 | 2 |
| 13 — Implementation Architecture Bridge | 10 | 4 | 2 | 4 |
| **Total** | **316** | **143** | **67** | **106** |

**Reading this table correctly:** the 106 `NOT COVERED` items are not 106 bugs in `09`
— that document explicitly scopes itself to representative test *clusters*, not an
exhaustive per-ID enumeration, and most gaps above are genuinely low-level MUSTs
(env-var overrides, structured-log formats, declarative-schema-file existence,
individual table-row logging) that a real test suite would naturally cover as a
byproduct of testing the higher-level behavior around them, without needing a
named row of their own. The list below is the material subset worth a second look
before or during implementation — genuine behavioral gaps, not paperwork gaps:

**Every `NOT COVERED` item, listed explicitly:**

*01 — FR-PRE-01, FR-PRE-02, FR-PRE-05, FR-PRE-06; FR-ENV-01, FR-ENV-02, FR-ENV-03, FR-ENV-05, FR-ENV-08, FR-ENV-09, FR-ENV-10; FR-GATE-01, FR-GATE-03, FR-GATE-04, FR-GATE-05, FR-GATE-07; FR-TOOL-01, FR-TOOL-02, FR-TOOL-04, FR-TOOL-05, FR-TOOL-07, FR-TOOL-08, FR-TOOL-10, FR-TOOL-11; FR-COUNCIL-01, FR-COUNCIL-02, FR-COUNCIL-10, FR-COUNCIL-12, FR-COUNCIL-14, FR-COUNCIL-16; FR-HIB-01, FR-HIB-02, FR-HIB-04, FR-HIB-05; FR-CTRL-01, FR-CTRL-05.*

*02 — NFR-RES-01, NFR-RES-03, NFR-RES-06; NFR-PERF-03; NFR-REL-01, NFR-REL-02, NFR-REL-03, NFR-REL-05, NFR-REL-06; NFR-SEC-01, NFR-SEC-02, NFR-SEC-04; NFR-USE-01, NFR-USE-02, NFR-USE-03; NFR-MAINT-01, NFR-MAINT-02, NFR-MAINT-03; NFR-PORT-01, NFR-PORT-02.*

*03 — DR-SCHEMA-04, DR-SCHEMA-05, DR-SCHEMA-13; DR-CONCURRENCY-02; DR-ARTIFACT-02, DR-ARTIFACT-04; DR-RETENTION-01, DR-RETENTION-02, DR-RETENTION-03; DR-BACKUP-02.*

*04 — IR-ENGINE-05; IR-STRUCTURED-04; IR-TOOL-01, IR-TOOL-02, IR-TOOL-03; IR-BRIDGE-01, IR-BRIDGE-03; IR-SANITIZE-01; IR-MCP-01, IR-MCP-02; IR-EXT-01, IR-EXT-02; IR-CTRL-01, IR-CTRL-02, IR-CTRL-05.*

*05 — SEC-SCOPE-03; SEC-CONTAIN-01, SEC-CONTAIN-02, SEC-CONTAIN-04; SEC-PROMPT-03; SEC-AUDIT-01, SEC-AUDIT-03; SEC-DATA-01, SEC-DATA-03.*

*06 — OPS-LIFECYCLE-01, OPS-LIFECYCLE-02, OPS-LIFECYCLE-04; OPS-MONITOR-01, OPS-MONITOR-04; OPS-LOG-01, OPS-LOG-02, OPS-LOG-03; OPS-MAINT-02, OPS-MAINT-03.*

*11 — C-08, C-29.*

*13 — IAB-SCHEMA-01, IAB-SCHEMA-03; IAB-FILES; IAB-CLI.*

**Highest-value gaps to close first (a judgment call, not a formal ranking):**
1. **FR-TOOL-05 / IR-TOOL-03 / SEC-CONTAIN-04** — the tiered-timeout mechanism (Quick
   Probes/Targeted/Deep-Full-Range) has no dedicated test anywhere, despite resolving
   a **High**-severity finding (C-08).
2. **FR-COUNCIL-14** — Gate 3's *base* false-positive-pattern checklist (WAF/rate-limit/
   5xx/honeypot) has no test of its own; only the 14a-specific triage-validation checks
   (impact/identity/baseline-diff) are tested.
3. **NFR-REL-01/02 and FR-ENV-08/09/10 (Phase 1 resumability chain)** — the
   crash-recovery/resume story that OPS-LIFECYCLE-04 explicitly calls out as a
   load-bearing guarantee has no dedicated test anywhere in `09`.
4. **C-29 (context-window growth)** — already known-open; no test can exist until a
   resolution requirement does.

This document adds no new tests and makes no recommendation about whether/when to
close these gaps — that decision belongs with whoever owns `09` next.
