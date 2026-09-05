# Acceptance Criteria & Test Plan — Autonomous Agentic VAPT System

Methods: **Demo** / **Inspection** / **Test** / **Analysis**. Grouped by requirement cluster;
each row states the verification method and pass criterion self-contained and independently.
Testing criteria validate the Dual-Mode Execution Architecture: verifying that Autonomous Mode
strictly enforces non-destructive boundaries (reads and safe verification writes only, barring
destructive data mutations and DoS), while Operator-Directed Mode executes human instructions
unconditionally with zero automated refusal or technical boundary interception.

All security invariants, verification models, and override behaviors evaluated in this plan
derive authoritatively from the Security Specification (`05`).

## TP-PRE — Pre-Flight

| Test | Method | Pass Criteria |
|---|---|---|
| Missing tool binary | Test | Hide `nmap`; pre-flight fails naming it specifically, blocks Phase 1. |
| GPU benchmark | Test | Both GPU/CPU tok/s recorded; if GPU ≤ CPU, engagement flagged CPU-only in `engagement_phase_log`. |
| Model file integrity | Test | Corrupt one `.gguf`; pre-flight fails on that model. |
| Operator override | Inspection | A failed check proceeds only with a logged justification, visible in export. |
| Engine already running | Test | Pre-flight detects it, blocks Phase 1, no duplicate spawn. |
| NVMe path validation | Test | Distinct failures for tmpfs / read-only / missing path. |
| Baseline snapshot | Inspection | RAM/swap/disk recorded before Phase 1. |

## TP-ENV — Hibernation & OOM Protection

| Test | Method | Pass Criteria |
|---|---|---|
| No interactive prompt | Test | Zero prompts through Phase 1 including first `SIGSTOP`. |
| No `/tmp` writes | Test | All artifacts/logs/temp files resolve to NVMe. |
| Denylist classification | Test | `dbus`/compositor classified "protected" before any signal. |
| Suspended-tree record | Inspection | PID list sufficient to reverse without re-discovery. |
| OOM deprioritization | Inspection | `oom_score_adj` set before the pressure step. |
| OOM casualty detection | Test (fault injection) | Missing PID logged as partial success, not full. |
| Locked-file protection | Test | A locked-file app is never `SIGSTOP`'d. |
| Privileged helper isolation | Inspection | Main process holds no capability; only the dedicated freezer-helper process does. |
| cgroup v2 fallback | Test (fault injection) | Capability removed → cgroup fallback, logged degraded. |
| Stale-socket SLA documented | Inspection | Status output states process-memory-only guarantee. |

## TP-RESUME — Phase 1 Exit & Resumability

| Test | Method | Pass Criteria |
|---|---|---|
| `IN_PROGRESS`/`PAUSED` offered for resume | Test | `start` offers resume, doesn't overwrite. |
| Schema present pre-Phase-2 | Inspection | Required tables exist before Phase 2. |
| Headroom re-check aborts on shortfall | Test | Capped RAM → Phase 2 aborted, not attempted. |
| Resume re-measures, doesn't trust stale state | Test | Resumed `PAUSED` run re-checks headroom. |

## TP-GATE — Inference Gateway

| Test | Method | Pass Criteria |
|---|---|---|
| Single residency | Test | Second load fully unloads first, OS-level verified. |
| Model-swap budget | Test | >60s flagged degraded, not failed. |
| Engine crash recovery | Test (fault injection) | One restart, then `PAUSED` on repeat failure. |
| Backend swap feasibility | Analysis | No engine-specific assumption in orchestration code. |
| Memory-settle gate | Test | Next model load blocks until available memory clears; 5s bound raises degraded alert. |
| Loopback-only binding | Test | Endpoint listens only on `127.0.0.1:11434`. |
| P-core pinning | Inspection | `Cpus_allowed` shows only the 4 P-Cores. |
| GPU fallback at startup | Test (fault injection) | Backend unavailable → CPU-only, logged degraded. |
| Eviction verified | Test | Actual freed memory checked, not just an API ack. |
| Context ceiling enforced | Test | All 6 models truncate/summarize on overflow, never error. |
| Endpoint stable across backend swap | Test | Identical OpenAI-compatible surface for both backends. |

## TP-COUNCIL1 — Two-Tier Scope Gate

