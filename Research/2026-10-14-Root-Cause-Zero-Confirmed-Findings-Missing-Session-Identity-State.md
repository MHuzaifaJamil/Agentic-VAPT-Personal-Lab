# Root Cause of Zero CONFIRMED Findings: Missing Session/Identity State Across Tool Invocations

**Author:** Mugheeraat 3.0 (Setup Research). **Trigger:** the operator redirected this
session's priority to "how to enable Mugheeraat to find some vulnerabilities in any system."
This is a direct, evidence-based answer, independent of the Juice-Shop-specific recon-gap
fix already written up and already acted on (the KeePass/`.kdbx` feroxbuster finding —
12 real `CANDIDATE` rows now exist in the live DB, inserted today by Mugheeraat 1.0).

## The hard number

`verified_vulnerabilities` across this project's entire history: **12 CANDIDATE, 6
DISMISSED, 0 CONFIRMED, 0 REMEDIATED, 0 ADJUDICATION_FAILED.** `model_invocation_logs` shows
exactly 6 historical Adjudicator (Gate 3) calls ever ran — and **all 6 returned DISMISSED.**
This research traces *why*, down to the exact commands, not just the verdict text.

## What all 6 historical DISMISSED verdicts actually said

Every `gate3_rationale` (verified directly, not summarized) gives the same reason in
slightly different words: *"no baseline request/response, no attack request/response, no
diff that concretely demonstrates the claimed impact... only shows something that is
technically possible."* This is the Adjudicator's own check #3 (`council/prompts.py:442-459`,
`ROLE_BLOCK_ADJUDICATOR`) — evidence structure must be baseline/attack/diff, unless (its own
explicit carve-out) the response body is independently, self-evidently conclusive.

## Tracing it upstream: what these 6 candidates' commands actually were

`task_queue.proposed_command` for each of the 6 (all `curl/script HTTP probe`-class
candidates, vulnerability_class IDOR x2, CSRF x3, BFLA x1):

```
663  curl -X GET  http://127.0.0.1:3000/upload?id=1
678  curl -X POST http://127.0.0.1:3000/change-password -d "username=otheruser&new_password=weakpass"
689  curl -X GET  http://127.0.0.1:3000/upload?id=1                              (repeated guess)
693  curl -X POST http://127.0.0.1:3000/change-password -d "username=otheruser&newpassword=weakpass"
823  curl -X POST http://127.0.0.1:3000/change-password -d "username=otheruser&newpassword=weakpass"
829  curl -X GET  http://127.0.0.1:3000/api/Feedbacks/
```

