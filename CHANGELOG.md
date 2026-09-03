# Changelog Index

An index of files touched, by push, not a restatement of their content. For *why*
each changed, follow the pointer — the substance lives in
`10-Decision-Log-and-Open-Questions.md`'s numbered entries and in the files
themselves, not here. Updating this index is a mandatory part of every push, per
standing operator instruction.

## Push history

| Commit(s) | Decisions | Summary |
|---|---|---|
| `7bbaad9` | #55 | 6-model council roster overhaul |
| `c367790` | #56, #57 | `claude-bug-bounty` mining sweep; extended capability domains + Human Checkpoint Gate |
| `a051df6` | — (operator, direct) | Removed `Standalone-Engine-Reference/report-generators/*.py` as unneeded |
| `15efa13` | #58, #59 | Second-round `claude-bug-bounty` mining sweep (`docs/`, `web3/` deep files, `scripts/full_hunt.sh` pipeline, `demo/`, `hooks/`) + new safety-control inventory (`21`); folded in the same push as the final top-level completeness check (`LICENSE`/`TERMS.md`/`serve.py`/etc., `FR-CICD-01`'s AI-agent sub-class, `FR-COUNCIL-10a`) |
| `31d9fbe` | — (follow-up) | One fix for the `a051df6` removal (doc 17's now-stale reference) |
| `2a3f608` | #60 | VAPT Monitoring Dashboard formalized (`22`) |
| *(pending)* | #61 | `Agentic VAPT Setup (HOME).md` full retroactive mirroring pass |

## By decision (this push: #61)

| Decision | Files touched |
|---|---|
| [#61](10-Decision-Log-and-Open-Questions.md) — HOME.md full retroactive mirroring pass | `Agentic VAPT Setup (HOME).md` (4 new §5-8 sections + a multi-target clarification), `10` |

## By file (this push)

| File | Status | Decision(s) |
|---|---|---|
| `Agentic VAPT Setup (HOME).md` | modified | #61 |
| `10-Decision-Log-and-Open-Questions.md` | modified | #61 |

## By decision (prior push, #60)

| Decision | Files touched |
|---|---|
| [#60](10-Decision-Log-and-Open-Questions.md) — VAPT Monitoring Dashboard | `22` (new), `00`, `02` (`NFR-RES-06`), `03` (`DR-SCHEMA-08`), `08` (`AC-DEPENDENCY-20`), `09` (`TP-DASHBOARD`), `10`, `13` (CLI + module layout), `CLAUDE.md` |

## By file (prior push, #60)

| File | Status | Decision(s) |
|---|---|---|
| `00-Requirements-Index.md` | modified | #60 |
| `02-NonFunctional-Requirements.md` | modified | #60 |
| `03-Data-and-Storage-Requirements.md` | modified | #60 |
| `08-Assumptions-Constraints-Dependencies.md` | modified | #60 |
| `09-Acceptance-Criteria-and-Test-Plan.md` | modified | #60 |
| `10-Decision-Log-and-Open-Questions.md` | modified | #60 |
| `13-Implementation-Architecture-Bridge.md` | modified | #60 |
| `22-VAPT-Monitoring-Dashboard-Specification.md` | **new** | #60 |
| `CLAUDE.md` | modified | #60 |

## By decision (prior pushes, #55-59)

| Decision | Files touched |
|---|---|
| [#55](10-Decision-Log-and-Open-Questions.md) — 6-model council roster overhaul | `Agentic VAPT Setup (HOME).md`, `00`, `01`, `03`, `05`, `07`, `08`, `09`, `10`, `11`, `13`, `14`, `15`, `17` |
| [#56](10-Decision-Log-and-Open-Questions.md) — `claude-bug-bounty` mining sweep (change-check + fresh sweep) | `Actual-Setup/commands/{bypass-403,cloud-recon,secrets-hunt,takeover}.md`, `Actual-Setup/tools/{bypass_403,cloud_recon,secrets_hunter,takeover_scanner}.sh`, `16`, `17` |
| [#57](10-Decision-Log-and-Open-Questions.md) — Extended capability domains + Human Checkpoint Gate | `19` (new), `20` (new), `Standalone-Engine-Reference/docs/` (new), `00`, `01`, `03`, `07`, `08`, `09`, `10`, `11`, `13`, `14`, `15`, `16`, `17`, `CLAUDE.md` |
| [#58](10-Decision-Log-and-Open-Questions.md) — Second-round mining sweep + safety-control inventory | `21` (new), `01`, `08`, `10`, `14`, `16`, `17`, `19`, `CLAUDE.md`, `Actual-Setup/{hooks,scripts,web3}/` (new), `Standalone-Engine-Reference/{demo,docs/*}` (new) |
| [#59](10-Decision-Log-and-Open-Questions.md) — Final top-level completeness check | `01` (`FR-CICD-01`'s AI-agent sub-class, `FR-COUNCIL-10a`), `00`, `10`, `16`, `17`, `CLAUDE.md`, `Standalone-Engine-Reference/{LICENSE,TERMS.md,serve.py,pytest.ini,uninstall.sh,uninstall_tools.sh}` (new) |

## By file (prior pushes, #55-59)

| File | Status | Decision(s) |
|---|---|---|
| `Agentic VAPT Setup (HOME).md` | modified | #55 |
| `00-Requirements-Index.md` | modified | #55, #57, #58, #59 |
| `01-Functional-Requirements.md` | modified | #55, #57, #58, #59 |
| `03-Data-and-Storage-Requirements.md` | modified | #55, #57 |
| `07-Risk-Register.md` | modified | #55, #57 |
| `08-Assumptions-Constraints-Dependencies.md` | modified | #55, #57, #58 |
| `09-Acceptance-Criteria-and-Test-Plan.md` | modified | #55, #57 |
| `10-Decision-Log-and-Open-Questions.md` | modified | #55, #56, #57, #58, #59 |
| `11-Critical-Analysis-and-Design-Challenges.md` | modified | #55, #57 |
| `13-Implementation-Architecture-Bridge.md` | modified | #55, #57 |
| `14-System-Prompt-Templates.md` | modified | #55, #57, #58 |
| `15-Implementation-Milestone-Roadmap.md` | modified | #55, #57 |
| `16-Actual-Setup-Reuse-and-Integration-Map.md` | modified | #56, #57, #58, #59 |
| `17-Standalone-Engine-Reuse-and-Comparison.md` | modified | #55, #56, #57, #58, #59 |
| `19-Extended-Capability-Domains.md` | new (#57), modified (#58) | #57, #58 |
| `20-Human-Checkpoint-and-Escalation-Safety-Catalog.md` | **new** | #57 |
| `21-Safety-Ethics-and-Misuse-Prevention-Control-Inventory.md` | **new** | #58 |
| `CLAUDE.md` | modified | #57, #58, #59 |
| `Actual-Setup/commands/bypass-403.md` | modified | #56 |
| `Actual-Setup/commands/cloud-recon.md` | modified | #56 |
| `Actual-Setup/commands/secrets-hunt.md` | modified | #56 |
| `Actual-Setup/commands/takeover.md` | modified | #56 |
| `Actual-Setup/tools/bypass_403.sh` | modified | #56 |
| `Actual-Setup/tools/cloud_recon.sh` | modified | #56 |
| `Actual-Setup/tools/secrets_hunter.sh` | modified | #56 |
| `Actual-Setup/tools/takeover_scanner.sh` | modified | #56 |
| `Actual-Setup/hooks/`, `Actual-Setup/scripts/`, `Actual-Setup/web3/` | **new** | #58 |
| `Standalone-Engine-Reference/docs/TODOS.md` | **new** | #56 |
| `Standalone-Engine-Reference/demo/`, `Standalone-Engine-Reference/docs/{advanced-techniques,payloads,auth-sessions,TUTORIAL,smart-contract-audit,auth.example.json}` | **new** | #58 |
| `Standalone-Engine-Reference/{LICENSE,TERMS.md,serve.py,pytest.ini,uninstall.sh,uninstall_tools.sh}` | **new** | #59 |