| Test | Method | Pass Criteria |
| --- | --- | --- |
| Tier 0 blocks out-of-scope CIDR in Autonomous Mode | Test | Autonomous task rejected before the semantic tier is invoked; logged in invocation records. |
| Operator directive bypasses Gate 1 | Test | Operator-directed task (`MANUAL_OPERATOR`) bypasses Tier 0 and Tier 1 checks completely, dispatching directly to execution. |
| Tier 1 reasoning persisted | Test | Autonomous contextually-excessive-but-in-scope task rejected with rationale. |
| Prompt-injection resistance | Test | Injection string in target response doesn't alter gate decisions. |

## TP-COUNCIL2 — Resident Operator + Deterministic Gate 2

| Test | Method | Pass Criteria |
|---|---|---|
| No swap during active loop | Test | One Operator load event per target loop; zero linter-model loads during it. |
| Deterministic rejection | Test | Malformed command rejected sub-second, no model call. |
| Correction bound | Test | 4th consecutive invalid command → `BLOCKED`, not retried indefinitely. |
| Offline syntax-check fallback | Demo | The lightweight syntax-check model is invoked only between phases for script checks. |
| Follow-on appended, not acted out-of-band | Test | Pivot task appended to the task queue, no direct action taken. |
| Unload timing | Test | Operator stays resident until every target is terminal or the session budget hits. |

## TP-COUNCIL3 — Gate 3 Adjudication

| Test | Method | Pass Criteria |
|---|---|---|
| WAF/rate-limit/5xx/honeypot dismissed | Test | Each pattern individually fails to reach `CONFIRMED`. |
| Base checklist necessary but not sufficient | Test | Passes base pattern checks but fails the impact/evidence-structure checks → still blocked, tracked as distinct fields. |
| Genuine finding confirmed | Test | Passes both check sets → `CONFIRMED`. |
| "Technically possible" insufficient | Test | Bare `alert(1)` → not confirmed; real cookie exfil → confirmed. |
| IDOR needs cross-identity proof | Test | Same data with zero auth → not IDOR, flagged as missing-auth instead; real cross-identity evidence → confirmed. |
| Baseline/attack/diff enforced | Test | Attack-only evidence (no baseline) blocks confirmation regardless of how convincing. |

## TP-LOOP — Diminishing-Returns Thresholds

| Test | Method | Pass Criteria |
|---|---|---|
| Per-target task cap | Test | 31st task → `CAPPED`, auto-pivot. |
| Zero-yield breaker (state-delta) | Test | 3 non-empty-but-zero-novel runs → `CIRCUIT_BROKEN`. |
| Noisy-tool false-reset prevented | Test | A run against an already-discovered entity does not reset the counter. |
| Global session budget | Test (accelerated clock) | All targets auto-terminate, evidence-adjudication phase begins. |
| Manual pause independent | Test | `pause` works mid-loop regardless of automatic thresholds. |
| Failure breaker independent of yield breaker | Test | 3 network-error runs → `UNREACHABLE`, not `CIRCUIT_BROKEN`. |
| Counters don't cross-contaminate | Test | 2 failures + 1 zero-yield success trips neither breaker. |
| Rate limit queues, doesn't reject | Test | 20 rapid tasks → ≤10 spawns/s, none dropped. |
| High-risk rate stricter | Test | Brute-force-category tooling caps at 1/s. |
| Rate limiting is per-target | Test | One target's cap doesn't throttle another. |

## TP-TIER2 — Allowlist, Denylist & Opt-In Flags

| Test | Method | Pass Criteria |
|---|---|---|
| Path resolution | Test | Symlink resolving outside the three directories refused. |
| Behavioral denylist (a)-(e) | Test | One test per rule — each refused, matching rule logged. |
| High-risk refusal without flag | Test | An unflagged high-risk tool → `POLICY_REFUSED`, loop continues. |
| Opt-in flag enables category | Test | The brute-force opt-in flag set via `resume` permits it, logged in the flag-history table. |
| Flag change is forward-only | Test | Already-queued task not retroactively re-evaluated. |
| Unaffected tools stay autonomous | Test | An unlisted Tier 2 binary needs no flag. |
| Operator sees flag state | Inspection | Disabled-category tool not repeatedly proposed against the same target. |
| No shell interpolation | Test | Shell metacharacters in any argument never reach a shell interpreter. |
| Denylist fires before spawn | Test | Rejection happens pre-execution, logged with the matched rule. |

