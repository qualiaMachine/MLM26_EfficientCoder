# MLM26: Local Coding Agent Challenge

Build the best local coding agent — measured on Terminal-Bench 2.0. Hosted by [ML+X](https://mlx.wisc.edu/) at UW–Madison, September–December 2026. Open to everyone.


---

## Overview

The last two years have transformed how software gets built. Frontier coding agents — Claude Code, Cursor, Codex, Devin — can now read a codebase, plan changes across many files, run tests, and recover from errors well enough to feel like real (if junior) collaborators. They are remarkable, but they are also closed and expensive: every keystroke flows to a third party, costs accumulate per task, and anyone working with sensitive data has to be careful nothing leaks.

Open-weight models have closed enough of the raw-quality gap that a credible coding agent can now plausibly run locally. *Plausibly*, but not yet *well*. The challenge is intended as a collaborative effort to close the remaining gap. You will build an autonomous coding agent on top of an open-weight model of your choice and measure it on [Terminal-Bench 2.0](https://tbench.ai), an industry-standard 89-task benchmark used to evaluate Claude Code, Cursor, and friends. Every submission runs on one of a handful of approved models in the 7–35 GB class, so the leverage is in the scaffold: a 14B model wrapped in a thoughtful agent loop can credibly beat a 32B with a naive one. The goal is not to build the largest agent, but the most *useful* one under realistic constraints.

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
- **Beats the leaderboard** — scored by Terminal-Bench performance minus a small token penalty, on an approved open-weight model (see [Evaluation](#evaluation)).

Architecture, prompting strategy, retrieval, tool design, and planning logic are all up to you. The starter code is a deliberately minimal [ReAct](https://arxiv.org/abs/2210.03629) loop — the model *reasons* about the next step, *acts* by emitting a shell command, observes the output, and repeats until it decides the task is done. It's a launchpad, not a solution.

### Starter materials

- [`starter/`](starter/) — a minimal ReAct baseline agent (~200 lines) wired into Harbor, meant to be forked and rebuilt.
- [`starter/docs/`](starter/docs/) — an end-to-end walkthrough (fresh machine → first Terminal-Bench score), model endpoint setup, and troubleshooting.
- [`MODELS.md`](MODELS.md) — the approved model list: six `(model, quantization)` rows, 7–35 GB. Additions can be requested via the Kaggle Discussion tab.
- [Resources](#resources) — where to run the benchmark and where to serve a model, with or without your own GPU.

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

**Models (binding).** Use one of the approved models in [`MODELS.md`](MODELS.md) — a deliberately short list (four model families, 7–35 GB reported VRAM) so the competition is about the scaffold, not model shopping. **Anchor: `Qwen/Qwen3.6-27B-FP8` (32 GB).** Development on any open-weight model is fine; the list governs the submitted run. Want a model added? Post in the Kaggle Discussion tab with the case for it — organizers respond within a day or two.

**What's not eligible:**
- **Closed-weight models** (GPT, Claude, Gemini) anywhere in your system, including "just the planner."
- **Any endpoint that won't tell you what it's serving.** If a provider doesn't disclose the exact `(model, quantization)` behind their API, you can't pin your submission to a `MODELS.md` row. Fine for prototyping, but your submitted run needs to use a listed model on an endpoint that names it.

**Per-task budget:**
- **No human-in-the-loop at evaluation time.** Terminal-Bench scoring is fully deterministic — pytest passes or fails, no LLM judges, no subjective grading.
- **No hard turn cap.** Set whatever per-task turn / wall-clock limit suits your dev loop. The token penalty (0.01 per million) already charges verbose agents, so no cap is needed.

**Generalizability.** One system prompt, one agent loop, no per-task `if task == "fix-git"` branching. Detecting task *categories* (e.g., "this looks like a debugging task") and adjusting strategy is fine — that's good engineering. Hardcoding solutions or prompts for individual tasks is not. At the finale, organizers re-run the top 5 submissions and review the code; task-specific hardcoding disqualifies.

---

## Evaluation

### Scoring

One eligibility rule, one formula.

**Eligibility.** Your submitted run must use one of the `(model, quantization)` rows in [`MODELS.md`](MODELS.md). Equivalent quantizations of a listed model (GGUF/Q4_K_M, GPTQ-Int4) count as its 4-bit row.

**Score.**

```
leaderboard_score = TB_score − 0.01 × (total_tokens / 1,000,000)
```

Where:
- **`TB_score`** is your mean Terminal-Bench reward across all 89 tasks (single attempt per task, `--n-attempts 1`) — a value between 0 and 1.
- **`total_tokens`** is the sum of `n_input_tokens + n_output_tokens` across all 89 tasks, taken straight from Harbor's per-task `result.json`.

The weighting in plain English: **every million tokens costs one point** (0.01) of Terminal-Bench score. A typical run spends 1–3M tokens, so the penalty lands around 0.01–0.03 — enough to decide races between agents of similar capability, never enough to beat a real capability gap. Worked example: TB 0.42 with 1.26M tokens scores `0.42 − 0.0126 = 0.407`; the same agent rerun with a verbose loop at 2.5M tokens drops to `0.395`.

The approved-model list plus the token penalty is what makes this a scaffold-engineering challenge: everyone picks from the same small pool of models, and the ranking rewards whoever gets the most out of it, most economically.

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

These three numbers, plus your model row from [`MODELS.md`](MODELS.md), are what go on the submission card. The leaderboard computes your score from them — the formula above is all there is.

### Reproducibility check (finale)

There is no rubric, no human-scored writeup component, no engineering-depth panel. Ranking is the formula above, on approved models. At the finale, organizers re-run the top 5 submissions to confirm the result:

1. **Score reproduction** — clone at the tagged commit, run `harbor run` against all 89 tasks, confirm the reported `TB_score` reproduces within run-to-run noise.
2. **Hardcoding check** — review the agent code at the tagged commit for task-specific branching, hardcoded solutions, or prompts written for individual tasks. All 89 tasks are public, so this is a code review, not a data check.
3. **Token + model verification** — confirm `total_tokens` matches the submission card and that the running agent is talking to the same model row claimed in the card.

Honest run-to-run variance is fine. Significant discrepancies, hardcoding, or model/quantization mismatches disqualify.

### Required elements (pass/fail)

| Requirement | Pass/Fail |
|---|---|
| Submission card fully filled out | Yes/No |
| Model + quantization on the approved list in [`MODELS.md`](MODELS.md) | Yes/No |
| Agent runs via `harbor run --agent-import-path` without modification | Yes/No |
| Open weights only (no closed-weight or opaque-provider API calls) | Yes/No |
| All 89 Terminal-Bench tasks evaluated | Yes/No |
| Public GitHub repo with tagged commit, licensed MIT or Apache 2.0 | Yes/No |
| Writeup covering all sections of [`WRITEUP_TEMPLATE.md`](WRITEUP_TEMPLATE.md) | Yes/No |


---

## Submitting your solution

Submissions go through Kaggle as a standardized one-row **`submission.csv`** with the fields below. The leaderboard is live: it recomputes your score on upload, and you can resubmit as your agent improves. Your standing at the deadline is what counts, and the top 5 get re-run and code-reviewed at the finale.

During the competition, also share early and often via the Kaggle Discussion tab: post draft writeups, share your repo, describe what's working and what isn't. Think of Discussion as an open lab notebook for the cohort.

### Part 1: Submission card (`submission.csv`)

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
| Total tokens (across 89 tasks) | `1,263,800` | sum of `n_input_tokens + n_output_tokens` from Harbor's `result.json` — feeds the token penalty |
| GPU used | `RTX A6000 48 GB` | informational, not scored |
| Mean wall-clock per task | `3m 12s` | informational, not scored |

**Valid quantization values** (must match the `MODELS.md` row for your chosen model): `FP8`, `Int4`, `AWQ 4-bit`. GGUF/Q4_K_M and GPTQ-Int4 checkpoints count as the model's `AWQ 4-bit` row.

**Fields computed for you:**

| Field | Example | How it's derived |
|---|---|---|
| Reported VRAM | `28 GB` | Looked up from your `(Model, Quantization)` row in [`MODELS.md`](MODELS.md) — informational; eligibility is simply being on the list |
| **Leaderboard score** | **`0.407`** | `TB_score − 0.01 × (total_tokens / 1M)` — for this example, `0.42 − 0.01 × 1.2638` |

### Part 2: Writeup (required)

A single writeup (≤5,000 words) attached to your Kaggle submission, following [`WRITEUP_TEMPLATE.md`](WRITEUP_TEMPLATE.md) — architecture, experiments (including failed ones), results, failure analysis, what you borrowed and what you added. **Submissions without a writeup covering all template sections are ineligible.** It's checked pass/fail for completeness, not judged on prose — it doesn't affect your rank, but it's how your work outlives the leaderboard.

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
| [`starter/docs/byo_model.md`](starter/docs/byo_model.md) | Ollama, vLLM, hosted endpoints, `.env` config |
| [`starter/docs/harbor.md`](starter/docs/harbor.md) | Harbor mental model, custom agents, leaderboard submission |
| [`starter/docs/troubleshooting.md`](starter/docs/troubleshooting.md) | First-week issues, in order of likelihood |


---

## Resources

A submitted run has two separate compute needs: **the machine that runs Harbor + your agent** (needs Docker host access), and **the endpoint that serves the model** (any OpenAI-compatible HTTP endpoint). They can be the same machine or different machines. Options for each below.

### Where to run Harbor + your agent (needs Docker)

Harbor spins up a fresh Docker container per Terminal-Bench task, so the machine you run `harbor run` from needs host Docker. That rules out Kaggle Notebooks and Google Colab — both explicitly block the privileged access Docker requires. Viable options:

- **Your own machine** — laptop, workstation, or lab machine with Docker Desktop (macOS/Windows) or Docker Engine (Linux). Cheapest option. Give Docker at least ~30 GB of disk for task images.
- **A rented Linux VM** — Lambda Labs, RunPod, Vast.ai, Hetzner, EC2, GCE. Any VM you have root on and can install Docker on. If you're also self-hosting the model on the same box, get one with a GPU that fits your `MODELS.md` row.
- **UW–Madison RunAI pod** — available to UW–Madison participants; comes preconfigured with Docker.

### Where to serve the model (any OpenAI-compatible endpoint)

The model server is independent. Any endpoint your agent code can HTTP-POST to works.

**Hosted (no GPU required):**

- **NVIDIA API catalog** ([build.nvidia.com](https://build.nvidia.com/)) — Free, OpenAI-compatible endpoints for 100+ open-weight models including Qwen2.5-Coder-32B. Free tier: 1,000 inference credits on signup (up to 5,000 on request), shared ~40 RPM across all calls. Good for prompt iteration and small eval runs; the rate cap makes a full 89-task sweep slow but doable.
- **Amazon Bedrock** — Pay-per-token, fully-managed `qwen3-coder-30b-a3b`, which counts as the approved `Qwen3-Coder-30B-A3B-Instruct-FP8` row (AWS doesn't formally publish serving precision; FP8 assumed). Bedrock's other models aren't on the approved list. [aws.amazon.com/bedrock](https://aws.amazon.com/bedrock/)
- **NRP managed-LLM endpoint** (UW–Madison participants) — CILogon-authenticated OpenAI-compatible endpoint at `https://ellm.nrp-nautilus.io/v1` hosting Qwen3 (397B), GLM-5 (744B), Kimi-K2.7-Code (1T), Gemma-4, MiniMax-M2, GPT-OSS-120B, and more. None of these are on the approved list — useful for prototyping and comparison, not for the submitted run. [nrp.ai/llms](https://nrp.ai/llms/)

**Self-hosted on your own GPU or a rented one:**

- Any GPU large enough to fit the reported VRAM of your chosen `MODELS.md` row. The anchor (`Qwen3.6-27B-FP8`, 32 GB) wants a ~40 GB+ card (RTX A6000, L40S, A100); the AWQ/Int4 rows cover everything from 12 GB cards up. Ollama or vLLM setup in [`starter/docs/byo_model.md`](starter/docs/byo_model.md).
- **NRP GPU pods** (UW–Madison participants) — A100, L40S, A40, RTX 4090, etc. Spin up your own vLLM. [nrp.ai/get-access](https://nrp.ai/get-access/).
- **CHTC** (UW–Madison participants) — [chtc.cs.wisc.edu](https://chtc.cs.wisc.edu/). Free shared campus GPU pool, good for batch sweeps and fine-tuning.

**Kaggle Notebooks and Google Colab** can host a model server behind a tunnel (ngrok, cloudflared) so a remote Harbor machine can reach them — but it's fragile (Colab drops after ~90 min idle, Kaggle caps sessions at 12 hr, free tunnel providers have request limits) and slower than any of the alternatives above. Fine for prompt iteration; not recommended for the submitted eval run.


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

**API keys deserve their own paragraph, because your agent can read files.** Anything an agent `cat`s — including `.env` — enters the model conversation and the endpoint's logs. During `harbor run` you're fine: task containers don't inherit your host environment. The exposure is dev-loop testing with local shell access. In order of effort:

- Use a throwaway key created for this event, never a personal or work key. If an agent may have read it, treat it as burned and rotate it.
- Keep `.env` out of any directory you point a dev agent at — the agent needs the key *in its process environment* to call the endpoint, not on disk where it explores.
- If you already use a secrets manager, inject at runtime instead of keeping a plaintext file: e.g. `op run --env-file .env.tpl -- ./scripts/run_baseline.sh` (1Password CLI), or the `pass`/Bitwarden equivalents. Know the limit: this removes the at-rest file, but the running agent still holds the key in memory — no tool changes the "rotate if touched" rule.

**If your agent does something unexpected and concerning, tell us.** Novel failure modes are findings, not embarrassments — they're also great writeup material.


---

## FAQ

**Can I use a closed-weight model just for planning, with a local model for execution?**
No. If part of your system calls GPT, Claude, or Gemini, it's out of scope.

**Can I use Amazon Bedrock?**
Narrowly, yes. The fully-managed pay-per-token `qwen3-coder-30b-a3b` counts as the approved `Qwen3-Coder-30B-A3B-Instruct-FP8` row (AWS doesn't officially state serving precision; FP8 assumed, corrected if AWS confirms otherwise). Bedrock's other models aren't on the approved list. **Bedrock Custom Model Import** is not viable (Provisioned-Throughput-only at $21–50/hr with a 1- or 6-month commit). If you want AWS for self-hosting, rent an EC2 or SageMaker GPU instance and self-host with vLLM — that's just cloud compute, fine like any other rented GPU. **But be extremely careful with costs:** GPU instances run $1–5+/hr and bill while idle, so a forgotten instance over a weekend is a three-figure surprise. Set a billing alarm before launching anything, stop instances the moment a run finishes, and consider the flat-rate marketplaces (Lambda, RunPod, Vast.ai) first — they're cheaper for this and easier to reason about.

**The model I want isn't in `MODELS.md`. What do I do?**
The list is deliberately short — the competition is about the scaffold, not model shopping. If you think a model materially changes what's possible (a new open-weight coder release, a hardware tier the list doesn't serve), post the case in the Kaggle Discussion tab with the HuggingFace link and quantization. Organizers respond within a day or two.

**Can I fine-tune a model for this?**
Yes, if the base is an approved model. The fine-tune counts as its base model's row. Document it in the writeup; weights must be either public or reproducible from the public base + your published LoRA/adapter.

**Can I use multiple models (e.g., a small planner + a larger coder)?**
Yes, as long as every model involved is on the approved list. The submission card carries the largest model's row; token counts sum across all models, and you should be ready to defend the setup on the reproducibility check.

**Can I submit my agent to the public Terminal-Bench leaderboard?**
Yes, please. It's independent of this challenge — a real leaderboard and a real artifact.

**Do I need to use the entire Terminal-Bench task set during the competition?**
No — work with whatever subset is useful for debugging. For the leaderboard, your submission must report results on all 89 tasks; at the finale, organizers re-run the top 5 and review their code for task-specific hardcoding.

**My team is just me. / My team is five people.**
Both fine. Teams of 1–5. Reflect honestly on contributions in the writeup.

**I don't have a GPU.**
See [Resources](#resources). For dev, NVIDIA's API catalog and the hosted APIs in [Resources](#resources) work without local hardware. Whatever model you finally submit must be a row in `MODELS.md`.

**I'm not at UW–Madison.**
Welcome. The challenge is fully open. You won't have access to weekly sprints, office hours, NRP, or RunAI endpoints, but the leaderboard is the leaderboard — you compete on equal footing.

**Will there be a live leaderboard during the competition?**
Yes. Submissions are a standardized `submission.csv` uploaded to Kaggle; the leaderboard recomputes scores as they land, and you can resubmit throughout the competition. Scores are self-reported from your own Harbor runs — the top 5 get re-run and code-reviewed at the finale, so submit numbers you can reproduce. You can also submit independently to the [public Terminal-Bench leaderboard](https://tbench.ai/leaderboard).

**What's the relationship to the upstream Terminal-Bench project?**
We're users and fans — but this challenge is a separate event. We don't speak for the Terminal-Bench maintainers.


---

## Contact

Chris Endemann (endemann@wisc.edu) — ML+X, UW–Madison.

Hosted by [ML+X](https://mlx.wisc.edu/) at the University of Wisconsin–Madison. Sponsor info: https://hub.datascience.wisc.edu/communities/mlx/sponsorship/

---

## Citation

```
Chris Endemann et al. MLM26: Local Coding Agent Challenge.
https://kaggle.com/competitions/MLM26-EfficientCoder, 2026. Kaggle.
```


