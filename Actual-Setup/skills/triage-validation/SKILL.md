---
name: triage-validation
description: Finding validation before writing any report — closure discipline (confirmed/ruled_out/open_proof_gap) for mid-hunt candidates including the baseline/attack/diff confirmation procedure, the control-vs-constraint test, and a 4-level confidence ladder for blocked exploit attempts, 7-Question Gate (all 7 questions), 4 pre-submission gates, always-rejected list, conditionally valid with chain table, CVSS 3.1 quick reference, severity calibration ("usually NOT high/critical" list + acceptance checklist), severity decision guide, report title formula, 60-second pre-submit checklist. Use DURING the hunt to close out candidates honestly, and BEFORE writing any report. One wrong answer = kill the finding and move on. Saves N/A ratio.
---

# TRIAGE & VALIDATION

One wrong answer = STOP. Kill it. Move on.

> "N/A hurts your validity ratio. Informative is neutral. Only submit what passes all 7 questions."

---

## CLOSURE DISCIPLINE — WHILE YOU HUNT, NOT JUST AT REPORT TIME

Every lead you open — a scanner hit, a hunch, a grep match, a weird response —
ends in exactly one of three states. "I moved on" is not one of them.

**`confirmed`** — you have a working PoC, or (source-available work) a complete
source → broken-control → sink → impact trace you've verified is reachable.
This is what goes to the 7-Question Gate below.

**`ruled_out`** — you can name the *specific* control that makes it safe, at a
specific location, and you've checked that control actually runs on the
attacker's path. Test: complete this sentence with real detail — *"This is
safe because `<control>` at `<endpoint/file:line>` `<does what>` before
`<the thing I was worried about>`, on every path I can reach it from."* If you
can't fill that in, you are not in `ruled_out` — you're in the next state.

**`open_proof_gap`** — plausible, you couldn't confirm it, and you also
couldn't name a control that rules it out. This is a normal, legitimate
outcome. Write it down (a note, a todo, a line in your hunt log) and come
back to it if time allows — do not silently drop it just because it's easier
to feel done. An `open_proof_gap` quietly relabeled as "probably fine" is
exactly how real bugs get missed.

### What does NOT count as ruling something out

Each of these *feels* like a reason to stop looking. None of them is one:

- **"The framework/ORM/library handles that."** Confirm the specific call,
  with the specific arguments, in the specific context — an HTML escaper does
  nothing in a JS-string context; a SQL identifier quoter isn't a value
  quoter; a path-join isn't a containment check.
- **"There's a check on the normal flow."** A guard on the UI button, the
  common route, or the web flow says nothing about the mobile API, the
  legacy endpoint, the admin alias, or the batch/webhook path that reaches
  the same backend action.
- **"The check runs... somewhere."** Validation *after* a redirect,
  canonicalization *after* a path is already used, an ownership check *after*
  the object was already fetched — these are ordering bugs, not controls.
  The control has to run before the dangerous effect, not just exist.
- **"It's behind a WAF/CAPTCHA/rate limit."** Those are speed bumps, not
  proof of safety — note them as friction, keep testing for a bypass before
  you rule anything out because of them.
- **"I couldn't find where this is called from."** Missing information is
  missing information, not evidence of safety. That's an `open_proof_gap`.
- **"It would take too long to set up."** A hard environment (need creds you
  don't have, service won't start) is a reason to write it down and move to
  the next candidate — not a reason to mark it clean.
- **One safe sibling.** If `/api/v1/orders/:id` checks ownership and
  `/api/v2/orders/:id` doesn't, the v1 check proves nothing about v2. Every
  reachable instance stands or falls on its own — don't let a correctly
  guarded sibling talk you out of testing the others.

### What DOES rule something out

- You sent the exact payload that should work if the bug were real, and it
  demonstrably failed — and you understand *why*, not just that you got a 403.
- You can point at the control, at a location, and show it runs on every path
  you can reach the sink from, before the effect happens, with no bypass.
- Send a negative control alongside it: the payload that *should* be blocked,
  and a benign variant that *should* succeed. Two data points beat one.

