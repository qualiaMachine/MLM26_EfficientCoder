# Walkthrough: Zero to Terminal-Bench score

This guide walks you through every step — from a fresh machine to a working agent with a real Terminal-Bench score. Every command you need to run is here, in order, with what to expect at each step.

**Time:** ~30 minutes end-to-end (mostly waiting for downloads).  
**What you need:** A computer with 16+ GB RAM, an internet connection, and admin access.

---

## Step 1: Install Docker

Terminal-Bench runs every task inside a fresh Docker container. Your agent never touches your real filesystem — it works inside the container, the container's final state gets graded, and the container is destroyed. Docker makes this possible.

### macOS

Download and install [Docker Desktop for Mac](https://docs.docker.com/desktop/setup/install/mac-install/) (pick Apple Silicon or Intel to match your machine). Launch it — you should see a whale icon in your menu bar.

### Linux (Ubuntu/Debian)

```bash
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
```

**Log out and back in** (or run `newgrp docker`) for the group change to take effect.

### Windows

All challenge work happens inside **WSL2** (Windows Subsystem for Linux), not PowerShell.

```powershell
# In PowerShell as Administrator:
wsl --install
```

Reboot. A terminal may open to finish Ubuntu setup (username + password) — if not, open **"Ubuntu"** from the Start menu to complete it. Then install [Docker Desktop for Windows](https://docs.docker.com/desktop/setup/install/windows-install/) with "Use WSL 2 based engine" checked. In Docker Desktop → Settings → Resources → WSL Integration, enable your Ubuntu distro. **Everything below runs in the Ubuntu terminal** — press the Windows key, type **Ubuntu**, and click the app (or use Windows Terminal's Ubuntu tab).

### Verify Docker works

```bash
docker run hello-world
```

On the first run, Docker downloads the image — expect output like this:

```
Unable to find image 'hello-world:latest' locally
latest: Pulling from library/hello-world
4f55086f7dd0: Pull complete
...
Status: Downloaded newer image for hello-world:latest

Hello from Docker!
This message shows that your installation appears to be working correctly.

To generate this message, Docker took the following steps:
 1. The Docker client contacted the Docker daemon.
 2. The Docker daemon pulled the "hello-world" image from the Docker Hub.
    (amd64)
 3. The Docker daemon created a new container from that image which runs the
    executable that produces the output you are currently reading.
 4. The Docker daemon streamed that output to the Docker client, which sent it
    to your terminal.
...
```

If you see `Hello from Docker!`, Docker is working. The pull step only happens the first time.

If you get "Cannot connect to the Docker daemon" — Docker isn't running. Start Docker Desktop (macOS/Windows) or `sudo systemctl start docker` (Linux). See [docker_setup.md](docker_setup.md) for more troubleshooting.

---

## Step 2: Install uv and Python 3.12

[uv](https://docs.astral.sh/uv/) is a fast Python package manager that can also fetch Python versions for you. Harbor (the Terminal-Bench harness) requires Python 3.12+.

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Close and reopen your terminal (so `uv` is on your PATH), then verify:

```bash
uv --version
```

You should see something like `uv 0.7.x` or newer. You don't need to install Python 3.12 separately — uv handles that in the next step.

---

## Step 3: Clone the repo and install the starter agent

The MLM26 repo contains both the challenge spec and the starter agent code. The agent lives in the `starter/` directory — that's your working directory for the semester.

```bash
git clone https://github.com/qualiaMachine/MLM26.git
cd MLM26/starter
```

Create a virtual environment with Python 3.12 and install everything:

```bash
uv venv --python 3.12
source .venv/bin/activate
uv pip install -e .
```

What just happened:
- `git clone` downloaded the MLM26 repo. The challenge rules and schedule are in `README.md` at the root; the agent code you'll work with is in `starter/`.
- `cd MLM26/starter` puts you in the agent directory — this is where you'll spend your time.
- `uv venv --python 3.12` created a `.venv/` directory with an isolated Python 3.12. If you don't have 3.12, uv downloaded it for you.
- `source .venv/bin/activate` activated the venv. Your prompt should now show `(.venv)` at the start.
- `uv pip install -e .` installed Harbor, the OpenAI client library, and the agent code in editable mode — meaning your edits to `agent/` take effect immediately without reinstalling.

**Verify the install:**

```bash
harbor --version
```

Should print `harbor 0.13.x` or newer. If you get "command not found," your venv isn't activated — run `source .venv/bin/activate`.

---

## Step 4: Verify Harbor + Terminal-Bench with the oracle

Before involving any LLM, confirm that Harbor and Docker are wired up correctly. The **oracle agent** replays each task's known solution — it always gets 100% and needs no model endpoint.

```bash
harbor run -d terminal-bench-sample@2.0 -a oracle
```

This will:
1. Download the 10-task Terminal-Bench sample dataset (first run only, cached after)
2. For each task: build a Docker image, run the oracle inside it, grade the result, destroy the container
3. Print an aggregate score

**Expected output** (abbreviated):

```
Running 10 tasks...
  build-cython-ext          ✓  reward: 1.0
  chess-best-move            ✓  reward: 1.0
  configure-git-webserver    ✓  reward: 1.0
  ...
Aggregate: 10/10 (100.0%)
```

If tasks fail here, the problem is Docker, not your agent. Common issues:
- Docker not running → start it
- Not enough disk space → give Docker ≥30 GB (Docker Desktop → Settings → Resources)
- Network issues pulling images → check your connection, retry

---

## Step 5: Set up a model endpoint

The baseline agent talks to any OpenAI-compatible chat completions endpoint. The easiest option to start is **Ollama** (free, local, works on most machines with a GPU or even CPU-only).

### Install Ollama

Download from [ollama.com/download](https://ollama.com/download) and install.

### Pull a model

```bash
ollama pull qwen2.5-coder:7b
```

This downloads a 7B parameter coding model (~4.5 GB). It's small enough to run on most hardware and good enough to see the agent work. You'll upgrade to larger models later.

> **Model sizes that fit common GPUs:**
> - **No GPU / CPU only:** `qwen2.5-coder:3b` (slow but works)
> - **8 GB VRAM:** `qwen2.5-coder:7b`
> - **16 GB VRAM:** `qwen2.5-coder:14b`
> - **24 GB VRAM:** `qwen2.5-coder:32b-q4_K_M` (quantized to fit)
> - **48+ GB VRAM:** `qwen2.5-coder:32b` at fp16, or 70B quantized

### Verify the endpoint

Ollama runs a server automatically. Test it:

```bash
curl http://localhost:11434/v1/models
```

You should see a JSON response listing your pulled model(s). If you get "connection refused," start the server with `ollama serve`.

### Configure the agent

```bash
cp .env.example .env
```

The defaults in `.env.example` already point at Ollama with `qwen2.5-coder:32b`. Edit `.env` to match the model you actually pulled:

```bash
# .env
LLM_BASE_URL=http://localhost:11434/v1
LLM_MODEL=qwen2.5-coder:7b
LLM_API_KEY=ollama
```

---

## Step 6: Run the baseline agent on one task

```bash
harbor run -d terminal-bench-sample@2.0 \
  --agent-import-path agent.agent:MLMBaselineAgent \
  -i build-cython-ext
```

Breaking down the flags:
- `-d terminal-bench-sample@2.0` — use the 10-task sample dataset
- `--agent-import-path agent.agent:MLMBaselineAgent` — run your agent (from `agent/agent.py`, the `MLMBaselineAgent` class)
- `-i build-cython-ext` — include only this one task (without `-i`, it runs all 10)

**What you'll see** (the interesting part):

```
[agent] turn 1: cat /task/instruction.md
[agent] turn 2: ls -la /task/
[agent] turn 3: cat setup.py
[agent] turn 4: python setup.py build_ext --inplace
[agent] turn 5: pytest tests/ -v
...
build-cython-ext    ✓  reward: 1.0    (or ✗  reward: 0.0)
```

The agent reads the task instruction, explores the container, attempts to solve the task with shell commands, and either passes or fails the test suite.

**Don't panic if it fails.** The baseline with a 7B model will fail most tasks — that's the point. Your job over the semester is to make it better.

### Where results go

Results are saved to `./jobs/<job-name>/`. Each trial has a `result.json`:

```bash
# Find the latest job
ls -t jobs/ | head -1

# Check the result
cat jobs/<job-name>/terminal-bench-sample__build-cython-ext/*/result.json | python3 -m json.tool
```

Key fields in `result.json`:
- `reward` — the score (1.0 = pass, 0.0 = fail)
- `agent_info` — your agent name and version
- `started_at` / `finished_at` — timing for each phase
- `exception` — what went wrong, if anything

---

## Step 7: Run the full sample set

Now run all 10 tasks:

```bash
harbor run -d terminal-bench-sample@2.0 \
  --agent-import-path agent.agent:MLMBaselineAgent
```

Or use the convenience script:

```bash
./scripts/run_baseline.sh
```

This takes longer (10 tasks × ~5 min max each). At the end you'll get an aggregate score — this is the number that matters.

**To run tasks in parallel** (if you have enough RAM — each task is a Docker container plus your model server):

```bash
harbor run -d terminal-bench-sample@2.0 \
  --agent-import-path agent.agent:MLMBaselineAgent \
  -n 2
```

`-n 2` runs 2 tasks concurrently. Start low, watch your RAM, then increase.

---

## Step 8: Run the MLM26 public subset (the real score)

The sample set is just 10 tasks for setup verification. The MLM26 public subset is what you self-report on the leaderboard. Once it's announced at kickoff (task names go in `eval/public_subset.txt`), run:

```bash
./scripts/run_subset.sh
```

This reads the task names from `eval/public_subset.txt` and runs your agent against each one from the full Terminal-Bench 2.0 dataset. The aggregate score at the end is what you post to the Kaggle leaderboard thread.

---

## Step 9: Understand what you're improving

Open `agent/agent.py` and read it — it's short. Here's the flow:

```
┌─────────────────────────────────────────────────────┐
│  Harbor calls your agent's run() method with:       │
│    • instruction (the task description)             │
│    • environment (the Docker container interface)   │
│    • context (where you report token usage)         │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
              ┌─── AGENT LOOP ───┐
              │                  │
              │  1. Send conversation to LLM          │
              │     (system prompt + history)          │
              │                                       │
              │  2. Parse response:                    │
              │     ```bash              → execute it  │
              │     TASK_COMPLETE        → stop        │
              │     anything else        → nudge       │
              │                                       │
              │  3. Run command in container via       │
              │     environment.exec(command=...)      │
              │                                       │
              │  4. Append output to conversation      │
              │                                       │
              │  5. Repeat (max 100 turns)             │
              └───────────────────────────────────────┘
```

The four files you'll modify:

| File | What it does | Improvement ideas |
|---|---|---|
| `agent/agent.py` | The main loop | Planning steps, context window management, early stopping, multi-stage pipelines |
| `agent/prompts.py` | System prompt + message templates | Task-type detection, output format constraints, self-verification instructions |
| `agent/tools.py` | Parses model output → actions, runs commands | Richer tool set (read file, write file as first-class actions), smarter truncation |
| `agent/llm.py` | Talks to the model endpoint | Retry logic, streaming, token counting, model routing |

---

## Step 10: Make a change and see the effect

Let's do one concrete improvement so you see the development loop.

The baseline's system prompt (`agent/prompts.py`) doesn't tell the agent to read the task instruction first. Let's fix that:

Open `agent/prompts.py` and add to the top of `SYSTEM_PROMPT`, after the first paragraph:

```python
SYSTEM_PROMPT = """\
You are an autonomous software engineering agent working inside a Linux \
container. You are given a task to complete. You cannot ask questions — \
work with what you have.

STRATEGY:
1. First, carefully read any instruction or README files to understand \
the full task before acting.
2. Explore the relevant files and directory structure.
3. Form a plan, then execute it step by step.
4. After each significant change, verify it works before moving on.
5. Run the relevant tests before declaring done.

RULES:
...
```

Now re-run the same task:

```bash
harbor run -d terminal-bench-sample@2.0 \
  --agent-import-path agent.agent:MLMBaselineAgent \
  -i build-cython-ext
```

Because you used `uv pip install -e .` (editable install), your change is live immediately — no reinstall. Compare the agent's behavior in the logs: does it explore more methodically? Does it run tests before finishing?

This is the development loop for the semester:
1. **Hypothesize** — "the agent fails because it doesn't read the instructions first"
2. **Change** — modify prompts, tools, or the loop
3. **Test** — run against a task (or the full subset)
4. **Measure** — compare scores and failure modes
5. **Repeat**

---

## Quick reference

| What you want to do | Command |
|---|---|
| Verify Docker works | `docker run hello-world` |
| Verify Harbor works | `harbor run -d terminal-bench-sample@2.0 -a oracle` |
| Run your agent on one task | `harbor run -d terminal-bench-sample@2.0 --agent-import-path agent.agent:MLMBaselineAgent -i <task-name>` |
| Run your agent on all sample tasks | `./scripts/run_baseline.sh` |
| Run the MLM26 public subset | `./scripts/run_subset.sh` |
| Run tasks in parallel | Add `-n 4` (or however many your RAM supports) |
| Use a specific model | Add `-m ollama/qwen2.5-coder:32b` or set `LLM_MODEL` in `.env` |
| See available tasks | `harbor datasets list` |
| See available built-in agents | `harbor run --help` |
| Check latest results | `ls -t jobs/ \| head -1` then inspect `result.json` inside |
| Submit to the TB leaderboard | See [harbor.md](harbor.md#submitting-to-the-public-terminal-bench-leaderboard) |

---

## What's next

- **Week 1:** Get this walkthrough done. Have a working baseline with a score.
- **Week 2:** Run the full public subset. Record your baseline score.
- **Week 3:** Classify *where* and *why* your agent fails. That failure taxonomy is your roadmap for the rest of the semester.

Full challenge schedule, rules, and judging criteria: [MLM26 README](../../README.md).
