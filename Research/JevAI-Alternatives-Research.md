# Local/Open-Source Jev-Style Decision Models — Research & Test Lab

**Context.** While diagnosing why Mugheeraat's `candidate_detection.py` misses real findings
(session investigation, 2026-09), a new class of model surfaced: TypeSafe AI's **Jev**, a
"System One" model that returns fast, typed, calibrated decisions instead of generated text.
Jev itself is a closed, cloud-hosted API — incompatible with this project's local-only
architecture (`05:SEC-DATA-01`/`03`). This doc tracks research into **local, open-source**
alternatives and hands-on testing of each, to see whether any is a credible input to
`candidate_detection.py` or Gate 1/Gate 3-style judgment calls.

**Host used for testing:** the Requirements-Specifying PC — CPU-only, 15GB RAM
(~2.5-5.8GB free during testing, shared with other processes), no GPU. This is a harder
environment than most of these projects' own benchmarks assume, which is itself informative.

---

## 1. Candidates identified

Found via `theseus-research` issue #76 (a personal research repo with an unusual
self-referential documentation style — see §5) and the `sfmqrb/awesome-decision-models`
curated list. Every repo below was checked directly against the GitHub API (stars, license,
creation date) before being trusted, not taken from blog summaries alone.

| Model | Repo | Stars | License | Created |
|---|---|---|---|---|
| GLiNER-PII | `knowledgator/gliner-pii-base-v1.0` (HF) | — | Apache-family | Pre-dates Jev by ~2yrs (NAACL 2024) |
| Laya | `NandhaKishorM/laya` | 28,116 | Apache-2.0 | 2026-09-18 |
| jeff (GliFormer) | `logan-markewich/jeff` | 261 | MIT | 2026-09-19 |
| SemIf | `TheoLeeCJ/SemIf` (was SemIf-OpenJev) | 4,554 | MIT | 2026-09-16 |
| Kev | `jaredpalmer/kev` | 7,780 | Apache-2.0 | 2026-09-17 |
| NanoJev | *(excluded, see §5)* | — | — | — |

**Not pursued:** NanoJev — the identical repo description appears duplicated verbatim across
at least 9 unrelated GitHub accounts (suzuke, T-Markus-Liang, chenyangcun, XinranSong,
cnzgray, sealofyou, kuishou68, TianyuCodings, bit-cook). That is a spam/bot-network pattern,
not a real single-author project. Excluded entirely rather than cloned from any of those
accounts.

---

## 2. Test methodology

10 ground-truth cases, written to mirror `candidate_detection.py`'s **real** Round 27 rules
directly (not generic benchmarks) — 5 genuine findings, 5 explicit negatives, including the
project's own documented noise-avoidance tests (a single email is not PII; a bare CORS
wildcard alone is not dangerous, only combined with `Access-Control-Allow-Credentials: true`):

`bulk_pii_leak · single_email_ordinary · directory_listing · clean_200_json · sql_error ·
generic_404 · api_key_leak · cors_wildcard_alone · cors_wildcard_with_credentials ·
ssn_credit_card`

Each model was queried with either its native entity-extraction API (GLiNER) or a single
holistic yes/no ("does this text contain a genuine security finding?") typed-decision
question, phrased identically across Laya/jeff/Kev/SemIf so the comparison is fair. Full test
case text and harness scripts live alongside this file (`test_cases.py`, `run_*.py`).

---

## 3. Results

| Model | Score | Avg latency (warm) | Model load | Notes |
|---|---|---|---|---|
| **GLiNER-PII** (base, threshold 0.65) | **6/10** (4/4 on true entity types) | ~140ms/case | 5.5s (cached) | See §3.1 |
| **Laya** (typed-decisions) | 6/10 | ~450ms/case | 0.1s + 192s first-call warmup | See §3.2 |
| **SemIf** (Qwen3-0.6B, llama.cpp CPU) | 4/10 | ~4s/case | ~10s | See §3.3 |
| **jeff / GliFormer-large** | 3/10 | ~1.4s/case | 21.3s | See §3.4 |
| **Kev-0.8B** | 4/10 | ~910ms/case | ~40s (download+load) | See §3.5 |