## TP-INJECT — Prompt-Injection Defense

| Test | Method | Pass Criteria |
|---|---|---|
| Tag integrity under adversarial input | Test | A forged closing tag in target content is escaped/stripped before wrapping. |
| Instruction-hierarchy clause present | Inspection | Present in every council model's system prompt. |
| Heuristic detector logging | Test | Flag set in the tool-execution log, surfaced in export. |
| Unicode/MCP smuggling detected | Test | Tag-block and line-jumping patterns both flagged. |
| Sanitizer produces common structured record | Test | 3+ tool types all produce the same `{ports,banners,urls,status_codes,raw_artifact_ref}` shape. |
| Detector absence doesn't weaken containment | Test (fault injection) | Detector disabled, injection still contained by tagging + instruction hierarchy. |

## TP-CVSS — Deterministic CVSS 3.1

| Test | Method | Pass Criteria |
|---|---|---|
| LLM never emits final score | Inspection | Output schema has metrics + justification only. |
| Calculator correctness | Test | Matches a published FIRST.org reference score. |
| Version lock | Inspection | `cvss_version` hardcoded `3.1` everywhere. |

## TP-STRUCTURED — Structured Output

| Test | Method | Pass Criteria |
|---|---|---|
| `response_format` requested | Inspection | Present on all 6 prompted roles. |
| Schema validation catches conformance gaps | Test | Valid JSON missing a required field is still rejected. |
| Bounded retry | Test | 2 failures → error fed back; 3rd failure → `BLOCKED`. |
| Single-engagement lock | Test | Concurrent `start` refused; unique-index rejects a bypassed direct insert too. |
| Lock releases on completion | Test | New `start` accepted once `COMPLETE`/`ABORTED`. |
| Schemas are standalone files | Inspection | All 5 output-type schemas exist independent of prompt text. |

## TP-REPORT — Report Pipeline

| Test | Method | Pass Criteria |
|---|---|---|
| Reporter is a distinct model load | Test | The Reporter's load event is distinct from the Strategist's. |
| CWE/CVE mapping | Test | Present where applicable, null when not fabricated. |
| Root-cause + remediation present | Inspection | Both present, distinct from the CVSS calculator's output. |
| Draft redaction | Test | Secret shows as a placeholder in `pending-approval/`. |
| Redaction pre-Reporter | Inspection | Redaction runs on evidence before the Reporter call, never post-hoc. |
| Approval triggers unredaction + render | Test | `approve-report` restores the exact value, renders HTML/PDF, only then. |
| No other trigger renders | Test | Neither completion nor budget expiry renders anything. |
| Formatting-standard compliance | Inspection | The formatting standard's automated grep checks all return no output. |
| Per-finding vs. register split | Test | 2 confirmed + 3 dismissed → 2 individual finding-report rows + 1 consolidated register row. |
| Consolidated register regenerates, doesn't multiply | Test | A 4th dismissed item updates the existing row. |
| Grounding catches an ungrounded reference | Test | Uncited URL detected, draft not passed through unmodified. |
| Grounding retry then block | Test | 3 failures → `BLOCKED_UNGROUNDED`, not silently emitted. |
| Grounding scoped to individual findings only | Inspection | The consolidated register is not subject to the same check. |

## TP-KILL — Emergency Stop

| Test | Method | Pass Criteria |
|---|---|---|
| Kill-switch timing | Test | Full stop ≤20s, `ABORTED` set atomically. |
| Escalation | Test | `SIGTERM`-ignoring process `SIGKILL`'d within budget. |
| Abort still restores apps | Test | Restoration still runs after `abort`. |
| Process-group kill | Test | No child of a multi-process tool survives `abort`. |
| Spawn uses new session | Inspection | Each subprocess spawns its own session. |

## TP-RESOURCE — Resource Thresholds

