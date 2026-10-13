# Realistic Mitigations for Every Issue Identified So Far

**Scope:** every issue catalogued in `2026-10-07-All-Known-Issues-and-RAG-Literature-Context.md`,
one by one. Each entry states the realistic fix, why it's realistic (not just theoretically
possible), effort/risk, and what still needs verifying before trusting it. Several were
checked directly against Mugheeraat's real code (fresh clone, commit `f93747c`) rather than
proposed from memory — flagged inline where that happened.

---

## 1. Recon-input gap (SPA static-crawling blindness) — Round 26, previously undecided

**The realistic fix, verified directly against the real binary on this host:**
`katana` — already installed, already in the baseline pipeline, already Tier-1-schema-
registered — **has a native headless-crawling mode**:

```
-hl, -headless          enable headless crawling (experimental)
-hh, -hybrid            enable headless hybrid crawling (experimental)
-sc, -system-chrome     use local installed chrome browser instead of katana's own
```

This runs a real embedded Chrome, executes the page's actual JavaScript, and captures the
real XHR/fetch calls a modern Angular/React SPA makes — exactly the capability the staged
Round 26 options (Playwright/Puppeteer integration, manual endpoint seeding, or accepting the
limitation) were trying to add from scratch, **already present in a tool already in the
arsenal.** This was not found anywhere in the Round 26 write-up or the Pipeline-Flow-Audit —
a real gap in what was considered, not just in what was implemented.

**Why this beats the three staged options:**
- vs. **Playwright/Puppeteer integration**: zero new dependency, zero new Tier-1 schema, zero
  new sandboxing consideration — it's one flag on a binary already wired in.
- vs. **manual endpoint seeding**: this is general-purpose, works against any future SPA
  target, not a one-off fix for this specific benchmark.
- vs. **accepting the limitation**: directly closes it instead of giving up on an entire
  class of modern web targets.

