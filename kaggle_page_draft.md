# Kaggle Hackathon Page Draft — MLM26: Local Coding Agent Challenge
# Copy each section into the corresponding Kaggle field.

---

## OVERVIEW (Kaggle "Overview" section)

Build the best local coding agent — one that runs entirely on open-weight models within a single GPU (≤96 GB VRAM) — and measure it on [Terminal-Bench 2.0](https://tbench.ai), the same benchmark used to evaluate Claude Code, Codex, Devin, and Cursor.

Frontier coding assistants are excellent, but they send your code to a third party, cost real money per task, and raise security concerns when data can't leave your environment. A growing class of users — researchers with sensitive data, organizations on tight budgets — needs coding agents that run locally. Open-weight models have closed enough of the gap that this is plausible. Your job: make it actually good.

**Hosted by [ML+X](https://mlx.wisc.edu/) at UW–Madison. September–December 2026.**

---

## TIMELINE (Kaggle "Timeline" section)

| Date | Milestone |
|---|---|
| September 2026 (Week 1) | Kickoff & team formation. Live Docker + Harbor setup workshop. |
| Week 2 | Baseline replication. Get the starter agent running with a score. |
| Week 3 | Failure analysis. Classify where your baseline fails. |
| Week 4 | Architecture commit. 5-min team pitch on your approach. |
| Week 5 | First working version. Demo your agent solving a task end-to-end. |
| Week 6 | **Mid-semester checkpoint.** Post writeup draft, demo to room, peer feedback. |
| Weeks 7–8 | Build & generalization test. Run against tasks you haven't optimized for. |
| Week 9 | Full writeup draft posted to Kaggle. |
| Week 10 | Peer review of writeups. |
| Week 11 | Final polish + dry run. |
| December 2026 (Week 12) | **Finale.** Public event. Live scoring, judging, awards. |

---

## DESCRIPTION (Kaggle "Description" section)

## What you're building

An autonomous coding agent that:
- Receives a task description (e.g., "find the lost git changes and merge them into master")
- Reads, explores, plans, and executes bash commands inside a Docker container
- Gets graded on the container's final state by an automated test suite
- Runs on open-weight models only, on a single GPU with ≤96 GB VRAM

The agent architecture is up to you: prompt engineering, tool design, planning, retrieval, context management, error recovery, self-verification, multi-stage pipelines, fine-tuning — anything goes within the hardware constraints.

## How it works

[Terminal-Bench 2.0](https://tbench.ai) provides 89 tasks spanning software engineering, security, data processing, system administration, scientific computing, and more. Each task ships as a Docker image with source code, instructions, and a test suite. [Harbor](https://www.harborframework.com/) is the official harness — it spins up containers, runs your agent, grades results, and reports scores.

```
harbor run → for each task:
  1. Build the task's Docker container
  2. Call your agent's setup() and run()
  3. Your agent reads the instruction, executes bash commands in the container
  4. Harbor runs the task's test suite against the final container state
  5. Score: 1.0 (pass) or 0.0 (fail)
```

Your agent never touches your real filesystem — it only acts inside the container through `environment.exec()`.

## The starter agent

We provide a minimal [ReAct](https://arxiv.org/abs/2210.03629)-style baseline agent (~60 lines of Python) that:
1. Sends the task instruction to an LLM via any OpenAI-compatible endpoint
2. Parses the LLM's response for a bash command
3. Executes it in the container
4. Feeds the output back as context
5. Repeats until the LLM says TASK_COMPLETE or hits the turn limit

With a 14B model (qwen2.5-coder:14b), this baseline can solve easy tasks like recovering lost git changes. With a 7B model, it fails almost everything. The gap between the baseline and a high-scoring agent is the competition.

## What you can change

| File | What it does | Improvement ideas |
|---|---|---|
| `agent/agent.py` | The main agent loop | Planning, context management, early stopping, multi-stage pipelines, loop detection |
| `agent/prompts.py` | System prompt + message templates | Task-type detection, output format constraints, self-verification, few-shot examples |
| `agent/tools.py` | Parses model output → actions | Richer tool set (read/write/search as first-class actions), smarter output truncation |
| `agent/llm.py` | Talks to the model endpoint | Retry logic, streaming, token budgeting, model routing |

You can also add entirely new files, modules, retrieval systems, or fine-tuned models. The only constraints are the hardware budget and generalizability requirement.

## Constraints

### Hardware
- **Single GPU with ≤96 GB VRAM.** Verified at finale on reference hardware.
- **Open-weight models only.** No API calls to GPT, Claude, Gemini, etc.
- **Quantization allowed.** fp16, int8, int4, AWQ, GGUF — whatever fits.
- **Dense or MoE both fine.** As long as it fits in the VRAM budget.

### Per-task budget
- **≤100 turns per task** (Terminal-Bench default)
- **≤5 minutes wall-clock per task** on reference hardware
- **No human-in-the-loop** at evaluation time

### Generalizability
Your agent must be general-purpose: one system prompt, one agent loop, no per-task `if task == "fix-git"` branching or task-specific prompt templates. Detecting task *categories* (e.g., "this looks like a debugging task") and adjusting strategy is fine — that's good engineering. Hardcoding solutions or prompts for individual tasks is not. Judges will read your code to verify.

## Why Terminal-Bench

[Terminal-Bench](https://tbench.ai) is the industry-standard benchmark for evaluating coding agents in terminal environments — joint work from Stanford, the Laude Institute, Anthropic, Snorkel, and many others. It has an active [public leaderboard](https://www.tbench.ai/leaderboard), and strong submissions have a post-MLM life as contributions the field actually cares about.

All 89 tasks are public — participants can browse descriptions, test suites, and solutions. The challenge is building an agent that *generalizes* across diverse task types, not memorizing individual solutions.

## Getting started

Full setup instructions, starter code, and walkthrough are in the challenge repo:

**[github.com/qualiaMachine/MLM26](https://github.com/qualiaMachine/MLM26)** (private — request access via the kickoff form)

The repo includes:
- Baseline agent code (`starter/agent/`)
- Setup scripts and environment config
- Step-by-step walkthrough from zero to a working Terminal-Bench score
- Documentation on Harbor, Docker setup, model endpoints, and troubleshooting

Quick summary of what you'll do:
1. Install Docker + uv + Python 3.12
2. Clone the repo, create a venv, install the starter package
3. Run the oracle agent to verify your setup (no model needed)
4. Set up Ollama with a local model (we recommend qwen2.5-coder:14b to start)
5. Run the baseline agent on an easy task and see it score 1.0

---

## SUBMISSION REQUIREMENTS (Kaggle "Submission Requirements" section)

A valid submission must contain the following:

### 1. Kaggle Writeup

Your project report. Should include:
- **Problem framing** — What are you trying to solve and why does it matter?
- **Approach** — What architecture, model, and techniques did you use? Why?
- **What worked and what didn't** — Honest analysis of your experiments.
- **Terminal-Bench scores** — Self-reported scores with the exact commands used to produce them.
- **Failure analysis** — Where does your agent still fail? What categories of tasks? Why?
- **Limitations** — What are the constraints of your approach?
- **What you'd do with another month** — Future directions.

Your Writeup should not exceed 5,000 words. Quality over length.

### 2. Video demo (3–5 minutes)

Show your agent solving at least one Terminal-Bench task end-to-end. Voiceover explaining what the agent is doing and why. Clear > polished.

Publish to YouTube, attach to your Writeup's Media Gallery.

### 3. Public notebook

Your agent code submitted as a public notebook in the Project Files field. Should be runnable or clearly documented.

### 4. Public project link

A GitHub repo link with:
- Your complete agent code in a runnable state
- A README with reproduction instructions
- Terminal-Bench-compatible agent (runnable via `harbor run --agent-import-path`)
- License: MIT or Apache 2.0

---

## TRACKS AND AWARDS (Kaggle "Tracks and Awards" section)

### Track A: Local Agent (main track)

Build the best general-purpose local coding agent under the hardware constraints. Open to all participants.

### Track B: Analysis & Insight (optional)

For teams that want to focus on understanding rather than engineering. Produce a rigorous analysis of coding agent behavior on Terminal-Bench: failure taxonomies, scaling laws, prompt sensitivity studies, model comparisons, etc. Scored primarily on engineering depth and clarity rather than raw Terminal-Bench score.

---

## EVALUATION (Kaggle "Evaluation" section)

## Judging Rubric (100 points total)

| Criteria | Points | Description |
|---|---|---|
| **Terminal-Bench score** | 0–25 | Raw performance across Terminal-Bench tasks. Higher is better. Evaluated by running your agent against a task set chosen by the judges. |
| **Generalizability** | 0–25 | Is your agent general-purpose? One system prompt, one agent loop, no per-task branching or task-specific prompt templates. Judges will read your code AND test your agent on tasks outside your reported set. Detecting task *categories* is fine; hardcoding individual task solutions is not. |
| **Engineering depth** | 0–20 | Is the work technically substantive? Did you try multiple approaches and analyze why some worked better? A deep understanding of *why* your agent fails on certain task categories scores higher than a marginally better number with no insight. |
| **Reproducibility** | 0–15 | Can someone else clone your repo and reproduce your results? Are hardware constraints respected? Does it fit in the VRAM budget? Are evaluation procedures honest? |
| **Clarity & presentation** | 0–15 | Writeup and video quality. Can a reader understand what you built, why, and what you learned? |

### Required elements (pass/fail)

| Requirement | Pass/Fail |
|---|---|
| Agent runs via `harbor run --agent-import-path` without modification | Yes/No |
| Open-weight models only (no closed API calls) | Yes/No |
| Fits within single GPU ≤96 GB VRAM | Yes/No |
| Public GitHub repo with reproduction instructions | Yes/No |
| Video demo ≤5 minutes | Yes/No |

### How Terminal-Bench score is evaluated

Judges will run your agent (from your public repo) against Terminal-Bench tasks using Harbor on reference hardware. Your self-reported scores should be reproducible. Significant discrepancies between self-reported and judge-evaluated scores will affect the Reproducibility criterion.

---

## JUDGES (Kaggle "Judges" section)

- **Chris Endemann** — ML+X, UW–Madison (organizer)
- TBD — Additional judges from ML+X and the Terminal-Bench community

---

## ADDITIONAL SECTION: Resources & Links

- **Challenge repo:** [github.com/qualiaMachine/MLM26](https://github.com/qualiaMachine/MLM26) (private — request access)
- **Terminal-Bench:** [tbench.ai](https://tbench.ai) — browse all 89 tasks
- **Terminal-Bench leaderboard:** [tbench.ai/leaderboard](https://www.tbench.ai/leaderboard)
- **Harbor docs:** [harborframework.com/docs](https://www.harborframework.com/docs)
- **Ollama:** [ollama.com](https://ollama.com) — easiest way to run local models
- **ML+X Discord:** [link TBD] — ask questions, find teammates, share progress
- **Office hours:** Wednesdays 4:30–6:30 pm CT (hybrid) during sprint weeks

---

## ADDITIONAL SECTION: FAQ

**Do I need a GPU to participate?**
You need a GPU to run your agent competitively, but you can get started on CPU with a small model (qwen2.5-coder:3b). UW participants can request RunAI-hosted endpoints. Cloud GPU providers (Lambda, RunPod, Vast.ai) work too.

**Can I use fine-tuned models?**
Yes. Document it in the writeup. Fine-tuned weights must be either public or reproducible from the public base model + your published LoRA/adapter.

**Can I use multiple models (e.g., a small model for planning, a large one for coding)?**
Yes, as long as the total fits in the VRAM budget at inference time.

**What if my team has unequal contributions?**
Both fine. Reflect honestly on contributions in the writeup.

**Can I use RAG, tool use, or external knowledge bases?**
Yes — anything that runs locally within the hardware constraints. No calls to external APIs for model inference.

**Is this individual or team-based?**
Teams of 1–4. Form at kickoff or find teammates on Discord.

**What programming language should the agent be in?**
The starter code is Python, and Harbor expects a Python class. Your agent can invoke any language inside the container, but the orchestration layer must be Python-compatible with Harbor's BaseAgent interface.
