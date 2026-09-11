# Functional Requirements — Autonomous Agentic VAPT System

Priority key (MoSCoW): **M** = Must have, **S** = Should have, **C** = Could have.
This document governs the phase-by-phase execution pipeline: operational workflows,
execution order, council role deliverables, and state transition triggers. The pipeline
implements a Dual-Mode Execution Architecture: Autonomous Mode enforces non-destructive
testing boundaries (permitting read and safe verification writes while barring destructive
mutations and DoS), whereas Human-Operator-Directed Mode executes the Human Operator's
instructions unconditionally with zero refusal. Gating and containment rationale are
governed authoritatively by the Security Specification (`05`).

---

## Council Roster

| Role | Model Identifier | Quantization | Memory Footprint | Function |
|---|---|---|---|---|
| **Lead Strategist** | `DeepSeek-R1-0528-Qwen3-8B` | `Q8_0` | ~8.6 GB | Phase 4.1 — produces the attack-path plan (`FR-COUNCIL-01`/`02`) |
| **Strategy Auditor** | `Hermes-3-Llama-3.1-8B` | `Q8_0` | ~8.4 GB | Phase 4.1 — audits whether the Lead Strategist's plan addresses the Human-Operator-defined scope, and whether it's sound (`FR-COUNCIL-04`); never itself decides what is in/out of scope |
| **Primary Scripter** | `Qwen2.5-Coder-7B-Instruct` | `Q8_0` | ~8.0 GB | Phase 4.2A — turns an approved task into a concrete tool invocation, stays resident for the whole per-target loop until its queue is exhausted (`FR-COUNCIL-07`) |
| **Secondary Scripter** | `DeepSeek-Coder-6.7B-Instruct` | `Q8_0` | ~7.2 GB | Phase 4.2B — loads only after the Primary Scripter fully unloads; pursues attack vectors orthogonal to everything the Primary Scripter already tried (`FR-COUNCIL-11c`) |
| **Criterion Adjudicator** | `Mistral-7B-Instruct-v0.3` | `Q8_0` | ~7.6 GB | Phase 4.3 — evaluates candidate findings against raw evidence and false-positive criteria (`FR-COUNCIL-13`/`14`) |
| **Executive Reporter** | `Ministral-8B-Instruct-2410` | `Q8_0` | ~8.4 GB | Phase 4.3 — drafts the client-facing finding writeup (`FR-COUNCIL-16`) |

*(Context ceilings are enforced per `FR-GATE-07`, not repeated here since they're a
runtime behavior, not an identity fact. Memory footprints are approximate at this
quantization; see `15-Implementation-Milestone-Roadmap.md` for build sequencing. This
table is this corpus's canonical council roster — it replaced an equivalent table
formerly in `CLAUDE.md`, which is agent operating instructions, not a technical
specification. `Agentic VAPT Setup (HOME).md`'s Section 3 table mirrors this one
verbatim — update both together.)*

---

## FR-PRE — Phase 0: Pre-Flight Self-Test

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-PRE-01 | Verify the inference engine is installed, version recorded, not already running, before Phase 1. | M |
| FR-PRE-02 | Verify the Level Zero/SYCL/OpenCL runtime can enumerate the Arc iGPU; fall back to documented CPU-only mode on failure, never fail silently. | M |
| FR-PRE-03 | Verify each council model file exists at its expected path/quantization (checksum or size check) before Phase 4. | M |
| FR-PRE-04 | Verify presence of every Tier 1 tool binary; record installed versions to the state store. | M |
| FR-PRE-05 | Verify the NVMe artifact path exists, is writable, and is not a `tmpfs` mount. | M |
| FR-PRE-06 | Record RAM/swap/disk-free as a pre-flight baseline snapshot before Phase 1 hibernation begins. | M |
| FR-PRE-07 | Pre-flight produces one pass/fail report; any failure blocks Phase 1 unless the Human Operator overrides with a logged justification. | M |
| FR-PRE-08 | One-time GPU-offload benchmark: run the same fixed inference with SYCL offload and forced CPU-only, compare tok/s. If offload fails or doesn't beat CPU-only, flag the **entire engagement** CPU-only from the start (not discovered mid-Phase-4). Record both measurements in `engagement_phase_log`. | M |

---

