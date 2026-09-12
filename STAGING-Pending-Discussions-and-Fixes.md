> ⚠️ **DO NOT INGEST THIS FILE.** This is a staging/discussion log for the operator's own
> review. It is **not** a requirement specification, is **not** binding, and MUST NEVER be
> read, parsed, or treated as a source of truth by build agents, code-generation agents, or
> any automated development process. Nothing in this file is active until the operator
> explicitly approves an item below and it gets merged into the numbered requirement docs
> (`01`–`24`) by a separate, deliberate edit.
>
> This file exists so in-progress discussion of bugs/future features has somewhere to live
> without touching the binding corpus before the operator has signed off.

---

# Pending Discussions & Fixes — Awaiting Operator Approval

**Ordering convention:** newest items on top within each section below. New genuinely
undecided items go into **Currently Pending Approval**. Once the operator decides, an item
moves into **Still Open** if any of its sub-items/action-steps remain unfinished (most often
because they need the operator's own `sudo`, which this assistant does not have passwordless
access to) — **a Round stays in Still Open, at the top, for as long as ANY part of it is
unfinished, even after every other part has been approved and/or implemented.** Only once a
Round is fully, completely done does it move down into the dated Archive. This file's
purpose is to show how a fix evolved, not just its final state.

---

## Currently Pending Approval

