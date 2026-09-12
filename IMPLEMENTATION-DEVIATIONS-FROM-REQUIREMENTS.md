> ⚠️ **DO NOT INGEST THIS FILE AS A REQUIREMENT.** This is a factual record of where the
> REAL, RUNNING CODE on the Implementing PC (`../implementation/`) diverges from the literal
> text of the numbered requirement docs (`01`–`24`) on this Requirement-Specifying PC, and
> why — kept alongside them, not merged into them, per the operator's own instruction
> (2026-09-08): *"Make a New MD File Along Side Requirement Files in which document such
> changes that we have done during actual implementation (On Implementing PC) which conflict
> the original requirements (From other Requirement Specifying PC) and state the reason of
> such changes."* A build agent must still treat `01`–`24` as the binding spec; this file
> exists so the NEXT requirements-sync pass (like the 2026-09-08 GitHub pull earlier this
> project) has a ready-made list of what to reconcile, instead of the two sides silently
> drifting apart. Every entry below has already been implemented and operator-approved —
> this is not a staging/discussion log awaiting a decision (see `STAGING-Pending-
> Discussions-and-Fixes.md` for that kind of thing); it's the opposite: a decision already
> made in code, recorded here so the spec can catch up to it deliberately.

---

# Implementation Deviations From Requirements

**Ordering convention:** newest on top, same as `STAGING-Pending-Discussions-and-Fixes.md`.

---

## 2026-09-12 — New capability: system suspend inhibited for the duration of an active engagement

**Status: ✅ IMPLEMENTED, ✅ APPROVED, unit-tested (real, live `systemd-inhibit` registration
confirmed via `systemd-inhibit --list`, not mocked). Full writeup, the live verification
that preceded it, and the options considered are in `STAGING-Pending-Discussions-and-
Fixes.md`'s Archive, Round 11.**

### What the requirement says

Nothing, currently — no numbered requirement doc (`01`–`24`) mentions system suspend/sleep
at all. This is a genuinely new capability, not a literal-text conflict with an existing
requirement.

### What real code now does

