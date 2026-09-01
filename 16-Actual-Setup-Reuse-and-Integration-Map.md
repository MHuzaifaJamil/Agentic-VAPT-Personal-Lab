# `Actual-Setup/` Reuse & Integration Map

**Purpose:** `Actual-Setup/` (a full copy of the `claude-bug-bounty` Claude Code
plugin) was added to this repository as a candidate source of reusable assets. This
document is the concrete, asset-by-asset analysis of what actually transfers to the
Agentic VAPT System defined in `01`-`15`, what doesn't, and why — verified by reading
the actual files, not inferred from `Actual-Setup/CLAUDE.md`'s own summary.

---

## 1. The Architectural Relationship (read this before anything below)

`Actual-Setup/` is a **Claude-Code-native, human-copilot toolkit**: a person runs
`claude`, types `/recon target.com`, and Claude itself — via Claude Code's own
runtime (Bash/Read/Write/WebFetch tool access, its own subagent dispatch) — reads
the skills/rules/agents as prompts and acts on them interactively. `rules/hunting.md`
makes the operating model explicit: it addresses "you" as a hunter working inside a
live chat session, with a human confirming scope via `/scope` before every asset.

The Agentic VAPT System is architecturally close to the opposite: fully local
(`NFR-SEC-02` — no cloud model dependency at all), five specific `.gguf` models via
`llama.cpp`, its own deterministic gates, its own SQLite state, its own CLI
(`vaptctl`), and — per `FR-COUNCIL-11`/`FR-CTRL-09` — designed to run **unattended**
for up to 12 hours with no human in the loop at all.

