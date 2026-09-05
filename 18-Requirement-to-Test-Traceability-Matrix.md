# Requirement-to-Test Traceability Matrix & QA Verification Baseline — Autonomous Agentic VAPT System

**Quality Assurance & Verification Mandate:** This document defines the bidirectional traceability baseline between system requirement specifications and the Acceptance Criteria & Test Plan (`09`). It is an active Quality Assurance and Test Engineering specification. Test-suite implementers, QA automation agents, and acceptance verifiers must utilize this matrix to ensure complete verification coverage across all requirement clusters before milestone sign-off.

The traceability matrix verifies adherence to the **Dual-Mode Execution Architecture**:

* Validating that test suites rigorously assert non-destructive constraints during **Autonomous Mode** (ensuring safe reads and benign verification writes pass, while data drops, schema mutations, file tampering, and DoS payloads are blocked).
* Validating that test suites verify unconditional execution, zero automated refusal, and gate bypasses during **Operator-Directed Mode**.

All security controls, containment invariants, and test pass criteria tracked in this document derive authoritatively from the **Security, Safety & Compliance Requirements (`05`)**.

---

## 1. Traceability Methodology & Coverage Standards

Every testable requirement identifier across the specification corpus is tracked to concrete test fixtures, suites, and assertion blocks. Coverage is evaluated against three standard verification statuses:

* **Covered:** An explicit, citable test case in Document `09` (or an executable automated test suite) directly exercises the requirement's functional logic, operational thresholds, or failure modes.
* **N/A (Non-Executable / Contextual Baseline):** Environmental assumptions, hardware limits, external package dependencies, and informational risk entries. These define operational boundaries; their technical mitigations are verified under their respective functional and security requirement IDs.
* **NOT COVERED (Priority Verification Targets):** Testable requirements that lack dedicated unit-level test rows in the primary test plan and must be verified through composite integration passes or prioritized for test expansion.

---

## 2. Requirement Verification Matrix by Functional Domain

| Domain Area & Specification | Total Reqs | Covered | N/A | NOT COVERED | Primary Test Suite Reference (`09`) |
| --- | --- | --- | --- | --- | --- |
| Functional Behavior (`01`) | 103 | 62 | 1 | 40 | `TP-PHASE-01` through `TP-PHASE-05` |
| Non-Functional Targets (`02`) | 23 | 8 | 1 | 14 | `TP-PERF-01`, `TP-HEADROOM-01` |
| Data & Storage Schema (`03`) | 33 | 21 | 0 | 12 | `TP-DATA-01`, `TP-ARTIFACT-01` |
| Interface & Wire Formats (`04`) | 30 | 17 | 0 | 13 | `TP-IFACE-01`, `TP-TOOLSCHEMA-01` |
| Security, Safety & Compliance (`05`) | 28 | 18 | 0 | 10 | `TP-SEC-01` through `TP-SEC-05` |
| Operational Lifecycle (`06`) | 15 | 3 | 2 | 10 | `TP-OPS-01`, `TP-DEGRADE-01` |
| Risk Register & Mitigations (`07`) | 33 | 0 | 33 | 0 | Verified via mitigating `SEC-*`/`FR-*` tests |
| Environmental Constraints (`08`) | 28 | 0 | 28 | 0 | Verified via environmental pre-flight checks |
| Architecture Bridge & Contracts (`13`) | 8 | 4 | 2 | 2 | `TP-PROC-01`, `TP-HELPER-01` |
| Tool Reuse & Bridge Integration (`16`) | 20 | 16 | 0 | 4 | `TP-TOOL-REUSE-01` |
| Resilience & Evidence Grounding (`17`) | 15 | 11 | 0 | 4 | `TP-RESIL-01`, `TP-GROUND-01` |
| **Total Corpus Baseline** | **336** | **160** | **67** | **109** | **Acceptance Verification Baseline** |

---

## 3. Mandatory Acceptance Gates for QA Verification

QA engineers and test agents must enforce these specific verification suites prior to certifying Milestone 8 (Full Acceptance Pass):

1. **Dual-Mode Execution Verification:**
* Inject autonomous tasks containing destructive payloads (`DROP TABLE`, `rm -rf`, heavy traffic bursts) and confirm Gate 1/Gate 2 deterministic blocking.
* Inject identical commands via operator intervention (`origin = 'MANUAL_OPERATOR'`) and verify unconditional execution without refusal.


2. **Subprocess Lifecycle & Tiered Timeout Containment:**
* Execute test probes under Quick (180s), Targeted (900s), and Deep (1800s) timeout tiers.
* Confirm process-group termination (`killpg`) with zero orphaned child processes or dangling TCP sockets.


3. **Adjudication False-Positive Checklist:**
* Exercise Gate 3 test fixtures against simulated Cloudflare WAF block pages, generic 502/503 errors, and 429 rate-limit responses. Confirm candidate findings are classified as `DISMISSED`.


4. **Crash Recovery & State Integrity:**
* Simulate sudden process termination (`SIGKILL`) during active Phase 4.2 loops.
* Verify that re-executing `vaptctl resume` recovers queue state from SQLite WAL without re-running completed tasks or corrupting evidence maps.


5. **Evidence Grounding Rigor:**
* Submit mock finding drafts containing ungrounded endpoints or fabricated parameters. Confirm deterministic grounding rejects drafts back to the Reporter up to the 3-attempt ceiling.



---

## Authority & Conflict Resolution

This document specifies the authoritative test-coverage baseline and verification criteria for quality assurance and acceptance testing. In the event of any discrepancy, ambiguity, or conflict between test assertions, coverage classifications, and system governance mandates, the **Security, Safety & Compliance Requirements (`05`)** serves as the final and supreme authority across the entire system.
