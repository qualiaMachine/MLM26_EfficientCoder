# MLM26 Coding Agent Starter

The fast path from "I registered" to "my agent has a Terminal-Bench score." This directory gives you a minimal working agent (~200 lines) wired into [Harbor](https://www.harborframework.com/), the official Terminal-Bench 2.0 harness. Your job is to make it better.

Challenge brief, rules, schedule, and judging: see the [MLM26 README](../README.md).

## Setup (15 minutes, once)

**0. Docker.** Required — Terminal-Bench runs every task in a Docker container. Follow [docs/docker_setup.md](docs/docker_setup.md) for your OS, then confirm `docker run hello-world` works.

**1. Install [uv](https://docs.astral.sh/uv/)** (fast Python package manager):

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**2. Clone, create a venv, install:**

```bash
git clone git@github.com:qualiaMachine/MLM26.git
cd MLM26

uv venv --python 3.12              # Harbor needs Python 3.12+; uv fetches it if missing
source .venv/bin/activate
uv pip install -e starter/         # installs harbor + this agent package (editable)
```

> Best practice: one venv per project, always activated when you work. The venv lives at the repo root; the agent code lives in `starter/`. If `harbor` is "not found" later, you forgot to activate. The `-e` (editable) install means your edits to `starter/agent/` take effect immediately — no reinstall needed. It also makes your agent importable by Harbor's `--agent-import-path`.

**3. Verify the harness** (no model needed — the oracle replays each task's known solution):

```bash
harbor run -d terminal-bench-sample@2.0 -a oracle
```

If this scores ~100%, Docker + Harbor work. If not: [docs/troubleshooting.md](docs/troubleshooting.md).

**4. Point at a model.** Easiest is [Ollama](https://ollama.com/download); all options in [docs/byo_model.md](docs/byo_model.md):

```bash
cp .env.example .env               # set LLM_BASE_URL, LLM_MODEL, LLM_API_KEY
```

**5. Run the baseline on one task:**

```bash
./scripts/run_baseline.sh build-cython-ext
```

Watch the logs: instruction in, commands out, verdict at the end. Results land in `./jobs/`.

## The weekly loop

```bash
./scripts/run_subset.sh            # run the official MLM26 public subset
```

Then self-report on the Kaggle leaderboard thread:

1. **Score** — the aggregate printed at the end of the run
2. **Command + job name** — what you ran, and the `jobs/<job-name>` it produced
3. **Setup** — model, quantization, hardware

Keep your `jobs/` directories — organizers verify self-reported scores at the Week 8 generalization checkpoint and the Week 12 finale by re-running your agent.

## Making it yours

Read `agent/agent.py` first — it's short on purpose. The loop is: instruction → ask LLM → parse one bash block → execute in container → feed output back → repeat until `TASK_COMPLETE` or budget exhausted.

Where points hide, roughly in order of effort:

- **`prompts.py`** — better instructions, task-type hints, output discipline
- **Context management** — the conversation grows every turn; what do you keep, summarize, drop?
- **Error recovery** — what happens after a failed command? The baseline just shows the error and hopes
- **Planning / self-critique** — separate plan and act steps; verify before declaring done
- **Model choice + quantization** — see [docs/byo_model.md](docs/byo_model.md); fit and speed matter as much as smarts
- **Architecture** — multi-stage pipelines, retrieval, ensembles, fine-tuning, or go [installed-agent](docs/harbor.md#writing-your-own-agent) and bring custom tools

Constraints that always apply (full rules in the [challenge README](../README.md)): single GPU ≤48 GB VRAM, open weights only, ≤100 turns and ≤5 min per task, no closed-weight API calls anywhere in your system. The suggested anchor model is Qwen2.5-Coder-32B-Instruct at 4-bit AWQ — it fits the budget cleanly and is a good starting point — but you can swap to anything open-weight that fits.

## Docs

| Doc | What's in it |
|---|---|
| [docs/walkthrough.md](docs/walkthrough.md) | **Start here.** End-to-end guide: Docker → uv → Harbor → model → first score → making changes |
| [docs/docker_setup.md](docs/docker_setup.md) | Per-OS Docker install + common failures |
| [docs/harbor.md](docs/harbor.md) | Harbor mental model, commands, custom agents, public leaderboard submission |
| [docs/byo_model.md](docs/byo_model.md) | Ollama / vLLM / hosted endpoints, `.env` config |
| [docs/troubleshooting.md](docs/troubleshooting.md) | First-week issues, in order of likelihood |
| [docs/safety.md](docs/safety.md) | The rules that keep your laptop alive |

## License

MIT. Your submission repo must be MIT or Apache 2.0 too.
