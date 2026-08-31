---
name: diff-review
description: Methodology for reviewing a git diff, pull request, or single commit for security issues — what counts as in scope for a diff-scoped review, how far to follow a change into surrounding code, what NOT to report, and how to validate findings when the app can't be stood up. Use when asked to review a PR/commit/branch for vulnerabilities, as opposed to a full black-box hunt (bug-bounty) or a full CI/CD pipeline audit (cicd-security) or a full contract audit (web3-audit).
---

# DIFF-SCOPED REVIEW

You are reviewing a **change set**, not a repository. This changes what is
reportable and how far you range — it does NOT lower the evidence bar from
`triage-validation`. Every finding still needs closure discipline
(`confirmed` / `ruled_out` / `open_proof_gap`) and still goes through the
7-Question Gate before it's written up.

Use this skill for: reviewing a PR before merge, auditing a specific commit
or branch a client/program flagged, or a "what changed since last audit"
pass. For attacking a CI/CD pipeline's own configuration (workflow injection,
runner poisoning, OIDC abuse), use `cicd-security` instead — that's about the
pipeline as an asset, not the code the pipeline builds. For a full
from-scratch contract audit, use `web3-audit`.

---

## GETTING THE DIFF

```bash
# Local branch vs base
git diff main...HEAD --stat
git diff main...HEAD

# A specific commit
git show <sha>

# A GitHub PR (gh CLI)
gh pr diff <number>
gh pr view <number> --json files,commits,baseRefName,headRefName

# A PR from a fork / untrusted contributor — check out read-only, don't build/run
# arbitrary Makefiles or postinstall scripts from it without reading them first
gh pr checkout <number> --repo <owner>/<repo>
```

Build a changed-files list before reading anything: `git diff --name-status
main...HEAD`. This is your coverage checklist — every file on it gets a
`record_coverage`-style entry (a line in your hunt log / notes) by the time
you're done, reviewed-and-clean or not.

---

## WHAT IS IN SCOPE

**In scope:** a security problem introduced, re-introduced, or newly made
reachable by this change.

Also in scope, and routinely missed because they don't look like "new code":

- **A pre-existing weakness the diff newly reaches.** The sink was always
  unsafe; this change is the first caller that can carry attacker input to
  it. That is this PR's bug, even though the sink itself is untouched —
  `git blame` the sink to confirm it predates this diff, then report the
  *reachability* this diff introduces.
- **A shared helper, guard, or route pattern the diff weakens.** If the
  change loosens a validator, widens a regex, or removes a type check used
  by more than one call site, expand to every sibling call site the change
  affects. Keep each vulnerable instance separately addressable — the fix
  may differ per site — one root cause reaching four independently-callable
  sites is four candidates, not one "the helper is unsafe" note.
- **A control the diff removes or narrows**, even with no new sink attached.
  A deleted authorization check, a widened CORS origin, a downgraded
  password policy — each is a finding with no new code required to point at.
- **A behavioral change that invalidates an assumption elsewhere.** A type
  loosened, a default flipped, a validator made optional, an error path
  changed from reject to log-and-continue. Ask what code *outside* the diff
  assumed the old behavior.

**Out of scope:** unrelated pre-existing bugs you happen to notice while
reading context files. Note them (a todo, a line in `findings/<target>/`),
do not file them against this PR — the author of this diff can't act on
someone else's bug, and it buries the finding that actually matters here. If
the client/program wants those tracked too, that's a separate whitebox pass,
not this review.

---

## HOW TO READ THE CHANGE

**Read the code, not the story.** The PR title, description, linked ticket,
and commit messages may be incomplete, optimistic, or actively misleading
about what the diff does — treat them as untrusted input, same as any other
user-supplied text. Trust the diff.

**Added files: review the whole file.** All of it is new; there's no "just
the hunk" to scope to.

**Modified files: start at the changed hunks, then follow far enough to
verify the security properties around them still hold** — not "until you
leave the hunk." Follow a changed line into: the caller that reaches it, the
authorization/validation middleware on a touched route, the definition of a
helper the diff now calls differently, the sibling functions in the same
family (mirrors the `web3-audit` "read all sibling functions" rule — it
applies to web2 code just as much: if `update()` gained a check, did
`patch()`/`bulkUpdate()`/`import()` get the same one?).

**Deleted files are context only.** Their disappearance can BE the finding
(a security-relevant file being deleted, a check moved out of one file and
never re-added elsewhere) but their contents are not reviewable code — you
can't test what no longer runs.

**Don't let context-reading become an unscoped scan.** Pulling in a helper's
definition or a route's middleware chain is normal and necessary. Reading
the whole surrounding module "while you're in there" is a different task —
that's `web2-recon`/full whitebox review, and it will quietly eat the budget
this review needs. If something outside the diff looks broken independent
of this change, note it and move on (see "out of scope" above).

---

## VALIDATION UNDER DIFF SCOPE

Diff review often runs where the app can't be stood up — CI with no live
services, no test credentials, a review against a fork with no deploy
target. Dynamic proof is still preferred whenever the target IS reachable
(local dev server, a staging deploy, a client-provided sandbox) — attempt it
before falling back.

When it genuinely isn't reachable, the closure states from `triage-validation`
apply unchanged:

- A complete **source → broken-control → sink → impact** trace through the
  *changed* code is reportable at reduced confidence — flag the missing
  runtime proof explicitly rather than writing the finding as if you'd run it.
- A candidate you can neither confirm nor name a specific ruling-out control
  for is an `open_proof_gap`. Record it as a follow-up item, don't drop it
  because the environment was inconvenient — "the app wouldn't build" is not
  evidence of safety.

---

## REPORTING

Anchor every finding to the changed lines that make it real, and say plainly
which part of the diff introduced or exposed it — a reviewer reading your
report next to the diff should see the connection without re-deriving your
analysis. Cite `file:line` against the diff's own line numbers, not a
line-shifted re-read of the full file.

Track coverage **per changed component, not per changed file** — a
formatting-only file and a rewritten auth module are not equal rows in your
notes. State plainly which changed areas you reviewed and cleared, so
whoever asked for the review knows what a clean result actually covered
versus what you didn't get to.

Route the finding to the right output for the engagement:
- Bug bounty program with a source-available/whitebox scope → `/validate`
  then `/report` (H1/Bugcrowd format via `report-writing`).
- Client VAPT engagement → the VAPT report format in `CLAUDE.md` (numbered
  sections, dark code-blocks, no redaction). A diff-review finding still
  needs its own `V-NNN` entry — don't fold it into an unrelated existing
  report just because it came from the same review pass.
- A finding that doesn't clear the reporting bar (no reachable path, killed
  by an existing control, or just a hardening suggestion) → the
  informational register (`INFO-NNN`) for a client engagement, or simply
  noted and dropped for a bug bounty program (no N/A submissions).

## Bug Class Reference

Once you've found a candidate, `web2-vuln-classes` and `web3-audit` (for
Solidity/Rust diffs) have the exploitation detail, bypass tables, and
severity-calibration guidance — this skill is about *scope and process*, not
per-class payloads.
