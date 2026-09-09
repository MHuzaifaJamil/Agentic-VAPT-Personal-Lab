# Changelog Index

An index of pushes to this repository, by commit — not a restatement of file content.
For *why* a change was made, follow the pointer into
`10-Decision-Log-and-Open-Questions.md`'s numbered entries; the substance of *what*
changed lives in the files themselves. Updating this index is a mandatory part of
every push, per standing Human Operator instruction.

Rebuilt from scratch on 2026-09-07 directly against `git log`, replacing a prior
version of this file that had gone missing from the working tree.

## Push history

| Commit | Decision(s) | Summary |
|---|---|---|
| `d096e4a` | 1–4 | Initial VAPT system requirements planning docs. |
| `ac05137` | 5–9 | Expanded requirements docs `03`–`08`; resolved early critical-analysis findings. |
| `98df5ea` | 10–14 | Resolved all critical-analysis findings to date; added docs `09`–`10`; corpus consistency fixes. |
| `77f2326` | 15–25 (approx.) | Added critical-analysis findings C-15–18; added the implementation architecture bridge (`13`). |
| `178ac88` | — | Added `Actual-Setup/`: the full Claude-dependent VAPT toolkit imported from `claude-bug-bounty` as reference material. |
| `775dbb6` | 26–33 (approx.) | Added critical-analysis findings C-19–21 (kill-switch behavior, SQLite locking, redaction precision). |
| `4c52cc9` | — | Synced `Actual-Setup/mcp/hackerone-mcp/server.py` with an upstream MCP server fix. |
| `7bbaad9` | 55 | Overhauled the LLM council to the current 6-model roster, avoiding gated Hugging Face models. |
| `c367790` | 56, 57 | Formalized the `claude-bug-bounty` mining sweep and extended capability domains (`19`). |
| `a051df6` | — (Human Operator, direct) | Removed unused report-generator scripts from `Standalone-Engine-Reference/`. |
| `15efa13` | 58, 59 | Completed the second-round mining sweep; added the standalone safety-control inventory (`21`). |
| `31d9fbe` | — (follow-up) | Reflected the `a051df6` removal in doc `17`'s now-stale reference. |
| `2a3f608` | 60 | Added the VAPT Monitoring Dashboard specification (`22`, `vaptctl dashboard`). |
| `d2e9126` | 61 | Brought `Agentic VAPT Setup (HOME).md` up to date as a complete high-level blueprint. |
| `97e9018` | 62–64 | Added the interactive TUI console (`23`) and historical state/dedup subsystem (`24`). |
| `d2d5b8e` | — (housekeeping) | Filled in the commit hash for the #62–64 push in this index. |
| `b34c493` | — (audit fix) | Fixed 8 cross-document inconsistencies found in a corpus-wide audit: `CLAUDE.md`'s `keep_alive` claim corrected to match `01`/`07`; doc `16`'s filename reference synced; `TR-SCRIPT-01` script count corrected (29→28); `FR-TOOL-01`/`TP-TIER1` tool-count parity fixed (11→12); doc `18`'s traceability matrix counts reconciled against every source doc; doc `04`'s `IR-CTRL` namespace-ownership split with `13` documented; doc `05`'s mislabeling of docs `07`/`08`/`12` fixed; primary-source lists harmonized between `00` and `CLAUDE.md`. |
| `8d32a85` | — (Human Operator, direct) | `Assumptions-Not-Approved.md`/`ASSET-CLASSIFICATION.md` moved here from `../implementation/`, maintained from this location going forward (content unchanged by the move). New `IMPLEMENTATION-DEVIATIONS-FROM-REQUIREMENTS.md`: records the 2026-09-08 Phase 1 hibernation architecture change (denylist→allowlist, `orchestrator/hibernation.py` on the Implementing PC) as an operator-approved deviation from `01:FR-ENV-03`'s literal "fixed denylist" wording — made after three real forced-hardware-shutdown incidents plus 15 further correctness bugs found in the same mechanism by one code-review pass — plus the additive `suspended_processes.start_time_ticks` pid-recycling fix (touches `03:DR-SCHEMA-13`, non-conflicting). Not yet reconciled into `01`'s own text; tracked for the next requirements-sync pass. |