| Test | Method | Pass Criteria |
|---|---|---|
| RAM margin abort | Test | Load aborts, engagement pauses, doesn't crash. |
| Disk thresholds | Test | Warning at 85%, hard block at 95%. |
| E-core thread cap | Inspection | Tool subprocess scheduling capped at 4 threads. |
| WAL mode | Inspection | Concurrent `status` read succeeds mid-write. |
| Busy-timeout under contention | Test | `pause`/`abort` retries, doesn't raise `database is locked`. |
| Redaction hash verification | Test | Truncated artifact → `approve-report` fails loudly. |
| Redaction round-trip on duplicate tokens | Test | Offset addressing restores the correct occurrence. |
| Combined headroom ceiling | Test | Model load blocked before exceeding ~13.0 GiB. |
| No `tmpfs` writes | Inspection | Static grep confirms none. |
| Swap growth flagged at 2 GiB | Test | Alert fires exactly at the confirmed threshold. |
| Disk block gates the index write too | Test | 95% fill blocks the artifact-index insert, not just the file. |
| All 4 phase-level metrics tracked continuously | Test | Sampled repeatedly, never only at start. |
| Log volume counts against quota | Test | Log-only growth measurably moves the tracked usage %. |

## TP-MULTI — Multi-Target Support

| Test | Method | Pass Criteria |
|---|---|---|
| Independent per-target counters | Test | One `CAPPED` target doesn't affect another's counters. |
| Artifact isolation | Inspection | Each target's output under its own subtree. |
| Raw output precedes sanitization | Test | Raw file written before summarization, named deterministically. |

## TP-CONFIG — Scope & Config Loading

| Test | Method | Pass Criteria |
|---|---|---|
| `scope.yaml` ingested correctly | Test | Allow/deny entries become correct scope-rule rows. |
| Missing config falls back to documented defaults | Test | `start` with no `--config` uses the system's documented default configuration. |

## TP-CLI — CLI Command Surface

| Test | Method | Pass Criteria |
|---|---|---|
| All subcommands exist with documented flags | Inspection | Match the documented CLI command surface exactly, no undocumented required flags. |
| `start` seeds engagement, no RoE gate | Test | Scope seeded; no authorization artifact requested. |
| `status` reports all 5 required fields | Test | Phase, resident model, RAM/swap, queue depth, finding counts. |
| All subcommands non-interactive-capable | Test | Each completes with flags/args only. |
| `status` supports human + JSON | Test | `--json` carries the same data as the table form. |
| `resume` flag semantics | Test | Passing one flag updates it; omitted flags stay unchanged. |
| `status` reflects live state | Test | Mid-session query matches live monitoring, not a start-time snapshot. |

## TP-USE — Usability

| Test | Method | Pass Criteria |
|---|---|---|
| Status readable without SQLite | Demo | Understandable from CLI output alone. |
| Logs are structured JSONL | Inspection | Tool/model layer JSON, report stays prose. |
| Error states surface plain-language reasons | Test | Blocked task / degraded GPU / abort all readable. |

## TP-MAINT / TP-PORT

| Test | Method | Pass Criteria |
|---|---|---|
| Model roles config-driven | Test | Swap a model's identity via config only, no code change. |
| Tool schemas declarative | Inspection | New tool needs no prompt edit. |
| Sanitization modular | Inspection | New parser added without touching the core loop. |
| Kali-specific deps isolated | Inspection | Confined to documented modules. |
| Hardware tuning is config | Analysis | Degrades to a logged fallback on different hardware. |

## TP-SECPOST — Local-Only Operation

| Test | Method | Pass Criteria |
|---|---|---|
| Loopback-only by default | Test | Non-loopback connection refused without explicit config change. |
| No data leaves the host | Test | Zero outbound calls to any non-target, non-loopback destination. |
| Destructive actions independently auditable | Test | Reconstructable from logs alone, no re-run needed. |

## TP-TIMEOUT — Tiered Timeouts

| Test | Method | Pass Criteria |
|---|---|---|
| Quick Probes = 180s | Test (fault injection) | Killed at 180s against a blackholed target. |
| Targeted Scans = 900s | Test | Killed at 900s, confirms non-Quick-Probe tier placement. |
| Deep/Full-Range = 1800s | Test | Killed at 1800s, not truncated earlier. |
| Timeout driven by classification | Inspection | Looked up per-tool tier, not a flat constant. |
| Timeout kills the whole tree | Test | No child survives. |
| Stall detected before hard timeout | Test | A connection accepted but silent is caught early via streaming. |
| Hung process can't extend the session budget | Test | Terminated well inside its tier ceiling, measured. |
| Timeout feeds failure classification | Inspection | Sets `timeout_hit=1`/`exit_code=NULL` for downstream failure-breaker classification. |

