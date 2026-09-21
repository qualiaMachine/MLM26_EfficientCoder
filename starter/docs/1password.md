# Loading the API key with 1Password (`.env.op`)

**This is the standard way our team supplies `LLM_BASE_URL` / `LLM_API_KEY` for the hosted endpoint.** The key lives in your 1Password vault and is injected into the process at launch. It is never written to a file, so it can't be committed, pasted into a notebook, or `cat`'d by an agent (see [safety.md](safety.md)).

Plain `.env` with a literal key still works — it's the right choice for local Ollama (no real secret) — but for the hosted endpoint, use this.

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

The agent itself needs no code changes; `llm.py` just reads `os.environ` as always.

## One-time setup

1. **Install and connect the CLI.** Install 1Password CLI (`brew install --cask 1password-cli`), then in the 1Password desktop app enable *Settings → Developer → Integrate with 1Password CLI*. Check with `op --version` and `op vault list`.
2. **Find your item.** Your endpoint credentials are in a 1Password item in the `Employee` vault (fields include `base url` and `credential`). The item name is per-person, so don't copy someone else's reference.
3. **Create your personal `.env.op`** (gitignored — it contains your item name):
   ```bash
   cp starter/.env.op.example starter/.env.op
   ```
   Replace `<your-item>` with your item name. To avoid typos: in 1Password, open the field's menu → **Copy Secret Reference**, and paste it in.
4. **Keep the LLM settings out of `starter/.env`.** If you copied `.env.example`, comment out or delete the active `LLM_BASE_URL`, `LLM_MODEL` and `LLM_API_KEY` lines (the Ollama defaults). `llm.py` loads `.env` with `override=True`, so an active value there **silently replaces** what `op run` injected — you'd end up talking to Ollama or the wrong model with no error. Things like `LLM_MAX_TOKENS=8192` and `AGENT_*` stay in `.env`.

## Running things

Prefix any command that calls the model with `op run`, from the repo root:

```bash
# single task
op run --env-file=starter/.env.op -- ./starter/scripts/run_baseline.sh regex-log

# all 10 sample tasks
op run --env-file=starter/.env.op -- ./starter/scripts/run_baseline.sh

# public subset
op run --env-file=starter/.env.op -- ./starter/scripts/run_subset.sh

# or harbor directly
op run --env-file=starter/.env.op -- harbor run -d terminal-bench-sample@2.0 \
  --agent-import-path agent.agent:BaselineAgent -i regex-log
```

Commands that don't call the model (e.g. the `-a oracle` sanity check) don't need it.

## Verify the connection

Connect the campus VPN (GlobalProtect) first — see [uw_madison_endpoint.md](uw_madison_endpoint.md). Then:

```bash
op run --env-file=starter/.env.op -- sh -c \
  'curl -s -m 10 "$LLM_BASE_URL/models" -H "Authorization: Bearer $LLM_API_KEY"'
```

The single quotes matter: the *inner* shell must expand `$LLM_BASE_URL`, after `op run` has set it. Expect JSON listing model ids; the `LLM_MODEL` in your `.env.op` must match one of them exactly. Timeout → VPN. 401 → wrong item/field. `op` error → not signed in, or the item/field name in your reference is wrong.

## Do I have to approve on every agent call?

**No.** Authorization happens when `op run` starts, not per request:

- `op run` resolves all references **once**, at launch, then starts your command. A full `harbor run` — hundreds of LLM calls over hours — needs one approval.
- The key stays in that process's memory for its lifetime. Nothing re-contacts 1Password mid-run, so a long run can't fail because an approval lapsed.
- Each *new* `op run` (a new script launch) may prompt again. With the desktop-app integration, an authorization typically stays valid for a short idle window (about 10 minutes per 1Password's docs; check your app's settings), so back-to-back runs often don't re-prompt.
- Per-read prompting is what happens with `op read` inside code (the pattern in the JupyterLab slide). We don't use that here.

## Gotchas

- **Output is masked.** `op run` replaces secret-looking values in the command's output with `<concealed by 1Password>` — even the base URL. That's expected; `--no-masking` disables it, but then secrets can land in your terminal/logs.
- **`op://...` inside `starter/.env` does nothing.** Only `op run --env-file` resolves references. Put them in `.env.op`.
- **Concurrent runs (`-n`) share the one process environment** — no extra prompts.
- **Rotate if exposed.** If a real key ever appears in a file, transcript or agent output, treat it as burned and rotate it.