**Build the negative control as a matched twin, not an unrelated benign
example.** The strongest negative control is the real payload/credential/
header with exactly one property changed — not a completely different,
obviously-safe request. Modify the smallest part that makes the difference
matter, and preserve everything else (format, prefix, length) so the twin
travels the identical code path and only the property under test differs:
a SQL boolean-bypass payload's twin flips `'1'='1'` to `'1'='2'` (same
syntax, opposite truth value); a leaked-credential's twin rotates a few
characters in the *middle* of the secret, not the prefix a provider uses
for routing (`sk-`, `ghp_`), so it still reaches the same validation
endpoint; a trusted-header bypass's twin is the identical request with that
one header removed. An unrelated "obviously benign" request proves much
less than a twin that differs in only the one property you're testing.

### Confirming a Candidate — Baseline / Attack / Diff

The mirror procedure for moving a candidate INTO `confirmed` (the negative
control above is for ruling one OUT): send a **baseline** request (normal,
unmodified — establishes what "expected" looks like for this endpoint),
then the **attack** request (your actual payload/identity swap/bypass), then
**diff** the two responses. A candidate is only `confirmed` when the diff
shows a concrete, reproducible difference that maps directly to the claimed
impact — a different status code alone is not enough; the response body,
not just the code, has to show the other user's data, the privileged action
succeeding, or the payload executing.

This is the same discipline as Q1's "exact HTTP request" requirement in the
7-Question Gate below — baseline/attack/diff is how you get the evidence
Q1 asks you to write down, not a separate step you do afterward.

**Name the check that earned `confirmed`, don't just assert it.** Writing
"confirmed" in your notes or a report without saying *which* diff/control
proved it is the same failure mode as a scanner flagging something with no
way to tell if it's real. State it in one line: "confirmed via baseline/
attack/diff — attack request returned victim's email+address, baseline
returned attacker's own" or "confirmed via matched-twin control — real key
authenticated, corrupted twin got 401." If you can't write that sentence,
you don't have a confirmation yet, you have a candidate.

