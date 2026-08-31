# Functional Requirements — Autonomous Agentic VAPT System

Priority key (MoSCoW): **M** = Must have, **S** = Should have, **C** = Could have.
Each requirement is traceable to a phase in the base architecture document
(`Agentic VAPT Setup (HOME).md`, §3) and to a verification method in
`09-Acceptance-Criteria-and-Test-Plan.md`.

---

## FR-PRE — Phase 0: Pre-Flight Self-Test (new; not in base document)

The base document begins execution at "Phase 1: Environment & Memory Prep" and assumes
every dependency already works. A pre-flight phase is required so failures surface
before memory is committed or a target is touched.

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-PRE-01 | The system MUST verify the inference engine (`llama.cpp`/`ollama`) is installed, its version recorded, and its process is not already running before Phase 1 starts. | M |
| FR-PRE-02 | The system MUST verify the Intel Level Zero / SYCL / OpenCL runtime is present and can enumerate the Arc iGPU before committing to GPU-offloaded inference; on failure it MUST fall back to a documented CPU-only inference mode rather than fail silently. | M |
| FR-PRE-03 | The system MUST verify each of the 5 council model files exists at its expected path and quantization, with a checksum or file-size sanity check, before Phase 4 is entered. | M |
| FR-PRE-04 | The system MUST verify presence of every Tier 1 wrapped tool binary (`nmap`, `masscan`, `nuclei`, `ffuf`, `feroxbuster`, `gobuster`, `sqlmap`, `nikto`, `whatweb`, `wafw00f`, `testssl`) and record installed version strings to the state store. | M |
| FR-PRE-05 | The system MUST verify the NVMe artifact path (`/home/mhj/.local/share/vapt_agent/artifacts/`) exists, is writable, and is not itself a `tmpfs` mount. | M |
| FR-PRE-06 | The system MUST record current available RAM, swap utilization, and disk free space as a pre-flight baseline snapshot in the state database before Phase 1 hibernation actions begin. | M |
| FR-PRE-07 | Pre-flight MUST produce a single pass/fail report; any failed check MUST block progression to Phase 1 unless the operator explicitly overrides with a logged justification. | M |

---

## FR-ENV — Phase 1: Environment, Storage & Memory Preparation

Traces to base §Phase 1.

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-ENV-01 | The system MUST redirect all agent-generated artifacts, logs, temp scripts, and cache/vector-store files to the designated NVMe path and MUST NOT write working data to `tmpfs`-backed `/tmp`. | M |
| FR-ENV-02 | The system MUST set `TMPDIR`/`TEMP`/`TMP` for its own process tree (and any subprocess it spawns) to the NVMe artifact path. | M |
| FR-ENV-03 | The system MUST enumerate active user-session GUI processes and classify each as "hibernation-eligible" or "protected" against an explicit denylist (`systemd`, `dbus`, `Xorg`/`Wayland` compositor, session manager, audio server) before issuing any signal. | M |
| FR-ENV-04 | The system MUST NOT send `SIGSTOP` to any process holding an open file lock on unsaved user document state unless the operator has confirmed hibernation is safe (see FR-ENV-06). | M |
| FR-ENV-05 | The system MUST record the full PID list and process tree of every application it suspends, in a form sufficient to reverse the action deterministically in Phase 5. | M |
| FR-ENV-06 | Before issuing the first `SIGSTOP`, the system MUST present the operator with the list of applications to be suspended and require explicit confirmation (default: interactive prompt; MAY be pre-authorized via a signed engagement config for unattended runs). | M |
| FR-ENV-07 | The system SHOULD trigger kernel-level memory reclamation (`process_madvise(MADV_PAGEOUT)` or cgroup memory limits) on suspended PIDs to accelerate the RAM headroom gain, but MUST NOT do so on any protected process. | S |
| FR-ENV-08 | The system MUST re-measure available RAM after hibernation and MUST abort progression to Phase 2 if the resulting headroom is below the minimum required for the smallest council model (~3.8 GB) plus a safety margin (see NFR-RES-02). | M |
| FR-ENV-09 | The system MUST initialize the SQLite state store with, at minimum, the tables `targets`, `scope_rules`, `rules_of_engagement`, `attack_paths`, `task_queue`, `tool_execution_logs`, `verified_vulnerabilities`, `model_invocation_logs`, and `engagement_state` (full schema in `03-Data-and-Storage-Requirements.md`) before Phase 2 begins. | M |
| FR-ENV-10 | If the state database already exists with an engagement marked `IN_PROGRESS` or `PAUSED`, the system MUST offer to resume that engagement rather than silently overwrite it. | M |

