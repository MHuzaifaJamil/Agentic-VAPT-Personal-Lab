---
name: whitebox-code-recon
description: Source-first reconnaissance methodology for engagements where we have code access (client VAPT with a repo handoff, source-available bug bounty scope, diff-review's full-repo sibling). Runs a structured pass over the codebase BEFORE any live testing — architecture map, entry-point inventory, schema harvest, security-pattern hunt, then taint-hunts per vuln class, then variant/patch-gap/differential analysis for zero-day discovery once known-pattern hunting is exhausted — so later phases test a known attack surface instead of guessing at one. Use when source is available and the engagement isn't diff-scoped (see diff-review for PR/commit-scoped review) and isn't a full black-box hunt (see bb-methodology/web2-recon for that).
---

# WHITE-BOX CODE RECON

Black-box recon finds *routes*. Source-first recon finds *sinks* — and tells
you, before you send a single request, which routes reach which sinks with
which guards in between. Do this pass first on any engagement where code is
in scope; it turns the live-testing phase into confirmation work instead of
discovery work.

This is a pre-recon phase, not a replacement for dynamic testing. Every
candidate this phase surfaces still needs a live PoC (or the
`triage-validation` `confirmed`/`ruled_out`/`open_proof_gap` discipline) before
it goes anywhere near a report.

---

## WHEN TO USE THIS VS. OTHER SKILLS

- **This skill** — full repo/codebase handoff, engagement start, no diff to
  scope to. Client VAPT with source access, source-available bug bounty
  program, or "here's the repo" at kickoff.
- **`diff-review`** — you're reviewing a specific PR/commit/branch, not the
  whole codebase. Use this skill's entry-point/schema harvest once at
  kickoff; use `diff-review` for every subsequent change.
- **`web2-recon`/`bb-methodology`** — no source access, black-box only. This
  skill assumes you can read the code; don't force it onto a target where you
  can't.
- **`cicd-security`** — the pipeline config itself is the target, not the
  application code the pipeline builds.

Once source recon below produces a candidate, hand it to `web2-vuln-classes`
or `web3-audit` for the exploitation detail and to `triage-validation` for
closure discipline — this skill is scope-and-mapping, not payloads.

---

## SCOPE RULE — WHAT'S REACHABLE

Not every line of source is a target. Before spending time on a file, ask:
**can a request the deployed server can receive reach this code path?**

**In scope:**
- Anything wired to an HTTP route, GraphQL resolver, WebSocket handler,
  message-queue consumer, scheduled job that processes external input, or
  webhook receiver.
- A shared library/helper/middleware that any of the above calls, even if the
  helper's own file has no route decorator.
- Config that changes runtime behavior for a reachable path (feature flags,
  env-driven auth toggles, CORS/CSP config).

**Out of scope (note and move past, don't audit deeply):**
- CLI-only scripts, one-off migration/seed scripts, build tooling
  (webpack/vite configs, Dockerfiles used only at build time), IDE/editor
  config, and test fixtures/mocks that never run in production.
- Dead code with no caller anywhere in the reachable graph — confirm with a
  reference search before writing it off, not on sight.

This rule exists because whitebox audits burn enormous time on code a
network attacker can never reach. When in doubt, trace one hop back toward an
entry point before deciding — "I couldn't immediately see how it's called"
is not the same as "confirmed unreachable."

---

## PHASE 1 — PARALLEL BASELINE PASS

Run these as independent passes (parallelize across sub-agents/tabs if your
tooling supports it — they don't depend on each other). Each produces a
written artifact you'll reuse in Phase 2, not just mental notes.

### 1. Architecture Scanner
Map the shape before the detail: language(s)/framework(s) per service,
monorepo vs. polyrepo, how services talk to each other (REST/gRPC/queue),
where auth is centralized vs. per-service, ORM/query layer in use, template
engine in use. This tells you which bug classes are even possible before you
go hunting for them (no template engine → skip SSTI; no raw SQL anywhere →
downgrade SQLi priority; shared JWT across microservices → treat token
exposure on one service as compromising the fleet, cf. shared-JWT findings on
past engagements).

```bash
# Quick framework/stack fingerprint
find . -maxdepth 3 -iname "package.json" -o -iname "requirements.txt" \
  -o -iname "Gemfile" -o -iname "pom.xml" -o -iname "go.mod" -o -iname "*.csproj"
grep -rl "express\|fastify\|django\|flask\|rails\|spring-boot\|laravel" --include="*.json" --include="*.txt" .
```

### 2. Entry Point Mapper
Build the full list of externally reachable entry points — this is your
attack-surface inventory, not a route dump. For each: method, path, auth
middleware present/absent, and the handler file:line.

```bash
# Route decorators / registrations (adjust per framework)
grep -rnE "@(Get|Post|Put|Delete|Patch)Mapping|router\.(get|post|put|delete|patch)|app\.(get|post|put|delete)|Route::" \
  --include="*.py" --include="*.js" --include="*.ts" --include="*.java" --include="*.rb" --include="*.php" .

# GraphQL resolvers
grep -rn "Resolver\|resolvers\s*=\|@Query()\|@Mutation()" --include="*.ts" --include="*.js" --include="*.py" .

# WebSocket / message-queue handlers
grep -rniE "\.on\(['\"](connection|message)|@RabbitListener|@KafkaListener|consumer\.subscribe" .
```

**Also harvest every schema file you can find** — OpenAPI/Swagger JSON/YAML,
GraphQL SDL, JSON Schema, protobuf `.proto` files — into a working
`schemas/` scratch directory. These are ground truth for parameter names,
types, and nullability that the live app's docs page often omits or hides
behind auth.

```bash
find . -iname "openapi*.json" -o -iname "openapi*.yaml" -o -iname "swagger*.json" \
  -o -iname "*.graphql" -o -iname "schema.gql" -o -iname "*.proto"
```

### 3. Security Pattern Hunter
Inventory the controls that exist, so Phase 2's taint-hunts know what a
"guard" looks like in this codebase and can tell present-but-broken apart
from genuinely absent.

```bash
# Auth/authz middleware and decorators
grep -rnE "@(RequireAuth|IsAuthenticated|login_required|Authorize|PreAuthorize|authenticate)" .
# Ownership/ACL check patterns worth knowing before Phase 2's authz hunt
grep -rniE "\.owner_id|current_user\.id\s*==|belongs_to\?|can\?\(|ability\.can" .
# Input validation / sanitization layers in use
grep -rniE "joi\.|zod\.|yup\.|class-validator|marshmallow|pydantic|ActiveModel::Validations" .
```

Write down, per framework/module, what the *sufficient* guard looks like —
Phase 2's authz section below depends on having a real example to compare
against, not a hypothetical one.

---

## PHASE 2 — TAINT HUNTS (per vuln class)

With the baseline from Phase 1 in hand, walk backward from each sink to its
sources. This is backward taint analysis, not a forward crawl: start at the
dangerous operation and ask "what reaches this, and through what, if
anything, that filters it?"

### Injection Sink Hunter (SQLi / command / SSTI)
```bash
# Raw query construction (string concat/interpolation, not parameterized)
grep -rnE "execute\(.*\+|query\(.*\+|f['\"].*SELECT|\.format\(.*SELECT" --include="*.py" --include="*.js" .
# Shell-out sinks
grep -rnE "exec\(|execSync\(|subprocess\.(call|run|Popen)|os\.system|Runtime\.getRuntime\(\)\.exec" .
# Template render sinks fed by request data
grep -rnE "render_template_string|Template\(.*request\.|ejs\.render\(.*req\." .
```
For each hit, trace backward: does the variable trace to a route parameter,
header, or body field with no parameterization/escaping between source and
sink? See `web2-vuln-classes` §7 (SQLi) and §14 (SSTI) for exploitation once
confirmed reachable.

### XSS Sink Hunter
Grep the DOM-sink list from `web2-vuln-classes` §3 (`innerHTML`,
`document.write`, `eval`, template `{{{unescaped}}}` blocks) and trace each
backward to its source the same way — a source-available pass finds the
sinks a black-box DOM crawl misses (sinks fed only by a code path a crawler
never triggers).

### SSRF Tracer
```bash
grep -rnE "requests\.(get|post)\(.*req\.|axios\.(get|post)\(.*req\.|fetch\(.*req\.|urlopen\(.*req\." .
```
Trace whether the URL/host component is attacker-influenced, and whether an
allowlist, protocol restriction, or private-IP block sits between source and
the outbound call. Cross-reference the SSRF sink taxonomy and bypass table in
`web2-vuln-classes` §4 once you have a candidate.

### Data Security Auditor
Grep for fields that get serialized/returned without a filter — over-fetching
ORM queries (`SELECT *` / `Model.find()` with no `.select()`), fields marked
sensitive in the schema harvest from Phase 1 but present in a response
serializer, and secrets in config/env files committed to the repo
(`grep -rniE "api[_-]?key|secret|password" --include="*.env*" --include="*.yml" --include="*.yaml" .` —
feed real hits into `secrets_hunter.sh` for a proper scan, this is just a
triage grep).

### Authorization Architecture Agent
Use this to build the map that `web2-vuln-classes`' authz backward-taint
procedure (see that skill's IDOR/BFLA sections) checks against: for every
entry point from Phase 1, which guard (if any) sits on it, and does that
guard match the "sufficient guard" pattern the Security Pattern Hunter
recorded in Phase 1 — or is it a weaker/different check than the sibling
routes use?

---

## LIVE-CORRELATION PASS (when Playwright/browser access is also available)

If you have both source and a running instance (dev/staging/client sandbox),
walk the live app's UI flows and correlate each one against the matching
backend code found above — this catches routes that exist in source but
whose actual runtime behavior (feature-flagged off, additional gateway-level
auth, a WAF rule) differs from what static reading suggested. Route Mapper
(what the UI actually calls), Authorization Checker (does the live response
match the static guard you found), Input Validator (does client-side
validation have a server-side twin), and Session Handler (how the live app
actually manages the session token you found being issued in source) are the
four angles worth walking; treat any live/source mismatch as a signal to dig
deeper, not as noise to ignore.

---

## PHASE 3 — VARIANT & PATCH-GAP ANALYSIS (when public vulns are exhausted)

Everything above finds vulnerabilities that match a known pattern. When
recon and the taint hunts turn up nothing and the target has a public CVE
history (its own, or in a shared dependency), the next-highest-yield source
of new bugs is the target's *own past bugs* and *own past fixes* — not
guessing blind.

**Variant analysis (highest-yield technique here):** take one of the
target's own past CVEs (or a CVE in a library it uses), extract the
*pattern* the patch addresses — not just the specific line, the shape of
the mistake — and grep the current codebase for the same pattern anywhere
the patch didn't reach. A fix applied to one endpoint/function rarely gets
applied to every sibling that shares the same root cause (see the Sibling
Rule in `rules/hunting.md`) — the unpatched sibling is your variant.

**Patch-gap analysis:** read the patch's actual filter/validation logic
line by line, not just its changelog description. Denylist-style fixes
almost always miss something: an encoding the filter didn't account for, an
equivalent function the patch didn't also cover, an alias/symlink the check
didn't resolve. The gap between what the patch *says* it fixes and what it
*actually* covers is a candidate on its own, and matters even more once you
already have one variant confirmed via the technique above.

**Differential testing:** when two components in the pipeline parse or
validate the same input independently (a WAF vs. the backend, a schema
validator vs. the code that actually executes on the data, a proxy vs. the
origin server), look for a case where they disagree about what the input
means. That disagreement is the root cause behind smuggling and most
validator-bypass bugs — see `web2-vuln-classes`'s Semantic Confusion class
and HTTP Request Smuggling class for the exploitation detail once you've
spotted a disagreement in source.

**N-day weaponization (when an advisory exists but no public PoC does):**
diff the vulnerable version against the patched version directly (source
diff if available; binary diff / bindiff-style comparison for compiled
components) to reconstruct what the advisory is actually describing, then
verify against a local copy of the target software before trying it
live. A vendor's own regression test added alongside the patch is
frequently a ready-made proof of the original bug.

**Sanity checks specific to this phase:** every candidate found this way
still needs the same proof standard as any other finding —
`triage-validation`'s closure discipline applies unchanged, and a variant
you found by pattern-matching a public CVE is *not* itself confirmed just
because the original CVE was real (see `triage-validation`'s "search result
is not a vulnerability" note under Confirming a Candidate).

---

## OUTPUT

Phase 1 + Phase 2 should leave you with:
- An entry-point inventory (method, path, guard present/absent, file:line)
- A `schemas/` directory of harvested API schemas
- A short list of taint-hunt candidates, each with source, sink, and the
  guard (if any) in between

Hand every candidate to `triage-validation`'s closure discipline before it
becomes a finding — a complete source → broken-control → sink → impact trace
is reportable at reduced confidence when the environment can't be stood up
(same rule as `diff-review`), but live PoC is still preferred whenever the
target is reachable.
