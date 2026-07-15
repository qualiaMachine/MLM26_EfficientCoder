# Bring your own model

The baseline talks to any **OpenAI-compatible** chat completions endpoint. Set three values in `.env`:

```bash
LLM_BASE_URL=...   # where the endpoint lives
LLM_MODEL=...      # model id as the endpoint knows it
LLM_API_KEY=...    # anything non-empty for local endpoints
```

## Provided endpoint (UW–Madison participants — default)

ML+X hosts a shared **`Qwen/Qwen3.6-27B-FP8`** deployment on campus RunAI for UW–Madison participants — no GPU of your own needed. *Request the API key by emailing endemann@wisc.edu with the following (1) your wisc email address, (2) your registered team name on Kaggle.*

```bash
# .env
LLM_BASE_URL=<retrieved from in-person kickoff>
LLM_MODEL=/mnt/shared-models/qwen3.6-27B-fp8
LLM_API_KEY=<see key request instructions above>
LLM_MAX_TOKENS=4096
```

Running *inside* a RunAI workspace on the same cluster? Use the cluster-internal hostname instead — it skips the public ingress:

```bash
LLM_BASE_URL=<internal URL retrieved from in-person kickoff>
```

Verify your key and the served model id in one shot:

```bash
curl $LLM_BASE_URL/models -H "Authorization: Bearer $LLM_API_KEY"
```

Things to know about this endpoint:

- **The model id is a checkpoint path** (`/mnt/shared-models/qwen3.6-27B-fp8`), not a HuggingFace repo id — vLLM serves it under the path it was loaded from. The `curl` above shows the exact string to put in `LLM_MODEL`. For your *submission card*, the corresponding approved checkpoint is `Qwen/Qwen3.6-27B-FP8` (37 GB).
- **It's a reasoning model.** Thinking tokens count against the completion budget, so set `LLM_MAX_TOKENS` to 4096 or higher — at the starter default of 2048 the model can spend the whole budget thinking and return an empty answer. Thinking arrives in `reasoning_content`, separate from the final `content`.
- **Long context, cheap re-prompting.** 250k-token context window with prefix caching enabled, so re-sending the growing conversation each turn (what the starter loop does) is fast. Every million tokens costs 0.01 leaderboard points, so lean context management still pays.
- **Capacity is shared across all teams** (a handful of concurrent sequences). Keep `harbor run -n` at 2–4 and give other teams a heads-up in the Kaggle Discussion tab before kicking off a full 89-task sweep.

## Ollama (easiest local option)

```bash
# Install: https://ollama.com/download
ollama pull qwen2.5-coder:32b      # pick a size that fits your GPU/RAM
ollama serve                        # usually already running as a service
```

```bash
# .env
LLM_BASE_URL=http://localhost:11434/v1
LLM_MODEL=qwen2.5-coder:32b
LLM_API_KEY=ollama
```

Tip: `ollama list` shows the exact model names to use.

## vLLM (serious local serving)

Higher throughput and better parallelism than Ollama — worth it once you're running full subsets.

```bash
uv pip install vllm
vllm serve Qwen/Qwen2.5-Coder-32B-Instruct-AWQ --max-model-len 16384
```

```bash
# .env
LLM_BASE_URL=http://localhost:8000/v1
LLM_MODEL=Qwen/Qwen2.5-Coder-32B-Instruct-AWQ
LLM_API_KEY=none
```

## Hosted open-weight APIs (no GPU needed)

Together, Fireworks, and Groq all serve open-weight models behind OpenAI-compatible endpoints — handy for development before you have local hardware. Example (Together):

```bash
# .env
LLM_BASE_URL=https://api.together.xyz/v1
LLM_MODEL=Qwen/Qwen2.5-Coder-32B-Instruct
LLM_API_KEY=<your-together-key>     # use a throwaway/dev key
```

**Constraint reminder:** hosted endpoints are fine for *development*, but your submitted run must use one of the approved models in the [challenge README](../../README.md#approved-models). Closed-weight models (GPT, Claude, Gemini) are out of scope everywhere. Bedrock's fully-managed `qwen3-coder-30b-a3b` counts as the approved FP8 entry; Bedrock Custom Model Import is not viable for a hackathon team (Provisioned-Throughput-only, $21–50/hr). Anchor: `Qwen/Qwen3.6-27B-FP8` (37 GB) — the UW–Madison-hosted endpoint above, or self-host it from HuggingFace; the most widely hosted alternative is `Qwen/Qwen2.5-Coder-32B-Instruct-AWQ` (28 GB).

## Swapping models

Everything is `.env`-driven — swap models as often as you like during the competition. You can also pass `-m provider/model` to `harbor run` to record which model a job used (the agent strips the provider prefix automatically; `LLM_MODEL` takes precedence if both are set).