---

## FR-GATE — Phase 2: Local Inference Gateway

Traces to base §Phase 2.

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-GATE-01 | The system MUST expose a single local, loopback-only OpenAI-compatible endpoint (`127.0.0.1:11434/v1`) for chat completions and embeddings; it MUST NOT bind to a non-loopback interface by default. | M |
| FR-GATE-02 | The system MUST enforce a hard single-model-residency policy: at most one council model may hold weights in RAM/VRAM at any instant. A request to load a second model MUST first fully unload the resident one and confirm the unload before proceeding. | M |
| FR-GATE-03 | The system MUST pin inference compute threads to the 4 Performance-Core / 8-thread group (`-t 8`) and MUST leave Efficient Cores free for subprocess/tool execution and I/O. | M |
| FR-GATE-04 | The system MUST attempt GPU offload via the Level Zero/SYCL backend to the Arc iGPU and MUST fall back to CPU-only inference (logged as a degraded-mode event) if the backend is unavailable, rather than fail the engagement. | M |
| FR-GATE-05 | The system MUST tear down (evict weights + KV cache) each model within a bounded time window after its phase step completes (`keep_alive: 0` or equivalent), and MUST verify the eviction actually freed memory before declaring the phase step complete. | M |
| FR-GATE-06 | The system MUST log every inference call (model, role, prompt token count, completion token count, wall-clock latency, phase/step ID) to `model_invocation_logs`. | M |
| FR-GATE-07 | The system MUST enforce per-model context window ceilings matching each model's documented profile (8k for DeepSeek-R1/Hermes-3/Mistral-7B, 16k for Qwen2.5-Coder-7B, 4k for Qwen2.5-Coder-3B) and MUST truncate/summarize inputs rather than silently error on overflow. | M |
| FR-GATE-08 | If the inference engine process crashes or becomes unresponsive (no token progress within a configurable timeout), the system MUST detect this, log it, attempt one restart, and escalate to a halted/`PAUSED` engagement state on repeated failure rather than hang indefinitely. | M |

---

## FR-TOOL — Phase 3: Security Framework & Kali Tool Bridge

Traces to base §Phase 3.

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-TOOL-01 | The system MUST provide structured, schema-validated function-calling wrappers ("Tier 1") for each of: `nmap`, `masscan`, `nuclei`, `ffuf`, `feroxbuster`, `gobuster`, `sqlmap`, `nikto`, `whatweb`, `wafw00f`, `testssl`. | M |
| FR-TOOL-02 | Each Tier 1 wrapper MUST declare, in machine-readable form, its allowed flags, required arguments, and forbidden flag combinations (e.g., destructive `sqlmap --os-shell`) so the linter (FR-COUNCIL) can validate against it. | M |
| FR-TOOL-03 | The system MUST provide a generic Tier 2 dynamic bridge (`run_security_command`) for any other installed `/usr/bin`/`/usr/sbin` binary, gated by an explicit allowlist-by-default policy (see FR-TOOL-06). | M |
| FR-TOOL-04 | All external tool invocation MUST use non-shell subprocess execution (`shell=False`) with explicit argument vectors; string-interpolated shell commands MUST NOT be constructed from model output. | M |
| FR-TOOL-05 | Every subprocess invocation MUST have a mandatory timeout (default 180s, configurable per-tool) after which the process tree is terminated. | M |
| FR-TOOL-06 | The Tier 2 dynamic bridge MUST check every candidate binary/argument set against a configurable denylist of destructive operations (e.g., `rm`, `dd`, `mkfs`, fork-bombs, disk-wiping utilities, anything targeting `127.0.0.1`/loopback/host-local addresses outside the declared scope) before execution, and MUST refuse execution on a match. | M |
| FR-TOOL-07 | The system MUST sanitize raw stdout/stderr from every tool run through a parsing pipeline that extracts structured signal (open ports, banners, URLs, status codes) and discards HTML bodies, repetitive 404 noise, and binary payloads before the data enters any model's context window. | M |
| FR-TOOL-08 | The system MUST persist the full, unsanitized raw output of every tool run to the NVMe artifact store regardless of what is summarized into context, so evidence is not lost to summarization. | M |
| FR-TOOL-09 | The system MUST record, for every subprocess execution, the exact argument vector, start/end timestamps, exit code, and originating task ID in `tool_execution_logs`. | M |
| FR-TOOL-10 | The system SHOULD extract and expose Burp Suite / Caido MCP server configurations and structured multi-turn assessment prompt templates as reusable methodology assets, without requiring them to be installed at planning time. | S |
| FR-TOOL-11 | The system MUST support pointing `claude-bug-bounty`, `CyberStrike`, and `strix` at the local endpoint via `OPENAI_BASE_URL`/`OPENAI_API_KEY`/`ANTHROPIC_BASE_URL` environment overrides, without hardcoding cloud endpoints anywhere in the bridge. | S |

