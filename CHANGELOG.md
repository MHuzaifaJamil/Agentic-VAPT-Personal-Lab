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
| `54b5203` | — (housekeeping) | Folded the `8d32a85` push into this index (the row above). |
| `e71dcf0` | 70, 72–74 | Consolidated push: `FR-ENV-03a`/`08a`–`08c` (hibernation self-exclusion, auto-launched dashboard/console, decision #70); corpus-wide rename disambiguating the AI "Operator" role from the Human Operator (Strategy Auditor, Primary Scripter, Criterion Adjudicator, `HUMAN_OPERATOR`/`HUMAN_OPERATOR_DIRECTIVE` throughout, decision #72, applied corpus-wide including docs `00`,`04`,`07`,`08`,`11`–`17`,`19`,`21`–`24`); `FR-CTRL-01a` (bounded `--notes`) and `OPS-NOTIFY-01`–`05` added; `FR-INTERVENE-06` corrected so a Human Operator directive takes queue priority only on genuine resource conflict (decision #73); the dual-scripter council architecture — Alignment Linter retired in favor of deterministic 3-tier Gate 2, Secondary Scripter added for an orthogonal Phase 4.2B pass (decision #74, `13`'s module tree finalized as `secondary_scripter.py`/`gate2_validator.py`). `HOME.md` brought back in sync throughout (new diagrams, roster table, relay-diagram fixes). New `STAGING-Pending-Discussions-and-Fixes.md` added. `CLAUDE.md` §4 (model roster) removed per Human Operator direction — model roster now lives only in `01`. |
| `0e02b59` | — | Merge commit reconciling a remote push; `CHANGELOG.md` kept per explicit Human Operator decision (a modify/delete conflict against a remote deletion of this file). |
| `6cffb3c` | 71 | `HOME.md`: actual model/quantization/footprint table added to Section 3 (previously deferred to `01`); exact reference-hardware specs (CPU, GPU, memory, host OS) added to Section 8. New brief GitHub-facing `README.md`: concept, the five core diagrams, a condensed user story. |
| `0bc551f` | — (follow-up, `/code-review` fixes) | `01`'s Council Roster table gained Quantization/Footprint columns for all 6 roles (previously only Secondary Scripter had inline figures); `HOME.md`'s swap-partition rationale corrected (tied to Step 1's app-freeze reclaim, not model loads), duplicated Section 8 facts removed, sync note added next to the council-relay diagram pointing at its `README.md` copy; matching sync note added in `README.md`; `CHANGELOG.md` corrected its own prior entry about which HOME.md section the model table landed in. |
| `8d88aca` | — (follow-up) | `16:TR-BRIDGE-03` corrected: cited a nonexistent official `npx @caido/mcp-server` package — fixed to the actual community server (`c0tton-fluff/caido-mcp-server`) and its real PAT/OAuth auth, verified against `Actual-Setup/mcp/caido-mcp-client/`. `04`'s `IR-MCP` section retitled (its old title implied Burp uses MCP, contradicting `16:TR-BRIDGE-01`'s direct-REST-only requirement for Burp). |
| `9378200` | — (Round 4 staged, nothing merged) | `STAGING-Pending-Discussions-and-Fixes.md` only: baseline recon pipeline design, `port_scanner.py`'s "redundant with nmap" verdict overturned on inspection, three deferred-gap integration points drafted. Awaiting approval. |
| `52ec453` | 75 | Round 4 merged: new `FR-BASELINE` cluster (deterministic `naabu`→`whatweb`→`ffuf`/`feroxbuster`→`nuclei` pipeline, runs once per target after Phase 3); `naabu` added to `FR-TOOL-01`; `FR-TOOL-17` (session reuse, `03:DR-SCHEMA-22`, `05:SEC-DATA-04`), `FR-TOOL-18` (fingerprint-triggered EOL/CVE lookup, `03:DR-SCHEMA-23`), `FR-TOOL-19` (multipart tool) added; `16:TR-SCRIPT-06` rewritten to point at the concrete spec. New `09:TP-BASELINE`/`TP-TOOLEXT` clusters; `13` gained `baseline_recon.py`. Doc `01` 109→116 (75 covered); corpus baseline 348→358 (182 covered). |
| `438b931` | — (Round 5 staged, nothing merged) | `STAGING-Pending-Discussions-and-Fixes.md` only: proposal to expand `FR-BASELINE` to the full 72-tool personal arsenal. Awaiting approval. |
| `af192a1` | 76 | Round 5 merged: `FR-BASELINE` expanded to 40+ tools across 4 dependency waves (bounded parallel execution per wave); trigger moved to between Phase 1 and Phase 2 (before the first model loads). Post-merge correction applied same-session per operator direction ("overlapping tools are always welcome"): un-trimmed `bbot`/`theHarvester`/`knockpy`/`dnsrecon`/`massdns`/`shuffledns` (Wave 1) and `waymore`/`hakrawler`/`gospider`/`cariddi`/`aquatone`/`eyewitness` (Wave 3); `sublert` now runs in both `FR-BASELINE` (one-shot) and `FR-MONITOR` (continuous). Only `maigret`/`pywhat` stay Tier-2-only (input-shape mismatch, not a redundancy trim). Doc `01` 116→119 (78 covered); corpus baseline 358→361 (185 covered). Rounds 6/7/8 staged for approval (nothing merged yet). |
| `b4e656e` | — (follow-up) | New reference file `KALI-TOOL-CATALOG.md` (repo root): full Kali tool census by official category plus everything else `kali-linux-everything` bundles, pulled directly from this machine's own `apt-cache show` output. Round 8's staged `FR-DISCOVER-01` simplified to reference this file directly instead of an inline curated mapping. |
| `ef8bd94` | 77 | Rounds 6/7/8 merged, including the requested gap-check: new `FR-TOOL-20` (Phase 4.2 AI-gated exploitation & specialist tools — `dalfox`/`xsstrike`/`ghauri`/`fuxploider` genuinely new; `hashcat`/`cupp`/`trevorspray`/`kerbrute`/`interactsh-client`/`mobsf`/`objection` formally registered, several already required by name in `19`'s prose — `cewler`/hashcat-rule mutation and `interactsh-client` were already named in `FR-CRED-01`/`FR-ARGUS-02`, not skipped as duplicates); new `FR-DISCOVER-01`–`04` cluster (consult `KALI-TOOL-CATALOG.md` for undefined domains, `shutil.which` presence check, no autonomous install without opt-in, new `ACTIVE_WIRELESS_DISRUPTION` checkpoint class); `FR-CHECKPOINT-01`'s fixed class list extended five→six. `19:FR-MOBILE-08` added (`objection` formally registered, `mobsf` new). New `09:TP-DISCOVER` cluster plus rows in `TP-TIER1`/`TP-CHECKPOINT`. Doc `01` 119→124 (83 covered); corpus baseline 361→366 (190 covered). `STAGING.md`: Rounds 6/7/8 archived as merged. This same commit also backfilled the CHANGELOG's own stale "Working Tree" section (`e71dcf0` through `b4e656e` above) into Push History with their real hashes. |

## Working Tree — Uncommitted Changes (Development Agents: read this first)

Not yet committed/pushed. This section is where a requirement change lands the moment
it's applied to the binding docs — before there's a commit hash for it — so a
Development Agent picking up this repo mid-session sees new/updated requirements
immediately rather than only after the next push. Folds into "Push history" above
(with a real commit hash) once actually committed, and is cleared at that point.

*(nothing uncommitted right now — clean working tree as of `ef8bd94`.)*

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
