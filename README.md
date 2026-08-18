# Badger Code

Build the best open coding agent on a single GPU — no proprietary models, no giant clusters, scored on Terminal-Bench 2.1. Hosted by [ML+X](https://hub.datascience.wisc.edu/communities/mlx/) at UW–Madison, September–December 2026. Open to everyone.




---

## Overview

The last two years have transformed how software gets built. Frontier coding agents — Claude Code, Cursor, Codex, Devin — can now read a codebase, plan changes across many files, run tests, and recover from errors well enough to feel like real (if junior) collaborators. They are remarkable, but they are also closed and expensive: every keystroke flows to a third party, costs accumulate per task, and anyone working with sensitive data has to be careful nothing leaks.

Open-weight models have closed enough of the raw-quality gap that a credible coding agent can now plausibly run locally. *Plausibly*, but not yet *well*. The challenge is intended as a collaborative effort to help narrow the remaining gap. You will build an autonomous coding agent on top of an open-weight model and measure it on [Terminal-Bench 2.1](https://tbench.ai), an industry-standard 89-task benchmark used to evaluate Claude Code, Cursor, and friends. Every submission runs within the same **96 GB memory budget** — one serious GPU — and inside that ceiling both levers are yours: **which open-weight model you pick, and the scaffold or "agent harness" you wrap around it**. Neither wins alone. A 14B model in a thoughtful agent loop can credibly beat a 32B in a naive one, and finding the checkpoint that gets the most out of your budget is its own piece of engineering. The goal is not to build the largest agent, but the most *useful* one under realistic constraints.

This is an **educational, collaborative challenge**. There are no cash prizes, no rankings-based awards, and no reason to hoard ideas. Share repos early, post findings to the Discussion tab, fork and build on each other's approaches. Credit what you borrowed in your writeup and explain what you added. Every improvement one team publishes raises the floor for everyone else — and every step forward here pushes the open-source community closer to genuine independence from closed frontier tools when it comes to agentic coding.

**Soft launch.** The competition is open for submissions now; the official kickoff for UW–Madison participants is September 2026. Between now and then, the model rules and scoring may be adjusted — nothing drastic is planned, and any change will be announced in the Discussion tab. Early submissions are welcome; if a change affects your entry, you can simply resubmit.




---

## Description

### Background

A raw language model can read a task description and emit a reasonable command, but it cannot, on its own, solve a multi-step coding problem that spans dozens of shell invocations and recovers from a chain of errors. It loses track of context, repeats failed commands, hallucinates files that do not exist, and does not know when to stop. The distance between "can think about code" and "can autonomously navigate a real engineering problem" is enormous — and bridging it is the central craft of building a coding agent.

The **scaffold** (or *agent harness*) is the code wrapped around the model that keeps track of context, recovers from failed commands, decides when the task is actually done, and chains reasoning, action, and verification into something that works reliably across a hundred turns. It's what separates an LLM and a shell from an agent. There is no consensus yet on what the best architecture looks like. Prompting strategies, tool design, planning logic, retrieval, multi-stage pipelines, self-critique, fine-tuning — the design space is wide open. *How* you build the agent matters as much as which model you pick — careful engineering on a small model can beat thoughtless deployment of a large one.

### Goal

Build an autonomous coding agent, running entirely on open-weight models, that:

- **Solves real software engineering tasks end-to-end** without human intervention — reading the problem, exploring the codebase, planning, executing, and verifying the result.
- **Generalizes** across Terminal-Bench's diverse task categories rather than memorizing solutions to individual tasks.
- **Runs efficiently** — modest memory footprint, lean token consumption — without sacrificing capability. Everything you serve fits in [96 GB of VRAM](#compute-budget). Inside that ceiling, choosing the right model is part of the challenge; the ceiling is what stops it from becoming a contest over who rented the biggest cluster.
- **Beats the leaderboard** — scored by Terminal-Bench performance minus a small token penalty, on open weights within the budget (see [Evaluation](#evaluation)).

### Terminal-Bench

[Terminal-Bench 2.1](https://tbench.ai) is the benchmark we score against — an open, industry-standard collection of 89 tasks spanning software engineering, security, data processing, system administration, and scientific computing. Each task ships as a Docker image with a starting environment, a natural-language instruction, and a hidden test suite that grades the container's final state. All 89 tasks are public and can be browsed at [tbench.ai](https://www.tbench.ai/).

> **2.1, not 2.0.** Terminal-Bench 2.1 keeps the same 89 tasks but fixes 26 of them — bugs, timeouts and resource limits, and hardening against reward hacking. Scores are therefore *not* directly comparable across the two: if you have numbers from a 2.0 run, re-run on 2.1 before you submit. The Harbor dataset id is `terminal-bench/terminal-bench-2-1`.

Your agent receives the instruction and is given shell access to the running container. It inspects the codebase the way a developer would — `ls`, `cat`, `grep`, `find`, `git log`, `pytest`, anything it wants to run — edits files by writing to disk, executes builds and tests, observes the output, and decides what to do next. There is no special tooling; the agent succeeds by knowing what commands to issue and how to interpret what comes back.

**Where the agent code lives.** The decision logic — what to prompt the model with, how to parse its response into a shell command, when to stop — is your code. You write a Python class implementing the `BaseAgent` interface from [Harbor](https://www.harborframework.com/), the open-source evaluation framework for Terminal-Bench 2.1. Harbor invokes your class's `run(instruction, environment)` method when a task starts; your code prompts the model with the instruction (plus a system prompt and the running conversation), parses the response into a bash command, runs it via `environment.exec()`, observes the output, decides the next step, and returns when the task is done. The baseline in [`starter/agent/agent.py`](https://github.com/qualiaMachine/MLM26_EfficientCoder/blob/main/starter/agent/agent.py) is a ~60-line ReAct loop you can fork. Pointing Harbor at your agent is a single CLI flag — `--agent-import-path agent.agent:YourAgentClass`. See [Starter materials](#starter-materials) below to get going.

### Example tasks

Three representative tasks from Terminal-Bench, varying in difficulty:

- **fix-git** (easy, software-engineering) — The container holds a small git repo in which a recent `git reset --hard` orphaned several commits of feature work. The branch *looks* clean, but the work is gone from `main`. The agent has to recognize that something was lost, use `git reflog` to locate the orphaned commits, recover them, merge them back into `main` cleanly, and resolve any conflicts that appear. Tests whether the agent can read git's terminal output, recognize a non-obvious failure state, and recall less-common git subcommands.

- **build-cython-ext** (medium, debugging) — A Cython extension that no longer compiles because the project's NumPy version moved forward and the underlying C API changed. The agent has to read the compiler error, trace it to the deprecated NumPy symbols in the `.pyx` source, patch either the source or the build configuration, and produce a working compiled extension that the test suite can import. Tests cross-language debugging, build-toolchain reasoning, and the discipline to re-run after each fix instead of guessing twice.

- **configure-git-webserver** (hard, system-administration) — A bare Linux container that needs to be turned into a self-deploying web server: when commits land in a designated local git repo, the served site should update automatically. The agent has to choose a server (nginx, lighttpd, caddy — its call), wire up a `post-receive` hook or equivalent, ensure the service starts on boot, and prove the end-to-end loop with a test commit. Tests multi-component system design and the kind of "no single right answer" judgment that fewer benchmarks capture.

Browse all 89 tasks with filters at [tbench.ai](https://www.tbench.ai/).

---

## Starter materials

The [challenge repo](https://github.com/qualiaMachine/MLM26_EfficientCoder) has everything you need to get a first scored run working:

- [`starter/`](https://github.com/qualiaMachine/MLM26_EfficientCoder/tree/main/starter/) — a deliberately minimal [ReAct](https://arxiv.org/abs/2210.03629) baseline agent (~200 lines) wired into Harbor, meant to be forked and rebuilt: the model *reasons* about the next step, *acts* by emitting a shell command, observes the output, and repeats until it decides the task is done. Architecture, prompting strategy, retrieval, tool design, and planning logic are all up to you.
- [`starter/docs/walkthrough.md`](https://github.com/qualiaMachine/MLM26_EfficientCoder/blob/main/starter/docs/walkthrough.md) — an end-to-end walkthrough (fresh machine → first Terminal-Bench score); the surrounding [`starter/docs/`](https://github.com/qualiaMachine/MLM26_EfficientCoder/tree/main/starter/docs/) folder covers model endpoint setup and troubleshooting.
- [`RESOURCES.md`](https://github.com/qualiaMachine/MLM26_EfficientCoder/blob/main/RESOURCES.md) — where to run the benchmark and where to serve a model, with or without your own GPU.

---

## Compute budget

Two rules govern your submitted run: **open weights**, and **everything you serve fits in 96 GB**.

**1. Open weights.** Every model in your system is a publicly downloadable checkpoint (HuggingFace or equivalent) under a license that permits use here, served on an endpoint that names the exact `(model, quantization)` it runs. Closed-weight models (GPT, Claude, Gemini) are out of scope anywhere in the system, including "just the planner."

**2. A 96 GB memory budget.** The total *reported VRAM* of every model your submitted run serves is **≤ 96 GB**, and the GPU(s) you run on total ≤ 96 GB. This is a **system budget, not a per-model one** — a small planner alongside a large coder spends the sum of both.

96 GB is one serious GPU: an RTX PRO 6000 Blackwell, a pair of 48 GB cards, or the equivalent rented by the hour. Inside that ceiling both levers are yours — which checkpoint gets the most out of 96 GB, and the scaffold you wrap around it. One large dense model, a bigger MoE with few active params, or a small fast model with the headroom spent on longer context or a second model are all live strategies. The writeup should explain both choices.

Development is unrestricted — prototype against any model or endpoint you like, closed ones included. The rules above govern the *submitted* run only.

### Checking that your model fits

[`starter/scripts/estimate_vram.py`](https://github.com/qualiaMachine/MLM26_EfficientCoder/blob/main/starter/scripts/estimate_vram.py) computes reported VRAM from public information — no GPU and no downloads, just two small JSON requests per model. Pass every model your system serves; it sums them and checks the budget:

```bash
python starter/scripts/estimate_vram.py Qwen/Qwen3.6-27B-FP8
python starter/scripts/estimate_vram.py Qwen/Qwen2.5-Coder-7B-Instruct-AWQ Qwen/Qwen2.5-Coder-32B-Instruct-AWQ   # planner + coder
```

Put its `reported_vram` total on your submission card. If your checkpoint isn't on the Hub (a local GGUF, your own fine-tune), report weights-on-disk + KV + 2 GB by the formula below and say so in the writeup.

### How "reported VRAM" is computed

Reported VRAM is **weights + KV cache for a 16k context window + small overhead**, at single-batch concurrency. It's an accounting convention for comparing models, not a measurement — peak VRAM varies with batch size, context length, and serving stack.

```
Reported VRAM (GB) ≈ published checkpoint size                               # weights
                   + (n_layers × n_kv_heads × head_dim × 2 × 16384 × 2) / 1e9   # KV @ 16k, fp16
                   + ~2 GB headroom (activations, runner overhead)
```

For **MoE models**, the full checkpoint loads into VRAM — active params reduce compute, not memory. Serving a longer context than 16k is fine and doesn't change the accounting, but your hardware still has to be ≤ 96 GB of VRAM in total.

### Quantization floor

Quantization is your call, with one limit: **weights at 4-bit or higher** (bf16, FP8, MXFP4, AWQ, GPTQ-Int4, GGUF Q4_K_M and friends). Sub-4-bit weights (2- and 3-bit) aren't eligible — they degrade unpredictably and would turn the budget into a race to cram the largest possible parameter count into 96 GB.

Use a published checkpoint where one exists. If you quantize a model yourself, publish the resulting checkpoint or the exact recipe, so the run can be reproduced. Name the quantization on your submission card either way.

### Where to start

Reasonable first models by hardware tier. The budget goes well past the largest of them.

| Your hardware | A reasonable starting point |
|---|---|
| 8–12 GB | `Qwen/Qwen2.5-Coder-7B-Instruct-AWQ` (9 GB) — runs almost anywhere, low score ceiling |
| 16 GB | `Qwen/Qwen2.5-Coder-14B-Instruct-AWQ` (15 GB) |
| 24 GB | `qwen3-coder:30b` (Ollama GGUF Q4_K_M, 22 GB) — MoE, ~3B active, fast |
| 32–40 GB | `Qwen/Qwen2.5-Coder-32B-Instruct-AWQ` (28 GB) — the most widely hosted, easiest no-GPU path · `Qwen/Qwen3-Coder-30B-A3B-Instruct-FP8` (35 GB) |
| 48 GB | `Qwen/Qwen3.6-27B-FP8` (37 GB) — reasoning model with coder tool-calling; UW–Madison participants have a hosted endpoint in [`starter/docs/uw_madison_endpoint.md`](https://github.com/qualiaMachine/MLM26_EfficientCoder/blob/main/starter/docs/uw_madison_endpoint.md) |
| 96 GB | The frontier open-weight coders — large MoEs at FP8, or 70B+ dense at 4-bit. Run the estimator on whatever shipped this month. |

Post what works in the **Kaggle Discussion tab** with the estimator output — it saves the rest of the cohort the search.

### Considerations

**What's not eligible:**
- **Closed-weight models** (GPT, Claude, Gemini) anywhere in your system, including "just the planner."
- **Any endpoint that won't tell you what it's serving.** If a provider doesn't disclose the exact `(model, quantization)` behind their API, you can't show your run fits the budget. Fine for prototyping; your submitted run needs a named checkpoint.
- **Anything over the budget**, including a system whose individual models each fit but whose total doesn't.

**Evaluation constraints:**
- **No human-in-the-loop at evaluation time.** Terminal-Bench scoring is fully deterministic — pytest passes or fails, no LLM judges, no subjective grading.
- **No hard turn cap.** Set whatever per-task turn / wall-clock limit suits your dev loop. The token penalty (0.01 per million) already charges verbose agents, so no cap is needed.

**Generalizability.** One system prompt, one agent loop, no per-task `if task == "fix-git"` branching. Detecting task *categories* (e.g., "this looks like a debugging task") and adjusting strategy is fine — that's good engineering. Hardcoding solutions or prompts for individual tasks is not. After the deadline, organizers re-run the top 5 submissions and review the code; task-specific hardcoding disqualifies.


---

## Submission Requirements

Submissions are **Kaggle Writeups** — there is no file upload. Create one with the "New Writeup" button on the competition page; after you save, a "Submit" button appears in the top right corner. **Your final Writeup must be submitted before the deadline — draft or un-submitted Writeups are not considered.** You can edit and resubmit as your agent improves; the submitted version at the deadline is what counts, and the top 5 get re-run and code-reviewed after the deadline.

During the competition, also share early and often via the Kaggle Discussion tab: post progress, share your repo, describe what's working and what isn't. Think of Discussion as an open lab notebook for the cohort.

### The Writeup (project report)

Title, subtitle, cover image, and your report, **≤2,500 words**. (Kaggle requires the cover image to submit — a screenshot of your `harbor view jobs` results table or a diagram of your scaffold both work.) [`WRITEUP_TEMPLATE.md`](https://github.com/qualiaMachine/MLM26_EfficientCoder/blob/main/WRITEUP_TEMPLATE.md) is a suggested structure if you want guidance — otherwise organize it however you like and fill it with whatever insights you learned. The one expectation: explain your learning journey — what you tried, what worked, what didn't, and where you ended up.

Open the report with your **submission card** — copy this block and fill in your values. Evaluation is always against all 89 Terminal-Bench tasks (single attempt each) — you don't declare that separately.

```
code_url: https://github.com/team/agent/tree/v1.0-submission
model: Qwen/Qwen2.5-Coder-32B-Instruct-AWQ
quantization: AWQ 4-bit
reported_vram: 28 GB
tb_score: 0.42
total_tokens: 1263800
leaderboard_score: 0.407
gpu: RTX A6000 48 GB
mean_wallclock_per_task: 3m 12s
```

- `code_url` — your public repo at the exact tag or commit SHA you ran (see below)
- `model` and `quantization` — the exact checkpoint(s) your run served, open weights, 4-bit or higher. List every model if you use more than one.
- `reported_vram` — total from `estimate_vram.py` across all models served; must be ≤ 96 GB
- `tb_score` — mean reward across all 89 tasks, 0–1
- `total_tokens` — `n_input_tokens + n_output_tokens` summed from Harbor's `result.json`
- `leaderboard_score` — `tb_score − 0.01 × (total_tokens / 1,000,000)`
- `gpu` — the hardware you served on; total VRAM must be ≤ 96 GB
- `mean_wallclock_per_task` — informational, not scored

**Getting your `code_url`.** It pins the exact version of your code you ran, so organizers can reconstruct it with `git clone` + `git checkout`. Commit and push everything, then either:

```bash
git rev-parse HEAD                                        # prints the commit SHA
# or, friendlier: tag the submission and use the tag name
git tag v1.0-submission && git push origin v1.0-submission
```

Your `code_url` is `https://github.com/<you>/<repo>/tree/<tag-or-SHA>`. Before submitting, open it in a private/incognito browser window — if the page loads, anyone can fetch exactly the code you ran (that's the point of the `/tree/` form: the link doubles as its own check). If it 404s, your repo is private or the commit isn't pushed.

---

## Tracks and Awards

**Open track** — the only track; select it when submitting your Writeup. All submissions compete together, ranked by leaderboard score (see [Evaluation](#evaluation)).

There are no cash or material awards — this is a non-monetary educational challenge (Kaggle Kudos only). Top teams may be invited to present at the ML+X showcase or contribute to open-source outputs.

---

## Evaluation

### Scoring

Your submitted run must use open weights within the [96 GB budget](#compute-budget) — any checkpoint, any vendor, 4-bit or higher. The shared budget plus the token penalty is what keeps the comparison honest: everyone works under the same memory ceiling, and the ranking rewards whoever gets the most out of it — through model choice, through the scaffold, and through not wasting tokens.

**Score.**

```
leaderboard_score = TB_score − 0.01 × (total_tokens / 1,000,000)
```

Where:
- **`TB_score`** is your mean Terminal-Bench reward across all 89 tasks (single attempt per task, `--n-attempts 1`) — a value between 0 and 1.
- **`total_tokens`** is the sum of `n_input_tokens + n_output_tokens` across all 89 tasks, taken straight from Harbor's per-task `result.json`.

**Every million tokens costs one point** (0.01) of Terminal-Bench score. A typical run spends 1–3M tokens, so the penalty lands around 0.01–0.03 — enough to decide races between agents of similar capability, never enough to beat a real capability gap. Worked example: TB 0.42 with 1.26M tokens scores `0.42 − 0.0126 = 0.407`; the same agent rerun with a verbose loop at 2.5M tokens drops to `0.395`.

### Computing your submission numbers

After running `harbor run -d terminal-bench/terminal-bench-2-1 --agent-import-path agent.agent:BaselineAgent`, Harbor writes one `result.json` per task trial under `jobs/<job-id>/<task>__<trial-id>/result.json` (plus a job-level summary at `jobs/<job-id>/result.json`). Extract the three numbers you need with the commands below (they use [`jq`](https://jqlang.org) — install it first with `sudo apt install jq` on Ubuntu/WSL2 or `brew install jq` on macOS):

```bash
JOB=jobs/<your-job-id>

# Terminal-Bench score (mean reward across trials; -mindepth 2 skips the job-level summary)
find "$JOB" -mindepth 2 -name result.json | xargs jq -s '
  [.[] | .verifier_result.rewards.reward // 0] | add / length
'

# Total tokens (input + output, summed across all 89 tasks)
find "$JOB" -mindepth 2 -name result.json | xargs jq -s '
  [.[] | (.agent_result.n_input_tokens // 0) + (.agent_result.n_output_tokens // 0)] | add
'

# Tasks evaluated (sanity check: should be 89)
find "$JOB" -mindepth 2 -name result.json | wc -l
```

These three numbers, plus your model and its reported VRAM, are what go on the submission card in your Writeup (see [Submission Requirements](#submission-requirements) above).

### Verification of top submissions

Leaderboard scores are **self-reported** — your score comes from numbers you report in your Writeup's submission card, so it is possible to lie. Two things keep the leaderboard a reflection of reality: organizers **spot-check submissions periodically during the competition** (fabricated entries are removed when found), and the **top 5 are fully verified before final standings are confirmed**. Every submission carries its own evidence — a public repo, an exact commit, and a writeup. For each verified submission, we:

1. **Re-run the agent.** Clone the repo at the submitted commit, run it against all 89 tasks with the declared model, and check the score matches the reported one. Declaring an unusual model is fine — tell us in the writeup how you served it, and expect us to serve it the same way. LLM sampling is stochastic, so normal run-to-run variation is expected and fine.
2. **Check the numbers.** Confirm the reported token count matches, and that the agent is actually calling the model claimed in the submission.
3. **Read the code.** Look for hardcoded solutions or prompts written for individual tasks — all 89 tasks are public, so cheating is possible and this is how it's caught. Confirm the declared checkpoints are open-weight and re-derive their reported VRAM against the 96 GB budget.

Significant discrepancies, hardcoding, running a different model than declared, exceeding the memory budget, or a missing writeup disqualify the submission. Beyond those pass/fail checks, nothing is judged — the writeup isn't graded, and the leaderboard score is the ranking.

### Evaluation rubric

Ranking is by **leaderboard score**, computed from the submission card in your Writeup. There is no subjective scoring — the rubric points are your measured score, verified as described above.

**Agent performance (100 points)**

| Criteria | Points possible |
|---|---|
| Leaderboard score × 100, where `leaderboard_score = tb_score − 0.01 × (total_tokens / 1,000,000)` | 0–100 |

**Required elements (all must pass; any "No" makes the submission ineligible)**

| Requirement | Pass/Fail |
|---|---|
| Submission card at the top of the Writeup, fully filled out | Yes/No |
| Open weights only, total reported VRAM ≤ 96 GB, weights 4-bit or higher | Yes/No |
| Agent runs via `harbor run --agent` without modification | Yes/No |
| No closed-weight or opaque-provider API calls anywhere in the system | Yes/No |
| All 89 Terminal-Bench tasks evaluated, single attempt each | Yes/No |
| Public GitHub repo at a tagged commit, licensed MIT or Apache 2.0, listed in the submission card | Yes/No |
| Writeup ≤2,500 words explaining your approach and learning journey | Yes/No |

Ties go to the earlier submission (Kaggle standard).

---

## Judges

Chris Endemann (endemann@wisc.edu) and Kevin Chovanec, UW–Madison. Judging is verification against the [Evaluation rubric](#evaluation-rubric), not subjective scoring.

Hosted by [ML+X](https://hub.datascience.wisc.edu/communities/mlx/) at the University of Wisconsin–Madison. Sponsor info: https://hub.datascience.wisc.edu/communities/mlx/sponsorship/

---

## Citation

```
Christopher Endemann. Badger Code.
https://kaggle.com/competitions/OpenAgent-Coding, 2026. Kaggle.
```
