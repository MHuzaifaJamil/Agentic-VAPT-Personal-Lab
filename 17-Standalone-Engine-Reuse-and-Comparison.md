# Standalone Engine (`agent.py`/`brain.py`/`engine.py`) — Reuse & Comparison

**Source:** `/home/vscysteam/claude-bug-bounty` — specifically the parts of that repo
**excluded** from the earlier `Actual-Setup/` copy (`16-Actual-Setup-Reuse-and-Integration-Map.md`)
because they weren't Claude-Code-specific. That exclusion criterion is exactly
backwards for this system: a **standalone, Ollama-first, works-without-Claude-Code**
engine turns out to be architecturally closer to what we're building than the
Claude-Code-dependent material already analyzed in `16`.

---

## ⚠️ Safety Notice — Read Before Touching the Source Repo Again

`/home/vscysteam/claude-bug-bounty` contains, alongside its generic tooling, **real,
live engagement data**:

- `hunt-memory/` — real session/audit JSONL files, real target hostnames (including
  NASA subdomains: `nasa.gov`, `nsc.nasa.gov`, `earthdata.nasa.gov`, and others:
  `usgeo.gov`, `globe.gov`, `travin.ai`).
- `findings/` — real per-client engagement directories (`myco.io`, `buypass.ai`,
  `baitussalam.org`, `travin.ai`), including dozens of `gen_*.py` **report-generator
  scripts that embed the actual client vulnerability content as inline Python
  source** (verified: `gen_VST081.py` alone references "buypass" 20 times) — these
  are real client data in `.py` form, not generic tooling, despite the file
  extension.
- `recon/` — real per-client recon output (`baitussalam.org`, `buypass.ai`,
  `expense.myco.io`, and others).
- `target_config.yaml` — a live-looking Bearer JWT and a live-looking target
  URL/IP embedded in an LLM red-team (`garak`) config.
- `.claude/settings.local.json` — **(found during a follow-up MCP-config check, not
  the original pass)** a permission allowlist containing real attack commands run
  against a real client (`myco.io`) — actual URLs, actual SSRF/open-redirect
  payloads. `.claude/` was never copied to this project (confirmed: `Actual-Setup/`
  contains no `.claude/` directory at all).
- `.playwright-mcp/` — a runtime cache of timestamped page snapshots and console
  logs from actual past browsing sessions, not a configuration file. Never copied.

**None of this was copied, and none of it should be**, regardless of what else gets
adopted from this repo. This was flagged during the research pass and confirmed
explicitly by the operator. `reports/{arsenal,poc_portfolio,portfolio}/gen_*.py` were
individually verified clean (only generic placeholder URLs like `target.com`,
one aesthetic-comparison comment naming `myco.io` with no data attached) before being
copied — every other file from this repo that was copied was verified the same way,
not assumed safe by association.

---

## 1. What Was Copied, and Why

Into `Standalone-Engine-Reference/` in this project:

