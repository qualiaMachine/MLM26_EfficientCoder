# UW–Madison hosted endpoint

ML+X hosts a shared **`Qwen/Qwen3.6-27B-FP8`** deployment on campus GPU infrastructure for UW–Madison participants — no GPU of your own needed. Request the API key via the kickoff form (it arrives in the kickoff email; never commit it).

```bash
# .env
LLM_BASE_URL=<retrieved from in-person kickoff>
LLM_MODEL=/mnt/shared-models/qwen3.6-27B-fp8
LLM_API_KEY=<key from the kickoff email>
LLM_MAX_TOKENS=4096
```

Running *inside* a workspace on the same campus cluster? Use the cluster-internal hostname instead — it skips the public ingress:

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