---

## FR-COUNCIL — Phase 4: State-Driven Council Execution

Traces to base §Phase 4, Steps 4.1–4.3, and §2 model profiles.

### 4.1 Strategic Planning & Scope Gate

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-COUNCIL-01 | `DeepSeek-R1-Distill-Qwen-8B` MUST be loaded to ingest target scope, IP ranges, and Rules of Engagement from the state store and produce an ordered, hypothesis-driven attack-path task queue. | M |
| FR-COUNCIL-02 | The Strategist's output MUST be a structured, parseable plan (task list with rationale) written to `attack_paths`/`task_queue`, not free-form prose only. | M |
| FR-COUNCIL-03 | The Strategist model MUST be fully unloaded from RAM before the Gatekeeper model loads (single-residency, FR-GATE-02). | M |
| FR-COUNCIL-04 | `Hermes-3-Llama-3.1-8B` (Council Gate 1) MUST evaluate every proposed task against the declared scope boundaries (`scope_rules`) and MUST reject or flag-for-revision any task that: targets an address/domain outside scope, exceeds an authorized testing window, or exceeds the authorized intrusiveness level (see `05-Security...`). | M |
| FR-COUNCIL-05 | Council Gate 1 decisions (approve / revise / reject) and its stated rationale MUST be persisted per task, not just a final aggregate verdict. | M |
| FR-COUNCIL-06 | A task that Council Gate 1 rejects MUST NOT reach Phase 4.2 execution under any circumstance, including operator "yolo" override modes — scope rejection is a hard gate, not a soft one. | M |

### 4.2 Tool Execution, Linting & Exploitation

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-COUNCIL-07 | `Qwen2.5-Coder-7B-Instruct` MUST read the next approved task from the queue and formulate a concrete CLI invocation or exploit script consistent with the Tier 1/Tier 2 schemas in FR-TOOL. | M |
| FR-COUNCIL-08 | `Qwen2.5-Coder-3B` (Council Gate 2) MUST validate every generated command's flags/arguments against the tool's declared schema before execution, and MUST return a corrected command or a rejection — never allow an unvalidated command to reach the subprocess bridge. | M |
| FR-COUNCIL-09 | If Gate 2 cannot produce a valid command after a bounded number of correction attempts (default 2), the task MUST be marked `BLOCKED` with the linter's rejection reason, not silently dropped or force-executed. | M |
| FR-COUNCIL-10 | Following execution, `Qwen2.5-Coder-7B` MUST evaluate parsed tool output and decide whether follow-on pivoting/secondary tasks are warranted, appending them to `task_queue` rather than acting outside the queue. | M |
| FR-COUNCIL-11 | The task-queue loop MUST have a bounded iteration/time limit per engagement to prevent unbounded autonomous looping; on reaching the limit the engagement MUST pause for operator review rather than continue indefinitely. | M |
| FR-COUNCIL-12 | The Operator model MUST be fully unloaded after the task queue for the current cycle is resolved or blocked. | M |

