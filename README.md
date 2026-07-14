# MLM26: EfficientCoder

Build the best open coding agent under real efficiency constraints — no proprietary models, no giant clusters, scored on Terminal-Bench 2.0. Hosted by [ML+X](https://mlx.wisc.edu/) at UW–Madison, September–December 2026. Open to everyone.




---

## Overview

The last two years have transformed how software gets built. Frontier coding agents — Claude Code, Cursor, Codex, Devin — can now read a codebase, plan changes across many files, run tests, and recover from errors well enough to feel like real (if junior) collaborators. They are remarkable, but they are also closed and expensive: every keystroke flows to a third party, costs accumulate per task, and anyone working with sensitive data has to be careful nothing leaks.

Open-weight models have closed enough of the raw-quality gap that a credible coding agent can now plausibly run locally. *Plausibly*, but not yet *well*. The challenge is intended as a collaborative effort to close the remaining gap. You will build an autonomous coding agent on top of an approved open-weight model and measure it on [Terminal-Bench 2.0](https://tbench.ai), an industry-standard 89-task benchmark used to evaluate Claude Code, Cursor, and friends. Every submission runs on one of a handful of approved models in the 7–37 GB class, so the leverage is in the scaffold: a 14B model wrapped in a thoughtful agent loop can credibly beat a 32B with a naive one. The goal is not to build the largest agent, but the most *useful* one under realistic constraints.

This is an **educational, collaborative challenge**. There are no cash prizes, no rankings-based awards, and no reason to hoard ideas. Share repos early, post findings to the Discussion tab, fork and build on each other's approaches. Credit what you borrowed in your writeup and explain what you added. Every improvement one team publishes raises the floor for everyone else — and every step forward here pushes the open-source community closer to genuine independence from closed frontier tools when it comes to agentic coding.




---

## Description

### Background

A raw language model can read a task description and emit a reasonable command, but it cannot, on its own, solve a multi-step coding problem that spans dozens of shell invocations and recovers from a chain of errors. It loses track of context, repeats failed commands, hallucinates files that do not exist, and does not know when to stop. The distance between "can think about code" and "can autonomously navigate a real engineering problem" is enormous — and bridging it is the central craft of building a coding agent.

The **scaffold** (or *agent harness*) is the code wrapped around the model that keeps track of context, recovers from failed commands, decides when the task is actually done, and chains reasoning, action, and verification into something that works reliably across a hundred turns. It's what separates an LLM and a shell from an agent. There is no consensus yet on what the best architecture looks like. Prompting strategies, tool design, planning logic, retrieval, multi-stage pipelines, self-critique, fine-tuning — the design space is wide open. *How* you build the agent matters as much as which model you pick — careful engineering on a small model can beat thoughtless deployment of a large one.

### Goal

Build an autonomous coding agent, running entirely on open-weight models, that:

- **Solves real software engineering tasks end-to-end** without human intervention — reading the problem, exploring the codebase, planning, executing, and verifying the result.
- **Generalizes** across Terminal-Bench's diverse task categories rather than memorizing solutions to individual tasks.
- **Runs efficiently** — modest memory footprint, lean token consumption — without sacrificing capability. Use one of the approved models below (roughly 7–37 GB reported VRAM) so the competition is about the scaffold, not model shopping.
- **Beats the leaderboard** — scored by Terminal-Bench performance minus a small token penalty, on an approved open-weight model (see [Evaluation](#evaluation)).

Architecture, prompting strategy, retrieval, tool design, and planning logic are all up to you. The starter code is a deliberately minimal [ReAct](https://arxiv.org/abs/2210.03629) loop — the model *reasons* about the next step, *acts* by emitting a shell command, observes the output, and repeats until it decides the task is done.

### Starter materials

[`starter/docs/walkthrough.md`](https://github.com/qualiaMachine/MLM26_EfficientCoder/blob/main/starter/docs/walkthrough.md) takes you from a fresh machine to a scored baseline run in about 30 minutes: Docker, Harbor, a model endpoint, first task. Start there.

- [`starter/README.md`](https://github.com/qualiaMachine/MLM26_EfficientCoder/blob/main/starter/README.md) — setup summary, where to modify the agent
- [`RESOURCES.md`](https://github.com/qualiaMachine/MLM26_EfficientCoder/blob/main/RESOURCES.md) — compute options for running the benchmark and serving a model
- [`FAQ.md`](https://github.com/qualiaMachine/MLM26_EfficientCoder/blob/main/FAQ.md) — models, Bedrock, fine-tuning, teams, leaderboard
- [`RULES.md`](https://github.com/qualiaMachine/MLM26_EfficientCoder/blob/main/RULES.md) — team limits, submission limits, integrity, licensing
- [Agent safety](https://github.com/qualiaMachine/MLM26_EfficientCoder/blob/main/starter/docs/safety.md) — keep your dev machine safe

### Terminal-Bench

[Terminal-Bench 2.0](https://tbench.ai) is the benchmark we score against — an open, industry-standard collection of 89 tasks spanning software engineering, security, data processing, system administration, and scientific computing. Each task ships as a Docker image with a starting environment, a natural-language instruction, and a hidden test suite that grades the container's final state. All 89 tasks are public and can be browsed at [tbench.ai](https://www.tbench.ai/).

Your agent receives the instruction and is given shell access to the running container. It inspects the codebase the way a developer would — `ls`, `cat`, `grep`, `find`, `git log`, `pytest`, anything it wants to run — edits files by writing to disk, executes builds and tests, observes the output, and decides what to do next. There is no special tooling; the agent succeeds by knowing what commands to issue and how to interpret what comes back.

**Where the agent code lives.** The decision logic — what to prompt the model with, how to parse its response into a shell command, when to stop — is your code, not the benchmark's. You write a Python class implementing the `BaseAgent` interface from [Harbor](https://www.harborframework.com/), the open-source evaluation framework for Terminal-Bench 2.0. Harbor invokes your class's `run(instruction, environment)` method when a task starts; your code prompts the model with the instruction (plus a system prompt and the running conversation), parses the response into a bash command, runs it via `environment.exec()`, observes the output, decides the next step, and returns when the task is done. The baseline in [`starter/agent/agent.py`](https://github.com/qualiaMachine/MLM26_EfficientCoder/blob/main/starter/agent/agent.py) is a ~60-line ReAct loop you can fork. Pointing Harbor at your agent is a single CLI flag — `--agent-import-path agent.agent:YourAgentClass`. Full integration details are in [`starter/docs/harbor.md`](https://github.com/qualiaMachine/MLM26_EfficientCoder/blob/main/starter/docs/harbor.md) and Harbor's upstream [Running Terminal-Bench tutorial](https://www.harborframework.com/docs/tutorials/running-terminal-bench).

### Example tasks

Three representative tasks from Terminal-Bench, one from each end of the difficulty spectrum and one in between:

- **fix-git** (easy, software-engineering) — The container holds a small git repo in which a recent `git reset --hard` orphaned several commits of feature work. The branch *looks* clean, but the work is gone from `main`. The agent has to recognize that something was lost, use `git reflog` to locate the orphaned commits, recover them, merge them back into `main` cleanly, and resolve any conflicts that appear. Tests whether the agent can read git's terminal output, recognize a non-obvious failure state, and recall less-common git subcommands.

- **build-cython-ext** (medium, debugging) — A Cython extension that no longer compiles because the project's NumPy version moved forward and the underlying C API changed. The agent has to read the compiler error, trace it to the deprecated NumPy symbols in the `.pyx` source, patch either the source or the build configuration, and produce a working compiled extension that the test suite can import. Tests cross-language debugging, build-toolchain reasoning, and the discipline to re-run after each fix instead of guessing twice.

- **configure-webserver** (hard, system-administration) — A bare Linux container that needs to be turned into a self-deploying web server: when commits land in a designated local git repo, the served site should update automatically. The agent has to choose a server (nginx, lighttpd, caddy — its call), wire up a `post-receive` hook or equivalent, ensure the service starts on boot, and prove the end-to-end loop with a test commit. Tests multi-component system design and the kind of "no single right answer" judgment that fewer benchmarks capture.

Browse all 89 tasks with filters at [tbench.ai](https://www.tbench.ai/).

### Approved models

Submissions must use one of the models below. The list is deliberately short so the competition is about how you build the scaffold, not which model you found. Scoring is Terminal-Bench score minus a small token penalty — see the Evaluation section below.

Development is unrestricted — prototype against any open-weight model or endpoint you like. The approved list governs the *submitted* run only.

**Pick by your GPU:** 8–12 GB → 7B AWQ · 16 GB → 14B AWQ · 24 GB → `qwen3-coder:30b` GGUF · 32–40 GB → 32B AWQ or 30B FP8 · 48 GB+ → the anchor.

| Model | FP8 | AWQ / 4-bit | Notes |
|---|---|---|---|
| Qwen3.6-27B | `Qwen/Qwen3.6-27B-FP8` (37 GB) | — none published | **Anchor.** Newest and strongest of the group; reasoning model with coder tool-calling. Self-host on a 48 GB card, or UW–Madison participants can use the hosted endpoint in [`starter/docs/byo_model.md`](https://github.com/qualiaMachine/MLM26_EfficientCoder/blob/main/starter/docs/byo_model.md). |
| Qwen3-Coder-30B-A3B | `Qwen/Qwen3-Coder-30B-A3B-Instruct-FP8` (35 GB) | `qwen3-coder:30b`, Ollama GGUF Q4_K_M (22 GB) — no official 4-bit safetensors exists | MoE: 30B total, ~3B active — fast. The GGUF runs on 24 GB cards, workable on 16 GB via expert offload. Bedrock's managed `qwen.qwen3-coder-30b-a3b-v1:0` counts as the FP8 column. |
| Qwen2.5-Coder-32B | — | `Qwen/Qwen2.5-Coder-32B-Instruct-AWQ` (28 GB) | A generation older but the most widely hosted (Together, Fireworks, NVIDIA API catalog) — easiest no-GPU path. |
| Qwen2.5-Coder-14B | — | `Qwen/Qwen2.5-Coder-14B-Instruct-AWQ` (15 GB) | Small-GPU tier (16 GB+ cards). |
| Qwen2.5-Coder-7B | — | `Qwen/Qwen2.5-Coder-7B-Instruct-AWQ` (9 GB) | Smallest approved; runs almost anywhere, expect a lower score ceiling. |

**Equivalent quantizations count as the same entry.** GGUF/Q4_K_M (Ollama) and GPTQ-Int4 checkpoints of a listed model map to its AWQ / 4-bit column; they're within ~10% of each other. Ollama's `qwen2.5-coder:7b/14b/32b` tags are the corresponding AWQ entries.

Reported VRAM is **weights + KV cache at a 16k context + ~2 GB overhead**, at single-batch concurrency — approximate by design, meant to tell you what hardware a model needs. You can verify any number (or the whole table) yourself with [`starter/scripts/estimate_vram.py`](https://github.com/qualiaMachine/MLM26_EfficientCoder/blob/main/starter/scripts/estimate_vram.py) and [`check_vram_table.py`](https://github.com/qualiaMachine/MLM26_EfficientCoder/blob/main/starter/scripts/check_vram_table.py) — no GPU needed; details in the script docstrings.

#### Requesting an addition

The list is meant to stay short, but it isn't frozen. If a model materially changes what's possible for participants (a new open-weight coder release, a hardware tier the list doesn't serve), post in the **Kaggle Discussion tab** with the HuggingFace id, the quantization, and the case for adding it. Additions should land at or under ~48 GB reported VRAM — a single serious GPU. Organizers respond within a day or two; once listed, the model is available to every team.

### Considerations

**Models (binding).** Your submitted run must use one of the approved models above. **Anchor: `Qwen/Qwen3.6-27B-FP8` (37 GB).**

**What's not eligible:**
- **Closed-weight models** (GPT, Claude, Gemini) anywhere in your system, including "just the planner."
- **Any endpoint that won't tell you what it's serving.** If a provider doesn't disclose the exact `(model, quantization)` behind their API, you can't pin your submission to an approved checkpoint. Fine for prototyping, but your submitted run needs to use a listed model on an endpoint that names it.

**Evaluation constraints:**
- **No human-in-the-loop at evaluation time.** Terminal-Bench scoring is fully deterministic — pytest passes or fails, no LLM judges, no subjective grading.
- **No hard turn cap.** Set whatever per-task turn / wall-clock limit suits your dev loop. The token penalty (0.01 per million) already charges verbose agents, so no cap is needed.

**Generalizability.** One system prompt, one agent loop, no per-task `if task == "fix-git"` branching. Detecting task *categories* (e.g., "this looks like a debugging task") and adjusting strategy is fine — that's good engineering. Hardcoding solutions or prompts for individual tasks is not. After the deadline, organizers re-run the top 5 submissions and review the code; task-specific hardcoding disqualifies.


### Contact

Chris Endemann (endemann@wisc.edu) — ML+X, UW–Madison.

Hosted by [ML+X](https://mlx.wisc.edu/) at the University of Wisconsin–Madison. Sponsor info: https://hub.datascience.wisc.edu/communities/mlx/sponsorship/

---

## Evaluation

### Scoring

One eligibility rule, one formula.

**Eligibility.** Your submitted run must use one of the `(model, quantization)` checkpoints in the approved model table above. Equivalent quantizations of a listed model (GGUF/Q4_K_M, GPTQ-Int4) count as its AWQ / 4-bit entry.

**Score.**

```
leaderboard_score = TB_score − 0.01 × (total_tokens / 1,000,000)
```

Where:
- **`TB_score`** is your mean Terminal-Bench reward across all 89 tasks (single attempt per task, `--n-attempts 1`) — a value between 0 and 1.
- **`total_tokens`** is the sum of `n_input_tokens + n_output_tokens` across all 89 tasks, taken straight from Harbor's per-task `result.json`.

The weighting in plain English: **every million tokens costs one point** (0.01) of Terminal-Bench score. A typical run spends 1–3M tokens, so the penalty lands around 0.01–0.03 — enough to decide races between agents of similar capability, never enough to beat a real capability gap. Worked example: TB 0.42 with 1.26M tokens scores `0.42 − 0.0126 = 0.407`; the same agent rerun with a verbose loop at 2.5M tokens drops to `0.395`.

The approved-model list plus the token penalty is what makes this a scaffold-engineering challenge: everyone picks from the same small pool of models, and the ranking rewards whoever gets the most out of it.

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

These three numbers, plus your approved model entry, are what go on the submission card. The leaderboard computes your score from them — the formula above is all there is.

### Submitting your solution

Submissions go through Kaggle as a standardized one-row **`submission.csv`** with the fields below. The leaderboard is live: it recomputes your score on upload, and you can resubmit as your agent improves. Your standing at the deadline is what counts, and the top 5 get re-run and code-reviewed after the deadline.

During the competition, also share early and often via the Kaggle Discussion tab: post draft writeups, share your repo, describe what's working and what isn't. Think of Discussion as an open lab notebook for the cohort.

#### Part 1: Submission card (`submission.csv`)

Structured metadata used for automated ranking. Evaluation is always against all 89 Terminal-Bench tasks (single attempt each) — you don't declare that separately.

One data row, exactly this header:

```
id,github_repo,commit_ref,model,quantization,tb_score,total_tokens,gpu,mean_wallclock_per_task,writeup_url
1,https://github.com/team/agent,v1.0-submission,Qwen/Qwen2.5-Coder-32B-Instruct-AWQ,AWQ 4-bit,0.42,1263800,RTX A6000 48 GB,3m 12s,https://kaggle.com/competitions/MLM26-EfficientCoder/discussion/…
```

(`id` is literally `1`. Malformed rows are rejected with a visible error at upload.)

**Fields you fill in:**

| Field | Example | Format |
|---|---|---|
| Team name | Terminal Velocity | free text |
| GitHub repo URL | `github.com/team/agent` | URL |
| Commit tag / SHA | `v1.0-submission` | git ref pointing at the exact code you ran |
| Model | `Qwen/Qwen2.5-Coder-32B-Instruct-AWQ` | HuggingFace id — must match an approved checkpoint |
| Quantization | `AWQ 4-bit` | one of the values below |
| Terminal-Bench score (across 89 tasks) | `0.42` | mean reward, 0–1 |
| Total tokens (across 89 tasks) | `1,263,800` | sum of `n_input_tokens + n_output_tokens` from Harbor's `result.json` — feeds the token penalty |
| GPU used | `RTX A6000 48 GB` | informational, not scored |
| Mean wall-clock per task | `3m 12s` | informational, not scored |
| Writeup URL | `kaggle.com/competitions/MLM26-EfficientCoder/discussion/…` | link to your writeup posted in the Discussion tab (see Part 2) |

**Valid quantization values** (must match the approved entry for your chosen model): `FP8`, `AWQ 4-bit`, `GGUF Q4_K_M`. GPTQ-Int4 checkpoints count as `AWQ 4-bit`.

**Fields computed for you:**

| Field | Example | How it's derived |
|---|---|---|
| Reported VRAM | `28 GB` | Looked up from your `(Model, Quantization)` entry in the approved model table — informational; eligibility is simply being on the list |
| **Leaderboard score** | **`0.407`** | `TB_score − 0.01 × (total_tokens / 1M)` — for this example, `0.42 − 0.01 × 1.2638` |

#### Part 2: Writeup (required)

A single writeup (≤2,500 words) posted in the competition's Discussion tab and linked from your submission card. [`WRITEUP_TEMPLATE.md`](https://github.com/qualiaMachine/MLM26_EfficientCoder/blob/main/WRITEUP_TEMPLATE.md) is a suggested structure if you want guidance — otherwise organize it however you like and fill it with whatever insights you learned. The one expectation: explain your learning journey — what you tried, what worked, what didn't, and where you ended up. **Submissions without a writeup are ineligible.** It's checked pass/fail, not judged on prose — it doesn't affect your rank, but it's how your work outlives the leaderboard.

Your code lives in the GitHub repo pointed at by your submission card — you don't attach it separately.

### Verification of top submissions

Leaderboard scores are self-reported, so before final standings are confirmed, organizers verify the top 5. For each one, we:

1. **Re-run the agent.** Clone the repo at the submitted commit, run it against all 89 tasks with the declared model, and check the score matches the reported one. LLM sampling is stochastic, so normal run-to-run variation is expected and fine.
2. **Check the numbers.** Confirm the reported token count matches, and that the agent is actually calling the model claimed in the submission.
3. **Read the code.** Look for hardcoded solutions or prompts written for individual tasks — all 89 tasks are public, so cheating is possible and this is how it's caught.

Significant discrepancies, hardcoding, running a different model than declared, or a missing writeup disqualify the submission. Beyond those pass/fail checks, nothing is judged — the writeup isn't graded, and the leaderboard score is the ranking.

### Required elements (pass/fail)

| Requirement | Pass/Fail |
|---|---|
| Submission card fully filled out | Yes/No |
| Model + quantization on the approved model list | Yes/No |
| Agent runs via `harbor run --agent-import-path` without modification | Yes/No |
| Open weights only (no closed-weight or opaque-provider API calls) | Yes/No |
| All 89 Terminal-Bench tasks evaluated | Yes/No |
| Public GitHub repo with tagged commit, licensed MIT or Apache 2.0 | Yes/No |
| Writeup posted in the Discussion tab and linked from the submission card | Yes/No |

---

## Citation

```
Chris Endemann et al. MLM26: EfficientCoder.
https://kaggle.com/competitions/MLM26-EfficientCoder, 2026. Kaggle.
```