## Working Tree — Uncommitted Changes (Development Agents: read this first)

Not yet committed/pushed. This section is where a requirement change lands the moment
it's applied to the binding docs — before there's a commit hash for it — so a
Development Agent picking up this repo mid-session sees new/updated requirements
immediately rather than only after the next push. Folds into "Push history" above
(with a real commit hash) once actually committed, and is cleared at that point.

| File | Status | Decision | Summary |
|---|---|---|---|
| `01-Functional-Requirements.md` | modified | #70 | Added `FR-ENV-03a` (hibernation MUST unconditionally protect the terminal session that ran `start`, walking to its session leader); `FR-ENV-08a` (`start` auto-launches `vaptctl dashboard` + `vaptctl console` immediately after the Phase 1 headroom check clears, before Phase 2); `FR-ENV-08b` (terminal-emulator auto-detection/spawn mechanism); `FR-ENV-08c` (graceful degradation if no terminal emulator is found). |
| `09-Acceptance-Criteria-and-Test-Plan.md` | modified | #70 | Added 4 `TP-ENV` rows covering `FR-ENV-03a`/`08a`/`08b`/`08c`. |
| `10-Decision-Log-and-Open-Questions.md` | modified | #70 | Decision #70 entry added. |
| `18-Requirement-to-Test-Traceability-Matrix.md` | modified | #70 | Doc `01` total reqs 103→107, now covered (66 vs. prior 62); corpus baseline covered 160→164. |
| `22-VAPT-Monitoring-Dashboard-Specification.md` | modified | #70 | Notes the `FR-ENV-08a` auto-launch trigger; `vaptctl dashboard` re-scoped as a manual-recovery command. |
| `23-Interactive-TUI-Console-and-Intervention-Pipeline-Specification.md` | modified | #70 | Notes the `FR-ENV-08a` auto-launch trigger; `vaptctl console` re-scoped as a manual-recovery command. |
| `Agentic VAPT Setup (HOME).md` | modified | #71 | Rewritten as a management-level blueprint: plain-English framing, Mermaid diagrams (phase lifecycle, council relay, dual-mode safety, dashboard/console auto-launch), and a new detailed Human Operator user-story section. |
| `CLAUDE.md` | modified | — (Human Operator, direct) | Removed §4 (Multi-Model Council Topology table) — Human Operator flagged that CLAUDE.md is agent operating instructions, not a technical specification, so model-roster detail doesn't belong there. Sections renumbered (old §5→§4, old §6→§5) accordingly. Where this content should actually live is proposed in `STAGING-Pending-Discussions-and-Fixes.md`, pending Human Operator decision. |
| `Agentic VAPT Setup (HOME).md` | modified | — (follow-up) | Footnote pointing to the now-removed `CLAUDE.md` §4 fixed to point at the staging file instead. |

| `01-Functional-Requirements.md` | modified | #72 | Council Roster section added; roles renamed (Strategy Auditor, Primary Scripter, Criterion Adjudicator); `FR-CTRL-01a` added (bounded inline `--notes` at `start`); every "operator" reference now reads "Human Operator" / `HUMAN_OPERATOR`. |
| `03-Data-and-Storage-Requirements.md` | modified | #72 | `engagements.human_operator_notes` column added; `operator_command_queue`→`human_operator_command_queue`; role/operator terminology renamed throughout. |
| `05-Security-Safety-and-Compliance-Requirements.md` | modified | #72 | `SEC-SCOPE-01` reworded to state explicitly that the Strategy Auditor never evaluates scope itself (Tier 0 alone does, against Human-Operator-configured `scope_rules`); operator terminology renamed throughout. |
| `06-Operational-Requirements.md` | modified | #72 | `OPS-NOTIFY-01`–`05` added (severity tags, no silent full stops, Error Code Dictionary, full raw error printing pre-Dashboard/Console); operator terminology renamed throughout. |
| `09-Acceptance-Criteria-and-Test-Plan.md` | modified | #72 | `TP-NOTIFY` cluster added; `TP-PRE` rows added for `FR-CTRL-01a`; operator/role terminology renamed throughout. |
| `10-Decision-Log-and-Open-Questions.md` | modified | #72 | Decision #72 added; historical entries' operator terminology renamed for corpus-wide consistency. |
| `18-Requirement-to-Test-Traceability-Matrix.md` | modified | #72 | Doc `01` 107→108 (67 covered); doc `06` 15→20 (8 covered); corpus baseline 340→346 (170 covered). |

