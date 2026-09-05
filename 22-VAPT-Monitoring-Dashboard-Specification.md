# VAPT Monitoring Dashboard Specification — Autonomous Agentic VAPT System

`vapt_agent/cli/dashboard.py` specifies the architectural, polling, calculation, and visual contracts
for the terminal monitoring interface. It operates as an independent, strictly **read-only** module
with zero write authority over `state.db`. It runs independently from the orchestrator's
cooperative signal pipeline (`pause`/`resume`/`abort`) as a continuous 1.0 Hz live terminal
display (`rich` + `plotext`).

This specification defines the observability layer for the **Dual-Mode Execution Architecture**:
measuring live model residencies, single-residency integrity invariants, autonomous task-funnel
progress, and circuit-breaker strikes, while surfacing operator-directed command activity and
resource margins in real time.

All security policies, containment invariants, and execution authority models reflected across
these monitoring requirements derive authoritatively from the Security Specification (`05`).

---

## 1. Connection, Polling & State Resilience

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-DASHBOARD-01 | The dashboard MUST connect to `state.db` exclusively via `sqlite3.connect("file:<path>?mode=ro", uri=True)` — read-only, **without** `immutable=1`. It MUST NOT acquire write locks, issue `PRAGMA wal_checkpoint`, or otherwise interfere with the orchestrator's own WAL-mode writes. | M |
| FR-DASHBOARD-02 | Query cadence is fixed at **1.0 Hz**, using `rich.live.Live(..., screen=True, auto_refresh=False)` with an explicit, manually-triggered refresh each cycle — not `rich`'s own auto-refresh timer. | M |
| FR-DASHBOARD-03 | If `state.db` does not exist, or exists but its tables are empty (no engagement has been `start`ed yet), the dashboard MUST render an interactive waiting screen (amber/cyan, per the palette in §4) and MUST NOT throw an uncaught exception — this is an expected, not an error, state. | M |
| FR-DASHBOARD-04 | `SIGINT` (Ctrl+C) MUST be caught to restore normal terminal state (cursor visibility, exit the alternate screen buffer) before exiting — a dashboard crash or forced exit MUST NOT leave the operator's terminal in a broken state. | M |

## 2. Turn Tracking & Predictive Forecasting Engine

