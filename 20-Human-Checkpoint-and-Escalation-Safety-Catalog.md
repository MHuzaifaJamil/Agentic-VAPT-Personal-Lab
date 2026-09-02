# Human-Checkpoint & Escalation Safety Catalog — Autonomous Agentic VAPT System

**Purpose:** a single, dedicated inventory of every mechanism in this system that
requires a live human confirmation before a specific action proceeds — what triggers
it, exactly where it's implemented, what happens if it's bypassed or misused, and why
it exists. This document exists because `19-Extended-Capability-Domains.md`'s mining
sweep surfaced four techniques whose *source* material's real safety property is a
human confirming something in real time — a property this system's otherwise
fully-autonomous, no-pause design (`FR-COUNCIL-11`, decision #13) did not previously
have anywhere. Rather than scatter this reasoning across four separate domain
sections, it is collected here once, in full, and cross-referenced from `01`/`03`/`19`.

**This document does not duplicate the requirement text itself** — `01`'s
`FR-CHECKPOINT-01..05` and `03`'s `DR-SCHEMA-18` (`checkpoint_events`) are the
authoritative requirements. This document is the *why*, at the depth the four
individual domain-section entries in `19` didn't have room for.

---

## 1. The mechanism itself, in one place

A deterministic classifier (`security/checkpoint_gate.py`, per `13`'s `IAB-LAYOUT`)
tags every proposed task against a **fixed, closed list** of four action classes.
Matching one, with its corresponding pre-engagement opt-in flag set, does not execute
the task — it writes a `checkpoint_events` row, transitions the engagement to
`PAUSED_AWAITING_CHECKPOINT`, and the orchestrator process **exits** (same
resource-efficiency philosophy as the existing `pause` mechanism — nothing idles
waiting). The engagement stays paused, indefinitely, until the operator runs
`vaptctl approve-checkpoint` or `vaptctl deny-checkpoint` — there is deliberately no
auto-timeout-to-approve anywhere in this mechanism, unlike this system's
resource-safety timeouts (`FR-GATE-10`'s 5-second settle-gate, the tiered subprocess
timeouts in `TP-TIMEOUT`) — silence is not consent for any of these four classes.

This is layered **on top of**, not instead of, the existing opt-in-flag system
(`FR-TOOL-06a`): the flag is the pre-engagement config-time decision ("I might need
this category at all this engagement"); the checkpoint is the live, per-instance
decision ("yes, do this specific one, right now"). Neither substitutes for the
other — a system that only had the flag would be reproducing the exact gap this
catalog exists to close.

## 2. The four action classes, in full

### 2.1 `ANTI_FORENSICS`

- **Where it comes from:** `Actual-Setup/skills/opt-in-advanced-techniques/SKILL.md`
  §2, read directly (not delegated to a research fork, given its sensitivity).
- **What it covers:** MITRE ATT&CK T1070 (Indicator Removal — log
  clearing/editing, shell-history clearing, timestomping), T1564 (Hide Artifacts —
  memory-resident execution favored over disk artifacts), T1622 (Debugger/EDR
  Evasion — checking for blocking monitoring before escalating aggressiveness).
  Referenced by ATT&CK technique ID in `19`, not reproduced as ready-to-run
  commands, so this system's documentation stays current against ATT&CK's own
  regularly-updated detail rather than calcifying a specific 2026-era command that
  may be detected/patched later.
- **The source material's own hard gate (all four required, not partial):** (1) the
  SOW/RoE explicitly authorizes anti-forensics/log-manipulation/"detection evasion
  testing" **by name** — a generic "penetration test" authorization does not cover
  this; (2) a named client-side "white cell" contact is aware of the engagement
  window and can distinguish the exercise from a real incident; (3) any log/timestamp
  change made during testing is disclosed and reverted as part of the final report —
  never a permanent, undisclosed alteration of the client's own records; (4) the goal
  is testing *whether* the blue team notices, not permanently defeating their ability
  to notice anything, ever.
- **Why this is different from every other opt-in category:** condition (2) is
  irreducibly a human-awareness fact this system cannot verify computationally — no
  scope-check, schema constraint, or heuristic can confirm "a specific named person
  at the client currently knows this window is happening and can tell it apart from
  a real breach." This is exactly the class of fact a live human confirmation exists
  to attest to; a config flag alone would let the system proceed on an operator's
  unverified claim that condition (2) holds, with no real-time check that it's still
  true when the specific action actually fires.
- **Implementation:** `FR-CHECKPOINT-05` requires `--white-cell-contact` (non-empty
  text) and `--attest-disclosure` (a fixed attestation flag) at `start` *in addition
  to* `--allow-anti-forensics` — `start` MUST refuse the flag combination if either
  is missing. Every individual matching action still requires a live
  `approve-checkpoint` regardless of these `start`-time fields being present.
- **Impact if bypassed/misused:** an autonomous agent tampering with a client's own
  detection/logging infrastructure with no live human confirmation that a white-cell
  contact is actually aware, in real time, is functionally indistinguishable from a
  real intrusion tampering with evidence — this is the single most severe
  misuse case in this entire document, which is why it carries both the config-time
  attestation fields (`FR-CHECKPOINT-05`) *and* the live checkpoint (`FR-CHECKPOINT-03`),
  the only action class with both.
- **Explicitly excluded regardless of authorization** (from the same source file, §
  "Explicitly Excluded"): cataloguing gray-market/criminal infrastructure discovered
  behind a compromised system — not a penetration-testing technique at all, an
  incident-response/legal question for the client (`FR-BROADSCOPE-03`, `19`).

### 2.2 `LIVE_CREDENTIAL_SPRAY`

- **Where it comes from:** `Actual-Setup/skills/credential-attack/SKILL.md` and
  `Actual-Setup/tools/spray_orchestrator.sh` (read directly for the exact guard
  implementation, per a dedicated mining fork).
- **What it covers:** the actual authentication-attempt stage of a credential-spray
  pipeline, across all four modes (`http-form`/`oauth`/`o365`/`okta`) — **not** the
  upstream wordlist-generation, breach-enrichment, or employee-OSINT stages, which
  have no live-target interaction and are correctly outside this gate (`FR-CRED-01`).
- **The source material's own safety mechanism, quoted from its own code comment:**
  *"`tools/scope_checker.py` is a library (no enforcement CLI), so the real safety
  mechanism here is making the human re-state the target out loud."* Concretely,
  two sequential interactive prompts: (1) type the target hostname to confirm it
  exactly matches, abort otherwise; (2) after an estimated lockout-percentage
  warning is shown, type "yes" to proceed, anything else aborts. A `--i-understand`
  flag bypasses both prompts entirely — but the source's own design treats that as
  an escape hatch for pre-confirmed/scripted invocation, not a weaker but equivalent
  check.
- **Why this is different from a pre-engagement config flag:** the two conditions
  this interactive prompt guards against — spraying the *wrong* target due to a
  copy-paste/config error, and *not knowing* the real-time lockout-risk estimate
  before committing — are both facts that only exist at the moment of execution, not
  at `start` time. A flag set hours or days before the spray actually runs cannot
  re-verify either fact at the moment it matters.
- **Implementation:** `FR-CRED-03` classifies the live spray-execution step
  `LIVE_CREDENTIAL_SPRAY`; `rationale_shown_to_operator` (`DR-SCHEMA-18`) MUST
  include the target hostname and an estimated lockout percentage, reproducing the
  *substance* of the source's interactive confirmation (not just noting that a
  checkpoint fired). Phishing-based MFA bypass (AiTM proxy, OAuth device-code
  phishing) is excluded from this system entirely, not merely checkpoint-gated —
  see `FR-CRED-03`'s closing clause.
- **Impact if bypassed/misused:** a spray against the wrong target (e.g. a
  copy-paste error landing on a similarly-named but out-of-scope/third-party
  domain) or an unbounded-round spray that locks out a large fraction of a client's
  real user base are both realistic, non-hypothetical outcomes this specific guard
  exists to catch — account lockout is a direct, real availability harm to the
  client's actual users, not just an infrastructure concern.

### 2.3 `CICD_EXTERNAL_ARTIFACT`

- **Where it comes from:** `Actual-Setup/skills/cicd-security/SKILL.md`, fully read.
- **What it covers:** any action that creates a persistent, visible artifact in a
  target's CI/CD system — opening a pull request, triggering a workflow run, or
  modifying repository secrets/permissions.
- **The source material's own framing:** self-hosted-runner poisoning and workflow
  injection are only provable by actually opening a PR against the real repository —
  the skill's own scope notes state this plainly ("self-hosted runner attacks
  require a successful workflow run, which means opening a real PR — confirm the
  program allows this") and separately warn never to trigger a workflow that could
  affect production infrastructure without explicit written permission.
- **Why this is different from ordinary Tier 2 execution:** every other Tier 2
  action in this system runs a subprocess against the target and reads back a
  response — nothing persists in the target's own systems as a result. Opening a PR
  or triggering a workflow run creates something the target's own team will see,
  potentially review, and cannot make disappear the way a scan probe simply stops
  existing once done.
- **Implementation:** `FR-CICD-03` classifies these actions `CICD_EXTERNAL_ARTIFACT`;
  `FR-CICD-04` requires the checkpoint's live approval to double as the point where
  program-policy permission for touching CI/CD infrastructure is actually confirmed,
  since this system has no other mechanism to verify that.
- **Impact if bypassed/misused:** an autonomous agent opening real PRs or triggering
  real workflow runs against a client's production-linked CI infrastructure, with no
  human ever confirming the program's policy actually permits it, risks real
  disruption to the client's actual development pipeline — a materially different
  risk class than a read-only scan.

### 2.4 `DEPENDENCY_CONFUSION_PUBLISH`

- **Where it comes from:** `Actual-Setup/skills/web2-vuln-classes/SKILL.md` §31
  (Dependency Confusion/Supply Chain), read as part of a dedicated mining pass over
  the file's remaining (non-§11) sections.
- **What it covers:** publishing (and the mandatory subsequent unpublishing) of a
  real package to a live, third-party public package registry (npm/PyPI/RubyGems/
  Maven) as part of proving a dependency-confusion finding.
- **The source material's own ethics line:** callback-only PoC (a DNS/HTTP beacon
  proving execution, never a real payload); verify the callback source is genuinely
  the target's own infrastructure, not a registry crawler, before treating it as
  confirmed; and unpublish immediately — "leaving a higher version live is a DoS"
  against every legitimate consumer of that package name, in the source's own words.
- **Why this is different from every other action in this system:** this is the
  only action in this entire document set that touches infrastructure with **no
  `scope_rules` relationship to the target at all** — a public package registry is
  neither the client's infrastructure nor infrastructure this system merely calls
  out to for its own operation (like the web3 RPC endpoint) — it's a third party's
  live production system, and the action has permanent external side effects
  (every consumer of that package name, not just the target) until reverted.
- **Implementation:** `FR-VULNCLASS-03` classifies the publish action (and requires
  the unpublish to be tracked as part of the same checkpointed action, not a
  separate, un-gated cleanup step) `DEPENDENCY_CONFUSION_PUBLISH`.
- **Impact if bypassed/misused:** an unattended agent that publishes a package and
  then fails to unpublish it (a crashed process, a misjudged callback-verification
  that never fires, a network partition during the cleanup step) leaves a real,
  potentially-exploitable package live on a public registry indefinitely, affecting
  everyone who happens to reference that package name — not just the intended
  target.

## 3. What this catalog deliberately does not cover

The three existing pre-engagement opt-in-flag categories (`--allow-brute-force`,
`--allow-active-exploitation`, `--allow-lateral-movement`, `FR-TOOL-06a`) are **not**
part of this catalog — they were evaluated during this same mining sweep (`19`'s
`FR-GRAPHQL-03`) and confirmed to be a sufficient, equivalent safeguard on their own
terms, since nothing in their own source material's design depends on a live,
real-time human confirmation the way the four classes above do. They remain
documented where they already are (`01`, `05`, `07`'s `RISK-UNBOUNDEDAUTONOMY`), not
duplicated here.
