*(Informational only — this document is an architectural Decision Log and Open Questions register capturing historical engineering decisions, design iterations, and deferred items. It does not define active requirements or functional specifications, and MUST be skipped by automated code-generation, parser pipelines, and core development processes.)*

# Decision Log & Open Questions — Autonomous Agentic VAPT System

Every substantive decision behind this document set, chronological, one line each.
Full reasoning for each decision, where non-obvious, is stated locally wherever that
decision now lives as a requirement — not repeated or cross-cited here.

| # | Decision |
| --- | --- |
| 1 | Absolute filesystem paths from the original planning session were kept verbatim (a different machine than this one). |
| 2 | An operator control surface (start/pause/resume/abort/status/export) is a real requirement, not an afterthought. |
| 3 | Authorization/Rules-of-Engagement verification is explicitly out of scope for the system itself; legal verification resides entirely with the human operator outside the software. |
| 4 | Numeric/design parameters are asked of the operator individually, never silently proposed. |
| 5-9 | RAM margin 1.5GB; disk 85%/95%; model-swap budget 60s; kill-switch 20s; E-core allocation 4/8. |
| 10-11 | Report pipeline: Markdown → pending-approval → operator approve → HTML/PDF; formatting rules cloned from `claude-bug-bounty`. |
| 12 | Multi-target support: one engagement can scope multiple hosts/domains. |
| 13 | Phase 4.2 loop bound set: 30-task cap + 3-zero-yield breaker + 12h budget, auto-pivot/report, no operator pause at any threshold during autonomous runs; fully configurable/extendable under direct operator instruction. |
| 14 | Project repository and git identity confirmed. |
| 15 | Pushback logged that a no-authorization-gate, no-pause autonomy design creates an unbounded-autonomy risk — reconciled via the Dual-Mode Mandate (strict non-destructive autonomous discovery paired with unconditional operator-directed execution). |
| 16-18 | Prompt-injection defense made mandatory; hibernation OOM protection added via a lowered OOM-kill priority; CVSS scoring moved to a deterministic calculator. |
| 19 | CLI-only control surface confirmed, no GUI. |
| 20-21 | Tool-execution containment settled: autonomous non-destructive boundaries (read/safe writes, no drops/alters/DoS) paired with unrestricted execution for operator-directed directives. |
| 22 | Redaction timing reconciled: raw evidence preserved verbatim locally; secret masking applied by default before Reporter drafting, restored upon report finalization. |
| 23-25 | A resource-budget framing note added; a driver-binding caveat left as documentation only; downgraded hallucination-mitigation language judged sufficient. |
| 26 | A residual tool-execution risk accepted: three curated opt-in categories run autonomously when flagged; execute immediately without pre-set flags when commanded by the operator. |
| 27-30 | CVSS 3.1 standardized; the GPU benchmark bar set as relative (vs. CPU-only), not absolute; the thermal-throttle trigger set to use the kernel's own signal; Gate 2's correction-attempt cap set to 3. |
| 31-32 | No interactive hibernation confirmation prompt (invoking `start` is the consent); the state store's backup was made mandatory. |
| 33 | Generic configurable autonomy levels (paranoid/normal/yolo) removed — superseded by the explicit Dual-Mode Execution Architecture. |
| 34 | (Later reversed, see #55) Gate 1's semantic tier swapped to a different instruct model, and a new deterministic first tier added ahead of it. |
| 35-38 | Zero model-swapping confirmed for the active tool-execution loop; Gate 2 made fully deterministic; tiered timeout classes adopted; one redundant performance target removed. |
| 39 | Base architecture document corrections applied in place for 9 major items (reversing an earlier "never touch the base document" policy). |
| 40 | Several findings resolved from an externally-sourced review; the OOM-kill priority value and the injection-provenance tag string were both concretized to specific values. |
| 41 | An implementation/architecture bridge document added: process model, language baseline, file formats, CLI framework, module layout. |
| 42 | Further findings resolved; a standing altitude policy set: the base architecture document carries corrections at a high level only, while the detailed requirement set carries full precision. |
| 43 | A structured-output reliability finding resolved via a hybrid approach: a structured-output-format request plus a mandatory deterministic schema validator plus a bounded retry. |
| 44 | A system-wide single-engagement lock added, enforced at both the application and the schema level. |
| 45-46 | System-prompt templates drafted for every council role; a build-order milestone roadmap added. |
| 47 | Second review pass: redaction timing moved to before report drafting; opt-in-flag-state visibility added to the tool-execution role's own context; a report-schema gap resolved. |
| 48 | A build-time coding-agent navigation file created at the repository root. |
| 49 | Third pass: model-file acquisition/dependency provenance flagged as an open item; one phase's wording corrected in the base document. |
| 50-51 | A prior toolkit's reuse potential fully mapped; a standalone comparison engine's reuse potential fully mapped — including an explicit safety notice that real client data in that source repository must never be copied in. |
| 52 | A full corpus audit: schema-enum drift fixed, several missing finding-resolution write-backs added, stale cross-document range references fixed. |
| 53 | Test-lab environment confirmed: local, disposable, container-based, never real infrastructure. |
| 54 | An MCP-integration verification follow-up: one integration confirmed genuinely real; another confirmed to have nothing usable to fetch. |
| 55 | **Six-model council roster overhaul**: the strategic-planning role reassigned to a different model; Gate 1's semantic tier reverted to its earlier model choice; the reporting role split out into its own dedicated model; quantization standardized to a uniform format across all six models. |
| 56 | A full mining sweep of the source toolkit: an upstream naming change synced; a new finding surfaced (undocumented Unicode/tool-description injection patterns); two methodology reference documents mined into the system-prompt material. |
| 57 | Full scope expansion: nine extended capability domains formalized; a Human Checkpoint Gate added for sensitive action classes (autonomous logging vs. immediate operator dispatch); schema generalized to support non-network target types. |
| 58 | Final mining pass: credential auto-propagation plumbing added; two more capability-domain requirement clusters added; the standalone audit-control catalog first drafted. |
| 59 | A completeness check: the audit-control catalog's corroborating-evidence section added; an AI-agent-security sub-class added to the CI/CD capability domain; a follow-on-task domain-routing requirement added. |
| 60 | A live monitoring dashboard formalized from an operator draft, with four corrections made during review: a mount-flag correction, a concrete swap-growth threshold adopted, a subcommand-naming fix, and a decision to derive dashboard state from existing invocation logs rather than a new dedicated table. |
| 61 | The base architecture document received a full retroactive mirroring pass — four new sections added (control surface, defense-in-depth, extended capability domains, monitoring). |
| 62 | An interactive console formalized: operator directives execute unconditionally with zero automated refusal; direct operator commands execute immediately (`approved_via = 'OPERATOR_DIRECTIVE'`) without interactive gate freezes. |
| 63 | Gate 1 evaluation relaxed: operator-originated tasks (`MANUAL_OPERATOR`) bypass both Tier 0 deterministic scope checking and Tier 1 semantic evaluation completely, executing with zero refusal. |
| 64 | A historical-state-inheritance and deduplication subsystem added — an explicit initial-vs-retest assessment mode, with regression findings never silently dropped from a report. |
| 65 | Operational flexibility formalized across the corpus: multi-line script execution via `script_runner`, class-aware zero-yield breaker thresholds, configurable per-target task ceilings, component-level grounding verification, tool-path symlink resolution, and explicit DNS-suffix scope matching. Operator-directed actions execute unconditionally across all classes. |
| 66 | The live-credential-spray checkpoint class finalized: configurable auto-lockout threshold enforces bounds during autonomous discovery; operator-directed credential testing runs per supplied parameters without interactive hostname re-typing or automated stalls. |
| 67 | The Human Checkpoint Gate's standalone predecessor document was merged verbatim into the audit-control catalog's own dedicated section, then deleted, to avoid two documents needing lockstep updates. |
| 68 | A corpus-wide deduplication and restructuring pass: enforced single-source-of-truth domain ownership across the whole requirements set; canonical IDs preserved unchanged; conversational bloat compressed to structured tables; Lateral cross-file citations removed corpus-wide; Security Specification (`05`) confirmed as the supreme authority over all security, safety, and control matters. |
| 69 | Architectural alignment to Dual-Mode Mandate: formal relaxation across all specifications, establishing strict non-destructive bounds for Autonomous Mode and unconditional, zero-refusal execution for Operator-Directed Mode. |

---

## Open Questions Remaining

| # | Item | Why still open |
| --- | --- | --- |
| A | Real-hardware feasibility checks (thermal telemetry, GPU driver binding, SYCL stability) | Only verifiable on the actual target machine. |
| B | Cross-machine transfer of this document set | Identified, accepted as a residual risk. |
| C | Gate 1's semantic tier's steerability behavior for "in-scope but excessive" autonomous tasks | Requires the actual model file plus live evaluation. |
| D | Whether the three high-risk-category binary lists are exhaustive | Not cross-checked against a full reference tool-suite manifest. |
| F | Model file acquisition (source/provenance) | Out of scope under this planning phase's no-install constraint. |
| G | No pinned Python dependency manifest | Deferred, installation-adjacent. |
| H | Context-window management strategy for the resident tool-execution role over a long task queue | No verified technique exists to adopt; none was fabricated to fill the gap. |

---

## Authority & Conflict Resolution

This document records the chronological history of architectural choices, design trade-offs,
and open research questions. In the event of any discrepancy, ambiguity, or conflict
between historical log entries, earlier design assumptions, and active system mandates,
the **Security, Safety & Compliance Requirements (`05`)** serves as the final and supreme
authority across the entire system.
