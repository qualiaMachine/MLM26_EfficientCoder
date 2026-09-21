# Loading the API key with 1Password (`.env.op`)

**This is the standard way our team supplies `LLM_BASE_URL` / `LLM_API_KEY` for the hosted endpoint.** The key lives in your 1Password vault and is injected into the process at launch. It is never written to a file, so it can't be committed, pasted into a notebook, or `cat`'d by an agent (see [safety.md](safety.md)).

Plain `.env` with a literal key still works — it's the right choice for local Ollama (no real secret) — but for the hosted endpoint, use this.

This guide is the end-to-end path for the hosted endpoint: install dependencies → set up the repo → wire up 1Password → run Terminal-Bench → read results. For the general (Ollama) walkthrough, see [walkthrough.md](walkthrough.md).

## Contents

1. [How it works](#how-it-works)
2. [Prerequisites](#prerequisites)
3. [Set up the repo](#set-up-the-repo)
4. [Connect 1Password](#connect-1password)
5. [Verify the connection](#verify-the-connection)
6. [Run Terminal-Bench with `op run`](#run-terminal-bench-with-op-run)
7. [Read your results](#read-your-results)
8. [Using `op read` (ad-hoc and one-off use)](#using-op-read-ad-hoc-and-one-off-use)
9. [Do I have to approve on every agent call?](#do-i-have-to-approve-on-every-agent-call)
10. [Troubleshooting](#troubleshooting)
11. [Gotchas](#gotchas)

## How it works

`starter/.env.op` holds *references* like `op://Employee/<item>/credential`. Python's `os.environ` can't resolve those — `python-dotenv` would hand your agent the literal string `op://...` as its Bearer token, and the server would answer 401. Something has to resolve the reference first. That something is `op run`:

```
op run --env-file=starter/.env.op -- <your command>
        │
        ├─ reads .env.op, asks 1Password to resolve each op:// reference
        │   (this is where you authorize — Touch ID / app prompt)
        └─ starts <your command> with the real values in its environment
              └─ harbor → agent/llm.py → os.environ["LLM_API_KEY"]  ✔ real key
```

The agent itself needs no code changes; `llm.py` just reads `os.environ` as always. The LLM client runs in the Harbor process on your machine, not inside the task's Docker container, so the key never enters the container the agent's shell commands run in.

## Prerequisites

| What | Why | Install / check |
|---|---|---|
| **Docker** (running) | Harbor runs every task in a fresh container | macOS: `brew install --cask docker`, then launch Docker Desktop once. Check: `docker run hello-world`. Other OSes: [walkthrough.md](walkthrough.md#step-1-install-docker) |
| **uv** + **Python 3.12+** | Creates the venv; Harbor needs 3.12+ (uv fetches it for you) | `curl -LsSf https://astral.sh/uv/install.sh \| sh` (or `brew install uv`). Check: `uv --version` |
| **1Password desktop app + CLI (`op`)** | Holds the key and resolves `op://` references | `brew install --cask 1password-cli`. Check: `op --version` |
| **Campus VPN (GlobalProtect)** | The hosted endpoint is only reachable through it | Connect before any model call — see [uw_madison_endpoint.md](uw_madison_endpoint.md) |
| **git** | Clone the repo | Preinstalled on macOS/most Linux |
| `jq` (optional) | Computing submission numbers from results | `brew install jq` / `sudo apt install jq` |

Python packages come from `starter/pyproject.toml` and are installed in the next section — you don't install them by hand: `harbor>=0.13`, `openai>=1.40`, `python-dotenv>=1.0`.

Windows: do everything inside WSL2 (Ubuntu), including the `op` CLI — see [walkthrough.md](walkthrough.md#windows).

## Set up the repo

From the repo root:

```bash
uv venv --python 3.12
source .venv/bin/activate
uv pip install -e starter/        # editable: edits to starter/agent/ take effect immediately
harbor --version                  # expect 0.13.x or newer
```

Every later command assumes the venv is active (your prompt shows `(.venv)`). If `harbor` is "command not found" or `agent.agent:BaselineAgent` fails to import, re-activate the venv and re-run the `uv pip install -e starter/` line.

**Sanity-check Docker + Harbor + grading before involving any model.** This replays reference solutions, so it needs neither `op` nor the VPN:

```bash
harbor run -d terminal-bench-sample@2.0 -a oracle
```

Expect `Mean: 1.000` with 0 exceptions (or `0.900` — the sample task `build-cython-ext` has a known-broken oracle). Details: [walkthrough.md](walkthrough.md#step-4-verify-harbor--terminal-bench-with-the-oracle).

## Connect 1Password

1. **Install and connect the CLI.** Install 1Password CLI (`brew install --cask 1password-cli`), then in the 1Password desktop app enable *Settings → Developer → Integrate with 1Password CLI*. Check with `op --version` and `op vault list`.
2. **Find your item.** Your endpoint credentials are in a 1Password item in the `Employee` vault (fields include `base url` and `credential`). The item name is per-person, so don't copy someone else's reference.
3. **Create your personal `.env.op`** (gitignored — it contains your item name):
   ```bash
   cp starter/.env.op.example starter/.env.op
   ```
   Replace `<your-item>` with your item name. To avoid typos: in 1Password, open the field's menu → **Copy Secret Reference**, and paste it in. Quote any reference containing a space (the `base url` field).
4. **Create `starter/.env` with only non-secret settings.** Do *not* `cp .env.example .env` for this setup: the template has active Ollama `LLM_BASE_URL` / `LLM_MODEL` / `LLM_API_KEY` lines, and `llm.py` loads `.env` with `override=True`, so those would **silently replace** what `op run` injected — you'd end up talking to Ollama or the wrong model with no error. Write just the tuning values instead:
   ```bash
   cat > starter/.env <<'EOF'
   LLM_MAX_TOKENS=8192
   EOF
   ```
   `8192` matters: the hosted model is a reasoning model whose thinking tokens count against the limit, and too low a value makes every response come back empty until the task times out. Optional extras (`AGENT_MAX_TURNS`, `AGENT_COMMAND_TIMEOUT_SEC`, `LLM_TEMPERATURE`) also go here, never the three `LLM_*` connection values.

   If you already have a `starter/.env` from the template, comment out or delete those three lines.

`LLM_MODEL` lives in `.env.op` (not secret, but it must match the server exactly). The template's value is fine for development; confirm the model is an approved one before any submission run.

## Verify the connection

Connect the campus VPN first. Then:

```bash
op run --env-file=starter/.env.op -- sh -c \
  'curl -s -m 10 "$LLM_BASE_URL/models" -H "Authorization: Bearer $LLM_API_KEY"'
```

The single quotes matter: the *inner* shell must expand `$LLM_BASE_URL`, after `op run` has set it. Expect JSON listing model ids; the `LLM_MODEL` in your `.env.op` must match one of them exactly (a wrong id gives 400 "Invalid model name"). Note `op run` masks secret-looking values in output, so the base URL may print as `<concealed by 1Password>` — that's expected.

## Run Terminal-Bench with `op run`

Prefix any command that calls the model with `op run --env-file=starter/.env.op --`, from the repo root, with the venv active, Docker running, and the VPN connected.

```bash
# one sample task — start here
op run --env-file=starter/.env.op -- ./starter/scripts/run_baseline.sh regex-log

# all 10 sample tasks
op run --env-file=starter/.env.op -- ./starter/scripts/run_baseline.sh

# the public subset (starter/eval/public_subset.txt) — the self-reported score
op run --env-file=starter/.env.op -- ./starter/scripts/run_subset.sh

# the full 89-task Terminal-Bench 2.0 (leaderboard-style run)
op run --env-file=starter/.env.op -- harbor run -d terminal-bench@2.0 \
  --agent-import-path agent.agent:BaselineAgent -n 2

# harbor directly, one task
op run --env-file=starter/.env.op -- harbor run -d terminal-bench-sample@2.0 \
  --agent-import-path agent.agent:BaselineAgent -i regex-log
```

Notes:

- **Concurrency:** `-n <N>` runs N tasks in parallel containers sharing the one endpoint. The scripts read `N_CONCURRENT` (default 1 for `run_baseline.sh`, 2 for `run_subset.sh`), e.g. `N_CONCURRENT=4 op run --env-file=starter/.env.op -- ./starter/scripts/run_subset.sh`. Start low and watch RAM; the shared endpoint is also used by others, so be considerate (etiquette in [uw_madison_endpoint.md](uw_madison_endpoint.md)).
- **Extra flags pass through** the scripts to `harbor run`. Beware `-m`: `LLM_MODEL` from `.env.op` always wins over the `-m`-derived name, so to switch models edit `.env.op`.
- **The public subset is currently placeholders** (`starter/eval/public_subset.txt`) until the official list is announced at kickoff, so don't treat its score as the leaderboard number yet.
- **Commands that don't call the model** (the `-a oracle` check, `harbor view`, `build_dashboard.py`) don't need `op run`.
- **Long runs:** one approval covers the whole run (see [below](#do-i-have-to-approve-on-every-agent-call)).

## Read your results

No `op` needed. Each run writes `./jobs/<job-name>/<task>__<trial-id>/result.json`:

```bash
ls -t jobs/ | head -1                              # latest job
harbor view jobs                                   # local web viewer; click a job to expand tasks
python starter/scripts/build_dashboard.py jobs/<job-name> --open   # static HTML with full transcripts
```

Key fields: `verifier_result.rewards.reward` (1.0 = pass), `agent_result.n_input_tokens` / `n_output_tokens` (submission token count), `exception_info`. For the three submission-card numbers (score, total tokens, task count), use the `jq` one-liners in the root `README.md` under "Computing your submission numbers".

Transcripts and dashboards can contain anything the agent printed inside the container. Keep them local; never upload or publish them ([safety.md](safety.md)).

## Using `op read` (ad-hoc and one-off use)

`op read` prints the value of one secret reference — the counterpart of `op run`'s "inject everything at launch". **`op run` remains the standard for launching agent runs;** use `op read` only for the cases below.

```bash
op read "op://Employee/<your-item>/base url"        # print one field (quote refs with spaces)
op read -n "op://Employee/<your-item>/credential"   # -n: no trailing newline (useful in $(...))
```

**1. Spot-checking a reference.** Confirms the item and field names are right without launching anything. Run it in a private terminal: unlike `op run`, `op read` output is **not masked**, so don't run it on a shared screen or in a recorded/logged session, and don't `echo` the result.

**2. Passing a value inline to a single command** (e.g. a tool that isn't launched through your `.env.op`). `.env.op` isn't read on this path, so you must also supply `LLM_MODEL` yourself:

```bash
LLM_BASE_URL="$(op read 'op://Employee/<your-item>/base url')" \
LLM_API_KEY="$(op read -n 'op://Employee/<your-item>/credential')" \
LLM_MODEL=qwen3.8-27b \
./starter/scripts/run_baseline.sh regex-log
```

The values live only in that command's environment. The same `.env` rule applies: no active `LLM_*` connection lines in `starter/.env`, or they override these.

**Why not the default?** Each `op read` is its own read from 1Password and can prompt for approval separately (two reads → up to two prompts), and it makes it easy to leak a value into a variable, `set -x` trace or shell history. `op run` resolves everything once, masks output, and keeps the values scoped to the launched process. Never write an `op read` result into `starter/.env` or any other file — that defeats the point.

## Do I have to approve on every agent call?

**No.** Authorization happens when `op run` starts, not per request:

- `op run` resolves all references **once**, at launch, then starts your command. A full `harbor run` — hundreds of LLM calls over hours — needs one approval.
- The key stays in that process's memory for its lifetime. Nothing re-contacts 1Password mid-run, so a long run can't fail because an approval lapsed.
- Each *new* `op run` (a new script launch) may prompt again. With the desktop-app integration, an authorization typically stays valid for a short idle window (about 10 minutes per 1Password's docs; check your app's settings), so back-to-back runs often don't re-prompt.
- Per-read prompting is what happens with `op read` inside code (the pattern in the JupyterLab slide). That's why the agent doesn't use it.

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `curl` times out / connection error | Not on the campus VPN | Connect GlobalProtect ([uw_madison_endpoint.md](uw_madison_endpoint.md)) |
| `401` from the endpoint | Wrong item/field, or the literal `op://...` string reached the agent (launched without `op run`, or refs put in `.env`) | Launch via `op run --env-file=starter/.env.op --`; re-copy the secret reference |
| `400 Invalid model name` | `LLM_MODEL` doesn't match what `/models` reports | Copy the id exactly from the verify step into `.env.op` |
| `op` errors: "not signed in", item/vault not found | CLI not integrated with the desktop app, or wrong item name in the reference | Enable *Settings → Developer → Integrate with 1Password CLI*; check `op vault list`; re-copy the reference |
| Agent talks to Ollama / wrong model, no error | Active `LLM_*` lines in `starter/.env` overriding `op run` | Delete or comment them out |
| Every response empty, task times out | `LLM_MAX_TOKENS` too low for a reasoning model | Set `LLM_MAX_TOKENS=8192` (or higher) in `starter/.env` |
| `harbor: command not found` / import of `agent.agent` fails | venv not active, or package not installed | `source .venv/bin/activate` and `uv pip install -e starter/` |
| Most tasks error immediately | Docker not running or low disk | Start Docker Desktop; give it ≥30 GB ([troubleshooting.md](troubleshooting.md)) |

## Gotchas

- **Output is masked.** `op run` replaces secret-looking values in the command's output with `<concealed by 1Password>` — even the base URL. That's expected; `--no-masking` disables it, but then secrets can land in your terminal/logs.
- **`op://...` inside `starter/.env` does nothing.** Only `op run --env-file` resolves references. Put them in `.env.op`.
- **Concurrent runs (`-n`) share the one process environment** — no extra prompts.
- **Rotate if exposed.** If a real key ever appears in a file, transcript or agent output, treat it as burned and rotate it.