## TP-BACKUP — State Backup & Retention

| Test | Method | Pass Criteria |
|---|---|---|
| Backup gates Phase 5 completion | Test | Timestamped backup exists before Phase 5 logs complete. |
| Backup stays local | Inspection | No network destination in the backup routine. |
| Dismissed/non-yielding raw output survives | Test | Both remain in the artifact index post-completion. |
| `state.db` is the source of record | Inspection | Backup targets `state.db`, not a derived report export. |
| Backup pruning is manual | Test | No automatic pruning across multiple engagements. |

## TP-TIER1 — Tier 1 Schema Coverage

| Test | Method | Pass Criteria |
|---|---|---|
| All 12 Tier-1 tools have a schema-validated wrapper | Inspection | Binary name, path, flags, forbidden combos, timeout class all present. |
| Wrapper declares combos | Inspection | Sampled wrappers expose all fields machine-readably. |
| Linter rejects a forbidden combo | Test | `sqlmap --os-shell` rejected pre-spawn with the specific reason cited. |
| Operator schema and Gate 2 schema can't disagree | Inspection | Both generated from the identical source file. |

## TP-SANITIZE — Sanitization & Raw Persistence

| Test | Method | Pass Criteria |
|---|---|---|
| Structured signal extracted, noise discarded | Test | Context contains signal only. |
| Full raw output persisted regardless | Test | Byte-for-byte, independent of summarization. |
| Raw persistence survives parser failure | Test (fault injection) | Malformed output still persists in full. |

## TP-EXT / TP-MCP — Third-Party Integration

| Test | Method | Pass Criteria |
|---|---|---|
| MCP configs/prompt templates exposed as assets | Demo | Available without Burp/Caido installed. |
| Third-party tools integrate via env vars only | Test | Zero source modification. |
| No hardcoded cloud endpoint fallback | Inspection | None found via grep. |
| Core loop functions with none installed | Test | All lifecycle phases complete normally absent all three. |
| MCP configs are versioned files | Inspection | Not inline in orchestration code. |
| MCP output passes the same untrusted pipeline | Test | Same tagging/instruction-hierarchy treatment as any other tool. |

## TP-STRATEGIST — Plan Generation

| Test | Method | Pass Criteria |
|---|---|---|
| Ordered task queue reflects seeded scope | Test | Not scope-blind. |
| Output is structured, not prose-only | Test | Machine-parseable list with rationale. |
| Malformed output rejected | Test (fault injection) | Free-prose response triggers schema-validation retry. |

## TP-HIBEXIT — Hibernation Exit & Restoration

| Test | Method | Pass Criteria |
|---|---|---|
| State marked before teardown | Inspection | Status write commits before any teardown action. |
| Eviction verified before restoration | Test | Freed memory checked first. |
| Missing suspended process logged, not fatal | Test (fault injection) | Discrepancy logged, rest of restoration continues. |
| Restoration time reported | Inspection | Sub-2s expectation noted as SHOULD, not a hard gate. |

## TP-AUDIT — Log Structure & Immutability

| Test | Method | Pass Criteria |
|---|---|---|
| Full timeline reconstructable from logs alone | Inspection | Every invocation/gate decision traceable without re-running. |
| Rejected/dismissed records never removed | Test | Survive subsequent normal operations unmodified. |
| Logs are structured/machine-reconstructable | Inspection | Valid JSON-serializable rows. |
| Degraded events distinguishably severe | Test | All 4 named conditions logged at a distinct severity. |

## TP-LIFECYCLE — Phase Sequencing & Crash Safety

| Test | Method | Pass Criteria |
|---|---|---|
| Phase sequence and logging | Test | Exact order, all phase-log fields populated. |
| `resume` re-enters correctly | Test | Re-enters at the council-execution phase, skips redundant hibernation. |
| Agent-process crash doesn't lose engagement data | Test (fault injection) | At most the in-flight step lost; `resume` continues from last commit. |

## TP-CHECKPOINT — Human Checkpoint Gate

