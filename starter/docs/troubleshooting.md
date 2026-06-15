# Troubleshooting

Work through these in order — they cover ~90% of first-week issues. Still stuck? Post in Discord with the exact command, the full error, and your OS.

## Setup

**`harbor: command not found`**
Your venv isn't activated (`source .venv/bin/activate` from the repo root) or the install failed. Re-run `uv pip install -e starter/` and check for errors.

**`requires-python >=3.12` / install resolution errors**
Harbor needs Python 3.12+. Recreate the venv: `uv venv --python 3.12` (uv downloads 3.12 for you if missing).

**`Failed to import module 'agent.agent'`**
The agent package isn't installed in the venv Harbor runs from. From the repo root: `uv pip install -e starter/` (the editable install is what makes `--agent-import-path agent.agent:MLMBaselineAgent` resolvable).

**`Cannot connect to the Docker daemon`**
Docker isn't running. See [docker_setup.md](docker_setup.md).

**Oracle run fails (`harbor run -d terminal-bench-sample@2.0 -a oracle`)**
This is the canary — if oracle fails, the problem is your Docker/Harbor setup, not your agent. Check Docker is running, you have disk space (≥30 GB for Docker), and your network can pull images.

## Agent runs

**Agent import fails with `--agent-import-path agent.agent:MLMBaselineAgent`**
Activate the venv and make sure you ran `uv pip install -e starter/` from the repo root — that's what puts the `agent` package on Harbor's import path.

**Agent starts but every LLM call fails (connection refused / 404)**
Your endpoint isn't up or `.env` is wrong. Test it directly:

```bash
curl $LLM_BASE_URL/models -H "Authorization: Bearer $LLM_API_KEY"
```

If that fails, fix the endpoint before debugging the agent. Ollama default is `http://localhost:11434/v1` (note the `/v1`).

**`No model configured`**
Set `LLM_MODEL` in `.env`, or pass `-m` to `harbor run`.

**Model replies but the agent does nothing (repeated nudge messages)**
The model isn't following the one-bash-block protocol. Common with very small models (<7B). Try a bigger/stronger coder model, lower the temperature, or tighten `prompts.py` — this is your first real agent-engineering problem, welcome.

**Tasks time out constantly**
Local models are slow; a 5-minute task budget is tight. Check tokens/sec on your endpoint. Quantize harder, shorten `LLM_MAX_TOKENS`, trim the conversation history, or reduce `-n` concurrency so tasks aren't starving each other.

**Out of memory / machine grinding during runs**
Each concurrent task is a full container plus your model server. Drop `-n` to 1–2, and give Docker more memory in Docker Desktop settings.

## Results

**Where are my scores?**
Console prints the aggregate at the end; per-trial details are in `./jobs/<job-name>/.../result.json`.

**My score varies run to run**
Normal — LLM sampling is stochastic. Use `--n-attempts` for pass@k stats, and report your evaluation procedure honestly in the writeup.
