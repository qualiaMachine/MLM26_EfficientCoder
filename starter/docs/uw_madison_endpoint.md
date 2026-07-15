# UW–Madison hosted endpoint

ML+X runs a shared model server on campus GPUs so UW–Madison participants can compete without a GPU of their own. This page explains how your agent connects to it.

## How the pieces fit

Your agent never loads a model itself. The starter's `agent/llm.py` reads three values from `.env` and sends OpenAI-style chat requests over HTTP:

```
your agent (llm.py)  ──HTTP──▶  LLM_BASE_URL  (the model server)
        │                             │
   LLM_API_KEY                   LLM_MODEL
   (sent as a Bearer token       (which model you're asking
    to prove you're allowed)      that server to run)
```

- **`LLM_BASE_URL`** — where the server lives. The main URL requires the **campus VPN (GlobalProtect) — connect it first, whether you're on campus or off**. A cluster-internal URL works only from workspaces on the same campus cluster (faster — it skips the ingress).
- **`LLM_MODEL`** — the model id *as that server knows it*. This must match what the server reports at `GET /models`, not a name you choose.
- **`LLM_API_KEY`** — sent with every request; the server rejects requests without it.

The URLs and the key are distributed at the in-person kickoff — they are deliberately not published in this repo.

## Configure `.env`

The `.env` file lives in the `starter/` directory. When Harbor starts your agent, `agent/llm.py` loads `starter/.env` automatically (via `python-dotenv`) — you never pass these values on the command line. Create the file from the template, then fill in the values from kickoff:

```bash
# run from the repo root
cp starter/.env.example starter/.env
```

```bash
# starter/.env — primary hosted endpoint (Qwen3.6-27B-FP8; key required)
LLM_BASE_URL=<retrieved from in-person kickoff>
LLM_MODEL=/mnt/shared-models/qwen3.6-27B-fp8
LLM_API_KEY=<key from the kickoff email>
LLM_MAX_TOKENS=4096

# Cluster-internal alternative for LLM_BASE_URL (workspaces on the campus cluster only):
#LLM_BASE_URL=<internal URL retrieved from in-person kickoff>

# Older test endpoint (no API key; campus VPN required) — handy for a quick
# connectivity check, but it's a vision model, not approved for submissions:
#LLM_BASE_URL=<older endpoint URL — from kickoff>
#LLM_MODEL=QuantTrio/Qwen3-VL-32B-Instruct-AWQ
#LLM_API_KEY=none
```

## Verify the connection

One command checks the VPN, the URL, your key, and tells you the exact `LLM_MODEL` string. But note: `.env` is read by the *agent*, not by your terminal — so for this one-off check you first have to load the file into your shell. Run both lines from the repo root:

```bash
set -a; source starter/.env; set +a    # load .env values into this shell session
curl "$LLM_BASE_URL/models" -H "Authorization: Bearer $LLM_API_KEY"
```

- **JSON listing a model** → connected; the `id` field is exactly what belongs in `LLM_MODEL`.
- **401** → key is wrong or missing.
- **Connection timeout / DNS failure** → you're not on the VPN (GlobalProtect), or the URL is wrong.

## Things to know about this endpoint

- **The model id is a checkpoint path** (`/mnt/shared-models/qwen3.6-27B-fp8`), not a HuggingFace repo id — the server serves it under the path it was loaded from. For your *submission card*, the corresponding approved checkpoint is `Qwen/Qwen3.6-27B-FP8` (37 GB).
- **It's a reasoning model.** Thinking tokens count against the completion budget, so set `LLM_MAX_TOKENS` to 4096 or higher — at the starter default of 2048 the model can spend the whole budget thinking and return an empty answer. Thinking arrives in `reasoning_content`, separate from the final `content`.
- **Long context, cheap re-prompting.** 250k-token context window with prefix caching enabled, so re-sending the growing conversation each turn (what the starter loop does) is fast. Every million tokens costs 0.01 leaderboard points, so lean context management still pays.
- **Capacity is shared across all teams** (a handful of concurrent sequences). Keep `harbor run -n` at 2–4 and give other teams a heads-up in the Kaggle Discussion tab before kicking off a full 89-task sweep.