**Effort/risk:** low. `-headless`/`-hybrid` are marked "experimental" by katana's own `-h`
output — worth a real test-lab comparison (headless crawl output vs. the known-11-finding
Juice Shop ground truth) before trusting it in production, not a blind flag flip. Resource
cost is real but bounded: a headless Chrome instance is heavier than katana's default
HTTP-only crawl (more RAM/CPU for the crawl's duration), worth measuring on this host's real
RAM budget before making it the default for every baseline recon pass — a reasonable middle
ground is gating it behind the same "no live URL yet" pattern already used elsewhere (only
escalate to headless mode if the non-headless crawl found suspiciously few URLs — e.g. under
some small threshold — rather than always paying the heavier cost).

**What to verify before trusting it:** run `katana -hl` against Juice Shop specifically and
check whether it actually surfaces the real `/rest/...`/`/api/...` routes this session's
manual ground-truth work found — this is empirically checkable in minutes, not a theoretical
question.

---

## 2. Candidate-detection vocabulary gap (9 of 19 classes undetectable)

Each of the 9 has a real, specific, mostly-deterministic signature — these are not novel
research, they're established penetration-testing detection techniques, several of which
this project **already has the raw ingredients for** and just hasn't wired up:

| Class | Realistic detection signature | Effort |
|---|---|---|
| **SSRF** | **Already has the exact mechanism available and unused**: `oob_listener.py`/`interactsh-client` are both Tier-1-registered (confirmed directly in the schema files) but **not in `candidate_detection.py`'s tool filter at all**. Wiring an OOB-callback confirmation in as its own candidate rule (a callback received = a blind SSRF/RCE/deserialization confirmation) closes SSRF and gives partial coverage for RCE/insecure-deserialization too, for free, using infrastructure already built. | Low — this is wiring, not new capability |
| **SSTI** | Mathematical-expression echo: send a template expression (`{{7*7}}`, `${7*7}`), check the response for the *evaluated* result (`49`) rather than the literal payload reflected back unescaped (which is XSS's signal, already covered). A regex comparing "did we send an expression and get back its arithmetic result" is deterministic and standard. | Low |
| **LFI** | Known-file-content signatures: `/etc/passwd` responses containing a `root:.*:0:0:` pattern, Windows `win.ini` responses containing `[fonts]` or `[extensions]` — both are textbook, well-documented LFI confirmation signatures, not guesswork. | Low |
| **Insecure deserialization** | Partially covered by the OOB mechanism above (blind cases); for non-blind cases, known exception/stack-trace signatures exist per language (Java's `ObjectInputStream`/`InvalidClassException` text, PHP's `unserialize()` warning text, Python `pickle` traceback text) — a pattern list analogous to the existing SQL-error-pattern list, same shape as a mechanism this module already has. | Low-Medium |
| **Race condition** | Structurally different from the rest — requires *comparing results across concurrent requests*, not pattern-matching one response. Realistic version: a dedicated Tier-1 tool invocation shape (fire N parallel identical requests, e.g. a double-spend/coupon-redeem attempt) with its own detection logic (count successes > expected), not a `candidate_detection.py` regex at all. This is the one class here that's a real, separate feature, not a cheap rule addition — lowest priority of the 9 for that reason. |  Medium-High |
| **JWT** | Structural pattern: detect a JWT-shaped token (`eyJ...\.eyJ...\.`) in the response **combined with** a known-weak-signing confirmation (`"alg":"none"` accepted, or a privileged action succeeding after a client-side-only role-claim edit) — the token-shape half is cheap regex; the "did the bypass actually work" half reuses the existing access-control-class 200/201/204-success signal already in the module. | Low — mostly recombining existing signal |
| **Subdomain takeover** | **Already has the exact tool wired in baseline recon and unused by candidate detection**: `subjack` is Tier-1-registered (confirmed directly in its schema) and runs in Wave 2, but isn't in `candidate_detection.py`'s tool filter. `subjack`'s own output already contains a vulnerability-confirmation marker in its stdout when it finds a dangling CNAME — adding `subjack` to the filter and matching its own "vulnerable" line format closes this with no new tool, same pattern as wiring in `nikto`/`testssl`/`wafw00f` already was in Round 27. **Verify `subjack`'s exact output string against a real run before finalizing the regex** — this doc states the mechanism with confidence, not the literal string, consistent with this project's own "verify, don't assume" discipline. | Low |
| **RCE** | Command-echo confirmation: inject a command whose output is distinctive and unlikely to appear otherwise (`id` producing `uid=\d+\(.*\) gid=\d+`, or a time-delay payload like `sleep 10` combined with measuring real response latency against a baseline — the latter needs the same "compare against a control request" capability as the Adjudicator's baseline/attack/diff question, see issue 11 below, so these two issues share a fix). | Low (string-echo half) / Medium (timing half) |
| **Prompt injection** | Lowest priority — only applies to AI-powered targets, a narrow slice of real-world scope, and detection requires comparing model *behavior* change, not a string in a response. Realistic minimal version: a short, fixed canary instruction in the payload (e.g. "respond with the literal string CONFIRMED_PI_9f3a") and check for that exact string in the output — cheap once a scope actually needs it, but not worth building ahead of a real need given everything else on this list. | Low effort, but defer until needed |

**Overall assessment:** 6 of the 9 (SSRF, SSTI, LFI, deserialization-partial, JWT, subdomain
takeover) are genuinely low-effort, because they're either textbook deterministic signatures
or — for SSRF and subdomain takeover specifically — **wiring in capability this project
already built and simply never connected to this module**. Race conditions and the timing
half of RCE need a real new capability (parallel/timed request comparison). Prompt injection
is fine to defer.

---

## 3. `GATE1_REJECTED` missing live-dashboard visibility

**Realistic fix:** `dashboard/compute.py`'s `TaskFunnel` dataclass has exactly 5 fields
(confirmed directly in the audit's own grep) — add a 6th (`gate1_rejected`) and a
corresponding warning-color row in `dashboard/render.py`, mirroring the existing
`gate2_blocked` amber-warning treatment exactly. This is the smallest, lowest-risk item in
this entire list — a dataclass field and a render-loop line, following an existing, already-
proven pattern in the same file. No new mechanism, no new risk.

**Effort/risk:** trivial. **Verification needed:** none beyond the existing dashboard test
suite's own coverage pattern for `gate2_blocked`.

---

## 4. Structured-output crash pattern (fixed 5 times independently — a process issue, not a code issue anymore)

**Realistic fix, now that all 5 instances are closed:** don't fix a 6th sibling site
reactively if one ever appears (e.g. if a 7th council role is ever added) — **centralize the
pattern into one decorator/context-manager** (`@guard_structured_output(terminal_status=...)`
or equivalent) that every council-role call site uses, so a new role automatically inherits
the guard instead of needing its own crash-then-fix cycle. This is a real, standard software-
engineering response to "the same bug was independently reintroduced/missed N times" — centralize
the cross-cutting concern instead of repeating it at each call site.

**Effort/risk:** low-medium — a refactor of 5 already-correct call sites into one shared
mechanism, not new logic. Real risk is purely regression risk during the refactor (each site's
specific terminal status differs — `GATE2_BLOCKED` vs `ADJUDICATION_FAILED` vs a phase-log
`FAILED` row for the Strategist) — needs the shared mechanism to accept the status/table as a
parameter, not hardcode one. **Not urgent** (no open bug today), but cheap insurance against
the same five-times-over discovery pattern recurring for a 6th site.

---

## 5. Low skill-RAG trigger rate (8.6%, 1/6 reaching dispatch)

**Already has a realistic fix proposed and documented in detail**:
`2026-10-07-Embedding-Based-Skill-Retrieval-Upgrade.md` (`all-MiniLM-L6-v2` + `sqlite-vec`,
fully local, no GPU). Not re-derived here — see that doc for the full mitigation, effort
estimate, and integration sketch. Worth re-measuring the real trigger rate after the
upgrade against this session's own logged 8.6%/70-task baseline specifically, not a
synthetic test alone.

---

## 6. Tier-1 SQL filter excludes `masscan`/`ffuf`/`feroxbuster`/`gobuster` output

**Realistic fix:** identical pattern to Round 27's own `nikto`/`testssl`/`wafw00f` addition —
widen the `tool_name IN (...)` filter (`candidate_detection.py:443`, confirmed directly) to
include these four. This has direct precedent in the same codebase, done correctly once
already — low risk of this being done wrong a second time.

**One real caveat worth checking first, not just assumed:** `ffuf`/`feroxbuster`/`gobuster`
output is mostly directory/file-existence enumeration (200/403/301 status lines per path) —
adding them to the filter without a *matching detection rule* for "does this look like an
exposed sensitive file" (the directory-listing rule Round 27 already added covers Apache/
nginx autoindex pages specifically, not a bare `ffuf` hit-list) would just mean their output
gets *read* without anything new being *detected* in it. **Pair this with extending the
existing directory-listing/PII rule to also check `ffuf`/`feroxbuster`/`gobuster`'s own
discovered-path list against a small sensitive-filename pattern** (`.env`, `.git/`,
`backup`, `.bak`, `id_rsa`, `.kdbx` — several of these literally match this session's own
ground-truth findings #3/#4) — the filter widening alone is necessary but not sufficient.

**Effort/risk:** low for the filter widening; low-medium for the accompanying sensitive-path
pattern (a straightforward addition in the same shape as the existing rules, not a new rule
*type*).

---

## 7. CORS/header-dependent rules blind without `-i`/`-D`/`-v`

**Realistic fix:** exact same proven pattern already used for status codes.
`bridge/tier2.py::_curl_argv_with_status_marker` already deterministically force-appends a
status-code marker to every Tier-2 curl invocation regardless of what the model remembered to
ask for (confirmed directly, and confirmed working via the real fix that unblocked the XSS/
access-control rules in §3.5 of the Testing Guide). **The same function should also force-
append `-D -` (dump headers to stdout) unless the command already requests headers some
other way** — this is the identical "inject deterministically after Gate 2, pure formatting
addition, no new capability" pattern, in the same function, not a new mechanism.

**Effort/risk:** low — this is extending an already-proven function, not building a new one.
**Verification needed:** confirm `-D -` doesn't interact badly with any existing flag
combination the Scripter already generates (e.g. a command that already writes to a file via
some other flag) — a small, bounded test matrix, not an open-ended risk.

---

## 8. Silent `OSError` swallow in `_read_raw_artifact_text`

**Realistic fix:** add one log line distinguishing "no signal found" from "couldn't read
evidence" — exactly what the audit's own remediation batch already recommends. Trivial,
no design decision needed, safe to batch with any other small fix.

## 9. Silent `continue` on unrecognized Tier-2 binary in `detect_candidates`

**Realistic fix:** same shape — a log line (or a lightweight counter/telemetry row) when a
command's `argv[0]` doesn't match any recognized shape, so "real output existed, nothing
looked at it" becomes visible in logs/telemetry instead of requiring another manual code
audit to rediscover. Doesn't need to *handle* every possible `argv[0]` shape (that's a much
bigger task) — just needs to stop being silent about skipping them.

## 10. Unbounded stdout/stderr buffer (real memory-growth risk, not truncation)

**Realistic fix:** a **large** size cap, not an aggressive one — this project's own
evidentiary-completeness mandate (`CLAUDE.md`'s unredacted-evidence directive, `FR-TOOL-08`)
means the cap should be a safety valve against true runaway (a multi-GB stream), not a normal-
case limit. A reasonable concrete number: cap at **50-100MB per subprocess**, with the
overflow point logged loudly and an explicit truncation marker written to the artifact
(matching the existing pattern already used elsewhere for degraded/fallback states) — this
would never trigger for any of this session's own real evidence (the largest real artifact
seen was katana's 2.5MB minified-JS dump, already two orders of magnitude under this cap)
while still bounding the actual failure mode (unbounded RAM growth from a legitimately
verbose tool like `nmap -p-` or a huge `ffuf` wordlist run before its own timeout fires).

**Effort/risk:** low — a size check in `executor.py`'s existing reader-thread loop, not a
new mechanism.

---

## 11. Adjudicator's "baseline/attack/diff" requirement may be structurally unsatisfiable

**Two realistic options, cheapest first — matching the audit's own recommendation to verify
empirically rather than guess:**

1. **Cheap, zero-new-capability option (try first):** add an explicit carve-out to
   `ROLE_BLOCK_ADJUDICATOR`'s prompt — "a single-request disclosure is sufficient evidence
   when the disclosure is self-evident and unambiguous (e.g. a JWT containing an admin role
   claim, a directly-downloadable credential file) — the baseline/attack/diff requirement
   applies to findings whose impact depends on a *comparison* (status-code-only IDOR,
   subtle behavioral differences), not to findings that are conclusive on their own." This is
   a prompt-text change only — no new infrastructure, testable in one live Adjudicator call
   against a reproduced version of this session's own real finding #1 (the SQLi→JWT).
2. **More expensive option, only if (1) proves insufficient in practice:** have the Scripter
   fire a genuine paired baseline request (same endpoint, no payload / different identity)
   alongside the attack request, and pass both to the Adjudicator. This doubles tool
   executions for every candidate and is a real scope increase — not worth building until a
   live test shows option 1 isn't enough.

**This is the same underlying capability gap as the "RCE via timing" half of issue 2** — a
real baseline-vs-attack comparison mechanism, if ever built for option 2, would also close
the timing-based RCE detection case. Worth building once, for both, if it turns out to be
needed at all.

---

## 12. Two independent Gate-1-Tier0 checks with no shared failure signal

**Already resolved** — Round 27 Item 3 (confirmed by direct diff review in the Pipeline-Flow-
Audit's own addendum) gave the round-progression breaker visibility into the Phase-4.2
re-check's rejections, closing the specific consequence this architectural note was about.
No further action needed unless a *new* decision-making path is added later that makes the
same mistake of only reading the first check's result.

## 13. `candidate_detection.py` vocabulary disconnected from `prompts.py` vocabulary

**Realistic fix:** a single shared Python constant (e.g. `council/vulnerability_classes.py`
exporting the 19-token list) that both `prompts.py` (the Strategist's controlled vocabulary)
and `candidate_detection.py` (which classes have a rule) import from — and a cheap CI test
that asserts every vocabulary token is either (a) mapped to a real detection rule, or (b)
explicitly listed in a documented "deliberately deprioritized as noise" exemption set (the
CORS-wildcard/missing-header precedent already established). This doesn't fix the §2
detection gap itself — it makes the *next* gap like it structurally impossible to introduce
silently, since adding a 20th vocabulary token without a rule or an explicit exemption would
fail the test immediately instead of requiring another full manual code audit to discover.

**Effort/risk:** low — a shared constants module and one test, not a behavior change.

---

## 14. CPU-only performance ceiling (~1.1-1.8 tok/s)

**This is a real hardware constraint, not a bug — the realistic mitigations are about
working within it, not eliminating it:**

- **Already correctly decided against:** GPU offload on this host's iGPU (confirmed slower,
  1.91 vs 2.50 tok/s, because the iGPU shares system RAM bandwidth with no dedicated VRAM) —
  nothing to change here, this is a settled, evidence-based finding.
- **A real, concrete, untested lever:** quantization level. This project already runs Q8_0
  for every model. A move to Q4_K_M or Q5_K_M would reduce memory-bandwidth pressure (the
  confirmed bottleneck, per the benchmarks report) and should measurably increase tok/s —
  at a real, non-zero quality cost that would need the same kind of ground-truth test-lab
  comparison already established for every other change in this project (does Q4 Strategist
  output still get genuine attack plans past Gate 1 at a similar rate, or does quality drop
  enough to matter). Worth a real, isolated A/B test before adopting — a concrete, bounded
  experiment, not a vague "try a smaller quantization" suggestion.
- **Not realistic given this project's own constraints:** anything requiring new hardware, or
  anything requiring a cloud API call for a council role (`05:SEC-DATA-01` local-only
  mandate) — ruled out by the project's own binding architecture, not re-litigated here.

## 15. GPU offload slower than CPU on this host's iGPU

**Already a settled, correctly-applied finding** — not an open issue requiring further
mitigation, included here only for completeness of the full catalog.

---

## Priority ordering, folding in what's realistic vs. merely possible

1. **Katana headless crawling** (issue 1) — single highest-leverage fix found this round;
   verifiable in minutes; closes the problem Mugheeraat's own report called the actual reason
   for zero confirmed findings.
2. **Wire `subjack`/`oob_listener` into candidate detection** (issue 2, SSRF/subdomain
   takeover specifically) — existing capability, just unconnected; closes 2 of 9 vocabulary
   gaps for near-zero new engineering.
3. **The remaining low-effort vocabulary rules** (SSTI, LFI, JWT, partial deserialization) —
   textbook deterministic signatures, same shape as existing rules.
4. **`GATE1_REJECTED` dashboard visibility** (issue 3) — trivial, same pattern as an existing
   field.
5. **Header-capture extension to the existing status-marker mechanism** (issue 7) — extends a
   proven function.
6. **Widen the Tier-1 SQL filter, paired with a sensitive-path pattern** (issue 6).
7. **Adjudicator prompt carve-out** (issue 11, option 1) — cheap, try before building anything
   real-baseline-capture-shaped.
8. **Hygiene batch** (issues 8-10, 13) — all low-risk, safe to batch together.
9. **Quantization A/B test** (issue 14) — a real, bounded experiment worth running, not urgent.
10. **Race conditions, RCE timing, prompt injection** (the harder slices of issue 2) — real new
    capability, lowest priority, defer until the cheaper 80% is done and re-measured against
    this session's own ground truth.
