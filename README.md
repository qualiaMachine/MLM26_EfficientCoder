# MLM26: Local Coding Agent Challenge

A Machine Learning Marathon track for building the best local coding agent — measured on Terminal-Bench. Hosted by ML+X at UW–Madison.

September–December 2026. Two tracks. Real prizes. Open to anyone.

---

## Why this challenge

Frontier coding assistants like Claude Code, Cursor, and Aider assume an API call to a frontier model. They are excellent. They also send your code to a third party, cost real money per task, and raise security concerns when the data can't leave your environment.

A growing class of users — researchers with sensitive data, organizations on tight compute budgets — needs coding agents that run locally. Open-weight models have closed enough of the gap that this is plausible. But "plausible" and "actually good" are different things, and nobody has run a competition of what the best *local* coding agent looks like under realistic constraints.

In this year's premiere MLM26 challenge, teams will compete to build the best local coding agent possible within a defined compute budget, or extend the evaluation methodology that tells us what "best" means.

The outputs of this competition feed directly into how we deploy AI for researchers.

### Why Terminal-Bench

We're not building a new benchmark from scratch. [Terminal-Bench](https://tbench.ai) is the industry-standard benchmark for evaluating coding agents in terminal environments — joint work from Stanford, the Laude Institute, Anthropic, Snorkel, and many others (including UW–Madison contributors). It's open source, it has an active leaderboard, and it's the same yardstick used to evaluate Claude Code, Codex, Devin, Cursor, and friends. [Harbor](https://www.harborframework.com/) is the official harness for running Terminal-Bench 2.0.

By building on Terminal-Bench, your work is comparable to public leaderboard entries from day one, and strong submissions have a post-MLM life as contributions to a benchmark the field actually cares about.

---

## At a glance