**Schema dependency:** the `model_invocation_logs` table's `turn_number` column and
load-bearing `ended_at IS NULL` semantics. No separate `engine_state` table.

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-DASHBOARD-05 | Before each model invocation, the orchestrator MUST assign `turn_number = COALESCE(MAX(turn_number), 0) + 1` for that `(engagement_id, role)` pair, then insert an **unfinalized** row (`started_at` set, `ended_at NULL`, no token/latency data yet) immediately — this is the write-path change the dashboard depends on to observe "currently generating" state without any new table. On completion, the same row is updated in place with `ended_at`, `prompt_tokens`, `completion_tokens`, `latency_ms`. | M |
| FR-DASHBOARD-06 | The dashboard MUST derive per-role state from `model_invocation_logs` alone: a row with `ended_at IS NULL` for a role means that role is currently generating (`RUNNING`); the absence of any in-flight row means that role is not currently generating. Historical per-role stats (`Turns Executed`, rolling latency, tok/s) are aggregated from finalized rows only. | M |
| FR-DASHBOARD-07 | The `RESIDENT`/`IDLE` display state (a model loaded in RAM but not currently generating) MUST only ever be shown for the **Operator** role — it is the only role that stays resident across multiple tasks in a per-target loop. Every other role (Strategist, Gate 1, Gate 3, Reporter) tears down immediately after each single invocation and MUST only ever display as `COLD` or `RUNNING`, never `RESIDENT`/`IDLE` — showing a non-Operator role as `RESIDENT` reflects a display bug, not a valid state, and SHOULD be flagged as such if it occurs. | M |
| FR-DASHBOARD-08 | At most one role's model may ever be `RUNNING` or `RESIDENT` at the same live instant, per the system's single-model-residency policy. The dashboard MUST treat more than one simultaneously-non-`COLD` row as an integrity alert (rendered distinctly, e.g. a bold-red banner), not a benign display state — this is evidence of an actual single-residency violation elsewhere in the system, not a rendering choice to accommodate. | M |
| FR-DASHBOARD-09 | Predictive remaining-turn count (`N_exp`) per role, computed each refresh cycle: **Operator** — `N_exp = T_pending + ceil(T_pending × max(0.10, R_retry))`, where `T_pending` is the count of `task_queue` rows with `status IN ('GATE1_APPROVED', 'PENDING')` and `R_retry = GATE2_BLOCKED_count / EXECUTED_count` (a floor of 0.10 avoids an underestimate when few or zero retries have occurred yet); **Gate 1** — count of remaining unvetted Strategist hypotheses; **Gate 2 (deterministic)** — N/A, no model, see `FR-DASHBOARD-11`; **Offline Linter** — real-time count of active Operator script submissions awaiting linting, shown only while Phase 4.2 is active; **Gate 3** — `COUNT(verified_vulnerabilities WHERE status = 'CANDIDATE')`; **Reporter** — `1` if Phase < 5, `0` once Phase 5 is reached and reporting is complete. All `N_exp` values are estimates, and MUST be visually marked as such (e.g. an `[EST.]` tag), never presented as guaranteed counts. | M |
| FR-DASHBOARD-10 | Time forecasting, computed each refresh cycle from `model_invocation_logs`: per-turn `Duration = latency_ms / 1000.0`; per-turn `Speed (tok/s) = completion_tokens / Duration`; `T_consumed = SUM(Duration)` across all finalized turns in the engagement; `t̄_turn` per role = the exponential moving average of that role's **last 3** completed turns (not a simple mean, and not the last 5 — an EMA responds faster to a role that's just sped up or slowed down); `T_remaining = Σ_role (N_exp_role × t̄_turn_role)`. Before a role has completed at least one turn (`N_done < 1`), its `t̄_turn` MUST fall back to the fixed hardware-benchmarked prior in `FR-DASHBOARD-12`, not zero or an undefined value. | M |
| FR-DASHBOARD-11 | Gate 2 (the deterministic command/argument validator) MUST be displayed as its own row distinct from the Offline Script Linter (`Qwen2.5-Coder-3B`) — Gate 2 has zero model dependence and Qwen2.5-Coder-3B is a separate, rarely-invoked model. Gate 2's row MUST show a fixed `N/A (deterministic)` in place of every model-only field (state badge, tok/s, turn count) — it never has a "turn," a "speed," or a "resident" state. The Offline Linter gets its own row with genuine model stats, populated only on the turns it's actually been invoked (between-phase only) — showing `0 / — tok/s` for the whole of Phase 4.2 is the expected, correct display, not a bug. | M |
| FR-DASHBOARD-12 | **Cold-start fallback priors** (used only until a role records its own first real turn, per `FR-DASHBOARD-10`): Strategist (`DeepSeek-R1-0528-Qwen3-8B`) ≈ 10.7 tok/s (~45s/turn); Operator (`Qwen2.5-Coder-7B-Instruct`) ≈ 28.5 tok/s (~15s/turn); Gate 1 (`Hermes-3-Llama-3.1-8B`) ≈ 11.0 tok/s (~8s/turn); Offline Linter (`Qwen2.5-Coder-3B-Instruct`) ≈ 28.5 tok/s (~4s/turn); Gate 3 (`Mistral-7B-Instruct-v0.3`) ≈ 12.1 tok/s (~12s/turn); Reporter (`Ministral-8B-Instruct-2410`) ≈ 11.0 tok/s (~180s for a full multi-pass synthesis). These are placeholder estimates for display purposes only, sourced from no benchmark run on this system's actual confirmed `Q8_0` roster — they MUST be labeled `[ESTIMATING]` in the UI and MUST NOT be treated as validated performance figures; a real pre-flight benchmark measures actual throughput separately and independently. | S |

## 3. Model-Matrix Display Semantics

The state-badge legend reflects the actual architecture, not a simplified illustration:

| Display state | Applies to | Meaning |
|---|---|---|
| `● RUNNING (Turn #N)` (bold green) | Any role | An in-flight, unfinalized `model_invocation_logs` row exists for this role right now. |
| `○ RESIDENT / IDLE` (bold cyan) | **Operator only** | Loaded, not currently generating, between tasks in its per-target loop. Never valid for any other role. |
| `◌ COLD / EVICTED` (dim blue) | Any role | No resident weights; the normal state for every non-Operator role between invocations, and for all roles before an engagement starts. |
| **Integrity alert** (bold red banner, distinct from the matrix rows) | System-wide | More than one role shows `RUNNING`/`RESIDENT` at once — a single-residency violation, not a display choice (`FR-DASHBOARD-08`). |