**Reproduce N/N before calling anything confirmed that could be flaky** —
race conditions, timing-based oracles (blind SQLi/SSRF via response delay),
and anything relying on a network callback (OAST/DNS) get a false positive
from network jitter or a lucky race far more easily than a plain request/
response diff does. Re-run 2-3 times and report the ratio (e.g. "reproduced
3/3") rather than treating one successful attempt as proof. A candidate
that worked once and failed on retry is an `open_proof_gap`, not
`confirmed` — write down what you saw, don't round a flaky result up.

Before writing up a confirmed candidate, dedupe against your own hunt log:
same endpoint + same attack vector you already logged as `confirmed` or
`ruled_out` is not a second finding — update the existing entry instead of
creating a near-duplicate.

**A search result is not a vulnerability.** This applies specifically to
CVE/PoC/writeup lookups (`/intel`, a public exploit-db entry, a blog post
describing the same framework/version): finding that a component matches a
known CVE, or that someone else's writeup describes this exact class of
bug, is a lead — `tentative`, not `confirmed`. The public PoC has to
actually run against *this* target and produce the baseline/attack/diff
evidence above before it counts. The same applies to a variant found via
`whitebox-code-recon`'s pattern-matching against one of the target's own
past CVEs — matching the pattern tells you where to look, it doesn't
substitute for firing the exploit.

### The Control-vs-Constraint Test

When an attempt gets blocked, ask one sharp question before you write it off:
**is this a security control designed to stop the attack, or an external
operational constraint that happens to be in the way right now?**

The difference decides whether you can mark something `ruled_out`:

- **A security control** (auth check, ownership filter, allowlist, WAF rule
  actually built to catch this class) blocking the exact attack you tried is
  real evidence — this is what `ruled_out` requires above.
- **An external operational constraint** (a firewall rule scoped to your
  current IP but not the class of attacker who'd actually exploit this, a
  test environment with a feature disabled that's live in prod, a rate limit
  that only slows you down, your own tooling failing to reach an endpoint) is
  not evidence the *vulnerability* is safe — it's evidence your *current
  attempt* didn't get through. That's an `open_proof_gap`, not `ruled_out`.

Use a 4-level confidence ladder to describe how far you actually got, instead
of collapsing everything into a binary pass/fail:

```
1. Weakness Identified  — the flaw exists in theory (source trace, missing
                           check found), no exploitation attempted yet
2. Partial Bypass        — some part of the defense fails, but you haven't
                           reached the actual impact (e.g. filter bypassed,
                           but the sink itself hasn't fired yet)
3. Confirmed             — full path proven, sink fired, impact demonstrated
4. Critical              — impact demonstrated AND it's severe/broad
                           (cross-tenant, admin-equivalent, mass data)
```

Report the ladder level honestly. A `Partial Bypass` that stalls because of
an operational constraint (not a real control) stays an `open_proof_gap` at
that level — don't round it up to `Confirmed` because you're confident it
*would* work, and don't round it down to `ruled_out` because you personally
couldn't push it further right now.

Bring the honest state into the 7-Question Gate: `confirmed` candidates go to
Q1 below, `open_proof_gap` candidates are your "needs more time" list — don't
let them silently disappear, and don't let them get written up as if they were
`confirmed`.

---

## THE 7-QUESTION GATE

Ask IN ORDER. One wrong answer = STOP immediately.

---

### Q1: Can an attacker use this RIGHT NOW, step by step?

Complete this template:
```
1. Setup:   I need [own account / another user's ID / no account]
2. Request: [exact HTTP method, URL, headers, body — copy-paste ready]
3. Result:  I can [read / modify / delete] [exact data shown in response]
4. Impact:  The real-world consequence is [account takeover / PII read / money stolen]
5. Cost:    Time: [X minutes], Capital: [$0 / $X subscription required]
```

**If you CANNOT write step 2 as a real HTTP request → KILL IT.**

---

### Q2: Is the impact on the program's accepted impact list?

Go to the program page. Find "Vulnerability Types" or "Out of Scope."

Common tiers:
- **Critical**: Any-user ATO without interaction, RCE, SQLi with data exfil, admin auth bypass
- **High**: Mass PII exfil, privilege escalation, internal SSRF with data, stored XSS all users
- **Medium**: IDOR on specific user non-critical data, XSS on sensitive page requiring click
- **Low**: Non-sensitive info disclosure, clickjacking with PoC

**If your bug maps to a listed exclusion → KILL IT.**

---

### Q3: Is the root cause in an in-scope asset?

Confirm:
- Vulnerable domain is on the in-scope list (not `*.internal.target.com`)
- It's a production asset (not staging/dev unless explicitly in scope)
- It's not a third-party service the company just uses (not Stripe, Salesforce, Google Auth)

**If out-of-scope → KILL IT.**

---

### Q4: Does it require privileged access that an attacker can't realistically get?

- "Admin can do X" = centralization risk = **KILL IT** (on 99% of programs)
- "Non-admin can do X that only admin should do" = valid
- "Requires physical access / MFA device" = usually invalid
- "Requires compromised victim account to work" = questionable, low severity at best

---

### Q5: Is this already known or accepted behavior?

Search:
1. Program's HackerOne/Bugcrowd disclosed reports: Ctrl+F endpoint name + bug class
2. GitHub issues on target repo: `is:issue label:security ENDPOINT_NAME`
3. Changelog/CHANGELOG.md — does it mention this behavior?
4. API docs / design docs — is it documented as intended?

**If acknowledged/design decision → KILL IT.**

---

### Q6: Can you prove impact beyond "technically possible"?

- XSS → show actual cookie theft or session hijack, not just `alert(1)` or `alert(document.domain)`
- SSRF → hit an internal endpoint that returns data, not just DNS ping
- SQLi → show actual data exfil from a real table, not just error message
- IDOR → show actual other-user's data in response, not just a 200 status code

**If you can only show "technically possible" → DOWNGRADE severity, not kill.**

---

### Q7: Is this a known-invalid bug class?

Check the NEVER SUBMIT list below. If it's on this list without a chain → **KILL IT.**

---

### Q8: Identity check — which session found this, and does it survive?

For any finding made under an authenticated hunt, record the answer to each:

```
1. Session ID:        [12-char BBHUNT_SESSION_ID hash from audit.jsonl]
2. Identity:          [low-priv user A / high-priv user B / API key / etc.]
3. Anonymous repro:   Does the same request work with NO auth header?
4. Cross-identity:    Does it work under session B with the same data scope?
5. Stale-cred repro:  Does a logged-out / expired session still get the data?
```

Why this matters:
- **IDOR / BOLA**: must work with session A reading session B's data — if it
  only works with no auth, that's "missing auth" not IDOR (different bug,
  different severity).