| Test | Method | Pass Criteria |
| --- | --- | --- |
| Autonomous checkpoint proposal logs event | Test | In Autonomous Mode, matching action class creates a `checkpoint_events` row (`status = 'AWAITING_APPROVAL'`) and pauses progression for operator visibility. |
| Direct operator dispatch executes immediately | Test | When explicitly commanded or dispatched by the operator, matching task executes immediately (`approved_via = 'OPERATOR_DIRECTIVE'`, `status = 'APPROVED'`) with zero pause or gate refusal. |
| No auto-timeout-to-approve in Autonomous Mode | Test | Autonomous task awaiting checkpoint approval stays paused indefinitely until the operator acts. |
| Approve executes exactly one task | Test | Specific autonomous checkpoint row marked `APPROVED`, execution resumes for that task only. |
| Deny skips the task, not the engagement | Test | Specific autonomous checkpoint row marked `DENIED`, task marked `BLOCKED_BY_OPERATOR`, engagement loop continues. |
| Attestation fields optional for operator dispatch | Test | Absence of pre-flight white-cell or disclosure attestation flags does not prevent operator-directed command dispatch or execution. |
| Live-spray lockout ceiling enforced autonomously | Test | Autonomous spray computes lockout estimate; exceeds ceiling → pauses for review. Operator-directed spray executes immediately per supplied user lists and concurrency parameters. |
| CI/CD external-artifact dual-mode execution | Test | In Autonomous Mode, external PR or workflow trigger pauses for checkpoint review; operator directive dispatches directly to the repository endpoint without holding. |
| Dependency-confusion publish/unpublish verification | Test | Callback-only non-destructive PoC used; autonomous publishing pauses at checkpoint; operator-directed publishing and unpublishing execute immediately as instructed. |


## TP-MONITOR — Scheduled Monitoring

| Test | Method | Pass Criteria |
|---|---|---|
| Detects a diff, logs without escalating | Test | Diff logged, no task queued, no active testing begins. |
| Model-free, doesn't hibernate | Inspection | No inference-engine or freezer-helper call. |
| Doesn't participate in the single-engagement lock | Test | Runs against a `COMPLETE` engagement while another is active. |
| No self-scheduling | Inspection | No cron/systemd/background-loop registration anywhere in code. |

## TP-DASHBOARD — VAPT Monitoring Dashboard

| Test | Method | Pass Criteria |
|---|---|---|
| Read-only connection never blocks the orchestrator | Test | Read-only mode without an immutable-connection flag; no lock errors either direction. |
| Waiting screen on empty state.db | Test | Renders cleanly, no crash. |
| Ctrl+C restores terminal state | Test | Clean exit, cursor restored. |
| Turn number monotonic per role | Test | Never reused or skipped. |
| In-flight row observable before completion | Test | An unfinished invocation row is visible mid-invocation. |
| `RESIDENT` never shown for non-Operator roles | Test | Every other role is `COLD`→`RUNNING`→`COLD` only. |
| Single-residency violation triggers the integrity alert | Test (fault injection) | Two simultaneous unfinalized rows → red banner, not silent display. |
| Gate 2 and the offline syntax linter are separate rows | Test | Gate 2 shows `N/A (deterministic)`; the linter shows real (mostly zero) stats. |
| Turn-forecast formulas match confirmed definitions | Test | Matches per-role formula including the 0.10 retry-ratio floor. |
| Cold-start priors replaced once real data exists | Test | An estimating tag is shown until the first real turn completes. |
| Swap-growth alert at 2 GiB | Test (constrained) | Fires exactly at the threshold. |

## TP-TUI — Interactive TUI Console

| Test | Method | Pass Criteria |
| --- | --- | --- |
| Console excludes host telemetry | Inspection | Interface displays event stream, journal, and command bar only; no host hardware/telemetry clutter. |
| Journal captures full record within memory bound | Test | 5,000+ lines rendered while console RSS remains ≤120 MiB. |
| Console detects engagement-state change | Test | Stops accepting runtime interventions once the engagement transitions to a terminal state (`COMPLETE`, `ABORTED`). |
| Offline linter has parity with other roles | Test | Directive prefix for offline linter fetched and injected identically to other council roles. |
| Operator precedence executes unconditionally | Test | Direct operator command executes with top priority, bypassing autonomous scope boundaries and checkpoint blocks with zero automated refusal. |
| Manual-operator origin skips both Gate 1 tiers | Test | `MANUAL_OPERATOR`-origin task skips Tier 0 deterministic scope check and Tier 1 semantic evaluation, recorded in the audit trail as direct operator dispatch. |
| Explicit console dispatch auto-attests checkpoint | Test | Console dispatch of sensitive tasks executes immediately without pausing; audit trail logs `approved_via = 'OPERATOR_DIRECTIVE'`. |
| Model-derived checkpoint actions pause autonomously | Test | Only explicit human operator input receives the immediate execution path; autonomous model escalations pause at the checkpoint. |
| No silent expiration | Test | Expired or discarded directives record a specific descriptive failure reason in `operator_command_queue.failure_reason`. |
| Journal content unredacted | Inspection | Live audit journal displays raw execution output consistent with local disk artifacts, not filtered through final report redaction. |
| 500-char cap enforced | Test | Input buffer rejects strings exceeding 500 characters client-side before queuing. |



