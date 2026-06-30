# MLM26: Local Coding Agent Challenge

Build the best local coding agent — measured on Terminal-Bench 2.0. Hosted by [ML+X](https://mlx.wisc.edu/) at UW–Madison, September–December 2026. Open to everyone.

**Start:** September 2026 · **Close:** December 2026

---

## Overview

Build a coding agent on top of an open-weight model — small, large, or somewhere in between — and measure it on [Terminal-Bench 2.0](https://tbench.ai), the same benchmark used to evaluate Claude Code, Codex, Devin, and Cursor. The leaderboard rewards both raw performance *and* efficiency: a single weighted score that combines Terminal-Bench accuracy, the model's memory footprint, and the agent's token consumption per task.

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
- Runs on an open-weight model picked from the [`MODELS.md`](MODELS.md) list (or a model you've added to that list via PR)

The orchestration code around the model is where the challenge lives — prompt engineering, tool design, planning, retrieval, context management, error recovery, self-verification, multi-stage pipelines, fine-tuning. The model gives you a reasoning engine. Everything you build around it is the part that decides whether the agent actually works. The efficiency tilt in the scoring formula means a 7B or 14B model with a clever loop can credibly beat a 70B with a naive one.

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

**Models (binding).** Pick a model from [`MODELS.md`](MODELS.md). That table maps each `(model, quantization)` to a canonical *reported VRAM* used by the leaderboard formula — you don't measure VRAM yourself, you pick a row. The table spans from ~7 GB (Qwen-Coder-7B AWQ) to ~500 GB (Kimi-K2.7-Code), so no hardware floor or ceiling is implied. **Suggested anchor: `Qwen/Qwen2.5-Coder-32B-Instruct-AWQ` (28 GB).** Open a PR to add any open-weight model you want to use that isn't already listed; we merge fast.

**What's not eligible:**
- **Closed-weight models** (GPT, Claude, Gemini) anywhere in your system, including "just the planner."
- **Opaque hosted providers** (Amazon Bedrock, generic chat APIs) where you can't pin the exact `(model, quantization)` to a `MODELS.md` row. Fine for development; can't be your submission's model.
- **Multi-GPU tensor parallelism within a single forward pass.** Serving a model that maps to >48 GB on a multi-GPU machine is fine — your scored footprint is the table value, not your hardware.

**Per-task budget:**
- ≤100 turns per task (Terminal-Bench default)
- No human-in-the-loop at evaluation time

**Generalizability.** One system prompt, one agent loop, no per-task `if task == "fix-git"` branching. Detecting task *categories* (e.g., "this looks like a debugging task") and adjusting strategy is fine — that's good engineering. Hardcoding solutions or prompts for individual tasks is not. At the finale, organizers re-run top submissions on a held-out task subset; a big gap between your public-set score and your private-set score gets investigated.

**Safety.** Terminal-Bench already runs each task in a fresh, throwaway Docker container with no host access. Don't undo it — don't mount your home directory, don't bake real credentials into the container, don't punch holes in the network allowlist beyond your model endpoint. Full safety guidance: [`starter/docs/safety.md`](starter/docs/safety.md).

### Contact

Chris Endemann (endemann@wisc.edu) — ML+X, UW–Madison.

Hosted by [ML+X](https://mlx.wisc.edu/) at the University of Wisconsin–Madison. Sponsor info: https://hub.datascience.wisc.edu/communities/mlx/sponsorship/

---

## Evaluation

### Scoring

Submissions are ranked on a single weighted score:

```
leaderboard_score = TB_score / log10(reported_VRAM_GB × total_tokens)
```

Where:
- **`TB_score`** is your mean Terminal-Bench reward across all 89 tasks (single attempt per task, `--n-attempts 1`).
- **`reported_VRAM_GB`** is the canonical number for your `(model, quantization)` row in [`MODELS.md`](MODELS.md). You don't measure it; you pick a row.
- **`total_tokens`** is the sum of `n_input_tokens + n_output_tokens` across all 89 tasks, taken straight from Harbor's per-task `result.json`.

Worked example: a `Qwen2.5-Coder-32B-AWQ` submission (28 GB) that scores 0.42 on Terminal-Bench with 1,263,800 total tokens across the 89 tasks lands at `0.42 / log10(28 × 1,263,800)` = `0.42 / 7.55` = **0.056**.

The formula rewards leaner agents but raw performance still dominates: a stronger TB score with a giant model can still outrank a weaker one with a tiny model, and a smaller, terser agent can outrank a similar score from a huge MoE that burns tokens. It's an efficiency *tilt*, not a hard equalizer.

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
| **Leaderboard score** (auto) | **0.056** = 0.42 / log10(28 × 1,263,800) |
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
- **Amazon Bedrock** — Pay-per-token, hosts several Qwen3-Coder variants, DeepSeek-V3.1, Llama 3.x, MoE models. **Not eligible as your submission's model.** Fully-managed Bedrock endpoints don't publish the serving quantization (no verifiable VRAM number), and Bedrock Custom Model Import is Provisioned-Throughput-only at $21–50/hr with a 1- or 6-month commitment — not viable for a hackathon team. Fine for dev-time prompt exploration. If you want to use AWS for your submitted run, rent an EC2 or SageMaker GPU instance and run vLLM yourself. [aws.amazon.com/bedrock](https://aws.amazon.com/bedrock/)

### Free GPU notebooks (dev / iteration)

- **Kaggle Notebooks** ([kaggle.com/docs/notebooks](https://www.kaggle.com/docs/notebooks)) — Available to Community Hackathon participants. Free tier: T4 ×2 (32 GB total VRAM), P100 16 GB, or TPU v3-8; 30 hr/week GPU quota; 12 hr session cap; ~29 GB host RAM; 20-min idle timeout. The 32 GB dual-T4 setup can host Qwen2.5-Coder-32B-AWQ via vLLM `--tensor-parallel-size 2` — workable but PCIe-only comms make inference materially slower than a single 48 GB card.
- **Google Colab (free tier)** ([colab.research.google.com](https://colab.research.google.com/)) — Single T4 16 GB, ~13 GB host RAM, ~12 hr sessions with 90-min idle disconnect, ~15-30 GPU-hr/week dynamic quota. A 32B model does not fit on a single T4; use this for prompt engineering with smaller models (≤14B AWQ) only. Colab Pro+ has A100 access for paid users.

### Local hardware

Any GPU large enough to fit the reported VRAM of your chosen `MODELS.md` row. The suggested anchor (`Qwen2.5-Coder-32B-Instruct-AWQ`, 28 GB) runs comfortably on an RTX A6000 48 GB, L40S 48 GB, RTX Pro 6000 96 GB (or half-slice thereof), or any 32 GB+ card with reduced context. See [`starter/docs/byo_model.md`](starter/docs/byo_model.md) for Ollama / vLLM setup.

### UW–Madison participants (additional)

- **NRP / Nautilus managed-LLM endpoint** ([nrp.ai/llms](https://nrp.ai/llms/)) — UW researchers authenticate via CILogon SSO and hit an OpenAI-compatible endpoint at `https://ellm.nrp-nautilus.io/v1` hosting Qwen3 (397B), GLM-5 (744B), Kimi-K2.7-Code (1T), Gemma-4 (12B/31B), MiniMax-M2 (230B), GPT-OSS-120B, and more. All are listed in [`MODELS.md`](MODELS.md) or PR-addable. NRP also lets you spin up your own GPU pod with vLLM (A100, L40S, A40, RTX 4090, etc.) — request access at [nrp.ai/get-access](https://nrp.ai/get-access/).
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
No, not for the submitted run. Fully-managed Bedrock endpoints don't disclose the serving quantization, and Bedrock Custom Model Import is Provisioned-Throughput-only ($21–50/hr per model unit, 1–6 month commit) — not a serverless pay-per-token option, and not viable for a hackathon team. Bedrock is fine for development. If you want to use AWS for your real run, rent an EC2 or SageMaker GPU instance and self-host with vLLM.

**My model isn't in `MODELS.md`. What do I do?**
Open a PR adding it. Include the HuggingFace link, the published quantization, and a one-line VRAM justification (weights size + KV cache at 16k context). We merge quickly — usually same-day during the semester.

**Can I fine-tune a model for this?**
Yes. Document it in the writeup. Fine-tuned weights must be either public or reproducible from the public base model + your published LoRA / adapter, and you'll likely need to PR your fine-tuned checkpoint into `MODELS.md` so the leaderboard can score it.

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
- [ ] Stand up the leaderboard-score auto-calculator (takes submission card → returns `TB_score / log10(VRAM × total_tokens)`).
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