A real live probe this session (`STAGING` Round 10.2's Option C latency measurement) caught
the host suspending itself mid-engagement (`s2idle`, `xfce4-power-manager`-triggered idle
timeout) while a council model was actively computing — survived unharmed only because
Linux's monotonic clock stops advancing during suspend, uncounted against any timeout
budget. Nothing previously prevented this. `vapt_agent/cli/run.py::run()` now wraps its
`run_full_engagement(...)` call in a new `hold_system_inhibition()` context manager, which
holds a real `systemd-inhibit --what=sleep:idle --mode=block` lock (via a `sleep infinity`
child process, no new Python dependency) for exactly the duration of active orchestration —
covering both the tmux-relaunched auto-start path and a direct/manual invocation uniformly,
since both converge on that one call site. Releases automatically on any exit path (normal
completion, PAUSE escalation, exception) via a `finally:` block, and is orphan-safe under
`vaptctl abort`'s process-group kill and a `systemd-oomd` cgroup-wide kill (Round 10.1)
alike, since it's a child in the same process group/cgroup rather than its own session.
Degrades to holding no lock (never fails the engagement) on a non-systemd host.

### Why this deviates / where it should land in the corpus

Candidate home: `06-Operational-Requirements.md` (engagement lifecycle) or
`05-Security-Safety-and-Compliance-Requirements.md` (a "the system must not silently lose
progress to an OS-level event" framing) — not yet decided, flagged here for the next
requirements-sync pass rather than picked unilaterally.

---

## 2026-09-12 — Strategist role's dedicated inference timeout raised from 1800s to 9000s, backed by a real measured ceiling

**Status: ✅ IMPLEMENTED, ✅ APPROVED. Full writeup, the uncapped probe that produced the
real number, and the options considered are in `STAGING-Pending-Discussions-and-Fixes.md`,
Round 10.2.**

### What the requirement says

`IR-TOOL-03`/`FR-TOOL-05`'s fixed timeout tiers (Quick Probes 180s / Targeted Scans 900s /
Deep-Full-Range 1800s) govern TOOL subprocess timeouts (`nmap`, `sqlmap`, etc.) — a
completely separate mechanism from `STRATEGIST_TIMEOUT_S`, which is the Strategist
council-role's own dedicated AI-model inference-call timeout (`vapt_agent/council/
strategist.py`), already documented in that file's own comments as intentionally NOT
sharing the generic 900s tool-timeout default. No numbered requirement doc names this
constant or its value at all — it has never been part of the literal spec text.

### What real code now does

A standalone, uncapped probe (bypassing `STRATEGIST_TIMEOUT_S` entirely, real baseline-recon
context reused verbatim from a completed engagement) measured the TRUE completion latency
for a real Phase 4.1 Strategist turn on this CPU-only reference host: **7043.4s (117.4 min,
~1h57m)** for a 12,449-prompt-token / 5,207-completion-token real exchange, producing a
genuinely coherent, target-appropriate attack plan. `STRATEGIST_TIMEOUT_S`
(`vapt_agent/council/strategist.py:48`) raised from `1800.0` to `9000.0` (150 min, ~28%
headroom over the measured ceiling) — with `FR-GATE-08`'s existing one-shot restart+retry,
a single attempt at this budget should now suffice without ever needing the retry. Full
suite re-verified clean after the change (1079 passed, 0 failed, 3 skipped).

### Why this deviates / where it should land in the corpus

Same candidate home as the suspend-inhibition entry above — this constant has never had a
documented home in the numbered corpus at all (unlike the tool-timeout tiers, which are
explicitly speced); flagged for the same future reconciliation pass rather than invented a
new requirement ID unilaterally.

---

## 2026-09-11 — `FR-BASELINE-06`: 17 more tools installed, verified, and wired for real

**Status: ✅ IMPLEMENTED, unit/integration-tested, several real invocations confirmed
end-to-end. `STAGING-Pending-Discussions-and-Fixes.md`'s Round 9 has the full writeup
(including the one real design gap this surfaced -- `git-hound`'s third-party API key --
and the two items deliberately NOT attempted this pass, `OPS-NOTIFY` and `FR-TOOL-17`'s
autonomous-login-flow half); this entry is the short, code-focused version.**

### What the requirement says

`FR-BASELINE-06`'s tool-roster table names `knockpy`, `sublert`, `puredns`, `shuffledns`,
`bbot` (Wave 1 subdomain/OSINT-enum group), `byp4xx`, `whatwaf`, `unwaf`, `log4j-scan` (Wave
3 WAF/vuln probing), `x8` (Wave 4 parameter discovery, alongside `arjun`), `graphw00f`,
`clairvoyance`, `graphql-cop` (Wave 4's GraphQL-conditional branch), `jwt_tool` (Wave 4's
JWT-conditional branch), `noseyparker`, `shhgit`, `git-hound` (Wave 1's CODE_REPO-conditional
secrets-scanning group) -- none of these were installed on the implementing host as of the
2026-09-10 audit-fix pass, and were documented there as genuinely deferred.

### What the code actually does now

All 17 are installed for real (apt was blocked by a missing `sudo` password on this host --
`knockpy` went in via its real PyPI package `knock-subdomains` instead of the apt route;
the rest via `go install`/`pipx install`/prebuilt release binaries downloaded directly from
each project's real GitHub releases/`python3 -m venv`+`pip install`-isolated manual clones),
each verified against a real `--help` before any schema was written -- and, for the ones
with identically-named-but-unrelated PyPI packages (`graphw00f`, `graphql-cop`, `x8`),
cross-checked against the package's own PyPI author/homepage/repo metadata FIRST, catching
three confirmed decoys/squatted names before installing anything (`graphw00f`'s PyPI
description literally reads "NOT the real graphw00f tool"). New Tier 1 YAML schemas for all
17 (`vapt_agent/bridge/tier1/schemas/`), wired into `orchestrator/baseline_recon.py`'s
wave-builder functions:

- Wave 1 (NETWORK): `knockpy --recon`, `sublert` (one-shot, `-q true -r true`), `puredns`/
  `shuffledns` in `bruteforce` mode (self-contained -- domain + `DEFAULT_BASELINE_WORDLIST` +
  a new bundled `vapt_agent/data/resolvers.txt`, closing the "no resolvers file" gap
  `massdns.yaml`'s own comment had flagged since the original pull), `bbot -p subdomain-enum
  -y --no-deps` (never autonomously installs a module's own extra dependencies).
- Wave 3 (NETWORK): `byp4xx`/`whatwaf`/`log4j-scan` (need Wave 2's live URL, skip cleanly if
  none), `unwaf` (bare domain, no live-URL gating).
- Wave 4 (NETWORK): `x8` (same live-URL gating as `arjun`); `graphw00f`/`clairvoyance`/
  `graphql-cop` gated on a new `_discovered_graphql_endpoint_from_summary` heuristic (regex
  over Wave 3's crawl output for a `/graphql`-shaped path); `jwt_tool` gated on a new
  `_discovered_jwt_from_summary` heuristic (regex for a `eyJ...` JWT-shaped string in Wave
  2/3 output) -- `jwt_tool`'s schema only allows its `-M` read-only scan modes, forbidding
  the exploit/tamper/crack/sign flags (same AI-gated-only posture as `sqlmap`).
- CODE_REPO (local-path only, same constraint `semgrep` already had): `shhgit -local
  <path> -config-path <bundled config.yaml copy>` (its own `--help` confirms "No need to
  have GitHub tokens with local run"); `noseyparker scan` then, in a SEPARATE wave (so it
  never races `scan` within one wave's concurrent dispatch), `noseyparker report` reading
  back the same relative datastore path.

### A real, pre-existing bug this surfaced and fixed

`bridge/tier1/tools/graphql_scanner.py` (an existing Tier 1 tool from Milestone 9, unrelated
to this pull) had a `graphw00f`-invocation code path written when `graphw00f` was never
actually installed to test against -- it assumed a pip-importable package shape
(`python3 -m graphw00f.main`) and treated ANY non-empty subprocess output, including
`graphw00f`'s own connection-error text, as a valid fingerprint finding. Installing the real
`graphw00f` CLI activated this dead code path for the first time and immediately surfaced
both bugs via the full test suite (not missed) -- fixed to invoke the real resolved binary
with its actual CLI flags and only record a finding on a genuine `returncode == 0`.

### What's still a real, disclosed gap

`git-hound` is registered but NOT baseline-dispatched -- its global-GitHub-search input
shape doesn't fit this pipeline's "scan THIS target repo" model, and it needs a real GitHub
personal access token for practical use that this project has no credential-type concept
for yet (`target_credentials` is per-target-scoped, not a tool's own API key) -- a real,
scoped design question, not decided here (`STAGING-Pending-Discussions-and-Fixes.md`'s Round
9.2 has the recommendation).

---

## 2026-09-10 — Audit-fix pass: `FR-TOOL-15` hash truncation, `FR-TOOL-18` real queued trigger, `FR-DISCOVER-01` real wiring, `FR-BASELINE-07` real crt.sh CT-log check

**Status: ✅ IMPLEMENTED, ✅ APPROVED (operator's own "Check and Map Once Again" audit request
this same day surfaced these as real gaps, not "deliberately partial" as earlier summarized;
this entry documents the fixes made in the 2-hour follow-up window, and is itself an honest
account of what's still open — see the bottom of this entry).**

### `FR-TOOL-15` — `secret_sha256` truncation

Shipped as a full 64-char SHA-256 hex digest (`credential_manager.py`), not the literal
`sha256(...)[:12]` correlation hash `FR-TOOL-15`'s own text specifies. No code anywhere
actually queried `secret_sha256` for real deduplication (dedup is `UNIQUE(target_id,
identity_label)`, not hash-based) — the "full hash backs real dedup" framing in the original
schema comment was aspirational, not a real consumer. Fixed to `[:12]`, matching the literal
spec exactly; `auth_sessions.credential_ref` already used the same `[:12]` form.

### `FR-TOOL-18` — trigger was a direct call, not a queued task; baseline-only, not general

Originally: `orchestrator/baseline_recon.py::_record_tech_fingerprints` called
`check_tech_intel`/`record_tech_intel` directly, and was the ONLY place in the codebase that
ever wrote `discovered_entities.entity_type = 'tech_fingerprint'` — meaning a `whatweb`/
`httpx-toolkit`-shaped tech fingerprint surfaced by an ordinary Phase 4.2 Scripter-selected
tool run (not baseline's own pipeline) never triggered the EOL/CVE check at all, despite
`FR-TOOL-18`'s own wording ("whenever a new `tech_fingerprint` entity is written... including
by `FR-BASELINE-01`'s pipeline" — implying, not limited to it).

Now: `bridge/sanitize.py`'s generic parser (the one parser every Tier 1/Tier 2 tool's raw
output passes through, `PARSERS` being empty) recognizes the same httpx-toolkit-style
`{"tech":["Name:Version",...]}` JSON shape and populates a new `SanitizedRecord.
tech_fingerprints` field — tool-agnostic, not `httpx-toolkit`-name-gated. `bridge/
discovered_entities.py::record_entities` — the one shared call site every Tier 1/Tier 2
dispatch passes through (`bridge/pipeline.py::execute_and_record`) — writes the
`tech_fingerprint` entity and, on a genuinely NEW sighting, calls `bridge/tech_intel.py::
queue_and_run_tech_intel_check`, which inserts a real `task_queue` row (`origin =
'TECH_INTEL_ENRICHMENT'`, a new enum value) before running the check — matching the literal
"queue a follow-on Tier 2 task" wording with a real, auditable queue row, not just a
docstring claiming one exists. `tech_fingerprint_intel` gained a nullable `task_id` FK
linking back to that row.

**Still a deviation, disclosed, not fixed:** the queued task is executed inline,
synchronously, immediately after being created — not drained later by an async worker. This
pipeline has no task-queue-then-later-drain mechanism to plug into (same constraint the
original entry already named); the schema now at least carries a real audit trail
(`task_queue` row + `tech_fingerprint_intel.task_id`) that a future async drain loop could
pick up without another schema change.

`orchestrator/baseline_recon.py::_record_tech_fingerprints` still exists, now calling the
same `queue_and_run_tech_intel_check` — kept only because this module's own test harness
uses a pluggable fake `dispatch` that never touches `execute_and_record`/`record_entities`;
in a real run (`_real_dispatch`, the only path `vaptctl` ever takes) the general path above
already covers baseline's own Wave 2 `httpx-toolkit` output, making this a harmless,
`INSERT OR IGNORE`-deduped no-op re-check in production.

### `FR-DISCOVER-01` — `bridge/tool_discovery.py` had zero call sites (dead code)

Now reachable: `council/primary_scripter.py::run_primary_scripter_command`/`_retry` accept
an optional `domain: str | None` param; when given, `discover_tools(domain)` +
`format_discovery_block` append a "CANDIDATE TOOLS FOR THIS DOMAIN" block (installed vs.
known-not-installed, `FR-DISCOVER-02`) to the Scripter's prompt.

**Still a deviation, disclosed, not fixed:** no caller in the live Phase 4.2 loop
(`orchestrator/phase_lifecycle.py`) actually supplies a `domain` value yet — there is no
task-description-to-Kali-catalog-category classifier anywhere in this codebase, and building
one under this pass's time budget risked exactly the kind of fabricated, unverified behavior
this project already caught once (`s3scanner`'s first draft). The mechanism is real, wired,
and tested end-to-end; the trigger condition (an upstream domain hint) is operator/caller-
supplied, same honesty pattern as `FR-TOOL-15`/`17`'s credential architecture below.

### `FR-BASELINE-07` — `sublert`'s CT-log technique, not installed on this host

`sublert` is not installed (`shutil.which` fails) and its CLI shape is unverified against a
real `--help`/invocation. Rather than fabricate a schema for an unverified binary (again, the
`s3scanner` lesson), `monitor/monitor_engine.py` now queries crt.sh's public JSON API
directly (`enumerate_subdomains_via_crtsh`) — the same certificate-transparency log source
`sublert` itself watches — and merges real CT-log-discovered hostnames into `FR-MONITOR-01`'s
existing `SUBDOMAIN_SET` baseline/diff check. This is a genuine implementation of the
technique FR-BASELINE-07 describes ("continuous CT-log monitoring for new subdomains"), not
a renamed no-op; degrades to the pre-existing static-prefix-DNS-only behavior on any network
failure, per `FR-MONITOR-01`'s own "diff detection, not a hard gate" framing.

### `FR-BASELINE-06` — two more real, installed+verified tools added: `assetfinder`, `gospider`

While auditing the remaining roster gap, checked which of the still-named tools are actually
installed on this host (`command -v`): `amass`, `assetfinder`, `hakrawler`, `gospider` all
are. `assetfinder` (Wave 1, alongside `subfinder`) and `gospider` (Wave 3, alongside
`katana`/`gau`/`waybackurls`) were straightforward to verify against a real `--help` and wire
in cleanly — done. The other two were deliberately NOT wired, for real, specific reasons
(not just "not installed" this time):

- `amass`: this host's `/usr/bin/amass` is a wrapper shell script that unconditionally
  `sudo`s to download libpostal transliteration data on first run if it isn't already
  present (read the wrapper script directly to confirm this, not guessed). Under this
  pipeline's non-interactive subprocess model, that `sudo` fails immediately rather than
  hanging — but every invocation would then be a guaranteed no-op failure until an operator
  pre-provisions that data as root, outside this pipeline. Not wired until that's a
  documented setup step.
- `hakrawler`: verified its entire flag surface (`hakrawler -h`) — there is no `-u`/
  positional-target flag at all; its only input model is a URL piped via stdin.
  `bridge/executor.py::run_subprocess` has no stdin-pipe support today. Wiring it in as-is
  would run with no input and silently produce nothing, ever — worse than leaving it out.

### `FR-BASELINE-06` — multi-repo discovery (a pre-existing limitation, not part of the 2026-09-09 pull itself)

`_discovered_repo_url_from_summary` (now `_discovered_repo_urls_from_summary`) previously
returned only the FIRST github/gitlab/bitbucket URL found in Wave 3's crawl output — a
NETWORK target whose crawl surfaced several distinct repos only got the first one scanned.
Now scans for every distinct repo URL, deduped, and runs one follow-on trufflehog+gitleaks
wave per repo.

### `FR-TOOL-17` — real session establishment + invalidation-stops-propagation, built on the same 2-hour budget

Genuinely built, not deferred after all: `security/session_manager.py` (new) —
`establish_session()` marks an already-`register_credential()`-registered credential as the
active named session for a target (`auth_sessions`, `credential_ref` copied straight from
the backing credential's own `secret_sha256`, never recomputed); `invalidate_session()` marks
it invalid; `get_active_session()` reads the current one. At most one VALID session per target
is an application-level invariant (`auth_sessions` carries no `UNIQUE(target_id)` — a
re-establish supersedes the prior row rather than a schema constraint enforcing it).

The actual enforcement point is `credential_manager.py::get_env_for_target` — the single
FR-TOOL-15 propagation entry point every Tier 1/Tier 2 dispatch already calls — now refuses
(`{}`, its existing no-credential contract, never raises) once a credential's most recently
established session has been marked invalid. This is the concrete form "automatically
injecting that session's credentials... without re-authenticating per call" plus "MUST NOT
auto-retry login" take: no new call site needed, no retry logic exists to disable, and a
credential that was never wrapped in a session at all (the common FR-TOOL-15-only case) is
completely unaffected.

`vaptctl establish-session` / `vaptctl invalidate-session` (new, `cli/session.py`) are the
operator-facing entry points, mirroring `register-credential`'s own CLI pattern.

**Still a real deviation, disclosed, not fixed:**
- The "or an autonomous login-flow task succeeds" half of `FR-TOOL-17`'s text — genuinely
  separate, target-specific login-flow automation. A session's backing credential must
  already be registered (`register_credential`) before `establish_session` can mark it
  active; this module does not itself drive a login form or capture a fresh cookie.
- `OPS-NOTIFY` surfacing (`06:OPS-NOTIFY-01..05`) — a real, separate, cross-cutting subsystem
  (severity-tagged events, dashboard/console banners, an Error Code Dictionary, `vaptctl
  status`'s reason field) that doesn't exist anywhere in this codebase. Invalidation is now
  persisted for real and DOES stop propagation; nothing notifies anyone it happened.

### `FR-BASELINE-06` — multi-repo discovery (a pre-existing limitation, not part of the 2026-09-09 pull itself)

`_discovered_repo_url_from_summary` (now `_discovered_repo_urls_from_summary`) previously
returned only the FIRST github/gitlab/bitbucket URL found in Wave 3's crawl output — a
NETWORK target whose crawl surfaced several distinct repos only got the first one scanned.
Now scans for every distinct repo URL, deduped, and runs one follow-on trufflehog+gitleaks
wave per repo.

### What's still genuinely open after this pass (not fixed, not silently dropped)

- `FR-TOOL-17`'s two remaining pieces (see above): autonomous login-flow automation, and
  `OPS-NOTIFY` — both real, separate infrastructure work.
- `FR-BASELINE-06`'s remaining tool-roster gaps (GraphQL/JWT Wave 4 branches at 0%, most of
  Wave 1's "Always" OSINT/DNS-brute extras, Wave 3's crawler/WAF-probing extras) — see
  `orchestrator/baseline_recon.py`'s own module docstring for the current, honest list.
- `mobsf` — **UPDATE 2026-09-12: now confirmed fully working**, this line's prior
  "unbuildable/unverifiable" status is stale. Pulled the official Docker image
  (`opensecurity/mobile-security-framework-mobsf:latest`), ran it, and did real
  verification (not just a successful pull): Django migrations applied, superuser created,
  gunicorn bound to `0.0.0.0:8000`, `curl -L http://127.0.0.1:8000/` returns a genuine
  `<title>Sign In</title>` page (302→200), MobSF v4.5.2, REST API key issued. Zero
  mentions of `mobsf` were found anywhere in `implementation/` (not even a schema stub) —
  the prior attempt never got far enough to leave a trace, which is why this line existed
  with no further detail. Docker-image verification only — `mobsf` is still NOT yet
  schema-registered as a Tier 1 tool (`19:FR-MOBILE-08`'s design, approved in Round 7,
  remains unimplemented) or wired into any wave; this entry corrects the "can't even get
  it running" status, it does not close `FR-MOBILE-08` itself.

---

## 2026-09-10 — `FR-TOOL-15`/`FR-TOOL-17`: target-credential storage architecture, operator-supplied

**Status: ✅ IMPLEMENTED, ✅ APPROVED, unit/integration-tested (real AES-GCM round-trip,
real subprocess env-injection proven against `/proc/<pid>/environ` vs `/proc/<pid>/cmdline`,
real key-lifecycle tests). Not yet exercised in a live `vaptctl start`→`run` engagement.**

### What the requirement says

`01-Functional-Requirements.md`, `FR-TOOL-15`: "Configured target credentials propagate
automatically to every Tier 1/Tier 2 call via env vars; only a `sha256(...)[:12]`
correlation hash is logged, never the raw credential. Two distinct identities (low/high-
privilege) are registrable as separate named sets." `FR-TOOL-17` (session reuse) builds on
top of this same propagation mechanism. Neither requirement — nor `03:DR-SCHEMA-22`
(`auth_sessions`, `FR-TOOL-17`'s own schema entry) — specifies HOW a raw credential is
actually registered, stored at rest, or decrypted for reuse. `auth_sessions.credential_ref`
is explicitly documented as a one-way `sha256(...)[:12]` hash (`05:SEC-DATA-04`), which by
construction cannot be reversed to actually reuse a session — the corpus names the audit
requirement but never closes the loop on the real storage/decrypt mechanism a working
implementation needs.

### What the code actually does now

A concrete storage/propagation architecture, supplied directly by the operator (not
invented unilaterally by the build agent — an earlier implementation pass explicitly
deferred `FR-TOOL-15`/`17` for exactly this reason, see the prior entry this one replaces
the deferral of):

- **`vapt_agent/data/schema.sql`**: new `target_credentials` table — `encrypted_secret`
  (AES-256-GCM ciphertext, base64), `nonce` (base64), `secret_sha256` (`sha256(...)[:12]`,
  matching `FR-TOOL-15`'s literal wording exactly as of the 2026-09-10 audit-fix pass below
  — never reversible; originally shipped as a full 64-char digest, corrected the same day),
  `scope_domain_regex` (defaults to the
  target's own identifier), `identity_label` (`FR-TOOL-15`'s "separate named sets"),
  `UNIQUE(target_id, identity_label)`. `auth_sessions` gained a nullable `credential_id`
  FK, linking a session to the real encrypted secret backing it — `credential_ref` itself
  is untouched, still exactly the one-way hash `SEC-DATA-04` requires.
- **`vapt_agent/security/engagement_key.py`**: a fresh 256-bit key (`os.urandom(32)`) is
  generated once per engagement, at `vaptctl start` (`cli/start.py`), written ONLY to
  `/dev/shm/vapt_agent/<engagement_id>.key` (tmpfs, RAM-backed) with `0600`/`0700`
  permissions — never to `state.db` or any NVMe-backed path. Discarded at `vaptctl abort`
  (`security/kill_switch.py::abort_engagement`) — "expire cleanly": the encrypted rows
  themselves are untouched, just unusable without a fresh key.
- **`vapt_agent/security/credential_manager.py`**: `register_credential()` (encrypts,
  validates the target belongs to the stated engagement, defaults
  `scope_domain_regex` from the target's own identity) and `get_env_for_target()` (decrypts
  strictly in-memory, maps `credential_type` → env var names — `TARGET_PASSWORD`/
  `TARGET_USERNAME`, `TARGET_AUTH_TOKEN`/`TARGET_AUTH_HEADER`, `TARGET_COOKIE_HEADER`,
  `TARGET_API_KEY`, `TARGET_SSH_KEY`, `TARGET_CERTIFICATE`).
- **`vapt_agent/bridge/executor.py::run_subprocess`** gained an `extra_env` parameter,
  merged on top of a full copy of the process's own environment (never a bare replacement,
  which would strip `PATH`) — never placed in `argv`, so it never appears in
  `/proc/<pid>/cmdline`/`ps aux` (verified directly against a real process's own
  `/proc/<pid>/cmdline` vs `/proc/<pid>/environ` in a real test, not just code inspection).
- **`vapt_agent/bridge/pipeline.py::execute_and_record`** — the ONE function both Tier 1's
  wrapper and Tier 2's bridge route every dispatch through — now calls
  `get_env_for_target()` and passes the result as `extra_env`, satisfying `FR-TOOL-15`'s
  literal "every Tier 1/Tier 2 call" wording from a single injection point. Returns `{}`
  or the overwhelmingly common case of no credential registered for a target — a genuine
  no-op, not a new failure mode.
- New dependency: `cryptography>=42.0` (added to `pyproject.toml`) — AES-GCM has no
  reasonable hand-rolled implementation; this is the standard, actively-maintained,
  OpenSSL-backed choice.

### Why

The operator supplied this architecture directly (2026-09-10) specifically to unblock
`FR-TOOL-15`/`17`, which a prior implementation pass had deliberately left unimplemented
after concluding the requirements corpus itself doesn't specify a storage mechanism and
that inventing one unilaterally for live, possibly high-privilege target credentials was
too large a security-architecture call to make without explicit sign-off. This entry
records that sign-off and the resulting implementation, per this file's own stated purpose
("a decision already made in code, recorded here so the spec can catch up to it
deliberately").

### What would need to change in `01`/`03`/`05` to reconcile this

- `01:FR-TOOL-15` would need a concrete storage-mechanism clause (AES-256-GCM at rest,
  ephemeral per-engagement key, tmpfs-only key storage) instead of only describing the
  propagation/logging behavior.
- `03-Data-and-Storage-Requirements.md` would need a new `DR-SCHEMA` entry for
  `target_credentials`, and `DR-SCHEMA-22`'s `auth_sessions` text should note the new
  `credential_id` linkage column.
- `05-Security-Safety-and-Compliance-Requirements.md`'s `SEC-DATA-04` could be extended to
  name the ephemeral-key architecture explicitly as the mechanism satisfying "local-only,
  never the raw secret in any log or database row."

---

## 2026-09-09 — `FR-GATE-10`: MemAvailable gate widened from 5s to 20s

**Status: ✅ IMPLEMENTED, ✅ APPROVED, live-tested.**

### What the requirement says

`01-Functional-Requirements.md`, `FR-GATE-10`: "poll `/proc/meminfo` `MemAvailable`... **Bounded to 5s**; raise a degraded-swap alert on timeout rather than spawn into a tight memory state."

### What the code actually does now

`vapt_agent/engine/mem_gate.py`'s `MemAvailableGate` defaults `poll_timeout_s` to `20.0`, not `5.0`.

### Why

Direct, real evidence from four consecutive live `vaptctl run` attempts against the actual
Implementing PC host (16 GiB total RAM), each immediately after the new "Graceful Userland
Application Teardown" mechanism (see the 2026-09-08 entry below) had genuinely closed every
targeted app: `MemAvailable` fluctuated within ~20-40 kB of the ~10.1 GiB Strategist-model
threshold from one attempt to the next — sometimes above it, sometimes below, purely on
timing (ordinary page-cache churn during the new `vaptctl run` process's own Python
interpreter startup). This is not a case of the model genuinely not fitting, nor of the
kernel taking a long time to reclaim memory (a 20-second sampled trace of `MemAvailable`
immediately after app-teardown showed a stable reading, not a slow climb) — it's a case of a
5-second window giving the poll loop (already sampling every 0.1s) too few chances to land on
a favorable reading in a state that's already true most of the time. Widening the window
doesn't change what "cleared the threshold" means or weaken the safety check itself, only how
many chances it gets to observe a true state.

**Operator approval:** given explicitly, 2026-09-09, after being shown the exact fluctuation
evidence above and the FR-GATE-10 conflict directly.

---

## 2026-09-08 — Phase 1 Hibernation: Denylist → Allowlist Architecture

**Status: ✅ IMPLEMENTED on the Implementing PC, ✅ APPROVED by the operator. NOT YET
reconciled into `01-Functional-Requirements.md`'s own text** — that edit belongs to
whoever next does a requirements-sync pass on this repo, informed by this entry.

### What the requirement says

`01-Functional-Requirements.md`, `FR-ENV-03`:

> Enumerate active GUI processes; classify each "hibernation-eligible" or "protected"
> against a **fixed denylist** (`systemd`, `dbus`, compositor, session manager, audio
> server) before any signal.

A denylist means: every process is hibernation-eligible **by default**, EXCEPT the ones on
a maintained list of known-dangerous names.

### What the code actually does now

`vapt_agent/orchestrator/hibernation.py`'s `classify_processes()` (implementation PC) now
requires a process to be **explicitly allowlisted by app identity** before it's eligible at
all — everything else survives by default. A pid must satisfy ALL of:

1. Its `comm` (or the `comm` of an ancestor whose full descendant-process tree it belongs
   to) matches `HIBERNATION_ELIGIBLE_APP_NAMES` — currently browsers (Chrome, Chromium,
   Brave, Firefox, Firefox ESR, Tor Browser) plus Thunar and Mousepad, per the operator's
   own stated policy for what hibernation exists to reclaim RAM from.
2. It's **also** not on the ORIGINAL fixed denylist (`PROTECTED_PROCESS_NAMES` — every
   category built up across this project's three real forced-hardware-shutdown incidents:
   kernel threads, GUI terminal/tmux windows, USB/Bluetooth hotplug daemons) — kept as a
   second, independent gate for defense in depth, not removed.
3. It's not caught by any of the other orthogonal, identity-independent protections this
   module already had: `controlling_session_pids()`, `tmux_session_pids()`,
   `container_managed_pids()`, `pids_holding_file_locks()`, and a new one added alongside
   this change, `in_flight_tool_pids()` (see below).

This is a structural inversion of FR-ENV-03's literal mechanism, not an extension of it.

### Why this deviation was made

A code-review pass on 2026-09-08 (`/code-review max` against the real `implementation/`
codebase) found 15 correctness bugs in this exact hibernation/restoration code path, on top
of three real, already-fixed forced-hardware-shutdown incidents earlier in the same
project:

1. Kernel threads getting `SIGSTOP`'d (2026-09-05) — froze the host solid, hardware
   power-button shutdown required.
2. GUI terminal/tmux windows getting `SIGSTOP`'d within about a second of the dashboard/
   console auto-launching (2026-09-07/08) — same failure mode.
3. USB/Bluetooth hotplug-mediating daemons getting `SIGSTOP`'d, hanging the kernel's own
   USB subsystem (2026-09-08) — same failure mode again, a third distinct category.

Each was fixed reactively by expanding the denylist after the fact. The pattern across all
three, plus the 15 further bugs the code-review pass found in the SAME mechanism, is
structural: **a denylist can only ever be as complete as the incidents that have already
happened to it.** "Protect anything not already known-dangerous" is the wrong default for
an action this destructive (an unrecoverable-without-physical-access host freeze, three
times over) on a host whose exact process inventory (VAPT tooling, browser-automation
libraries, arbitrary tool subprocesses) is not fully enumerable in advance.

An allowlist inverts the risk: hibernation now only ever touches a process whose identity
is explicitly, deliberately marked safe to freeze. Everything else — including any category
nobody has thought of yet, the exact blind spot that caused all three incidents — survives
automatically. The cost is narrower coverage (only browsers/Thunar/Mousepad get frozen,
not "everything except a growing list"), which the operator's own stated policy this
session already scoped hibernation to in practice: *"Most of the Times, the Extra Apps
include Browsers (Chrome, Firefox, Tor, Brave), Thunar (File Manager), Mousepad (Text
Editor)."*

**Operator approval:** given explicitly, 2026-09-08 — *"Architecture Level Change is
approved"* — in the same message that accepted the two other code-review recommendations
below.

### A new gap this change would have introduced, and how it's closed

Allowlisting by app identity alone has a real edge case this project's own host exposes:
headless-browser-automation tooling (`playwright`, `pyppeteer`, `ferrum` — all installed on
the Implementing PC) spawns a real subprocess literally named `chrome`/`chromium`/`brave`
when a VAPT task uses it for JS-rendering/browser-automation recon. Under the new allowlist,
that in-flight tool subprocess would match `HIBERNATION_ELIGIBLE_APP_NAMES` by name — and
per `CLAUDE.md`'s own coding rule, every tool subprocess is spawned with
`preexec_fn=os.setsid` (its own new POSIX session, deliberately separate from the
orchestrator's), so `controlling_session_pids()` alone does not protect it. Freezing the
pipeline's own active work mid-task would be worse than the incident this change fixes.

Closed by a new function, `in_flight_tool_pids()` (`orchestrator/hibernation.py`), which
protects every pid (`tool_execution_logs.end_ts IS NULL` for the current engagement, joined
through `task_queue`/`targets` — the same join `security/kill_switch.py`'s `abort_engagement`
already uses) plus its full descendant-process closure. Not itself a requirement conflict
(nothing in `01`/`05` currently addresses tool-subprocess hibernation-safety one way or the
other) — recorded here only because it's a direct structural consequence of the deviation
above, not a standalone decision.

### What would need to change in `01-Functional-Requirements.md` to reconcile this

- `FR-ENV-03`'s own wording ("classify... against a fixed denylist") would need to become
  an allowlist description, naming `HIBERNATION_ELIGIBLE_APP_NAMES`'s actual scope
  (browsers, Thunar, Mousepad) as the eligibility criterion, with the current denylist
  categories re-described as a secondary, defense-in-depth filter rather than the primary
  mechanism.
- A new requirement covering `in_flight_tool_pids()`'s protection of in-flight tool
  subprocesses would be a reasonable, currently-missing addition to the `FR-ENV` cluster.

---

## 2026-09-08 — `thaw_all()`/`verify_suspended_alive()`: pid-recycling safety (additive, not a conflict)

**Status: ✅ IMPLEMENTED, ✅ APPROVED.** Not a requirement deviation in the same sense as the
entry above — recorded here for completeness since it landed in the same operator-approval
message, and it does touch `03-Data-and-Storage-Requirements.md`'s `suspended_processes`
shape (a new `start_time_ticks` column, additive/nullable, no existing requirement text
contradicted).

**Gap fixed:** `thaw_all()`/`verify_suspended_alive()` previously identified "the process I
suspended" purely by numeric pid, with no start-time/identity check. FR-ENV-12 already
requires detecting an OOM-killed suspended process ("mark the outcome partial/degraded"),
but if that pid was later reused by the kernel for a completely unrelated process before
Phase 5 restoration ran, the old code would `SIGCONT` the wrong process and record it as a
successful resume — the original target stays gone, silently.

**Fix:** `/proc/<pid>/stat` field 22 (`starttime`, verified directly against a real running
process on this host before trusting it) is recorded in `suspended_processes.start_time_ticks`
at suspend time and compared against the live process's own starttime at thaw/verify time. A
mismatch is now treated identically to "pid is gone" (FR-ENV-12's existing degraded-outcome
path), not as a successful resume. `NULL` for rows written before this column existed, which
correctly falls back to the pre-existing liveness-only check for those.

This is additive to `03`'s `suspended_processes` table shape (nullable column, no existing
row format broken) and doesn't contradict any requirement's literal text — included here
only because the operator's approval covered it in the same breath as the architecture
change above.

---

## How to add new entries

New entries go **above the existing ones**, newest on top, same convention as
`STAGING-Pending-Discussions-and-Fixes.md`. Only record something here once it is BOTH
implemented in `../implementation/` AND operator-approved — this file is a record of
settled divergence, not a place to propose one.
