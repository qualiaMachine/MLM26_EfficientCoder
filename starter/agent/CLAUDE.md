# starter/agent/

## Purpose
The agent package Harbor imports (`agent.agent:BaselineAgent`): a minimal ReAct loop that
solves a Terminal-Bench task by issuing bash commands inside the task's Docker container.

## Contents
- `__init__.py` — empty; makes `agent` importable (needs the editable install of `starter/`).
- `agent.py` — `BaselineAgent(BaseAgent)` and the loop in `run()`: LLM call → `parse_action` → `run_shell` → append observation. Reads `AGENT_MAX_TURNS` (100) and `AGENT_COMMAND_TIMEOUT_SEC` (60). `setup()` is a no-op.
- `prompts.py` — all LLM-facing text: `SYSTEM_PROMPT`, `NUDGE_MESSAGE`, `observation_message()`.
- `tools.py` — `parse_action()` (regex for a fenced code block, else the `TASK_COMPLETE` marker) and `run_shell()` (wraps `environment.exec`, formats exit code/stdout/stderr, truncates).
- `llm.py` — `LLMClient`, an async wrapper over any OpenAI-compatible `/chat/completions`; `_resolve_model()` strips litellm provider prefixes.

## How it fits in
This is the whole product. `starter/scripts/run_*.sh` point Harbor at `agent.agent:BaselineAgent`;
`starter/scripts/build_dashboard.py` reads the `context.metadata` this loop writes. Data flow is
`agent.py` → `llm.py` (text + usage) → `tools.py` (action, observation) → back into `messages`,
with `prompts.py` supplying the strings. All improvement levers (prompts, context mgmt, error
recovery, self-critique) are edits here.

## Gotchas
- **Never touch the host.** Only `environment.exec()` may affect anything (`starter/docs/safety.md`).
- **`context` must be updated every turn** — tokens and `metadata` (`turns`, `finished`, `messages`) — so a timeout still yields a usable `result.json`. `messages` is stored by reference, so later appends show up automatically.
- **Code block beats `TASK_COMPLETE`**, and `CODE_BLOCK_RE` also accepts *untagged* fences (not only ```` ```bash ````). An empty block falls through to the done check.
- **Truncation is per stream, not per observation**: stdout and stderr are each capped at `MAX_OBSERVATION_CHARS` (6000, first/last half kept), so one observation can reach ~12k chars. Intentionally blunt; a named improvement target.
- **No context-window management**: `messages` grows unbounded every turn.
- **No retry in `llm.chat()`**: an endpoint exception propagates out of `run()` and ends the trial.
- **Reasoning-model fallback**: empty `content` falls back to `reasoning_content`; that text is then parsed as an action, so a code block inside the model's thinking *will be executed*. Real fix is `LLM_MAX_TOKENS` ≥ 8192 (code default is only 2048).
- **Model resolution**: `LLM_MODEL` beats Harbor's `-m`. `.env` loads with `override=True`, so it also clobbers vars injected by `op run` — keep active `LLM_*` lines out of `.env` when using `.env.op`.
- `SYSTEM_PROMPT` asserts "no network"; some tasks may differ, and finale tasks may truly have none, so `setup()` must not rely on downloads.
- No task-specific branches or hardcoded prompts (competition rule; grounds for disqualification).
- `tools.py`'s `CODE_BLOCK_RE` and `prompts.py`'s `NUDGE_MESSAGE` are duplicated in `scripts/build_dashboard.py` — change them together.
