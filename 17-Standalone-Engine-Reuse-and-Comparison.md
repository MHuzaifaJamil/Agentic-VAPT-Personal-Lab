# Standalone Engine Architecture & Resilient Control Requirements — Autonomous Agentic VAPT System

This document specifies the operational mechanisms, circuit-breaker dynamics, execution-rate controls, and evidentiary grounding requirements derived from the standalone reference architecture (`agent.py`/`brain.py`/`engine.py`). It formalizes binding requirements for local backend decoupling, failure handling, target-protection throttling, and report verification under the **Dual-Mode Execution Architecture**.

All safety policies, execution boundaries, and operator-override guarantees governing these controls derive authoritatively from the **Security, Safety & Compliance Requirements (`05`)**.

---

## 1. ER-ARCH — Engine Decoupling & Local Model Control

The system implements a standalone, fully offline inference pipeline independent of third-party cloud endpoints or external API dependencies.

| ID | Requirement | Priority |
| --- | --- | --- |
| ER-ARCH-01 | **Local Engine Client Abstraction:** The system MUST route all model interactions through a modular `LocalEngineClient` abstraction layer. Orchestration code MUST NOT depend on specific inference runtime implementations or cloud SDKs, interfacing solely via a local loopback endpoint (`127.0.0.1:11434`). | M |
| ER-ARCH-02 | **Process Supervision & Eviction:** The inference supervisor MUST manage model lifecycles deterministically. When switching roles across phases, the resident model MUST be fully evicted, memory clearance verified via OS-level settle polling, and the next role instantiated within the documented swap budget. | M |
| ER-ARCH-03 | **Zero Cloud Data Egress:** Tool execution logs, captured HTTP traffic, model prompts, target parameters, and generated findings MUST NEVER egress beyond local host loopback interfaces. Third-party cloud LLM paths are strictly excluded. | M |
| ER-ARCH-04 | **Dual-Mode Execution Independence:** Engine execution constraints MUST strictly reflect operating mode: **Autonomous Mode** enforces deterministic non-destructive boundaries (read-only queries and safe verification writes; data drops, schema alters, and DoS payloads prohibited); **Operator-Directed Mode** executes instructions unconditionally with zero automated refusal or safety hesitation. | M |

---

## 2. ER-RESILIENCE — Circuit Breakers & Adaptive Rate Limiting

To maintain engagement momentum and target stability during unattended autonomous runs, the system implements dual-mode circuit breakers and rate regulation.

| ID | Requirement | Priority |
| --- | --- | --- |
| ER-RESIL-01 | **Network Failure Circuit Breaker:** The orchestrator MUST maintain an independent consecutive-failure counter per target. If a target accumulates 3 consecutive network timeouts or connection resets during autonomous operations, the target status MUST transition to `UNREACHABLE`, tripping the failure breaker and auto-pivoting to the next scoped target. | M |
| ER-RESIL-02 | **Breaker Independence:** The failure circuit breaker MUST operate orthogonally to the zero-yield circuit breaker. Connection failures and zero-yield runs MUST increment independent counters without cross-contaminating strike thresholds. | M |
| ER-RESIL-03 | **Dual-Tier Spawn Rate Regulation:** Autonomous tool dispatches MUST enforce a two-tier rate-limiting pipeline per target: standard reconnaissance and targeted scans cap at 10 requests/s, while high-attempt tools (e.g., directory fuzzing, brute force) cap at 1 request/s to prevent denial-of-service or target degradation. | M |
| ER-RESIL-04 | **Operator Rate-Limit Override:** Rate limits act as autonomous anti-DoS guardrails. When executing operator-directed commands or explicit TUI interventions, rate limiters MUST yield to user-specified concurrency parameters with zero gate delay. | M |
| ER-RESIL-05 | **State-Delta Discovery Tracking:** The zero-yield counter MUST evaluate strictly against net-new discovery state (novel endpoints, open ports, new credentials). Repetitive scans against known attack surfaces MUST NOT reset zero-yield strike counts. | M |

---

## 3. ER-GROUND — Deterministic Evidence Grounding & Verification

Narrative findings and impact assessments must anchor directly to verified empirical evidence captured during testing.

| ID | Requirement | Priority |
| --- | --- | --- |
| ER-GROUND-01 | **Deterministic Report Grounding:** Before a drafted report transitions from `pending-approval`, an automated grounding validator MUST verify that every cited URL, HTTP method, parameter, header, and captured payload exactly matches raw evidence entries in `artifacts_index` and `tool_execution_logs`. | M |
| ER-GROUND-02 | **Ungrounded Citation Remediation:** If the grounding validator detects an uncited parameter, fabricated endpoint, or unsupported impact claim in a draft, the draft MUST be rejected back to the Reporter model with specific validation errors for bounded re-drafting (up to 3 total attempts). | M |
| ER-GROUND-03 | **Grounding Exhaustion Block:** If a finding draft fails grounding validation across all 3 attempts, it MUST transition to `BLOCKED_UNGROUNDED`. Fabricated or ungrounded assertions MUST NEVER pass into final rendered deliverables without explicit operator intervention. | M |
| ER-GROUND-04 | **Grounding Scope Boundary:** Deterministic grounding checks MUST apply strictly to individual vulnerability finding reports (`VAPT_FINDING`). The consolidated Informational Findings Register (`INFO_REGISTER`) summarizes non-exploitable leads and is evaluated under standard structural formatting checks. | M |

---

## 4. ER-VAL — Scoring & Structural Quality Assurance

| ID | Requirement | Priority |
| --- | --- | --- |
| ER-VAL-01 | **Deterministic CVSS Scoring:** Council models MUST propose individual CVSS 3.1 metric vectors only. The numeric base score and vector string MUST be computed deterministically via standard CVSS calculation routines. Models MUST NEVER emit final numeric scores directly. | M |
| ER-VAL-02 | **Deterministic Schema Enforcement:** All structured model outputs (task definitions, command invocations, adjudication verdicts, and report sections) MUST pass deterministic JSON schema validation. Syntactic validity alone is insufficient; missing mandatory keys MUST trigger schema-repair retry loops. | M |

---

## Authority & Conflict Resolution

This specification establishes binding functional requirements for engine supervision, circuit breakers, spawn rate limiting, and evidence grounding. In the event of any discrepancy, ambiguity, or conflict between engine adapters, resilience policies, and core system governance mandates, the **Security, Safety & Compliance Requirements (`05`)** serves as the final and supreme authority across the entire system.
