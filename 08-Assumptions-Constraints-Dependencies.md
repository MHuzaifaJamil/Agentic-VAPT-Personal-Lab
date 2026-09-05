*(Informational only — this document records environmental assumptions, host constraints, external dependencies, and explicit non-goals. It outlines baseline operational prerequisites rather than functional pipeline requirements.)*

# Assumptions, Constraints, Dependencies & Non-Goals — Autonomous Agentic VAPT System

This document outlines the operational environment, physical hardware limitations,
dependency inventory, and structural boundaries governing the system. These constraints
frame the Dual-Mode Execution Architecture: physical memory limits mandate sequential
model swaps and memory reclamation, while operational boundaries strictly distinguish
autonomous non-destructive discovery from unconditional, operator-directed execution.

All security models, authorization assignments, and containment mandates cited across
these assumptions derive authoritatively from the Security Specification (`05`).
---

## AC-ASSUME — Assumptions

| ID | Assumption |
|----|-------------|
| AC-ASSUME-01 | The base document's hardware profile (Intel Core Ultra 5 125H, 15.3 GiB RAM, specific NVMe layout, Kali Debian 15.3 rolling) describes a **different physical machine** than this planning session's host. All paths/tuning throughout this requirements set inherit it verbatim. |
| AC-ASSUME-02 | The operator (Muhammad Huzaifa Jamil) is the sole user — no multi-tenant/multi-operator scenario is assumed anywhere. |
| AC-ASSUME-03 | The operator assumes full responsibility for independently confirming legal and contractual authorization for any tested target. The system enforces no internal legal or contractual gating — verification resides entirely with the human operator prior to execution. |
| AC-ASSUME-04 | Kali's rolling-release kernel/driver stack is assumed adequate for sustained AI-inference + tool workloads — **not verified**, and carries GPU-offload and thermal-throttling risk. |
| AC-ASSUME-05 | `kali-linux-everything` (or equivalent) is assumed installed on the target machine — not verified/installed by this planning phase. |
| AC-ASSUME-06 | Acceptance testing and validation milestones run against configured test targets or disposable containerized labs (e.g., Juice Shop, DVWA) as designated by the operator. |

## AC-CONSTRAINT — Hard Constraints

| ID | Constraint |
|----|-------------|
| AC-CONSTRAINT-01 | Total RAM fixed at 15.3 GiB — the entire single-residency, sequential-swap council design exists *because of* this, not stylistically. |
| AC-CONSTRAINT-02 | All agent-writable state/artifacts confined to the NVMe path — `tmpfs`/`/tmp` is a hard prohibition. |
| AC-CONSTRAINT-03 | Operator control surface is **CLI only** — no GUI/web dashboard in scope. |
| AC-CONSTRAINT-04 | The session budget, per-target task caps, and yield circuit breakers serve as operational defaults for autonomous execution. All thresholds can be extended, overridden, or disabled via CLI flags when commanded by the operator. |
| AC-CONSTRAINT-05 | Execution paths encompass standard binary locations (/usr/bin/, /usr/sbin/, /opt/) and operator-configured tool paths necessary for specialized testing suites. |

## AC-DEPENDENCY — External Dependencies

| ID | Dependency | Notes |
|----|-------------|-------|
| AC-DEPENDENCY-01 | `llama.cpp --server` | SYCL backend maturity unverified |
| AC-DEPENDENCY-02 | `ollama` (optional substitute) | Only if `llama.cpp`'s SYCL path proves inadequate |
| AC-DEPENDENCY-03 | Intel Level Zero/SYCL/OpenCL, `i915`/`xe` modules | Driver co-activity claim needs on-machine verification |
| AC-DEPENDENCY-04 | SQLite3 (WAL-capable) | Standard, low-risk |
| AC-DEPENDENCY-05 | `kali-linux-everything` tool suite | No install/version-pinning policy defined |
| AC-DEPENDENCY-06 | `pandoc` + `wkhtmltopdf`/`weasyprint` | Markdown→HTML/PDF, converter choice is implementation-time |
| AC-DEPENDENCY-07 | `claude-bug-bounty` toolkit + its `CLAUDE.md` | Exists only on this planning machine — cross-machine transfer needed |
| AC-DEPENDENCY-08 | GitHub (`github.com/MHuzaifaJamil`) | Docs version control only, not a runtime dependency |
| AC-DEPENDENCY-09 | The six council `.gguf` weight files (current roster, all `Q8_0`) | Acquisition source/provenance never specified — flagged, prerequisite for the model-acquisition build milestone. `Hermes-3-Llama-3.1-8B` derives from Meta's gated Llama 3.1 base — a legal read at acquisition time is worthwhile. |
| AC-DEPENDENCY-10 | Pinned Python manifest (Click, PyYAML, `cvss`, HTTP client) | Not yet created — deferred to build time |
| AC-DEPENDENCY-11 | Foundry (`forge`/`cast`/`anvil`) + third-party RPC endpoint | Web3 auditing — nobody's job yet |
| AC-DEPENDENCY-12 | `adb`, `apktool`, `jadx`, `frida-tools`/`objection`; physical Android + jailbroken iOS device | Mobile pentesting |
| AC-DEPENDENCY-13 | `graphw00f`, `clairvoyance`, `graphql-cop`, `gqlmap`, `wscat` | GraphQL auditing |
| AC-DEPENDENCY-14 | `sisakulint`, authenticated `gh` CLI | CI/CD security |
| AC-DEPENDENCY-15 | `cewler`, hashcat rule files | Credential-attack wordlist generation |
| AC-DEPENDENCY-16 | `interactsh-client` | Out-of-band confirmation for blind-injection detection |
| AC-DEPENDENCY-17 | Playwright/Puppeteer (CDP-capable headless browser) | Client-side request-signing reversal |
| AC-DEPENDENCY-18 | Slither, Echidna/Medusa | Smart-contract static/fuzz testing |
| AC-DEPENDENCY-19 | `solidity-audit-mcp` | Only if this MCP integration is pursued |
| AC-DEPENDENCY-20 | `rich`, `plotext`, `psutil` | Monitoring dashboard |
| AC-DEPENDENCY-21 | `Textual` | Interactive console |

## AC-NONGOAL — Explicit Non-Goals

| ID | Non-Goal | Rationale |
|----|-----------|-----------|
| AC-NONGOAL-01 | Authorization/RoE verification | Out of scope by decision — see `AC-ASSUME-03` |
| AC-NONGOAL-02 | GUI or web dashboard control surface | CLI only, by decision |
| AC-NONGOAL-03 | Automatic tool-signature/CVE-feed freshness | Deferred by explicit decision |
| AC-NONGOAL-04 | Remote/offsite backup | Local-only, no-cloud-dependency design |
| AC-NONGOAL-05 | Automatic artifact retention/pruning | Deferred — retained indefinitely until a deliberate policy decision |
| AC-NONGOAL-06 | Multi-tenant/multi-operator support | Single-operator by assumption (`AC-ASSUME-02`) |
| AC-NONGOAL-07 | Installing, downloading, or executing any part of this system | This entire document set is a planning-phase artifact |

---

## Authority & Conflict Resolution

This document formalizes system baselines, environmental dependencies, operational constraints,
and structural non-goals. In the event of any discrepancy, ambiguity, or conflict between
environmental assumptions, operational boundaries, and system governance mandates, the
**Security, Safety & Compliance Requirements (`05`)** serves as the final and supreme
authority across the entire system.