## FR-ENV — Phase 1: Environment, Storage & Memory Preparation

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-ENV-01 | Redirect all agent artifacts/logs/temp files to the NVMe path; MUST NOT write working data to `tmpfs`-backed `/tmp`. | M |
| FR-ENV-02 | Set `TMPDIR`/`TEMP`/`TMP` to the NVMe path for the agent process tree and any subprocess. | M |
| FR-ENV-03 | Enumerate active GUI processes; classify each "hibernation-eligible" or "protected" against a fixed denylist (`systemd`, `dbus`, compositor, session manager, audio server) before any signal. | M |
| FR-ENV-03a | The fixed denylist (FR-ENV-03) MUST also unconditionally protect the invoking terminal session — the TTY/PTY, terminal emulator, and any terminal-multiplexer process tree the `start` command was launched from — plus the agent's own process tree, walking parent PIDs to the session leader before enumeration. The hibernation step MUST NOT suspend the session it is itself running from, even transitively. *(Field-observed defect: naive process enumeration classified the launching terminal as hibernation-eligible, causing the orchestrator to suspend itself mid-run.)* | M |
| FR-ENV-04 | MUST NOT `SIGSTOP` a process holding an open file lock on unsaved document state — unconditional, not Human-Operator-waivable. | M |
| FR-ENV-05 | Record the full PID/process-tree of every suspended application, sufficient to reverse deterministically in Phase 5. | M |
| FR-ENV-06 | No runtime confirmation prompt before the first `SIGSTOP` — invoking `start` is the Human Operator's consent for the whole non-interactive pipeline. Suspended-app list still logged (FR-ENV-05). | M |
| FR-ENV-07 | SHOULD trigger `process_madvise(MADV_PAGEOUT)`/cgroup reclamation on suspended PIDs; MUST NOT touch protected processes. Requires elevated capability the main process doesn't hold — see FR-ENV-13. | S |
| FR-ENV-08 | Re-measure available RAM after hibernation; abort progression to Phase 2 if headroom is below the smallest model's requirement plus the fixed safety margin. | M |
| FR-ENV-08a | Immediately once FR-ENV-08's headroom check passes — and strictly before Phase 2 begins — the `start` command MUST automatically launch both `vaptctl dashboard` and `vaptctl console`, each as a new child process in its own new terminal-emulator window, bound to the engagement `start` just created. The Human Operator MUST NOT need to enter any separate command for this to happen in the default flow. *(Design rectification: this replaces the earlier, riskier pattern of the Human Operator manually launching `start`/`dashboard`/`console` as three concurrent commands, which is what exposed the dashboard/console terminals to the same hibernation-eligibility bug as FR-ENV-03a — launching them only after the one-shot Phase 1 sweep has already completed removes that exposure at the root, rather than requiring hibernation to recognize arbitrary `vaptctl` processes.)* | M |
| FR-ENV-08b | Terminal-window spawning for FR-ENV-08a MUST use a configurable, auto-detected terminal-emulator launch command, checked in order: the `$TERMINAL` environment variable if set, then `gnome-terminal`, `konsole`, `xfce4-terminal`, `x-terminal-emulator`, `xterm`. Each window is spawned via `subprocess.Popen` with an explicit argument vector (never `shell=True`) in its own process group (`preexec_fn=os.setsid`), per this system's standard subprocess rules. | M |
| FR-ENV-08c | If no supported terminal emulator can be located, or either spawn attempt fails, this MUST degrade gracefully: log a warning naming the specific failure, continue the Phase 1→Phase 2 transition without aborting the engagement, and print Human-Operator-facing guidance to manually run `vaptctl dashboard`/`vaptctl console` instead. | M |
| FR-ENV-09 | Initialize the SQLite state store before Phase 2 begins. | M |
| FR-ENV-10 | An existing `IN_PROGRESS`/`PAUSED` engagement is offered for resume, never silently overwritten. | M |
| FR-ENV-11 | Before the memory-reclamation step, lower OOM-kill priority for every suspended PID to `oom_score_adj = -900` (not `-1000`) — hibernated apps are the *last* OOM-kill candidate; the agent's own processes are more eligible by comparison. | M |
| FR-ENV-12 | Verify every suspended PID is still alive post-hibernation; log and report any OOM casualty, and mark the outcome partial/degraded, not full success. | M |
| FR-ENV-13 | `SIGSTOP`/`oom_score_adj`/`process_madvise` MUST run via a narrow, single-purpose helper (`vapt-freezer-helper`) granted only the specific capability needed (`setcap cap_sys_ptrace+ep`) — the main agent process MUST NOT hold elevated capability. Fall back to cgroup v2 limits if the helper/capability is unavailable, never silently skip. | M |
| FR-ENV-14 | The hibernation guarantee covers process memory/UI state only, not network/session continuity — resumed apps may show reconnect prompts; this is expected, documented behavior, not a defect. | M |

---

## FR-GATE — Phase 2: Local Inference Gateway

