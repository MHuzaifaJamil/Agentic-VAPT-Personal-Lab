---
description: Review a git diff, PR, or commit for security issues introduced/exposed by the change — diff-scoped, not a full repo audit. Usage: /diff-review [PR number | commit sha | base...head]
---

# /diff-review

Security review of a change set (PR / commit / branch diff), not the whole
repository. Loads the `diff-review` skill and applies `triage-validation`'s
closure discipline to every candidate before anything gets written up.

## Usage

```
/diff-review                     # reviews the current branch vs its base
/diff-review 482                 # reviews GitHub PR #482 (gh CLI)
/diff-review abc1234              # reviews a single commit
/diff-review main...feature/x     # reviews an explicit range
```

## What This Does

1. Resolves the diff (`git diff`, `git show`, or `gh pr diff`) and builds a
   changed-files coverage checklist
2. For each changed file: added files reviewed whole; modified files
   reviewed from the changed hunks outward (caller, middleware, sibling
   functions); deleted files treated as context only
3. Flags anything in scope per the `diff-review` skill — new vulnerabilities,
   pre-existing sinks newly reached, weakened shared controls, removed
   checks, invalidated assumptions elsewhere in the codebase
4. Runs every candidate through closure discipline (`confirmed` /
   `ruled_out` / `open_proof_gap`) before it's allowed to become a finding
5. Attempts dynamic validation if the app/service is reachable; otherwise
   files a reduced-confidence static trace and says so explicitly
6. Routes output: bug-bounty whitebox scope → `/validate` then `/report`;
   client VAPT engagement → a numbered report per `CLAUDE.md`'s format, or
   the `INFO-NNN` register if it doesn't clear the reporting bar

## Out of Scope (on purpose)

Pre-existing bugs unrelated to this diff are noted, not filed against the
PR/commit under review — that's a separate full whitebox pass. This command
answers "did this change make things worse," not "is this codebase secure."

## After

Report the changed-component coverage (reviewed-and-clean vs findings) so
whoever asked for the review knows what was actually checked, not just what
came back positive.