| `00`, `04`, `07`, `08`, `11`, `12`, `13`, `14`, `15`, `16`, `17`, `19`, `21`, `22`, `23`, `24`, `Agentic VAPT Setup (HOME).md` | modified | #72 | Same terminology sweep extended to the remaining corpus (background pass): Strategy Auditor / Primary Scripter / Alignment Linter / Criterion Adjudicator role renames, `Human Operator` phrasing, `HUMAN_OPERATOR`/`HUMAN_OPERATOR_DIRECTIVE`/`human_operator_command_queue`. `23`'s `@op` console prefix renamed `@script`; its `target_role` enum updated to match `03`'s precedent. `13`'s module-layout filenames also renamed (`scope_gate.py`→`strategy_auditor.py`, `operator.py`→`primary_scripter.py`, `offline_linter.py`→`alignment_linter.py`, `adjudicator.py`→`criterion_adjudicator.py`) — **a judgment call awaiting explicit confirmation**, since it implies code structure, not just prose. |
| `18-Requirement-to-Test-Traceability-Matrix.md`, `19-Extended-Capability-Domains.md`, `CLAUDE.md` | modified | — (follow-up) | 3 leftover pre-sweep terminology misses fixed after a verification grep: a stale `MANUAL_OPERATOR`/casing miss in `18`, a lowercase casing miss in `19`, and two stale `MANUAL_OPERATOR`/"operator" mentions in `CLAUDE.md`'s Directives 1 (fixed for consistency with the rest of the now-renamed corpus). |

| `13-Implementation-Architecture-Bridge.md` | modified | — (follow-up) | `alignment_linter.py` renamed `secondary_scripter.py` in the module tree, per operator instruction ahead of the broader Secondary Scripter proposal (staged, see `STAGING-Pending-Discussions-and-Fixes.md` Round 3) — avoids cementing the deprecated Linter role into the documented module tree. |

| `23-Interactive-TUI-Console-and-Intervention-Pipeline-Specification.md` | modified | #73 | `FR-INTERVENE-06` revised: Human Operator directives take priority only on genuine resource conflict, no longer supersede/cancel the autonomous queue outright. |

| `01-Functional-Requirements.md` | modified | #74 | Council Roster: Alignment Linter removed, Secondary Scripter added. `FR-COUNCIL-08` rewritten as three-tier deterministic Gate 2; `FR-COUNCIL-09a` removed (absorbed into Tier 2A); `FR-COUNCIL-11c/11d` added (shared session budget, batch-sequential handoff); `FR-COUNCIL-12` corrected for the two-sub-phase unload timing; `FR-TOOL-16`, `FR-GATE-07` updated. |
| `03-Data-and-Storage-Requirements.md` | modified | #74 | `DR-SCHEMA-21: scripter_execution_ledger` added; `target_role`/`model_invocation_logs.role` enums updated (Linter removed, both scripters added). |
| `09-Acceptance-Criteria-and-Test-Plan.md` | modified | #74 | `TP-COUNCIL2` rewritten for the three-tier Gate 2 and dual-scripter handoff; new `TP-SCRIPT-ORTHOGONAL` cluster added. |
| `13-Implementation-Architecture-Bridge.md` | modified | #74 | Module tree finalized: `secondary_scripter.py`, `gate2_validator.py` and `phase_lifecycle.py` descriptions updated for the three-tier/dual-scripter design. |
| `14-System-Prompt-Templates.md` | modified | #74 | Alignment Linter system prompt replaced with the Secondary Scripter's (Advanced Offensive Exploit Engineer & Orthogonal Bypass Specialist). |
| `18-Requirement-to-Test-Traceability-Matrix.md` | modified | #74 | Doc `01` 108→109 (68 covered); doc `03` 33→34 (22 covered); corpus baseline 346→348 (172 covered). |
| `22-VAPT-Monitoring-Dashboard-Specification.md` | modified | #74 | Model-matrix rows updated for the dual-scripter roster; Gate 2 row description updated for the three-tier design. |
| `23-Interactive-TUI-Console-and-Intervention-Pipeline-Specification.md` | modified | #74 | `@lint` retired; `@script1`/`@script2` added (generic `@script` resolves to whichever scripter is resident); `FR-INTERVENE-07`'s stale Linter reference fixed. |
| `15-Implementation-Milestone-Roadmap.md` | modified | #74 | Milestone 4's council-integration list updated for the retired Linter / new Secondary Scripter. |
| `Agentic VAPT Setup (HOME).md` | modified | #74 | Council roster table, relay diagram (Gate labels corrected away from "safety" framing), new dual-scripter handoff diagram, and a stale pre-R2.6 "overriding" sentence in the user story fixed to match the actual console-priority behavior. |