Read task 663's actual raw evidence (artifact `663_curl_..._0000.raw`): the response body is
Juice Shop's Angular SPA shell `index.html` — the exact trap the Adjudicator's own prompt
names by name ("a single-page app's client-side router serving its own shell page is the
common case" — a bare 200 that proves nothing). **None of the 6 commands carry any
`Cookie`/`Authorization` header, and none pair an authenticated request with a second,
different-identity request.** They are single, anonymous, stateless probes against guessed
endpoint names — not a formatting problem, a *capability* problem: IDOR requires showing
identity A reading identity B's data (the Adjudicator's own check #2, "identity/session
check"); CSRF and BFLA equally depend on an authenticated victim/privilege-level context. No
anonymous single request can ever satisfy that bar, for any of these three vulnerability
classes, on any target — these 6 were correctly dismissed, but they were never confirmable
to begin with, by construction.

## The actual gap: no session/identity-state mechanism exists anywhere in this codebase

Checked exhaustively, not assumed:

- **Zero of 92 historical `curl` tasks, ever, used a cookie jar** (`grep` for `-c `/`-b `/
  `--cookie-jar` across every `task_queue.proposed_command` row returns 0 matches).
- **No cross-task variable-passing/templating mechanism exists in the codebase at all** —
  searched for any `{token}`/`captured_cookie`/`session_var`/similar pattern across
  `vapt_agent/`; nothing. Each task is one isolated `subprocess.Popen(shell=False, argv=...)`
  call (per `CLAUDE.md` Directive 2); nothing threads a value captured from one task's
  output into a later task's command.
- **No prompt instruction tells the Scripter/Strategist how to obtain or carry forward an
  authenticated identity.** `council/prompts.py:337-338` states the bar ("data exposure
  across two identities") but never says how to get there — no guidance to register/log in,
  capture a session artifact, or reuse it.

This is this project's **third** layer of the same underlying investigation.
`bridge/tier2.py:20-33` and `bridge/denylist.py:94-108` both document two *earlier* real
fixes under the identical heading "root-cause investigation into zero confirmed
vulnerabilities across every real engagement" (2026-09-22): first, Scripter commands weren't
emitting a parseable HTTP status (fixed by forcing `-w` status markers); then headers weren't
captured either (fixed by forcing `-D -`, Round 33). Both fixes correctly addressed *detection
blindness* — making candidate_detection able to see signal that was already there. **Neither
fix, nor anything since, addresses this third layer: even with perfect detection, an entire
class of vulnerability (anything requiring two identities or an authenticated session —
IDOR, BFLA, CSRF, broken access control generally, one of the most common bug classes in any
real system) can never produce Adjudicator-satisfying evidence, because the execution layer
has no way to establish or carry forward a session at all.**

## Secondary finding: the fix for this would currently have a safety gap

`bridge/denylist.py:94-108` (`check_behavioral_denylist`'s rule (c), the file-write
confinement check) only inspects `output_flags = {-o, -O, -oA, -oN, -oX, -oG, --output,
--out}`. Curl's `-c`/`--cookie-jar` (write) and `-b`/`--cookie` (read) are **not** in that
set — so if a Scripter command starts using `-c <path>` (the natural, obvious fix for this
problem), its write destination is **not** checked against the artifact-store confinement
rule that `-o`/`--output` already enforces. This is currently latent (never exercised, since
`-c` has never been used), but would become live the moment session-state support is added,
and is also a second-order instance of the prompt-injection concern from this session's
other research doc today — if a manipulated Strategist/Scripter proposes `-c
/some/path/outside/artifacts`, nothing currently stops it.

## Recommendation (not actioned — research only, per this project's Research/ convention)

1. **Add a deterministic, non-LLM session-bootstrap step** for targets with self-service
   registration (confirmed feasible for Juice Shop specifically, generalizes to any app with
   a standard register/login flow): register at least two distinct test accounts once per
   engagement, capture each one's session cookie/JWT via a fixed, scripted request (not an
   LLM-proposed one), and persist each under a predictable path inside `artifacts_dir` (e.g.
   `{artifacts_dir}/{engagement_id}/session_user_a.jar`).
2. **Teach the Scripter, via an explicit `council/prompts.py` instruction, to use `-c
   {path}`/`-b {path}` with those fixed, predictable paths** — giving every future IDOR/BFLA/
   CSRF command a concrete, repeatable way to act "as user A" and compare against "as user B"
   within the existing one-task-per-command architecture, no cross-task variable-passing
   engineering required.
3. **Close the secondary gap**: add `-c`, `--cookie-jar`, `-b`, `--cookie` to
   `bridge/denylist.py`'s `output_flags` (or a parallel check) so cookie-jar paths get the
   same artifact-store confinement `-o`/`--output` already has, before this capability goes
   live.

This is the single most generalizable, highest-leverage fix available right now toward the
operator's stated goal — it is not Juice-Shop-specific (the missing capability is architectural,
not target-specific) and it targets the exact vulnerability-class family (identity/
access-control bugs) that both the Adjudicator's own prompt and real-world VAPT practice treat
as a primary target class. Staged for Mugheeraat 1.0/2.0 and the operator's decision on
scope/timing.
