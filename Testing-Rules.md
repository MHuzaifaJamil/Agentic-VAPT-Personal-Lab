> **Scope.** Binding conventions for how this project's testing/benchmark work gets
> *written up*, not what testing itself must cover. Applies to every future engagement
> report, benchmark report, and probe writeup for the `implementation` repo. Referenced
> from `CLAUDE.md`.

---

## Rule 1 — Per-engagement summaries: max 5 sentences, 50–80 words

When reporting on a real engagement, benchmark run, or probe, the narrative summary for
it (what happened / why / how it was fixed, if anything broke) MUST be **5 sentences or
fewer, 50–80 words total**. Long "what happened and why it happened and how it was fixed"
narratives are hard to digest and bury the numbers that actually matter — keep them short
enough to scan in one pass.

This applies per-engagement, not per-document — a report covering 3 engagements gets 3
short summaries, not one long one covering all three.

## Rule 2 — Numbers go in the metrics tracker, not buried in prose

Every real timing/outcome data point (model load time, wall time, prompt/completion token
counts, tok/s, success/failure, RSS, or any other varying system metric) belongs in
`implementation/reports/LLM-Council-Benchmarks.md` as a table row — append, never
overwrite past rows — not only described in narrative text. A reader should be able to get
every number from that one file without reading a single full report.

## Rule 3 — Full narrative reports still have a place, just not as the primary record

A detailed `BENCHMARK-REPORT-<date>.md` (root-cause writeups, full methodology, the "how
it was fixed" detail) is still worth writing for anything non-trivial — but it lives in
`implementation/reports/`, and it is the *secondary*, deep-dive record. The 5-sentence
summary (Rule 1) and the metrics table (Rule 2) are the *primary* ones a future reader
should check first.

## Where these live

- Metrics/timing data: `implementation/reports/LLM-Council-Benchmarks.md`
- Full narrative reports: `implementation/reports/BENCHMARK-REPORT-<date>.md`
- This rule file: `source/Testing-Rules.md` (referenced from `source/CLAUDE.md`)