### 3.1 GLiNER-PII

Raw entity-extraction model, not a general decision engine — tested by asking it to find
labels (`email address`, `api key or secret token`, `credit card number`, `social security
number`, `sql error message`, `directory listing`, `dangerous cors misconfiguration`) and
treating "any hit above threshold" as `is_finding`.

- **4/4 perfect** on its actual trained competency: `bulk_pii_leak`, `api_key_leak`,
  `ssn_credit_card` all correctly flagged (confidence 0.68–0.94); `single_email_ordinary`
  correctly NOT flagged at threshold 0.65 (though its raw email-detection confidence was
  0.94 — high because it correctly found an email, the *count* logic that makes it "not a
  finding" is a downstream rule, not something GLiNER itself encodes).
- **0/3 on free-text/compound judgments**: `sql_error`, `directory_listing`,
  `cors_wildcard_with_credentials` — architecturally, a single-pass entity extractor cannot
  express "if header A and header B are both present." Out of its design scope, not a bug.
- Threshold tuning (0.4 → 0.65) traded 2 false positives for 2 false negatives — a real
  precision/recall knob, not a free win.
- Fast and small once cached; first download took 313s (mostly network, not compute).

### 3.2 Laya (typed-decisions checkpoint)

Uses its native Choice/Score/Noul API (`Router().predict(text, questions)`), which should be
the best-suited interface of the group for this kind of holistic judgment.

- **Self-reported calibration defect** at load time: `RuntimeWarning: this checkpoint ships
  invalid temperatures or values outside [0.5, 5]... Treat confidence from the affected
  entries as uncalibrated.` This is the checkpoint disclosing its own problem, not something
  inferred.
- Got the hardest compound case **wrong in both directions**: `cors_wildcard_alone` (safe)
  flagged True at 0.73 confidence; `cors_wildcard_with_credentials` (dangerous) flagged False
  at 0.31 confidence — the opposite of a defensible judgment.
- `generic_404` flagged as a finding at 0.96 confidence — a severe false positive on
  completely benign content.
- First real inference call took **192 seconds** (one-time JIT/weight-materialization cost,
  not reflective of the router's own "33ms" marketing figure, which assumes a warmed GPU
  path); subsequent calls were ~400–500ms on this CPU host.

### 3.3 SemIf (methodology test, Qwen3-0.6B via llama.cpp CPU backend)

SemIf isn't a model — it's a technique: read typed-option probabilities directly off an
existing open LLM's logits, no generation, no JSON parsing. Ran via its real `semif-score`
CLI against a genuine llama.cpp CPU backend (`Qwen3-0.6B-Q8_0.gguf`, the smallest model this
host's RAM budget allowed; SemIf's own published benchmarks use a 4B model).

- 4/10 — the worst score of the live-tested set, but with a clear, honest explanation: the
  model was **systematically under-confident on genuine findings** (`sql_error` scored
  P(finding)=0.019, `api_key_leak`=0.105, `ssn_credit_card`=0.164, `bulk_pii_leak`=0.011) —
  consistent with a model too small to make this judgment reliably, not a flaw in the
  read-logits-directly technique itself.
- Notably, it's the **only** candidate that correctly resolved the CORS+credentials case
  (0.965 — the one case Laya got backwards and GLiNER can't express at all).
- Real, working CPU-only path with no GPU — directly reuses the exact runtime
  (`llama.cpp`) this project's own Council already depends on, which is a genuine integration
  advantage over the others if a larger base model were used.
- Real cost: needs an existing open LLM (2B–27B in its own docs); a small one is fast but
  weak, a good one needs multiple GB of RAM this host didn't reliably have spare.

### 3.4 jeff / GliFormer-large

Getting this running took two attempts (see §4 for the real engineering cost). Once working,
via jeff's own `TorchBackend`/`Engine` classes (not a generic loader):

- 3/10 — the worst live-tested result. Several cases came back **inverted**:
  `single_email_ordinary` (should be low) scored 0.80; `clean_200_json` (should be low) scored
  0.70; `bulk_pii_leak` (should be high) scored 0.20.
- Correctly resolved `cors_wildcard_with_credentials` (0.84) and `ssn_credit_card` (0.79).
- GliFormer's own HF tags (`named-entity-recognition`, `relation-extraction`,
  `structured-extraction`, `document-understanding`) suggest it's tuned for structured
  extraction, not open-ended "is this a security finding" judgment calls — the mismatch
  between its training distribution and this test's phrasing is the likely cause, not
  necessarily a defect in the model itself.
- 21.3s load once cached (904MB download, ~8 min first time), ~1.4s/case inference.

### 3.5 Kev-0.8B

Ran the real `kev.serve` HTTP server (`python -m kev.serve --run jaredpalmer/kev-0.8b`,
downloads and merges the LoRA adapter onto `Qwen3.5-0.8B-Base` on first run), queried over
real HTTP with the identical typed-decision question used for Laya/jeff.

- 4/10, but the cleanest failure pattern of any candidate: **every single `noul` score fell
  between 0.15 and 0.38** — it never once crossed the 0.5 threshold, not even for the most
  blatant findings (`bulk_pii_leak`=0.23, `sql_error`=0.38, `api_key_leak`=0.30,
  `cors_wildcard_with_credentials`=0.18). It got the 4 true negatives right purely because it
  says "not a finding" almost unconditionally.
- Consistent with SemIf-0.6B's pattern (§3.3): the smallest checkpoint in a size family is not
  capable enough for this specific judgment, even more pronounced here since Kev-0.8B never
  flipped even slightly toward "finding." Kev's own published benchmarks show real accuracy
  gains at 4B/9B/27B (Brier scores improving from 0.481 at 0.8B to 0.236 at 27B on "new
  sources") — this result says nothing about those larger sizes, which this host's RAM
  couldn't test.
- Real HTTP round-trip ~910ms/case including network overhead — genuinely fast, matching
  the project's own latency goals if a larger, more capable checkpoint were used.
- Straightforward to get running once Python 3.13 + `uv` were in place — official server,
  official client shape, no reverse-engineering needed (contrast with jeff, §4).

---

## 4. Real engineering cost (a comparison dimension in its own right)

Not just accuracy — how much friction each candidate added, observed directly:

- **GLiNER-PII**: trivial. `pip install gliner`, `GLiNER.from_pretrained(...)`,
  `model.predict_entities(text, labels)`. No custom serving code needed.
- **Laya**: trivial. `pip install laya`, `Router().predict(text, questions)`.
- **SemIf**: moderate. Needs `pip install -e '.[llamacpp]'`, a GGUF download, and knowing the
  right `--model`/`--revision` HF reference for prompt construction even when scoring via a
  local GGUF file. CLI is JSONL-file-based, not a Python function call.
- **jeff**: high. The generic `gliner` package **cannot load this checkpoint**
  (`KeyError: 'layout-deberta'` — a custom encoder architecture). Needs the dedicated
  `gliformer` package, which is a large multi-modal document-processing library (vision/
  audio/layout/PDF task heads) — got it working only by reading jeff's own test suite
  (`tests/conftest.py`, `tests/test_torch_backend.py`) to find the correct
  `TorchBackend`/`Engine`/`SystemOneRequest` construction, not from jeff's own README alone
  (which hides all of this behind a full HTTP server).
- **Kev**: high. Ships as a LoRA adapter only — needs a separate ~1.6GB base-model download
  (`Qwen3.5-0.8B-Base`) plus the adapter, requires exactly Python 3.12/3.13 (its own docs:
  "torch has no wheels for 3.14 yet"), and `uv`.
- **Real infrastructure lesson, not model-specific**: the scratchpad directory used for this
  lab sits on a 7.7GB **tmpfs**, not the real 131GB disk. jeff's install alone pulled ~2.5GB
  of unused NVIDIA/CUDA libraries (this host has no GPU) and filled it completely, aborting
  mid-install with `No space left on device`. Fixed by moving the whole lab to
  `/home/vscysteam/decision-model-lab` (real disk) and forcing CPU-only torch via
  `UV_TORCH_BACKEND=cpu`. Worth remembering: **none of these projects reliably auto-detect
  "no GPU present" and skip the CUDA wheels** — every one of them defaulted to downloading
  multi-hundred-MB to multi-GB NVIDIA packages on a CPU-only host unless explicitly told not
  to.
- Running multiple `uv`-based installs concurrently caused real **lock contention** on the
  shared `~/.cache/uv` wheel cache (one install timed out after 300s waiting on another's
  lock). Serializing installs fixed it.

---

## 5. A note on the research trail itself

The `theseus-research` GitHub issue that surfaced this whole candidate list has an unusual,
almost ritualistic documentation style — self-generated "receipts" with commit hashes and
SHA256s for its own blog posts, formalized tags like `ECOSYSTEM_ADOPTION_SIGNAL = STRONG`, a
"1F916 companion" logging system, a non-English "Blog Шута" editorial record. Two of its cited
claims (Simon Willison's blog, LangChain's official blog) were independently verified against
the real, primary sources and checked out. Its other claims (Pydantic AI, LiteLLM, Vercel
Connect, SuperQode, "JevBench scoring 93 systems") were **not** independently re-verified here
and should be treated as unconfirmed rather than accepted on the thread's own say-so. Separate
from all of that, NanoJev turned out to be an actual spam pattern (§1) — a concrete example of
why every specific claim in this space needs checking against a primary source (GitHub API,
official blog, etc.), not trusted because it appears in a well-organized-looking research
document.

---

## 6. Verdict

**None of these is ready to replace `candidate_detection.py`'s deterministic rules.** A clear
pattern emerged across all 5 live tests, ranked by what was actually observed:

1. **GLiNER-PII** — the one candidate with a real multi-year track record (NAACL 2024) and a
   clean, honest failure boundary (fails by not firing, never by inverting). Best fit: a
   second signal feeding the *existing* `_bulk_pii_signal`/secret-detection logic specifically
   for the PII/secret sub-problem, not a replacement for the whole rule set. **The only
   candidate worth acting on from this lab.**
2. **Small models are the dominant confound, not architecture.** SemIf-0.6B and Kev-0.8B —
   the two smallest models tested — both failed the same way: systematically under-confident,
   almost never crossing the "finding" threshold even for blatant cases. This looks like a
   model-capacity ceiling, not a flaw in either project's actual technique. Kev's own
   published numbers show real accuracy gains up to 27B; none of that range was testable on
   this host's RAM.
3. **Laya and jeff are the two genuine red flags.** Both didn't just score low — they
   produced *inverted* judgments on real cases at real confidence (Laya: safe CORS flagged
   0.73, dangerous CORS flagged 0.31; jeff: an ordinary single email flagged 0.80, a real bulk
   PII leak flagged 0.20). A model that's confidently wrong is worse than one that's honestly
   unsure — this is the actual failure mode a security pipeline needs to guard against most,
   and it's the one two of these five candidates exhibited.
4. **SemIf's technique** (read logits off an existing LLM, not a shipped checkpoint) is the
   one worth revisiting if larger local hardware becomes available — it reuses this project's
   own llama.cpp runtime directly and was the only candidate to correctly resolve the hardest
   test case.

No candidate here should be wired into anything without: (a) re-running with a properly-sized
model (4B+) where RAM allows, (b) expanding the test set well past 10 cases, and (c) an
explicit Human Operator decision, given every one of these is 2 weeks old with zero
security-domain validation before this lab.
