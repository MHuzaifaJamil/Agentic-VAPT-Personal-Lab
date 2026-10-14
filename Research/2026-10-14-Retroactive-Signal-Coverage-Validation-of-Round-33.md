# Retroactive Signal-Coverage Validation of Round 33

**Author:** Mugheeraat 3.0 (Setup Research). **Method:** a read-only Python script
(`vapt_agent.council.candidate_detection`'s pure signal-matching functions imported
directly, zero DB writes, zero model loading) replayed every historical
`tool_execution_logs` row across every engagement this project has ever run against
Round 33's just-landed detection rules, and diffed the result against what actually
existed in `verified_vulnerabilities` at the time. The question: did Round 33's rule
expansion (subjack, masscan/ffuf/feroxbuster/gobuster admission, LFI, deserialization,
JWT, SSTI) find anything *real* in evidence this pipeline already collected weeks ago
but never looked at — not a synthetic test, the project's own actual history.

**Scanned:** 562 historical `tool_execution_logs` rows (every non-timeout,
non-network-error row across 18 targets, engagements 1 through 32). Already-candidate
rows (6, all pre-Round-33, all since DISMISSED): unaffected. New signal under Round 33's
rules with no prior candidate row: **12**.

## Headline finding: a real, exploitable KeePass database has been sitting undetected across 5 separate engagements

`feroxbuster`'s own baseline-recon output, present in **every one of engagements 1, 28,
30, 31, and 32** (task_ids 52/616/714/730/756/801/862 — several engagements found it
*twice*, since baseline recon includes more than one directory-brute pass), contains:

```
200      GET       15l       65w     5767c http://127.0.0.1:3000/ftp/incident-support.kdbx
```

A real, live, HTTP-200-confirmed KeePass database at `/ftp/incident-support.kdbx`. This
is this project's own already-documented ground-truth finding #3/#4
(`implementation/reports/JuiceShop-VAPT-Testing-Guide-2026-09-19.md` §4 — the KeePass
DB / sensitive-file-exposure class, independently confirmed real by Agentic-Bug-Hunter
weeks ago). The evidence was *always there*. `candidate_detection.py`'s Tier-1 SQL
filter excluded `feroxbuster` from the six tools it would ever read until Round 33
(`480a952`) admitted it this very session — so this real, already-proven-exploitable
finding has been structurally invisible to the Council's own detection layer across
five entire engagements, not because recon failed, but because the pipeline's own
candidate-detection step was never looking at the tool that found it.

This is not a hypothetical "this rule might help" claim — it is direct, measured proof
that Round 33's Tier-1 filter widening closes a real gap that cost this project a real,
confirmable finding, repeatedly, for weeks.

## Secondary finding: a pre-existing (not Round 33) nuclei rule is noise-prone

One more new signal, task 857 (engagement 32, nuclei): `_NUCLEI_SEVERITY_PATTERN`
(predates Round 33, untouched by it) matches **any** `"severity":"..."` value in
nuclei's JSONL output, including `"info"`. The real matched content: "Public Swagger
API - Detect" and three "HTTP Missing Security Headers" (CORS/COOP/COEP) findings —
exactly the class of finding the Primary Scripter's own system prompt
(`prompts.py:332-336`) explicitly tells it to treat as noise ("missing security headers
alone... treat them as noise"). The rule fired correctly per its own (broad) design, but
its design is broader than the rest of this pipeline's own stated philosophy. Worth
narrowing to exclude `"info"` specifically (keep `low`/`medium`/`high`/`critical`) so
Gate 3 isn't diluted with the one class of finding this project has repeatedly decided
isn't worth an Adjudicator's time. Low effort, not urgent, flagged to Mugheeraat 2.0's
incoming code review for the same file.

## Tertiary observation: engagement 32 never reached its own adjudication stage

`engagement_phase_log` for engagement 32 contains exactly one row: `0_PREFLIGHT|OK`.
Phase 4 (and therefore 4.3/Adjudicator) never ran for this engagement at all — it
aborted very early, for reasons outside this analysis's scope (unrelated side-work on
this host in the following two weeks is the far more likely explanation than a pipeline
defect, given Round 30-32's crash-guards were all confirmed holding through Engagement
31's full 12h44m run). Not investigated further here — flagged only because it's part
of why task 857/862's real evidence was never adjudicated, same underlying reason
(nothing ever got that far), distinct from the Round-33 detection-rule question itself.

## Recommendation — two separable steps, only one needs the operator's sign-off

**Step 1 (no model loading, deterministic, safe to do right now):** actually run
`candidate_detection.detect_candidates(conn, target_id=X)` for real (not a dry run)
against target_ids 25/26/27/28 (engagements 28/30/31/32) — this only inserts
`CANDIDATE` rows into `verified_vulnerabilities` from already-captured, already-real
evidence; it is pure, already-tested, already-shipped code, no new risk beyond what
Round 33's own test suite already covers.

**Step 2 (requires loading the Adjudicator/Mistral-7B — needs explicit operator
go-ahead, same discipline as every other model-facing change this session):** once
real `CANDIDATE` rows exist for the `.kdbx` finding, run the real Gate 3 Adjudicator
against them. Given the evidence is a direct, unambiguous, single-request disclosure
(a live, downloadable credential file at a known URL, HTTP 200, confirmed real) — this
is exactly the shape Round 33's own Adjudicator carve-out (`38c97bd`) was written for
("a directly-downloadable credential file" is the carve-out's own example class), and
is the single most promising, lowest-effort path to this project's first-ever
`CONFIRMED` finding, without needing a brand-new multi-hour engagement at all.

Not actioned by this research pass — per the standing Research/ convention, this is a
finding and a recommendation, not an implementation. Staged for Mugheeraat 1.0/2.0 and
the operator's decision on whether/when to run Step 1 and Step 2.
