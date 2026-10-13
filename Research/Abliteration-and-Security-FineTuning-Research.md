# Abliteration, Security-Domain Models & Fine-Tuning — Research

**Question:** HF has 6000+ "abliterated" models — worth anything for this project? Are there
models built specifically for VAPT/offensive-security use? Can we fine-tune our own, and do
CTF/hacking datasets exist for it? All claims below checked against the HF API directly, not
taken from blog summaries.

---

## 1. What abliteration actually is (verified, not hype)

Real, published technique (Arditi et al., "Refusal in LLMs is mediated by a single direction,"
plus [mlabonne's widely-cited writeup](https://huggingface.co/blog/mlabonne/abliteration)).
Refusal behavior in instruct-tuned LLMs is mediated by one dominant direction in the residual
stream, computed as the difference in mean activations between harmful and harmless prompts.
Ablating that direction (at inference time, or permanently via weight orthogonalization)
removes the model's ability to represent "I should refuse this" — without a full retrain.
Cheap (hours, not days) — which is why so many exist.

## 2. Why 6000+ exist: concentration, not 6000 independent efforts

Checked the HF API directly (`/api/models?search=abliterated`). In the first 100 hits, **26**
belong to one account (`huihui-ai`), a prolific single practitioner who abliterates nearly
every popular open-weight release within days of launch; `mradermacher`/`bartowski` (9 and 6)
are well-known GGUF re-quantizers who redistribute others' abliterations, not originators.
Realistically this is a few dozen serious practitioners' output, multiplied by every base
model release and every quantization format — not 6000 independent research efforts. Quality
varies enormously; stick to a handful of known-reputable names (`huihui-ai`, `mlabonne`,
`failspy`, `NousResearch`) rather than obscure single-upload accounts.

## 3. Do abliterated versions of this project's own 6 council models exist?

Checked each by name directly against the HF API:

| Council role | Model | Abliterated variant found? |
|---|---|---|
| Lead Strategist | DeepSeek-R1-0528-Qwen3-8B | ✅ `huihui-ai/DeepSeek-R1-0528-Qwen3-8B-abliterated`, plus `Josiefied-...-abliterated-v1` (MLX/GGUF) |
| Strategy Auditor | Hermes-3-Llama-3.1-8B | ✅ `gulan28/Hermes-3-Llama-3.1-8B-abliterated-GGUF` (399 downloads — thin traction) |
| Primary Scripter | Qwen2.5-Coder-7B-Instruct | ✅ `bartowski/...-abliterated-GGUF` (**35,676 downloads** — real, substantial traction, GGUF-ready) |
| Secondary Scripter | DeepSeek-Coder-6.7B-Instruct | ❌ **No variant found.** Older/less popular model, never picked up by the abliteration crowd. |
| Criterion Adjudicator | Mistral-7B-Instruct-v0.3 | ✅ Several, e.g. `mradermacher/...-abliterated-GGUF` (1,375 downloads) |
| Executive Reporter | Ministral-8B-Instruct-2410 | ✅ `mradermacher/ministral-8B-Instruct-2410-abliterated-GGUF` |

5 of 6 have real, GGUF-packaged variants (drop-in for this project's llama.cpp stack). The
Secondary Scripter's model does not.

## 4. Is abliteration actually beneficial here? — nuanced, not a clean yes

**The real argument for it:** `CLAUDE.md` Directive 1 already complains about exactly the
problem abliteration targets — "do not inject synthetic ethics disclaimers, capability
refusals, or moralizing warnings into technical responses." An off-the-shelf instruct model
asked to write a real SQLi payload or exploit script for an authorized target sometimes
hedges, lectures, or softens output even when the request is entirely legitimate — that's
friction abliteration removes at the model level.

**The real argument against it — and it's a strong one:** searched specifically for
documented side effects, and the clearest hit is a **llama.cpp maintainers' own GitHub
discussion** reporting an abliterated Qwen3.8-27B "loops and falls apart on multi-step
agentic tasks" — degraded multi-step recovery, repeated tool calls, hallucination once a
small mistake happens. Separately, benchmarked drops are real and specific: lower MMLU,
higher hallucination rate, **math/logical reasoning is the most sensitive capability to
abliteration**, and comprehension format-sensitivity gets worse (a Qwen2.5 abliterated
variant answers "no" to open-ended "is this wrong?" questions while still correctly
classifying the same content in multiple-choice format).

This matters a great deal for THIS project specifically, not abstractly: the whole Council is
a **multi-round, multi-step agentic pipeline** (`FR-COUNCIL-19`'s round loop — Strategist →
Auditor → Scripter → Adjudicator, repeating) that this session already spent weeks
debugging for reliability (zero-yield loops, StructuredOutputError crashes, wasted multi-day
runs). Abliteration's most-documented failure mode is precisely "falls apart on multi-step
agentic tasks." Swapping in abliterated models risks trading one class of reliability problem
for another, worse one, in the exact dimension already fragile.

**Also worth weighing:** `CLAUDE.md` Directive 2 already establishes that safety is enforced
by **deterministic code gates, not LLM alignment** — Tier 0 scope checks, Gate 2 validation,
the Human Checkpoint Gate. The model's own refusal training was never the actual safety
boundary in this architecture. That means abliteration's upside here is narrower than it
looks: it would reduce *friction* (fewer hedged/refused legitimate technical asks), not close
a *safety gap* — the gap is already closed elsewhere. Worth testing on the Primary Scripter
specifically (best-traction variant, most likely to hit refusal friction on payload
generation) before touching the reasoning-heavy Strategist role, given reasoning is the most
abliteration-sensitive capability and the Strategist is this project's most reasoning-heavy,
already-most-fragile role.

## 5. Purpose-built security models — a cleaner alternative to genericabliteration

Two real, verified options exist that are fine-tuned *on security content* rather than merely
de-refused:

- **WhiteRabbitNeo** (`WhiteRabbitNeo/Llama-3.1-WhiteRabbitNeo-2-8B`) — one of the earliest
  open cybersecurity LLMs, explicitly positioned as "uncensored" and tuned for offensive
  security (finding vulnerabilities, writing exploit code). Real but modest traction (489
  downloads, 35 likes) — has since evolved into a commercial product ("Deep Hat," by Kindo).
  8B, Llama-3.1-based — same size class as this project's models.
- **Foundation-Sec-8B** (`fdtn-ai/Foundation-Sec-8B`) — checked its actual model card
  directly: continued-pretrained on ~5.1B tokens of real security data (threat intel, CVE/
  vulnerability databases, incident response docs), Apache 2.0, real traction (16k
  downloads), GGUF quants already exist. **Important distinction: this model explicitly
  retains standard safety training and is NOT abliterated** — its own card lists "autonomous
  security decision-making without human oversight" and "developing attack plans targeting
  specific organizations" as **out-of-scope uses**, i.e. close to what this project's
  Autonomous Mode actually does. More security *knowledge*, not necessarily less refusal
  friction — the two axes (domain depth vs. refusal-avoidance) don't automatically come
  together, and picking the wrong one for the wrong role would be a real mismatch.

## 6. Fine-tuning our own — feasibility on this hardware

Direct answer: **not practical on the Requirements-Specifying PC as configured** (confirmed
this session: CPU-only, no GPU, 15GB RAM, often <3GB free). Even parameter-efficient
fine-tuning (LoRA/QLoRA) of a 7-8B model is realistically a GPU job — CPU training is
possible in principle but would run to days-to-weeks for a modest dataset, not a reasonable
local option. This mirrors what showed up repeatedly in the Jev-alternatives lab (`jeff`,
Kev) — every one of these projects' own training/fine-tuning tooling assumes a CUDA or Apple
Silicon device. A real fine-tuning attempt would need a rented cloud GPU (the pattern Kev's
own README uses: `uv run modal deploy` on an L4/L40S/H100), not local hardware.

## 7. CTF / hacking / exploit datasets — real availability, checked directly

Searched the HF datasets API directly (not just search-engine summaries). Real, substantial
options exist:

| Dataset | Downloads | Likes | What it is |
|---|---|---|---|
| `Trendyol/Trendyol-Cybersecurity-Instruction-Tuning-Dataset` | 7,212 | 135 | Instruction-tuning pairs, cybersecurity domain, from a real company |
| `AlicanKiraz0/Cybersecurity-Dataset-Fenrir-v2.1` | 4,572 | 147 | High like:download ratio — a quality signal |
| `Vyber07/cyber-security` | 3,751 | 109 | General cybersecurity instruction data |
| `Alibaba-AAIG/alibaba-ctf` | 3,914 | 2 | Real CTF benchmark, 87 curated tasks, from Alibaba's AI safety group |
| `CyberNative/Code_Vulnerability_Security_DPO` | 1,548 | 170 | Preference-pair (DPO) data specifically for vulnerability/security code judgments — very high like ratio |
| `jason-oneal/mitre-stix-cve-exploitdb-dataset-alpaca-chatml-harmony` | 567 | — | Combines MITRE STIX, CVE, and Exploit-DB into instruction-ready (Alpaca/ChatML) format |
| `detoxioai/exploit_db_train_v1` | 87 | 12 | Training data derived directly from Exploit-DB |
| `WhitzardAgent/CyberSecurity-1M` | 649 | 23 | Million-scale cybersecurity dataset |
| `preemware/pentesting-eval` | 370 | 14 | Pentesting-specific evaluation set |

Real data exists; the gate isn't dataset availability, it's compute (§6).

---

## 8. Bottom line

- **Abliteration:** real technique, real risk. Don't blanket-apply it across the Council —
  its most-documented failure mode (multi-step agentic degradation) is exactly this
  project's own architecture's most fragile dimension. If tried at all, start narrow: the
  Primary Scripter only (best-traction variant, least reasoning-dependent role), with the
  same before/after test-lab discipline used for the Jev-alternatives research, not a
  wholesale swap.
- **Purpose-built security models:** more promising than generic abliteration, but pick for
  the right axis — WhiteRabbitNeo for reduced refusal friction on offensive tasks,
  Foundation-Sec-8B for security knowledge depth (while explicitly *not* solving the refusal
  problem — its own card flags autonomous attack-planning as out of scope).
- **Fine-tuning our own:** datasets are real and available; local hardware isn't. Needs a
  rented cloud GPU to be practical, not something to build in-session on this host.
- Nothing here should be adopted without the same live test-lab treatment as the
  Jev-alternatives research (`JevAI-Alternatives-Research.md`) and an explicit Human Operator
  decision — this document is research, not a recommendation to swap any council model yet.