- **Format:** Kaggle Community Hackathon, semester-long, two tracks
- **Dates:** Kickoff September 2026 → Finale December 2026
- **Sprints:** Wednesdays 4:30–6:30 pm (Madison time, hybrid)
- **Eval backbone:** Terminal-Bench 2.0 via [Harbor](https://www.harborframework.com/) (Docker-per-task, outcome-based scoring)
- **Hardware constraint:** Single GPU ≤96 GB VRAM
- **Per-task budget:** ≤100 turns (Terminal-Bench default), ≤5 minutes wall-clock
- **Models:** Open weights only. Bring-your-own endpoint (Ollama, vLLM, hosted open-weight API). RunAI-hosted endpoints available on request for UW participants.
- **Submission:** Kaggle Writeup + video demo + public repo link
- **Prizes:** TBD (sponsor pool, capped at Kaggle's $10K limit)

---

## Tracks

You pick one track at registration. You can switch once, before the Week 6 mid-checkpoint.

### Track A — Best Local Coding Agent

Build a coding agent that scores highest on a held-out Terminal-Bench subset under local-model constraints. ≤96 GB VRAM on a single GPU, open-weight models only, capped per-task budget. Within those limits, anything goes — your choice of base model, scaffolding, retrieval, tool design, prompting, quantization, agent loop, fine-tuning.

Submissions are scored on a held-out subset of Terminal-Bench tasks revealed at the finale. Local MLM26 participants must also submit a writeup explaining what they built and why.

**This track suits you if:** you like building systems, you enjoy prompt engineering and agent design, you want to climb a leaderboard the field watches.

### Track B — Extending the Evaluation

Terminal-Bench is the starting point, not the endpoint. This track is about extending, critiquing, or specializing it. Examples of what a strong Track B submission could be:

- A curated subset of Terminal-Bench tasks specifically suited to local-model evaluation (e.g., tasks where local agents currently fail, or tasks where compute budget matters)
- New Terminal-Bench-format tasks contributed back to the project (data science, notebook-shaped workflows, scientific computing, whatever you think is under-represented)
- An analysis of *which* Terminal-Bench tasks discriminate between local and frontier models, and why
- A methodology for measuring something Terminal-Bench doesn't — agent latency, cost per task, robustness to prompt variation, failure mode taxonomy
- A new harness feature or task type that the Terminal-Bench maintainers might accept upstream

Submissions are judged on rigor, reusability, and what they reveal about local coding agents. Strong submissions become ML+X-maintained artifacts and ideally upstream contributions.

**This track suits you if:** you care about measurement, you've thought about why benchmarks are hard, you'd rather build the ruler than the thing being measured.

---

## Constraints (Track A)

These exist to make this a *local* coding agent competition rather than "whoever brought the biggest GPU." If they're too tight for what you want to build, the answer is probably Track B.

### Hardware

- **Single GPU with ≤96 GB VRAM.** Verified at finale on reference hardware (e.g. A100-80GB, H100).
- **Quantization allowed.** fp16, int8, int4, AWQ, GGUF — we only care that it fits.
- **Dense or MoE both fine.** As long as it fits in the VRAM budget.
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

Twelve sprint weeks plus kickoff and finale.

**Phase 1 — Foundations (Weeks 1–3)**

- **Week 1 — Kickoff & team formation.** Challenge brief, Terminal-Bench walkthrough, **live Docker + Harbor setup workshop** (bring your laptop — this is the #1 place people get stuck), baseline demo, endpoint setup. Teams form by end of week.
- **Week 2 — Baseline replication.** Get the reference agent running. Score it against a public Terminal-Bench subset. Deliverable: working baseline with score.
- **Week 3 — Failure analysis.** Classify where your baseline fails on Terminal-Bench tasks. Deliverable: failure taxonomy writeup.

**Phase 2 — Build (Weeks 4–8)**

- **Week 4 — Architecture commit.** 5-min team pitch on your approach.
- **Week 5 — First working version.** Demo your agent solving a task end-to-end.
- **Week 6 — Mid-semester checkpoint.** Extended session. Post writeup draft to Kaggle gallery, demo to full room, structured peer feedback. **Most important week.**
- **Week 7 — Iteration sprint.** No big demo. Just build.
- **Week 8 — Generalization test.** Run against a fresh Terminal-Bench subset you haven't seen. Self-report scores. Catches overfitting.

**Phase 3 — Polish & Finale (Weeks 9–12)**

- **Week 9 — Writeup draft.** Full draft posted to Kaggle.
- **Week 10 — Peer review.** Teams review each other's writeups. Optional outside reviewers from the Terminal-Bench community.
- **Week 11 — Final polish + dry run.** Rehearse finale demo.
- **Week 12 — Finale.** Public event. Held-out task set scored live. Per-track judging. Awards. Gallery goes live.

**Red team exercise** runs between Weeks 2 and 3: a deliberately misbehaving sample agent that participants analyze for safety issues. Builds the right reflexes early.

---

## Submission format

Same shape for both tracks. Modeled on Kaggle's community hackathon format.

1. **Kaggle Writeup.** Public, in your team's name. Problem framing, approach, what worked, what didn't, Terminal-Bench scores, limitations, what you'd do with another month. Markdown. Quality > length.
2. **Video demo.** 5–8 minutes. Show the agent working (or your methodology in action). Voiceover. Clear > polished.
3. **Public repo.** GitHub link with code, README, reproduction instructions. License: MIT or Apache 2.0.

For Track A, the repo must include a Terminal-Bench-compatible agent in a runnable state. For Track B, the repo must include the extension/methodology in a state someone else could pick up and use — ideally as a PR-ready contribution to Terminal-Bench.

---

## Judging

### Track A rubric

- **Terminal-Bench score (45%)** — Performance on the held-out finale subset.
- **Engineering depth (20%)** — Is the work technically substantive? Does the writeup show real understanding of the tradeoffs?
- **Reproducibility (15%)** — Can someone else run this? Are the constraints actually respected? Does it fit in the VRAM budget?
- **Clarity & presentation (20%)** — Writeup and demo quality.

### Track B rubric

- **Rigor (35%)** — Is the methodology sound? Are claims supported? Are the new tasks well-designed?
- **Reusability (30%)** — Could the Terminal-Bench maintainers accept this? Could another lab pick it up? Documentation, license, code quality.
- **Insight (20%)** — Does the work reveal something useful about the state of local coding agents?
- **Clarity & presentation (15%)** — Writeup and demo quality.

Judging panel includes ML+X organizers plus invited reviewers — we're aiming for at least one reviewer from the Terminal-Bench community.

---

## Getting started

This section is your fast path from "I registered" to "I have a working baseline scoring on Terminal-Bench."

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
   Reboot when prompted. This installs Ubuntu by default.
2. Install [Docker Desktop for Windows](https://docs.docker.com/desktop/setup/install/windows-install/). During setup, ensure **"Use WSL 2 based engine"** is checked.
3. In Docker Desktop → Settings → Resources → WSL Integration, enable integration for your Ubuntu distro.
4. Open the Ubuntu terminal (search "Ubuntu" in the Start menu) and verify:
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

**1. Install uv** (if you don't have it):

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**2. Clone and set up your environment:**

```bash
git clone https://github.com/mlplusx/mlm26-coding-agent-starter.git
cd mlm26-coding-agent-starter

# Create a virtual environment (best practice: one venv per project)
uv venv --python 3.12              # creates .venv/; uv fetches Python 3.12 if missing
source .venv/bin/activate          # activate it (on Windows/WSL2 same command)
uv pip install -e .                # installs harbor + the agent package (editable)
```

**3. Verify Harbor + Terminal-Bench works** by running the oracle agent against the 10-task sample set (the oracle replays each task's known solution — it confirms your Docker/Harbor setup without needing a model):

```bash
harbor run -d terminal-bench-sample@2.0 -a oracle
```

**4. Run the baseline agent** against a single sample task:

```bash
cp .env.example .env               # set LLM_BASE_URL, LLM_MODEL, LLM_API_KEY
./scripts/run_baseline.sh build-cython-ext
```

You should see the baseline agent receive a task instruction, work inside a fresh Docker container, and have its result graded by the task's test suite. Results land in `jobs/`. If you get something different, see `docs/troubleshooting.md`.

### What's in the starter repo

```
mlm26-coding-agent-starter/
├── agent/
│   ├── agent.py            # MLMBaselineAgent (Harbor BaseAgent) — main loop, read it
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
├── pyproject.toml          # `uv pip install -e .` makes the agent importable by Harbor
└── README.md
```

The agent code is *yours to modify*. Harbor handles container lifecycle, scoring, and result aggregation — you focus on the agent logic in `agent/agent.py`, which implements Harbor's `BaseAgent` interface.

### How agents plug into Harbor

Harbor supports custom agents without modifying Harbor itself. Two integration styles:

1. **External agents** — implement Harbor's `BaseAgent` interface (`name`, `version`, `setup`, `run`). Your agent runs on your machine and drives the task container through Harbor's `BaseEnvironment` interface (executing bash via `exec`). **The starter baseline is an external agent** — it's the simplest place to start.
2. **Installed agents** — implement `BaseInstalledAgent`. Your agent is installed *into* the task container and runs headless inside it. More setup, but lets you bring custom tools into the environment. Worth considering once your agent matures.

Either way, you run it the same way:

```bash
harbor run -d terminal-bench@2.0 --agent-import-path agent.agent:MLMBaselineAgent
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

### Red team week (between Weeks 2 and 3)

We'll release a deliberately misbehaving sample agent. Your job: figure out what it does wrong, what damage it could do in a less-sandboxed environment, and how the Terminal-Bench harness prevents most of it. Writeup due before Week 3.

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
  --agent-import-path agent.agent:MLMBaselineAgent
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

- **Qwen2.5-Coder 32B / Qwen3-Coder** variants — strong coding baselines, fit in 24 GB at 4-bit
- **DeepSeek-Coder V2** family — strong on harder tasks
- **GLM-4.5** — recent, well-regarded for agent work
- **Llama 3.3 70B** — fits comfortably at fp16 with 96 GB, or 4-bit on smaller cards
- **Mixtral-style MoEs** — high active-to-total ratio, useful when total params aren't the constraint

A 32B-class Qwen-Coder agent has already cracked the Terminal-Bench leaderboard above some larger MoE setups — careful agent design matters more than parameter count.

---

## Task sets

Track A is scored against Terminal-Bench tasks. We use the framework directly, with three subsets:

### Public set — used for self-evaluation

A subset of public Terminal-Bench tasks (the easy and medium tiers, mostly). Participants run against this all semester. Scores are self-reported. Use it to debug your agent and track your own progress.

### Generalization set (Week 8)

A different public Terminal-Bench subset, not announced at kickoff. Released Week 8. Tests whether you overfit to the public set.

### Held-out finale set (Week 12)

A small curated set of Terminal-Bench tasks — possibly including new tasks contributed by Track B submissions, possibly including unreleased upstream tasks (subject to permission). Revealed and scored at the finale. This is the main Track A number.

---

## Communication

- **Kaggle forum** — async questions, public discussion
- **Discord** — informal, real-time, drop-in office hours
- **Weekly Wednesday sprints** — hybrid, recorded
- **Office hours** — TBD, posted in Discord
- **Terminal-Bench Discord** — separate, upstream community. Worth joining if you're serious about Track B.

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

**My team is just me.** / **My team is six people.**
Both fine. Reflect honestly on contribution in the writeup.

**I don't have a GPU.**
Hosted open-weight APIs are cheap for development. Reference hardware at the finale is provided. UW participants can request RunAI access.

**I'm not at UW.**
Welcome. The challenge is open. Sprints are hybrid. Prizes don't care.

**Will Track A get an automated leaderboard during the semester?**
Self-reported scores against the public set are submitted via the Kaggle hackathon page. Scores are honor-system during the semester; verification happens at the Week 8 generalization checkpoint and the Week 12 finale when organizers run agents on reference hardware. You can also submit to the public Terminal-Bench leaderboard independently.

**What's the relationship to the upstream Terminal-Bench project?**
We're users, contributors, and (hopefully) collaborators — but MLM26 is a separate event. We don't speak for the Terminal-Bench maintainers. Strong Track B submissions may be proposed upstream, subject to their review.

---

## Organizer notes (delete before publishing)

- [ ] Confirm prize pool with sponsors
- [ ] Confirm finale reference hardware spec
- [ ] Identify the UW–Madison contributor(s) to Terminal-Bench 2.0; reach out for collaboration
- [ ] Reach out to Terminal-Bench / Laude Institute about possible coordination (finale judge from their side? early heads-up on upstream tasks?)
- [ ] Build the starter repo (`mlplusx/mlm26-coding-agent-starter`) — scaffold drafted in `starter/` in this repo; split it out, set the real public-subset task list in `eval/public_subset.txt`, and cold-start test before publishing
- [ ] Cold-start test the quickstart on a machine that didn't write it
- [ ] Build the red team sample agent
- [ ] Recruit Track B-relevant judges (eval methodology folks, Terminal-Bench contributors)
- [ ] Set up Discord
- [ ] Coordinate with Kaggle on Community Hackathon setup
- [ ] Final pass on safety doc with UW research-IT
- [ ] Decide finale held-out task selection process — entirely public TB tasks, or include some Track B contributions, or some upstream-unreleased tasks?

Open questions:

- Do we want a "beginner track" or scaffolding for first-time agent builders? Could be done via paired teams or a workshop in Week 1, rather than a third track.
- How do we handle teams that want to share infrastructure (shared model endpoint)? Probably fine if disclosed.
- Outside reviewers for the finale — who? Terminal-Bench team is the obvious ask. Ludwig Schmidt? Anthropic contacts? NVIDIA?