| File(s) | Why |
|---|---|
| `agent.py`, `brain.py`, `engine.py` | The standalone engine itself — reference material for comparison against our own architecture, not code to run or import as-is (see §2 for why not). |
| `requirements.txt` | Confirms the real dependency floor: `requests>=2.31.0`, `pytest>=8.0.0` — everything else (`ollama`, `langgraph`, `langchain-ollama`, `anthropic`) is verified optional (`try/except ImportError` at every import site checked). |
| `config.example.json` | Verified safe — placeholder strings only (`YOUR_PROJECTDISCOVERY_CHAOS_API_KEY`, etc.), not `target_config.yaml`. |
| `AGENTS.md`, `OPENCODE.md` | Document this repo's multi-harness portability (Claude Code, OpenCode, Pi Agent, Codex-style, generic `.agents/skills`) — context for why parts of it were never Claude-Code-locked in the first place. |
| `install.sh`, `install_tools.sh` | Reference only (this project doesn't execute installation) — `install.sh` installs skills/commands/agents per harness; `install_tools.sh` installs external recon/scan binaries. Different jobs, kept distinct. |
| `tests/` (minus `__pycache__`) | A real, mature test suite for the standalone engine specifically (`test_autopilot_guard.py`, `test_agent_time_budget_gate.py`, `test_cookie_redaction.py`, `test_config_file_permissions.py`, etc.) — verified clean of any real hostname before copying. Reference for how to structure our own analogous tests. |
| `wordlists/` | Generic wordlists (`common.txt`, `api-endpoints.txt`, `sensitive-files.txt`, etc.) — no target-specific content. |
| ~~`report-generators/gen_arsenal_report.py`, `gen_poc_portfolio.py`, `gen_portfolio_report.py`~~ | **Removed** (operator decision, a later commit): judged not needed as reference material after all — these were the operator's own tool-inventory/portfolio report generators, not third-party client reports, and had been individually verified to contain only placeholder URLs before the original copy. No longer present in `Standalone-Engine-Reference/`. |
| `docs/TODOS.md` | **(Added in a later follow-up sweep)** A genuine engineering hardening log for the standalone engine, analogous in spirit to this project's own `10`/`11` — verified clean of real target data. Documents the actual provenance of `CircuitBreaker`/`RateLimiter`/`SafeMethodPolicy`/`AutopilotGuard` (all in `memory/audit_log.py`) and confirms the "unsafe HTTP method → require approval" tier (§3 below) is the same mechanism already declined in C-28, not a separate gap. |
| `docs/advanced-techniques.md`, `payloads.md`, `auth-sessions.md`, `TUTORIAL.md`, `smart-contract-audit.md`, `auth.example.json` | **(Added in the "mine everything" follow-up sweep, independently re-verified clean of real client/target data — grepped for all known real hostnames, zero matches)** `advanced-techniques.md` contributed framework-specific attack playbooks (mined into `19`'s `FR-VULNCLASS-05`) and a timing side-channel methodology (`FR-VULNCLASS-04`) not covered anywhere else; `auth-sessions.md` contributed the auth-session-plumbing pattern (mined into `01`'s new `FR-TOOL-15`); `payloads.md` overlaps `security-arsenal` almost entirely (same "not prompt-transferable" verdict) but contributed two new vuln-class names not in `web2-vuln-classes`' 32-class catalog (XS-Leaks, MiniKit/WebView event-spoofing — also `FR-VULNCLASS-04`); `TUTORIAL.md` is a complete, self-contained 6-bug walkthrough against a fictional demo target (all placeholder data, including AWS's own documented example key) — see the `demo/` entry below; `smart-contract-audit.md` is materially redundant with `web3/01-foundation.md` (kept for completeness, not because it adds anything). |
| `demo/app.py`, `README.md` | **(Added in the same sweep)** A complete, working, zero-dependency Flask app with 6 planted bugs (reflected XSS, open redirect, SSRF, `.env` secrets leak, unauthed admin, debug info disclosure), paired with `TUTORIAL.md` above — stronger evidence for this as a viable *supplementary* lightweight test-lab component than an earlier pass gave it credit for. Does **not** replace the confirmed Docker/Juice-Shop/DVWA test lab (decision #53, `AC-ASSUME-06`) — flagged as an option worth considering alongside it, not a substitute, since that was already an explicit operator decision. |
| `hooks/hooks.json`, `README.md` | **(Added in the same sweep)** Three Claude Code lifecycle hooks (`SessionStart`/`SessionStop`/`Stop`), each just a printed reminder string ("check scope first," etc.) — **no enforcement logic at all**. Kept for completeness/comparison only: this actually reinforces, rather than challenges, this project's own design — the deterministic Tier 0 scope checker (`FR-COUNCIL-03a`) is a meaningfully stronger mechanism than a printed reminder at session boundaries. |
| `LICENSE`, `TERMS.md`, `serve.py`, `pytest.ini`, `uninstall.sh`, `uninstall_tools.sh` | **(Added in a final completeness sweep, all confirmed trivial/safe)** `LICENSE` is MIT (`Copyright (c) 2026 Claude Bug Bounty Hunter Contributors`) — retained per MIT's attribution requirement, given how much of this repo has been copied into this project. `TERMS.md` is the source project's own ethical-use terms — directly corroborates this project's own design; see `21-Safety-Ethics-and-Misuse-Prevention-Control-Inventory.md`'s new cross-reference. `serve.py` is a thin, "recording-friendly" launcher wrapper for `demo/app.py` (already copied) — no new content. `pytest.ini`/`uninstall.sh`/`uninstall_tools.sh` are trivial companions to files already copied (`tests/`, `install.sh`/`install_tools.sh`) — copied for completeness only. |

Deliberately not copied: `.github/` (issue templates, PR template, code of conduct, `SECURITY.md`) — reviewed directly; this is the *source repo's own* GitHub-project governance boilerplate, not reference material relevant to this project's own specification. `site/index.html` — reviewed, a marketing/landing page with no unique technical content beyond what `CLAUDE.md` already describes.

**Note on `memory/` (`audit_log.py`, `rotation.py`, `schemas.py`, `pattern_db.py`, `__init__.py`, `README.md`):** `agent.py` imports `AutopilotGuard`/`CircuitBreaker`/`RateLimiter` from this sibling package, but it was never duplicated into `Standalone-Engine-Reference/` — it did not need to be, because it's **already present, byte-identical, in `Actual-Setup/memory/`** (copied there during the earlier `16` analysis, under a different mirror for an unrelated reason). A follow-up sweep initially flagged this as a missing file/dangling import; re-verified directly and found it isn't — the file exists in this project already, just organized under `Actual-Setup/` rather than duplicated here. Noted here only so a future reader isn't confused about where `AutopilotGuard` actually lives.

Not copied, and not safe to copy: everything under §"Safety Notice" above, plus
`recon/`'s sibling `reports/` output artifacts (the `.pdf`/`.html` files themselves,
as opposed to the three generator scripts named above). (Two newly-found real-data
files, `rules/NASA_VDP_Intel.md` and `rules/VRT_Reference.md`, were also confirmed
excluded during a follow-up sweep — noted in `16`, since `rules/` is that document's
mirror scope, not this one's.)

---

## 2. Why the Engine Itself Isn't Directly Reusable

Despite being architecturally closer to our system than `Actual-Setup/`,
`agent.py`/`brain.py`/`engine.py` embody choices that conflict with decisions already
confirmed for this system:

| Their choice | Our confirmed choice | Conflict |
|---|---|---|
| `brain.py`'s `LLMClient` supports 12 providers, 11 of them cloud (Claude, OpenAI, Grok, Groq, DeepSeek, Gemini, Kimi, Mistral, Together, Cerebras, Perplexity) | Fully local, no cloud API dependency (`NFR-SEC-02`) | Importing `brain.py` means importing 11 code paths this system deliberately excludes. |
| `agent.py` is Ollama-first (LangGraph optional) | `llama.cpp` primary, behind a Local Engine Client (`IR-ENGINE-01..06`, decision #21 resolving finding C-13) | Already-resolved fork, in the other direction — adopting `agent.py` would silently reopen it. |
| `engine.py` is a third, independent CLI/session model | `vaptctl`, per-invocation/SQLite-signal-coordinated (`13-Implementation-Architecture-Bridge.md` IAB-PROC) | Two incompatible CLI/session designs; picking one means not using the other. |
| `BRAIN_SYSTEM`'s prompt instructs "NEVER refuse... NEVER add ethics disclaimers... authorization is already in place" | Council Gate 1's semantic tier (`Hermes-3-Llama-3.1-8B`, decision #55) does avoid blanket safety refusals — same surface similarity to `BRAIN_SYSTEM`'s framing — but for a different, narrower reason: a **non-bypassable deterministic Tier 0 pre-check** (`FR-COUNCIL-03a`), not this prompt, is the system's actual safety boundary, and nothing here instructs the model to ignore ethics or treat authorization as blanket-given the way `BRAIN_SYSTEM` does | Converges on the surface (reduced-refusal tuning) but not the underlying design — this system still has a non-bypassable code-level check `BRAIN_SYSTEM`'s approach never had; not a reason to import `BRAIN_SYSTEM`'s prompt itself, which goes further (instructing the model to suppress ethics considerations entirely). *(This row briefly read the opposite way, when Gate 1 used `Llama-3.1-8B-Instruct` under decision #34 — see `11`'s revised C-03 resolution for the full history.)* |
| CVSS computed by the LLM in prose | Deterministic Python `cvss`-library calculator, LLM proposes metrics only (`FR-COUNCIL-16a`, finding C-07) | Their approach is exactly the unreliable pattern C-07 already rejected — validates our choice, isn't something to adopt from. |

**Conclusion, matching `16`'s own framing:** mine techniques, don't import code.

---

## 3. What Was Actually Mined Into This System (implemented, not just proposed)

Four gaps were found by direct comparison, all confirmed and implemented — see
`11-Critical-Analysis-and-Design-Challenges.md` C-26 through C-29 for the full
rationale on each:

| Finding | What `claude-bug-bounty` has | What we adopted |
|---|---|---|
| **C-26 — Report grounding** | `brain.py`'s `_ground_report_output()`: regex-extracts every URL/path from both the LLM's report output and the source evidence; deletes any report content whose references aren't a subset of the evidence; falls back to an explicit "ungrounded" signal. | `FR-COUNCIL-17b` / `IR-GROUND-01..03`: the same mechanism, wired into our `DRAFT_PENDING_APPROVAL` → `BLOCKED_UNGROUNDED` status transition, with `IR-STRUCTURED-03`'s existing 2-retry/3-attempt pattern reused rather than inventing a new one. |
| **C-27 — Failure circuit breaker** | `CircuitBreaker` class (defined in `memory/audit_log.py`, imported into `agent.py` — not defined in `agent.py` itself, a misattribution corrected here): per-host consecutive-failure counter, threshold 5, 60s cooldown — distinct from information-yield concerns entirely. | `FR-COUNCIL-11b`: a second, independent breaker at 3 consecutive failures (matching our existing zero-yield breaker's count rather than their 5, for internal consistency), marking the target `UNREACHABLE` rather than `CIRCUIT_BROKEN` so the two conditions stay distinguishable in the audit trail. |
| **C-28 — Rate limiting** | `AutopilotGuard` (also defined in `memory/audit_log.py`, imported into `agent.py`) bundles a two-speed `RateLimiter` (`recon_rps=10.0`, `test_rps=1.0`) into its unified `check_request()` gate, checked in a fixed order: scope → circuit breaker → unsafe-method-approval → allow. | `FR-TOOL-14` / `IR-BRIDGE-05`: the same two-speed idea, mapped onto our *existing* categories instead of inventing a new "recon vs. test" taxonomy — 10/s for anything outside the three high-risk opt-in categories (`FR-TOOL-06a`), 1/s for anything inside them. Their "require human approval for unsafe HTTP methods" tier was **not** adopted — it conflicts with this system's confirmed fully-unattended design (`FR-COUNCIL-11`, decision #13); our opt-in-flag system already covers the same underlying concern without a per-request approval step. **Checked, not reopened:** a follow-up sweep of `docs/TODOS.md` (now copied, see §1) found this same tier is formally named `SafeMethodPolicy` there (GET/HEAD/OPTIONS default-safe, PUT/DELETE/PATCH/POST → `require_approval`) — confirmed to be the identical mechanism already evaluated and declined above, not a distinct, previously-unconsidered gap; no new requirement follows from re-reading it under its formal name. |
| **C-29 — Context-window management** | `agent.py`'s docstring claims working memory is "compressed every 5 steps" (`MEMORY_REFRESH_N = 5`), for a 16k+-token ReAct loop. | **Not adopted — genuinely unresolved.** The research pass could not verify the actual LLM-driven rewrite logic behind that constant within what it read. Fabricating a technique to fill this gap would violate this document set's own evidence standard (established across `C-01`-`C-28`: mine verified techniques, don't invent plausible-sounding ones). Logged as Open Item H in `10-Decision-Log-and-Open-Questions.md` — this system has the identical underlying problem (`FR-COUNCIL-07`'s resident Operator across a 30-task loop against `FR-GATE-07`'s 16k ceiling) and no answer for it yet. |

## 4. Additional Observations (not yet turned into requirements — noted for awareness)

- **`brain.py`'s `triage_finding()`** implements its own 7-question gate, independently
  of `skills/triage-validation/SKILL.md`'s 8-question version already mined into our
  `FR-COUNCIL-14a` (`16` §4a). `brain.py`'s version is materially simpler and doesn't
  add anything the skill-file version didn't already cover — no action needed.
- **`AutopilotGuard`'s fixed check order** (scope → circuit breaker → unsafe-method →
  allow, fail-closed with no scope checker configured) is a clean pattern worth
  keeping in mind when actually implementing our own bridge's check sequence
  (`FR-TOOL-03/06/06a-c/14`, `IR-BRIDGE-01..06`) — not a new requirement, since our
  own gate ordering is already implied by the numbering of those requirements, but
  worth an explicit code-review checkpoint at implementation time that the real
  ordering matches: path-allowlist → behavioral-denylist → opt-in-flag-category →
  rate-limit → spawn.
- **`_sanitize_exploit_command()`**'s small denylist (empty commands, `msfconsole`
  restricted to `search` unless exploitation is enabled, literal `admin`/`admin`
  credential-guessing rejection) is narrower than and already subsumed by our own
  `FR-TOOL-06` behavioral denylist plus the `FR-TOOL-06a` opt-in-category system — no
  gap found here.
- **`test_cookie_redaction.py`** and **`test_config_file_permissions.py`** (now in
  `Standalone-Engine-Reference/tests/`) are relevant reference points for
  implementing our own `FR-COUNCIL-18`/`DR-SCHEMA-14` redaction tests and for
  deciding file permissions on `vapt_agent.config.yaml` (which may eventually hold
  sensitive defaults) — worth a look during Milestone 1/7 of
  `15-Implementation-Milestone-Roadmap.md`, not analyzed further here.
