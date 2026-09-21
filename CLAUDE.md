# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

This is the starter kit for the **Efficient Coder** competition (ML+X, UW–Madison, Kaggle): build an autonomous coding agent on top of an *approved open-weight model* (7–37 GB class) and score it on Terminal-Bench 2.0 (89 tasks) via [Harbor](https://www.harborframework.com/). The repo root holds the competition spec (`README.md`, `RULES.md`, `FAQ.md`, `RESOURCES.md`, `WRITEUP_TEMPLATE.md`); all agent code lives under `starter/`.

The scoring formula matters for how you should optimize the agent: `leaderboard_score = TB_score − 0.01 × (total_tokens / 1,000,000)`. Capability improvements dominate; token-hungry changes (extra self-critique passes, verbose prompts) have a real but small cost.

## Setup

```bash
uv venv --python 3.12
source .venv/bin/activate
uv pip install -e starter/          # editable install — edits to agent/ take effect immediately
cp starter/.env.example starter/.env  # non-secret settings (LLM_MAX_TOKENS, AGENT_*); local Ollama values
cp starter/.env.op.example starter/.env.op  # hosted endpoint: 1Password references for LLM_BASE_URL / LLM_API_KEY
```

**Team standard for the hosted endpoint:** credentials come from 1Password, not a plaintext `.env`. Launch anything that calls the model as `op run --env-file=starter/.env.op -- <command>` (e.g. `op run --env-file=starter/.env.op -- ./starter/scripts/run_baseline.sh regex-log`). `op://` references only resolve through `op run` — never put them in `starter/.env`, and never leave active `LLM_BASE_URL`/`LLM_MODEL`/`LLM_API_KEY` lines in `starter/.env` when using `.env.op` (`llm.py` loads `.env` with `override=True` and would clobber the injected values). Full guide: `starter/docs/1password.md`.

Requires Docker running (Harbor spins up a fresh container per task) and Python 3.12+. Full fresh-machine walkthrough: `starter/docs/walkthrough.md`.

## Commands

```bash
# Sanity-check Docker+Harbor+grading pipeline (no model involved — replays reference solutions)
harbor run -d terminal-bench-sample@2.0 -a oracle

# Run the agent on a single task (10-task sample dataset, fast iteration)
harbor run -d terminal-bench-sample@2.0 --agent agent.agent:BaselineAgent -i <task-name>

# Run the agent on all 10 sample tasks
./starter/scripts/run_baseline.sh
./starter/scripts/run_baseline.sh <task-name>          # or just one
./starter/scripts/run_baseline.sh <task-name> -m ollama/qwen2.5-coder:32b   # extra harbor flags pass through

# Run the official public subset (starter/eval/public_subset.txt) — the self-reported leaderboard score
./starter/scripts/run_subset.sh

# List available datasets / built-in agents
harbor datasets list
harbor run --help
```

All `harbor run` invocations must be run from inside the activated venv, and `agent.agent:BaselineAgent`-style import paths only resolve because `starter/` was installed editable — if that import fails, re-run `uv pip install -e starter/` from the repo root.

Concurrency: `-n <N>` runs N tasks in parallel containers, all sharing one model endpoint — start at `-n 1`/`2` and watch RAM.

### Reading results

Each `harbor run` writes `./jobs/<job-name>/<task>__<trial-id>/result.json`. Key fields: `verifier_result.rewards.reward` (0/1 score), `agent_result.n_input_tokens`/`n_output_tokens` (submission token count), `agent_result.metadata` (whatever the agent wrote to `context.metadata`, including the full message transcript), `exception_info`. `harbor view jobs` starts a local web viewer over the same data.

To compute the three submission-card numbers (`tb_score`, `total_tokens`, task count) from a job directory, see the `jq` one-liners in the root `README.md` under "Computing your submission numbers."

## Architecture

The agent is a **ReAct loop**: Harbor calls `BaselineAgent.run(instruction, environment, context)` once per task; the loop repeatedly (1) sends the full conversation to the LLM, (2) parses its response into exactly one action, (3) executes that action in the task's Docker container, (4) appends the output back into the conversation — until the model emits `TASK_COMPLETE` or `AGENT_MAX_TURNS` (default 100) is hit.

```
starter/agent/
├── agent.py     # BaseAgent subclass + the loop itself (BaselineAgent.run)
├── prompts.py   # SYSTEM_PROMPT, NUDGE_MESSAGE, observation_message() — all LLM-facing text
├── tools.py     # parse_action() (regex-extracts a ```bash block or TASK_COMPLETE) + run_shell()
└── llm.py       # LLMClient — thin async wrapper over any OpenAI-compatible /chat/completions endpoint
```

Key contracts and invariants, since they're easy to break silently:

- **The agent never touches the host filesystem.** The only way it affects anything is `environment.exec(command=..., timeout_sec=...)` inside the task's disposable Docker container. Don't add code paths that shell out locally to "test faster" — see `starter/docs/safety.md`.
- **One action per turn, by construction.** `tools.parse_action()` looks for a fenced ` ```bash ` block first; only if none is found does it check for the literal `TASK_COMPLETE` marker. A code block always wins, so the model can discuss finishing without accidentally ending the task. Anything else → `Action(kind="none")` → `agent.py` appends `NUDGE_MESSAGE` and loops.
- **`context` (an `AgentContext`) must be updated every turn, not just at the end.** Harbor reads it after `run()` returns *or times out*, so token counts and `context.metadata` (which the baseline uses to snapshot `turns`, `finished`, and the full `messages` list) need to reflect partial progress at every iteration — this is how a mid-run timeout still produces usable `result.json` data.
- **Output truncation is blunt on purpose.** `tools.MAX_OBSERVATION_CHARS` (6000) keeps only the first/last half of long command output with an omission marker in between. This is a named improvement target, not an oversight.
- **Model name resolution.** `llm._resolve_model()` strips litellm-style provider prefixes (`ollama/`, `hosted_vllm/`, etc.) that Harbor's `-m` flag may prepend, since the raw OpenAI SDK wants the bare model id. `LLM_MODEL` in `.env` always wins over the `-m`-derived name. `.env` is loaded with `override=True` specifically so stale shell-exported vars (from ad-hoc `curl` testing) can't silently shadow it.
- **Reasoning-model empty-response fallback.** If `message.content` comes back empty (a reasoning model burned its whole `LLM_MAX_TOKENS` budget on hidden thinking), `llm.chat()` falls back to `reasoning_content` rather than returning nothing — otherwise the agent nudge-loops to a timeout. The real fix when this happens is raising `LLM_MAX_TOKENS` (8192+ for reasoning models), not just relying on the fallback.