**Consequence:** nothing in `Actual-Setup/skills/`, `commands/`, or `agents/` is
directly executable by this system. They are markdown prompts written for a
different runtime (Claude Code's own tool-calling loop) talking to a different model
(Claude). Our Operator cannot "load a skill" the way Claude Code does — there is no
equivalent mechanism in this design, and building one is out of scope (it would mean
depending on Claude Code / a cloud model, which `NFR-SEC-02` rules out entirely).

What follows is not "does this concept fit" — it's an asset-by-asset breakdown.

---

## 2. Tool Scripts (`Actual-Setup/tools/*.py`, `*.sh`) — the highest-value category

44 Python scripts were checked for internal package coupling (`from memory.` /
`from tools.` imports) — this is the difference between "drop this one file in and
it works" and "this needs the whole package or a rewrite."

### 2a. Verified standalone (29 files — no cross-module imports)

```
auth_session.py       banner.py            breach_checker.py
credential_store.py   dashboard.py         dom_xss_harness.py
h1_mutation_idor.py   hai_payload_builder.py  hai_probe.py
jwt_scanner.py         lead_board.py        llm_redteam.py
mindmap.py             oob_listener.py      port_scanner.py
prompt_safety.py       recon_adapter.py     safe_http.py
sast_scan.py           scope_checker.py     sneaky_bits.py
_spray_http_form.py    _spray_oauth.py      target_selector.py
visual_triage.py       waf_encoder.py       zendesk_idor_test.py
zero_day_fuzzer.py
```

### 2b. Verified coupled (15 files — pull in `memory.*`/`tools.*` internals)

```
cors_scanner.py     crlf_scanner.py      eol_check.py
h1_idor_scanner.py  h1_oauth_tester.py   h1_race.py
hunt.py             intel_engine.py      learn.py
memory_gc.py        multipart_mutator.py nosqli_scanner.py
token_scanner.py    validate.py          waf_response_analyzer.py
```

Coupled scripts are not unusable — they'd just need either the whole `memory`/
`tools` package structure imported alongside them, or the specific logic extracted
and rewritten against our own `03-Data-and-Storage-Requirements.md` schema instead
of their JSONL-based memory layer. Treat 2a as "adopt directly," 2b as "port the
logic, don't import the package."

### 2c. Highest-confidence Tier 1 candidates (read in full, verified standalone)

| Script | Maps to | Notes |
|---|---|---|
| `scope_checker.py` | **`FR-COUNCIL-03a`** (deterministic Tier 0 scope check) | Near-exact match for what we need: "deterministic scope checker — code check, not LLM judgment," anchored suffix matching (`*.target.com` matches `sub.target.com`, not `evil-target.com`), explicit IP/CIDR non-support with a clear warning rather than silent wrong behavior. **Recommendation: use this file's `_domain_matches`/`ScopeChecker` logic directly as the reference implementation for `FR-COUNCIL-03a`**, extending it for CIDR support (`FR-COUNCIL-03a` requires CIDR matching, which this file explicitly does not support) and the port-range/destructive-flag checks `FR-COUNCIL-03a` also requires. |
| `jwt_scanner.py` | New Tier 1 tool (JWT attack testing) | Not currently in our Tier 1 list (`nmap`/`masscan`/`nuclei`/`ffuf`/`feroxbuster`/`gobuster`/`sqlmap`/`nikto`/`whatweb`/`wafw00f`/`testssl`). Candidate addition if JWT-based auth testing is in scope for a given engagement. |
| `port_scanner.py` | Overlaps `nmap`/`masscan` (already Tier 1) | Likely redundant with existing Tier 1 tools — evaluate whether it adds non-HTTP service-specific value (per its `CLAUDE.md` description: SSH/DB/Redis/Docker-API/RDP discovery) before adding as a separate tool. |
| `dom_xss_harness.py`, `oob_listener.py` | New Tier 1 tools (headless-browser DOM XSS confirmation, OAST/blind-vuln confirmation) | Both describe capabilities (headless browser rendering, out-of-band callback listening) our current Tier 1 list has no equivalent for at all — genuinely additive, not overlapping. |
| `sast_scan.py` | Out of scope for this system as specified | Wraps Semgrep over fetched JS/source for static analysis — `01-Functional-Requirements.md` never defines a source-code-access mode (this system is a black-box/grey-box network VAPT tool per its whole design). Note but don't adopt unless the system's scope is deliberately expanded later. |

**Not yet classified individually:** the remaining standalone scripts (`banner.py`,
`dashboard.py`, `mindmap.py`, `prompt_safety.py`, `safe_http.py`, `waf_encoder.py`,
`zero_day_fuzzer.py`, etc.) and all 15 coupled ones. **Recommendation:** a one-time
classification pass over the full `tools/` directory belongs in
`15-Implementation-Milestone-Roadmap.md` Milestone 1 (Tool Bridge), not fabricated
here without reading each file.

### 2d. Deployment path — no requirements change needed

`FR-TOOL-03`'s Tier 2 path-restricted allowlist already covers `/usr/bin/`,
`/usr/sbin/`, and **`/opt/`**. Any adapted script from this section deploys to
`/opt/vapt_agent/tools/` on the target machine — already inside the existing
allowlist. No amendment to `FR-TOOL-03` is needed; this is a packaging/deployment
convention, not a requirements gap (an earlier chat-only version of this analysis
overstated this as a gap — corrected here).

---

## 3. MCP / Burp / HackerOne Integration

| Asset | Finding (verified by reading `config.json`/`server.py`) | Integration guidance |
|---|---|---|
| `mcp/burp-mcp-client/` | **Not actually MCP.** `config.json`'s own comment states it plainly: `cc-bridge` is a REST API Burp extension, called via `curl` in `tools/burp_bridge.sh` (`base_url: http://127.0.0.1:1337`, bearer token from `~/.cc-bridge-token`). | Our Tier 2 bridge (or a dedicated integration module) can call the same REST endpoints directly via `requests`/`httpx`. **No MCP client implementation is needed on our side for Burp.** |
| `mcp/hackerone-mcp/server.py` | A genuine registered MCP server, but its own docstring shows it's independently CLI-invocable and is "a lightweight wrapper around HackerOne's public GraphQL API" — no auth required. | Call HackerOne's public GraphQL API directly, bypassing the MCP layer entirely, for the same reason as Burp above. |
| `mcp/caido-mcp-client/` | **Verified — genuinely different from Burp/HackerOne.** `opencode-config.json` registers a real MCP server: `{"mcp":{"caido":{"type":"local","command":["npx","-y","@caido/mcp-server"],"environment":{"CAIDO_API_KEY":"...","CAIDO_URL":"..."}}}}`. There is no REST-bypass shown anywhere in this config the way `cc-bridge` provides one for Burp — Caido's own MCP server is the only integration path evidenced here. | **A real MCP client would be needed if Caido integration is wanted** — see revised conclusion below. |
| No dedicated Playwright MCP config exists anywhere in the source repo. | Checked `.claude/settings.json` (no `mcpServers` key at all — only hooks and enabled plugins) and the whole repo for a `mcp/playwright-mcp-client/`-style folder analogous to Burp/Caido — neither exists. The only Playwright-related artifact is `.playwright-mcp/` at the repo root, which is a **runtime cache** (timestamped page snapshots and console logs from actual past sessions), not a configuration file. Playwright MCP is therefore registered outside this repository entirely — most likely a global/user-level `claude mcp add` registration on that machine, which has no file to "fetch" in the first place. | **Nothing to copy or configure from — there is no Playwright MCP config in this repo.** `.playwright-mcp/` was correctly never copied (see updated safety note below — it also contains real session artifacts, not just being the wrong kind of file). |

**Revised conclusion (corrects the original, Burp/HackerOne-only-based one):** Burp
and HackerOne integration need no MCP client — both reduce to plain REST calls
callable directly from our own bridge code. **Caido is different: if Caido
integration is ever wanted, this system would need an actual MCP client
implementation** (or a Burp-style REST bridge extension for Caido, if one exists —
not evidenced by anything copied here). This is not currently a requirement anywhere
in `01`-`17` — Burp/Caido/HackerOne integration was always `FR-TOOL-10`/`11`-level
**optional** methodology tooling, not a core requirement — but it should not be
assumed "free" the way Burp turned out to be. No MCP client is added to `04`'s
requirements or `13`'s module layout by this correction; it's flagged here as
groundwork for if/when that optional integration is actually pursued.

**Additional safety note (new, not in the original safety notice):** while checking
`.claude/settings.json` for MCP registrations, `.claude/settings.local.json` in the
source repo was found to contain a permission allowlist listing **real attack
commands run against a real client (`myco.io`)** — actual URLs, actual SSRF/open-redirect
payloads. This was never copied (confirmed: `Actual-Setup/` contains no `.claude/`
directory at all), but it belongs alongside `hunt-memory/`/`findings/`/`recon/`/
`target_config.yaml` in `17-Standalone-Engine-Reuse-and-Comparison.md`'s safety
notice as a category to never go back and copy from that source repo.

---

## 4. Skills & Rules — Methodology to Mine, Not Code to Run

None of these are executable by our system (§1). Their value is as **verified
source material to enrich `14-System-Prompt-Templates.md`'s prompts** — mining
content, not integrating code.

### 4a. Implemented this pass (verified in full)

**`skills/triage-validation/SKILL.md`** was read in full. Its "7-Question Gate" (in
practice 8 questions) and closure-discipline procedures are materially more rigorous
than `FR-COUNCIL-14`'s current 4-item false-positive checklist (WAF block / rate
limit / generic error / honeypot). Not everything in it applies — Q2 ("is impact on
the *program's* accepted impact list") and Q7 (bug-bounty "never submit" class list)
are bounty-payout-eligibility concepts with no equivalent in an authorized VAPT
engagement, where any confirmed vulnerability gets reported regardless of whether a
bounty program would pay for it. What **does** transfer directly:

- **Q6 — "prove impact beyond technically possible."** E.g. XSS must show actual
  cookie theft/session hijack, not just `alert(1)`; SSRF must hit an internal
  endpoint that returns data, not just a DNS ping; IDOR must show the actual
  other-user's data in the response, not just a 200 status.
- **Q8 — the identity/session check for IDOR/BOLA and privilege-escalation
  findings.** A finding that only reproduces under one identity, or stops working
  when logged out, is very often a scoped permission boundary, not a real bug — the
  skill file states this is "the most common reason confirmed IDOR findings come
  back as N/A."
- **Baseline/attack/diff confirmation** and the **matched-twin negative control**
  discipline (change exactly one property, preserve everything else, so the twin
  travels the identical code path) — a materially stronger evidence standard than
  our current gate's generic "distinguish real injections from generic errors."

These three have been folded into `FR-COUNCIL-14` (revised) and the Gate 3
Adjudicator prompt in `14-System-Prompt-Templates.md` §4 — see those files for the
actual applied text. This is the one methodology-mining item actually implemented in
this pass; everything below is identified but not yet drafted.

### 4b. Identified as high-value, not yet mined (recommend as follow-up work)

| Skill | Target | Why (from its own `CLAUDE.md` description, not yet fully read) |
|---|---|---|
| `skills/web2-vuln-classes/SKILL.md` | Strategist prompt (`14` §1) | 32 documented bug classes with root causes, bypass tables, and bug-specific checklists (SSRF's 11 IP-bypass techniques, IDOR's backward-taint procedure, etc.) — would give the Strategist a far more specific hypothesis vocabulary than its current generic "propose a specific, testable hypothesis" instruction. |
| `skills/bb-methodology/SKILL.md` | Strategist prompt (`14` §1) | Describes a 5-phase non-linear workflow + a "developer psychology / anomaly detection / what-if experiments" critical-thinking framework for deciding what to test next — directly relevant to how the Strategist should reason about attack-path ordering. |
| `skills/report-writing/SKILL.md` | Reporter prompt (`14` §5) | Impact-first writing rules, a title formula, an impact-statement formula, a "never write 'could potentially'" rule, a reproduction-capsule convention — all directly applicable to strengthening the Reporter's narrative-drafting instructions. |
| `skills/security-arsenal/SKILL.md` | Operator prompt (`14` §3) | Payloads/bypass tables and a "submittable vs. always-rejected" table — could inform what the Operator considers worth proposing as a follow-on task (`FR-COUNCIL-10`). |

**Why these weren't drafted into `14` in this pass:** each of `01`'s prompts was
written to be exact and traceable to a verified source, not "plausible-sounding."
`4a` was implemented because the source was read in full first. `4b`'s entries were
only skimmed via their own frontmatter description — mining them properly means
reading each in full first, the same discipline applied to `4a`, not summarizing
from a one-line description into a rewritten prompt.

---

## 5. What Does Not Reuse At All

| Asset | Why not |
|---|---|
| `commands/*.md` (39 slash commands) | Claude-Code-specific dispatch definitions. Our command surface is `vaptctl` (Click, `13-Implementation-Architecture-Bridge.md` IAB-CLI) — an unrelated mechanism. |
| `agents/*.md` (9 subagents) | Claude-Code subagent prompts, invoked via Claude Code's own Agent/Task tool. Our "agents" are the five local models in the council — a different concept entirely. `agents/autopilot.md`'s scope→recon→rank→hunt→validate→report loop is a useful *conceptual* validation that our own 5-phase shape is sound (it's solving the same problem), but contains no transferable logic — the reasoning there is done by Claude itself, not by a portable algorithm. |
| Running any `skill/`, `command/`, or `agent/` file as-is | These require Claude Code's runtime and a cloud model to interpret; running them "against" our local council does nothing, because they're prompts for a different system, not portable instructions. |

---

## 6. Follow-Up Items (not resolved in this pass)

| Item | Action needed |
|---|---|
| `rules/vapt_report_format.md` vs `12-Report-Formatting-Rules.md` | `12` was cloned from an earlier version of this toolkit's `CLAUDE.md`. `Actual-Setup/rules/vapt_report_format.md` is a separate, likely-evolved file under the same lineage — diff the two before implementation; `12` should be re-verified against whichever is more current, not assumed still accurate. |
| `mcp/caido-mcp-client/` | Unverified — check whether it's genuine MCP or another REST wrapper (§3) before assuming either. |
| Full `tools/` classification | 15 files beyond §2c were named but not individually read — a classification pass belongs in Milestone 1 of `15-Implementation-Milestone-Roadmap.md`. |
| §4b methodology mining | Reading `web2-vuln-classes`, `bb-methodology`, `report-writing`, and `security-arsenal` in full and drafting the resulting prompt revisions — recommended as its own follow-up pass, not rushed here. |