| `Agentic VAPT Setup (HOME).md` | modified | — (follow-up) | Council relay diagram's "runs the tool"/"Tool actually runs" ordering bug fixed (Primary Scripter writes a command, Gate 2 validates it, only then does the tool run); `Strategist` renamed `Lead Strategist` for consistency. Round 2 features that had never made it into the blueprint added: Human Operator guidance notes at `start` (`FR-CTRL-01a`), and the error/notification policy (`OPS-NOTIFY-01`–`05` — plain-English reasons, loud banners for serious issues, full raw detail for pre-Dashboard failures). |

| `Agentic VAPT Setup (HOME).md` | modified | — (follow-up) | Secondary Scripter integrated directly into the main council-relay diagram (it had been left in a separate, disconnected diagram) — shown feeding into the same Gate 2 → Tool → Adjudicator → Reporter pipeline via the Pass 1 → Pass 2 handoff; the redundant standalone handoff diagram removed. |

| `Agentic VAPT Setup (HOME).md` | modified | — (follow-up) | Added the actual model/quantization/footprint table (previously just pointed to `01`) to Section 3, and exact reference-hardware specs (CPU, GPU, memory, host OS) to Section 8, per operator request. `01`'s own Council Roster table gained the same Quantization/Footprint columns so HOME.md's "mirrors `01`" claim is actually true. |

| `README.md` | **new** | — (follow-up) | GitHub-facing README added: concept, the five core diagrams (mirrored from `HOME.md`), and a condensed user story — deliberately brief, links out to `HOME.md` and the numbered docs for detail. |