## 4. Visual Palette & Color Standard

Strict 24-bit TrueColor:

| Color | Hex | Meaning |
|---|---|---|
| Green | `#00FF66` / bold green | Active running model, normal latency (>15 tok/s), approved tasks, zero breaker strikes. |
| Cyan / Blue | `#00DFFF` / `#1E90FF` | Informational panels, cold/standby states, historical tok/s traces, verified low/info findings. |
| Amber / Yellow | `#FFD700` / bold yellow | Memory approaching the 1.5 GiB buffer, 1st/2nd breaker strikes, Gate 2 rejection→retry iterations. |
| Red | `#FF3333` / bold red | 3-strike circuit breaker trips, 1.5 GiB memory-margin breach, swap growth exceeding the confirmed 2 GiB threshold, critical vulnerabilities, and the §3 integrity alert. |
| Magenta | `#FF00FF` / bold magenta | High-severity vulnerabilities, active-phase indicators. |

## 5. Live Graphical Elements

All rendered via `plotext` inside `rich.panel.Panel`:

1. **Multi-trace tok/s line graph** — last 30 turns, color-coded by model family (DeepSeek = yellow, Qwen = green, Mistral = cyan, Hermes = magenta) — sourced from `FR-DASHBOARD-10`'s per-turn `Speed` values, not a separate telemetry stream.
2. **Multi-segment memory safety bar** — `[Resident Model] [Context/OS] [Safety Margin: 1.5 GiB] [Free]`, pulsing bold red if free memory infringes the confirmed 1.5 GiB safety margin.
3. **Task-queue funnel** — `Targeted → Gate 1 Pass → Executing → Gate 2 Blocked → Complete`, sourced from `task_queue.status` counts — every status value used here (`GATE1_APPROVED`, `EXECUTING`, `GATE2_BLOCKED`, etc.) already exists in the confirmed schema, no new values needed.

## 6. Screen Layout

The Gate 2 row shows `N/A (deterministic)` fields per `FR-DASHBOARD-11` (with the
Offline Linter as its own adjacent row), and the model matrix never shows two
simultaneously non-`COLD` rows in a genuine live snapshot per `FR-DASHBOARD-08`.
Layout structure: `rich.layout.Layout`, header / two-column body / footer graph row.

## 7. Implementation Directives

- **Dependencies:** `rich`, `plotext`, `psutil`.
- **Connection string:** see §1, `FR-DASHBOARD-01`.
- **Queries** (against the real schema):
  ```sql
  -- Per-role aggregate stats
  SELECT role, model_name,
         COUNT(*) FILTER (WHERE ended_at IS NOT NULL) AS turns_done,
         SUM(latency_ms) / 1000.0 AS total_duration_sec,
         AVG(completion_tokens * 1000.0 / NULLIF(latency_ms, 0)) AS avg_tok_per_sec
  FROM model_invocation_logs
  WHERE engagement_id = ?
  GROUP BY role, model_name;

  -- Currently active role
  SELECT role, model_name, started_at
  FROM model_invocation_logs
  WHERE engagement_id = ? AND ended_at IS NULL
  ORDER BY started_at DESC LIMIT 1;
  ```
- **Task/finding counters:** `task_queue`, `targets`, `verified_vulnerabilities` all carry the columns/status-values referenced (`GATE2_BLOCKED`, `CANDIDATE`, etc.).
- **Signal handling:** catch `SIGINT`, restore cursor visibility, exit cleanly (`FR-DASHBOARD-04`).
- **CLI entry point:** `vapt_agent/cli/dashboard.py`, registered as `vaptctl dashboard`.

---

## Authority & Conflict Resolution

This document governs read-only dashboard presentation, terminal telemetry polling, and forecasting
heuristics. In the event of any discrepancy, ambiguity, or conflict between visual status representations,
turn estimates, and core system governance mandates, the **Security, Safety & Compliance Requirements (`05`)**
serves as the final and supreme authority across the entire system.
