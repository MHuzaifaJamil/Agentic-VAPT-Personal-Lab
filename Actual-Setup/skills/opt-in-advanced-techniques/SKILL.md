---
name: opt-in-advanced-techniques
description: ⚠️ OPT-IN ONLY — techniques deliberately excluded from this toolkit's default behavior because they conflict with its normal operating rules (strict scope adherence, no log tampering, general-purpose over narrow single-product scripts). Covers broad/unlimited-scope engagement framing, red-team anti-forensics (requires specific written authorization), and narrow product-specific exploit patterns. Do NOT reach for this skill by default — bb-methodology, rules/hunting.md, and triage-validation are the correct default for every engagement. Only load this when the user explicitly invokes it by name, or when a specific written SOW/ROE explicitly authorizes one of these techniques by name.
---

# OPT-IN ADVANCED TECHNIQUES

This file exists so three specific techniques aren't lost, without making
them part of this toolkit's default behavior. Each one was excluded from
the normal skills because it conflicts with a rule this toolkit otherwise
enforces on every engagement — that conflict doesn't go away just because
the technique is documented here. **The default for every engagement is
still `bb-methodology` + `rules/hunting.md` + `triage-validation`.** Use
anything in this file only when a specific, written engagement scope
explicitly calls for it — never because a target is being stubborn under
the normal rules.

---

## 1. BROAD / UNLIMITED-SCOPE ENGAGEMENT FRAMING

`rules/hunting.md` Rule 1 (read full scope first) is correct for the
overwhelming majority of engagements — public bug bounty programs and
almost all client VAPT contracts define a fixed asset list, and testing
outside it is a policy violation regardless of how interesting the
adjacent surface looks.

A small minority of engagement types use genuinely broader scope language —
mature adversary-emulation contracts, some "assumed compromise" exercises,
and a few program policies phrased as "anything the client owns or
operates" rather than a fixed domain list. **This section applies only when
the written ROE actually uses that language** — verify via `/scope` or by
asking, never by inferring it from how much attack surface a target has.

What changes under genuinely broad scope, and what doesn't:

- **Changes:** you don't stop at a fixed list — any asset confirmed to be
  owned/operated by the client is fair game, and a pivot from one
  in-scope system into another client-owned system doesn't need a separate
  scope check each time.
- **Does NOT change:** every other discipline stays identical. Third-party
  infrastructure the client merely uses (a SaaS vendor, a CDN they don't
  operate, another company's API) is still out of scope even if reachable
  from an in-scope asset — broad scope means "everything you own," not
  "everything you can reach." `triage-validation` closure discipline, the
  7-Question Gate, and Rule 21's change-ledger discipline all still apply
  in full. This is a *wider fence*, not *no fence* — never treat it as
  license to skip verifying ownership before touching something adjacent.

If a target simply has a lot of attack surface, that is not a signal to
assume broader scope — it's a signal to work through the fixed list more
thoroughly.

---

## 2. RED-TEAM ANTI-FORENSICS / OPSEC — REQUIRES SPECIFIC WRITTEN AUTHORIZATION

**Hard gate before any of this applies — all four required, not a checklist
to satisfy partially:**

1. The SOW/ROE explicitly authorizes anti-forensics / log manipulation /
   "detection evasion testing" **by name** — a generic "penetration test"
   or "VAPT" authorization does not cover this. Most standard engagements
   explicitly forbid it, because the client's logs are the evidence used
   to grade their own detection & response capability — tampering with
   them defeats the exercise for everyone except a pure "can we get away
   with it" contract, which is a different (and rarer) engagement type.
2. A named client-side contact ("white cell") is aware of the engagement
   window and can distinguish the exercise from a real incident.
3. Any log or timestamp change made during testing is disclosed and
   reverted as part of the final report — this is never a permanent,
   undisclosed alteration of the client's records.
4. The goal is to test *whether the blue team notices*, not to permanently
   defeat their ability to notice anything, ever, about anything.

**What this category actually covers**, referenced by MITRE ATT&CK
technique ID rather than reproduced as ready-to-run commands here — look
up the current ATT&CK page for the authoritative, regularly-updated detail
and platform-specific detection guidance:

- **T1070** (Indicator Removal) and its sub-techniques — clearing or
  selectively editing logs (T1070.001 on Windows Event Logs), clearing
  shell history (T1070.003), timestomping file metadata (T1070.006) to
  match a plausible neighboring file.
- **T1564** (Hide Artifacts) — minimal-footprint execution favoring
  memory-resident techniques over dropping files to disk, when the ROE
  permits any code execution at all.
- **T1622** (Debugger Evasion) / general "check for EDR/SIEM agent
  presence before escalating technique aggressiveness" — a live
  adversary-emulation exercise typically progresses passive → confirm no
  blocking monitoring → active → exploitation, escalating only after each
  step confirms it's safe to continue, or accepting that triggering
  detection IS the point of that specific exercise.

Rate-limiting and traffic-blending techniques (avoiding a WAF/IDS ban
while still completing testing) are **not** gated the same way — those are
already covered in `security-arsenal`'s rate-limit-bypass tables and don't
require this section's authorization, since they don't touch the client's
own evidence trail.

---

## 3. NARROW, PRODUCT-SPECIFIC EXPLOIT PATTERNS

These aren't excluded for ethical/rule-conflict reasons — they're excluded
from the general skill files because they're too narrow (one specific
product) to belong there. Verify the exact product/version is actually
present via recon before spending time on any of these; if it isn't, skip
straight past this section.

