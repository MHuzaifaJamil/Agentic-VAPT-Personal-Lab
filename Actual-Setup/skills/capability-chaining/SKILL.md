---
name: capability-chaining
description: Framework for deriving novel exploit chains when no known A→B pattern fits — express every finding as a capability primitive (read/write/exec/ssrf/sqli/cred/idor/etc.), treat RCE as one of a small set of primitive-combination equations rather than a single vulnerability, and search forward/backward through the capability graph to find a path from what you have to what you need. Use when you have several low/medium findings and no single high-severity bug, or when `chain-builder`'s known-pattern table has no entry that fits.
---

# CAPABILITY-PRIMITIVE CHAINING

`chain-builder`'s A→B table covers *known* chain patterns (IDOR→auth bypass,
SSRF→cloud metadata, open redirect→OAuth theft). This skill is for when
nothing in that table applies — several low/medium findings, no single big
vulnerability, and the target-specific chain that connects them doesn't
exist in any writeup because you have to derive it on the spot.

---

## THE CORE REFRAME

RCE (or any high-impact goal) is not one vulnerability — it's an emergent
property of a **set of capabilities** coming together. Without a single big
hole, several info-level or low-severity findings can still add up to code
execution. The mental shift: stop asking "did I find an RCE/deserialization/
upload bug?" and start asking "what capabilities do I currently have, and
what am I missing to reach the goal?"

**Express every finding as a primitive**, not as a named vuln class:
```
read(path)        — can read an arbitrary or specific file/resource
write(path)       — can write/overwrite a file or resource
exec(cmd)         — can run an OS command or equivalent
ssrf(url)         — can make the server issue an outbound request
sqli              — can inject SQL
redirect(url)     — can control where the app redirects
eval_expr         — can get server-side expression/template evaluation
idor(id)          — can access another user/tenant's object by ID
cred(svc, priv)   — hold valid credentials for a service, at some privilege
coerce_auth       — can force a privileged party to authenticate to you
write_acl         — can modify an access-control entry
```

## RCE AS A SET OF EQUATIONS, NOT ONE BUG

RCE only needs to satisfy **any one** of these — decompose the goal into
whichever equation is closest to what you already hold, then go acquire the
missing primitive(s):

| # | Equation | Notes |
|---|---|---|
| A | `write(path)` + path is reachable by an execution engine | Web shell drop, cron-read directory, a file the app later `include()`s |
| B | control over config/env + config points at your code | Poisoned include path, `NODE_OPTIONS`, a webhook URL used as a code source |
| C | reach an admin/management panel + panel has a built-in "run a command" feature | **This isn't a vulnerability — it's a legitimate feature you weren't supposed to reach.** Cron/job runners, plugin installers, "test connection" tools that shell out |
| D | `cred(svc, priv)` + service exposes a legitimate execution entry point | Abusing a real feature with real (but improperly scoped) credentials — CI runner, DB console, management API |
| E | `read(*)` + read reaches credentials + those credentials reach a login/execution surface | Config file leak → DB password → DB has `INTO OUTFILE`/UDF → shell |
| F | control over data + that data flows into a dangerous sink | `eval`, a template engine, a SQL string, a deserializer — same root cause as SSTI/SQLi/deserialization, framed as a primitive |

## TRANSLATING "LOW SEVERITY" FINDINGS INTO PRIMITIVES

The habit this framework replaces: dismissing a finding as "just an info
leak" or "just an SSRF with no direct data" because it doesn't look like a
named critical bug on its own. Translate it into what it actually grants:

| Low-severity finding | Primitive(s) it grants | Feeds equation |
|---|---|---|
| Info disclosure (`.git`, backup file, stack trace) | `read` of source/config/paths | B, E, F |
| LFI / arbitrary file read | `read` → often config/credentials | E; or `write` via log/session poisoning → A |
| SSRF, even GET-only with no visible response | `ssrf(url)` → internal Redis/Consul/K8s API/cloud metadata | C (internal admin surface), D (metadata → cloud creds) |
| Weak/default/reused credentials | `cred(svc, priv)` → check what that account's panel can *do* | C |
| CORS misconfig / CSRF / XSS | borrow an authenticated admin's browser to hit a privileged feature | C |
| Upload restricted by extension only | `write(path)` via path traversal, parser-confusion, or a `.htaccess`/config write | A, B |
| SQLi, even read-only | `read` of hashes/secrets, or `INTO OUTFILE` | E, or A if the DB can write files |
| Server-controllable template field | SSTI = `eval_expr` | F |
| Prototype pollution | polluted property read downstream | F |

## STATE-SPACE SEARCH — DERIVING A CHAIN THAT ISN'T IN ANY TABLE

Treat the engagement as a search problem: **state** = the set of primitives
you currently hold, **actions** = using primitives to unlock new ones,
**goal** = the impact you're trying to reach.

**Forward search** (when you have several findings and want to see what
they add up to):
- For every primitive you hold, ask "what does this unlock?"
- For every *pair* of primitives, ask "what do these unlock together?"
  (`read`+`write` → edit a config; `ssrf`+internal Redis → `exec` via Redis
  module load or cron-key injection; `sqli`+`FILE` privilege → web shell;
  `coerce_auth`+relay → domain-level `exec`; `idor`+mass-assignment →
  modify another user's role to admin)

**Backward search** (when you're stuck and want a direction — use this
first when nothing obvious is unlocking):
- Fix the goal (e.g. `exec(cmd)`), pick the equation from the table above
  that's closest to your current state, and work backward: which single
  primitive, if you had it, would complete that equation? That becomes your
  next sub-goal — go hunt specifically for it instead of hunting blind.

**Cross-domain chaining** — don't stop the search at one system's boundary.
A primitive earned in the web app (`ssrf`) can unlock a primitive in the
cloud layer (`cred` via metadata service), which unlocks a primitive in a
completely different internal service. The chain doesn't have to stay
inside the class of bug you started with.

---

## HOW THIS FITS THE REST OF THE TOOLKIT

- `chain-builder` agent — use its A→B table first (fast, known patterns);
  reach for this skill when nothing in that table fits, or when you want
  to double-check that a "no big vuln found" target really has nothing to
  chain rather than just nothing *tabulated*.
- Every hop in a derived chain still needs the same proof standard as any
  other finding — run it through `triage-validation`'s closure discipline
  (`confirmed`/`ruled_out`/`open_proof_gap`) and the baseline/attack/diff
  confirmation procedure. A clever chain on paper that you haven't actually
  fired end-to-end is a hypothesis, not a finding.
- `web2-vuln-classes`'s per-class "Chain Escalation" tables are the
  pre-tabulated version of exactly this idea for that one class — this
  skill is what to reach for once you're combining primitives *across*
  classes.
