# Second-Order Prompt-Injection Gap in Derived-Text Fields

**Author:** Mugheeraat 3.0 (Setup Research). **Method:** targeted code audit (read-only; no
DB writes, no code changes) checking whether `CLAUDE.md` §4's "Evidence Tagging & Untrusted
Content Isolation" rule — raw target-derived text MUST be wrapped in
`<tool_output_untrusted>...</tool_output_untrusted>` before reaching an LLM prompt — is
implemented consistently everywhere evidence flows into a prompt, not just where it was
first designed for. Every claim below was independently verified against the real code on
this host (file:line references are exact at commit HEAD as of this writing).

## 1. The real mechanism exists and is sound for first-order evidence

`vapt_agent/bridge/sanitize.py:18-19` defines the tag constants; `wrap_untrusted()`
(`sanitize.py:122-126`) is a real, used function, not a stub — called from every role module
that ingests raw tool/HTTP output (`strategist.py`, `primary_scripter.py`,
`secondary_scripter.py`, `criterion_adjudicator.py`, `reporter.py`, `strategy_auditor.py`,
`bridge/pipeline.py`).

Breakout is handled: `_escape_forged_tags()` (`sanitize.py:112-119`) neutralizes any literal
`<tool_output_untrusted>`/`</tool_output_untrusted>` a target embeds in its own response
(case-insensitive), replacing `<`/`>` with Unicode lookalikes (‹›) *before* wrapping — a
target cannot forge a closing tag to escape the wrapped region. This has direct test
coverage: `tests/test_bridge_sanitize.py:46`
(`test_wrap_untrusted_escapes_forged_closing_tag`). First-order evidence handling is
genuinely solid.

## 2. The gap: LLM-authored free text, written *after* reading wrapped evidence, is spliced back in unwrapped

Three fields carry this shape — a model reads provenance-tagged target content, writes its
own free-text summary/rationale about it, and that free text is persisted to the DB — and
each is later spliced into a *subsequent* prompt with **no wrapping, no re-tagging, and no
instruction anywhere telling the authoring role not to quote raw evidence verbatim**:

- **`prior_dismissal_rationale`** — `vapt_agent/council/criterion_adjudicator.py:79`:
  ```
  f"...was DISMISSED for the reason below...):\n{prior_dismissal_rationale}"
  ```
  Sourced from `verified_vulnerabilities.gate3_rationale`, a free-text field a past
  Adjudicator wrote (schema only requires non-empty string — `engine/schemas.py`). The
  function's own docstring (`criterion_adjudicator.py:65-68`) justifies the omission: "this
  system's own past model output, not target-controlled, so it is not provenance-tagged."

- **`explored_attack_paths`** and **`closed_vectors`** —
  `vapt_agent/council/dedup.py:96-134` (`build_explored_attack_paths_block`) and
  `:137-161` (`build_closed_vectors_block`) pull `task_queue.description` /
  `proposed_command` (Strategist/Scripter-authored) and join them into plain strings with no
  call to `wrap_untrusted` anywhere in either function. They reach the next prompt via
  `strategist.py:153,156` as flat string concatenation. `strategist.py`'s own docstring
  (lines 78, 97-103, 105-110) gives the identical justification three times: "not
  target-derived content... this system's own derived summary/state... not provenance-tagged
  either."

**This is an inconsistency already implicit in the codebase's own stated pattern, not a
purely theoretical gap.** `existing_findings` is the direct sibling of these three fields —
also LLM-authored (`title`/`description` text assembled in
`orchestrator/phase_lifecycle.py:386`) from a model that had access to wrapped target
content — and it **is** wrapped (`strategist.py:117`: `wrap_untrusted(existing_findings)`).
The three fields above are functionally identical in provenance (LLM output, written after
reading untrusted evidence) but land on the opposite side of the line the codebase itself
already draws elsewhere.

## 3. Concrete attacker scenario

A target plants injection-shaped text in an HTTP response body or banner (e.g. a string
designed to look like a system instruction). The Scripter/Strategist reads it properly
wrapped and, in the normal course of writing a `task_queue.description` or an Adjudicator
writing `gate3_rationale` while explaining a dismissal, quotes a fragment of that text
verbatim (nothing prevents this — there is no "never quote raw evidence verbatim in your own
rationale/description field" instruction in `council/prompts.py`). That quoted fragment now
sits unwrapped in the DB. On a later round or a later engagement against the same
fingerprint, it is spliced directly — unwrapped, untagged — into the Strategist's planning
context (`explored_attack_paths`/`closed_vectors`) or the Adjudicator's CONFIRM/DISMISS
context (`prior_dismissal_rationale`): exactly the two places in this pipeline where
unmarked, instruction-shaped text is most dangerous (task generation and verdict-making).
This is a **second-order / transitive** injection path — the first-order defense
(`wrap_untrusted` on raw evidence) is working exactly as designed and does not cover it,
because the attack surface here is the system's own prior output, contaminated once, not the
live tool output itself.

## 4. Test coverage

None. Every existing `tool_output_untrusted`-adjacent test
(`test_council_strategist.py`, `test_council_adjudicator.py`, `test_bridge_sanitize.py`)
checks that first-order raw evidence gets wrapped. Nothing exercises whether
`explored_attack_paths`/`closed_vectors`/`prior_dismissal_rationale` can carry and replay
injection-shaped text forward.

## Assessment and recommendation

Severity is modest in practice (it requires a prior round's model to have already quoted
attacker text into its own free-text output — not guaranteed, but also not prevented), but
the fix is cheap relative to the risk given these fields feed the Strategist's planning and
the Adjudicator's verdicts — the two roles this project's own threat model treats as highest
value to manipulate. Two independent, non-exclusive mitigations, in order of
cost/effectiveness:

1. **Wrap all three fields the same way `existing_findings` already is** — change
   `strategist.py:153,156` to `wrap_untrusted(explored_attack_paths)` /
   `wrap_untrusted(closed_vectors)` (matching the `(none on record)`/`(none closed yet)`
   empty-case handling already there), and the equivalent at
   `criterion_adjudicator.py:79`. Purely mechanical — same pattern already proven elsewhere
   in the same files, no new code path needed.
2. **Add an explicit prompt instruction** (in `council/prompts.py`, the relevant
   `ROLE_BLOCK_*` constants) telling the Adjudicator/Strategist/Scripter to summarize
   findings/rationale in their own words rather than quoting raw target content verbatim —
   reduces how often contaminated text enters these fields in the first place, independent
   of whether wrapping is added.

Not actioned by this research pass — per the standing Research/ convention, this is a
finding and recommendation, not an implementation. Staged for Mugheeraat 1.0/2.0 and the
operator's decision on whether/when to apply either mitigation.
