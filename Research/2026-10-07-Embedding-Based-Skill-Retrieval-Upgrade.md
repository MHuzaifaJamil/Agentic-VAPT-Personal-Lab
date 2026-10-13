# Upgrading the Skill-Corpus Matcher to Real Embedding-Based Retrieval

**Follow-up to:** `2026-10-07-FineTuning-GPU-Access-and-Maximizing-CYS-Models.md` §4, which
flagged this as the highest-leverage next step — needs no GPU, no fine-tuning, no ToS
navigation. This doc works out whether that claim actually holds up and what the concrete
upgrade would look like.

**What exists today** (Round 12, `01:FR-COUNCIL-07b`): a Szymkiewicz-Simpson token-overlap
coefficient (τ = 0.65) over a task's hypothesis/technique text against each skill's parsed
frontmatter/tags, with a ≥2-tag-intersection fallback. This is **lexical** matching — it
needs literal word overlap (or shared tags) between the task description and the skill file.
It cannot match "find other users' private data via a sequential ID" against a skill titled
"exploiting-idor-vulnerabilities" unless the task description happens to use the word "IDOR"
or a shared tag.

**What embedding-based retrieval adds:** a vector encoding of *meaning*, not word overlap —
the IDOR example above would match on semantic similarity even with zero shared vocabulary.
This is the real capability gap, not a marginal tuning improvement.

---

## 1. Embedding model — verified choice, not just a name

Checked against current (2026) comparisons, not a single blog's opinion:

- **`sentence-transformers/all-MiniLM-L6-v2`** is the consistently-recommended default:
  **23MB**, 384-dim output, Apache-2.0, described across multiple independent 2026 sources as
  "the best accuracy-per-compute-dollar ratio" and "unbeatable per millisecond on CPU." This
  is not a security-specific model — **no real security-domain embedding model was found**
  (one obscure, 22-download hit and nothing else) — but this is consistent with the actual
  RAG-for-pentesting literature surveyed in the prior doc (PentestAgent, VulnBot, etc. all use
  general-purpose embeddings over HackTricks-style chunked text, not a specialized embedder).
  General-purpose is the real-world norm here, not a compromise.
- **Quality step-up if ever needed:** `all-mpnet-base-v2` (768-dim, ~100-150ms/query on CPU) —
  heavier, likely unnecessary for a corpus this size (819 skill files).
- **A further speed option worth knowing about, probably unnecessary here:**
  `Model2Vec` distills any sentence-transformer into static token embeddings — up to 50x
  smaller, 500x faster, and the distillation itself takes ~30 seconds on CPU. Not needed given
  the throughput numbers below, but worth remembering if the corpus ever grows by orders of
  magnitude.

**CPU throughput — honest range, not a cherry-picked number:** published figures for
`all-MiniLM-L6-v2` on CPU range from ~40-100 sentences/sec (single-threaded, conservative) up
to 1,200+/sec with batching/ONNX optimization. Even at the conservative end, embedding the
entire 819-skill corpus (a few thousand chunks once frontmatter + operational sections are
split out) is a **one-time job well under a minute**, not a meaningful compute cost at all.
Per-task query-time embedding (one short hypothesis/technique string) is effectively
instant.

## 2. Storage/retrieval layer — `sqlite-vec`, not a new database

**A real currency check mattered here:** the older, more commonly-referenced
`sqlite-vss` (Faiss-based) **is no longer actively developed** — its own maintainer has
redirected effort to its successor, `sqlite-vec`. Verified `sqlite-vec` directly via the
GitHub API before recommending it: **8,164 stars, Apache-2.0, not archived, last pushed
2026-05-18** — real and current, not abandoned.

**Why this is the right fit specifically for Mugheeraat, not just a generically good tool:**
this project's entire state store is already a single SQLite file (`CLAUDE.md` §3: "State
Store: SQLite 3 with WAL... `busy_timeout`"). `sqlite-vec` is a dependency-free C extension
that adds vector columns and similarity search *directly inside* that same SQLite file — no
Pinecone/Weaviate/Qdrant server, no new storage technology, no new operational surface. The
skill embeddings can live in `state.db` itself (or a dedicated local `.db` file loaded
alongside it), consistent with the project's existing single-file-state philosophy rather
than adding a parallel system next to it.

