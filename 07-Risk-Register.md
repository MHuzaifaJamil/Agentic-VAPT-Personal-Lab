*(Informational only — this document is an architectural Risk Register documenting technical, operational, and residual trade-offs. It does not constitute an actionable specification or a set of functional requirements, and MUST be skipped by automated code-generation, parser pipelines, and core development processes.)*

# Risk Register — Autonomous Agentic VAPT System

Likelihood/Impact: **L/M/H**. "Status" reflects implemented engineering controls versus
accepted operational trade-offs within the Dual-Mode Execution Architecture. Autonomous
risks are mitigated via strict non-destructive constraints (reads and safe writes only),
rate limits, resource margins, and circuit breakers. Operator-directed risks are accepted
by design, treating the human operator as the sole authority governing authorization,
scope verification, and attack intensity outside the software.

All security invariants, containment mechanisms, and bypass rules cited across these
risks are governed authoritatively by the Security Specification (`05`).

| ID | Risk | L | I | Sev | Mitigation | Status |
|---|---|---|---|---|---|---|
| RISK-MEMEXHAUST | Combined model + subprocess memory exceeds RAM mid-engagement. | M | H | High | Documented RAM safety margin, pause-on-breach monitoring, and a settle-poll gate before each model spawn. | Mitigated |
| RISK-OOMKILL | OOM killer reaps a frozen (`SIGSTOP`) app during the Phase 1 memory spike. | M | H | High | Lowered OOM-kill priority for suspended processes, post-hibernation liveness verification, and a narrow privileged helper for the reclamation step. | Mitigated (best-effort — a casualty is detected and reported, not guaranteed impossible) |
| RISK-THERMAL | Sustained inference load throttles the CPU over a multi-hour session. | M | M | Medium | Deployment-time thermal-telemetry check — contingent on unverified hardware telemetry. | Partially mitigated |
| RISK-GPUOFFLOAD | SYCL/Level-Zero backend is immature for this kernel+driver combo. | M | M | Medium | CPU-only fallback, logged degraded. | Mitigated (degradation, not prevention) |
| RISK-PROMPTINJECT | Target responses containing injection payloads attempt to hijack reasoning flows. | M | M | Medium | Untrusted outputs isolated via boundary tags (`<tool_output_untrusted>`); passive heuristic detection logs anomalies without stalling execution. | Mitigated |
| RISK-UNCENSOREDGATE | Gate 1 semantic tier (`Hermes-3-Llama-3.1-8B`) causes false-positive refusals on valid testing instructions. | L | M | Low | Semantic Tier 1 operates strictly as an advisory steerability guide for autonomous planning; operator-directed commands bypass Tier 1 entirely with zero refusal. | Mitigated |
| RISK-CVSSACCURACY | An 8B model's autonomous CVSS score is inaccurate. | H | M | Med-High | A deterministic calculator computes the final CVSS score; the model proposes per-metric values only. | Mitigated |
| RISK-TIER2RESIDUAL | Path allowlist still permits the full Kali toolset unattended for 12h. | M | H | Med-High | Behavioral denylist plus three-category opt-in flags. | Partially mitigated — residual risk for unlisted tools/enabled categories |
| RISK-UNBOUNDEDAUTONOMY | Autonomous execution causes unintended target disruption during unattended sessions. | L | H | Medium | Autonomous Mode enforces non-destructive testing invariants (prohibiting data drops, schema alters, file wipes, and DoS); legal authorization and RoE remain external operator responsibilities. | Mitigated by Architecture |
| RISK-ENGINEAMBIGUITY | Base plan treated `llama.cpp`/`ollama` as interchangeable (`keep_alive` is Ollama-specific). | H | M | Medium | A Local Engine Client abstraction decouples orchestration code from the specific inference backend. | Mitigated |
| RISK-SWAPWEAR | Daily hibernation cycles accelerate NVMe wear. | L-M | M | Medium | Cumulative swap-write visibility logging, no hard limit. | Partially mitigated (visibility only) |
| RISK-DBLOCKCONTENTION | Default SQLite journal mode blocks concurrent reads during a write. | M | L | Low | SQLite WAL (Write-Ahead Logging) journal mode. | Mitigated |
| RISK-LOGVOLUME | A 12h multi-target session's logs threaten the disk quota. | M | M | Medium | Disk-quota thresholds apply to log volume as well as artifacts, under a documented retention policy. | Mitigated |
| RISK-FALSEPOSITIVE | Automated finding adjudication incorporates false-positive screening checklists (WAF/rate-limit/5xx filters). Borderline or disputed candidates are flagged for human operator review, accepting residual model variance as an operational baseline. | M | M | Medium | Fixed pre-confirmation checklist (WAF/rate-limit/5xx/honeypot rule-outs); no further mitigation — the acceptance criteria do not assume zero false positives. | Partially mitigated — inherent LLM-judgment limit |
| RISK-TOOLDECAY | `nuclei` templates/CVE feeds/wordlists go stale, no update mechanism. | H | M | Medium | None — deferred by explicit decision. | **Deferred** |
| RISK-CORPUSDRIFT | No existing verified report to serve as canonical reference. | M | L | Low | Written rules stand in until a first verified report exists. | Mitigated (procedural) |
| RISK-CROSSMACHINE | This doc set + report-formatting rules were authored on a different machine than the target. | H | M | Medium | None — flagged as a cross-machine transfer assumption requiring operator action. | **Open — operator action required** |
| RISK-NOMODELFILES | Council model `.gguf` acquisition source/provenance never specified. | H | M | Medium | None — flagged as a pre-build dependency. | **Open — before model-acquisition milestone** |
| RISK-MADVISEPERM | `process_madvise` needs a capability the least-privileged agent process doesn't hold. | H | H | High | Narrow single-purpose privileged helper process, cgroup v2 fallback. | Mitigated |
| RISK-STALESOCKETS | Freezing apps 10-12h lapses network/IPC sessions. | H | L-M | Medium | Hibernation SLA reframed to cover process memory only, not network/session continuity. | Mitigated at the SLA level — underlying lapse not preventable |
| RISK-NOISYYIELD | A naive "yield" definition lets noisy tools defeat the circuit breaker. | H | M | Med-High | Class-aware zero-yield counters backed by a state-delta discovery ledger. | Mitigated |
| RISK-MEMSETTLERACE | Spawning the next model immediately after the outbound one exits risks a transient over-allocation. | M | M | Medium | Settle-poll gate before the next model spawn. | Mitigated |
| RISK-ORPHANPROC | A multi-process tool leaves orphans past `abort` if only the parent PID is targeted. | H | H | High | New process-session isolation per subprocess, plus process-group kill on abort. | Mitigated |
| RISK-DBLOCKED | Concurrent `pause`/`abort` writes can raise `database is locked`. | M | H | Med-High | SQLite `busy_timeout`. | Mitigated |
| RISK-REDACTMISMATCH | Regex-based redaction can restore the wrong occurrence of a repeated token. | M | H | High | `redaction_map` exact byte-offset + content-hash addressing. | Mitigated |
| RISK-STRUCTOUTPUT | Quantized models can emit malformed JSON for any LLM-to-code handoff. | H | H | High | Structured-output response mode, a deterministic schema validator, and a bounded retry. | Mitigated |
| RISK-STALEREDACT | Post-hoc scanning an LLM's draft for secrets is fragile (paraphrase evades exact-match). | M | H | High | Redaction moved before the Reporter call — it never sees the real value. | Mitigated |
| RISK-OPERATORWASTE | The Operator can't see opt-in flag state, wastes budget on predictable refusals. | M | L | Low-Med | Flag state surfaced directly in the Operator's own per-task context. | Mitigated |
| RISK-REPORTSCHEMA | `reports` (keyed only by `engagement_id`) couldn't represent per-finding + register. | H | H | High | `finding_id`/`document_type` columns plus a partial unique index. | Mitigated |
| RISK-UNGROUNDEDREPORT | The Reporter can cite a plausible but unverified detail. | M | H | High | Deterministic grounding check on every cited URL/path/hostname. | Mitigated |
| RISK-DEADTARGETWASTE | No failure-specific breaker — an unreachable target only incidentally trips the yield breaker. | M | M | Medium | Separate failure-based circuit breaker with a distinct `UNREACHABLE` status. | Mitigated |
| RISK-NORATELIMIT | Nothing limited Operator spawn rate — DoS-adjacent risk for a 12h unattended run. | M | M-H | Med-High | Per-target spawn-rate limiting. | Mitigated |
| RISK-CONTEXTGROWTH | The resident Operator has no context-window management strategy against its 16k ceiling over a long per-target loop. | M | M | Medium | None — genuinely unresolved. | **Open** |
| RISK-CHECKPOINTBYPASS | Sensitive action classes run unattended without operational visibility. | L | M | Low | Autonomous proposals log structured checkpoint audit events for operator visibility; direct operator commands execute immediately (`approved_via = 'OPERATOR_DIRECTIVE'`) with full audit logging. | Mitigated |
| RISK-EXTDOMAINSCOPE | The four extended domains' authorization models haven't been validated together against a real multi-domain engagement. | M | M | Medium | Each capability domain states its authorization posture explicitly; the public-research domain is read-only. | Partially mitigated |

---

## Risks Governed by Operator-Directed Design

Under the Dual-Mode Architecture, operational flexibility and manual intervention take
precedence during operator-directed execution. **RISK-TIER2RESIDUAL** (execution of unlisted
Kali binaries upon explicit operator command) and **RISK-UNCENSOREDGATE** (elimination of model
refusals on offensive security tasks) are intentional architectural design decisions, not
oversights. Legal authorization, rules of engagement (RoE), and target boundary verification
remain the sole operational responsibility of the human operator outside the tool.

---

## Authority & Conflict Resolution

This register documents technical, operational, and architectural trade-offs across the
system. In the event of any conflict, discrepancy, or ambiguity between risk assessments,
mitigation statuses, and system execution rules, the **Security, Safety & Compliance
Requirements (`05`)** serves as the final and supreme authority across the entire system.