**Engine:** `llama.cpp --server`, native SYCL backend. No `keep_alive` hot-swap
exists in raw `llama.cpp` — load/unload is explicit process spawn/terminate via the
**Local Engine Client** interface, abstracted so `ollama` can substitute later.

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-GATE-01 | Expose a single loopback-only OpenAI-compatible endpoint (`127.0.0.1:11434/v1`); MUST NOT bind non-loopback by default. | M |
| FR-GATE-02 | Hard single-model-residency: at most one council model resident at any instant; loading a second requires the first fully unloaded and confirmed first. | M |
| FR-GATE-03 | Pin inference threads to the 4 P-Core/8-thread group; leave E-Cores free for subprocess/tool execution. | M |
| FR-GATE-04 | Attempt SYCL GPU offload; fall back to CPU-only (logged degraded) if unavailable, rather than failing the engagement. | M |
| FR-GATE-05 | Evict weights+KV cache within a bounded window after each phase step; verify freed memory before declaring the step complete. | M |
| FR-GATE-06 | Log every inference call (model, role, token counts, latency, phase/step ID) to `model_invocation_logs`. | M |
| FR-GATE-07 | Enforce per-model context ceilings: 8k (DeepSeek-R1-0528-Qwen3-8B / Hermes-3-Llama-3.1-8B / Mistral-7B-Instruct-v0.3), 16k (Qwen2.5-Coder-7B-Instruct / DeepSeek-Coder-6.7B-Instruct / Ministral-8B-Instruct-2410). Truncate/summarize on overflow, never silently error. *(Corrected post-Round-3: `Qwen2.5-Coder-3B-Instruct`'s 4k tier is removed along with the retired Alignment Linter role; `DeepSeek-Coder-6.7B-Instruct` added at 16k, matching the Primary Scripter's tier since the Secondary Scripter's exhausted-vectors exclusion block benefits from the same headroom.)* | M |
| FR-GATE-08 | Detect engine crash/unresponsiveness (no token progress within a timeout); attempt one restart, escalate to `PAUSED` on repeated failure. | M |
| FR-GATE-09 | Model load/unload exclusively via the Local Engine Client; `unload` MUST verify complete OS-level process exit (`waitpid`), not just an API ack. | M |
| FR-GATE-10 | After confirmed exit, poll `/proc/meminfo` `MemAvailable` and MUST NOT spawn the next model until it clears the documented minimum-headroom threshold. Bounded to 5s; raise a degraded-swap alert on timeout rather than spawn into a tight memory state. | M |

---

## FR-TOOL — Phase 3: Security Framework & Kali Tool Bridge

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-TOOL-01 | Provide schema-validated Tier 1 wrappers for the original core set: `nmap`, `masscan`, `nuclei`, `ffuf`, `feroxbuster`, `gobuster`, `sqlmap`, `nikto`, `whatweb`, `wafw00f`, `testssl`, `script_runner` (`FR-TOOL-16`); plus the full recon/enumeration/assessment roster registered for the baseline pipeline (`FR-BASELINE-06`'s table) — `naabu`, `subfinder`, `amass`, `assetfinder`, `bbot`, `theHarvester`, `knockpy`, `sublert`, `dnsrecon`, `massdns`, `puredns`, `shuffledns`, `httpx`, `dnsx`, `aquatone`, `eyewitness`, `katana`, `gau`, `waybackurls`, `waymore`, `hakrawler`, `gospider`, `cariddi`, `gf`, `qsreplace`, `anew`, `arjun`, `x8`, `dnsreaper`, `subjack`, `semgrep`, `log4j-scan`, `graphql-cop`, `jwt_tool`, `byp4xx`, `whatwaf`, `unwaf`, `s3scanner`, `cloud_enum`, `cloudfail`, `scoutsuite`, `trufflehog`, `noseyparker`, `gitleaks`, `shhgit`, `git-hound`, `apkleaks`, `jadx`, `graphw00f`, `clairvoyance`; plus `maigret`, `pywhat` (input-shape mismatch for the baseline pipeline — username/string, not domain/IP — registered as AI-selectable Tier 2 tools only, `FR-BASELINE-07`). All available to the AI-driven Phase 4.2 loop too, not exclusively the deterministic baseline pipeline. | M |
| FR-TOOL-02 | Each Tier 1 wrapper declares recognized flags, required arguments, and execution profiles machine-readably for Gate 2 validation. In Autonomous Mode, destructive capabilities (such as direct file wipes, database alters, drops, deletes, updates, or DoS triggers) are blocked to maintain non-destructive testing. In Human-Operator-Directed Mode, all wrapper flag restrictions and parameter suppressions stand down completely to execute the exact requested parameters. | M |
| FR-TOOL-03 | Tier 2 dynamic bridge (`run_security_command`): eligible binary MUST resolve (invocation path, not symlink target) inside `/usr/bin/`, `/usr/sbin/`, or `/opt/`; execution within scope is fully autonomous, no per-binary approval. | M |
| FR-TOOL-04 / 04a | Non-shell execution (`shell=False`, explicit argv) — no model output ever becomes a shell string; every subprocess spawns in its own session (`start_new_session=True`) so the kill-switch can reach its whole process group. | M |
| FR-TOOL-05 | Every subprocess has a mandatory timeout: Quick Probes 180s / Targeted Scans 900s / Deep-Full-Range 1800s. | M |
| FR-TOOL-06 | Tier 2 behavioral boundaries enforce the dual-mode policy: In Autonomous Mode, actions MUST NOT perform state destruction (strictly prohibiting DROP, DELETE, ALTER, UPDATE, rm, mkfs, dd, shred, fork-bombs, or DoS/resource-exhaustion tools). Safe reads (GET/SELECT) and non-destructive writes (POST) are permitted. In Human-Operator-Directed Mode, behavioral denylists stand down entirely, executing the requested command chain as instructed. | M |
| FR-TOOL-06a | High-risk testing categories (brute-force, active exploitation, lateral movement) run autonomously when enabled via runtime flags or profile configuration. When dispatched directly by the Human Operator via manual directive or console dispatch, these tasks execute immediately without requiring pre-set opt-in flags. | M |
| FR-TOOL-06b | In Autonomous Mode, an unconfigured high-risk task is marked DEFERRED and the engine continues discovery along alternative non-destructive paths. Any high-risk directive initiated or requested by the Human Operator executes immediately with zero refusal. | M |
| FR-TOOL-06c | The three flags are settable at `start`, independently updatable at `resume`; a change applies only to tasks generated after it, and is timestamped in `engagement_flag_history`. | M |
| FR-TOOL-07 | Sanitize raw stdout/stderr into structured signal (ports, banners, URLs, status codes); discard HTML/repetitive-404/binary noise before it reaches model context. | M |
| FR-TOOL-08 | Persist full unsanitized raw output to the artifact store regardless of what's summarized — evidence is never lost to summarization. | M |
| FR-TOOL-09 | Record exact argv, timestamps, exit code, and task ID for every subprocess execution in `tool_execution_logs`. | M |
| FR-TOOL-10 | SHOULD expose Burp Suite/Caido MCP configs and multi-turn assessment templates as reusable methodology assets. | S |
| FR-TOOL-11 | Support pointing `claude-bug-bounty`/`CyberStrike`/`strix` at the local endpoint via env-var overrides, no code modification. | S |
| FR-TOOL-12 | All target-derived content (banners, HTTP responses, tool logs) MUST be wrapped in boundary markers (<tool_output_untrusted>...</tool_output_untrusted>) prior to ingestion by model contexts to maintain context separation. | M |
| FR-TOOL-13 | SHOULD run a lightweight heuristic injection-pattern detector over raw target output (telemetry and detection only, never blocking or interrupting execution). | S |
| FR-TOOL-14 | Per-target spawn rate caps serve as anti-DoS and target stability guardrails during autonomous operations (default 10 invocations/s standard, 1/s high-volume). When running under direct Human Operator instruction, rate limits are dynamically adjustable or bypassable up to system/network capacity upon Human Operator demand. | M |
| FR-TOOL-15 | Configured target credentials propagate automatically to every Tier 1/Tier 2 call via env vars; only a `sha256(...)[:12]` correlation hash is logged, never the raw credential. Two distinct identities (low/high-privilege) are registrable as separate named sets. | M |
| FR-TOOL-16 | `script_runner`: the only path for executing a multi-line script that has passed Gate 2 Tier 2A (`FR-COUNCIL-08`) — `{script_body, interpreter, workspace_subdir}`, never an inline `-c`/`-e` string (does not reopen `FR-TOOL-06(b)`). `workspace_subdir` MUST resolve inside the artifact path; the script MUST pass Gate 2 Tier 2A's deterministic syntax check first; runs as `<interpreter> <file>` under the Targeted-Scans (900s) timeout tier. | M |
| FR-TOOL-17 | **Authenticated session reuse:** The system MUST support establishing a named authenticated session (cookie jar or bearer/token-based) against a target once, then automatically injecting that session's credentials into every subsequent Tier 1/Tier 2 call scoped to that session, without re-authenticating per call. A Human Operator supplies login credentials/a pre-captured session at `start` or via the Console, or an autonomous login-flow task succeeds (scope-gated identically to any other autonomous action). Session state is `03:DR-SCHEMA-22`. If a session is invalidated mid-engagement (logout, expiry), it is marked invalid and surfaced via `OPS-NOTIFY` — never silently left stale, since subsequent authenticated calls would otherwise look like false-negative findings; the system MUST NOT auto-retry login without fresh Human-Operator-supplied or autonomously-re-validated credentials. | M |
| FR-TOOL-18 | **Fingerprint-triggered EOL/CVE lookup:** Whenever a new `tech_fingerprint` entity is written to `discovered_entities` (including by `FR-BASELINE-01`'s pipeline), the system MUST automatically queue a follow-on Tier 2 task checking that `tech=version` pair against an EOL database (a plain `endoflife.date` lookup) and a CVE feed (GitHub Advisory DB/NVD by product+version), recording results (`03:DR-SCHEMA-23`) as corroborating evidence for the Reporter/Adjudicator — never as a finding by itself. If the EOL/CVE feed is unreachable, log degraded and continue; this is enrichment, not a required gate. | M |
| FR-TOOL-19 | **Multipart parser-confusion tool (Tier 1):** A declaratively-schema'd Tier 1 tool — `{target_upload_endpoint, file_path, variant_name \| "all"}` — covering the fixed, enumerable set of multipart parser-confusion variants (boundary confusion, duplicate-field injection, content-type mismatches). `file_path` MUST resolve inside the artifact workspace, rejected via the same boundary check `script_runner`'s `workspace_subdir` already uses (`FR-TOOL-16`) — no separate mechanism invented. Output uses the standard Tier 1 evidence shape, no bespoke reporting format. | M |
| FR-TOOL-20 | **Phase 4.2 AI-gated exploitation & specialist tools (Tier 1):** never members of `FR-BASELINE`'s zero-AI pipeline, gated through the normal Gate 1/Gate 2/Adjudicator loop like `sqlmap` already is. Genuinely new capability: `dalfox`, `xsstrike` (XSS scanning/confirmation — no prior dedicated XSS tool); `ghauri` (blind-SQLi specialist, complements rather than replaces `sqlmap`); `fuxploider` (file-upload RCE testing). Formal Tier 1 registration of tools already named in domain-19 prose (not net-new capability, just closing the "named in a requirement's text" vs. "actually schema-registered" gap): `hashcat`, `cupp`, `trevorspray`, `kerbrute` implement `19:FR-CRED-01`'s 4-stage credential-attack pipeline (`cewler` and hashcat-rule mutation were already registered under that same requirement's own text); `interactsh-client` implements `19:FR-ARGUS-01`'s OOB-callback confirmation, already an explicitly required dependency per `19:FR-ARGUS-02`; `mobsf`, `objection` implement `19:FR-MOBILE-08` (`objection` was already named in `FR-MOBILE-03`/`05` prose; `mobsf` is new mobile static+dynamic analysis capability). | M |

---

## FR-DISCOVER — Dynamic Domain-Based Tool Discovery

Extends `FR-TOOL-03`'s Tier 2 dynamic bridge for domains with no dedicated Tier 1
schema (wireless, Bluetooth, forensics, hardware, and the rest of Kali's tool
categories) — discoverability, not a new execution mechanism.

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-DISCOVER-01 | When a task falls in a domain with no dedicated Tier 1 schema, the system MUST consult `KALI-TOOL-CATALOG.md` (the implementation repository's root — a reference file, not a requirement doc, kept current against `apt-cache show kali-linux-everything` and its category metapackages) for candidate tool names in that category, rather than the Scripter guessing at binary names or this corpus enumerating every tool inline. An untagged/unknown domain, or one not found in the catalog, falls back to `FR-TOOL-03`'s generic Tier 2 bridge unchanged — additive, not a replacement. If the catalog file itself is missing/unreadable, log degraded and fall back the same way — never block the task on a reference-file read. | M |
| FR-DISCOVER-02 | Before a domain's candidate tools are offered to the Scripter, the system MUST check each one's actual presence (`shutil.which`, the same pattern `oob_listener.py`'s graceful-degradation already uses) — only present binaries are offered as immediately callable; absent ones are reported as "known, not installed" naming the Kali/apt package that provides them. | M |
| FR-DISCOVER-03 | The system MUST NOT run a package-manager install (`apt install`, etc.) autonomously by default when a candidate tool is missing — a system-modifying action outside this project's read-only-discovery/Tier-1-2-execution model, with real supply-chain-trust and host-state implications. A Human Operator MAY explicitly pre-authorize auto-install via runtime configuration (e.g. a `start` flag); only then does installation proceed, via the same non-shell/`setsid`/logged subprocess rules as everything else, with the install itself recorded in the audit trail. If no opt-in is given and a tool is missing, report it and continue — never block the engagement waiting for a tool that isn't there. | M |
| FR-DISCOVER-04 | Actively disruptive wireless/Bluetooth actions discovered via `FR-DISCOVER-01` (e.g. `aireplay-ng --deauth`, jamming-style Bluetooth attacks — these knock real clients off a real network, not passive recon) are classified under the `ACTIVE_WIRELESS_DISRUPTION` checkpoint class (`FR-CHECKPOINT-01`), gated identically to `LIVE_CREDENTIAL_SPRAY`: autonomous use requires the same opt-in flag pattern as `FR-TOOL-06a`'s other high-risk categories; Human-Operator-directed use runs unconditionally as always. Purely passive scanning/monitoring tools discovered in the same domain (e.g. `bluetoothctl` device enumeration) are ordinary Tier 2 tools, not subject to this gate. | M |

---

## FR-BASELINE — Deterministic Baseline Reconnaissance, Enumeration & Assessment (Phase 1 → 2 Bridge)

Runs once per target, automatically, with **zero AI model invocation** — a fixed,
bounded-parallel pipeline, not an AI-selected one. Its whole purpose is to hand the Lead
Strategist a real, already-discovered starting surface instead of a blank target, and to
do it using the RAM Phase 1 just freed, before any model competes for that memory.

**Trigger point (revised): runs between Phase 1 and Phase 2, not after Phase 3.** Tool
invocation here uses the same safe-subprocess conventions Tier 1/Tier 2 use
(`shell=False`, `preexec_fn=os.setsid`, tiered timeouts) directly — it does not require
Phase 3's AI-facing Tier 1 schema registration to be complete first, since no AI ever
selects a tool here. This lets the whole pipeline run immediately after Phase 1's
headroom check passes, fully before Phase 2 loads the first model, maximizing available
RAM/CPU for parallel execution. Phase 2 and Phase 3 keep their existing numbers and
scope (Phase 3's Tier 1/Tier 2 schema registration still exists for the AI-driven Phase
4.2 loop) — only the wall-clock position of this new pipeline changes.

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-BASELINE-01 | Immediately once Phase 1's headroom check (`FR-ENV-08`) passes — before Phase 2 begins loading any model, and before `FR-ENV-08a`'s dashboard/console auto-launch if both land at the same trigger point, dashboard/console auto-launch takes priority so the Human Operator has visibility while this pipeline runs — the system MUST automatically run the fixed tool set in `FR-BASELINE-06`'s table, grouped into dependency waves (`FR-BASELINE-02`). First-run-per-target only; skipped on `resume` if already completed for that target (matching `06:OPS-LIFECYCLE-02`'s "don't redo completed work" pattern). | M |
| FR-BASELINE-02 | Tools within the same wave (`FR-BASELINE-06`'s "Wave" column) MUST run in parallel with each other, bounded by a configurable max-concurrency cap (default 8 concurrent subprocesses) — never unbounded, to avoid CPU/network contention and to keep `FR-TOOL-14`'s per-target spawn-rate guardrails meaningful even during this deterministic phase. A wave MUST NOT start until every tool in the prior wave has completed or timed out — later waves consume earlier waves' outputs (e.g. `nmap -sV` in Wave 2 targets only the ports `naabu` found in Wave 1). | M |
| FR-BASELINE-03 | Each tool's raw output persists via the existing `tool_execution_logs`/`artifacts_index` path — ordinary Tier 1/Tier 2-shaped execution, deterministically dispatched instead of AI-selected; no new storage mechanism. | M |
| FR-BASELINE-04 | A structured summary (subdomains, live hosts, ports, technologies fingerprinted, discovered paths/parameters, baseline `nuclei`/assessment-tool hits) is assembled directly from those persisted rows and injected verbatim into the Lead Strategist's first Phase 4.1 invocation as a `<baseline_recon_findings>` context block — MUST NOT be re-summarized by a model first, to avoid hallucinating detail into a deterministic result. | M |
| FR-BASELINE-05 | If any individual tool fails or times out, log it and continue — a partial baseline is still handed to the Strategist with the specific gap noted, never blocking Phase 2/Phase 4.1 on one slow/failed tool. A whole wave delayed past a fixed ceiling (default: the Targeted-Scans 900s tier) proceeds with whatever completed, rather than blocking Phase 2 indefinitely. | M |
| FR-BASELINE-06 | **Tool roster, by wave and condition.** Conditional waves/tools only run when their trigger condition is met for this target — skipped, not run-and-discarded, when not applicable (see table below). | M |
| FR-BASELINE-07 | `sublert`'s technique (continuous CT-log monitoring for new subdomains over time) additionally runs on `FR-MONITOR-01`'s schedule, since that's the correct home for a *continuous* check — it is also included in Wave 1 below for its one-shot value. Per operator direction, overlapping-purpose tools are welcomed rather than trimmed: every tool in the arsenal that can run against a domain/IP/repo input is included in the pipeline it fits, even where another tool already covers similar ground. `maigret`/`pywhat` are the only two kept out of the fixed wave table — not a redundancy trim, but an input-shape mismatch (they take a username/arbitrary string, not a domain/IP, so a blind per-target pipeline has nothing to feed them); both remain registered, AI-selectable Tier 2 tools for the Scripter to reach for on a matching task. | M |

**FR-BASELINE-06's tool roster:**

| Wave | Condition | Tools |
|---|---|---|
| 1 (parallel) | Always (`NETWORK` targets) | `subfinder`, `amass`, `assetfinder`, `bbot`, `theHarvester`, `knockpy`, `sublert` (subdomain/OSINT enumeration — all included together, per operator direction not to trim for overlap) · `dnsrecon`, `massdns`, `puredns`, `shuffledns` (DNS resolution/brute-force, all four) · `naabu` (fast async port sweep) |
| 1 (parallel) | `CODE_REPO` target, or a repo discovered/in scope | `trufflehog`, `noseyparker`, `gitleaks`, `shhgit`, `git-hound` (secrets scanning) · `semgrep` (SAST) |
| 1 (parallel) | Cloud-provider indicator present (S3 bucket pattern, cloud ASN) | `s3scanner`, `cloud_enum`, `cloudfail`, `scoutsuite` |
| 1 (parallel) | `MOBILE_BINARY` target | `apkleaks`, `jadx` (static mobile recon) |
| 2 (parallel, needs Wave 1) | Always | `httpx`, `dnsx` (live-host probing) · `nmap -sV` (targeted deep scan, ports from Wave 1's `naabu` only) · `dnsreaper`, `subjack` (subdomain takeover check) |
| 3 (parallel, needs Wave 2) | Always | `whatweb` + `httpx -tech-detect` (tech fingerprinting → `discovered_entities.entity_type = 'tech_fingerprint'`, feeds `FR-TOOL-18`) · `katana`, `gau`, `waybackurls`, `waymore`, `hakrawler`, `gospider`, `cariddi` (crawling/URL discovery — full set, `cariddi` additionally does inline secret/endpoint pattern-matching the others don't) · `ffuf`, `feroxbuster`, `gobuster` (content/directory fuzzing) · `nuclei` (baseline-template scan) · `aquatone`, `eyewitness` (visual/screenshot triage of live hosts) · `byp4xx`, `whatwaf`, `unwaf` (WAF detection/bypass probing) · `log4j-scan` |
| 4 (needs Wave 3's crawl/fuzz output) | Always | `arjun`, `x8` (parameter discovery — fed via `gf`/`qsreplace`/`anew` piping Wave 3's crawl output) |
| 4 (needs Wave 3) | A GraphQL endpoint surfaced during crawling | `graphw00f`, `clairvoyance`, `graphql-cop` |
| 4 (needs Wave 3) | A JWT surfaced during crawling/parameter discovery | `jwt_tool` |

*(Not in this pipeline at all — genuinely exploit-class, stay AI-gated in the normal
Phase 4.2 loop, never run unattended without Gate 1/Gate 2/Adjudicator review:
`sqlmap`, `dalfox`, `xsstrike`, `ghauri`, `fuxploider`, `hashcat`, `cewler`, `cupp`,
`trevorspray`, `kerbrute`, `interactsh-client`, `mobsf`, `objection` — formally
registered as Tier 1 tools per `FR-TOOL-20`/`19:FR-MOBILE-08` (decision log #77); still
never invoked by this pipeline.)*

---

## FR-COUNCIL — Phase 4: State-Driven Council Execution

### 4.1 Strategic Planning & Strategy Audit

Council Gate 1 is two-tier: Tier 0 (deterministic, every task — the *only* component
that mechanically checks tasks against `scope_rules`) + Tier 1 (the **Strategy
Auditor** — `Hermes-3-Llama-3.1-8B`). The Strategy Auditor never evaluates scope
itself; its only job is judging whether the Lead Strategist's proposed plan
*addresses* the Human-Operator-defined scope, whether the plan is sound, and whether
it makes sense — see `05:SEC-SCOPE-01` for the authoritative statement of this
division of labor.

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-COUNCIL-01 | `DeepSeek-R1-0528-Qwen3-8B` (Lead Strategist) ingests scope/IP-ranges/RoE and produces an ordered, hypothesis-driven task queue. | M |
| FR-COUNCIL-02 | Lead Strategist output is a structured, parseable plan (`attack_paths`/`task_queue`), not free-form prose. | M |
| FR-COUNCIL-03 | Lead Strategist fully unloads before the Strategy Auditor loads (single-residency, FR-GATE-02). | M |
| FR-COUNCIL-03a | Deterministic Tier 0 scope checker validates autonomous tasks against configured operational target boundaries to guide autonomous crawling. For HUMAN_OPERATOR-origin tasks, Tier 0 scope checks stand down completely: Human Operator instructions execute unconditionally without boundary interception. | M |
| FR-COUNCIL-04 | The Strategy Auditor (Tier 1, `Hermes-3-Llama-3.1-8B`) evaluates whether the Lead Strategist's proposed task addresses the configured scope, is non-destructively sound, and makes sense — exclusively for AUTONOMOUS_COUNCIL-origin tasks. It never itself decides what is in/out of scope (that is Tier 0's mechanical job, per FR-COUNCIL-03a). It is completely bypassed for any HUMAN_OPERATOR-origin task, ensuring the model never refuses, alters, or intercepts the Human Operator's direct instructions. | M |
| FR-COUNCIL-05 | Both tiers' decisions and rationale are persisted per task; an AUTONOMOUS_COUNCIL task logs both gate outcomes, while a HUMAN_OPERATOR task's rationale records direct Human Operator dispatch with automated scope gates bypassed. | M |
| FR-COUNCIL-06 | In Autonomous Mode, a task failing non-destructive or operational validation is rejected and logged without stopping the pipeline. In Human-Operator-Directed Mode, manual tasks bypass Tier 0 and Tier 1 gates entirely and dispatch directly to Phase 4.2 execution without refusal. | M |

### 4.2 Tool Execution & Exploitation — Dual-Scripter Batch-Sequential Loop

Phase 4.2 is split into two strictly sequential sub-phases, never concurrent (single
residency, `FR-GATE-02`, holds throughout): **4.2A** — the **Primary Scripter**
(`Qwen2.5-Coder-7B-Instruct`) runs the baseline task queue across every target; then,
after a full unload and memory-settle, **4.2B** — the **Secondary Scripter**
(`DeepSeek-Coder-6.7B-Instruct`) runs a second, orthogonal pass across every target,
explicitly excluding whatever the Primary Scripter already tried. Gate 2 is deterministic
code throughout both sub-phases — no LLM linter is invoked for syntax checking; that
job is now Gate 2's Tier 2A (`FR-COUNCIL-08`).

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-COUNCIL-07 | The Primary Scripter loads once at Phase 4.2A start, stays resident for the whole per-target loop across every target; its per-task context includes current opt-in-flag state (waste-avoidance only — enforcement is at FR-TOOL-06a regardless). | M |
| FR-COUNCIL-08 | Gate 2 performs three deterministic sub-checks, in sequence, with zero LLM involvement at any tier: **Tier 2A** (syntax/AST validity — `ast.parse()`/`py_compile` for Python, `bash -n <path>` for Bash; applies only to `script_runner` submissions) → **Tier 2B** (tool CLI flag/argument schema validation — the original Gate 2 check) → **Tier 2C** (orthogonal-vector deduplication — rejects a command whose `param_vector_hash` already exists in `scripter_execution_ledger` for that task, `REJECTED_DUPLICATE_SCRIPTER_VECTOR`). In Autonomous Mode, Tier 2B enforces non-destructive boundaries (blocking SQL data mutations like UPDATE/DELETE/DROP and system-level wipes). In Human-Operator-Directed Mode, Tier 2B validates syntax format only and does not restrict or reject Human-Operator-approved commands or payloads; Tier 2A/2C still apply (a Human-Operator-submitted script still must parse, and duplicate-vector rejection is a waste-avoidance check, not a safety gate — Tier 2C stands down for Human-Operator-directed re-tests, since a deliberate repeat may be exactly what's being verified). | M |
| FR-COUNCIL-09 | On any Gate 2 tier's rejection, the active scripter (Primary in 4.2A, Secondary in 4.2B) regenerates up to 3 attempts; beyond that, the task is `BLOCKED` with the specific tier and rejection reason — never dropped or force-executed. | M |
| FR-COUNCIL-10 | The resident scripter (whichever is active — Primary in 4.2A, Secondary in 4.2B) evaluates output and appends any follow-on task to `task_queue` — never acts outside the queue. | M |
| FR-COUNCIL-10a | A follow-on signal belonging to a different domain (`target_type`) is queued against that domain's own requirement set, not force-fit into the current task's domain. | S |
| FR-COUNCIL-11 | Task-queue loop bound, applied independently within each of 4.2A and 4.2B: 30-task-per-target baseline cap (CAPPED), 3-consecutive-zero-yield circuit breaker (CIRCUIT_BROKEN). In Autonomous Mode, reaching limits triggers an auto-pivot to the next target within the same sub-phase, or (if the last target) transition to the next sub-phase/Phase 4.3. In Human-Operator-Directed Mode, task caps stand down or dynamically adjust to Human Operator demands. | M |
| FR-COUNCIL-11a | "Zero-yield" = no new discovered_entities row, preventing unattended execution from spinning on repetitive output. Two class-aware counters (STANDARD threshold 3, HIGH_ATTEMPT threshold 15 default) guide autonomous progression, tracked independently per sub-phase (a target's 4.2A counter does not carry into its 4.2B pass — a fresh, orthogonal attempt deserves a fresh counter). Counters apply to autonomous task cycling and do not restrict explicit Human-Operator-dispatched actions. | M |
| FR-COUNCIL-11b | Failure-based circuit breaker: 3 consecutive network-error/timeout runs marks a target UNREACHABLE during autonomous crawling, pivoting resources to viable targets. A target marked UNREACHABLE during 4.2A carries that status into 4.2B — the Secondary Scripter does not retry a target the Primary Scripter already confirmed unreachable, unless a Human Operator directive explicitly re-targets it (either sub-phase). | M |
| FR-COUNCIL-11c | The **12-hour default session budget** spans Phase 4.2 as a whole (4.2A + 4.2B combined) — it is not doubled for the second sub-phase. If the budget is exhausted during 4.2A, 4.2B is skipped entirely for that engagement (logged, not treated as a failure) and the pipeline proceeds directly to Phase 4.3. | M |
| FR-COUNCIL-11d | **Batch-sequential handoff**: when 4.2A's task queue reaches exhaustion, its per-target cap, or a circuit-breaker auto-pivot, for every target — the Primary Scripter fully unloads (`FR-GATE-09`, OS-level exit confirmed) and the memory-settle gate (`FR-GATE-10`) clears before the Secondary Scripter loads. The Secondary Scripter's context for each target includes the active hypothesis, target state, and an exclusion block of every parameter/endpoint/tool-hash the Primary Scripter already executed against that target (from `scripter_execution_ledger`), framed as negative constraints — it MUST NOT re-propose any of them (enforced deterministically by Gate 2 Tier 2C, not by the model's own restraint alone). | M |
| FR-COUNCIL-12 | The Primary Scripter unloads only when Phase 4.2A ends for the whole engagement (every target reaches terminal/cap for its primary pass, or the session budget is hit first) — never per-task/per-target. The Secondary Scripter, analogously, loads once for the whole engagement's 4.2B pass and unloads only when 4.2B ends for the whole engagement (or the shared session budget runs out, `FR-COUNCIL-11c`) — never per-task/per-target. | M |

### 4.3 Evidence Adjudication & Reporting

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-COUNCIL-13 | `Mistral-7B-Instruct-v0.3` (Criterion Adjudicator, Gate 3) evaluates candidate findings against raw evidence, recording `CONFIRMED, DISMISSED, or INFO` with contextual rationale. | M |
| FR-COUNCIL-14 | Criterion Adjudicator evaluates candidate findings against common false-positive patterns (WAF blocks, rate-limit responses, generic 5xx, honeypots) to maintain signal quality. Findings flagged with anomalies may still be marked for review or promoted via Human Operator instruction. | M |
| FR-COUNCIL-14a | Adjudication evaluates verified impact, proper vulnerability categorization (e.g., distinguishing unauthenticated endpoints from IDOR/BOLA), and baseline-versus-probe response differences. Human Operator directives can override classification flags to preserve exploratory observations. | M |
| FR-COUNCIL-15 | Confirmed findings populate the primary VAPT_FINDING register. Non-confirmed, informational, or remediated observations are routed to the consolidated INFO_REGISTER or retained as auxiliary artifacts based on Human Operator reporting preferences. | M |
| FR-COUNCIL-16 | `Ministral-8B-Instruct-2410` (Executive Reporter, a distinct model from the Lead Strategist) ingests confirmed findings, produces CWE/CVE mapping, root-cause narrative, remediation. | M |
| FR-COUNCIL-16a | The model proposes CVSS 3.1 metric vectors; a deterministic calculator computes final base scores. The Human Operator may override any vector component directly during report review. | M |
| FR-COUNCIL-17 | Two distinct document types, never conflated: (a) one `VAPT_FINDING` report per `CONFIRMED` finding; (b) one consolidated `INFO_REGISTER` per engagement, regenerated in place. Both emit as Markdown to `pending-approval/` first. A `REGRESSION_CHECK`-origin finding still gets its own report, marked carried-forward. | M |
| FR-COUNCIL-17a | Rendered HTML/PDF exports are produced upon Human Operator command (approve-report or explicit CLI export), ensuring the Human Operator controls final report delivery. | M |
| FR-COUNCIL-17b | Grounding verification validates that URLs, endpoints, and parameters cited in finding drafts match observed raw tool evidence. Flagged discrepancies are highlighted for Human Operator review rather than silently dropped. | M |
| FR-COUNCIL-18 | Secrets are redacted by default from raw evidence presented to the Executive Reporter model via a reversible redaction_map. Redacted secrets are restored upon report finalization, with raw values remaining intact in the secure local artifact store. | M |

---

## FR-HIB — Phase 5: Hibernation & Restoration

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-HIB-01 | Mark engagement state `COMPLETE`/`PAUSED` before teardown begins. | M |
| FR-HIB-02 | Evict all resident weights/KV caches; verify freed memory before application restoration. | M |
| FR-HIB-03 | `SIGCONT` every suspended PID (FR-ENV-05); verify each resumed (not zombie/dead), never assume success. | M |
| FR-HIB-04 | A missing previously-suspended process is logged as a discrepancy, not a whole-restoration failure. | M |
| FR-HIB-05 | SHOULD report restoration completion time; sub-2-second expectation for paged-out memory. | S |

---

## FR-CTRL — Human Operator Control Surface

CLI-only (no GUI/web dashboard). Every action below is reachable as a `vaptctl`
subcommand.

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-CTRL-01 | `start` accepts a target scope (IP ranges/domains). Legal authorization, permissions, and rules of engagement (RoE) are strictly the Human Operator's responsibility outside the tool. Operational scope limits guide autonomous scanning only and do not restrict Human-Operator-directed commands. | M |
| FR-CTRL-01a | `start` MUST also accept an optional free-text guidance block (`--notes "<text>"`), persisted verbatim to the new `engagements.human_operator_notes` column (`03:DR-SCHEMA-01`) and surfaced to the Lead Strategist's first Phase 4.1 invocation under a clearly labeled `HUMAN OPERATOR GUIDANCE` context section, distinct from target scope data. Capped at 500 characters (matching `FR-INTERVENE-08`'s existing intervention-text bound); text exceeding the cap is rejected at the CLI with a specific error, letting the Human Operator shorten and retry, rather than silently truncated. No file-based (`--notes-file`) variant — small models in this council cannot usefully consume long documents, so only the bounded inline form is offered. | M |
| FR-CTRL-02 | `pause` halts task-queue progression at the next safe checkpoint (not mid-subprocess) without losing state. | M |
| FR-CTRL-03 | `resume` continues a `PAUSED` engagement from last-committed state; accepts optional updates to the three high-risk flags (FR-TOOL-06c). | M |
| FR-CTRL-04 | `abort` immediately terminates all subprocess trees, unloads any resident model, marks the engagement ABORTED, within 20 seconds. | M |
| FR-CTRL-05 | `status` shows: phase, resident model, RAM/swap headroom, queue depth, finding counts by state. | M |
| FR-CTRL-06 | Mode configuration supports distinct operating postures: Autonomous Non-Destructive Mode (strictly enforcing read/safe-write boundaries and prohibiting data destruction/DoS) and Human-Operator-Directed Mode (unconditional, unrestricted execution of Human Operator commands with zero refusal). | — |
| FR-CTRL-07 | Export the final report and full audit trail as a single offline-review package. | M |
| FR-CTRL-08 | `approve-report` serves as the primary trigger for (a) verifying or finalizing evidence unredaction and (b) generating rendered HTML/PDF deliverables (FR-COUNCIL-17a). Direct CLI export flags are also supported for rapid ad-hoc generation. | M |
| FR-CTRL-09 | System-wide single-engagement lock: `start` refuses if any engagement is `IN_PROGRESS`/`PAUSED` — enforced at both application and schema level via a dedicated `engagement_lock_slot`. | M |

---

## FR-CHECKPOINT — Human Checkpoint Gate

Operational sensitivity classification tracks tasks against a fixed, closed list of
six action classes. In Autonomous Mode, tasks matching these classes log checkpoint
audit events for Human Operator visibility. In Human-Operator-Directed Mode, commands
dispatched or directed by the Human Operator execute immediately without interactive
pausing.

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-CHECKPOINT-01 | Fixed, closed list of six classes: ANTI_FORENSICS, LIVE_CREDENTIAL_SPRAY, CICD_EXTERNAL_ARTIFACT, DEPENDENCY_CONFUSION_PUBLISH, PHISHING_MFA_BYPASS, ACTIVE_WIRELESS_DISRUPTION (`FR-DISCOVER-04`). MUST NOT be silently extended without a recorded decision. | M |
| FR-CHECKPOINT-02 | High-impact operational classes (credential spraying, lateral movement, artifact publishing) utilize runtime flags for autonomous execution. Any checkpoint class directly commanded or invoked by the Human Operator requires no additional opt-in flags and executes immediately. | M |
| FR-CHECKPOINT-03 | When a sensitive action is autonomously proposed, it logs a pending checkpoint event for Human Operator visibility. However, any action directly dispatched or triggered by the Human Operator executes immediately (approved_via = 'HUMAN_OPERATOR_DIRECTIVE') without pausing the engine or blocking on human approval gates. | M |
| FR-CHECKPOINT-04 | `approve-checkpoint`/`deny-checkpoint` act on exactly one flagged task; neither requires restarting the engagement. | M |
| FR-CHECKPOINT-05 | Pre-flight disclosure and white-cell attestation flags are optional Human-Operator-managed tracking parameters. Their absence does not hard-abort start or prevent Human-Operator-directed task execution. | M |
| FR-CHECKPOINT-06 | Credential spraying and brute-force tasks run within configurable lockout estimation limits during autonomous discovery. Human-Operator-directed credential operations run with zero automated gating, executing exactly per the parameters provided by the Human Operator. | M |

---

## FR-MONITOR — Scheduled Monitoring Mode

External cron/systemd-timer triggers a lightweight, discovery-only invocation — the
system never self-schedules or runs continuously in the background.

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-MONITOR-01 | `monitor <engagement_id>` performs a fixed recon-diff subset against registered targets, compares to a stored `monitoring_baseline`, logs any diff to `discovered_entities`. Continuous subdomain/CT-log watching (`sublert`'s technique — new subdomains appearing over time, not a one-shot baseline) belongs here, invoked on the same external cron/systemd-timer schedule as any other monitoring subset — explicitly not part of `FR-BASELINE`'s one-shot pipeline (`FR-BASELINE-07`). | M |
| FR-MONITOR-02 | Changes are logged by default; --monitor-auto-scan queues targeted non-destructive discovery tasks into Phase 4.2. | M |
| FR-MONITOR-03 | Scheduled monitoring performs deterministic baseline recon without requiring resident model inference or full council startup. | M |
| FR-MONITOR-04 | Does not create an `engagements` row and does not participate in FR-CTRL-09's lock — may run against any engagement status, including concurrently with an active one. | M |

---

## Authority & Conflict Resolution

This functional specification defines pipeline mechanics and state progression. In the
event of any discrepancy, ambiguity, or conflict regarding containment boundaries,
authorization assumptions, scope enforcement, or Human Operator override precedence, the
**Security, Safety & Compliance Requirements (`05`)** serves as the supreme, binding
authority across the entire system.