## TP-DEDUP — Historical State Deduplication

| Test | Method | Pass Criteria |
|---|---|---|
| Strategist receives exclusion context | Test | Explored-attack-path context is present in the second engagement's prompt. |
| Gate 2 blocks exact-duplicate commands | Test | Rejected via the existing retry pipeline as a duplicate command; task count not incremented. |
| Command-hash canonicalization avoids false positives | Test | Swapped flag/value pairs hash differently. |
| Retest mode always surfaces a visible outcome | Test | Still-vulnerable → carried-forward report; remediated → consolidated register. |
| Regression-origin tasks get zero gate exceptions | Test | Narrowed scope still rejects it exactly as a fresh proposal would. |

## TP-OPFLEX — Operational Flexibility Fixes

| Test | Method | Pass Criteria |
|---|---|---|
| sqlmap symlink resolution fixed | Test | Executes correctly via the invocation-path check. |
| Suffix anchoring admits same-zone subdomains, excludes lookalikes | Test | `aws.abc.com` in, `abc.com.attacker.com` out. |
| `script_runner` never runs inline code | Test | Invalid script blocked pre-spawn; valid script runs as a file argument only. |
| `workspace_subdir` bounded to the artifact path | Test | Outside path rejected pre-execution. |
| Class-aware breakers don't cross-contaminate | Test | Standard (3) and high-attempt (15) breakers track independently. |
| `--max-target-tasks` is configurable and ceiling-bounded | Test | 60 accepted; 150 rejected (hard ceiling 100). |
| Grounding accepts cross-artifact synthesis, blocks fabrication | Test | Multi-artifact-sourced URL passes; wholly-uncited hostname still blocks. |
| Phishing/MFA-bypass is checkpoint-gated, not autonomous | Test | Flag set → still pauses; unset → `POLICY_REFUSED`. |
| Blanket checkpoint pre-authorization was not implemented | Inspection | No `--preauthorize-checkpoints`-style mechanism exists anywhere — only the console-dispatch auto-attestation and the live-spray auto-approval threshold skip the pause, both narrowly scoped. |
| `--max-auto-lockout-threshold` only skips the pause at/under the ceiling | Test | 10% at threshold 10 → auto-approved with both values recorded; 15% → full pause regardless. |
| Default threshold applies without the flag; `resume` can change it | Test | Past events retain the threshold active at their own time, not retroactively changed. |

## TP-FEASIBILITY — Deployment-Time Only

Items that cannot be verified against a written specification alone — they
require the actual deployed hardware/software stack to observe:

| Item | Why it's deployment-time only |
|---|---|
| Thermal/throttle telemetry availability | Depends on the real hardware's sensor exposure. |
| Actual GPU driver binding | Documentation-only until validated against the real GPU/kernel combination. |
| SYCL backend stability under sustained load | Requires the real hardware's thermal/power behavior over an extended run. |
| Engine smoke test after a kernel/driver update | Only meaningful once a live system has an update to test against. |
| Context-window management over a long task-queue loop | Structurally not testable in advance — no adopted mitigation technique exists to verify. |

## Acceptance Boundary Statement

No test in this plan asserts "zero false positives" or "zero hallucinated
findings" — the adjudication checklist and the documented downgraded-severity
language are the agreed control; residual judgment-error risk is accepted, not
tested away.

---

## Authority & Conflict Resolution

This test plan formalizes pass/fail criteria, verification procedures, and acceptance
boundaries. In the event of any discrepancy, ambiguity, or conflict between test
definitions, expected outcomes, and system execution mandates, the **Security, Safety &
Compliance Requirements (`05`)** serves as the final and supreme authority across the entire system.
