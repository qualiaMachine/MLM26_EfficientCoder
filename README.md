# MLM26: Local Coding Agent Challenge

Build the best local coding agent — measured on Terminal-Bench 2.0. Hosted by [ML+X](https://mlx.wisc.edu/) at UW–Madison, September–December 2026. Open to everyone.

**UW–Madison participants** get weekly sprints, office hours, mid-semester presentations, and RunAI GPU access. Everyone else is welcome to participate remotely — the starter code, Terminal-Bench, and submission pipeline are fully open.

---

## Why this challenge

Frontier coding assistants like Claude Code, Cursor, and Codex are excellent — but they send your code to a third party, cost real money per task, and raise security concerns when data can't leave your environment. A growing class of users — researchers with sensitive data, organizations on tight budgets — needs coding agents that run locally. Open-weight models have closed enough of the gap that this is plausible. Your job: make it actually good.

The model is only half the story. A raw LLM can't reliably solve multi-step coding tasks on its own — it loses track of context, repeats failed commands, hallucinates file contents, and doesn't know when to stop. The real challenge is the **orchestration code around the model**: How do you manage a conversation that spans dozens of turns without blowing the context window? How do you detect when the agent is stuck in a loop? How do you chain reasoning, action, and verification into a pipeline that produces reliable results — not just sometimes, but every time? And how do you do all of this on a single GPU, where you can't just throw a bigger model at the problem?

This is an engineering challenge as much as an ML one. The teams that do well won't just pick the best model — they'll build the best system around it.

**This is a collaborative challenge, not a prize competition.** There are no cash prizes and no reason to hoard ideas. Share your repo early, post findings to the Discussion tab, fork each other's approaches, and build on what works. The best outcomes happen when everyone's baseline keeps rising — your writeup is where you show what *you* contributed, what you learned, and why your approach works.

### Why Terminal-Bench

We're not building a new benchmark from scratch. [Terminal-Bench](https://tbench.ai) is the industry-standard benchmark for evaluating coding agents in terminal environments — joint work from Stanford, the Laude Institute, Anthropic, Snorkel, and many others. It's open source, it has an active leaderboard, and it's the same yardstick used to evaluate Claude Code, Codex, Devin, Cursor, and friends. [Harbor](https://www.harborframework.com/) is the official harness for running Terminal-Bench 2.0.

By building on Terminal-Bench, your work is comparable to public leaderboard entries from day one, and strong submissions have a post-MLM life as contributions to a benchmark the field actually cares about.

---

## At a glance

- **Format:** Kaggle Community Hackathon, semester-long, collaborative
- **Dates:** Kickoff September 2026 → Finale December 2026
- **Sprints:** Wednesdays 4:30–6:30 pm (Madison time, hybrid)
- **Eval backbone:** Terminal-Bench 2.0 via [Harbor](https://www.harborframework.com/) (Docker-per-task, outcome-based scoring)
- **Hardware constraint:** Single GPU ≤48 GB VRAM (sized to fit Qwen2.5-Coder-32B at 4-bit AWQ comfortably)
- **Per-task budget:** ≤100 turns (Terminal-Bench default), ≤5 minutes wall-clock
- **Default model:** Qwen2.5-Coder-32B-Instruct (AWQ 4-bit) — the suggested anchor so anyone with a ~48 GB GPU slice can compete. Teams are free to explore other open-weight models that fit the budget.
- **Models:** Open weights only. Bring-your-own endpoint (Ollama, vLLM, hosted open-weight API). RunAI-hosted endpoints available on request for UW participants.
- **Submission:** Submission card + writeup + public notebook + public GitHub repo (one per team, end of semester)
- **Judging:** Automated ranking by score → top ~10 get human review
- **Teams:** 1–4 people, open to everyone

---

## The challenge

Build an autonomous coding agent that scores highest on Terminal-Bench 2.0 under local-model constraints. ≤48 GB VRAM on a single GPU, open-weight models only, capped per-task budget. The suggested anchor model is **Qwen2.5-Coder-32B-Instruct at 4-bit AWQ** — it fits the VRAM budget with room for context and batching, runs locally on a single 48 GB GPU (or half of a 96 GB card), and gives every team a strong common baseline. Teams are free to explore other open-weight models that fit. Within those limits, anything goes — your choice of base model, scaffolding, retrieval, tool design, prompting, quantization, agent loop, fine-tuning.

The model gives you a reasoning engine. Everything else — how you prompt it, how you manage conversation history, how you recover from errors, how you decide when the task is actually done — is the orchestration layer you build around it. That orchestration code is where the challenge lives.

All 89 Terminal-Bench tasks are public — the challenge is building an agent that generalizes, not memorizing solutions. See [Judging](#judging) for the full rubric.

---

## Constraints

These exist to make this a *local* coding agent challenge rather than "whoever brought the biggest GPU."

### Hardware

- **Single GPU with ≤48 GB VRAM.** Sized to fit Qwen2.5-Coder-32B at 4-bit AWQ with room for context and batching. Verified at finale on reference hardware (e.g. half-slice of an RTX Pro 6000 96 GB, L40S 48 GB, or A100/H100 partitioned to a 48 GB budget).
- **The 48 GB budget exists to keep this inclusive.** Anyone with a single ~48 GB GPU (or a slice of a larger one) should be able to participate locally — including folks outside UW without cluster access.
- **Quantization allowed.** fp16, int8, int4, AWQ, GGUF — we only care that it fits in 48 GB at evaluation time (weights + KV cache + activations).
- **Dense or MoE both fine.** As long as the loaded footprint fits the VRAM budget.
- **No multi-GPU agents.** Tensor parallelism across two GPUs disqualifies.
- **No closed-weight model calls.** This is a *local* coding agent challenge. Calling GPT-5 or Claude or Gemini from inside your agent is out of scope, even for "just the planner." Open weights served locally or via open-weight hosted APIs (Together, Fireworks, Groq serving Qwen/Llama/DeepSeek/etc.) are fine.

### Per-task budget

- **≤100 turns per task.** Matches Terminal-Bench default.
- **≤5 minutes wall-clock per task** on reference hardware.
- **No human-in-the-loop at evaluation time.** The agent runs autonomously from task instruction to completion.

### Safety (non-negotiable)

Terminal-Bench already runs each task in a fresh Docker container with no host access. Don't undo that. Specifically:

- Don't mount your home directory into the agent container.
- Don't embed personal credentials in the container.
- Don't punch holes in the network allowlist beyond your model endpoint.

Full safety section below.

---

## Schedule

| Date | Milestone |
|---|---|
| September 2026 | **Kickoff.** Team formation, Docker + Harbor setup workshop (bring your laptop), starter code walkthrough. |
| Mid-October 2026 | **Mid-semester presentation.** 5-min team presentation: your approach, progress so far, and what you've learned. |
| December 2026 | **Final submission.** Writeup, code, and notebook due. Live scoring and awards event. |

How you manage the weeks in between is up to your team. We recommend getting the baseline running in Week 1, doing failure analysis in Weeks 2–3, and iterating from there — but you know your schedule best.

**Weekly sprints** (Wednesdays 4:30–6:30 pm CT, hybrid) are available for working sessions, questions, and informal demos throughout the semester.

---

## Submission format

**One submission per team, at the end of the semester.** There is no live leaderboard and no mid-semester submissions — focus on building and understanding, not chasing a number.

During the semester, share early and often via the Kaggle Discussion tab: post draft writeups, share your repo, describe what's working and what isn't. Other teams should feel free to fork, adapt, and build on your ideas — that's the point. Credit what you borrowed in your writeup, and explain what you added.

Your submission has two parts:

**Part 1: Submission card** — Structured metadata used for automated ranking (model, params, quantization, GPU, VRAM, Terminal-Bench score, repo URL, commit tag). See the [Kaggle page](TBD) for the full field list.

**Part 2: Full submission** — Attached to your Kaggle Writeup:
1. **Writeup** (≤5,000 words). Problem framing, approach, what worked, what didn't, Terminal-Bench scores, failure analysis, limitations, what you'd do with another month. Quality > length.
2. **Public notebook.** Your agent code as a public notebook. Should be runnable or clearly documented.
3. **Public GitHub repo.** Complete agent code, README with reproduction instructions, a tagged release or commit hash matching your reported scores (e.g., `git tag v1.0-submission`), Terminal-Bench-compatible agent (runnable via `harbor run --agent-import-path`). License: MIT or Apache 2.0.

---

## Judging

Evaluation happens in two stages to scale to many submissions without drowning in manual review.

### Stage 1: Automated ranking (all submissions)

Every team submits a **submission card** with structured metadata: model used, parameter count, quantization, GPU, VRAM usage, Terminal-Bench score, and repo link. Submissions are ranked by self-reported score. No human review at this stage.

### Stage 2: Human review (top ~10)

Judges deep-review the top ~10 submissions by score:
1. Clone the repo at the tagged commit, run `harbor run` on reference hardware, verify the reported score.
2. Read the code to check for generalizability — no per-task branching or hardcoded solutions.
3. Read the writeup and score against the rubric below.

Honest run-to-run variance is fine. Significant discrepancies between reported and reproduced scores disqualify. Cherry-picked or inflated numbers are not tolerated.

### Rubric (100 points, applied to finalists)

- **Terminal-Bench score (25%)** — Raw performance. Verified by judges on reference hardware.
- **Generalizability (25%)** — One system prompt, one agent loop, no per-task `if task == "fix-git"` branching. Judges read your code AND test on tasks outside your reported set. Detecting task *categories* is fine; hardcoding individual solutions is not.
- **Engineering depth (20%)** — Did you try multiple approaches and analyze why some worked better? Deep understanding of *why* your agent fails scores higher than a marginally better number with no insight.
- **Reproducibility (15%)** — Can someone clone your repo and reproduce your results? Does it fit the VRAM budget? Is the submission card accurate?
- **Clarity & presentation (15%)** — Writeup quality. Can a reader understand what you built, why, and what you learned?

---

## Getting started

This section is your fast path from "I registered" to "I have a working baseline scoring on Terminal-Bench." The baseline agent and all supporting docs live in the [`starter/`](starter/) directory of this repo. For a detailed step-by-step walkthrough with expected output at every stage, see [`starter/docs/walkthrough.md`](starter/docs/walkthrough.md).

### Prerequisites

- **Python 3.12+** (required by Harbor)
- **[uv](https://docs.astral.sh/uv/)** — fast Python package manager (recommended over pip)
- **Docker** — required by Harbor / Terminal-Bench (see setup below)
- **A model endpoint.** Options:
  - **Local Ollama.** Easiest, runs on most laptops with a GPU. Recommended for first-week setup.
  - **Local vLLM.** Higher throughput, more setup. Recommended for serious work.
  - **Hosted open-weight API.** Together, Fireworks, Groq, etc. Easy for development if you don't have local hardware yet.
  - **RunAI-hosted endpoint.** UW participants can request access via the kickoff form. Capacity is limited.

### Why Docker, and how to set it up

Terminal-Bench runs every task inside a **fresh Docker container** — that's both the sandbox (the agent can't touch your real filesystem) and the reproducibility guarantee (everyone's agent sees the identical environment). There is no way to run Terminal-Bench without Docker, so getting it installed and running is step zero. We'll do a live Docker setup walkthrough at the Week 1 kickoff — if you get stuck, bring your laptop.

After installing (instructions per-OS below), verify with:

```bash
docker --version          # should print a version
docker run hello-world    # should print "Hello from Docker!"
```

Expected output (first run pulls the image, then prints the greeting):

```
Unable to find image 'hello-world:latest' locally
latest: Pulling from library/hello-world
...
Status: Downloaded newer image for hello-world:latest

Hello from Docker!
This message shows that your installation appears to be working correctly.
...
```

If you see `Hello from Docker!`, you're good. The rest of the output is informational.

<details>
<summary><strong>🍎 macOS</strong></summary>

1. Install [Docker Desktop for Mac](https://docs.docker.com/desktop/setup/install/mac-install/). Choose **Apple Silicon** or **Intel** to match your machine (check  → About This Mac).
2. Open the downloaded `.dmg`, drag Docker to Applications, and launch it.
3. Docker Desktop must be **running** (whale icon in the menu bar) whenever you use Harbor.

Alternative for the homebrew-inclined: `brew install --cask docker`, then launch Docker from Applications.

</details>

<details>
<summary><strong>🐧 Linux (Ubuntu/Debian)</strong></summary>

Install Docker Engine (no Desktop app needed):

```bash
# Official convenience script
curl -fsSL https://get.docker.com | sh

# Let your user run docker without sudo
sudo usermod -aG docker $USER
newgrp docker   # or log out and back in

# Docker starts automatically on most distros; verify:
docker run hello-world
```

For other distros, see [Docker Engine install docs](https://docs.docker.com/engine/install/).

</details>

<details>
<summary><strong>🪟 Windows</strong></summary>

Docker on Windows requires **WSL2** (Windows Subsystem for Linux). Do everything below **inside WSL2**, not in PowerShell — the whole challenge toolchain (uv, Harbor, the starter repo) assumes a Unix shell.

1. Install WSL2: open PowerShell **as Administrator** and run:
   ```powershell
   wsl --install
   ```
   Reboot when prompted. This installs Ubuntu by default. After rebooting, a terminal window may open automatically to finish Ubuntu setup (username + password) — if not, open **"Ubuntu"** from the Start menu to complete it.
2. Install [Docker Desktop for Windows](https://docs.docker.com/desktop/setup/install/windows-install/). During setup, ensure **"Use WSL 2 based engine"** is checked.
3. In Docker Desktop → Settings → Resources → WSL Integration, enable integration for your Ubuntu distro.
4. Open the Ubuntu terminal: press the **Windows key**, type **Ubuntu**, and click the **"Ubuntu"** app. (You can also open Windows Terminal and select the Ubuntu tab from the dropdown.) **All remaining setup commands go here, not in PowerShell.** Verify Docker works:
   ```bash
   docker run hello-world
   ```

Common gotcha: if `docker` isn't found inside Ubuntu, WSL integration (step 3) isn't enabled.

</details>

**Common issues (all platforms):**

- *"Cannot connect to the Docker daemon"* → Docker isn't running. Start Docker Desktop (macOS/Windows) or `sudo systemctl start docker` (Linux).
- *Permission denied on Linux* → you skipped the `usermod -aG docker` step.
- *Disk space* — Terminal-Bench task images add up. Give Docker ≥30 GB. `docker system prune` reclaims space (careful: deletes stopped containers and unused images).

### Quickstart

> **Windows users:** run everything below inside your **Ubuntu / WSL2 terminal**, not PowerShell.

**1. Install uv** (if you don't have it):

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc   # reload your shell so uv is on your PATH
```

**2. Clone this repo and set up the starter environment:**

```bash
git clone git@github.com:qualiaMachine/MLM26.git
cd MLM26

# Create a virtual environment (best practice: one venv per project)
uv venv --python 3.12              # creates .venv/; uv fetches Python 3.12 if missing
source .venv/bin/activate          # activate it (on Windows/WSL2 same command)
uv pip install -e starter/         # installs harbor + the agent package (editable)
```

**3. Verify Harbor + Terminal-Bench works** by running the oracle agent against the 10-task sample set.

**Background:** Terminal-Bench tasks are challenges that test what a coding agent can do from a bash terminal. The 89 tasks span categories (software-engineering, security, data-processing, scientific-computing, system-administration, etc.) and difficulties (easy → hard). Examples: "find lost git changes and merge them" (easy, software-engineering), "build a Cython extension with NumPy compatibility" (medium, debugging), "configure a git-triggered webserver" (hard, system-administration). Browse all tasks at [tbench.ai](https://www.tbench.ai/). Each task ships as a Docker image containing source code, instructions, and a test suite that grades the final state of the container. Your agent's job (eventually) is to read the instructions, figure out what to do, and execute bash commands inside the container until the task is solved.

[Harbor](https://www.harborframework.com/) is the official harness that orchestrates all of this — it pulls task definitions, spins up Docker containers, runs your agent inside them, grades results against the test suite, and tears everything down.

**What this step does:** Harbor downloads 10 sample task definitions (~first run only, cached after), then for each task it builds a Docker container and runs the **oracle agent** inside it. The oracle is a cheat — it just replays each task's known solution step-by-step instead of thinking. It exists so you can verify your Docker + Harbor setup without needing a GPU, a model endpoint, or an API key. If the oracle scores 100%, your plumbing works.

**Expect:** ~5–10 minutes on first run (downloading task images), ~2 minutes on subsequent runs. Needs ~4 GB disk for task images and ~4 GB RAM. Everything runs on CPU.

```bash
cd starter
harbor run -d terminal-bench-sample@2.0 -a oracle
```

Expected output:
```
  10/10 Mean: 1.000 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 0:02:52 0:00:00

terminal-bench-sample • oracle
┏━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━┓
┃ Trials ┃ Exceptions ┃  Mean ┃
┡━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━┩
│     10 │          0 │ 1.000 │
└────────┴────────────┴───────┘

Job Info
Total runtime: 3m 5s
Results written to jobs/2026-06-15__13-39-11/result.json
```

If you see `Mean: 1.000` with 0 exceptions, Docker and Harbor are working correctly. If tasks fail, it's a Docker or network issue — see `starter/docs/troubleshooting.md`.

**4. Run the baseline agent** against a single sample task.

What this does: unlike the oracle, this runs **your actual agent** — it sends the task instruction to an LLM, the LLM generates bash commands, the agent executes them inside the Docker container, and the loop repeats until the agent declares done or hits the turn limit. The task's test suite then grades the final container state.

**Requires:** a running LLM that the agent can talk to via an API. The baseline agent communicates with the model through an OpenAI-compatible HTTP endpoint (chat completions API) — it doesn't load model weights directly. That means you need something that *serves* a model, not just the model files themselves.

The quickest way to get this running is [Ollama](https://ollama.com/download). Ollama handles downloading the model, quantizing it, and serving it behind an OpenAI-compatible API — all in one tool. You could also download models from Hugging Face and serve them yourself with [vLLM](https://docs.vllm.ai/) or [llama.cpp](https://github.com/ggml-org/llama.cpp), which gives you more control (custom quantizations, batching, multi-GPU). See `starter/docs/byo_model.md` for those options. For getting started, Ollama is the path of least resistance.

This design also means you can swap in *any* OpenAI-compatible endpoint later — a model on a shared cluster (e.g., RunAI/Slurm + vLLM), a cloud API like Amazon Bedrock or Google Vertex, or a friend's GPU across the network. Just change `LLM_BASE_URL`, `LLM_MODEL`, and `LLM_API_KEY` in `.env`. No code changes needed.

**Set up Ollama:**

```bash
# Install Ollama (if you don't have it)
sudo apt-get update && sudo apt-get install -y zstd   # required by the Ollama installer
curl -fsSL https://ollama.com/install.sh | sh
```

The installer starts Ollama's HTTP server automatically in the background (via systemd). Verify it's running:

```bash
curl http://localhost:11434/v1/models
```

You should see a JSON response (an empty model list is fine — you haven't pulled anything yet). If you get "connection refused," run `ollama serve` in a separate terminal.

Now download a model. This just saves files to disk — **no GPU usage yet.** Ollama loads models into GPU memory on demand when the first API request arrives, keeps them loaded for ~5 minutes of inactivity, then unloads. Your GPU stays idle until the agent actually runs.

```bash
# Pick one that fits your hardware:
#   No GPU / CPU only:     ollama pull qwen2.5-coder:3b      (~2 GB, slow but works)
#   8 GB VRAM:             ollama pull qwen2.5-coder:7b      (~4.7 GB)
#   16+ GB VRAM:           ollama pull qwen2.5-coder:14b     (~9 GB)  ← recommended starting point
#   24+ GB VRAM:           ollama pull qwen2.5-coder:32b     (~20 GB)
ollama pull qwen2.5-coder:14b
```

**Configure the model endpoint** (from the `starter/` directory — that's where `.env` and the agent code live):

```bash
cd ~/MLM26/starter
cp .env.example .env
```

The defaults in `.env.example` already point at Ollama with `qwen2.5-coder:14b`. If you pulled a different model, edit `.env` to match:
```bash
LLM_BASE_URL=http://localhost:11434/v1
LLM_MODEL=qwen2.5-coder:14b            # adjust to 7b if < 32 GB memory; expect most tests to fail with small models
LLM_API_KEY=ollama                      # Ollama doesn't need auth — this is a dummy
                                        # value to satisfy the OpenAI client library,
                                        # which errors if api_key is empty. Any non-empty
                                        # string works.
```

**Understand the agent before you run it.** A raw LLM can't solve Terminal-Bench tasks — it can only generate text. What makes it useful is the **agent loop** (the orchestration code) that sits between the model and the Docker container. This is the architecture that companies like Cursor, Devin, and Codex are built on, and it's what you'll be improving all semester.

The baseline agent lives in `starter/agent/agent.py` (~60 lines). Here's what it does:

```
┌─────────────────────────────────────────────────┐
│  Harbor spins up a Docker container for the     │
│  task, then calls your agent's run() method     │
│  with the task instruction + container access.  │
└──────────────────────┬──────────────────────────┘
                       ▼
              ┌─── AGENT LOOP ───┐
              │                  │
              │  1. Send the full conversation    │
              │     (system prompt + history)     │
              │     to the LLM via HTTP API       │
              │                                   │
              │  2. Parse the LLM's response:     │
              │     ```bash ...```  → command     │
              │     TASK_COMPLETE   → stop         │
              │     anything else   → nudge LLM   │
              │                                   │
              │  3. Execute the command inside     │
              │     the Docker container           │
              │                                   │
              │  4. Append the output back to      │
              │     the conversation as context    │
              │                                   │
              │  5. Repeat (up to MAX_TURNS)        │
              └───────────────────────────────────┘
```

This is a minimal [ReAct](https://arxiv.org/abs/2210.03629) loop: the LLM **reasons** about what to do, **acts** by emitting a bash command, **observes** the output, and repeats. The baseline is deliberately simple — no planning, no error recovery, no context management, no self-critique. **That's what you'll add.** The orchestration layer is where all the points are.

Read the code: `agent/agent.py` (the loop), `agent/prompts.py` (what the LLM sees), `agent/tools.py` (how commands get parsed and run), `agent/llm.py` (the API client).

**Now run it** on a single task with a low turn limit so it finishes quickly (make sure you're in `starter/`):

```bash
cd ~/MLM26/starter    # harbor must run from here — .env and agent/ live here
AGENT_MAX_TURNS=15 harbor run -d terminal-bench@2.0 \
  --agent-import-path agent.agent:BaselineAgent \
  -i fix-git
```

What this command does:
- `AGENT_MAX_TURNS=15` — caps the agent at 15 reasoning/action cycles instead of the default 100. For this test run you just want to see the loop work, not wait an hour.
- `-d terminal-bench@2.0` — use the full 89-task Terminal-Bench dataset as the task source (first run downloads task definitions, cached after). This doesn't mean it runs all 89 — that's what `-i` controls.
- `--agent-import-path agent.agent:BaselineAgent` — load our agent class from `agent/agent.py`.
- `-i fix-git` — **include only** the `fix-git` task (the output will show `1/1`). Without `-i`, Harbor would run all 89 tasks. You can pass `-i` multiple times to include more tasks (e.g., `-i fix-git -i polyglot-c-py` runs 2). This task is one of the easiest in Terminal-Bench (difficulty: easy, category: software-engineering) — the agent needs to find some lost git changes and merge them into master.

> **About task difficulty:** Terminal-Bench tasks span easy/medium/hard across categories like software-engineering, security, data-processing, scientific-computing, and system-administration. You can browse all 89 tasks with filters at [tbench.ai](https://www.tbench.ai/). The 10-task sample set (`terminal-bench-sample@2.0`) is handy for quick iteration but contains no easy tasks — so for this first demo we use the full dataset with a single easy task.

**Expect:** ~5–10 minutes depending on model speed. You need enough RAM/VRAM to run your chosen model **plus** the Docker container (~2 GB). First run may take longer as Harbor downloads the task definition.

Expected output (with the 14B model):

```
  1/1 Mean: 1.000 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 0:08:49 0:00:00

terminal-bench • mlm26-baseline
┏━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━┓
┃ Trials ┃ Exceptions ┃  Mean ┃
┡━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━┩
│      1 │          0 │ 1.000 │
└────────┴────────────┴───────┘
```

If you see `Mean: 1.000`, your agent just solved a real Terminal-Bench task — it found orphaned git changes via `git reflog`, merged them into master, resolved a merge conflict, verified the result, and declared done. All autonomously, with a local 14B model.

> **Scoring 0.0?** Check `job.log` in the job directory (see [Reading your results](#reading-your-results) below) to see what the model actually did. Common failure modes: the model gets stuck in a loop repeating the same command, tries to push to a remote that doesn't exist, or uses `sed` on files with special characters and mangles them. Smaller models (7B) will fail most tasks — that's the starting line. The competition is about improving the agent orchestration to get more tasks passing.

> **Why only 15 turns?** The competition default is 100 turns per task, but small models tend to get stuck in loops — repeating the same command dozens of times. For this setup check, 15 turns is enough. When you start improving your agent, remove the cap or set it higher: `AGENT_MAX_TURNS=100`.

### Reading your results

Every run creates a timestamped directory under `starter/jobs/`:

```
starter/jobs/2026-06-15__16-00-02/          ← one directory per run
├── job.log                                  ← full agent trace: every LLM command, every output
├── terminal-bench__fix-git/                 ← one subdirectory per task
│   └── 0/                                   ← attempt number (0-indexed; more with --n-attempts)
│       └── result.json                      ← score, timing, token usage, metadata
├── terminal-bench__polyglot-c-py/
│   └── 0/
│       └── result.json
└── ...
```

**`job.log`** — Your first stop for debugging. Contains the full agent trace: every command the model ran, every turn, in order. This is how you see *what* the model did and *where* it went wrong. Example:

```
[agent] turn 1: git status
[agent] turn 2: git log --oneline --graph --all
[agent] turn 3: git checkout d7d3e4b
...
```

**`result.json`** — One per task per attempt. Key fields:

| Field | What it tells you |
|---|---|
| `reward` | The score: `1.0` = passed the test suite, `0.0` = failed |
| `started_at` / `finished_at` | Timing for each phase (environment setup, agent setup, agent execution, verifier) |
| `exception` | What went wrong if the trial crashed (null if it ran cleanly) |
| `n_input_tokens` / `n_output_tokens` | How many tokens your agent consumed |
| `metadata.turns` | How many reasoning/action cycles the agent used |
| `metadata.finished` | Whether the agent said TASK_COMPLETE (`true`) or hit the turn limit (`false`) |
| `metadata.messages` | The full LLM conversation — every system/user/assistant message, in order |

Inspect a result:
```bash
# Pretty-print the latest result
cat jobs/2026-06-15__16-00-02/terminal-bench__fix-git/0/result.json | python3 -m json.tool

# Just see the score
python3 -c "import json; print(json.load(open('jobs/2026-06-15__16-00-02/terminal-bench__fix-git/0/result.json'))['reward'])"
```

When you run with `--n-attempts 5` (required for the leaderboard), each task gets attempt directories `0/` through `4/`, each with its own `result.json`. Harbor reports the aggregate pass@k stats in the console.

See `starter/docs/troubleshooting.md` if you get errors instead of a verdict.

### What's in `starter/`

```
starter/
├── agent/
│   ├── agent.py            # BaselineAgent (Harbor BaseAgent) — main loop, read it
│   ├── tools.py            # Action parsing + shell execution helpers
│   ├── llm.py              # OpenAI-compatible client wrapper
│   └── prompts.py          # System prompts (modify freely)
├── eval/
│   └── public_subset.txt   # Official MLM26 public task subset (announced at kickoff)
├── scripts/
│   ├── run_baseline.sh     # Single-task runner (sample set)
│   └── run_subset.sh       # Run the official public subset
├── docs/
│   ├── docker_setup.md     # Per-OS Docker install + troubleshooting
│   ├── safety.md
│   ├── troubleshooting.md
│   ├── byo_model.md        # How to point at your own endpoint
│   └── harbor.md           # Harbor orientation + custom agent guide
├── .env.example
├── pyproject.toml          # `uv pip install -e starter/` makes the agent importable by Harbor
└── README.md
```

The agent code is *yours to modify*. Harbor handles container lifecycle, scoring, and result aggregation — you focus on the agent logic in `agent/agent.py`, which implements Harbor's `BaseAgent` interface.

### How agents plug into Harbor

Harbor supports custom agents without modifying Harbor itself. Two integration styles:

1. **External agents** — implement Harbor's `BaseAgent` interface (`name`, `version`, `setup`, `run`). Your agent runs on your machine and drives the task container through Harbor's `BaseEnvironment` interface (executing bash via `exec`). **The starter baseline is an external agent** — it's the simplest place to start.
2. **Installed agents** — implement `BaseInstalledAgent`. Your agent is installed *into* the task container and runs headless inside it. More setup, but lets you bring custom tools into the environment. Worth considering once your agent matures.

Either way, you run it the same way:

```bash
harbor run -d terminal-bench@2.0 --agent-import-path agent.agent:BaselineAgent
```

Useful flags: `-i <task-name>` to include specific tasks (repeatable, supports globs), `-x` to exclude, `-n` to control how many tasks run concurrently, `-m` to record the model used.

Harbor also ships with pre-integrated agents (Terminus-2, Claude Code, Codex CLI, OpenHands, Mini-SWE-Agent, and more — see `harbor run --help`). These are useful reference points, but remember: closed-weight agents are out of scope for Track A scoring. Running Terminus-2 with your local model is a legitimate baseline to beat.

### The agent loop, briefly

The baseline is intentionally minimal. ReAct-style, inside the `run()` method of a `BaseAgent`:

1. Receive the task instruction from Harbor
2. Ask the LLM what to do next, with the current state
3. Parse the response for a tool call (shell, read, write, done)
4. Execute the tool inside the task container via the `environment` interface
5. Loop until "done" or budget exhausted, populating the agent context as you go

~200 lines of Python. No frameworks. Read it before you modify it.

Things you might add: better planning, retrieval over the codebase, multi-step reasoning, smarter context management, error recovery, self-critique, ensemble approaches, fine-tuning. That's the work.

### Understanding Terminal-Bench (briefly)

Each Terminal-Bench task ships with:
- An instruction (natural language description of what to do)
- A Docker image (the starting environment)
- A set of tests (graded on final container state, not on what the agent said)
- An example solution
- A time limit

Your agent gets the instruction and a shell-like interface to the container. It works on the task. When it declares done (or the budget runs out), the tests run. Pass or fail.

Harbor handles container lifecycle, scoring, and result aggregation. See `docs/harbor.md` for a quick orientation, or go straight to [harborframework.com/docs](https://www.harborframework.com/docs) and [tbench.ai](https://tbench.ai) for the upstream docs.

### Submitting to the Terminal-Bench leaderboard

Leaderboard logs are stored in [this HuggingFace repo](https://huggingface.co/datasets/harborframework/terminal-bench-2-leaderboard). To submit your results, run with `--n-attempts 5` and open a PR there following the instructions in its README (a validation bot checks ≥5 trials per task). View the live leaderboard at [tbench.ai/leaderboard](https://tbench.ai/leaderboard).

---

## Safety

Coding agents are powerful and stupid in roughly equal measure. They will, given the chance, do the worst thing the available tools allow. Not maliciously — they hallucinate paths, misinterpret instructions, and confidently run destructive commands. This has happened in production at companies with full-time safety teams.

**Treat agent safety like lab safety.** Don't pipette by mouth, don't give your agent your real filesystem.

### Good news: Terminal-Bench already sandboxes most of this

Terminal-Bench runs each task in a fresh Docker container with no host access. The container is destroyed after the task. You'd have to actively work to make this unsafe.

### What you still need to think about

- **Don't undo the sandbox.** Don't mount your home directory in. Don't bind your `~/.gitconfig` or SSH keys. Don't disable network restrictions to "just try something quick."
- **Don't bake real credentials into the container image.** Use throwaway API keys for the hackathon. If your agent needs an OpenAI-compatible key, point it at your local endpoint or a hackathon-specific key.
- **Be cautious with your own development loop.** When debugging locally *outside* the Terminal-Bench sandbox, your agent has access to whatever you give it. Develop in a scratch directory, not your home directory. Don't run "let me see what it does" against a real repo you care about.
- **Resource quotas.** Use Docker's built-in CPU/memory limits during dev. The Terminal-Bench harness sets task-level time limits but a runaway agent on your dev machine is still a problem.

### High-risk areas to think about

- **Git operations.** An agent that can run `git` can force-push, delete branches, rewrite history, leak credentials. Inside Terminal-Bench this doesn't matter (the container has no real remote). Outside it, keep your `.git` directories away from your dev agent.
- **Package installation.** `pip install` from an LLM suggestion can install anything from PyPI. Inside Terminal-Bench the container is throwaway. Outside, use a venv or container.
- **Shell commands.** Even "safe" commands compose into damage. `find . -name "*.py" -exec rm {} \;` looks like a search. `mv` and `cp` overwrite without prompting. `>` truncates files.
- **Looks-safe traps.** `chmod` can lock you out. `git clean -fdx` deletes untracked files including your work. `docker system prune` deletes everything.

### Red team exercise

At some point early in the semester, we'll release a deliberately misbehaving sample agent. Your job: figure out what it does wrong, what damage it could do in a less-sandboxed environment, and how the Terminal-Bench harness prevents most of it.

The instincts that prevent your agent from `rm -rf`ing your homedir are the same instincts that prevent it from confidently making wrong edits to a real codebase.

### Liability

Participants are responsible for their own machines and accounts. UW provides sandboxed cluster access on request via RunAI; usage there is bound by standard UW research-IT policy. If your agent does something unexpected and concerning, tell us — we want to know about novel failure modes.

---

## Bring-your-own model

The baseline agent talks to any OpenAI-compatible endpoint. Configure via `.env`:

```bash
LLM_BASE_URL=http://localhost:11434/v1   # Ollama default
LLM_MODEL=qwen2.5-coder:32b
LLM_API_KEY=ollama                       # Anything non-empty for Ollama
```

Harbor also supports passing model config directly:

```bash
harbor run \
  -d terminal-bench@2.0 \
  -m ollama/qwen2.5-coder:32b \
  --agent-import-path agent.agent:BaselineAgent
```

Tested endpoints (community-maintained list — additions welcome):

- **Ollama** — easiest local setup, good model selection, works on Apple Silicon
- **vLLM** — production-grade, requires more setup
- **llama.cpp / llamafile** — CPU and Apple Silicon friendly
- **Together AI, Fireworks, Groq** — hosted open-weight inference, useful for development
- **RunAI (UW)** — request access at kickoff

Pick whatever lets you iterate fast. You can swap models freely throughout the semester. The constraint at evaluation time is that whatever you submit must fit the hardware budget.

### Recommended models to try (as of mid-2026)

This list ages fast. Treat it as a starting point.

**Default / suggested anchor: Qwen2.5-Coder-32B-Instruct (AWQ 4-bit).** This is our recommended starting model — it fits comfortably in 48 GB with headroom for context and batching, has a well-tested AWQ checkpoint on Hugging Face, and serves cleanly under vLLM. Using this as your baseline makes it easy to compare results across teams. You are **not** required to use it — anything open-weight that fits the budget is fair game.

Other models worth trying (must still fit in ≤48 GB at eval time):

- **Qwen2.5-Coder 14B / Qwen3-Coder** variants — smaller footprint, more headroom for long context or larger batches
- **DeepSeek-Coder V2** family — strong on harder tasks
- **GLM-4.5** — recent, well-regarded for agent work
- **Llama 3.x** — quantized variants that fit in 48 GB
- **MoE models with a small active-parameter slice** — only if the loaded footprint fits 48 GB (note: full weights still need to fit)

A 32B-class Qwen-Coder agent has already cracked the Terminal-Bench leaderboard above some larger MoE setups — careful agent design matters more than parameter count.

---

## Task sets

All 89 Terminal-Bench 2.0 tasks are public — participants can browse descriptions, test suites, and solutions at [tbench.ai](https://tbench.ai). The challenge is building an agent that *generalizes* across diverse task types, not memorizing individual solutions.

Run your agent against any tasks you want during the semester to track progress. Your final submission should report scores with the exact commands used to produce them. Judges may run your agent against tasks outside your reported set to test generalizability.

---

## Communication

- **Kaggle forum** — async questions, public discussion
- **Discord** — informal, real-time, drop-in office hours
- **Weekly Wednesday sprints** — hybrid, recorded
- **Office hours** — TBD, posted in Discord
- **Terminal-Bench Discord** — separate, upstream community. Worth joining.

Be kind, be specific, search before you ask.

---

## FAQ (initial)

**Can I use a closed-weight model just for planning, with a local model for execution?**
No. The whole challenge is local. If part of your system calls GPT-5, Claude, or Gemini, it's out of scope.

**Can I fine-tune a model for this?**
Yes. Document it in the writeup. Fine-tuned weights need to be either public or runnable from the public base model + your published LoRA / patch.

**Can I submit my agent to the public Terminal-Bench leaderboard?**
Yes, please. Independent of MLM. It's a real leaderboard and a real artifact.

**Do I need to use the entire Terminal-Bench task set?**
For evaluation during the semester, no — work with whatever subset is useful for your debugging. For the finale, you don't pick — we score against a fixed held-out subset.

**My team is just me.** / **My team is four people.**
Both fine. Teams of 1–4. Reflect honestly on contributions in the writeup.

**I don't have a GPU.**
You can get started on CPU with a small model (qwen2.5-coder:3b). UW participants can request RunAI-hosted endpoints. Cloud GPU providers (Lambda, RunPod, Vast.ai) work too.

**I'm not at UW.**
Welcome. The challenge is fully open. You won't have access to weekly sprints, office hours, or RunAI endpoints, but you're eligible for all main track awards. UW participants also compete for local awards.

**Will there be a leaderboard during the semester?**
No live leaderboard. Run Terminal-Bench locally, track your own progress, and share findings via the Discussion tab. At the deadline, everyone submits a structured submission card with their score — that's the ranking. Judges then deep-review the top ~10. You can also submit independently to the [public Terminal-Bench leaderboard](https://tbench.ai/leaderboard).

**What's the relationship to the upstream Terminal-Bench project?**
We're users and fans — but MLM26 is a separate event. We don't speak for the Terminal-Bench maintainers.

---

## Organizer notes (delete before publishing)

- [ ] Confirm finale reference hardware spec
- [ ] Reach out to Terminal-Bench / Laude Institute about possible coordination (judge from their side?)
- [ ] Cold-start test the quickstart on a machine that didn't write it
- [ ] Recruit judges (Terminal-Bench contributors, agent researchers)
- [ ] Set up Discord
- [ ] Coordinate with Kaggle on Community Hackathon setup
- [ ] Final pass on safety doc with UW research-IT
- [ ] Create Google Form for final submissions