- **Priv-esc**: must work with low-priv session reading high-priv data — if
  both sessions can already see it, no bug.
- **Auth bypass**: must work *without* a valid session — if it stops working
  when you log out, you've found a permissions issue, not a bypass.
- **Always check both directions**: a finding that only reproduces under
  one identity is often a real, scoped permission boundary, not a vuln.

`audit.jsonl` entries are tagged with `session_id`. Re-run the request
under each identity and confirm the bug holds before writing the report.
This is the most common reason "confirmed IDOR" findings come back as N/A.

If you cannot answer the identity questions, treat the finding as unproven.
Blank answers auto-fail on auth-related findings.

---

---

## 4 PRE-SUBMISSION GATES

Run in sequence. ALL 4 must PASS.

### Gate 0: Reality Check (30 seconds)
```
[ ] Bug is REAL — confirmed with actual HTTP requests, not code reading alone
[ ] Bug is IN SCOPE — checked program scope page explicitly
[ ] Reproducible from scratch — can reproduce starting from fresh session
[ ] Evidence ready — screenshot, response body, or video
```

### Gate 1: Impact Validation (2 minutes)
```
[ ] Can answer: "What can attacker DO that they couldn't before?"
[ ] Answer is more than "see non-sensitive data" (unless program pays for info disclosure)
[ ] Real victim: another user's data, company's data, financial loss
[ ] Not relying on victim doing something unlikely
```

### Gate 2: Deduplication Check (5 minutes)
```
[ ] Searched HackerOne Hacktivity for this program + similar bug title/endpoint
[ ] Searched GitHub issues for target repo
[ ] Read most recent 5 disclosed reports for this program
[ ] Not a "known issue" in their changelog or public docs
[ ] Google: "TARGET_NAME ENDPOINT_NAME bug bounty"
```

### Gate 3: Report Quality (10 minutes)
```
[ ] Title: [Bug Class] in [Endpoint] allows [actor] to [impact]
[ ] Steps to Reproduce: copy-pasteable HTTP request
[ ] Evidence: screenshot/video of actual impact (not just 200 status)
[ ] Severity: matches CVSS 3.1 score AND program's severity definitions
[ ] Remediation: 1-2 sentences of concrete fix
[ ] NEVER used "could potentially" or "may allow"
```

---

## NEVER SUBMIT LIST

Submitting these destroys your validity ratio.

```
Missing CSP / HSTS / security headers
Missing SPF / DKIM / DMARC
GraphQL introspection alone (no auth bypass, no IDOR demonstrated)
Banner / version disclosure without working CVE exploit
Clickjacking on non-sensitive pages (no sensitive action PoC)
Tabnabbing
CSV injection (no actual code execution shown)
CORS wildcard (*) without credential exfil proof of concept
Logout CSRF
Self-XSS (only exploits own account)
Open redirect alone (no ATO or OAuth theft chain)
OAuth client_secret in mobile app (known, expected)
SSRF DNS callback only (no internal service access or data)
Host header injection alone (no password reset poisoning PoC)
Rate limit on non-critical forms (search, contact, login with Cloudflare)
Session not invalidated on logout
Concurrent sessions
Internal IP in error message
Mixed content
SSL weak ciphers
Missing HttpOnly / Secure cookie flags alone
Broken external links
Autocomplete on password fields
Pre-account takeover (usually — very specific conditions required)
```

---

## COMMON N/A CLASSES — KILL SIGNALS

