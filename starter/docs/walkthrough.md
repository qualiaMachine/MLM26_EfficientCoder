# Walkthrough: Zero to Terminal-Bench score

This guide walks you through every step — from a fresh machine to a working agent with a real Terminal-Bench score. Every command you need to run is here, in order, with what to expect at each step.

**Time:** ~30 minutes end-to-end (mostly waiting for downloads).  
**What you need:** A computer with 16+ GB RAM, an internet connection, and admin access.

---

## Step 1: Install Docker

Terminal-Bench runs every task inside a fresh Docker container. Your agent never touches your real filesystem — it works inside the container, the container's final state gets graded, and the container is destroyed. Docker makes this possible.

> **Remember what you're building: an agent that runs arbitrary shell commands.** Inside `harbor run` the container is your protection. The moment you test agent code *outside* Harbor — pointing your loop at a local shell "just to see" — it has whatever access you have, and it will eventually try something destructive. Read [safety.md](safety.md) before you do that.

### macOS

Download and install [Docker Desktop for Mac](https://docs.docker.com/desktop/setup/install/mac-install/) (pick Apple Silicon or Intel to match your machine). Launch it — you should see a whale icon in your menu bar, and it must be running whenever you use Harbor. Homebrew alternative: `brew install --cask docker`, then launch Docker from Applications once.

### Linux (Ubuntu/Debian)

```bash
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
```

**Log out and back in** (or run `newgrp docker`) for the group change to take effect. Other distros: see the [Docker Engine install docs](https://docs.docker.com/engine/install/).

### Windows

All challenge work happens inside **WSL2** (Windows Subsystem for Linux), not PowerShell.

```powershell
# In PowerShell as Administrator:
wsl --install
```

Reboot. A terminal may open to finish Ubuntu setup (username + password) — if not, open **"Ubuntu"** from the Start menu to complete it. Then install [Docker Desktop for Windows](https://docs.docker.com/desktop/setup/install/windows-install/) with "Use WSL 2 based engine" checked. In Docker Desktop → Settings → Resources → WSL Integration, enable your Ubuntu distro. **Everything below runs in the Ubuntu terminal** — press the Windows key, type **Ubuntu**, and click the app (or use Windows Terminal's Ubuntu tab). Keep the repo inside the WSL2 filesystem (`~/...`), not `/mnt/c/...` — it's dramatically faster.

### Verify Docker works

On macOS and Windows, **Docker Desktop must be open and running** for this to work (look for the whale icon in your menu bar / system tray) — the daemon only runs while the app does. On Linux the service runs in the background automatically.

```bash
docker run hello-world
```

Expected output:

```
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

To try something more ambitious, you can run an Ubuntu container with:
 $ docker run -it ubuntu bash

Share images, automate workflows, and more with a free Docker ID:
 https://hub.docker.com/

For more examples and ideas, visit:
 https://docs.docker.com/get-started/
```

If you see `Hello from Docker!`, Docker is working. (On the very first run you'll also see a few image-download lines above this — that's normal.)

If you get "Cannot connect to the Docker daemon" — Docker isn't running. Start Docker Desktop (macOS/Windows) or `sudo systemctl start docker` (Linux). More Docker failures are covered in [troubleshooting.md](troubleshooting.md).

---

## Step 2: Install uv and Python 3.12

[uv](https://docs.astral.sh/uv/) is a fast Python package manager that can also fetch Python versions for you. Harbor (the Terminal-Bench evaluation framework) requires Python 3.12+.

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc   # reload your shell so uv is on your PATH
```

Verify it works:

```bash
uv --version
```

You should see something like `uv 0.7.x` or newer. You don't need to install Python 3.12 separately — uv handles that in the next step.

---

## Step 3: Clone the repo and install the starter agent

This repo contains both the challenge spec and the starter agent code. The agent lives in the `starter/` directory. The virtual environment lives at the repo root so it's shared across everything.

```bash
git clone https://github.com/qualiaMachine/MLM26_EfficientCoder.git
cd MLM26_EfficientCoder
```

Create a virtual environment with Python 3.12 and install everything:

```bash
uv venv --python 3.12
source .venv/bin/activate
uv pip install -e starter/
```

What just happened:
- `git clone` downloaded the challenge repo. The challenge rules and schedule are in `README.md` at the root; the agent code you'll work with is in `starter/`.
- `cd MLM26_EfficientCoder` puts you at the repo root — the venv lives here.
- `uv venv --python 3.12` created a `.venv/` directory with an isolated Python 3.12. If you don't have 3.12, uv downloaded it for you.
- `source .venv/bin/activate` activated the venv. Your prompt should now show `(.venv)` at the start.
- `uv pip install -e starter/` installed Harbor, the OpenAI client library, and the agent code in editable mode — meaning your edits to `starter/agent/` take effect immediately without reinstalling.

**Verify the install:**

```bash
harbor --version
```

Should print `harbor 0.13.x` or newer. If you get "command not found," your venv isn't activated — run `source .venv/bin/activate`.

---

## Step 4: Verify Harbor + Terminal-Bench with the oracle

Before involving any LLM, confirm that Harbor and Docker are wired up correctly — using the **oracle agent**. Every Terminal-Bench task ships with a reference solution (the exact shell commands that solve it, written by the task's author). The oracle is a built-in agent that ignores any model and simply replays that reference solution. It should therefore score 100% every time: there's no intelligence involved, so a perfect score proves your Docker + Harbor + grading pipeline works, and any failure here is an environment problem, not an agent problem.

```bash
harbor run -d terminal-bench-sample@2.0 -a oracle
```

`harbor run` is the command you'll use for every evaluation: it takes a dataset of tasks (`-d`) and an agent — here the built-in oracle (`-a oracle`); later your own code (`--agent-import-path`) — then runs the agent against each task in its own container, grades the final state, and writes results to `./jobs/`.

This particular run will:
1. Download the 10-task Terminal-Bench sample dataset (first run only, cached after)
2. For each task: build the task's Docker image, replay the reference solution inside it (that's the oracle), grade the container's final state, destroy the container
3. Print an aggregate score

**Expected output:**

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
Results written to jobs/<date>__<time>/result.json
```

If you see `Mean: 1.000` with 0 exceptions, everything works.

If tasks fail here, the problem is Docker, not your agent. Common issues:
- Docker not running → start it
- Not enough disk space → give Docker ≥30 GB (Docker Desktop → Settings → Resources)
- Network issues pulling images → check your connection, retry

---

## Step 5: Set up a model endpoint

The baseline agent talks to any OpenAI-compatible chat completions endpoint.

> **UW–Madison participant with a kickoff-email API key?** Skip Ollama entirely — the provided `Qwen3.6-27B-FP8` endpoint needs no GPU. Copy `.env.example` to `.env`, uncomment the "Provided endpoint" block, paste your key, and jump to [Verify the endpoint](#verify-the-endpoint). Full details in [byo_model.md](byo_model.md).

Otherwise, the easiest option to start is **Ollama** (free, local, works on most machines with a GPU or even CPU-only). If you haven't used it: Ollama is an app that downloads open-weight models and runs them on your own machine, exposing them through a local HTTP endpoint that speaks the same API as the big hosted providers. Your agent sends chat requests to `localhost` instead of a cloud service — no account, no API costs, and nothing leaves your machine.

**Why an endpoint instead of loading the weights in your own code?** You *could* load the model directly in Python (e.g., with `transformers`), but then the model lives inside your agent process: every agent restart reloads gigabytes of weights, and your code gets tied to one inference library. Serving it behind an endpoint separates the two — the model loads once and stays resident, while your agent is just an HTTP client you can edit and rerun instantly. This matters for Harbor specifically: `harbor run -n 4` runs four tasks concurrently, and all four agent instances share the one model server instead of each loading its own copy. It's also what makes your submission portable — the starter's `agent/llm.py` speaks this API, so switching from Ollama on your laptop to a hosted endpoint (or the setup organizers use to re-run the top 5) is a `.env` change, not a code change.

### Install Ollama

Download from [ollama.com/download](https://ollama.com/download) and install.

### Pull a model

```bash
ollama pull qwen2.5-coder:14b
```

This downloads a 14B parameter coding model (~9 GB). It's the recommended starting point — large enough to reason through most easy/medium tasks, small enough to run on 16+ GB VRAM. The 7B works too but expect most tasks to fail due to limited reasoning capacity.

> **Model sizes that fit common GPUs** (dev is unrestricted; the submitted run must use an approved model from the [challenge README](../../README.md#approved-models)):
> - **No GPU / CPU only:** `qwen2.5-coder:7b` (slow on CPU, but works)
> - **8 GB VRAM:** `qwen2.5-coder:7b` (counts as the approved 7B AWQ row)
> - **16+ GB VRAM:** `qwen2.5-coder:14b` (recommended starting point; approved 14B AWQ row)
> - **24+ GB VRAM:** `qwen2.5-coder:32b` (~20 GB; approved 32B AWQ row) or `qwen3-coder:30b`
> - **48+ GB VRAM:** the anchor `Qwen3.6-27B-FP8` under vLLM

### Verify the endpoint

Ollama runs a server automatically. Test it:

```bash
curl http://localhost:11434/v1/models
```

You should see a JSON response listing your pulled model(s). If you get "connection refused," start the server with `ollama serve`.

Using the provided UW–Madison endpoint instead? Same check, with your key:

```bash
curl https://qwen36-27b-vllm-runai-shared-models.deepthought.doit.wisc.edu/v1/models \
  -H "Authorization: Bearer $LLM_API_KEY"
```

The model id it returns (`/mnt/shared-models/qwen3.6-27B-fp8`) is exactly what goes in `LLM_MODEL`.

### Configure the agent

```bash
cp .env.example .env
```

The defaults in `.env.example` already point at Ollama with `qwen2.5-coder:14b`. Edit `.env` if you pulled a different model:

```bash
# .env
LLM_BASE_URL=http://localhost:11434/v1
LLM_MODEL=qwen2.5-coder:14b
LLM_API_KEY=ollama
```

---

## Step 6: Run the baseline agent on one task

```bash
harbor run -d terminal-bench-sample@2.0 \
  --agent-import-path agent.agent:BaselineAgent \
  -i build-cython-ext
```

Breaking down the flags:
- `-d terminal-bench-sample@2.0` — use the 10-task sample dataset
- `--agent-import-path agent.agent:BaselineAgent` — run your agent (from `agent/agent.py`, the `BaselineAgent` class)
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

**Don't panic if it fails.** The baseline with a 7B model will fail most tasks — that's expected. Your job over the competition is to make it better.

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
  --agent-import-path agent.agent:BaselineAgent
```

Or use the convenience script:

```bash
./scripts/run_baseline.sh
```

This takes longer (10 tasks × ~5 min max each). At the end you'll get an aggregate score — this is the number that matters.

**To run tasks in parallel** (if you have enough RAM — each task is a Docker container plus your model server):

```bash
harbor run -d terminal-bench-sample@2.0 \
  --agent-import-path agent.agent:BaselineAgent \
  -n 2
```

`-n 2` runs 2 tasks concurrently. Start low, watch your RAM, then increase.

---

## Step 8: Run the public subset (the real score)

The sample set is just 10 tasks for setup verification. The public subset is what you self-report on the leaderboard. Once it's announced in the Kaggle Discussion tab (task names go in `eval/public_subset.txt`), run:

```bash
./scripts/run_subset.sh
```

This reads the task names from `eval/public_subset.txt` and runs your agent against each one from the full Terminal-Bench 2.0 dataset. The aggregate score at the end is what you post in the Kaggle Discussion tab (the live leaderboard is for full 89-task runs).

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
  --agent-import-path agent.agent:BaselineAgent \
  -i build-cython-ext
```

Because you used `uv pip install -e starter/` (editable install), your change is live immediately — no reinstall. Compare the agent's behavior in the logs: does it explore more methodically? Does it run tests before finishing?

This is the development loop for the competition:
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
| Run your agent on one task | `harbor run -d terminal-bench-sample@2.0 --agent-import-path agent.agent:BaselineAgent -i <task-name>` |
| Run your agent on all sample tasks | `./scripts/run_baseline.sh` |
| Run the public subset | `./scripts/run_subset.sh` |
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
- **Week 3:** Classify *where* and *why* your agent fails. That failure taxonomy is your roadmap for the rest of the competition.

Full challenge schedule, rules, and judging criteria: [challenge README](../../README.md).
