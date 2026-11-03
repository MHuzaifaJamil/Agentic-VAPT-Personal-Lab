# How Today's Landscape Survey Connects to Mugheeraat's Actual Current State

**Status:** Exploratory research per `CLAUDE.md` §6. Not binding, not actioned.

**Purpose:** `2026-10-28-Comparable-Small-Scale-AI-Pentest-Projects-Landscape-Survey.md`
surveyed the field in general terms. This file does the specific, concrete work the operator
asked for next: check that survey against Mugheeraat's **actual current code and actual
currently-open items** (verified via a fresh clone, commit `f587cd1`, and a direct read of
`STAGING-Pending-Discussions-and-Fixes.md`, not assumed from memory) and say what it means for
what's being built, right now, not in the abstract.

## What changed since the last time this side looked at the real code

Mugheeraat has moved substantially since the last verified read (Rounds 26-34, all real,
confirmed via `gh api` and the fresh clone):
- Round 26's SPA recon gap is **resolved** — not via the katana-headless flag this project's
  own Oct-7 research suggested, but via a purpose-built `spa_crawler.py` (Playwright-based)
  that found 10 real endpoints vs. katana's 5 static ones. Round 33 then *did* test the
  katana-headless idea live, found it real but narrower (9 endpoints from the landing page
  alone, structurally blind to Angular's `HashLocationStrategy` hash-routed views), and
  correctly kept `spa_crawler.py` as primary rather than switching. Verified directly: `grep
  useHash` against Juice Shop's real `main.js`.
- **10 of the 11 actionable items in this project's own
  `2026-10-07-Realistic-Mitigations-for-Every-Known-Issue.md` are already implemented and
  tested** on the Implementing side (Round 33, commits `480a952`..`38c97bd`, full suite 1280
  passing). The one holdout (`interactsh-client` install) is an operator system-install
  decision, not a research gap. This means most of what last round's research proposed is no
  longer "pending" — it's done, and today's research should build on top of it, not repeat it.
- A new, more specific and more important root cause was found and documented
  (`2026-10-14-Root-Cause-Zero-Confirmed-Findings-Missing-Session-Identity-State.md`, pulled
  from GitHub, authored by the Implementing-side peer "Mugheeraat 3.0"): **every historical
  Adjudicator call (6/6) correctly DISMISSED, because none of the underlying commands ever
  used a cookie jar or carried an authenticated identity — the codebase has no session/
  identity-state mechanism at all.** This is currently the single most load-bearing open
  technical gap, and it is *not yet staged as its own Round* in `STAGING.md` — it exists only
  as a dated research file with a 3-step recommendation at the bottom, awaiting the operator's
  decision on scope/timing.
- Round 34 (OS-level write-boundary for `artifacts_dir`, replacing the denylist whack-a-mole)
  is open and pending — a generic sandboxing/allowlist-vs-denylist engineering question, not
  something today's AI-pentest-specific research bears on directly; noted for completeness,
  not force-connected to this survey.

## The one connection worth flagging above everything else

**XBOW — the single strongest real-world AI-pentest success story in today's survey — has a
documented, named weakness: independent analysis found "no evidence of authentication-bypass
or business-logic findings," with its real successes concentrated in SQLi/XSS/SSRF/path
traversal instead.** That is not a coincidence relative to what Mugheeraat just found about
itself. IDOR, CSRF, and BFLA (the three vulnerability classes behind every one of Mugheeraat's
6 historical DISMISSED verdicts) are exactly the access-control/business-logic class that
requires demonstrating a second, different identity's data or privilege boundary being
crossed — which is precisely the capability (session/identity state) that's missing. **The
best-performing AI pentest system found anywhere in this survey has the same hole Mugheeraat
just diagnosed in itself.** This is independent, field-wide confirmation that the gap is real,
general, and worth closing — not a Juice-Shop-specific quirk.

## Why this is good news, specifically

Today's academic-literature pass (`2026-10-28` survey, section B) found a useful taxonomy
(arXiv:2602.17622): **Type A failures (engineering gaps — missing tools, missing capabilities)
are "readily addressed" by better scaffolding; Type B failures (planning/state-management
limits) are "largely invariant to the underlying LLM"** — no amount of model-swapping fixes
them. The session/identity-state gap is cleanly **Type A**: it is a missing deterministic
capability (a cookie jar, a session-bootstrap step), not a reasoning limitation. The
Implementing-side peer's own proposed fix — register two deterministic test accounts once per
engagement via a fixed scripted request (not LLM-proposed), persist their cookies under
predictable `artifacts_dir` paths, teach the Scripter via `prompts.py` to pass `-c {path}`/
`-b {path}` — is exactly the right *category* of fix per the literature: engineering, not a
bigger or different model. That means **it doesn't need to wait on the fine-tuning/model-swap
research tracks to be worth doing** — it's independently the highest-confidence, most
field-validated next move available, and it is currently the single highest-leverage item
sitting unstaged in `Research/` rather than in `STAGING.md`.

## A second connection: the Adjudicator is *not* exhibiting the field's most common failure

Today's survey (section C) found Garak's own follow-up research showing an LLM evaluator's
pass/fail judgment on the *same* attack attempt varies by **up to 33%** depending on which
judge model scores it — i.e., across the field, the evaluation/grounding step is typically the
least reliable component, not attack generation. Mugheeraat's own history says the opposite
about its own Adjudicator: all 6 historical DISMISSED verdicts were independently confirmed
correct (the underlying evidence genuinely couldn't support the claim, by construction — see
the root-cause file), and a live replay test against real strong evidence (the ground-truth
SQLi auth-bypass, `POST /rest/user/login`) produced a correct `CONFIRMED` verdict with a
well-reasoned rationale (Round 27 item 5, resolved 2026-09-29). **This is a point of
distinction worth recognizing, not a gap to chase:** Mugheeraat's deterministic-grounding +
baseline/attack/diff evidence bar (`CLAUDE.md` §4.3, `ROLE_BLOCK_ADJUDICATOR`) is avoiding
exactly the failure mode most comparable tools exhibit. The one loose thread worth tracking
(noted in Round 27 item 5's own writeup, n=1, not yet acted on) is that the `CONFIRMED`
verdict's `false_positive_checks` booleans all came back `false` despite the rationale
correctly ruling them out — an internal self-contradiction within one response, not yet known
to be systematic. Worth gathering more samples before treating it as a real bug, consistent
with how it was already left.

## A third connection: the one Oct-7 proposal that's still genuinely open

Of this project's own prior research, **the embedding-based skill-retrieval upgrade
(`all-MiniLM-L6-v2` + `sqlite-vec`, replacing the current lexical Szymkiewicz-Simpson matcher
in `vapt_agent/knowledge/skills_index.py`) is the one substantial item that has not been
touched** — verified directly: `grep -rn "embedding\|sqlite-vec"` across the real codebase
returns nothing outside unrelated incidental hits (`oob_listener.py`'s "embedding a unique OOB
hostname", a DOM-XSS harness's "embedding `marker`") — the actual retrieval mechanism is still
pure lexical overlap. Today's academic pass adds real, numbers-backed motivation to actually
prioritize this: the ablation in arXiv:2604.27143 showed RAG as one of five scaffolding
techniques that, combined, took 7-8B models from 8% to 67% success on privilege-escalation
tasks — matching *guided* GPT-4o. That is the same class of gain this project already
hypothesized in `2026-10-07-Embedding-Based-Skill-Retrieval-Upgrade.md`, now with independent
field evidence behind it rather than just this project's own reasoning. Given 10/11 other
items from that research round are done, this is the one concretely "ready to prioritize next"
item among last round's work.

## A fourth, lower-confidence connection: vulnerability-class-specific architecture

arXiv:2606.25332 (today's survey) found no single agent architecture dominates across
vulnerability classes — multi-agent isolation wins long-sequence chains (e.g.
deserialization), monolithic wins short-chain injection, graph-driven wins cross-session
access-control bugs. Mugheeraat's Primary/Secondary Scripter split is architecturally a
mild form of this idea already (Secondary Scripter explicitly tries what Primary didn't).
This is a softer, more speculative connection than the three above — flagged for awareness,
not as a recommendation, since mapping which of Mugheeraat's two Scripters should specialize
in which vulnerability class would need its own dedicated investigation before being
actionable.

## What this means, concretely, if the operator wants to act on any of it

None of the following is staged or approved — this section exists so a staging decision, if
wanted, doesn't have to re-derive the reasoning:

1. **Highest-confidence, field-validated, Type-A-category fix:** stage the session/identity-
   state recommendation already written in
   `2026-10-14-Root-Cause-Zero-Confirmed-Findings-Missing-Session-Identity-State.md` as its own
   Round in `STAGING.md` — it currently has no Round number and risks being lost among the
   dated research files. Today's survey adds the XBOW parallel and the Type-A/Type-B framing
   as additional justification, not new content to the proposal itself.
2. **Second-highest-confidence, independently numbers-validated:** prioritize the
   embedding-retrieval upgrade over further detection-vocabulary patching — it's the one
   substantial piece of this project's own prior research that hasn't shipped yet, and today's
   literature gives it the strongest external evidence of any pending item.
3. **No action needed, but worth recording as a confirmed strength:** the Adjudicator/
   deterministic-grounding design is validated by contrast with the field's most common
   failure mode (evaluator unreliability) — this is evidence the existing architecture is
   sound on this axis, not a signal to change anything here.
4. **Fine-tuning (Hackphyr precedent, already covered in
   `2026-10-07-FineTuning-GPU-Access-and-Maximizing-CYS-Models.md`) remains a longer-horizon,
   complementary track**, not a prerequisite for items 1-2 — today's survey's honest negative
   result (Hackphyr: 85%+ undefended, 23-50% against active defenders) suggests it's worth
   the investment eventually, specifically because scaffolding alone caps out at matching
   *guided* large-model performance rather than closing the gap outright, but there's no reason
   to wait on it before doing 1 and 2, which are cheaper and already-written-up.