These pass basic gut-check but consistently come back N/A. Each row has a **specific signal** that tells you to kill it *before* writing the report.

| Finding | Why it N/As | Kill signal — if you see this, stop |
|---|---|---|
| Reflected XSS | CSP blocks execution; sandbox context; no session access | Dalfox found `alert(1)` but no cookie in response; `Content-Security-Policy` header present |
| SSRF — DNS callback only | No internal data reached; programs require HTTP response with data | Interactsh/Collaborator got DNS ping but no HTTP reply with internal content |
| IDOR — own data only | Attacker == victim; no cross-account access proven | User ID in response matches your own test account |
| SQLi — error message only | WAF filtered or error is cosmetic; no data exfiltrated | Got DB error string but no actual table rows returned |
| CORS wildcard `*` | `*` blocks `withCredentials`; no PII actually exfiltrated | `Access-Control-Allow-Credentials: true` absent; credentialed request returns 403 |
| Rate limit missing — non-sensitive endpoint | Program only pays for rate-limit on auth/payment/OTP surfaces | Endpoint handles search, contact form, or sits behind Cloudflare |
| Nuclei `info` template match | Version detection, not exploitation | Template severity is `info`; no CVE PoC executed against live service |
| MFA rate limit (no lockout) | Impact depends on OTP brute-force succeeding — it usually doesn't | 15 requests returned 200 but no OTP code was accepted |
| Open redirect alone | Redirect is informational without token theft chain | No OAuth `redirect_uri` parameter; no auth code or token in the redirected URL |
| Auth bypass — admin precondition | Requires compromised admin to trigger; attacker can't get there | "Admin can do X on behalf of user" — attacker must already be admin |
| XSS via `alert(document.domain)` | Not proof of session theft | PoC shows domain popup only; no `document.cookie` exfil, no event listener |
| SAML metadata exposed | Disclosure only — aids attack but is not standalone impact | No private key or signing cert extracted; metadata is publicly documented by IdP |

**Decision rule:** if your finding matches a kill signal → classify as `[INFORMATIONAL]`, do **not** run `/validate`, move on.

---

## CONDITIONALLY VALID — CHAIN REQUIRED

Build the chain first, prove it works end to end, THEN report.

| Standalone Finding | Chain Required | Valid Result |
|---|---|---|
| Open redirect | + OAuth redirect_uri → auth code theft | ATO (Critical) |
| Clickjacking | + sensitive action + working PoC | Medium |
| CORS wildcard | + credentialed request exfils user PII | High |
| CSRF | + sensitive action (transfer funds, change email, delete account) | High |
| Rate limit bypass | + OTP/reset token brute force succeeds | Medium/High |
| SSRF DNS-only | + internal service access + data returned | Medium |
| Host header injection | + password reset email uses injected host | High |
| Prompt injection | + reads other user's data (IDOR) | High |
| S3 bucket listing | + JS bundles contain API keys or OAuth secrets | Medium/High |
| Self-XSS | + CSRF to trigger it on victim without their knowledge | Medium |
| Subdomain takeover | + OAuth redirect_uri registered at that subdomain | Critical |
| GraphQL introspection | + auth bypass mutation or IDOR on node() | High |

---

## CVSS 3.1 QUICK REFERENCE

### Common Score Examples

| Finding | Score | Severity | Vector |
|---|---|---|---|
| IDOR read PII, any user, auth required | 6.5 | Medium | AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N |
| IDOR write/delete, any user | 7.5 | High | AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N |
| Auth bypass → admin panel | 9.8 | Critical | AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H |
| Stored XSS → cookie theft, stored | 8.8 | High | AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:L/A:N |
| SQLi → full DB dump | 8.6 | High | AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N |
| SSRF → cloud metadata | 9.1 | Critical | AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:N |
| Race → double spend | 7.5 | High | AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:N |
| GraphQL auth bypass | 8.7 | High | AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N |
| JWT none algorithm | 9.1 | Critical | AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H |

### Metric Quick Guide