### 4.3 Evidence Adjudication & Reporting

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-COUNCIL-13 | `Mistral-7B-Instruct-v0.3` (Council Gate 3) MUST independently assess every candidate finding against its raw evidence (HTTP dumps, headers, status codes, tool exit codes) and mark each `CONFIRMED` or `DISMISSED` with a stated reason. | M |
| FR-COUNCIL-14 | Gate 3 MUST explicitly check for and dismiss common false-positive patterns: WAF block pages, rate-limit responses, generic 5xx errors, and honeypot/canary responses, before a finding can reach `CONFIRMED`. | M |
| FR-COUNCIL-15 | Only `CONFIRMED` findings MUST be eligible for inclusion in the final report; `DISMISSED` findings MUST be retained in the state store for audit purposes but excluded from the report body (an appendix listing dismissed candidates is permitted). | M |
| FR-COUNCIL-16 | `DeepSeek-R1-Distill-Qwen-8B` MUST be reloaded to ingest confirmed findings and produce: CWE/CVE mapping where applicable, a CVSS score (version and vector string) per finding, a root-cause narrative, and remediation guidance. | M |
| FR-COUNCIL-17 | The generated report MUST be emitted in at least one durable, human-readable file format (Markdown at minimum) written to the NVMe artifact path, and MUST include: executive summary, scope statement, methodology, per-finding evidence references (linking to raw artifact files), CVSS, and remediation. | M |
| FR-COUNCIL-18 | The report generation step MUST NOT include raw secrets (passwords, tokens, session cookies) in plaintext in the report body; such values MUST be redacted/truncated with a pointer to the raw evidence file for authorized reviewers. | M |

---

## FR-HIB — Phase 5: Hibernation & Restoration

Traces to base §Phase 5.

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-HIB-01 | The system MUST mark the engagement state as `COMPLETE` or `PAUSED` in the state store before beginning teardown. | M |
| FR-HIB-02 | The system MUST evict all resident model weights and KV caches and verify the resulting freed memory before proceeding to application restoration. | M |
| FR-HIB-03 | The system MUST issue `SIGCONT` to every PID it suspended in Phase 1 (FR-ENV-05), using the recorded PID/process-tree list, and MUST verify each target process resumed (is running, not zombie/dead) rather than assume success. | M |
| FR-HIB-04 | If a previously suspended process no longer exists at restoration time (e.g., it was killed externally while stopped), the system MUST log this discrepancy rather than fail the whole restoration sequence. | M |
| FR-HIB-05 | The system SHOULD report restoration completion time to the operator, with an expectation of sub-2-second resume for previously paged-out application memory. | S |

---

## FR-CTRL — Operator Control Surface (new; not explicit in base document)

The base document describes an end-to-end autonomous loop with no defined human
interaction points beyond the two internal LLM gates. The following requirements add
the missing operator-facing control layer.

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-CTRL-01 | The system MUST provide an operator-invokable **start** action that accepts a target scope definition (IP ranges/domains) to seed the engagement. Per explicit decision, this system does **not** itself gate execution on a separate authorization/Rules-of-Engagement artifact — obtaining and verifying authorization is treated as out of scope for this system and is the operator's responsibility outside the tool. | M |
| FR-CTRL-02 | The system MUST provide an operator-invokable **pause** action that halts task-queue progression at the next safe checkpoint (i.e., not mid-subprocess) without losing state. | M |
| FR-CTRL-03 | The system MUST provide an operator-invokable **resume** action that continues a `PAUSED` engagement from its last committed state. | M |
| FR-CTRL-04 | The system MUST provide an operator-invokable **abort/kill-switch** action that immediately terminates all in-flight subprocess trees, unloads any resident model, and marks the engagement `ABORTED`, within a bounded time (see NFR-REL-04). | M |
| FR-CTRL-05 | The system MUST provide a **status** view showing: current phase, current resident model (if any), RAM/swap headroom, task-queue depth, and count of findings by state (`CANDIDATE`/`CONFIRMED`/`DISMISSED`). | M |
| FR-CTRL-06 | The system MUST support configurable **autonomy levels** (e.g., paranoid / normal / yolo) that gate how much human approval is required before intrusive or exploitation-class tasks execute, consistent with the hard scope gate in FR-COUNCIL-06 which is never bypassable regardless of level. | S |
| FR-CTRL-07 | The system MUST allow the operator to export the final report and the full audit trail (tool logs + model invocation logs + gate decisions) as a single package for offline review. | M |
