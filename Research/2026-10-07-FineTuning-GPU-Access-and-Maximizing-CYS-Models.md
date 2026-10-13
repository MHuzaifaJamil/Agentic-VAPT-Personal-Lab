# Fine-Tuning Cybersecurity-Capable Open-Weight Models, Free/Cheap GPU Access, and Maximizing Them

**Follow-up to:** `2026-10-07-Domain-FineTuned-Pentest-Models-CIPHER-xOffense-and-Alternatives.md`.
That doc surveyed existing fine-tunes; this one covers building your own, where to get the
GPU to do it, and how to get the most out of whichever model ends up in a council role.

---

## 1. Open-weight cybersecurity model landscape — benchmarks exist, trust them less than a real test

Real, published benchmarks exist specifically for this domain: **CyberSecEval2** (Meta,
measures code security + prompt-injection resistance + a "false refusal rate" metric —
directly relevant to the refusal-friction question from the abliteration research),
**CTIBench** (NeurIPS 2024, evaluates 11 models on threat-intel tasks), **SecBen** (dynamic
leaderboard, 14 models including cybersecurity-domain ones), and **CAIBench** (2026, a
meta-benchmark specifically for cybersecurity AI *agents*, not just raw Q&A — closer to what
Mugheeraat's Council actually is).

**A real, important caveat found while checking this:** a dedicated reliability audit —
["Benchmark Scores Are Pipeline-Dependent"](https://arxiv.org/pdf/2609.08765) (Berriche,
Shalby, Alhanahnah, Boshmaf) — found that **the same model gets substantially different
scores depending on the evaluation harness's own implementation choices** (prompt formatting,
response parsing, scoring logic). Published rankings in this space are measurably less stable
than they look. This reinforces every prior research round's conclusion in this project:
**a real test-lab run against this project's own ground-truth cases is worth more than any
published leaderboard position** — the leaderboard itself is known to be unreliable, not just
potentially irrelevant to this specific hardware/use case.

## 2. Fine-tuning your own — concrete, verified numbers

**Tooling:** `Unsloth` is the dominant tool for this at the 7-8B scale — 2x faster, ~70% less
memory than a standard LoRA pipeline, purpose-built for consumer/single-GPU fine-tuning.

**Real VRAM numbers for a 7-8B model** (confirmed across multiple 2026 sources):

| Method | VRAM needed |
|---|---|
| Full fine-tune (16-bit) | ~112 GB — datacenter-only |
| Standard LoRA (16-bit) | ~16 GB |
| QLoRA (4-bit, Unsloth) | **~6-8 GB** |

QLoRA at 6-8GB VRAM is realistic on a **free-tier cloud GPU** (a T4 has 15-16GB — comfortable
headroom even for QLoRA plus overhead). This is the single most important practical fact from
this research round: **fine-tuning a 7-8B security model is not a datacenter-scale
undertaking** — it's within reach of a single free Colab/Kaggle session, hardware-wise.

**What this project's own hardware can't do:** Unsloth's speed advantage comes from custom
Triton/CUDA kernels — it has no meaningful CPU path. This host (CPU-only, no GPU) **cannot do
the fine-tuning step itself**, regardless of how small the dataset is. Inference on a
fine-tuned result (via GGUF/llama.cpp, as already established) is fine locally; the training
step itself needs a GPU somewhere.

## 3. Free/cheap GPU access — real, checked against actual ToS text, and the realism answer is mixed

### Free-tier notebook platforms

| Platform | What's offered | Content restriction relevant to this project |
|---|---|---|
| **Google Colab** | 15-30 hrs/week, T4/P100, 12h session cap, no credit card | Its own managed-runtime policy **explicitly names "password cracking" as a disallowed activity**, alongside DoS, proxy circumvention, and deepfakes. This is a direct, named conflict with this project's own `FR-CRED` credential-attack domain specifically — not a vague "offensive content" worry, an actually-named prohibition. |
| **Kaggle** | 30 hrs/week guaranteed, T4/P100, 9h sessions, more reliable availability | Bans "malicious activity" and "harmful or offensive content" in vaguer terms — real enforcement has included removing notebooks; a real incident search also turned up 140+ hardcoded credentials found in public Kaggle notebooks, i.e. Kaggle does actively watch for security-sensitive content on the platform. |
| **Lightning AI** | 80 free GPU-hrs/month, persistent workspace, phone verification | Vaguer wording ("no purpose prohibited by U.S. law," no "malicious computer programming codes") — plausibly more permissive for *authorized* fine-tuning work than Colab's named list, but this is a reading of the ToS text, not a tested-in-practice confirmation. |

### Academic/research-grant style programs

- **Google TPU Research Cloud (TRC)** — up to 110 free Cloud TPUs, real and substantial. **But
  participation requires agreeing to conduct research "in accordance with Google AI
  Principles" AND to publish the work** (peer-reviewed paper, open-source code, or blog post).
  This is a real, structural conflict with this project's entire operating posture — Mugheeraat
  is explicitly local-only, operator-controlled, and not something this project's own
  `05:SEC-DATA-01` local-only/no-telemetry stance is compatible with publishing. Not a fit,
  independent of any content concern.