| What you have | Metric | Value |
|---|---|---|
| Exploitable over internet | AV | Network (N) |
| No special timing or race | AC | Low (L) |
| Free account needed | PR | Low (L) |
| No login needed | PR | None (N) |
| Admin needed | PR | High (H) |
| No victim action | UI | None (N) |
| Victim must click | UI | Required (R) |
| Reads all data | C | High (H) |
| Reads some data | C | Low (L) |
| Modifies all data | I | High (H) |
| Crashes service | A | High (H) |
| Affects only app | S | Unchanged (U) |
| Affects browser/OS/cloud | S | Changed (C) |

---

## SEVERITY CALIBRATION

CVSS gives you a number once you've picked the metrics. This is about
picking them honestly, before you fill in the vector — severity is a
conclusion you reach after validation, not an opening bid.

**The test that matters:** would a triager at a program that pays real bounties
accept this as High/Critical, or would they need to accept a chain of
assumptions first? If it's the second one, it isn't High. Rate the weakness
you actually proved, not the worst case you can imagine chaining it into.

### Usually NOT High/Critical — even though they look scary

Each of these gets over-claimed constantly. They need unusual, *demonstrated*
circumstances to clear Medium:

- Self-XSS and clickjacking on non-sensitive actions
- Missing security headers, cookie attribute nits, TLS configuration issues
- Open redirect on its own (no OAuth/token theft chain)
- "Could matter if chained with several unproven assumptions"
- Anything that already requires admin/shell/physical access to trigger — if
  the attacker already has that, the finding adds little
- Session weaknesses that require the attacker to already hold a victim
  secret (a stolen cookie, an intercepted link) — unless the *same* finding
  shows how to obtain that secret, this is usually Low/Medium
- Enumeration that only confirms an account/domain/version exists

### Acceptance checklist for High/Critical

All of these must be true. If any one isn't, drop a severity level:

```
[ ] Attack path is realistic and in scope — not lab-only, not dependent on
    an unproven prior compromise
[ ] The attacker position required (auth level, preconditions) is one an
    attacker can actually reach — PR/AC in your CVSS vector reflect that
    honestly, not optimistically
[ ] Impact is demonstrated, not asserted — C:H/I:H means proven broad
    read/write, not one record
[ ] You ran the closure-discipline pass above and found no constraint that
    meaningfully limits exploitation (or you can explain why it doesn't hold)
[ ] You have concrete reachability evidence, not an assumption about how the
    app is deployed
[ ] You would defend this exact rating to the program's triager, not just to
    yourself
```

### Downgrade, don't delete

A finding that turns out to be constrained (internal-only reachability, a
narrow precondition, requires a privileged role) gets a *lower severity* — not
a silent drop. Say so explicitly in the report. Missing evidence about
deployment/exposure lowers your **confidence**, not the severity floor — don't
treat "I couldn't confirm this is internet-facing" as if it were "this is
internal-only." When your gut severity and the computed CVSS disagree,
re-check `privileges_required`, `attack_complexity`, and the impact triad —
usually one of those was set optimistically. Fix the metric; don't override
the score.

---

## KILL FAST RULES

The goal is to QUICKLY disqualify bad leads so you hunt real bugs:

1. **5-minute rule**: If you can't fill in Q1's template in 5 minutes → move on
2. **Precondition count**: More than 2 preconditions simultaneously required → kill it
3. **Impact test**: "What does attacker walk away with?" — if nothing tangible → kill it
4. **Admin bypass**: "Admin can do X" is NEVER a bug → kill it immediately
5. **Design doc test**: If it's documented behavior → kill it immediately
6. **Rabbit hole signal**: 30+ min on Q6 with no reproducible PoC → kill it

---

## ANTI-PATTERNS THAT LOSE MONEY

```
Writing a report before confirming the bug exists (most common)
Submitting theoretical impact without proof
"The API returns more fields than necessary" (sensitivity matters — is it actually sensitive?)
Chaining A+B into one report when they're separate bugs (two separate payouts)
Reporting B saying "similar to A in my other report" — fresh Gate 0 for every bug
Overclaiming severity — triagers trust you less next time
Under-describing impact — triager doesn't understand why it matters
```
