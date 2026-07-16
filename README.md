# Efficient Coder

Build the best open coding agent on a single GPU — no proprietary models, no giant clusters, scored on Terminal-Bench 2.0. Hosted by [ML+X](https://hub.datascience.wisc.edu/communities/mlx/) at UW–Madison, September–December 2026. Open to everyone.




---

## Overview

The last two years have transformed how software gets built. Frontier coding agents — Claude Code, Cursor, Codex, Devin — can now read a codebase, plan changes across many files, run tests, and recover from errors well enough to feel like real (if junior) collaborators. They are remarkable, but they are also closed and expensive: every keystroke flows to a third party, costs accumulate per task, and anyone working with sensitive data has to be careful nothing leaks.

Open-weight models have closed enough of the raw-quality gap that a credible coding agent can now plausibly run locally. *Plausibly*, but not yet *well*. The challenge is intended as a collaborative effort to help narrow the remaining gap. You will build an autonomous coding agent on top of an approved open-weight model and measure it on [Terminal-Bench 2.0](https://tbench.ai), an industry-standard 89-task benchmark used to evaluate Claude Code, Cursor, and friends. Every submission runs on one of a handful of approved models in the 7–37 GB class, so the leverage is in the scaffold or "agent harness": a 14B model wrapped in a thoughtful agent loop can credibly beat a 32B with a naive one. The goal is not to build the largest agent, but the most *useful* one under realistic constraints.

This is an **educational, collaborative challenge**. There are no cash prizes, no rankings-based awards, and no reason to hoard ideas. Share repos early, post findings to the Discussion tab, fork and build on each other's approaches. Credit what you borrowed in your writeup and explain what you added. Every improvement one team publishes raises the floor for everyone else — and every step forward here pushes the open-source community closer to genuine independence from closed frontier tools when it comes to agentic coding.

**Soft launch.** The competition is open for submissions now; the official kickoff for UW–Madison participants is September 2026. Between now and then, the approved model list and rules may be adjusted — nothing drastic is planned, and any change will be announced in the Discussion tab. Early submissions are welcome; if a change affects your entry, you can simply resubmit.




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

### Terminal-Bench

[Terminal-Bench 2.0](https://tbench.ai) is the benchmark we score against — an open, industry-standard collection of 89 tasks spanning software engineering, security, data processing, system administration, and scientific computing. Each task ships as a Docker image with a starting environment, a natural-language instruction, and a hidden test suite that grades the container's final state. All 89 tasks are public and can be browsed at [tbench.ai](https://www.tbench.ai/).

Your agent receives the instruction and is given shell access to the running container. It inspects the codebase the way a developer would — `ls`, `cat`, `grep`, `find`, `git log`, `pytest`, anything it wants to run — edits files by writing to disk, executes builds and tests, observes the output, and decides what to do next. There is no special tooling; the agent succeeds by knowing what commands to issue and how to interpret what comes back.

**Where the agent code lives.** The decision logic — what to prompt the model with, how to parse its response into a shell command, when to stop — is your code. You write a Python class implementing the `BaseAgent` interface from [Harbor](https://www.harborframework.com/), the open-source evaluation framework for Terminal-Bench 2.0. Harbor invokes your class's `run(instruction, environment)` method when a task starts; your code prompts the model with the instruction (plus a system prompt and the running conversation), parses the response into a bash command, runs it via `environment.exec()`, observes the output, decides the next step, and returns when the task is done. The baseline in [`starter/agent/agent.py`](https://github.com/qualiaMachine/MLM26_EfficientCoder/blob/main/starter/agent/agent.py) is a ~60-line ReAct loop you can fork. Pointing Harbor at your agent is a single CLI flag — `--agent agent.agent:YourAgentClass`. See [Starter materials](#starter-materials) below to get going.

### Example tasks

Three representative tasks from Terminal-Bench, varying in difficulty:

- **fix-git** (easy, software-engineering) — The container holds a small git repo in which a recent `git reset --hard` orphaned several commits of feature work. The branch *looks* clean, but the work is gone from `main`. The agent has to recognize that something was lost, use `git reflog` to locate the orphaned commits, recover them, merge them back into `main` cleanly, and resolve any conflicts that appear. Tests whether the agent can read git's terminal output, recognize a non-obvious failure state, and recall less-common git subcommands.

- **build-cython-ext** (medium, debugging) — A Cython extension that no longer compiles because the project's NumPy version moved forward and the underlying C API changed. The agent has to read the compiler error, trace it to the deprecated NumPy symbols in the `.pyx` source, patch either the source or the build configuration, and produce a working compiled extension that the test suite can import. Tests cross-language debugging, build-toolchain reasoning, and the discipline to re-run after each fix instead of guessing twice.

- **configure-webserver** (hard, system-administration) — A bare Linux container that needs to be turned into a self-deploying web server: when commits land in a designated local git repo, the served site should update automatically. The agent has to choose a server (nginx, lighttpd, caddy — its call), wire up a `post-receive` hook or equivalent, ensure the service starts on boot, and prove the end-to-end loop with a test commit. Tests multi-component system design and the kind of "no single right answer" judgment that fewer benchmarks capture.

Browse all 89 tasks with filters at [tbench.ai](https://www.tbench.ai/).

---

## Starter materials

The [challenge repo](https://github.com/qualiaMachine/MLM26_EfficientCoder) has everything you need to get a first scored run working:

- [`starter/`](https://github.com/qualiaMachine/MLM26_EfficientCoder/tree/main/starter/) — a deliberately minimal [ReAct](https://arxiv.org/abs/2210.03629) baseline agent (~200 lines) wired into Harbor, meant to be forked and rebuilt: the model *reasons* about the next step, *acts* by emitting a shell command, observes the output, and repeats until it decides the task is done. Architecture, prompting strategy, retrieval, tool design, and planning logic are all up to you.
- [`starter/docs/walkthrough.md`](https://github.com/qualiaMachine/MLM26_EfficientCoder/blob/main/starter/docs/walkthrough.md) — an end-to-end walkthrough (fresh machine → first Terminal-Bench score); the surrounding [`starter/docs/`](https://github.com/qualiaMachine/MLM26_EfficientCoder/tree/main/starter/docs/) folder covers model endpoint setup and troubleshooting.
- [`RESOURCES.md`](https://github.com/qualiaMachine/MLM26_EfficientCoder/blob/main/RESOURCES.md) — where to run the benchmark and where to serve a model, with or without your own GPU.

---

## Approved models

Submissions must use one of the models below. The list is deliberately short so the competition is about how you build the scaffold, not which model you found. Scoring is Terminal-Bench score minus a small token penalty — see the Evaluation section below.

Development is unrestricted — prototype against any open-weight model or endpoint you like. The approved list governs the *submitted* run only.

**Pick by your GPU:** 8–12 GB → 7B AWQ · 16 GB → 14B AWQ · 24 GB → `qwen3-coder:30b` GGUF · 32–40 GB → 32B AWQ or 30B FP8 · 48 GB+ → the anchor.

| Model | FP8 | AWQ / 4-bit | Notes |
|---|---|---|---|
| Qwen3.6-27B | `Qwen/Qwen3.6-27B-FP8` (37 GB) | — none published | **Anchor.** Newest and strongest of the group; reasoning model with coder tool-calling. Self-host on a 48 GB card, or UW–Madison participants can use the hosted endpoint in [`starter/docs/uw_madison_endpoint.md`](https://github.com/qualiaMachine/MLM26_EfficientCoder/blob/main/starter/docs/uw_madison_endpoint.md). |
| Qwen3-Coder-30B-A3B | `Qwen/Qwen3-Coder-30B-A3B-Instruct-FP8` (35 GB) | `qwen3-coder:30b`, Ollama GGUF Q4_K_M (22 GB) — no official 4-bit safetensors exists | MoE: 30B total, ~3B active — fast. The GGUF runs on 24 GB cards, workable on 16 GB via expert offload. Bedrock's managed `qwen.qwen3-coder-30b-a3b-v1:0` counts as the FP8 column. |
| Qwen2.5-Coder-32B | — | `Qwen/Qwen2.5-Coder-32B-Instruct-AWQ` (28 GB) | A generation older but the most widely hosted (Together, Fireworks, NVIDIA API catalog) — easiest no-GPU path. |
| Qwen2.5-Coder-14B | — | `Qwen/Qwen2.5-Coder-14B-Instruct-AWQ` (15 GB) | Small-GPU tier (16 GB+ cards). |
| Qwen2.5-Coder-7B | — | `Qwen/Qwen2.5-Coder-7B-Instruct-AWQ` (9 GB) | Smallest approved; runs almost anywhere, expect a lower score ceiling. |

**Equivalent quantizations count as the same entry.** GGUF/Q4_K_M (Ollama) and GPTQ-Int4 checkpoints of a listed model map to its AWQ / 4-bit column; they're within ~10% of each other. Ollama's `qwen2.5-coder:7b/14b/32b` tags are the corresponding AWQ entries.

### How "reported VRAM" is computed

Each checkpoint's reported VRAM is **weights + KV cache for a 16k context window + small overhead**, at single-batch concurrency. It's there to tell you what hardware a model needs — approximate by design, since peak VRAM varies with batch size, context length, and serving stack.

```
Reported VRAM (GB) ≈ published checkpoint size                               # weights
                   + (n_layers × n_kv_heads × head_dim × 2 × 16384 × 2) / 1e9   # KV @ 16k, fp16
                   + ~2 GB headroom (activations, runner overhead)
```

For **MoE models**, the full checkpoint loads into VRAM — active params reduce compute, not memory.

### Requesting an addition

The list is meant to stay short, but it isn't frozen. If a model materially changes what's possible for participants (a new open-weight coder release, a hardware tier the list doesn't serve), post in the **Kaggle Discussion tab** with the HuggingFace id, the quantization, and the case for adding it. Additions should land at or under ~48 GB reported VRAM — a single serious GPU. Organizers respond within a day or two; once listed, the model is available to every team.

### Considerations

**Models.** Your submitted run must use one of the approved models above.

**What's not eligible:**
- **Closed-weight models** (GPT, Claude, Gemini) anywhere in your system, including "just the planner."
- **Any endpoint that won't tell you what it's serving.** If a provider doesn't disclose the exact `(model, quantization)` behind their API, you can't pin your submission to an approved checkpoint. Fine for prototyping, but your submitted run needs to use a listed model on an endpoint that names it.

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

Open the report with your **submission card** — copy this table and fill in your values. Evaluation is always against all 89 Terminal-Bench tasks (single attempt each) — you don't declare that separately.

| Field | Your entry (example) |
|---|---|
| `code_url` | `https://github.com/team/agent/tree/v1.0-submission` — your public repo at the exact tag or commit SHA you ran |
| `model` | `Qwen/Qwen2.5-Coder-32B-Instruct-AWQ` — must match an approved checkpoint |
| `quantization` | `AWQ 4-bit` — `FP8`, `AWQ 4-bit`, or `GGUF Q4_K_M`, matching the approved entry |
| `tb_score` | `0.42` — mean reward across all 89 tasks, 0–1 |
| `total_tokens` | `1263800` — `n_input_tokens + n_output_tokens` summed from Harbor's `result.json` |
| `leaderboard_score` | `0.407` — `tb_score − 0.01 × (total_tokens / 1,000,000)` |
| `gpu` | `RTX A6000 48 GB` — informational, not scored |
| `mean_wallclock_per_task` | `3m 12s` — informational, not scored |

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

Your submitted run must use one of the `(model, quantization)` checkpoints in the approved model table above. Equivalent quantizations of a listed model (GGUF/Q4_K_M, GPTQ-Int4) count as its AWQ / 4-bit entry. The approved-model list plus the token penalty is what makes this a scaffold-engineering challenge: everyone picks from the same small pool of models, and the ranking rewards whoever gets the most out of it.

**Score.**

```
leaderboard_score = TB_score − 0.01 × (total_tokens / 1,000,000)
```

Where:
- **`TB_score`** is your mean Terminal-Bench reward across all 89 tasks (single attempt per task, `--n-attempts 1`) — a value between 0 and 1.
- **`total_tokens`** is the sum of `n_input_tokens + n_output_tokens` across all 89 tasks, taken straight from Harbor's per-task `result.json`.

**Every million tokens costs one point** (0.01) of Terminal-Bench score. A typical run spends 1–3M tokens, so the penalty lands around 0.01–0.03 — enough to decide races between agents of similar capability, never enough to beat a real capability gap. Worked example: TB 0.42 with 1.26M tokens scores `0.42 − 0.0126 = 0.407`; the same agent rerun with a verbose loop at 2.5M tokens drops to `0.395`.

### Computing your submission numbers

After running `harbor run -d terminal-bench@2.0 --agent agent.agent:BaselineAgent`, Harbor writes one `result.json` per task trial under `jobs/<job-id>/<task>__<trial-id>/result.json` (plus a job-level summary at `jobs/<job-id>/result.json`). Extract the three numbers you need with the commands below (they use [`jq`](https://jqlang.org) — install it first with `sudo apt install jq` on Ubuntu/WSL2 or `brew install jq` on macOS):

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

These three numbers, plus your approved model entry, are what go on the submission card in your Writeup (see [Submission Requirements](#submission-requirements) above).

### Verification of top submissions

Leaderboard scores are **self-reported** — your score comes from numbers you report in your Writeup's submission card, so it is possible to lie. Two things keep the leaderboard a reflection of reality: organizers **spot-check submissions periodically during the competition** (fabricated entries are removed when found), and the **top 5 are fully verified before final standings are confirmed**. Every submission carries its own evidence — a public repo, an exact commit, and a writeup. For each verified submission, we:

1. **Re-run the agent.** Clone the repo at the submitted commit, run it against all 89 tasks with the declared model, and check the score matches the reported one. LLM sampling is stochastic, so normal run-to-run variation is expected and fine.
2. **Check the numbers.** Confirm the reported token count matches, and that the agent is actually calling the model claimed in the submission.
3. **Read the code.** Look for hardcoded solutions or prompts written for individual tasks — all 89 tasks are public, so cheating is possible and this is how it's caught.

Significant discrepancies, hardcoding, running a different model than declared, or a missing writeup disqualify the submission. Beyond those pass/fail checks, nothing is judged — the writeup isn't graded, and the leaderboard score is the ranking.

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
| Model + quantization on the approved model list | Yes/No |
| Agent runs via `harbor run --agent` without modification | Yes/No |
| Open weights only (no closed-weight or opaque-provider API calls) | Yes/No |
| All 89 Terminal-Bench tasks evaluated, single attempt each | Yes/No |
| Public GitHub repo at a tagged commit, licensed MIT or Apache 2.0, listed in the submission card | Yes/No |
| Writeup ≤2,500 words explaining your approach and learning journey | Yes/No |

Ties go to the earlier submission (Kaggle standard).

---

## Judges

Chris Endemann (endemann@wisc.edu), UW–Madison — organizer and judge. Judging is verification against the [Evaluation rubric](#evaluation-rubric), not subjective scoring.

Hosted by [ML+X](https://hub.datascience.wisc.edu/communities/mlx/) at the University of Wisconsin–Madison. Sponsor info: https://hub.datascience.wisc.edu/communities/mlx/sponsorship/

---

## Citation

```
Christopher Endemann. Efficient Coder.
https://kaggle.com/competitions/efficient-coder, Unpublished. Kaggle.
```