- **AWS Cloud Credit for Research** / **Azure Research Credits** — both real, both offer GPU
  compute credits to academic researchers. These are closer to raw IaaS rental (see below)
  than a managed-notebook content policy — worth distinguishing from Colab/Kaggle specifically
  because of what that distinction means for permitted content (next section).

### The important distinction this research surfaced: managed notebook platform vs. raw GPU rental

Colab/Kaggle/TRC are all **managed services with their own specific, named content
policies** layered on top of the generic "don't do anything illegal" boilerplate — that's
where "password cracking" gets named explicitly. **Raw GPU rental** (an AWS/Azure GPU VM you
fully control, or marketplaces like **RunPod**/**Vast.ai**/**Lambda Labs**, real pricing
found: under $1/hr for an A100 or RTX 4090) is governed by a much more generic
acceptable-use policy (no illegal activity, no attacking *other* tenants) — you're running
your own code on your own rented machine, not inside someone else's curated notebook
environment. This is a meaningfully different risk profile, and it's also where the actual
open-source fine-tuning community does most of this kind of work in practice (informal
signal, not a cited policy: these marketplaces show up constantly in guides for
edge-case/permissive-content fine-tuning precisely because enforcement is lighter than on a
big consumer platform).

### Is it realistic? — direct answer

- **For general cybersecurity-knowledge fine-tuning** (CTF writeups, CVE/vuln data,
  defensive content): yes, realistically achievable on a free Colab/Kaggle T4 session with
  QLoRA+Unsloth, no ToS conflict apparent.
- **For anything touching the credential-attack domain specifically** (`19:FR-CRED-01`'s
  hashcat/cupp/trevorspray/kerbrute pipeline, or training data that looks like password
  cracking): **Colab's own policy explicitly forbids it by name.** Use a different path —
  academic AWS/Azure research credits or a cheap raw GPU rental (RunPod/Vast.ai/Lambda),
  neither of which name this activity specifically.
- **For anything meant to stay private** (which, per `05:SEC-DATA-01`, is this entire
  project): TRC and similar publish-your-work programs are structurally wrong regardless of
  content concerns — not a fit, full stop.
- **Cost reality if going the paid-but-cheap route:** sub-$1/hr GPU rental for a few hours of
  QLoRA fine-tuning on a 7-8B model is a realistically small, one-time cost — likely a better
  default recommendation than threading the ToS needle on a free platform for anything in the
  credential-attack domain.

## 4. Using a cybersecurity model "to its extreme potential" — the literature converges on the architecture Mugheeraat already has

Searched specifically for how real pentesting-LLM research projects maximize model
effectiveness (not raw model swaps). The consistent pattern across `PentestAgent`, `VulnBot`,
`Autopentest`, `AutoPT`, `PTFusion`:

1. **RAG over a real security knowledge corpus is the standard augmentation**, typically
   HackTricks/HackingArticles-style content chunked (~750 words) into a vector database,
   retrieved at inference time. **Mugheeraat already does a version of this** — Round 12's
   task-dispatched knowledge ingestion (`01:FR-COUNCIL-07b`) matches task hypotheses against a
   local 819-skill corpus and injects the matched operational section as a `<task_reference>`
   block. The gap relative to the literature: this project's matcher is token-overlap/tag-based,
   not true embedding-based retrieval over chunked documents — a real, concrete upgrade path if
   more coverage/precision is ever wanted, not a new capability to invent from scratch.
2. **Long-term memory over MITRE ATT&CK/CVE-NVD/CAPEC** is the other standard augmentation —
   `19:FR-TOOL-18`'s fingerprint-triggered EOL/CVE lookup is this project's existing analog,
   narrower in scope (reactive, triggered by a tech-fingerprint sighting) than a full
   always-available ATT&CK/CAPEC knowledge base, but the same underlying idea.
3. **Multi-agent Planner/Executor splits with tool-calling, not a single monolithic model** —
   already covered in the prior research doc; the Council's Strategist/Scripter split is
   already this pattern.

**Conclusion: this project's architecture is not behind the state of the art here — it
already implements the two dominant augmentation patterns (skill-corpus RAG, fingerprint-
triggered enrichment) the literature converges on.** The highest-leverage next step, if one is
wanted, is upgrading the *existing* skill-matcher from token-overlap to real embedding-based
retrieval (a vector DB over the same 819-skill corpus) — refining a mechanism that already
exists, not bolting on a new one.

## 5. Summary / what to actually do next

- Fine-tuning a 7-8B cybersecurity model is realistic and cheap (QLoRA, ~6-8GB VRAM, free-tier
  GPU-feasible) — but not on this host, which has no GPU at all.
- Free managed platforms (Colab especially) have real, specific, named content restrictions
  that conflict with at least the credential-attack portion of this project's scope — don't
  use them for that specific training data without reading the exact current policy text
  yourself first.
- Raw GPU rental (RunPod/Vast.ai/Lambda, or AWS/Azure research credits) is the more permissive
  and still cheap option, and doesn't carry TRC's publish-your-research requirement that would
  conflict with this project's private, local-only posture.
- Before spending any money or GPU-hours on fine-tuning: this project's own RAG/skill-injection
  mechanism already follows the literature's recommended pattern — test whether upgrading that
  (real embeddings over the existing skill corpus) closes more of the gap than a new fine-tune
  would, since it requires no GPU, no training data sourcing, and no ToS navigation at all.
