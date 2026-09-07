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

| `Agentic VAPT Setup (HOME).md` | modified | — (follow-up) | Added the actual model/quantization/footprint table (previously just pointed to `01`) and exact reference-hardware specs (CPU, GPU, memory, OS) to Section 8, per operator request. |

| `README.md` | **new** | — (follow-up) | GitHub-facing README added: concept, the five core diagrams (mirrored from `HOME.md`), and a condensed user story — deliberately brief, links out to `HOME.md` and the numbered docs for detail. |

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