**CDN/reverse-proxy control-plane scope-check gap.** Some CDN and
edge-config management APIs (GoEdge is a real, disclosed example) validate
that a caller holds *a* valid admin API key/token, but not that the
specific resource ID being requested belongs to that caller's own
account/tenant. This is a direct application of the **Authorization
Backward-Taint Procedure** in `web2-vuln-classes` §2 — the "sufficient
guard" for a multi-tenant resource requires tenant/ownership binding, not
just identity — applied specifically to a CDN control plane. The concrete
technique: once you have *any* valid admin key for the panel (even a
low-privilege one, or one issued for a single site), sweep sequential
resource IDs (certificate configs, domain configs) against the same
"fetch resource by ID" endpoint and see how many return data outside what
that key should own. On products like this, a single valid key
frequently exports every TLS private key or config across the entire
multi-tenant install, not just the caller's own. Impact: full certificate
compromise across every domain hosted on that install → MITM/traffic
decryption capability.

**Same-subnet credential interception (ARP MITM).** Already covered in
depth by `cybersecurity-skills:performing-arp-spoofing-attack-simulation`
(available separately in this environment, see `bb-methodology`'s
Complementary Skill Library section) — use that rather than re-deriving
this technique here.

**CDN-to-cloud-storage credential escalation.** Where a CDN/edge config
exposes cloud STS or other temporary credentials (via its own management
API, or a misconfigured origin-pull config pointing at cloud storage),
this is the same pattern as `chain-builder`'s "S3 → OAuth ATO" chain and
`web2-vuln-classes`'s Cloud/Infra Misconfigs class, with the CDN control
plane as the pivot point instead of a directly-exposed bucket. No new
technique — apply those existing chain patterns.

**Hybrid CMS/panel + hybrid-mobile-app combinations.** When recon turns up
both a PHP-based admin panel (e.g. a product like BT Panel/aaPanel) and a
UniApp-based mobile client talking to the same backend, that's a signal to
run `whitebox-code-recon` against the panel and `mobile-pentest`'s UniApp
shortcut against the app — not a distinct technique, just a reminder to
check both when you see the combination, since the two together often
share the same underlying API surface and the panel access can reveal
config the app obfuscates (or vice versa).

---

## EXPLICITLY EXCLUDED — NOT INCLUDED EVEN HERE

One category from the source material this file's content was drawn from
is deliberately left out entirely, not just gated: cataloguing gray-market
or criminal infrastructure found behind a compromised system (classifying
wallet-phishing brand impersonation, gambling operations, pirated-content
hosting, or similar, via keyword-matching against domain/certificate data).
That isn't a penetration-testing technique — it's OSINT investigation of
someone else's criminal campaign, which is outside this toolkit's purpose
regardless of authorization framing, and normalizing brand/keyword
matrices for identifying that content as toolkit reference material isn't
appropriate here. If a live engagement genuinely surfaces this situation
(a compromised system is found to be hosting unrelated criminal
infrastructure), that's an incident-response and legal question for the
client, not a hunting technique — flag it to the client and stop, don't
catalogue it.