## 3. Resource fit — this does not compete with the Council's single-residency constraint

`FR-GATE-02` enforces hard single-model-residency specifically because this host's RAM is
tight even for one 7-8B council model at a time. The embedding model does not create the same
pressure: **23MB is roughly 300-400x smaller than even the smallest council model** (Mistral-
7B-Instruct-v0.3's footprint, per `01`'s Council Roster table, is several GB). This is a
different *class* of model, not a smaller version of the same thing — it's realistic for it
to stay loaded continuously as a lightweight auxiliary process for the whole engagement
duration, rather than being loaded/unloaded per the Council's own model-swap discipline. No
new memory-settle gate or residency rule is needed for it.

## 4. Concrete integration sketch

1. **One-time indexing step** (new CLI command, or a startup/first-use hook): walk the skill
   corpus exactly as `skills_index.py` does today, chunk each skill's operational section
   (the same anchor-priority logic already used: Workflow → Common Scenarios → Steps →
   Instructions → Objectives → Core Concepts → Overview), embed each chunk with
   `all-MiniLM-L6-v2`, store the vectors in a `sqlite-vec` virtual table alongside the
   skill's identifying metadata.
2. **Matching at dispatch time**: embed the task's hypothesis/technique string once, query
   `sqlite-vec` for nearest neighbors by cosine similarity, apply a tuned threshold (a direct
   analog of the existing τ = 0.65 — needs its own real calibration pass against this
   project's own task distribution, not assumed from a generic default).
3. **Keep the existing token-overlap/tag match as a deterministic fallback**, not a discarded
   mechanism — this matches the project's own established graceful-degradation pattern
   (`oob_listener.py`'s degrade-on-absence behavior, `FR-DISCOVER-01`'s catalog-missing
   fallback): if the embedding index isn't built yet, or the embedding query fails for any
   reason, fall back to the current lexical matcher rather than silently returning no match at
   all.

## 5. Honest caveats — this is not a free lunch, just a cheap one

- Embedding similarity is still probabilistic, not exact — it will need its own real
  calibration against this project's actual task distribution (false-positive/false-negative
  skill matches), the same discipline every other threshold in this corpus already gets
  (`FR-COUNCIL-11a`'s zero-yield thresholds, candidate-detection's confidence cutoffs).
- No amount of research substitutes for actually building and testing this against real task
  descriptions from a real engagement — the same "test in your own lab before trusting it"
  conclusion every prior research round in this project has reached.
- This upgrade improves *what the Scripter is told about a technique it's already been
  assigned* — it does not address the deeper, already-identified problems this session found
  repeatedly (recon-input gaps like the Juice-Shop-SPA static-crawling limitation, or
  structured-output reliability). It's a real, cheap improvement to one specific mechanism,
  not a fix for the project's bigger open problems.

## 6. Bottom line

The claim from the prior doc holds up under scrutiny: this is genuinely GPU-free (23MB model,
CPU-fast), fine-tuning-free (a pretrained general embedding model, used as-is), and ToS-free
(nothing here touches any cloud service at all — fully local, consistent with
`05:SEC-DATA-01`). The concrete stack is `all-MiniLM-L6-v2` + `sqlite-vec`, both verified
current and real, both small enough to not compete with the Council's own residency
constraints. Worth prototyping before any of the model-swap options from the other research
docs, precisely because it's strictly cheaper to try and already matches how the real
RAG-for-pentesting literature does this.

---

*(Aside, re: the TPU Research Cloud publish-the-research requirement raised in the prior
doc — if you do end up wanting to publish any of this research yourself, that's entirely your
call to make, not something this doc is trying to steer you away from; it was flagged purely
because it conflicts with using TRC specifically for Mugheeraat's own private fine-tuning
work, not as a general objection to publishing.)*
