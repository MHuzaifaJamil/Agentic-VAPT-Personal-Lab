# Directives: Testing New Candidate Models Without Touching Mugheeraat's Production Setup

**Purpose:** every research round so far (Jev-alternatives, abliteration, CIPHER/xOffense)
has ended with "candidate models worth testing" — this doc is the standing procedure for
actually testing them, on whichever machine is doing the testing, without risking the real
Mugheeraat installation. Follow this before running any candidate model for real, every time.

---

## 1. Physical isolation — a separate directory tree, always

- Test-lab work lives in its own directory **outside** the Mugheeraat repo (`implementation/`)
  entirely — e.g. a sibling directory such as `~/model-testlab/`, never nested inside
  Mugheeraat's own working tree. It must not be a subdirectory `git` there would ever pick up,
  and it must never share a Python venv, `pyproject.toml`, or dependency lock file with the
  real `vapt_agent` package.
- **Never use a tmpfs-backed scratch/temp directory for model weights or venvs.** Confirmed
  the hard way this session: a scratchpad on a 7.7GB tmpfs filled completely from a single
  model's unwanted CUDA dependency download and aborted mid-install. Model weights, venvs, and
  anything multi-hundred-MB+ belong on real, persistent disk.
- Each candidate model gets its own venv (or at minimum, conflicting dependency sets get
  separate venvs) — don't let one candidate's package resolution fight another's in a shared
  environment.

## 2. Never touch production config or the production model directory

- Mugheeraat's real models live under its configured `models_dir`
  (`config/defaults.yaml` → `models.models_dir`, currently
  `/home/mhj/.local/share/vapt_agent/models/`), with six explicit filenames under
  `models.<role>`. **Never download a test candidate into this directory, and never edit
  `defaults.yaml`'s `models:` block as part of testing** — a test is not a production change.
- A test-lab inference server must bind to a **different port** than the production
  `127.0.0.1:11434` endpoint (e.g. `11435`) and must still be **loopback-only** — test infra
  follows the same local-only discipline as everything else in this project
  (`05:SEC-DATA-03`), it isn't exempt just because it's experimental.
- The only way a tested model ever reaches production is: pass a real test-lab evaluation →
  get written up in `Research/` → get proposed as its own item in
  `STAGING-Pending-Discussions-and-Fixes.md` → explicit Human Operator approval → **only then**
  does `defaults.yaml` get edited, by a deliberate, separate change. Never shortcut this path
  because a candidate "looked good" in testing.

## 3. Never run a test-lab load concurrently with a live engagement

- Mugheeraat's architecture is **hard single-model-residency** (`FR-GATE-02`) and this host's
  own RAM budget is tight even for one resident model (observed repeatedly this session:
  often under 5GB genuinely free out of 15GB total). Loading a second model for testing while
  a real engagement has one resident **will** starve one or both, and can crash or stall a
  real, possibly multi-hour-invested engagement.
- Before loading any test candidate: check whether an engagement is actually running
  (`vaptctl status`, or equivalent — a live dashboard/console session, a `PAUSED`/
  `IN_PROGRESS` state) on whatever host you're testing against. If one is active, wait for it
  to reach a natural pause point, or test on a different, idle machine instead.

## 4. Dependency hygiene — lessons already paid for this session, don't re-learn them

- **Force CPU-only backends explicitly.** None of the model-serving projects encountered so
  far (jeff, Kev, SemIf) auto-detect "no GPU present" — every one of them defaulted to
  downloading multi-hundred-MB-to-multi-GB NVIDIA/CUDA wheels on this CPU-only host unless
  told not to. Use `UV_TORCH_BACKEND=cpu` (for `uv`-based projects) or the project's own
  `--backend cpu`/`--device cpu` equivalent, and verify afterward
  (`python3 -c "import torch; print(torch.cuda.is_available())"` should print `False` with a
  `+cpu` build, not just `False` with a full CUDA build silently installed anyway).
- **Serialize installs. Don't run multiple `uv`/`pip` installs at once.** Confirmed this
  session: concurrent `uv` processes contend for the same shared wheel-cache lock
  (`~/.cache/uv/...`) and will time out waiting on each other rather than actually working in
  parallel. One install at a time, start to finish, then the next.
- Prefer each project's own real serving code/client over reverse-engineering a bespoke
  loader — jeff's underlying `gliformer` library failed when loaded through the generic
  `gliner` package; the correct construction was only found by reading jeff's own test suite.
  If a project ships its own client/server, use it, even if it takes more setup than a bare
  `from_pretrained()` call would.

## 5. Test methodology — same discipline every time, not ad hoc

- Build a small ground-truth test set modeled on the **actual council role's real job**, not
  a generic benchmark — e.g. real sanitized tool-output shapes for a candidate-detection/
  Adjudicator test, real task-generation prompts for a Scripter test. `JevAI-Alternatives-
  Research.md`'s `test_cases.py` is the template to copy and adapt, not reinvent.
- Report results honestly, including inverted/confidently-wrong failures (the two Laya/jeff
  cases this session found are exactly the failure mode worth watching for — a model that's
  confidently wrong is more dangerous than one that's honestly uncertain).
- Clean up test-lab venvs/model weights once a comparison round concludes unless a candidate
  is being kept for further work — don't let disk usage grow unbounded across research
  rounds.

---

**This document is itself subject to the standing Research-folder convention** — see
`CLAUDE.md`'s note on where research output goes and how it's named. Update this file in
place if a future test round surfaces a new lesson; don't fork a near-duplicate directives
file.