| `01-Functional-Requirements.md` | modified | — (follow-up) | Council Roster table gained Quantization/Memory-Footprint columns for all 6 roles (previously only Secondary Scripter had inline figures) — fixes a `/code-review` finding that `HOME.md`'s "mirrors `01`" claim was false for 5/6 roles. |
| `Agentic VAPT Setup (HOME).md` | modified | — (follow-up) | `/code-review` fixes: swap-partition description corrected (tied to Step 1's app-freeze reclaim, not "model loads"); duplicated "Memory strategy"/Host-OS facts removed from the Section 8 table; sync note added next to the council-relay diagram pointing at its `README.md` copy. |
| `README.md` | modified | — (follow-up) | Sync note added next to the council-relay diagram pointing at its `HOME.md` copy, per `/code-review` finding (no shared-include mechanism exists in plain Markdown, so an explicit maintenance note is the fix, not full de-duplication — the diagram's presence here is by design). |
| `CHANGELOG.md` | modified | — (follow-up) | Corrected its own prior entry: the model/footprint table landed in `HOME.md` Section 3, not Section 8 as previously stated; the Section 8 parenthetical now matches its actual (now 4-row) contents. |

| `16-Actual-Setup-Reuse-and-Integration-Map.md` | modified | — (follow-up) | `TR-BRIDGE-03` corrected: cited `npx @caido/mcp-server` (no such official package exists) — fixed to the actual community server (`c0tton-fluff/caido-mcp-server`) and its real PAT/OAuth auth mechanism, matching `Actual-Setup/mcp/caido-mcp-client/`'s reference client exactly. Found via direct comparison against the operator's live reference toolkit. |
| `04-Interface-and-Integration-Requirements.md` | modified | — (follow-up) | `IR-MCP` section retitled — its old title ("Burp Suite / Caido MCP Integration") implied Burp uses MCP, contradicting `16:TR-BRIDGE-01`'s explicit direct-REST-only requirement for Burp. Requirement text clarified to say which parts apply to Burp's REST bridge vs. Caido's actual MCP integration. |

| `01-Functional-Requirements.md` | modified | #75 | New `FR-BASELINE` cluster (deterministic Phase-3→4.1 recon pipeline); `naabu` added to `FR-TOOL-01`'s roster; `FR-TOOL-17/18/19` added (session reuse, fingerprint-triggered EOL/CVE lookup, multipart Tier 1 tool). |
| `03-Data-and-Storage-Requirements.md` | modified | #75 | `DR-SCHEMA-22: auth_sessions`, `DR-SCHEMA-23: tech_fingerprint_intel` added. |
| `05-Security-Safety-and-Compliance-Requirements.md` | modified | #75 | `SEC-DATA-04` added — session credentials follow the existing correlation-hash pattern, never raw in logs. |
| `09-Acceptance-Criteria-and-Test-Plan.md` | modified | #75 | New `TP-BASELINE` and `TP-TOOLEXT` clusters added. |
| `13-Implementation-Architecture-Bridge.md` | modified | #75 | Module tree gained `baseline_recon.py`. |
| `16-Actual-Setup-Reuse-and-Integration-Map.md` | modified | #75 | `TR-SCRIPT-06` rewritten concretely, pointing to `01:FR-BASELINE` for the actual pipeline spec. |
| `18-Requirement-to-Test-Traceability-Matrix.md` | modified | #75 | Doc `01` 109→116 (75 covered); doc `03` 34→36 (24 covered); doc `05` 28→29 (19 covered); corpus baseline 348→358 (182 covered). |

| `01-Functional-Requirements.md` | modified | #76 | `FR-BASELINE` expanded to 40+ tools across 4 dependency waves (bounded parallel execution within each wave); trigger moved to between Phase 1 and Phase 2 (before the first model loads); `FR-TOOL-01` roster expanded to match; `FR-MONITOR-01` gained the `sublert`-technique cross-reference. |
| `09-Acceptance-Criteria-and-Test-Plan.md` | modified | #76 | `TP-BASELINE` expanded: wave-order, bounded-parallelism, conditional-skip, and exclusion tests added. |
| `13-Implementation-Architecture-Bridge.md` | modified | #76 | `baseline_recon.py`'s description updated for the parallel wave executor and new Phase-1→2 trigger point. |
| `18-Requirement-to-Test-Traceability-Matrix.md` | modified | #76 | Doc `01` 116→119 (78 covered); corpus baseline 358→361 (185 covered). |

| `01-Functional-Requirements.md`, `09-Acceptance-Criteria-and-Test-Plan.md` | modified | — (follow-up to #76) | Un-trimmed per operator correction: overlapping-purpose tools are welcomed, not trimmed. Added back `bbot`/`theHarvester`/`knockpy`/`dnsrecon`/`massdns`/`shuffledns` to Wave 1 and `waymore`/`hakrawler`/`gospider`/`cariddi`/`aquatone`/`eyewitness` to Wave 3; `sublert` now runs in both `FR-BASELINE` (one-shot) and `FR-MONITOR` (continuous). Only `maigret`/`pywhat` stay Tier-2-only (input-shape mismatch, not a redundancy trim). |

## Earlier decisions not yet mapped to a specific commit

Decisions #34–54 in the decision log predate this index's practice of citing commit
hashes per entry. They are covered collectively by the pushes between `77f2326` and
`178ac88` above; consult `10-Decision-Log-and-Open-Questions.md` directly for their
content rather than assuming a 1:1 commit mapping.

## Pending, not yet in this index

See `STAGING-Pending-Discussions-and-Fixes.md` (repo root) for changes under Human Operator
review that have **not** been merged into the binding requirement docs, and therefore
have no entry here yet. That file is excluded from the build/development-agent scope
exclusion list and MUST NOT be treated as a source of active requirements.
