*(Informational only — this document is an architectural Critical Analysis and adversarial challenge log documenting technical reviews, historical plan corrections, and unresolved limitations. It does not define active requirements or functional specifications, and MUST be skipped by automated code-generation, parser pipelines, and core development processes.)*

# Critical Analysis — Challenges to the Original Plan's Correctness

Adversarial review of the original plan's technical claims. Each finding's
resolution is now a live requirement elsewhere in this corpus — this table records
*that* a finding existed and, in plain language, *how* it was addressed, not the
full original argument (which would duplicate requirement text owned elsewhere).

All security boundaries, containment invariants, and operational execution postures
cited across these resolutions are governed authoritatively by the Security Specification (`05`).

| ID | Area | Severity | How it was addressed |
| --- | --- | --- | --- |
| C-01 | "Zero data loss" hibernation claim overstated — OOM killer can still reap a frozen app | High | OOM-kill priority for suspended processes is set to the least-eligible tier, and every suspended process is independently verified alive post-hibernation; a casualty is reported as a discrepancy, not silently absorbed into a false "success." |
| C-02 | Base doc's memory-reclamation figures treated as guaranteed, not sample-case | Medium | Reframed as a documented resource-budget expectation, backed by a mandatory post-hibernation RAM re-measurement gate rather than a guaranteed figure. |
| C-03 | Gate 1 evaluation structure and refusal handling | High | Reconciled via the Dual-Mode Mandate: in Autonomous Mode, deterministic Tier 0 scope checks guide non-destructive discovery while advisory Tier 1 checks evaluate contextual steerability. For operator-directed commands, both Tier 0 and Tier 1 gates stand down completely, ensuring zero automated refusal on manual instructions. |
| C-04 | No defense against prompt injection via scanned target content | High | All target-derived content is wrapped in reserved boundary tags (`<tool_output_untrusted>`) before model ingestion, paired with passive heuristic injection logging that records anomalies without interrupting pipeline continuity. |
| C-05 | iGPU/SYCL backend maturity presented as settled | Medium | A one-time relative GPU-offload-vs-CPU-only benchmark runs before committing the whole engagement to GPU acceleration. |
| C-06 | Driver co-activity claim unverified | Low | Left as a documentation caveat only — the relative benchmark above surfaces a non-working acceleration path regardless of which driver binds. |
| C-07 | Autonomous CVSS scoring by an 8B model isn't verifiable as accurate | High | The model proposes per-metric values only; a deterministic calculator computes the final score — the model never emits a final number. |
| C-08 | Flat single timeout doesn't fit tools with very different realistic runtimes | Medium | Replaced with tiered timeout classes matched to each tool's realistic execution time; timeouts act as autonomous runaway guards and do not truncate active operator-directed fuzzing or exploitation. |
| C-09 | Unbudgeted per-command model-swap cost in the exec loop | Medium | The tool-execution model stays resident for the whole per-target loop, and per-command validation is deterministic code, never a second model invocation. |
| C-10 | Thermal throttling under sustained load, unverified | Medium | Added as an explicit feasibility check performed during operation, not an unstated assumption. |
| C-11 | "Completely mitigates hallucination" is an overclaim | Medium | Downgraded to non-absolute language, backed by an explicit adjudication checklist ruling out common false-positive causes before a finding is confirmed; no acceptance test assumes zero false positives. |
| C-12 | Tool execution boundaries and destructive risks | High | Reconciled via dual-mode execution: Autonomous Mode enforces strict non-destructive constraints (reads and safe writes permitted; data drops, schema alters, file wipes, and DoS prohibited). Operator-Directed Mode executes the requested command chain as instructed without containment interference. |
| C-13 | Two inference backends treated as interchangeable when a backend-specific feature was actually used | Medium | The inference backend is abstracted behind a single load/unload/chat-completion interface so backend-specific behavior can't leak into orchestration code. |
| C-14 | System utility access | Bounded residual risk | Autonomous execution uses standard security tool paths; operator directives may invoke specialized binaries across the host environment without arbitrary platform restrictions. |
| C-15 | A privileged memory-reclamation operation needs a capability the least-privilege design doesn't hold | High | The privileged operation runs via a narrow, single-purpose helper process granted only the one capability it needs — the main process never holds it. |
| C-16 | Long process-suspend breaks network/IPC session state, not just memory | Medium | The hibernation guarantee was explicitly reframed to cover process memory/UI state only; resumed-app reconnect prompts are documented as expected behavior, not a defect. |
| C-17 | "Zero-yield" was left undefined, letting a noisy tool defeat the circuit breaker | High | Defined precisely as the absence of any new discovery record, with two independent class-aware counters (standard vs. high-attempt tooling) instead of one blunt shared threshold. |
| C-18 | A race exists between process teardown and the next model allocation | Medium | Added a bounded settle-poll step between confirmed teardown and the next allocation, so a new model can't spawn into a not-yet-reclaimed memory state. |
| C-19 | A kill signal targeting only the parent PID lets orphaned subprocesses survive an abort | High | Every subprocess now spawns in its own process group/session, so a kill signal reaches the whole tree, not just the parent PID. |
| C-20 | A single concurrency mode alone doesn't prevent a "database is locked" error between concurrent invocations | Medium | Added an explicit busy-timeout setting on top of the existing concurrency mode. |
| C-21 | An offset-or-regex redaction-restore approach could restore the wrong secret | High | Changed to exact byte-offset addressing plus a content hash, eliminating the ambiguity a regex/offset-only approach could produce. |
| C-22 | Structured LLM output was never mechanically guaranteed valid | High | Every structured output must pass a mandatory deterministic schema validator regardless of which output-format request flag was used — the flag alone is never treated as a validity guarantee. |
| C-23 | Redaction timing was unspecified; post-processing a drafted report is fragile | High | Redaction now happens before the reporting step ever sees the evidence, never as post-processing on an already-drafted report. |
| C-24 | The tool-execution model had no visibility into current opt-in-flag state, wasting task budget on proposals that would be refused anyway | Medium | Its per-task context now includes the current opt-in-flag state, purely to avoid wasted proposals — the flag check itself is still enforced independently regardless. |
| C-25 | The report data model couldn't distinguish a per-finding report from the consolidated register | High | Added an explicit document-type/finding-linkage field so the two document kinds are never conflated. |
| C-26 | A drafted report's claims were never mechanically checked against its own supporting evidence | High | Grounding verification matches citations against raw session evidence during drafting. Discrepancies are highlighted for operator review and confirmation rather than dropped. |
| C-27 | Only a yield-based circuit breaker existed — no failure-based one | Medium | Added a second, independent circuit breaker based on consecutive network/timeout failures, distinct from and orthogonal to the yield-based one. |
| C-28 | No rate limiting existed anywhere in the design | Medium | Rate limits act as anti-DoS and target stability guardrails during autonomous operations; limits are dynamically adjustable or bypassable when executing operator-directed commands. |
| C-29 | Context-window management over a long task-queue loop | Medium — **genuinely unresolved** | No verified technique exists to adopt, and none was fabricated to fill the gap — remains an open item. |
| C-30 | A uniform quantization change sharply tightened the RAM headroom margin | Medium (accepted trade-off) | Accepted as a trade-off — the existing RAM re-measurement/abort gate already re-checks headroom regardless of which quantization is in use. |
| C-31 | A heuristic injection detector had no named patterns for known smuggling/line-jumping techniques | Medium | Its pattern list was revised to add named detection patterns for those specific techniques. |

---

## Authority & Conflict Resolution

This analysis documents adversarial findings and historical architectural remediations.
In the event of any discrepancy, ambiguity, or conflict between historical review
summaries, analytical notes, and active operational mandates, the **Security, Safety &
Compliance Requirements (`05`)** serves as the final and supreme authority across the
entire system.
