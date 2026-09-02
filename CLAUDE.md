# Agentic VAPT System — Repo Guide

**This repository currently contains planning only — no code exists yet.** It is a
complete requirements/architecture specification for an autonomous, locally-hosted,
multi-model LLM council that plans, executes, and reports on penetration-testing
engagements. If you are about to write code here, **read `00-Requirements-Index.md`
in full before writing anything** — it is the map of every other document, why each
exists, and how they relate. This file is a shorter pointer into that map for quick
orientation; `00` is the authoritative one.

## Read this first, in this order

1. `00-Requirements-Index.md` — the map. Explains what every other document is for
   and in what order to read them for full context.
2. `15-Implementation-Milestone-Roadmap.md` — the build order. Don't try to build
   everything at once; this sequences 9 independently-testable milestones.
3. Whichever numbered document matches the specific thing you're about to build —
   see the lookup table below.

## "I need to build/understand X — which document?"

| You're working on... | Read |
|---|---|
| What the system must do, phase by phase (functional behavior) | `01-Functional-Requirements.md` |
| Performance, reliability, resource budgets (RAM/disk/timeouts) | `02-NonFunctional-Requirements.md` |
| SQLite schema, table definitions, artifact file layout | `03-Data-and-Storage-Requirements.md` |
| API contracts, CLI command surface, tool-bridge interfaces | `04-Interface-and-Integration-Requirements.md` |
| Security rules, privilege boundaries, kill-switch, redaction | `05-Security-Safety-and-Compliance-Requirements.md` |
| Day-to-day operation: startup/shutdown, monitoring, degraded-mode behavior | `06-Operational-Requirements.md` |
| What could go wrong and how it's mitigated (before touching a risky area) | `07-Risk-Register.md` |
| What's assumed true, what's explicitly out of scope, external dependencies | `08-Assumptions-Constraints-Dependencies.md` |
| How to verify a requirement is actually satisfied (writing tests) | `09-Acceptance-Criteria-and-Test-Plan.md` |
| **Why** a requirement reads the way it does (every decision, chronological) | `10-Decision-Log-and-Open-Questions.md` |
| What was technically wrong with the original plan and how it was fixed | `11-Critical-Analysis-and-Design-Challenges.md` |
| Exact client-report formatting (HTML/CSS structure for PDF rendering) | `12-Report-Formatting-Rules.md` |
| Process model, language, file formats, privileged-helper contract, module layout | `13-Implementation-Architecture-Bridge.md` |
| The actual system-prompt text to send to each LLM role | `14-System-Prompt-Templates.md` |
| What order to build things in | `15-Implementation-Milestone-Roadmap.md` |
| What to actually reuse from `Actual-Setup/`, and what's Claude-Code-only | `16-Actual-Setup-Reuse-and-Integration-Map.md` |
| What's in `Standalone-Engine-Reference/` and why (**read the safety notice first**) | `17-Standalone-Engine-Reuse-and-Comparison.md` |
| Whether a requirement actually has a test behind it (coverage gaps) | `18-Requirement-to-Test-Traceability-Matrix.md` |
| Web3/mobile/GraphQL/CI-CD/credential-attack/source-code-access capability domains | `19-Extended-Capability-Domains.md` |
| Why certain actions (anti-forensics, live credential-spray, etc.) require a live human checkpoint, not just a config flag | `20-Human-Checkpoint-and-Escalation-Safety-Catalog.md` |
| The complete inventory of every misuse-prevention/ethics control (location, purpose, impact) | `21-Safety-Ethics-and-Misuse-Prevention-Control-Inventory.md` |
| The live terminal monitoring dashboard (`vaptctl dashboard`) | `22-VAPT-Monitoring-Dashboard-Specification.md` |
| The original high-level plan (now corrected in place — see below) | `Agentic VAPT Setup (HOME).md` |
| Existing reusable skills/tools/agents from a prior Claude-Code-based toolkit | `Actual-Setup/` (read `16` first — most of it is NOT directly reusable) |
| A standalone, non-Claude-Code hunting engine, kept for comparison only | `Standalone-Engine-Reference/` (read `17` first — its multi-cloud-provider and Ollama-first design conflicts with decisions already made here; mine techniques, don't import code) |

## Things that would otherwise be easy to get wrong

- **`Agentic VAPT Setup (HOME).md` is not the authoritative spec — `01`-`22` are.**
  The base file has been corrected in place for major issues (see its inline
  `*(...)*` notes, each pointing to a specific finding in `11`), but it deliberately
  states corrections at a **high level only** (no code-level specifics) and predates
  the `19`/`20` extended-capability-domain expansion entirely. `01`-`22` carry full
  precision. If the two ever seem to disagree on a detail, `01`-`22` wins.
- **This system is fully autonomous with no pause — except four specific action
  classes.** Anti-forensics, live credential-spray execution, CI/CD actions that
  create a real external artifact (opening a PR, etc.), and dependency-confusion
  package-publish all hard-stop for a live human `approve-checkpoint`/`deny-checkpoint`
  (`01`'s `FR-CHECKPOINT-01..05`) — this is a deliberate, narrow exception to the
  no-pause design (decision #13), not an oversight to "fix" by removing it. See `20`
  for the full rationale on each.
- **Nothing has been installed or downloaded.** Model `.gguf` files, Python
  dependencies, and the `kali-linux-everything` toolset are all prerequisites this
  planning phase deliberately left untouched — see `08` and `10`'s Open Questions
  (items F/G) before assuming they're available.
- **Authorization/Rules-of-Engagement verification is explicitly NOT built into this
  system** — it's the operator's responsibility outside the tool. Don't add an
  authorization gate; it was deliberately excluded (see `05` and `10` decision #3).
- **`Actual-Setup/`** is a separate, already-functional Claude-Code toolkit
  (skills/agents/commands/tools) copied in as a reference/dependency — it is not
  itself the system being planned here, and its own conventions don't override
  anything in `01`-`17`.
- **`Standalone-Engine-Reference/`** is reference material only — see `17`'s safety
  notice before ever going back to its source repo (`/home/vscysteam/claude-bug-bounty`)
  for anything else; that repo also contains real client engagement data that must
  never be copied into this project.
- Every open question that hasn't been resolved is listed explicitly in
  `10-Decision-Log-and-Open-Questions.md`'s "Open Questions Remaining" table — check
  there before assuming an unstated detail rather than guessing at it.
