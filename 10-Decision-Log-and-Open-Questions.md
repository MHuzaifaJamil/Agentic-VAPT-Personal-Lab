# Decision Log & Open Questions — Autonomous Agentic VAPT System

Every substantive decision in `01`-`09`/`11`/`12` traces back to an explicit answer
given during this planning session — none were assumed. This document is the
chronological record of *why* the requirements read the way they do, so a future
reader isn't left guessing why (for example) there's no authorization gate, or why
Council Gate 1 no longer uses Hermes-3.

---

## Decisions On Record

| # | Decision | Rationale / Trigger |
|---|---|---|
| 1 | `/home/mhj/...` paths kept verbatim, not updated to this session's machine | Base doc describes a different physical PC than this planning session ran on |
| 2 | Operator control surface (start/pause/resume/abort/status/export) kept as a real requirement | "There should be both Automation and Control Simultaneously" |
| 3 | Authorization / Rules-of-Engagement verification is explicitly **out of scope** for the system | Operator decision — obtaining authorization is the operator's own responsibility outside the tool (see `AC-ASSUME-03` for the load-bearing assumption this creates) |
| 4 | Numeric/design parameters: ask each one individually rather than propose defaults | Explicit process instruction, applied for the rest of the session |
| 5 | RAM safety margin = 1.5 GB | Direct answer |
| 6 | Disk thresholds = 85% warn / 95% block | Direct answer |
| 7 | Model-swap time budget = 60s | Direct answer |
| 8 | Kill-switch full-stop budget = 20s | Direct answer |
| 9 | E-core allocation for tool subprocesses = 4 of 8 threads | Direct answer |
| 10 | Report pipeline: Markdown first → held in `pending-approval/` → operator approves → HTML + PDF via `pandoc`+`wkhtmltopdf`/`weasyprint` | Direct answer |
| 11 | Report formatting rules cloned from `claude-bug-bounty/CLAUDE.md`, identity replaced (Muhammad Huzaifa Jamil / protonmail), single-assessor footer, original file untouched, saved as `12-Report-Formatting-Rules.md` | Direct answers (two-question round) |
| 12 | Multi-target support: one engagement may scope multiple hosts/domains | Direct answer — drove the `engagements`/`targets` schema split in `03` |
| 13 | Phase 4.2 loop bound: 30-task-per-target cap + 3-zero-yield circuit breaker + 12-hour global budget, auto-pivot/auto-report, **no operator pause** | Direct, detailed answer |
| 14 | GitHub repo `MHuzaifaJamil/Agentic-VAPT-Personal-Lab`, private, `gh` CLI (self-installed by operator), local git identity `Muhammad Huzaifa Jamil <muhammad.huzaifa.jamil@gmail.com>` | Direct answers across a multi-step setup exchange |
| 15 | Pushback logged: combining no-RoE-gate (#3) with no-pause 12h autonomy (#13) creates `RISK-UNBOUNDEDAUTONOMY` | Raised proactively per "counter unrealistic responses" instruction; **not reversed** by operator — kept as documented residual risk |
| 16 | Prompt-injection defense (critical-analysis C-04) = **MUST** requirement | Direct answer |
| 17 | Hibernation OOM protection (C-01) = mandate `oom_score_adj` deprioritization | Direct answer |
| 18 | CVSS scoring (C-07) = deterministic calculator computes the score; LLM only proposes metrics | Direct answer |
| 19 | Operator control interface = **CLI only**, no GUI/dashboard | Direct answer |
| 20 | Tier 2 bridge safety (C-12): path-restricted allowlist (`/usr/bin`,`/usr/sbin`,`/opt`) + behavioral denylist, no per-binary approval by default | Direct answer (rejected the original multiple-choice framing; operator supplied their own more specific mechanism) |
| 21 | Inference engine (C-13): `llama.cpp --server` primary, explicit process-lifecycle model swap, abstracted behind a Local Engine Client so `ollama` can substitute later | Direct answer (operator supplied their own mechanism, not one of the offered options) |
| 22 | Evidence redaction reconciliation: draft redacted by default, reversibly unredacted only on operator's `approve-report` action | Direct answer, resolving a real contradiction between `FR-COUNCIL-18` and the cloned report rules' "never redact" clause |
| 23 | C-02 (memory-reclamation figures): add an explicit "illustrative, not guaranteed" framing note to `02`, on top of the already-existing `FR-ENV-08` live re-measurement | Direct answer |
| 24 | C-06 (`i915`/`xe` claim): documentation caveat only, no new pre-flight check | Direct answer |
| 25 | C-11 (hallucination overclaim): downgraded language + existing Gate 3 checklist judged sufficient, no new control | Direct answer |
| 26 | C-14 (Tier 2 residual risk): three curated high-risk categories, each gated by its own pre-engagement opt-in flag (`--allow-brute-force`, `--allow-active-exploitation`, `--allow-lateral-movement`), settable at `start` and updatable via `resume`; unpermitted tasks are refused and the loop auto-continues, no mid-run halt | Multi-round direct answers (category count, full binary lists, flag names, mid-engagement mutability, default-for-unlisted-tools) |
| 27 | CVSS version standardized on **3.1** | Direct answer |
| 28 | GPU-offload benchmark pass bar (`FR-PRE-08`): relative — GPU offload must beat CPU-only in the same benchmark, no fixed tok/s number | Direct answer |
| 29 | Thermal-throttle trigger (`OPS-MONITOR-03`): use the kernel's own reported throttle/PROCHOT signal, not a guessed °C threshold | Direct answer |
| 30 | Gate 2 correction attempts before `BLOCKED` (`FR-COUNCIL-09`) = 3 | Direct answer (changed from an earlier un-confirmed default of 2) |
| 31 | Hibernation confirmation (`FR-ENV-06`): no runtime interactive prompt — invoking `start` is itself the consent; resolves a contradiction with the fully-unattended design | Direct answer |
| 32 | `state.db` backup (`DR-BACKUP-01`): **MUST**, not best-effort — Phase 5 isn't complete without it | Direct answer |
| 33 | Generic "autonomy levels" (paranoid/normal/yolo) concept: **removed** | Direct answer — judged redundant once the three opt-in flags (#26) and fixed loop-bound thresholds (#13) existed; all references across `01`/`02`/`03`/`05` updated accordingly |
| 34 | Council Gate 1 model swap (C-03): replace `Hermes-3-Llama-3.1-8B` with `Llama-3.1-8B-Instruct` for the semantic layer, **plus** add a new non-LLM deterministic scope-checker as a mandatory first tier (`FR-COUNCIL-03a`); `Mistral-7B` stays dedicated to Gate 3 only | Direct answer — operator supplied the specific mechanism (not one of the offered options) |
| 35 | Exec-loop model-swap granularity (C-09): **zero swapping** inside the active loop — `Qwen2.5-Coder-7B` stays resident for the whole per-target loop; Gate 2 becomes a deterministic Python validator; `Qwen2.5-Coder-3B` demoted to an offline, between-phase role only | Direct answer — operator supplied the specific mechanism (not one of the offered options) |
| 36 | Tiered subprocess timeouts (C-08): Quick Probes 180s / Targeted Scans 900s / Deep-Full-Range 1800s, plus mandatory non-blocking output streaming to detect stalls before the hard timeout | Direct answer, with an explicit tool-to-tier mapping |
| 37 | `gobuster`/`feroxbuster`/`testssl` explicitly confirmed into the 900s Targeted Scans tier (this was an inference in `IR-TOOL-03`, now closed) | Direct answer |
| 38 | `NFR-PERF-04` (an un-confirmed `[PROPOSED]` item predating the 12-hour budget) removed as redundant with `NFR-PERF-05` | Direct answer |
| 39 | **Reversal of decision #1-era policy:** `Agentic VAPT Setup (HOME).md` — previously off-limits to editing — is now directly corrected in place (silent replacement style) for 9 items: the Gate 1/Gate 2 model-and-mechanism swap (C-03/C-09), CVSS scoring (C-07), Tier 2 bridge safety + opt-in flags (C-12/C-14), inference engine (C-13), tiered timeouts (C-08), the "zero data loss" claim (C-01), and the unbounded task-queue loop (`FR-COUNCIL-11`). C-02/C-04/C-05/C-06/C-10 were explicitly *not* applied to the source file. Each correction carries an inline note pointing back to `11`. | Direct instruction, explicitly reversing the earlier "do not change the original plan file" instruction |
| 40 | Four new critical-analysis findings added and resolved from an externally-sourced issue list, all analyzed and confirmed as genuine (not just transcribed): **C-15** (`process_madvise` needs privileges the least-privilege design doesn't have → narrow `setcap`/`sudoers`-scoped helper, `FR-ENV-13`, cgroup v2 fallback), **C-16** (long `SIGSTOP` lapses network/IPC sessions → hibernation SLA reframed to process-memory only, `FR-ENV-14`, with an added caveat that some apps may still force-reload on stale-session detection), **C-17** (undefined "zero-yield" let noisy tools defeat the circuit breaker → redefined as a state-delta against a new `discovered_entities` ledger, `FR-COUNCIL-11a`/`DR-SCHEMA-12`), **C-18** (model-swap teardown/respawn race → mandatory `MemAvailable` poll gate before the next model spawns, 5s bound, `FR-GATE-10`/`IR-ENGINE-06`). Also concretized two previously-generic mechanisms with the specific values proposed: the prompt-injection tag is `<tool_output_untrusted>...</tool_output_untrusted>` (was a generic placeholder), and the CVSS 3.1 calculator is specifically the Python `cvss` library. `oom_score_adj` was concretized to `-900`. All of this was also mirrored into the base plan file (decision #39's treatment, extended). The proposed GRUB/kernel-parameter driver-migration remediation (for the `i915`/`xe` mismatch, C-06) was evaluated and kept as a **documented manual recommendation only** — not an automated agent capability — since it is a system-wide, reboot-requiring bootloader change outside this design's risk class. | Operator supplied a detailed externally-sourced issue list and asked for critical analysis + fixes; two scope questions (GRUB automation, base-file mirroring) were asked before implementing |
| 41 | **Implementation architecture bridge (`13-Implementation-Architecture-Bridge.md`).** Before handing the doc set to a build-time coding agent, an honest gap assessment found `01`-`12` were requirements, not a buildable spec: no process/daemon model, no declared language, no file formats, no helper IPC contract, no module layout. Confirmed: (a) process model = per-invocation, SQLite/signal-coordinated, no daemon — `pause` cooperative via `SIGUSR1`+intent flag, `abort` a direct external kill (not cooperative), `resume` spawns a fresh process; (b) language = Python 3.x; (c) scope-rules file = YAML; (d) thresholds = a YAML config file with the confirmed values as defaults (config format extended to YAML by inference from (c), not re-asked); (e) freezer-helper invocation = one-shot subprocess call per operation, not a persistent helper+IPC protocol; (f) CLI framework = Click; (g) a concrete module layout was requested and proposed. Designing the process model surfaced three real schema gaps (no table for suspended-PID tracking, no PID column for `abort` to find a running subprocess, no redaction-mapping table for `FR-COUNCIL-18`) — closed in `03` as `DR-SCHEMA-13`/`14` and new columns. | Two rounds of direct questions (4 questions each) on the foundational forks; the three schema gaps were found and closed while writing, not re-asked (mechanical consequence of the chosen process model, not a new design fork) |
| 42 | **Three more build-level fixes from a second externally-sourced review, all analyzed and confirmed genuine:** C-19 (kill-switch targeted only the recorded PID, not the process group → subprocesses now spawn via `start_new_session=True`, `abort` uses `os.killpg`), C-20 (WAL mode alone doesn't stop "database is locked" between concurrent CLI invocations → `PRAGMA busy_timeout = 5000` on every connection), C-21 (redaction addressing via "offset or regex" could restore the wrong secret on a duplicate token → revised to exact `start_offset`/`end_offset` + `content_hash`, with a hard failure on hash mismatch). **Standing policy established** (applies going forward, not just this batch): `Agentic VAPT Setup (HOME).md` carries **high-level statements only** — no Python-specific flags, SQLite pragmas, or schema-column-level detail — while `01`-`13` carry full precision. Consistency between the two is maintained by paraphrasing each fix at the appropriate altitude for the base file, not by copying the precise mechanism verbatim. All three fixes were mirrored into the base file at that high level. | Operator supplied a second detailed review; explicitly asked for the altitude split as a standing rule rather than a one-off answer |

---

## Open Questions Remaining

These are the only items in the requirement set that are **not yet closed** by an
explicit operator decision — everything else in `01`-`09`/`11`/`12` traces to the log
above.

| # | Open Item | Why It's Still Open |
|---|---|---|
| A | Real-hardware feasibility checks (`TP-FEASIBILITY` in `09`): thermal/throttle telemetry availability, actual `i915`/`xe` driver binding, SYCL backend stability under sustained load | These can only be verified on the actual target machine at deployment time — nothing in a planning phase can close them |
| B | Cross-machine transfer (`RISK-CROSSMACHINE` in `07`) | This entire document set, plus `12-Report-Formatting-Rules.md` and the `claude-bug-bounty` toolkit it was cloned from, currently exist only on this planning session's machine, not on the target PC described in the base document |
| C | `RISK-UNCENSOREDGATE`-adjacent residual: Council Gate 1's semantic layer is now `Llama-3.1-8B-Instruct` instead of Hermes-3 (decision #34), which should reduce this risk, but no test has actually verified the new model's refusal behavior is in fact more conservative — it's a reasoned model swap, not yet an empirically confirmed one | Requires the actual model file and a live evaluation, out of reach of a planning-phase document |
| D | Whether the three high-risk category binary lists (decision #26) are exhaustive, or whether other Kali tools should be added to `--allow-brute-force`/`--allow-active-exploitation`/`--allow-lateral-movement` as they're discovered in practice | The lists as confirmed are believed complete for common cases but were not cross-checked against the full `kali-linux-everything` package manifest |

No other assumptions were made in place of a decision. If a future reader finds a
requirement in `01`-`09` that looks like an unstated assumption, it should be treated
as a documentation gap to raise, not as settled — cross-check against this log first.
