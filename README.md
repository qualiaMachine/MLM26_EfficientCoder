# MLM26: Local Coding Agent Challenge

Build the best local coding agent — measured on Terminal-Bench 2.0. Hosted by [ML+X](https://mlx.wisc.edu/) at UW–Madison, September–December 2026. Open to everyone.

**Start:** September 2026 · **Close:** December 2026

---

## Overview

Build a coding agent that runs entirely on open-weight models inside a single GPU (≤48 GB VRAM) and measure it on [Terminal-Bench 2.0](https://tbench.ai) — the same benchmark used to evaluate Claude Code, Codex, Devin, and Cursor.

The model is only half the story. A raw LLM can't reliably solve multi-step coding tasks on its own — it loses track of context, repeats failed commands, hallucinates file contents, and doesn't know when to stop. The real challenge is the **orchestration code around the model**: How do you manage a conversation that spans dozens of turns without blowing the context window? How do you detect when the agent is stuck in a loop? How do you chain reasoning, action, and verification into a pipeline that produces reliable results — every time?

This is a **collaborative challenge, not a prize competition.** There are no cash prizes and no reason to hoard ideas. Share repos early, post findings to the Discussion tab, fork and build on each other's approaches. Credit borrowed ideas in your writeup; explain what you added.

**UW–Madison participants** get weekly sprints, office hours, and RunAI GPU access. Everyone else is welcome to participate remotely — the starter code, Terminal-Bench, and submission pipeline are fully open.

---

## Schedule

| Date | Milestone |
|---|---|
| September 2026 | Kickoff |
| December 2026 | Final submission |

UW participants: weekly sprints Wednesdays 4:30–6:30 pm CT (hybrid).

---

## Description

### Background

Frontier coding assistants like Claude Code, Cursor, and Codex are excellent — but they send your code to a third party, cost real money per task, and raise security concerns when data can't leave your environment. A growing class of users — researchers with sensitive data, organizations on tight budgets — needs coding agents that run locally. Open-weight models have closed enough of the gap that this is plausible. Your job: make it actually good.

### Goal

Build an autonomous coding agent that:
- Receives a task description (e.g., "find the lost git changes and merge them into master")
- Reads, explores, plans, and executes bash commands inside a Docker container
- Gets graded on the container's final state by an automated test suite
- Runs on open-weight models only, within the hardware budget

The orchestration code around the model is where the challenge lives — prompt engineering, tool design, planning, retrieval, context management, error recovery, self-verification, multi-stage pipelines, fine-tuning. The model gives you a reasoning engine. Everything you build around it is the part that decides whether the agent actually works.

### What's provided

- **Starter code** in [`starter/`](starter/) — a minimal ReAct-style baseline agent (~200 lines) wired into Harbor. Yours to modify and extend.
- **[Terminal-Bench 2.0](https://tbench.ai)** — 89 public tasks across software engineering, security, data processing, system administration, scientific computing, and more. Each task ships as a Docker image with source code, instructions, and a test suite.
- **[Harbor](https://www.harborframework.com/)** — the official Terminal-Bench 2.0 harness. Pulls task definitions, spins up containers, runs your agent, grades results, tears everything down.
- **Setup docs** under [`starter/docs/`](starter/docs/) — Docker, model endpoints, walkthrough, troubleshooting, safety.
- **RunAI-hosted model endpoints** for UW participants on request.

All 89 Terminal-Bench tasks are public — the challenge is building an agent that *generalizes*, not memorizing solutions.

### Example tasks

Terminal-Bench tasks span easy → hard across categories. A few representative examples:

- **fix-git** (easy, software-engineering) — recover lost git changes via `git reflog` and merge them into master.
- **build-cython-ext** (medium, debugging) — build a Cython extension with NumPy compatibility.
- **configure-webserver** (hard, system-administration) — configure a git-triggered webserver.

Browse all 89 with filters at [tbench.ai](https://www.tbench.ai/).

### Considerations

**Hardware (binding):**
- **Single GPU with ≤48 GB VRAM.** Sized to fit Qwen2.5-Coder-32B at 4-bit AWQ comfortably (weights + KV cache + activations). The 48 GB cap exists so anyone with a single 48 GB GPU (or a 48 GB slice of a larger card) can compete locally — including folks outside UW without cluster access.
- **No multi-GPU agents.** Tensor parallelism across two GPUs disqualifies.
- **Open weights only.** No closed-weight API calls anywhere in your system, including "just the planner."
- **Quantization allowed** (fp16, int8, int4, AWQ, GGUF) — we only care that it fits.
- Verified at finale on reference hardware (48 GB GPU, or a 48 GB slice of a larger card).

**Per-task budget:**
- ≤100 turns per task (Terminal-Bench default)
- ≤5 minutes wall-clock per task on reference hardware
- No human-in-the-loop at evaluation time

**Models — suggested default:** **Qwen2.5-Coder-32B-Instruct at 4-bit AWQ.** Fits the 48 GB budget cleanly, has a well-tested AWQ checkpoint on Hugging Face, serves cleanly under vLLM, and gives every team a strong common baseline. You are **not** required to use it — Qwen3-Coder, DeepSeek-Coder V2, GLM-4.5, Llama 3.x, or any open-weight model that fits is fair game. See [`starter/docs/byo_model.md`](starter/docs/byo_model.md) for endpoint configuration (Ollama, vLLM, hosted open-weight APIs).

**Generalizability.** One system prompt, one agent loop, no per-task `if task == "fix-git"` branching. Detecting task *categories* (e.g., "this looks like a debugging task") and adjusting strategy is fine — that's good engineering. Hardcoding solutions or prompts for individual tasks is not. Judges read your code to verify.

**Safety.** Terminal-Bench already runs each task in a fresh, throwaway Docker container with no host access. Don't undo it — don't mount your home directory, don't bake real credentials into the container, don't punch holes in the network allowlist beyond your model endpoint. Full safety guidance: [`starter/docs/safety.md`](starter/docs/safety.md).

### Contact

Chris Endemann (endemann@wisc.edu) — ML+X, UW–Madison.

Hosted by [ML+X](https://mlx.wisc.edu/) at the University of Wisconsin–Madison. Sponsor info: https://hub.datascience.wisc.edu/communities/mlx/sponsorship/

---

## Evaluation

Two-stage to scale across many submissions without drowning in manual review.

### Stage 1: Automated ranking (all submissions)

Every team submits a **submission card** with structured metadata: model used, parameter count, quantization, GPU, peak VRAM, Terminal-Bench score, and repo link. Submissions are ranked by self-reported score. No human review at this stage.

### Stage 2: Human review (top ~10)

Judges deep-review the top ~10 submissions by score:
1. Clone the repo at the tagged commit, run `harbor run` on reference hardware, verify the reported score.
2. Read the code to check for generalizability — no per-task branching or hardcoded solutions.
3. Read the writeup and score against the rubric.

Honest run-to-run variance is fine. Significant discrepancies between reported and reproduced scores disqualify. Cherry-picked or inflated numbers are not tolerated.

### Rubric (100 points, applied to finalists)

| Criteria | Points | Description |
|---|---|---|
| **Terminal-Bench score** | 25 | Raw performance. Verified by judges on reference hardware. |
| **Generalizability** | 25 | One system prompt, one agent loop. Judges read your code AND test on tasks outside your reported set. Detecting task categories is fine; hardcoding individual solutions is not. |
| **Engineering depth** | 20 | Multiple approaches tried and analyzed. Deep understanding of *why* your agent fails scores higher than a marginally better number with no insight. |
| **Reproducibility** | 15 | Clones cleanly, fits the VRAM budget, submission card accurate. |
| **Clarity & presentation** | 15 | Writeup quality. Can a reader understand what you built, why, and what you learned? |

### Required elements (pass/fail)

| Requirement | Pass/Fail |
|---|---|
| Submission card fully filled out | Yes/No |
| Agent runs via `harbor run --agent-import-path` without modification | Yes/No |
| Open-weight models only (no closed API calls) | Yes/No |
| Fits within single GPU ≤48 GB VRAM | Yes/No |
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
| Model(s) used | Qwen2.5-Coder 32B (AWQ 4-bit) |
| Total parameters | 32B |
| Quantization | AWQ int4 |
| GPU used | RTX A6000 (48 GB) |
| Peak VRAM usage | 38 GB |
| Terminal-Bench score | 0.42 (37/89 tasks passed) |
| Tasks evaluated | All 89 |
| Mean wall-clock per task | 3m 12s |

### Part 2: Full submission (attached to your Kaggle Writeup)

1. **Writeup** (≤5,000 words). Problem framing, approach, what worked, what didn't, Terminal-Bench scores, failure analysis, limitations, what you'd do with another month. Quality > length.
2. **Public notebook.** Your agent code as a public notebook. Should be runnable or clearly documented.
3. **Public GitHub repo.** Complete agent code, README with reproduction instructions, tagged release or commit hash matching your reported scores (e.g., `git tag v1.0-submission`), Terminal-Bench-compatible agent (runnable via `harbor run --agent-import-path`). License: MIT or Apache 2.0.

---

## Tracks and awards

**Track A: Local Agent (main track).** Best general-purpose local coding agent under the hardware constraints. Open to everyone.

**Track B: Analysis & Insight (optional).** For teams that want to focus on understanding rather than engineering — failure taxonomies, scaling laws, prompt sensitivity studies, model comparisons. Scored primarily on engineering depth and clarity rather than raw Terminal-Bench score.

**UW–Madison local awards.** UW participants are eligible for additional recognition based on in-person engagement. Details at kickoff.

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
No. The whole challenge is local. If part of your system calls GPT, Claude, or Gemini, it's out of scope.

**Can I fine-tune a model for this?**
Yes. Document it in the writeup. Fine-tuned weights must be either public or reproducible from the public base model + your published LoRA / adapter.

**Can I use multiple models (e.g., a small planner + a larger coder)?**
Yes, as long as the total loaded footprint fits the VRAM budget at inference time.

**Can I submit my agent to the public Terminal-Bench leaderboard?**
Yes, please. Independent of MLM. It's a real leaderboard and a real artifact.

**Do I need to use the entire Terminal-Bench task set during the semester?**
No — work with whatever subset is useful for debugging. For the finale, you don't pick — we score against a fixed held-out subset.

**My team is just me. / My team is four people.**
Both fine. Teams of 1–4. Reflect honestly on contributions in the writeup.

**I don't have a GPU.**
Start on CPU with a small model (qwen2.5-coder:3b). UW participants can request RunAI-hosted endpoints. Cloud providers (Lambda, RunPod, Vast.ai) work too. Whatever you *submit* must fit the 48 GB single-GPU budget at eval time.

**I'm not at UW.**
Welcome. The challenge is fully open. You won't have access to weekly sprints, office hours, or RunAI endpoints, but you're eligible for all main track awards.

**Will there be a live leaderboard during the semester?**
No. Run Terminal-Bench locally, track your own progress, share findings via the Discussion tab. At the deadline, everyone submits a structured submission card with their score — that's the ranking. Judges then deep-review the top ~10. You can also submit independently to the [public Terminal-Bench leaderboard](https://tbench.ai/leaderboard).

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

- [ ] Confirm finale reference hardware spec (48 GB target)
- [ ] Reach out to Terminal-Bench / Laude Institute about possible coordination (judge from their side?)
- [ ] Cold-start test the quickstart on a machine that didn't write it
- [ ] Recruit judges (Terminal-Bench contributors, agent researchers)
- [ ] Set up Discord
- [ ] Coordinate with Kaggle on Community Hackathon setup
- [ ] Final pass on safety doc with UW research-IT
- [ ] Create Google Form for final submissions
