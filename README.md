# MLM26: Local Coding Agent Challenge

Build the best local coding agent — measured on Terminal-Bench 2.0. Hosted by [ML+X](https://mlx.wisc.edu/) at UW–Madison, September–December 2026. Open to everyone.

---

## Overview

The last two years have transformed how software gets built. Frontier coding assistants — Claude Code, Cursor, Codex, Devin — can now read a codebase, plan changes across many files, run tests, and recover from errors well enough to feel like real collaborators. They are remarkable, but they are also closed, expensive, and untrusting. Every keystroke flows to a third party, costs accumulate per task, and anyone working with sensitive has to take extreme caution to ensure nothing gets leaked.

Open-weight models have closed enough of the raw-quality gap that a credible coding assistant can now plausibly run locally. *Plausibly*, but not yet *well*. The challenge is intended as a collaborative effort to close the remaining gap. You will build an autonomous coding agent on top of an open-weight model of your choice and measure it on [Terminal-Bench 2.0](https://tbench.ai), an industry-standard 89-task benchmark used to evaluate Claude Code, Cursor, and friends. The challenge evaluation rewards both raw performance and efficiency, so a 14B model wrapped in a thoughtful agent loop can credibly beat a 480B with a naive one. The goal is not to build the largest agent, but the most *useful* one under realistic constraints.

This is a collaborative challenge, not a prize competition. There are no cash prizes and no reason to hoard ideas — share repos early, post findings to the Discussion tab, fork and build on each other's approaches. Credit what you borrowed in your writeup; explain what you added. The best outcomes happen when everyone's baseline keeps rising. UW–Madison participants get weekly sprints, office hours, and shared GPU access through ML+X; everyone else is welcome to participate remotely with the same starter code, benchmark, and submission pipeline.

---

## Description

### Background

A raw language model can read a task description and emit a reasonable command, but it cannot, on its own, solve a multi-step coding problem that spans dozens of shell invocations and recovers from a chain of errors. It loses track of context, repeats failed commands, hallucinates files that do not exist, and does not know when to stop. The distance between "can think about code" and "can autonomously navigate a real engineering problem" is enormous — and bridging it is the central craft of building a coding agent.

The **orchestration layer** is where that work happens. It's the harness around the model that keeps track of context, recovers from failed commands, decides when the task is actually done, and chains reasoning, action, and verification into something that works reliably across a hundred turns. It's what separates an LLM and a shell from an agent. There is no consensus yet on what the best architecture looks like. Prompting strategies, tool design, planning logic, retrieval, multi-stage pipelines, self-critique, fine-tuning — the design space is wide open. The bet of this challenge is that *how* you build the agent matters as much as which model you pick, and that careful engineering on a small model can beat thoughtless deployment of a large one.

### Goal

Build an autonomous coding agent, running entirely on open-weight models, that:

- **Solves real software engineering tasks end-to-end** without human intervention — reading the problem, exploring the codebase, planning, executing, and verifying the result.
- **Generalizes** across Terminal-Bench's diverse task categories rather than memorizing solutions to individual tasks.
- **Runs efficiently** — modest memory footprint, lean token consumption — without sacrificing capability.
- **Beats the leaderboard**, which rewards a single weighted score combining Terminal-Bench accuracy, model footprint, and tokens per task.

Architecture, prompting strategy, retrieval, tool design, and planning logic are all up to you. The starter code is a deliberately minimal ReAct loop — a launchpad, not a solution.

### What we provide

- **A starter agent** in [`starter/`](starter/) — a minimal ReAct-style baseline (~200 lines) you can fork and rebuild from. It is intentionally simple; improving it is the whole point.
- **Setup documentation** in [`starter/docs/`](starter/docs/) — Docker installation, model endpoint configuration, a full end-to-end walkthrough, troubleshooting, and safety guidance.
- **A curated model catalog** in [`MODELS.md`](MODELS.md) — the eligible open-weight models for the leaderboard, each with a reported VRAM number used by the scoring formula. Roughly 50 entries spanning ~7 GB to ~500 GB; new models can be requested via the Kaggle Discussion tab.
- **Compute pointers** in the [Resources](#resources) section — free GPU notebooks, hosted endpoints, and (for UW participants) shared GPU access through ML+X, NRP, and CHTC.

### Terminal-Bench

[Terminal-Bench 2.0](https://tbench.ai) is the benchmark we score against — an open, industry-standard collection of 89 tasks spanning software engineering, security, data processing, system administration, and scientific computing. Each task ships as a Docker image with a starting environment, a natural-language instruction, and a hidden test suite that grades the container's final state. All 89 tasks are public and can be browsed at [tbench.ai](https://www.tbench.ai/).

Your agent receives the instruction and is given shell access to the running container. It inspects the codebase the way a developer would — `ls`, `cat`, `grep`, `find`, `git log`, `pytest`, anything it wants to run — edits files by writing to disk, executes builds and tests, observes the output, and decides what to do next. There is no special tooling; the agent succeeds by knowing what commands to issue and how to interpret what comes back.

**Where the agent code lives.** The decision logic — what to prompt the model with, how to parse its response into a shell command, when to stop — is your code, not the benchmark's. You write a Python class implementing the `BaseAgent` interface from [Harbor](https://www.harborframework.com/), the open-source harness for Terminal-Bench 2.0. Harbor invokes your class's `run(instruction, environment)` method when a task starts; your code prompts the model with the instruction (plus a system prompt and the running conversation), parses the response into a bash command, runs it via `environment.exec()`, observes the output, decides the next step, and returns when the task is done. The baseline in [`starter/agent/agent.py`](starter/agent/agent.py) is a ~60-line ReAct loop you can fork. Pointing Harbor at your agent is a single CLI flag — `--agent-import-path agent.agent:YourAgentClass` — and the same string is what your submission card declares. Full integration details are in [`starter/docs/harbor.md`](starter/docs/harbor.md) and Harbor's upstream [Running Terminal-Bench tutorial](https://www.harborframework.com/docs/tutorials/running-terminal-bench).

### Example tasks

Three representative tasks from Terminal-Bench, one from each end of the difficulty spectrum and one in between:

- **fix-git** (easy, software-engineering) — The container holds a small git repo in which a recent `git reset --hard` orphaned several commits of feature work. The branch *looks* clean, but the work is gone from `main`. The agent has to recognize that something was lost, use `git reflog` to locate the orphaned commits, recover them, merge them back into `main` cleanly, and resolve any conflicts that appear. Tests whether the agent can read git's terminal output, recognize a non-obvious failure state, and recall less-common git subcommands.

- **build-cython-ext** (medium, debugging) — A Cython extension that no longer compiles because the project's NumPy version moved forward and the underlying C API changed. The agent has to read the compiler error, trace it to the deprecated NumPy symbols in the `.pyx` source, patch either the source or the build configuration, and produce a working compiled extension that the test suite can import. Tests cross-language debugging, build-toolchain reasoning, and the discipline to re-run after each fix instead of guessing twice.

- **configure-webserver** (hard, system-administration) — A bare Linux container that needs to be turned into a self-deploying web server: when commits land in a designated local git repo, the served site should update automatically. The agent has to choose a server (nginx, lighttpd, caddy — its call), wire up a `post-receive` hook or equivalent, ensure the service starts on boot, and prove the end-to-end loop with a test commit. Tests multi-component system design and the kind of "no single right answer" judgment that fewer benchmarks capture.

Browse all 89 tasks with filters at [tbench.ai](https://www.tbench.ai/).

### Considerations

**Models (binding).** Pick a model from [`MODELS.md`](MODELS.md). That table maps each `(model, quantization)` to a canonical *reported VRAM* used by the leaderboard formula — you don't measure VRAM yourself, you pick a row. The table spans from ~7 GB (Qwen-Coder-7B AWQ) to ~500 GB (Kimi-K2.7-Code), so no hardware floor or ceiling is implied. **Suggested anchor: `Qwen/Qwen2.5-Coder-32B-Instruct-AWQ` (28 GB).** Want to use a model that isn't listed? Post in the Kaggle Discussion tab — organizers add rows on request, usually within a day or two.

**What's not eligible:**
- **Closed-weight models** (GPT, Claude, Gemini) anywhere in your system, including "just the planner."
- **Opaque hosted providers** (Bedrock Custom Model Import, generic chat APIs that don't disclose `(model, quantization)`) where you can't pin the exact row in `MODELS.md`. Fine for development; can't be your submission's model. (Bedrock's *fully-managed* Qwen3-Coder lineup is eligible via the approximate-VRAM mapping in `MODELS.md`.)

**Multi-GPU serving is fine.** How you actually run the model — single GPU, tensor-parallel across many, sharded MoE deployment, multi-node cluster — does not affect your score. The scored footprint is always the table value for your `(model, quantization)` row.

**Per-task budget:**
- **No human-in-the-loop at evaluation time.** Terminal-Bench scoring is fully deterministic — pytest passes or fails, no LLM judges, no subjective grading.
- **No hard turn cap.** Set whatever per-task turn / wall-clock limit suits your dev loop; the leaderboard formula already penalizes verbose agents through the `total_tokens` term, so you don't have to be told to stop. A finale-time wall-clock cap may apply to keep the reproducibility queue moving — number TBD.

**Generalizability.** One system prompt, one agent loop, no per-task `if task == "fix-git"` branching. Detecting task *categories* (e.g., "this looks like a debugging task") and adjusting strategy is fine — that's good engineering. Hardcoding solutions or prompts for individual tasks is not. At the finale, organizers re-run top submissions on a held-out task subset; a big gap between your public-set score and your private-set score gets investigated.

### Contact

Chris Endemann (endemann@wisc.edu) — ML+X, UW–Madison.

Hosted by [ML+X](https://mlx.wisc.edu/) at the University of Wisconsin–Madison. Sponsor info: https://hub.datascience.wisc.edu/communities/mlx/sponsorship/

---

## Agent safety

**Terminal-Bench's sandbox does the heavy lifting.** Every task runs in a fresh Docker container with no host access, destroyed afterward. Inside `harbor run`, your agent can't hurt you. Don't undo that:

- Don't mount your home directory, SSH keys, or `~/.gitconfig` into containers.
- Don't bake real credentials into images or `.env` files you commit. Use throwaway keys.
- `.env` is gitignored in the starter — keep it that way.

**The danger zone is your own dev loop.** When you test agent code *outside* Harbor (e.g., pointing your loop at a local shell "just to see"), it has whatever access you have:

- Develop in a scratch directory, never your home directory or a repo you care about.
- Never give a dev agent access to directories containing `.git` remotes, credentials, or anything you can't lose.
- Remember the classics: `git clean -fdx`, `docker system prune`, `find ... -exec rm`, `>` truncation. An agent will eventually try one.

**If your agent does something unexpected and concerning, tell us.** Novel failure modes are findings, not embarrassments — they're also great writeup material.

---

## Evaluation

### Scoring

Submissions are ranked on a single weighted score:

```
leaderboard_score = TB_score / log10(reported_VRAM_GB × total_tokens)^2
```

Where:
- **`TB_score`** is your mean Terminal-Bench reward across all 89 tasks (single attempt per task, `--n-attempts 1`).
- **`reported_VRAM_GB`** is the canonical number for your `(model, quantization)` row in [`MODELS.md`](MODELS.md). You don't measure it; you pick a row.
- **`total_tokens`** is the sum of `n_input_tokens + n_output_tokens` across all 89 tasks, taken straight from Harbor's per-task `result.json`.

Worked example: a `Qwen2.5-Coder-32B-AWQ` submission (28 GB) that scores 0.42 on Terminal-Bench with 1,263,800 total tokens across the 89 tasks lands at `0.42 / log10(28 × 1,263,800)^2` = `0.42 / 7.55^2` = `0.42 / 57.0` = **0.00737**.

The squared log denominator makes efficiency a real design pressure: a leaner agent can credibly outrank a more capable but more expensive one. Raw performance still matters — a sufficiently strong TB score wins regardless — but it has to genuinely outpace the footprint penalty, not just edge ahead by a sliver.

### Head-to-head comparisons

Each row shows two hypothetical submissions and which one wins under the formula. These are illustrative; real submissions will land all over the place.

| Submission A | Submission B | Winner | Why |
|---|---|---|---|
| Qwen2.5-Coder-32B-AWQ (28 GB), TB 0.42, 1.26M tokens → **0.00737** | Qwen2.5-Coder-7B-AWQ (7 GB), TB 0.30, 500k tokens → **0.00700** | **A** | Raw capability gap (0.42 vs 0.30) wins. The 7B is leaner but not lean enough to close 12 points of TB score. |
| Qwen2.5-Coder-32B-AWQ (28 GB), TB 0.42, 1.26M tokens → **0.00737** | Qwen2.5-Coder-14B-AWQ (12 GB), TB 0.38, 800k tokens → **0.00780** | **B** | A clever 14B agent at 4 points lower raw score wins by being meaningfully leaner. |
| Qwen2.5-Coder-32B-AWQ (28 GB), TB 0.42, 1.26M tokens → **0.00737** | Same Qwen-32B, TB 0.42, **2.5M** tokens → **0.00682** | **A** | Same model, same TB score — the leaner agent loop wins. A verbose loop costs you real ranking. |
| Kimi-K2.7-Code (510 GB), TB 0.65, 1M tokens → **0.00857** | Qwen2.5-Coder-32B-AWQ (28 GB), TB 0.42, 1.26M tokens → **0.00737** | **A** | Even with an 18× footprint penalty, Kimi's 23-point raw advantage carries the day. Raw capability still dominates when the gap is large. |
| Kimi-K2.7-Code (510 GB), TB 0.65, 1M tokens → **0.00857** | Qwen3-Coder-30B-A3B via Bedrock (35 GB), TB 0.50, 1M tokens → **0.00878** | **B** | A 15-point raw gap is no longer enough — the smaller MoE wins on efficiency. Footprint matters when the raw scores are within ~30%. |

### Computing your submission numbers

After running `harbor run -d terminal-bench@2.0 --agent-import-path agent.agent:BaselineAgent`, Harbor writes one `result.json` per task under `jobs/<job-id>/terminal-bench__<task>/0/result.json`. Extract the three numbers you need with:

```bash
JOB=jobs/<your-job-id>

# Terminal-Bench score (mean reward)
find "$JOB" -name 'result.json' -path '*/0/result.json' | xargs jq -s '
  [.[] | .reward] | add / length
'

# Total tokens (input + output, summed across all 89 tasks)
find "$JOB" -name 'result.json' -path '*/0/result.json' | xargs jq -s '
  [.[] | (.n_input_tokens + .n_output_tokens)] | add
'

# Tasks evaluated (sanity check: should be 89)
find "$JOB" -name 'result.json' -path '*/0/result.json' | wc -l
```

These three numbers, plus your model row from [`MODELS.md`](MODELS.md), are what go on the submission card. The leaderboard recomputes `leaderboard_score` from them — you don't need to compute it yourself, but the worked example above is the formula you'd use to sanity-check.

### Reproducibility check (finale)

There is no rubric, no human-scored writeup component, no engineering-depth panel. Ranking is the formula above. At the finale, organizers re-run the top ~10 submissions to confirm the result:

1. **Score reproduction** — clone at the tagged commit, run `harbor run` against all 89 tasks, confirm the reported `TB_score` reproduces within run-to-run noise.
2. **Held-out subset** — run the same agent against a private subset of ~20 fresh Terminal-Bench tasks not in the public set during the semester. Significantly lower private-set scores get investigated for task-specific hardcoding.
3. **Token + model verification** — confirm `total_tokens` matches the submission card and that the running agent is talking to the same model row claimed in the card.

Honest run-to-run variance is fine. Significant discrepancies, hardcoding, or model/quantization mismatches disqualify.

### Required elements (pass/fail)

| Requirement | Pass/Fail |
|---|---|
| Submission card fully filled out | Yes/No |
| Model + quantization listed in [`MODELS.md`](MODELS.md) | Yes/No |
| Agent runs via `harbor run --agent-import-path` without modification | Yes/No |
| Open weights only (no closed-weight or opaque-provider API calls) | Yes/No |
| All 89 Terminal-Bench tasks evaluated | Yes/No |
| Public GitHub repo with tagged commit | Yes/No |

---

## Submitting your solution

**One submission per team, at the end of the semester.** There is no live leaderboard and no mid-semester submissions — focus on building and understanding, not chasing a number.

During the semester, share early and often via the Kaggle Discussion tab: post draft writeups, share your repo, describe what's working and what isn't. Think of Discussion as an open lab notebook for the cohort.

### Part 1: Submission card

Structured metadata used for automated ranking:

| Field | Example |
|---|---|
| Team name | Terminal Velocity |
| GitHub repo URL | github.com/team/agent |
| Commit tag | `v1.0-submission` |
| Model (from `MODELS.md`) | `Qwen/Qwen2.5-Coder-32B-Instruct-AWQ` |
| Quantization (from `MODELS.md`) | AWQ 4-bit |
| Reported VRAM (from `MODELS.md`) | 28 GB |
| Terminal-Bench score | 0.42 (37/89 tasks passed) |
| Total tokens (across 89 tasks) | 1,263,800 |
| Tasks evaluated | All 89 |
| **Leaderboard score** (auto) | **0.00737** = 0.42 / log10(28 × 1,263,800)² |
| GPU used (informational) | RTX A6000 48 GB |
| Mean wall-clock per task (informational) | 3m 12s |

### Part 2: Full submission (attached to your Kaggle Writeup)

1. **Writeup** (≤5,000 words). Problem framing, approach, what worked, what didn't, Terminal-Bench scores, failure analysis, limitations, what you'd do with another month. Quality > length.
2. **Public notebook.** Your agent code as a public notebook. Should be runnable or clearly documented.
3. **Public GitHub repo.** Complete agent code, README with reproduction instructions, tagged release or commit hash matching your reported scores (e.g., `git tag v1.0-submission`), Terminal-Bench-compatible agent (runnable via `harbor run --agent-import-path`). License: MIT or Apache 2.0.

---

## Awards

Top of the leaderboard wins. **UW–Madison local awards** — UW participants are eligible for additional recognition based on in-person engagement. Details at kickoff.

---

## Getting started

The fastest path from "I registered" to "my agent has a Terminal-Bench score" lives in [`starter/`](starter/). Roughly:

1. **Install** Docker, [uv](https://docs.astral.sh/uv/), Python 3.12.
2. **Clone** this repo, create a venv, `uv pip install -e starter/`.
3. **Verify Harbor** with the oracle agent (no model required):
   ```bash
   harbor run -d terminal-bench-sample@2.0 -a oracle
   ```
4. **Set up a model endpoint** — Ollama is easiest. The suggested anchor is `Qwen/Qwen2.5-Coder-32B-Instruct-AWQ` under vLLM; for first-week dev `ollama pull qwen2.5-coder:14b` works on smaller GPUs.
5. **Run the baseline** on a single task to confirm everything is wired up.

Full instructions:

| Doc | What's in it |
|---|---|
| [`starter/README.md`](starter/README.md) | Setup in ~15 minutes, the weekly loop, where to dig in |
| [`starter/docs/walkthrough.md`](starter/docs/walkthrough.md) | End-to-end: Docker → uv → Harbor → first model → first score |
| [`starter/docs/docker_setup.md`](starter/docs/docker_setup.md) | Per-OS Docker install + common failures |
| [`starter/docs/byo_model.md`](starter/docs/byo_model.md) | Ollama, vLLM, hosted endpoints, `.env` config |
| [`starter/docs/harbor.md`](starter/docs/harbor.md) | Harbor mental model, custom agents, leaderboard submission |
| [`starter/docs/safety.md`](starter/docs/safety.md) | Sandbox guidance, what to keep away from your dev loop |
| [`starter/docs/troubleshooting.md`](starter/docs/troubleshooting.md) | First-week issues, in order of likelihood |

---

## Resources

You need somewhere to run your agent. Options, roughly easiest → most powerful:

### Hosted endpoints (no GPU required)

- **NVIDIA API catalog** ([build.nvidia.com](https://build.nvidia.com/)) — Free hosted, OpenAI-compatible endpoints for 100+ open-weight models including Qwen2.5-Coder-32B. Free tier: 1,000 inference credits on signup (up to 5,000 on request), shared ~40 RPM rate limit across all calls. Good for prompt iteration and limited eval runs; rate cap makes a full 89-task sweep slow but doable.
- **Amazon Bedrock** — Pay-per-token, fully-managed serverless access to the Qwen3 lineup: `qwen3-coder-30b-a3b`, `qwen3-coder-480b-a35b`, `qwen3-coder-next`, `qwen3-235b-a22b-instruct-2507`, and `qwen3-32b`. **Eligible with an approximate VRAM mapping**: AWS doesn't formally publish the serving quantization, but the practical assumption is FP8 (the smallest precision Qwen publishes a checkpoint for, consistent with Bedrock's pricing). See [`MODELS.md`](MODELS.md) "Bedrock fully-managed (approximate)" for the assumed numbers. Bedrock **Custom Model Import** is Provisioned-Throughput-only at $21–50/hr with a 1- or 6-month commit — not viable for hackathon teams. If you want AWS for self-hosting, rent an EC2 or SageMaker GPU instance and run vLLM yourself. [aws.amazon.com/bedrock](https://aws.amazon.com/bedrock/)

### Free GPU notebooks (dev / iteration)

- **Kaggle Notebooks** ([kaggle.com/docs/notebooks](https://www.kaggle.com/docs/notebooks)) — Available to Community Hackathon participants. Free tier: T4 ×2 (32 GB total VRAM), P100 16 GB, or TPU v3-8; 30 hr/week GPU quota; 12 hr session cap; ~29 GB host RAM; 20-min idle timeout. The 32 GB dual-T4 setup can host Qwen2.5-Coder-32B-AWQ via vLLM `--tensor-parallel-size 2` — workable but PCIe-only comms make inference materially slower than a single 48 GB card.
- **Google Colab (free tier)** ([colab.research.google.com](https://colab.research.google.com/)) — Single T4 16 GB, ~13 GB host RAM, ~12 hr sessions with 90-min idle disconnect, ~15-30 GPU-hr/week dynamic quota. A 32B model does not fit on a single T4; use this for prompt engineering with smaller models (≤14B AWQ) only. Colab Pro+ has A100 access for paid users.

### Local hardware

Any GPU large enough to fit the reported VRAM of your chosen `MODELS.md` row. The suggested anchor (`Qwen2.5-Coder-32B-Instruct-AWQ`, 28 GB) runs comfortably on an RTX A6000 48 GB, L40S 48 GB, RTX Pro 6000 96 GB (or half-slice thereof), or any 32 GB+ card with reduced context. See [`starter/docs/byo_model.md`](starter/docs/byo_model.md) for Ollama / vLLM setup.

### UW–Madison participants (additional)

- **NRP / Nautilus managed-LLM endpoint** ([nrp.ai/llms](https://nrp.ai/llms/)) — UW researchers authenticate via CILogon SSO and hit an OpenAI-compatible endpoint at `https://ellm.nrp-nautilus.io/v1` hosting Qwen3 (397B), GLM-5 (744B), Kimi-K2.7-Code (1T), Gemma-4 (12B/31B), MiniMax-M2 (230B), GPT-OSS-120B, and more. All are already listed in [`MODELS.md`](MODELS.md); anything missing can be requested in the Kaggle Discussion tab. NRP also lets you spin up your own GPU pod with vLLM (A100, L40S, A40, RTX 4090, etc.) — request access at [nrp.ai/get-access](https://nrp.ai/get-access/).
- **UW-hosted Qwen-Coder endpoint** — A shared Qwen-Coder deployment for MLM26 participants is available through ML+X. Request access via the kickoff form.
- **CHTC (Center for High Throughput Computing)** ([chtc.cs.wisc.edu](https://chtc.cs.wisc.edu/)) — Free shared campus GPU pool, good for batch sweeps and long-running fine-tunes.

---

## Communication

- **Kaggle Discussion tab** — async questions, public discussion
- **Discord** — informal, real-time, drop-in office hours (link TBD)
- **Weekly Wednesday sprints** — hybrid, recorded
- **Office hours** — TBD, posted in Discord
- **Terminal-Bench Discord** — separate, upstream community. Worth joining.

Be kind, be specific, search before you ask.

---

## FAQ

**Can I use a closed-weight model just for planning, with a local model for execution?**
No. If part of your system calls GPT, Claude, or Gemini, it's out of scope.

**Can I use Amazon Bedrock?**
Yes, with caveats. The **fully-managed pay-per-token Qwen3-Coder lineup** (`30B-A3B`, `480B-A35B`, `Coder-Next`, `Qwen3-32B`) is eligible — see [`MODELS.md`](MODELS.md) "Bedrock fully-managed (approximate)" for the assumed FP8 VRAM numbers. AWS doesn't officially state the serving precision, so our mapping is a best-effort approximation that we'll correct if AWS confirms otherwise. **Bedrock Custom Model Import** is not viable (Provisioned-Throughput-only at $21–50/hr with a 1- or 6-month commit). If you want AWS for self-hosting, rent an EC2 or SageMaker GPU instance and self-host with vLLM — that's just cloud compute, fine like any other rented GPU.

**My model isn't in `MODELS.md`. What do I do?**
Post in the Kaggle Discussion tab with the HuggingFace link, the quantization you want listed, and (if you have it) a quick VRAM estimate. Organizers add the row, usually within a day or two.

**Can I fine-tune a model for this?**
Yes. Document it in the writeup. Fine-tuned weights must be either public or reproducible from the public base model + your published LoRA / adapter, and you'll likely need to request your fine-tuned checkpoint be added to `MODELS.md` (via the Kaggle Discussion tab) so the leaderboard can score it.

**Can I use multiple models (e.g., a small planner + a larger coder)?**
Yes, but the submission card carries a single model row. If you use two models, your scored VRAM and token count must reflect the larger / costlier one (or sum), and you should be ready to defend that on the reproducibility check.

**Can I submit my agent to the public Terminal-Bench leaderboard?**
Yes, please. Independent of MLM. It's a real leaderboard and a real artifact.

**Do I need to use the entire Terminal-Bench task set during the semester?**
No — work with whatever subset is useful for debugging. For the leaderboard, your submission must report results on all 89 tasks; at the finale, organizers also run the top ~10 on a held-out subset to catch task-specific hardcoding.

**My team is just me. / My team is four people.**
Both fine. Teams of 1–4. Reflect honestly on contributions in the writeup.

**I don't have a GPU.**
See [Resources](#resources). For dev, NVIDIA's API catalog and Kaggle Notebooks both work without local hardware. UW participants can hit the NRP managed-LLM endpoint or request RunAI/UW endpoints. Whatever model you finally submit must be a row in `MODELS.md`.

**I'm not at UW.**
Welcome. The challenge is fully open. You won't have access to weekly sprints, office hours, NRP, or RunAI endpoints, but the leaderboard is the leaderboard — you compete on equal footing.

**Will there be a live leaderboard during the semester?**
No live leaderboard. Run Terminal-Bench locally, track your own progress, share findings via the Discussion tab. At the deadline, everyone submits a structured submission card — that's the ranking. Organizers spot-check the top ~10 for reproducibility and generalization. You can also submit independently to the [public Terminal-Bench leaderboard](https://tbench.ai/leaderboard).

**What's the relationship to the upstream Terminal-Bench project?**
We're users and fans — but MLM26 is a separate event. We don't speak for the Terminal-Bench maintainers.

---

## Citation

```
Chris Endemann et al. MLM26: Local Coding Agent Challenge.
https://kaggle.com/competitions/MLM26-EfficientCoder, 2026. Kaggle.
```

---

## Organizer notes (delete before publishing)

- [ ] Ask NRP staff (via the Nautilus AI/ML Matrix channel at `matrix.nrp-nautilus.io`) whether they would deploy a shared Qwen2.5-Coder-32B-AWQ endpoint for MLM26 participants, in addition to the existing managed-LLM catalog. If yes, every team — UW or not — gets a frictionless path to the suggested anchor model. Worth asking about Qwen3-Coder-30B-A3B and Qwen3-Coder-480B-A35B too.
- [ ] Stand up the leaderboard-score auto-calculator (takes submission card → returns `TB_score / log10(VRAM × total_tokens)^2`).
- [ ] Curate the held-out task subset for the finale reproducibility check (~20 tasks, not in the public 89).
- [ ] Confirm finale reference hardware spec (one or two GPU sizes for the spot-check pool).
- [ ] Reach out to Terminal-Bench / Laude Institute about possible coordination (judge from their side?)
- [ ] Cold-start test the quickstart on a machine that didn't write it
- [ ] Recruit judges (Terminal-Bench contributors, agent researchers)
- [ ] Set up Discord
- [ ] Coordinate with Kaggle on Community Hackathon setup
- [ ] Final pass on safety doc with UW research-IT
- [ ] Create Google Form for final submissions
- [ ] PR review SLA for `MODELS.md` additions during the semester (target: same-day)