## Competition constraints that affect how you can change the agent

- **No task-specific hardcoding.** One system prompt, one agent loop, no `if task_name == "fix-git"` branches. Detecting a task *category* from the instruction text and adjusting strategy generically is fine; hardcoding a solution or prompt for an individual task is grounds for disqualification (all 89 tasks are public and the top 5 submissions get code-reviewed).
- **Approved models only for the submitted run** (dev/prototyping is unrestricted). No closed-weight model anywhere in the system, including "just as a planner" — see the approved list and quantization-equivalence rules in the root `README.md`.
- Any endpoint change is a `.env` / `.env.op` edit (`LLM_BASE_URL`/`LLM_MODEL`/`LLM_API_KEY`), never a code change — that portability is intentional and should be preserved when extending `llm.py`.
- Real keys never go in a committed file. The hosted key is loaded via 1Password (`starter/.env.op`, gitignored; `starter/.env.op.example` is the committed template). If someone uses a plaintext key in the gitignored `starter/.env` instead, treat any key an agent might have `cat`'d as burned (see `starter/docs/safety.md`).

## Where the improvement levers are (per `starter/README.md`)

Roughly in order of effort: `prompts.py` (instructions, task-type hints, output discipline) → context management (the conversation grows every turn — what to keep/summarize/drop) → error recovery (the baseline just shows the error and hopes) → planning/self-critique (separate plan/act steps, verify before declaring done) → model choice/quantization → architecture (multi-stage pipelines, retrieval, or switching to an *installed* agent per `starter/docs/harbor.md` for custom in-container tooling).
