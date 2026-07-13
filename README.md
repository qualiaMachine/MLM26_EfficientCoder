# MLM26: Local Coding Agent Challenge

Build the best local coding agent — measured on Terminal-Bench 2.0. Hosted by [ML+X](https://mlx.wisc.edu/) at UW–Madison, September–December 2026. Open to everyone.

---

## Overview

The last two years have transformed how software gets built. Frontier coding agents — Claude Code, Cursor, Codex, Devin — can now read a codebase, plan changes across many files, run tests, and recover from errors well enough to feel like real (if junior) collaborators. They are remarkable, but they are also closed and expensive: every keystroke flows to a third party, costs accumulate per task, and anyone working with sensitive data has to be careful nothing leaks.

Open-weight models have closed enough of the raw-quality gap that a credible coding agent can now plausibly run locally. *Plausibly*, but not yet *well*. The challenge is intended as a collaborative effort to close the remaining gap. You will build an autonomous coding agent on top of an open-weight model of your choice and measure it on [Terminal-Bench 2.0](https://tbench.ai), an industry-standard 89-task benchmark used to evaluate Claude Code, Cursor, and friends. Every submission must fit under a 48 GB VRAM limit, so the leverage is in the scaffold: a 14B model wrapped in a thoughtful agent loop can credibly beat a 32B with a naive one. The goal is not to build the largest agent, but the most *useful* one under realistic constraints.

This is an **educational, collaborative challenge**. There are no cash prizes, no rankings-based awards, and no reason to hoard ideas. Share repos early, post findings to the Discussion tab, fork and build on each other's approaches. Credit what you borrowed in your writeup and explain what you added. Every improvement one team publishes raises the floor for everyone else — and every step forward here pushes the open-source community closer to genuine independence from closed frontier tools when it comes to agentic coding.

---

## Description

### Background

A raw language model can read a task description and emit a reasonable command, but it cannot, on its own, solve a multi-step coding problem that spans dozens of shell invocations and recovers from a chain of errors. It loses track of context, repeats failed commands, hallucinates files that do not exist, and does not know when to stop. The distance between "can think about code" and "can autonomously navigate a real engineering problem" is enormous — and bridging it is the central craft of building a coding agent.

The **scaffold** (you'll also hear *agent harness*) is the code wrapped around the model that keeps track of context, recovers from failed commands, decides when the task is actually done, and chains reasoning, action, and verification into something that works reliably across a hundred turns. It's what separates an LLM and a shell from an agent. There is no consensus yet on what the best architecture looks like. Prompting strategies, tool design, planning logic, retrieval, multi-stage pipelines, self-critique, fine-tuning — the design space is wide open. *How* you build the agent matters as much as which model you pick — careful engineering on a small model can beat thoughtless deployment of a large one.

### Goal

Build an autonomous coding agent, running entirely on open-weight models, that:

- **Solves real software engineering tasks end-to-end** without human intervention — reading the problem, exploring the codebase, planning, executing, and verifying the result.
- **Generalizes** across Terminal-Bench's diverse task categories rather than memorizing solutions to individual tasks.
- **Runs efficiently** — modest memory footprint, lean token consumption — without sacrificing capability.
- **Beats the leaderboard** — ranked by Terminal-Bench score among models that fit under the 48 GB VRAM limit, with fewer total tokens breaking ties.

Architecture, prompting strategy, retrieval, tool design, and planning logic are all up to you. The starter code is a deliberately minimal [ReAct](https://arxiv.org/abs/2210.03629) loop — the model *reasons* about the next step, *acts* by emitting a shell command, observes the output, and repeats until it decides the task is done. It's a launchpad, not a solution.

### What we provide

- **A starter agent** in [`starter/`](starter/) — a minimal ReAct-style baseline (~200 lines) you can fork and rebuild from. It is intentionally simple; your job is to improve it.
- **Setup documentation** in [`starter/docs/`](starter/docs/) — Docker installation, model endpoint configuration, a full end-to-end walkthrough, troubleshooting, and safety guidance.
- **A curated model catalog** in [`MODELS.md`](MODELS.md) — the open-weight models eligible for the leaderboard, each with a canonical reported VRAM number checked against the 48 GB limit. Entries above the limit stay listed for prototyping reference; new models can be requested via the Kaggle Discussion tab.
- **Compute pointers** in the [Resources](#resources) section — free GPU notebooks, hosted endpoints, and (for UW participants) shared GPU access through ML+X, NRP, and CHTC.

### Terminal-Bench

[Terminal-Bench 2.0](https://tbench.ai) is the benchmark we score against — an open, industry-standard collection of 89 tasks spanning software engineering, security, data processing, system administration, and scientific computing. Each task ships as a Docker image with a starting environment, a natural-language instruction, and a hidden test suite that grades the container's final state. All 89 tasks are public and can be browsed at [tbench.ai](https://www.tbench.ai/).

Your agent receives the instruction and is given shell access to the running container. It inspects the codebase the way a developer would — `ls`, `cat`, `grep`, `find`, `git log`, `pytest`, anything it wants to run — edits files by writing to disk, executes builds and tests, observes the output, and decides what to do next. There is no special tooling; the agent succeeds by knowing what commands to issue and how to interpret what comes back.

**Where the agent code lives.** The decision logic — what to prompt the model with, how to parse its response into a shell command, when to stop — is your code, not the benchmark's. You write a Python class implementing the `BaseAgent` interface from [Harbor](https://www.harborframework.com/), the open-source evaluation framework for Terminal-Bench 2.0. Harbor invokes your class's `run(instruction, environment)` method when a task starts; your code prompts the model with the instruction (plus a system prompt and the running conversation), parses the response into a bash command, runs it via `environment.exec()`, observes the output, decides the next step, and returns when the task is done. The baseline in [`starter/agent/agent.py`](starter/agent/agent.py) is a ~60-line ReAct loop you can fork. Pointing Harbor at your agent is a single CLI flag — `--agent-import-path agent.agent:YourAgentClass` — and the same string is what your submission card declares. Full integration details are in [`starter/docs/harbor.md`](starter/docs/harbor.md) and Harbor's upstream [Running Terminal-Bench tutorial](https://www.harborframework.com/docs/tutorials/running-terminal-bench).

### Example tasks

Three representative tasks from Terminal-Bench, one from each end of the difficulty spectrum and one in between:

- **fix-git** (easy, software-engineering) — The container holds a small git repo in which a recent `git reset --hard` orphaned several commits of feature work. The branch *looks* clean, but the work is gone from `main`. The agent has to recognize that something was lost, use `git reflog` to locate the orphaned commits, recover them, merge them back into `main` cleanly, and resolve any conflicts that appear. Tests whether the agent can read git's terminal output, recognize a non-obvious failure state, and recall less-common git subcommands.

- **build-cython-ext** (medium, debugging) — A Cython extension that no longer compiles because the project's NumPy version moved forward and the underlying C API changed. The agent has to read the compiler error, trace it to the deprecated NumPy symbols in the `.pyx` source, patch either the source or the build configuration, and produce a working compiled extension that the test suite can import. Tests cross-language debugging, build-toolchain reasoning, and the discipline to re-run after each fix instead of guessing twice.

- **configure-webserver** (hard, system-administration) — A bare Linux container that needs to be turned into a self-deploying web server: when commits land in a designated local git repo, the served site should update automatically. The agent has to choose a server (nginx, lighttpd, caddy — its call), wire up a `post-receive` hook or equivalent, ensure the service starts on boot, and prove the end-to-end loop with a test commit. Tests multi-component system design and the kind of "no single right answer" judgment that fewer benchmarks capture.

Browse all 89 tasks with filters at [tbench.ai](https://www.tbench.ai/).

### Considerations

**Models (binding).** Pick a model from [`MODELS.md`](MODELS.md) with a reported VRAM of **48 GB or less**. That table maps each `(model, quantization)` to a canonical *reported VRAM* — you don't measure VRAM yourself, you pick a row, and the row decides eligibility. **Suggested anchor: `Qwen/Qwen2.5-Coder-32B-Instruct-AWQ` (28 GB).** Want to use a model that isn't listed? Post in the Kaggle Discussion tab — organizers add rows on request, usually within a day or two.

**What's not eligible:**
- **Closed-weight models** (GPT, Claude, Gemini) anywhere in your system, including "just the planner."
- **Any endpoint that won't tell you what it's serving.** If a provider doesn't disclose the exact `(model, quantization)` behind their API, you can't pin your submission to a `MODELS.md` row. Fine for prototyping, but your submitted run needs to use a listed model on an endpoint that names it.

**Per-task budget:**
- **No human-in-the-loop at evaluation time.** Terminal-Bench scoring is fully deterministic — pytest passes or fails, no LLM judges, no subjective grading.
- **No hard turn cap.** Set whatever per-task turn / wall-clock limit suits your dev loop. Total tokens only break leaderboard ties, but a verbose loop is also a slow one — your own patience will enforce a budget.

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

Two rules:

1. **VRAM limit (eligibility).** Your model's *reported VRAM* — the canonical number for your `(model, quantization)` row in [`MODELS.md`](MODELS.md) — must be **48 GB or less**. You don't measure VRAM yourself; you pick a row, and the row decides eligibility.
2. **Ranking.** Submissions are ranked by **`TB_score`** — mean Terminal-Bench reward across all 89 tasks (single attempt per task, `--n-attempts 1`). Ties are broken by fewer **`total_tokens`** — the sum of `n_input_tokens + n_output_tokens` across all 89 tasks, taken straight from Harbor's per-task `result.json`.

The limit is what makes this a scaffold-engineering challenge rather than a model-shopping one: everyone picks from models that fit on a single serious GPU, and the ranking rewards whoever gets the most out of that pool.

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

These three numbers, plus your model row from [`MODELS.md`](MODELS.md), are what go on the submission card. Ranking is by Terminal-Bench score, with total tokens breaking ties — nothing else is computed.

### Reproducibility check (finale)

There is no rubric, no human-scored writeup component, no engineering-depth panel. Ranking is Terminal-Bench score, under the VRAM limit. At the finale, organizers re-run the top ~10 submissions to confirm the result:

1. **Score reproduction** — clone at the tagged commit, run `harbor run` against all 89 tasks, confirm the reported `TB_score` reproduces within run-to-run noise.
2. **Held-out subset** — run the same agent against a private subset of ~20 fresh Terminal-Bench tasks not in the public set during the semester. Significantly lower private-set scores get investigated for task-specific hardcoding.
3. **Token + model verification** — confirm `total_tokens` matches the submission card and that the running agent is talking to the same model row claimed in the card.

Honest run-to-run variance is fine. Significant discrepancies, hardcoding, or model/quantization mismatches disqualify.

### Required elements (pass/fail)

| Requirement | Pass/Fail |
|---|---|
| Submission card fully filled out | Yes/No |
| Model + quantization listed in [`MODELS.md`](MODELS.md) with reported VRAM ≤ 48 GB | Yes/No |
| Agent runs via `harbor run --agent-import-path` without modification | Yes/No |
| Open weights only (no closed-weight or opaque-provider API calls) | Yes/No |
| All 89 Terminal-Bench tasks evaluated | Yes/No |
| Public GitHub repo with tagged commit, licensed MIT or Apache 2.0 | Yes/No |

---

## Submitting your solution

**One submission per team, at the end of the semester.** There is no live leaderboard and no mid-semester submissions — focus on building and understanding, not chasing a number.

During the semester, share early and often via the Kaggle Discussion tab: post draft writeups, share your repo, describe what's working and what isn't. Think of Discussion as an open lab notebook for the cohort.

### Part 1: Submission card

Structured metadata used for automated ranking. Evaluation is always against all 89 Terminal-Bench tasks (single attempt each) — you don't declare that separately.

**Fields you fill in:**

| Field | Example | Format |
|---|---|---|
| Team name | Terminal Velocity | free text |
| GitHub repo URL | `github.com/team/agent` | URL |
| Commit tag / SHA | `v1.0-submission` | git ref pointing at the exact code you ran |
| Model | `Qwen/Qwen2.5-Coder-32B-Instruct-AWQ` | HuggingFace id — must match a row in [`MODELS.md`](MODELS.md) |
| Quantization | `AWQ 4-bit` | one of the values below |
| Terminal-Bench score (across 89 tasks) | `0.42` | mean reward, 0–1 |
| Total tokens (across 89 tasks) | `1,263,800` | sum of `n_input_tokens + n_output_tokens` from Harbor's `result.json` — used only to break ties |
| GPU used | `RTX A6000 48 GB` | informational, not scored |
| Mean wall-clock per task | `3m 12s` | informational, not scored |

**Valid quantization values** (must match the `MODELS.md` row for your chosen model): `bf16`, `FP16`, `FP8`, `Int8`, `AWQ 4-bit`, `GPTQ 4-bit`, `Int4`, `MXFP4`, `NVFP4`, `w4a16 (QAT)`.

**Fields computed for you:**

| Field | Example | How it's derived |
|---|---|---|
| Reported VRAM | `28 GB` | Looked up from your `(Model, Quantization)` row in [`MODELS.md`](MODELS.md) — must be **≤ 48 GB** for the submission to be eligible |

### Part 2: Writeup

A single writeup (≤5,000 words) attached to your Kaggle submission. Problem framing, approach, what worked, what didn't, Terminal-Bench scores, failure analysis, limitations, what you'd do with another month. Quality > length.

Your code lives in the GitHub repo pointed at by your submission card — you don't attach it separately.

---

## Getting started

The fastest path from "I registered" to "my agent has a Terminal-Bench score" lives in [`starter/`](starter/). Roughly:

1. **Install** Docker, [uv](https://docs.astral.sh/uv/), Python 3.12.
2. **Clone** this repo, create a venv, `uv pip install -e starter/`.
3. **Verify Harbor** with the oracle agent (no model required):
   ```bash
   harbor run -d terminal-bench-sample@2.0 -a oracle
   ```
4. **Set up a model endpoint** — Ollama is easiest: `ollama pull qwen2.5-coder:14b` works on smaller GPUs for first-week dev. All options in [`starter/docs/byo_model.md`](starter/docs/byo_model.md).
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

A submitted run has two separate compute needs: **the machine that runs Harbor + your agent** (needs Docker host access), and **the endpoint that serves the model** (any OpenAI-compatible HTTP endpoint). They can be the same machine or different machines. Options for each below.

### Where to run Harbor + your agent (needs Docker)

Harbor spins up a fresh Docker container per Terminal-Bench task, so the machine you run `harbor run` from needs host Docker. That rules out Kaggle Notebooks and Google Colab — both explicitly block the privileged access Docker requires. Viable options:

- **Your own machine** — laptop, workstation, or lab machine with Docker Desktop (macOS/Windows) or Docker Engine (Linux). Cheapest option. Give Docker at least ~30 GB of disk for task images.
- **A rented Linux VM** — Lambda Labs, RunPod, Vast.ai, Hetzner, EC2, GCE. Any VM you have root on and can install Docker on. If you're also self-hosting the model on the same box, get one with a GPU that fits your `MODELS.md` row.
- **UW-Madison RunAI pod** — available to UW participants; comes preconfigured with Docker.

### Where to serve the model (any OpenAI-compatible endpoint)

The model server is independent. Any endpoint your agent code can HTTP-POST to works.

**Hosted (no GPU required):**

- **NVIDIA API catalog** ([build.nvidia.com](https://build.nvidia.com/)) — Free, OpenAI-compatible endpoints for 100+ open-weight models including Qwen2.5-Coder-32B. Free tier: 1,000 inference credits on signup (up to 5,000 on request), shared ~40 RPM across all calls. Good for prompt iteration and small eval runs; the rate cap makes a full 89-task sweep slow but doable.
- **Amazon Bedrock** — Pay-per-token, fully-managed access to the Qwen3 lineup (`qwen3-coder-30b-a3b`, `qwen3-coder-480b-a35b`, `qwen3-coder-next`, `qwen3-235b-a22b-instruct-2507`, `qwen3-32b`). AWS doesn't formally publish the serving quantization, so the VRAM mapping in [`MODELS.md`](MODELS.md) is an approximation based on FP8. [aws.amazon.com/bedrock](https://aws.amazon.com/bedrock/)
- **NRP managed-LLM endpoint** (UW participants) — CILogon-authenticated OpenAI-compatible endpoint at `https://ellm.nrp-nautilus.io/v1` hosting Qwen3 (397B), GLM-5 (744B), Kimi-K2.7-Code (1T), Gemma-4, MiniMax-M2, GPT-OSS-120B, and more. Most of these exceed the 48 GB submission limit — useful for prototyping and comparison, not for the submitted run. [nrp.ai/llms](https://nrp.ai/llms/)

**Self-hosted on your own GPU or a rented one:**

- Any GPU large enough to fit the reported VRAM of your chosen `MODELS.md` row. The suggested anchor (`Qwen2.5-Coder-32B-Instruct-AWQ`, 28 GB) runs comfortably on an RTX A6000 48 GB, L40S 48 GB, RTX Pro 6000 96 GB (or half-slice), or any 32 GB+ card with reduced context. Ollama or vLLM setup in [`starter/docs/byo_model.md`](starter/docs/byo_model.md).
- **NRP GPU pods** (UW participants) — A100, L40S, A40, RTX 4090, etc. Spin up your own vLLM. [nrp.ai/get-access](https://nrp.ai/get-access/).
- **CHTC** (UW participants) — [chtc.cs.wisc.edu](https://chtc.cs.wisc.edu/). Free shared campus GPU pool, good for batch sweeps and fine-tuning.

**Kaggle Notebooks and Google Colab** can host a model server behind a tunnel (ngrok, cloudflared) so a remote Harbor machine can reach them — but it's fragile (Colab drops after ~90 min idle, Kaggle caps sessions at 12 hr, free tunnel providers have request limits) and slower than any of the alternatives above. Fine for prompt iteration; not recommended for the submitted eval run.

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
See [Resources](#resources). For dev, NVIDIA's API catalog and Kaggle Notebooks both work without local hardware. Whatever model you finally submit must be a row in `MODELS.md`.

**I'm not at UW.**
Welcome. The challenge is fully open. You won't have access to weekly sprints, office hours, NRP, or RunAI endpoints, but the leaderboard is the leaderboard — you compete on equal footing.

**Will there be a live leaderboard during the semester?**
No live leaderboard. Run Terminal-Bench locally, track your own progress, share findings via the Discussion tab. At the deadline, everyone submits a structured submission card — that's the ranking. Organizers spot-check the top ~10 for reproducibility and generalization. You can also submit independently to the [public Terminal-Bench leaderboard](https://tbench.ai/leaderboard).

**What's the relationship to the upstream Terminal-Bench project?**
We're users and fans — but this challenge is a separate event. We don't speak for the Terminal-Bench maintainers.

---

## Citation

```
Chris Endemann et al. MLM26: Local Coding Agent Challenge.
https://kaggle.com/competitions/MLM26-EfficientCoder, 2026. Kaggle.
```

---

## Organizer notes (delete before publishing)

- [ ] Ask NRP staff (via the Nautilus AI/ML Matrix channel at `matrix.nrp-nautilus.io`) whether they would deploy a shared Qwen2.5-Coder-32B-AWQ endpoint for challenge participants, in addition to the existing managed-LLM catalog. If yes, every team — UW or not — gets a frictionless path to the suggested anchor model. Worth asking about Qwen3-Coder-30B-A3B too.
- [ ] Stand up the submission-card validator (checks the model row is ≤ 48 GB reported VRAM and the token/score fields parse).
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