*(Genuinely new, undecided items — awaiting the operator's own review/choice.)*

### Round 12 — Task-Dispatched Knowledge Ingestion: Bridging 818+ Security Skills Directly Into Council Tasks

**Status: 🟢 PROPOSAL & SPECIFICATION.** Supersedes the earlier, lighter Round 12 draft
(a simpler `skill_lookup` Tier 2 tool sketch) with a fully worked design the operator
provided directly. Same origin as before: `mukul975/Anthropic-Cybersecurity-Skills` (818
Claude-Code Skill files, installed via `npx skills add ...`, symlinked under
`~/.agents/skills/<skill-name>/SKILL.md` on this host) can't be "installed into" Mugheeraat
directly (Skills are a Claude-Code-specific mechanism; the council has no dynamic
skill-loading tool of its own) — but the underlying content is real, local, and reachable.
This version replaces the earlier "explicit tool call" framing with a fully automatic,
task-dispatch-driven design.

#### 1. Conceptual Architecture & Shift: Task-Driven vs. Tool-Driven

Instead of exposing an explicit tool that models must discover, call, and wait for,
**knowledge ingestion is entirely task-driven and orchestrated automatically**:

1. **Strategic Task Emission:** The Lead Strategist (`DeepSeek-R1-0528-Qwen3-8B`) generates
   an execution graph containing concrete tasks stored in `state.db`. Each task record
   includes a `task_id`, `hypothesis`, `technique`, and `target_asset`.
2. **Pre-Dispatch Ingestion:** When the orchestrator dispatches an active task to a Scripter
   (`Primary Scripter` or `Secondary Scripter`), it matches the task's hypothesis, technique,
   and target metadata against the local skills index.
3. **Automatic Context Augmentation:** If a relevant skill matches above the confidence
   threshold, the orchestrator extracts its operational playbook sections and injects them
   directly into the task context block before the model begins token generation.
4. **Zero Model Overhead:** The Scripter does not spend a tool-call turn or infer
   parameters; the domain expertise is already present in its task assignment prompt.

```
[ Phase 4.1: Lead Strategist Plan in state.db ]
                    │
                    ▼ (Task Dispatch Event: task_id, hypothesis, technique)
┌────────────────────────────────────────────────────────────────────────┐
│ Dynamic Skill Matcher (BM25 / Keyword Overlap on Local Repository)     │
│   ├── Scans ~/.agents/skills/ & /opt/mughiraat/skills/                 │
│   ├── Evaluates Task Hypothesis against YAML frontmatter & tags        │
│   └── Matches Top Skill (Score ≥ Threshold τ)                          │
└────────────────────────────────────────────────────────────────────────┘
                    │
                    ▼ (Structural Section Filter)
┌────────────────────────────────────────────────────────────────────────┐
│ Operational Playbook Extractor                                         │
│   ├── Discards: Theory, introduction, references, verbose history      │
│   └── Retains: Vectors, syntax, parameter mutations, payload examples   │
└────────────────────────────────────────────────────────────────────────┘
                    │
                    ▼
[ Injected into Scripter Context: <task_reference> ]
                    │
                    ▼
[ Phase 4.2A / 4.2B: Scripter Generates AST-Valid Attack Code ]
```

#### 2. Future-Proofing for 818+ Current and Incoming Skills

To ensure any new skill dropped into the system works immediately without code refactoring:

- **Dynamic Repository Traversal:** The indexer walks all configured skill directories
  (`~/.agents/skills/`, `/opt/mughiraat/skills/`, etc.) at startup or cache invalidation.
- **Standardized Frontmatter Parsing:** Parses the standardized YAML frontmatter present in
  modern security playbooks:
  ```yaml
  ---
  name: graphql-introspection-abuse
  description: Playbook for querying hidden GraphQL schemas and bypassing batch limits.
  tags: [graphql, api, introspection, batching, nosql]
  mitre: [T1190, T1059]
  ---
  ```
- **Hybrid Lexical Matcher (BM25 / Token Ingestion):** Matches the incoming task description
  against the indexed `name`, `description`, and `tags` using a pure Python BM25 or
  set-intersection algorithm. Sub-millisecond execution time, zero GPU/CPU LLM inference
  cost, exactly 0 MB memory footprint during idle states.
- **Fallback Behavior:** If no skill scores above the confidence threshold, the orchestrator
  injects nothing, and the Scripter executes using its base pre-trained knowledge without
  latency penalties.

#### 3. Hardware Constraints & Operational Context Limits

Under this host's 15.3 GiB physical RAM and single-model residency policy, the allocated
context length in `llama.cpp` (`-c`) must remain bounded to protect the memory budget:

| Model Role | Quantization | Native Capability | Bound Runtime Allocation (`-c`) | Allocated KV-Cache Footprint |
|---|---|---|---|---|
| Lead Strategist (`DeepSeek-R1-Qwen3-8B`) | `Q8_0` (~8.7 GB) | 128k tokens | **16,384 tokens** | ~1.5 GB |
| Strategy Auditor (`Hermes-3-Llama-3.1-8B`) | `Q8_0` (~8.5 GB) | 128k tokens | **8,192 tokens** | ~0.8 GB |
| Primary Scripter (`Qwen2.5-Coder-7B`) | `Q8_0` (~8.1 GB) | 128k tokens | **16,384 tokens** | ~1.3 GB |
| Secondary Scripter (`DeepSeek-Coder-6.7B`) | `Q8_0` (~7.2 GB) | 16k tokens | **16,384 tokens** | ~1.2 GB |
| Criterion Adjudicator (`Mistral-7B-v0.3`) | `Q8_0` (~7.7 GB) | 32k tokens | **16,384 tokens** | ~1.4 GB |
| Executive Reporter (`Ministral-8B-2410`) | `Q8_0` (~8.5 GB) | 128k tokens | **16,384 tokens** | ~1.5 GB |

*Context Budget Rule:* within a 16k context window, reserving 2,000–4,000 tokens for system
prompts and history leaves ample room, but streaming thousands of irrelevant tokens on CPU
compute degrades prompt processing speed (`O(N)` latency) — directly relevant given Round
10.2's now-measured real prefill/generation speeds on this exact hardware.

#### 4. Structural Extraction Over Blind Truncation or Complex Chunking

Passing multi-thousand-word Markdown documents in sequential chunks is counterproductive for
single-pass code synthesis, while blind character truncation (`[:1000]`) risks chopping off
mid-command or mid-payload. Instead, the extractor performs **Deterministic Structural
Parsing**:

1. Ingests the raw `SKILL.md`.
2. Strips out academic preamble, background history, author metadata, and generic
   remediation sections.
3. Extracts only actionable headings: `## Attack Vectors` / `## Verification Procedure` /
   `## Payloads` / `## CLI Examples` / `## Headers`.
4. The extracted section is capped structurally at ~500–800 tokens — dense, high-signal
   technical instructions without wasting context space or slowing down CPU inference.

#### 5. Context Enclosure & Prompt Assembly

Since all skill files reside locally on this secured, operator-controlled host, they are
fully trusted operational assets — the `<tool_output_untrusted>` quarantine wrapper this
project uses for live target data is deliberately omitted. Instead, a clean, semantic
structural container (`<task_reference>`) separates guidance from output constraints:

```xml
<active_task id="TSK-042" target="https://api.internal.lab/v1/graphql">
  <hypothesis>Bypass access control via GraphQL introspection and nested batch mutations</hypothesis>
  <assigned_operator>SECONDARY_SCRIPTER</assigned_operator>

  <task_reference source_skill="graphql-introspection-and-query-abuse">
    Key Tactical Vectors:
    - Probe schema availability: POST /graphql with {"query": "{__schema{types{name}}}"}
    - Test mutation batching bypass: Array-wrapped payloads [{"query":"..."}, {"query":"..."}]
    - Check alias overloading to force resource exhaustion / state changes:
        query { a: node(id:1){id} b: node(id:1){id} }
  </task_reference>

  <negative_constraints>
    Operator Alpha already ran basic ffuf directory enumeration on /graphql.
    Do NOT rerun basic dictionary scans. Generate custom Python scripts to test batching or introspection.
  </negative_constraints>
</active_task>
```

#### 6. Role Scope Mapping

- **Primary Scripter (`Qwen2.5-Coder-7B`) & Secondary Scripter (`DeepSeek-Coder-6.7B`):**
  **Primary Consumers.** Receives the specific tactical playbook whenever an active task
  involves an identified protocol, framework, or vulnerability class.
- **Lead Strategist (`DeepSeek-R1-0528-Qwen3-8B`):** **Strategic Baseline Only.** Receives
  top-level summary tags during Phase 4.1 attack-graph generation to assist in branching
  hypotheses.
- **Strategy Auditor, Criterion Adjudicator, Executive Reporter:** **Excluded.** The Auditor
  checks scope rules; the Adjudicator evaluates raw HTTP/OS evidence against deterministic
  criteria; the Reporter structures verified findings into NIST/CWE reporting standards —
  none of the three need tactical attack playbooks for their own jobs.

#### 7. Implementation Plan

1. **`vapt_agent/knowledge/skills_index.py`** — `SkillIndex` class using `pathlib` to
   discover all `SKILL.md` files; parse YAML frontmatter (`yaml.safe_load`); implement
   `match_skill(query_text: str) -> Optional[SkillMatch]`.
2. **`vapt_agent/knowledge/skill_extractor.py`** — markdown AST or heading-based parser to
   pull execution/payload sections per §4 above.
3. **`vapt_agent/orchestrator/phase_lifecycle.py`** — in the dispatch pipeline for Phase
   4.2A and Phase 4.2B, call `SkillIndex.match_skill()` using the current task's hypothesis
   and technique; inject the formatted `<task_reference>` block directly into the prompt
   context.

**Still genuinely open, not settled by this spec**: the exact BM25/keyword-overlap
confidence threshold `τ`; whether `/opt/mughiraat/skills/` (a second, project-owned skills
directory alongside `~/.agents/skills/`) actually needs to exist yet or is aspirational;
test coverage plan for the matcher/extractor before any of this touches a real role prompt.
Not yet built — awaiting operator approval before any code is written.

---

## Still Open — Approved, Action Items Remain

*(Decided by the operator, but not fully finished — usually because a step needs the
operator's own `sudo`, which this assistant has no passwordless access to. Stays here, at
the top of this section, until every sub-item is done — even once some parts are already
implemented and verified.)*

### Round 10 — Two Real Findings From the 2026-09-12 Live Benchmark: `systemd-oomd` Kills, and the Strategist's CPU-Only Latency Ceiling

**Status: ✅ APPROVED (2026-09-12) — PARTIALLY IMPLEMENTED, `sudo` STEPS STILL OPEN.**

| Item | Decision | Status |
|---|---|---|
| 10.1 — `systemd-oomd` drop-in | Option A (90%/60s session override) | ✅ **Done (2026-09-13)** — operator ran it; confirmed live via `systemctl show user@1000.service -p ManagedOOMMemoryPressureLimit -p ManagedOOMMemoryPressureDurationUSec` returning `3865470566` (systemd's fraction-of-`UINT32_MAX` encoding of 90%: `4294967295 × 0.9 ≈ 3865470566`) and `1min` |
| 10.2 Option A — raise `STRATEGIST_TIMEOUT_S` | Approved as the concrete next step once Option C's real number was in | ✅ **Done** — `vapt_agent/council/strategist.py:48`, `1800.0 → 9000.0`, full suite re-verified clean (1079/0/3) |
| 10.2 Option B — Intel Level Zero/OpenCL driver | Approved as the real long-term fix | 🔲 **Not yet applied — needs the operator's own `sudo`** (commands below) |
| 10.2 Option C — uncapped latency probe | Approved, run to completion | ✅ **Done** — real result: 117.4 min, see below |
| 10.2 Option D — downgrade to 3B model | Explicitly rejected | ❌ Rejected, not revisited |

10.1: **Option A** (session drop-in,
`ManagedOOMMemoryPressureLimit=90%`/`ManagedOOMMemoryPressureDurationSec=60s`) —
Option B rejected (strips protection entirely, a real risk if an unrelated app leaks
memory), Option C rejected (its `systemd-run --scope -p` mechanism already confirmed
failing live on this systemd 261, not worth the extra engineering for a personal
dev/test host). 10.2: **Option C first** (raw uncapped latency probe, in progress),
**then Option B** (install the missing Intel Level Zero/OpenCL compute runtime so real
GPU offload becomes possible) as the permanent fix — Option D (downgrade to a 3B model)
explicitly rejected, since a smaller model would compromise the Strategist's actual
planning/reasoning quality, not just its speed; Option A (blindly raise the timeout
further) also rejected as premature until Option C's real number is known. Both 10.1's
drop-in and 10.2's driver install need root (`sudo`), which this session has no
passwordless access to for general commands — commands below are ready to run by the
operator directly; implementation-side work (the Option C probe) proceeds in parallel.

```bash
# 10.1 — systemd-oomd session drop-in (Option A)
sudo mkdir -p /etc/systemd/system/user@1000.service.d/
sudo tee /etc/systemd/system/user@1000.service.d/20-vapt-oomd-override.conf << 'EOF'
[Unit]
Description=Permit High Memory Pressure for Local VAPT LLM Execution

[Service]
ManagedOOMMemoryPressureLimit=90%
ManagedOOMMemoryPressureDurationSec=60s
EOF
sudo systemctl daemon-reload

# 10.2 Option B — Intel Level Zero / OpenCL compute runtime (verify AFTER Option C's probe)
sudo apt update
sudo apt install -y intel-opencl-icd intel-level-zero-gpu level-zero libze1 libze-dev
clinfo | grep "Device Name"
```

---

**Status (superseded by the approval above): 🟡 AWAITING REVIEW.** Both items came out of 4 real, live full-engagement runs
against JuiceShop/MediaCMS this pass (see
`local-llm-agentic-vapt/implementation`'s session memory,
`vapt_venv_rebuild_and_benchmark_2026_09_12`, for the full run-by-run detail). Neither is a
code-correctness bug — both are real operational/hardware constraints this host's config
runs into, laid out here with concrete options rather than a unilateral pick, per this file's
usual purpose for exactly this kind of decision.

#### 10.1 — `systemd-oomd` kills the whole engagement's cgroup under memory pressure, ignoring the project's own `oom_score_adj` protection

**The problem, confirmed live and root-caused precisely.** Engagement 17 was SIGKILLed in
its entirety (orchestrator, `llama-server`, every tool subprocess — 29 processes at once)
~9 minutes into Strategist model loading, even though `MemAvailableGate` (`FR-GATE-10`) had
already cleared the load, and even though `security/kill_switch.py`'s `oom_score_adj=-900`
protection was correctly applied to the orchestrator process. Root cause:
**`systemd-oomd`**, a separate userspace daemon from the kernel's own OOM killer (which never
fired — nothing in `dmesg`), watches per-cgroup **PSI (pressure stall information)**, not
per-process `oom_score_adj`, and Kali ships a default drop-in
(`/usr/lib/systemd/system/user@.service.d/10-oomd-user-service-defaults.conf`) that arms
`ManagedOOMMemoryPressure=kill` with `ManagedOOMMemoryPressureLimit=50%` on every user
session's `user@1000.service` slice — meaning ANY cgroup under the desktop session
(including the tmux-spawned scope `vaptctl start` launches the orchestrator into) gets
killed outright if memory pressure sits above 50% for a sustained ~20s window, independent
of whether the process holding that memory is well-behaved, self-throttling, or already has
its own kernel-level OOM protection. On a 15GB host running an 8.7GB Q8_0 model, crossing
that 50% pressure threshold during model load/reload is close to inevitable, not a fluke —
this WILL recur on any future live run unless addressed.

**What I verified live this session, so the options below are fact-checked, not
speculative:**
- Confirmed via `journalctl -u systemd-oomd` (the kernel's own OOM killer log, `dmesg`,
  showed nothing — a real trap for anyone debugging this by kernel log alone).
- Confirmed the exact drop-in file and its two relevant settings (above).
- Tried the two "fix it live, narrowly, per-invocation" mechanisms first (lowest blast
  radius): `systemctl --user set-property <tmux-scope> ManagedOOMMemoryPressure=no` and
  `systemd-run --user --scope -p ManagedOOMMemoryPressure=no -- ...`. **Both failed** with
  `Failed to set unit properties: Invalid argument` on this host's systemd 261 — this
  property does not appear to be settable imperatively per-scope via either mechanism here
  (possibly requires a declarative unit **file**, not a runtime/creation-time property
  injection; not fully root-caused since further live experimentation risked destabilizing
  the operator's real desktop session mid-investigation).
- Did **not** attempt the remaining candidate fix (a real `/etc/systemd/system/` drop-in
  file) live: it requires root, this session has no passwordless `sudo` for general commands
  (confirmed: `sudo -n` demands a password for anything outside the one narrowly-scoped
  `vapt-freezer-helper` NOPASSWD rule), and a system-wide daemon config change is exactly the
  kind of action this file exists to route through the operator first rather than applying
  unilaterally.

**Options:**

| # | Option | Feasibility | Blast radius / impact | Pros | Cons |
|---|---|---|---|---|---|
| A | **Drop-in override raising the limit/duration for `user@1000.service`** — e.g. `/etc/systemd/system/user@1000.service.d/20-vapt-oomd-override.conf` setting `ManagedOOMMemoryPressureLimit=90%` and/or `ManagedOOMMemoryPressureDurationSec=60s` | High — standard, well-documented systemd mechanism (`systemd.resource-control(5)`), just needs root once to create the file + `systemctl daemon-reload` (no reboot) | **Whole desktop session** — every app under this user session gets more pressure headroom before `systemd-oomd` intervenes, not just VAPT | Simple, one file, easy to revert (`rm` + reload), no code changes to the project at all | Weakens `systemd-oomd`'s protection for everything else running in the session too (browser tabs, etc.) — the exact class of problem `systemd-oomd` exists to catch; a runaway *unrelated* app would now get more rope before being killed |
| B | **Disable `ManagedOOMMemoryPressure` entirely for `user@1000.service`** (`ManagedOOMMemoryPressure=no` in the same drop-in) | High — same mechanism as A, just a different value | Whole desktop session, same as A but total removal rather than a raised threshold | Fully eliminates this specific failure mode, permanently, with certainty | Same session-wide tradeoff as A, but total rather than partial — no pressure-based protection left for the whole desktop session at all (kernel OOM killer still exists as a last resort, just much blunter and later-triggering) |
| C | **Narrow, code-level fix**: change `cli/run.py::launch_in_tmux` to launch the orchestrator via `systemd-run --user --unit=vapt-orchestrator-<engagement_id> --scope ...` instead of a bare `tmux new-session`, giving it a **stable, predictable** unit name, then ship a matching **project-owned** drop-in (`~/.config/systemd/user/vapt-orchestrator-@.scope.d/oomd.conf` or similar templated path) that exempts ONLY VAPT's own orchestrator scope, leaving the rest of the desktop session's `systemd-oomd` protection fully intact | Medium — real code change (`launch_in_tmux` + its tests + `engagement_tmux_session_names` interplay all need updating), and the earlier live "Invalid argument" failures mean the declarative-file half of this needs to be verified working BEFORE relying on it, not assumed | Narrowest possible — only VAPT's own engagement processes are exempted; everything else in the desktop session keeps full `systemd-oomd` protection | Correctly scoped, permanent, doesn't weaken protection for anything unrelated to VAPT | More engineering than A/B; not yet verified end-to-end (the declarative-drop-in half of the mechanism is untested); still needs one root-owned file created once, same as A/B |
| D | **Keep the current workaround** (reduce memory footprint before each run — stop non-essential MediaCMS workers, close idle apps, JuiceShop-only when tight) and accept `systemd-oomd` as an occasional real constraint rather than something to engineer around | High — zero new config, this is what's already been done live, twice, successfully | None — no system changes at all | Zero risk, zero new surface area, already proven to work | Not "permanent" in the sense the operator asked for — requires the operator (or me) to actively manage memory headroom before every future run; doesn't fix the underlying fragility, just avoids triggering it |

My recommendation if asked to pick one: **A**, as the pragmatic middle ground — real,
permanent, one file, easily reversible, and 90%/60s still leaves *some* protection rather
than none (unlike B), while being far simpler and more certain to actually work than C given
C's core mechanism is still unverified on this host. B is reasonable if the operator would
rather have zero risk of this recurring and is comfortable losing pressure-based protection
session-wide. C is the "correct" long-term answer if this project ever runs on a host where
protecting *other* unrelated apps from `systemd-oomd` actually matters, but shouldn't be
built until A/B's simpler file-based mechanism is confirmed to actually work as designed
(neither A nor B has been applied/tested live yet either — both need root, not available to
me this session).

#### 10.2 — Strategist role's CPU-only inference exceeds the current 2×30min timeout budget, confirmed reproducible

**UPDATE 2026-09-12, Option C run to completion — the real number.** A standalone probe
(`engine/client.py` called directly, bypassing `STRATEGIST_TIMEOUT_S`, real baseline-recon
context reused verbatim from engagement 18's completed run — 33,318 chars / 12,449 prompt
tokens) **completed successfully**: `elapsed_s: 7043.4` (**117.4 min, ~1h57m**),
`completion_tokens: 5207`, producing a genuinely good, coherent attack-plan (IDOR on
product-detail IDs, SSRF via an image-fetch feature pivoting to the internal CUPS service on
`:631`, unauthenticated `/admin`, CUPS path traversal) — real validation that the council
architecture works, not just a latency number. **~1h57m is the true CPU-only ceiling for
this role on this hardware and this prompt size**, roughly 4x the current 1800s
(`STRATEGIST_TIMEOUT_S`) per-attempt budget — explains why both real attempts (60.5min/
60.3min combined, i.e. 2×1800s) never finished: the model was still working, just needed
about twice that.

**A second, unplanned finding from the same run, worth its own line:** `journalctl` shows
the host **suspended itself mid-probe** (`xfce4-power-man`-triggered `s2idle` suspend,
16:49:48 → 18:45:40, 1h56m) while the model was actively computing. The probe survived this
completely unharmed — Linux's monotonic clock (which both my Python timer and, very likely,
the underlying socket-timeout mechanism use) simply stops advancing during `s2idle` suspend,
so neither the client's timeout nor my own elapsed-time measurement counted the sleep at
all; the process resumed exactly where it left off on wake and finished normally. **This is
good news for this specific probe's result being clean, but it surfaces a real, previously
undocumented gap**: nothing in this project currently inhibits system suspend during an
active engagement. This particular run got lucky (whatever timeout was in effect at each
moment happened to still have headroom left when suspend hit); a real orchestrator run using
the 1800s `STRATEGIST_TIMEOUT_S` could suspend and resume with a very different, less
forgiving outcome depending on exact timing, and the Blueprint document's own claim that the
system "runs unattended for hours if needed" implicitly assumes the OS won't nap through
part of that unattended stretch. Flagging as a candidate for its own follow-up item
(inhibit suspend for the duration of an active engagement, e.g. via `systemd-inhibit
--what=sleep` wrapping the orchestrator process) rather than folding it into 10.2's own
timeout-tuning decision, since it's a different mechanism entirely — not staged as a full
proposal yet, just recorded here so it isn't lost.

**Original two data points (engagements 18/19, both hit the OLD 2×30min budget before this
Option C run measured the true number):** Two independent full engagements (18, 19), each running the identical
Strategist Phase 4.1 turn 1 call against `DeepSeek-R1-0528-Qwen3-8B-Q8_0.gguf` (no GPU
offload available — `libze_intel_gpu.so` absent from this host, confirmed every preflight
run), both timed out on BOTH the initial attempt and `FR-GATE-08`'s one automatic
restart+retry, landing within 12 seconds of each other: **3631.8s (60.5 min)** and
**3619.9s (60.3 min)** combined, neither producing a response. Both times the engagement
degraded gracefully to `PAUSED` exactly as `FR-GATE-08` designs it to — zero data loss, zero
orphaned processes, full RAM recovery both times. This is NOT new: the 2026-09-09 session
memory (`vapt_2026_09_09_mem_gate_and_app_teardown`) already flagged "Strategist inference
exceeding the 900s client timeout (~30min+ actual)" as the real blocker back then too —
`STRATEGIST_TIMEOUT_S` was already raised once (to 1800s, from whatever it was at 900s) in
response, and the model still exceeds twice that. **The true completion latency ceiling on
this hardware remains unmeasured beyond "more than 60 minutes."** Every one of the 1076
passing tests that exercise Strategist logic does so against a fake/mocked engine
(`_FakeBenchEngine` and similar) — the test suite has never validated real end-to-end
Strategist latency, only the interface contract; this benchmark pass is the first time real
GGUF inference has been exercised live to a terminal outcome at all.

**Options:**

| # | Option | Feasibility | Impact | Pros | Cons |
|---|---|---|---|---|---|
| A | **Raise `STRATEGIST_TIMEOUT_S` further** (`vapt_agent/council/strategist.py:48`, currently `1800.0`) | Trivial — one constant | Delays the PAUSE escalation further; does not change how long inference actually takes | Zero engineering risk, five-minute change | The true ceiling is unmeasured — could need hours, not minutes; raising blindly risks a multi-hour hang before the safety-net (graceful pause) even fires, with no new information gained about whether it will EVER finish |
| B | **Get real GPU offload working** (install the Intel Arc/Meteor Lake iGPU compute driver so `libze_intel_gpu.so` exists) | Medium — a real Kali/Intel oneAPI driver install, outside this project's own codebase entirely (an OS/driver-layer change, similar class of decision to 10.1) | Could plausibly cut inference time substantially (iGPU offload for a Q8_0 7-8B model is often several times faster than CPU-only on this class of hardware) — the ONLY option here that could make full engagements complete in reasonable wall-clock time rather than just tolerating slowness | Addresses the root cause (speed) rather than working around it; `run_gpu_offload_benchmark` (`FR-PRE-08`) already exists specifically to quantify this once available — no new code needed, just the driver | Real install effort/risk on the host outside this project's control; not guaranteed to be dramatically faster on an iGPU class this small; preflight would need to be re-verified after |
| C | **Run one uncapped raw latency probe** (bypass the orchestrator's timeout entirely, call the Strategist model directly via `engine/client.py` with a very large or no timeout, just to learn the TRUE number) | High — straightforward script, no code changes | One-time cost: as much as another 60-90+ minutes of wall-clock/CPU for a single data point | Answers "how long does it actually take" definitively, which every other option here is currently guessing at; informs whether A (raising the timeout) is even viable at all | Pure information-gathering, no functional improvement by itself; expensive in wall-clock time for one number; was already flagged as an option in the prior session and deliberately not run unilaterally given the cost |
| D | **Swap the Strategist role to a smaller/faster model** (`vapt_agent/config/defaults.yaml`'s `models.strategist`, e.g. to one of the already-downloaded smaller GGUFs like `qwen2.5-coder-3b-instruct-q8_0.gguf`) | High — one config line, but changes WHAT is being benchmarked/used for real engagements, not just how fast | Directly reduces compute cost proportional to model size; likely the single fastest practical win available today (no driver install, no hardware dependency) | Immediate, low-risk, no OS-level change needed, testable in one more live cycle | A smaller model may reason noticeably worse for the Strategist's planning role specifically — this is a real capability/quality tradeoff the operator should decide, not something to silently downgrade |

My recommendation if asked to pick one: **C first** (cheap relative to the others in
engineering risk, and every other option is currently a guess without it), **then D** as the
most practical standing fix if C's number turns out to be large, with **B** as the "do this
eventually regardless" long-term answer and **A** only as a follow-on tuning step once C's
real number is known (raising a timeout blindly, without knowing the ceiling, risks a
multi-hour silent hang for no better outcome than what already happens today).

**Now that C's real number is in (~117 min), the concrete next step is A**: raise
`STRATEGIST_TIMEOUT_S` (`vapt_agent/council/strategist.py:48`) from `1800.0` to something
with real margin over the measured ceiling — e.g. `9000.0` (150 min) leaves ~28% headroom
over the observed 117.4 min for prompt-size/run-to-run variance the 2026-09-02 docstring
finding already documented (763.8s vs. 900s+ on two real attempts at a SHORTER prompt back
then). With `FR-GATE-08`'s existing one-shot restart+retry, a single attempt at 9000s should
now be enough to finish without ever needing the retry — worth a live confirmation run once
approved. **B (GPU driver) remains the real long-term fix** — a ~118min single-turn latency
makes a full multi-target, multi-role engagement a many-hours-to-overnight affair even once
A is applied; B is what would actually bring that down. D stays rejected (capability
tradeoff, not revisited by this update).

---

## Archive — Resolved / Merged Items (newest first)

### Round 11 — Prevent System Suspend During an Active Engagement

**Status: ✅ APPROVED AND IMPLEMENTED (2026-09-12).** Operator approved Option A with an
explicit code pattern. Implemented in `vapt_agent/cli/run.py` as `hold_system_inhibition()`,
wrapping the `run_full_engagement(...)` call inside `run()`'s `try:` block — covers both the
tmux-relaunched auto-start path and a direct/manual invocation (e.g. after `vaptctl resume`)
uniformly, since both converge on that one call site. Holds a real
`systemd-inhibit --what=sleep:idle --mode=block` lock via a `sleep infinity` child process
for exactly the duration of that call; releases it (SIGTERM, falling back to SIGKILL after a
3s grace period) in a `finally:` block on any exit path — normal completion, PAUSE
escalation, or exception. Deliberately NOT spawned with its own process group
(`start_new_session` left at its default `False`) so it dies automatically alongside the
orchestrator under `vaptctl abort`'s `os.killpg` and under a Round 10.1-style
`systemd-oomd` cgroup-wide kill, without any separate cleanup path. Degrades to holding no
lock (never fails the engagement) if `systemd-inhibit` isn't on `PATH`.

**Verified, not just implemented**: 3 new real tests in `tests/test_cli_run.py` —
`test_hold_system_inhibition_registers_and_releases_a_real_lock` (genuinely calls
`systemd-inhibit --list` and confirms the entry appears during the `with` block and is gone
after), `test_hold_system_inhibition_terminates_lock_process_on_exception` (same, but
raising inside the block), `test_hold_system_inhibition_degrades_gracefully_when_binary_absent`.
Full suite: **1079 passed, 0 failed, 3 skipped**; `ruff` clean; `mypy` clean on the touched
files. Fully done — no `sudo` was needed for this Round at all.

---

### Round 9 — Three Items Closed Out of a "Close the Remaining Open Items" Pass, One Real Design Gap Found, Two Deliberately NOT Attempted

**Status: ✅ APPROVED (2026-09-12).** 9.1 (17 tools installed/wired) and the `knockpy`
correction were already-completed implementation work, now formally on record. 9.2's
`tool_api_keys`/`get_env_for_tool` design and 9.4's `task_queue.origin_purpose = 'LOGIN_FLOW'`
tag are approved as designs — **not yet implemented**, queued as real follow-on work (each
is a genuine build, not a one-line change). 9.3's phased `OPS-NOTIFY` build-out is approved
as a plan; also **not yet implemented** — same reasoning, a multi-session body of work, not
started this pass. Original context: the operator asked to close every remaining item
from an earlier audit (`FR-TOOL-17`'s real session mechanism, the rest of `FR-BASELINE-06`'s
tool roster, `mobsf`) and to detail any real issues here instead of forcing them. Three of
four sub-items below were genuinely closed (tool installs); one surfaced a real, scoped
design gap worth a decision; two (`OPS-NOTIFY`, `FR-TOOL-17`'s autonomous login-flow half)
were deliberately NOT attempted, with the reasoning laid out for review rather than silently
skipped or rushed.

#### 9.1 — CLOSED: 17 more `FR-BASELINE-06` tools installed, verified, and wired for real

Every remaining named-but-not-installed tool from the earlier audit
(`knockpy`/`sublert`/`puredns`/`shuffledns`/`bbot`/`whatwaf`/`unwaf`/`log4j-scan`/
`graphw00f`/`clairvoyance`/`graphql-cop`/`jwt_tool`/`x8`/`byp4xx`/`noseyparker`/`shhgit`/
`git-hound`) was actually installed this pass — real apt/pipx/`go install`/prebuilt-release-
binary/manual-clone-into-venv installs, each verified against a real `--help` (several also
cross-checked against GitHub/PyPI author and repo metadata *before* installing — `graphw00f`/
`graphql-cop`/`x8`'s identically-named PyPI packages turned out to be confirmed decoys/
unrelated libraries, correctly never installed). All are now real Tier 1 schemas, wired into
`orchestrator/baseline_recon.py`'s waves (including new GraphQL/JWT-endpoint detection
heuristics gating Wave 4's conditional branches, and a two-wave `noseyparker scan`→`report`
split so `report` never races `scan`), and test-covered. Full detail in
`IMPLEMENTATION-DEVIATIONS-FROM-REQUIREMENTS.md`'s matching entry. `git-hound` is the one
exception — registered but not baseline-dispatched, see 9.2 below.

A real, useful side effect: closing the "no resolvers file" gap `massdns.yaml` had flagged
since the 2026-09-09 pull — `puredns`/`shuffledns` needed one too, so
`vapt_agent/data/resolvers.txt` (a small curated list of well-known public DNS resolvers:
Cloudflare, Google, Quad9, OpenDNS, Verisign) is now bundled with the project. `massdns`
itself is still not baseline-dispatched (no self-contained "generate candidates from a
wordlist" mode the way puredns/shuffledns's `bruteforce` subcommand has), but a Scripter-
selected one-off `massdns` task can now use this resolvers file too.

A real, pre-existing latent bug this surfaced and fixed along the way:
`bridge/tier1/tools/graphql_scanner.py`'s `phase_engine_fingerprint` assumed `graphw00f`,
if ever installed, would be a pip-importable Python package (`python3 -m graphw00f.main`) —
an assumption written when `graphw00f` was never actually present to test against. It also
treated ANY non-empty combined stdout+stderr as a valid fingerprint finding, including
`graphw00f`'s own connection-error output. Now installed for real, `shutil.which("graphw00f")`
started finding it and this path activated for the first time, immediately surfacing both
bugs (caught by the full test suite, not missed). Fixed: invokes the real resolved binary
directly with its actual CLI flags, and only records a finding when the subprocess exits 0.

#### 9.2 — REAL DESIGN GAP: no credential-type concept for a third-party tool's own API key

`git-hound` (GitHub secret-search) and, less critically, `shhgit`'s remote-GitHub modes (not
used — `shhgit` only runs in local-directory mode, which needs no token at all) both need a
**GitHub personal access token** to be useful beyond GitHub's severely-rate-limited
unauthenticated public search tier. `security/credential_manager.py`'s `target_credentials`
table (`FR-TOOL-15`) is explicitly scoped to *per-target* credentials (a login for a specific
engagement target) — there's no existing concept of a credential that belongs to a *tool
itself* (an API key the Scripter's `git-hound` invocation would need regardless of which
target it's running against). Not invented unilaterally here, for the same reason
`FR-TOOL-15`/`17`'s original credential architecture waited for an explicit operator
decision rather than guessing at a schema.

**Recommend**: a small, separate `tool_api_keys` table (or a `scope='TOOL'` variant of
`target_credentials`, reusing the same AES-256-GCM-at-rest architecture and ephemeral
engagement key) — `credential_type` stays a per-tool key/token, `identity_label` becomes the
tool name (`git-hound`), and `get_env_for_tool(conn, *, tool_name)` (mirroring
`get_env_for_target`) injects e.g. `GITHOUND_GITHUB_TOKEN` only for that tool's own
dispatches. A `vaptctl register-tool-credential` CLI command would mirror
`register-credential`'s existing pattern. Genuinely small, but a real operator decision
(whether to build this now vs. leave `git-hound` Scripter-reachable only with a manually
operator-set env var in the meantime) — not decided here.

#### 9.3 — NOT ATTEMPTED: `06:OPS-NOTIFY-01..05` (severity-tagged events / dashboard-console banners / Error Code Dictionary / `vaptctl status` reason surfacing)

Checked the actual scope before starting rather than after: **none** of `OPS-NOTIFY-01..05`
exist in the codebase yet — no severity-tagged event log, no Error Code Dictionary, no
`engagements.status_reason`-shaped column (`engagements.status`'s own `CHECK` constraint
doesn't even include a `'BLOCKED'` value the requirement's own text names — `PAUSED`,
`PAUSED_AWAITING_CHECKPOINT`, `COMPLETE`, `ABORTED` are the only terminal-ish states that
exist today), no dashboard/console banner rendering for it. This is real, substantial,
genuinely cross-cutting infrastructure — every existing "log degraded and continue" call site
across this session's own work alone (baseline_recon's tool-missing skips, tech_intel's
feed-unreachable degradation, monitor_engine's crt.sh-unreachable fallback, and many more
from earlier sessions) is a candidate `OPS-NOTIFY` emission point, and `OPS-NOTIFY-01`/`05`
specifically require dashboard (`rich`/`plotext`) and console (`Textual`) rendering changes
this environment has no way to visually verify beyond structural/text-content assertions.

Deliberately NOT rushed into a partial, unverified build — the same discipline this whole
effort has held to (`s3scanner`'s fabricated-schema mistake earlier this project, caught and
fixed, is the cautionary example). **Recommend a phased build, not one big pass**: (1) a real
`ops_events` table + `vapt_agent/ops/notify.py` (severity constants, a real Error Code
Dictionary as a plain Python dict, `log_event()`/`get_unacknowledged_blocking_events()`) —
fully unit-testable, no UI risk; (2) wire `vaptctl status` to surface unacknowledged
BLOCKING/FATAL events and a new `engagements.status_reason` column (closes `OPS-NOTIFY-02`
concretely); (3) dashboard/console banner rendering, tested via captured plain-text output,
not visual inspection; (4) retrofit existing degraded-mode call sites to actually call
`log_event()` — the long tail, done incrementally rather than in one pass. Flagging for the
operator to confirm this phasing (or a different one) before it's started, since it's a
genuinely large, multi-session body of work, not a quick fix.

#### 9.4 — NOT ATTEMPTED: `FR-TOOL-17`'s "autonomous login-flow task succeeds" half

The credential/session-reuse *mechanism* (`security/session_manager.py`:
`establish_session`/`invalidate_session`, enforced at `get_env_for_target`) is real and done
(2026-09-10). What's still open is the OTHER trigger `FR-TOOL-17`'s own text names: "...or an
autonomous login-flow task succeeds." Concretely, this needs: (a) a way for the Strategist/
Scripter to recognize a proposed task AS a login-flow attempt (no such tagging exists on
`task_queue` today), and (b) a way to capture that task's *result* (a `Set-Cookie` header or
bearer token from a successful login POST) and feed it into `establish_session` automatically
— rather than the current, entirely-manual `vaptctl register-credential` +
`vaptctl establish-session` operator flow.

**Not attempted** because the obvious shortcut — pattern-matching ANY successful task's
output for `Set-Cookie`/`Authorization` header shapes and auto-registering it as a session —
is a real security judgment call this project's own architecture wouldn't want made
unilaterally: it would mean auto-trusting arbitrary tool output as a credential without any
operator review, a meaningfully different trust posture than everything else in this
codebase's credential handling (which always requires an explicit `register_credential`/
`establish_session` call). **Recommend**: a `task_queue.origin_purpose = 'LOGIN_FLOW'` tag
(or similar) the Strategist sets explicitly when proposing a login-flow task, so only tasks
*deliberately* run for this purpose get their output considered for auto-registration — a
real, scoped feature, but a design decision, not a default any build pass should invent on
its own.

#### Informational, not a decision needed: `knockpy` is no longer blocked

The earlier audit's "install everything installable" pass flagged `knockpy` as blocked by a
missing `sudo` password (its only known install path was assumed to be the apt package,
which needs root). Turned out wrong on closer check: `knockpy`'s real upstream
(`guelfoweb/knockpy`) publishes to PyPI under the package name `knock-subdomains` (not
`knockpy` — that PyPI name is a squatted, unrelated statistics library, confirmed via its own
PyPI summary before installing anything). `pipx install knock-subdomains` installed the real
tool with no sudo needed at all. Noted here only because the earlier report specifically
called this out as blocked — it no longer is.

---

### Round 8 — Dynamic Domain-Based Tool Discovery (WiFi/Bluetooth, and the Wider Kali Catalog)

**Status: ✅ MERGED (decision #77).** `FR-DISCOVER-01..03` added to `01`, referencing
`KALI-TOOL-CATALOG.md`. The flagged wireless-checkpoint question was resolved by
proceeding with the recommended approach: `FR-DISCOVER-04` classifies actively
disruptive wireless/Bluetooth actions under a new `ACTIVE_WIRELESS_DISRUPTION`
checkpoint class, gated identically to `LIVE_CREDENTIAL_SPRAY` (`FR-CHECKPOINT-01`
extended from five to six classes). Passive wireless/Bluetooth tools stay ungated.

You asked for wireless/Bluetooth task support plus "every possible tool" from
`kali-linux-everything`, and pushed back (correctly) on "too many to enumerate" —
**the fix was simpler than I made it sound**: put the full list in a separate reference
file, not inside the requirements corpus. Done — `KALI-TOOL-CATALOG.md` (the implementation
repository's root) now has the complete, current tool set for every one of Kali's ~29 official tool categories
plus everything else `kali-linux-everything` bundles directly, pulled straight from this
machine's own `apt-cache show` output (not reconstructed from memory). `FR-TOOL-03`'s
Tier 2 dynamic bridge already lets the AI invoke any resolvable binary — the missing
piece was purely *discoverability*, which the new file now solves directly.

> ### FR-DISCOVER-01: Consult `KALI-TOOL-CATALOG.md` for Undefined Task Domains
> * **Statement**: When a task falls in a domain with no dedicated Tier 1 schema (e.g.
>   wireless, Bluetooth, forensics, hardware), the system MUST consult
>   `KALI-TOOL-CATALOG.md` (the implementation repository's root — a reference file, not a requirement doc, kept
>   current against `apt-cache show kali-linux-everything` and its category
>   metapackages) for candidate tool names in that category, rather than the Scripter
>   guessing at binary names or the corpus trying to enumerate every tool inline.
> * **Pre-conditions & Inputs**: A task is tagged with a domain that has no dedicated
>   Tier 1 tool already covering it.
> * **Post-conditions & State Mutations**: The matched category's candidate list is
>   surfaced to the Scripter as available options for that task, resolved through
>   `FR-DISCOVER-02`.
> * **Edge & Failure Behaviors**: An untagged/unknown domain, or one not found in the
>   catalog, falls back to `FR-TOOL-03`'s generic Tier 2 bridge unchanged — this is
>   additive, not a replacement. If the catalog file itself is missing/unreadable, log
>   degraded and fall back the same way — never block the task on a reference-file read.
> * **Target Verification**: *(new test row needed in `09`)*

> ### FR-DISCOVER-02: Presence Check Before Suggesting
> * **Statement**: Before a domain's candidate tools are offered to the Scripter, the
>   system MUST check each one's actual presence (`shutil.which`, the same pattern
>   `oob_listener.py`'s graceful-degradation already uses) — only present binaries are
>   offered as immediately callable; absent ones are reported as "known, not installed"
>   naming the Kali/apt package that provides them.
> * **Target Verification**: *(new test row needed in `09`)*

> ### FR-DISCOVER-03: No Autonomous Package Installation Without Explicit Opt-In
> * **Statement**: The system MUST NOT run a package-manager install (`apt install`,
>   etc.) autonomously by default when a candidate tool is missing — this is a
>   system-modifying action outside this project's read-only-discovery/Tier-1-2-execution
>   model, with real supply-chain-trust and host-state implications. A Human Operator MAY
>   explicitly pre-authorize auto-install via runtime configuration (e.g. a `start` flag);
>   only then does installation proceed, via the same non-shell/`setsid`/logged subprocess
>   rules as everything else, with the install itself recorded in the audit trail.
> * **Edge & Failure Behaviors**: No opt-in given, tool missing: report it and continue —
>   never block the engagement waiting for a tool that isn't there.
> * **Target Verification**: *(new test row needed in `09`)*

**Safety note on WiFi/Bluetooth specifically**: several candidate tools are actively
disruptive by design (`aireplay-ng --deauth`, jamming-style Bluetooth attacks) — these
aren't passive recon, they knock real clients off a real network. **Recommend**: gate
these specific *active* wireless actions the same way `LIVE_CREDENTIAL_SPRAY` is gated
today (`FR-CHECKPOINT-01`'s fixed class list, or a new class alongside it) — autonomous
use requires the same opt-in flag pattern as `FR-TOOL-06a`'s other high-risk categories;
Human-Operator-directed use runs unconditionally as always. Purely passive
scanning/monitoring tools in the same domain (e.g. `bluetoothctl` device enumeration)
would not need this gate. Flagging this distinction for your confirmation rather than
deciding it myself, since it's a genuine new checkpoint-class question.

---

### Round 7 — Phase 5 Mobile Runtime Tools as Tier 1 Candidates

**Status: ✅ MERGED (decision #77).** `19:FR-MOBILE-08` added exactly as drafted:
`objection` formally registered (closing the "named in prose, not schema-registered"
gap against `FR-MOBILE-03`/`05`); `mobsf` added as new static+dynamic analysis
capability. The flagged design question (spawned per-task vs. long-lived local
service) was resolved as per-task-spawned, consistent with this system's
single-residency posture for everything outside the council models themselves.

The arsenal's Phase 5 (2 tools): `mobsf`, `objection`. This project already has a full
Mobile domain (`19:FR-MOBILE-01..07`, `MOBILE_BINARY` target type) — `objection` is
already *named* there (`FR-MOBILE-03`'s cert-pinning bypass, `FR-MOBILE-05`'s utility
list) but not registered as a formal Tier 1 schema entry the way `01`'s tools are.
`mobsf` (Mobile Security Framework — static + dynamic analysis, its own local web UI/API)
isn't mentioned in `19` at all yet.

> ### FR-MOBILE-08 (new): `mobsf` and `objection` as Registered Tools
> * **Statement**: `objection` is formally registered as a Tier 1/Tier 2 tool matching
>   its existing use in `FR-MOBILE-03`/`05` (no functional change, just formal schema
>   registration closing the gap between "named in prose" and "actually callable via a
>   declared schema"). `mobsf` is added as a new Tier 1 tool for static+dynamic mobile
>   analysis, offered as an alternative/complement to the `apktool`/`jadx` + manual-Frida
>   path `FR-MOBILE-01`/`02` already specify — not a replacement for the
>   runtime-first-never-decompile-first methodology `FR-MOBILE-01` mandates.
> * **Edge & Failure Behaviors**: `mobsf` typically runs as a local service (own web
>   UI/API) rather than a one-shot CLI invocation — needs a design decision on whether
>   it's spawned per-task or kept as a longer-lived local service the Scripter calls
>   into; flagging this rather than assuming.
> * **Target Verification**: *(new test row needed in `09`)*

**Also touches**: `06:FR-MOBILE-06`'s hardware-constraint note (emulator RAM budget)
already covers `mobsf`'s likely resource footprint if it needs an emulator too — no new
constraint, just confirming it applies.

---

### Round 6 — Phase 4 Exploitation Tools as Tier 1 Candidates (AI-Gated Loop Only)

**Status: ✅ MERGED (decision #77), including the requested gap-check.** The 4
genuinely-new tools (`dalfox`, `xsstrike`, `ghauri`, `fuxploider`) registered exactly
as drafted. The gap-check against `19` (performed before merging, per explicit
instruction, rather than assuming redundancy either way) found: `cewler` and the
hashcat-rule-mutation technique were already named in `FR-CRED-01`'s prose —
**formally Tier 1 schema-registered now, not skipped as a duplicate** — same
treatment for `interactsh-client`, already an explicitly required dependency per
`FR-ARGUS-02`. `hashcat`, `cupp`, `trevorspray`, `kerbrute` were not named anywhere in
`19` — genuinely new registrations implementing `FR-CRED-01`'s existing 4-stage
framework (`kerbrute` closes a real gap: `FR-CRED-03`'s mode list had no Kerberos/AD
mode). All ten tools registered — per standing instruction, overlap with existing
mechanisms is documented accurately, never used as grounds to skip registration.

The arsenal's Phase 4 (11 tools). **Confirmed staying out of `FR-BASELINE`'s zero-AI
pipeline** — these are exploitation-class, gated through the normal Gate 1/Gate 2/
Adjudicator loop like any other Tier 2 action, same as `sqlmap` (already registered)
already works today.

**Genuinely new capability, no current overlap** — straightforward Tier 1 additions:
- `dalfox`, `xsstrike` — XSS scanning/confirmation (no dedicated XSS tool currently registered)
- `ghauri` — blind-SQLi specialist, complements rather than replaces `sqlmap`
- `fuxploider` — file-upload RCE testing (no current equivalent)

**Needs a gap-check before registering, not assumed redundant** — flagging these as
*likely* overlapping existing project mechanisms, rather than either registering or
skipping them without checking first:
- `hashcat`, `cewler`, `cupp`, `trevorspray`, `kerbrute` — `19:FR-CRED-01` already
  specifies a 4-stage credential-attack pipeline (wordlist gen, breach enrichment,
  employee OSINT, live spray). Worth checking whether these five tools are the
  *implementation* of stages `FR-CRED-01` already calls for, or genuinely new capability
  it's missing — my guess is the former (these look like exactly the tools that pipeline
  would use), meaning this is a "confirm it's built," not "register something new."
- `interactsh-client` — already wrapped by `oob_listener.py` per
  `ASSET-CLASSIFICATION.md`'s own finding. Almost certainly already covered; would need
  confirming `oob_listener.py` is actually wired to a Tier 1 schema, not just archived
  as reference material.

**Recommend**: approve the 4 genuinely-new tools now; treat the credential/OOB five as a
"verify existing coverage" task rather than a registration task, since duplicating an
already-built mechanism under a new name would be worse than doing nothing.

---

### Round 5 — Expand `FR-BASELINE` With the Full Personal Tool Arsenal

**Status: ✅ MERGED in full**, with a correction applied after initial merge (`01`, `09`,
`13`, `18`; decision #76 in `10`, amended by a same-session follow-up).

- Pulled the actual 72-tool arsenal from the operator's portfolio report; scoped to
  Phase 1+2+3 (recon, enumeration, **and assessment** — assessment folded in per
  operator correction, since those tools are detection/read-only probes, not
  exploitation) for the zero-AI `FR-BASELINE` pipeline. Phase 4/5 (exploitation, mobile
  runtime) confirmed excluded, spun into their own rounds below (6, 7).
- Trigger point moved: runs between Phase 1 and Phase 2 (before the first model loads
  at all), not after Phase 3 — resolved without renumbering any phase, since the
  pipeline's direct safe-subprocess dispatch doesn't need Phase 3's AI-facing schema
  registration.
- Execution model: 4 dependency waves, bounded parallel execution within each wave
  (default 8 concurrent) — `naabu` (fast sweep) → `nmap -sV` (targeted, naabu's ports
  only) satisfies "use both naabu and nmap."
- **Post-merge correction** (operator: "overlap is always welcome, even when purposes
  overlap"): the initial merge trimmed several overlapping-purpose tools for efficiency
  (a judgment call, not requested) — reversed on operator correction. Added back
  `bbot`/`theHarvester`/`knockpy`/`dnsrecon`/`massdns`/`shuffledns` (Wave 1) and
  `waymore`/`hakrawler`/`gospider`/`cariddi`/`aquatone`/`eyewitness` (Wave 3); `sublert`
  now runs in both `FR-BASELINE` (one-shot) and `FR-MONITOR` (continuous) rather than
  only the latter. Only `maigret`/`pywhat` stay Tier-2-only — not a trim, an input-shape
  mismatch (username/string input, not domain/IP, so a blind per-target pipeline has
  nothing to feed them).

Traceability: `18` doc `01` 109→119 (78 covered); corpus baseline 348→361 (185 covered).

---

### Round 4 — Baseline Recon Pipeline, Efficiency Re-Check, Deferred-Gap Integration Points

**Status: ✅ MERGED in full** (`01`, `03`, `05`, `09`, `13`, `16`, `18`; decision #75 in `10`).

- **R4.1/R4.2 (efficiency re-check)**: `port_scanner.py`'s "redundant with `nmap`"
  verdict overturned after reading the actual script — `naabu` (fast broad-port
  discovery) and `nmap -sV` (deep version detection) solve different problems, not the
  same job at different verbosity. `lead_board.py`/`memory_gc.py`/`validate.py`'s
  redundancy verdicts confirmed correct on inspection.
- **R4.3**: `16:TR-SCRIPT-06` rewritten concretely as new `01:FR-BASELINE-01..04` — a
  deterministic, zero-AI pipeline (`naabu` → `whatweb` → `ffuf`/`feroxbuster` → `nuclei`)
  that runs automatically once per target right after Phase 3, feeding its structured
  output verbatim into the Lead Strategist's first Phase 4.1 invocation. `naabu` added
  to `FR-TOOL-01`'s Tier 1 roster (the open naabu-vs-tuned-nmap decision resolved in
  naabu's favor, per the recommendation).
- **R4.4**: `FR-TOOL-17` (authenticated session reuse) + `03:DR-SCHEMA-22
  auth_sessions` + `05:SEC-DATA-04` (inherits `FR-TOOL-15`'s no-raw-secret-in-logs
  pattern).
- **R4.5**: `FR-TOOL-18` (fingerprint-triggered EOL/CVE lookup) + `03:DR-SCHEMA-23
  tech_fingerprint_intel` — fed for free by `FR-BASELINE-01`'s `whatweb` step.
- **R4.6**: `FR-TOOL-19` — `multipart_mutator.py`'s technique registered as a proper
  schema'd Tier 1 tool instead of staying an interactive one-off CLI.

Test coverage: new `09:TP-BASELINE` and `09:TP-TOOLEXT` clusters. Traceability: `18`
doc `01` 109→116 (75 covered), doc `03` 34→36 (24 covered), doc `05` 28→29 (19 covered),
corpus baseline 348→358 (182 covered).

### Round 3 — Secondary Scripter: Dual-Scripter Council Architecture

**Status: ✅ MERGED in full** (`01`, `03`, `09`, `13`, `14`, `18`, `22`, `23`, `15`,
`Agentic VAPT Setup (HOME).md`; decision #74 logged in `10`).

The Alignment Linter (`Qwen2.5-Coder-3B-Instruct`) is retired. Syntax checking is now
Gate 2 **Tier 2A** (`ast.parse()`/`py_compile`/`bash -n`, zero LLM), alongside **Tier 2B**
(existing schema/flag validation) and new **Tier 2C** (orthogonal-vector deduplication
against `03:DR-SCHEMA-21 scripter_execution_ledger`). A **Secondary Scripter**
(`DeepSeek-Coder-6.7B-Instruct`) is added: Phase 4.2 is now batch-sequential — **4.2A**
(Primary Scripter, baseline pass, all targets) → full unload → memory-settle → **4.2B**
(Secondary Scripter, orthogonal pass, all targets, explicitly excluding every vector
Primary already tried, enforced deterministically by Tier 2C, not model self-restraint).
Council size unchanged at 6 — a clean swap, not a growth.

**Naming:** an external draft of this proposal used "Operator"/"Beta"/mismatched enum
naming for the new role (`Operator Beta`, `Primary Operator`, `PRIMARY_OPERATOR` vs.
`SECONDARY_SCRIPTER`, `@op1`/`@op2`, `TP-OP-ORTHOGONAL-01`, `operator_execution_ledger`)
— confirmed a mistake of an outdated external source and ignored throughout. **Secondary
Scripter** / **Primary Scripter** / `PRIMARY_SCRIPTER`/`SECONDARY_SCRIPTER` /
`@script1`/`@script2` / `TP-SCRIPT-ORTHOGONAL-01` / `scripter_execution_ledger` used
consistently instead, matching the corpus-wide rename (decision #72).

**Codebase question, resolved:** confirmed no `vapt_agent/` directory or Python source
exists anywhere in this repo (verified by search) — this stays documentation-only,
per `00`'s own "Planning phase only" status. Folded into `13`'s already-documented module
tree and prose (`gate2_validator.py`, `phase_lifecycle.py`, `secondary_scripter.py`
descriptions) rather than creating real `.py` files.

**Schema-duplication question, resolved:** kept `scripter_execution_ledger` as a separate
narrow table (not merged into `tool_execution_logs`) but documented explicitly why: it
exists purely as a fast lookup index for Tier 2C's hash-membership check, populated by
the same write path as `tool_execution_logs` — never a second source of truth for *what
happened*, only for *has this exact vector been tried yet*.

**Post-merge consistency check** (explicitly requested) caught and fixed 3 real defects
the new architecture introduced, none of which were part of the original directive:
- `01:FR-COUNCIL-12`'s unload-timing wording didn't account for the new two-sub-phase
  split (fixed: Primary unloads at 4.2A's end, Secondary at 4.2B's end, both still
  "never per-task/per-target").
- `01:FR-GATE-07`'s context-ceiling table still listed the retired
  `Qwen2.5-Coder-3B-Instruct` and omitted the new model entirely (fixed: removed the
  stale 4k tier, added `DeepSeek-Coder-6.7B-Instruct` at 16k).
- `23:FR-INTERVENE-07`'s per-invocation directive-injection list still named "the
  Alignment Linter's between-phase invocation" instead of the new Phase 4.2B invocation
  point (fixed).

Also fixed in `HOME.md` (not a defect from this round, but caught during the same pass):
the relay diagram's Gate 2 label still said "Is the command safe?" — the exact "safety"
framing R2.3 established was wrong for this check — and a leftover pre-R2.6 sentence in
the user story still described Console commands as "overriding" the AI instead of
running alongside it. Both corrected.

**Memory budget:** verified fine — `DeepSeek-Coder-6.7B-Instruct` (~7.2 GB) is smaller
than the largest existing model (~8.6 GB), and models never reside concurrently
(`FR-GATE-02`), so the peak single-model memory ceiling, ~13.0 GiB post-hibernation
headroom target, and 1.5 GiB safety margin are all unaffected.

---

### R2.6 — Console Command Handling: Conflict Flag + Corrected Requirement

**Status: ✅ MERGED.** Confirmed exactly as drafted: the Human Operator's command runs
alongside the LLM's pre-defined tasks; on genuine conflict (same resident-model slot),
the Human Operator's command wins. Applied to `23:FR-INTERVENE-06`. Decision #73 logged
in `10`.

Root cause this fixed: `23:FR-INTERVENE-05` said directives are dispatched "ahead of
pending autonomous tasks" (ordering — both run), while `FR-INTERVENE-06` said directives
"supersede autonomous tasks... unconditionally" (sounds like replacement) — the two were
in tension before this correction.

---

### R2.3 — Alignment Linter Elimination

**Status: ✅ RESOLVED — subsumed by Round 3.** You asked *"why do I even need the Linter
LLM!?"* — the recommendation (eliminate it, absorb syntax-checking into deterministic
Gate 2) is exactly what Round 3 did, plus added the Secondary Scripter as its
replacement council seat. No separate action needed beyond what's recorded above.

---

### Round 2 — Role Renaming, Function Corrections & New Requirements

**Status: ✅ MERGED in full**, across `01`, `03`, `05`, `06`, `09`, `10`, `18`,
`CHANGELOG.md`, and (via a background sweep) `00`, `04`, `07`, `08`, `11`–`17`, `19`,
`21`–`24`, and `HOME.md`. "Analyst" was a naming mistake, corrected to **Strategy
Auditor**.

**Final role mapping applied corpus-wide:**

| Old name(s) | New name |
|---|---|
| Lead Strategist | **Lead Strategist** *(unchanged)* |
| Scope Gate / Gatekeeper / Council Gate 1 (Tier 1, semantic) | **Strategy Auditor** |
| Lead Operator / bare AI-role "Operator" | **Primary Scripter** |
| Offline Script Linter | *(retired entirely — see Round 3)* |
| Adjudicator / Gate 3 | **Criterion Adjudicator** |
| Executive Reporter | **Executive Reporter** *(unchanged)* |
| Any human "operator"/"Operator" | **Human Operator** (exact phrase, every occurrence) |
| `Operator-Directed Mode` | **Human-Operator-Directed Mode** |
| `MANUAL_OPERATOR` | **`HUMAN_OPERATOR`** |
| `OPERATOR_DIRECTIVE` | **`HUMAN_OPERATOR_DIRECTIVE`** |
| `operator_command_queue` | **`human_operator_command_queue`** |
| `operator_identity` | **`human_operator_identity`** |

Verified by whole-corpus grep with zero stale hits (two deliberate, confirmed-correct
exceptions: "NoSQL operator-injection" in `19` and lowercase "gatekeeper" in `HOME.md` —
both genuinely unrelated meanings, not role references). `13`'s module-layout filenames
renamed to match (`strategy_auditor.py`, `primary_scripter.py`, `criterion_adjudicator.py`,
`secondary_scripter.py` — the last one corrected during Round 3 after briefly landing as
`alignment_linter.py`, which would have cemented the deprecated role into the module
tree).

**R2.2 — Strategy Auditor function correction:** `05:SEC-SCOPE-01` reworded — "Council
Gate 1" means Tier 0 + Tier 1 combined; only Tier 0 mechanically checks `scope_rules`;
the Strategy Auditor never itself decides scope, only whether the Lead Strategist's plan
addresses it and makes sense.

**R2.4 — Human Operator guidance notes:** `01:FR-CTRL-01a` added — bounded inline
`--notes` only (500-char cap, rejected not truncated over-length), no `--notes-file`
(small council models can't usefully consume long documents). Schema, test rows, and
traceability all updated alongside.

**R2.5 — Error reporting & notification policy:** `06:OPS-NOTIFY-01`–`05` added —
severity tags surfaced live on Dashboard/Console, no silent full stops, a formal Error
Code Dictionary (your "do we need a dictionary" question — yes), and full raw error
printing to the terminal for pre-Dashboard/Console technical failures (your "this is a
technical step" point).

**R2.7 — Persistence/pause-resume:** confirmed already existing and fairly robust
(`FR-CTRL-02`/`03`, `OPS-LIFECYCLE-02`/`03`/`04`, the whole SQLite WAL state store) — no
new requirement was needed.

---

### Items 1 & 2 — Hibernation Self-Exclusion + Dashboard/Console Exposure

**Status: ✅ MERGED** (approved with a rectification changing the operator workflow
itself, applied to `01`, `10`, `18`, `22`, `23`).

Rather than generalizing hibernation-detection to recognize arbitrary `vaptctl`
processes in arbitrary terminals, the operator workflow changed instead: `dashboard`/
`console` are no longer manually launched concurrently with `start`. `start` now
auto-launches both automatically, in new terminal windows, immediately after Phase 1
hibernation's headroom check clears and strictly before Phase 2 — removing the
concurrent-launch race at its root, since by the time `dashboard`/`console` exist the
one-shot hibernation sweep is already over. `FR-ENV-03a`/`08a`/`08b`/`08c` added to `01`;
the standalone `vaptctl dashboard`/`vaptctl console` commands remain, re-scoped
explicitly as manual-recovery commands.

---

## How to add new items

New items go **above the archive, under "Currently Pending Approval"** — newest on top,
per standing instruction. Same format as always: problem statement → root cause →
proposed fix (exact draft text, per `CLAUDE.md` §5 schema where a real requirement is
being authored) → status. Nothing in this file is binding until explicitly approved and
applied to the numbered docs.
