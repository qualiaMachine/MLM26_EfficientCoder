# Approved models

Submissions must use one of the models below. The list is deliberately short so the competition is about how you build the scaffold, not which model you found. Scoring is Terminal-Bench score minus a small token penalty — see the [README's Evaluation section](README.md#evaluation).

Development is unrestricted — prototype against any open-weight model or endpoint you like. The approved list governs the *submitted* run only.

| Model | Quantization | Reported VRAM | Notes |
|---|---|---|---|
| `Qwen/Qwen3.6-27B-FP8` | FP8 | 37 GB | **Anchor.** Newest and strongest of the group; reasoning model with coder tool-calling. Self-host on a 48 GB card, or UW–Madison participants can use the hosted endpoint in [`starter/docs/byo_model.md`](starter/docs/byo_model.md). |
| `qwen3-coder:30b` (Ollama GGUF Q4_K_M of `Qwen/Qwen3-Coder-30B-A3B-Instruct`) | GGUF Q4_K_M | 22 GB | The 4-bit tier of the MoE — no official 4-bit safetensors checkpoint exists, so this row is the Ollama tag. MoE: 30B total, ~3B active — fast, runs on 24 GB cards, workable on 16 GB via expert offload. |
| `Qwen/Qwen3-Coder-30B-A3B-Instruct-FP8` | FP8 | 35 GB | Same model, higher precision. Bedrock's managed `qwen.qwen3-coder-30b-a3b-v1:0` counts as this row. |
| `Qwen/Qwen2.5-Coder-32B-Instruct-AWQ` | AWQ 4-bit | 28 GB | A generation older but the most widely hosted (Together, Fireworks, NVIDIA API catalog) — easiest no-GPU path. |
| `Qwen/Qwen2.5-Coder-14B-Instruct-AWQ` | AWQ 4-bit | 15 GB | Small-GPU tier (16 GB+ cards). |
| `Qwen/Qwen2.5-Coder-7B-Instruct-AWQ` | AWQ 4-bit | 9 GB | Smallest approved; runs almost anywhere, expect a lower score ceiling. |

**Equivalent quantizations count as the same row.** GGUF/Q4_K_M (Ollama) and GPTQ-Int4 checkpoints of a listed model map to its AWQ 4-bit row; they're within ~10% of each other. Ollama's `qwen2.5-coder:7b/14b/32b` tags are the corresponding AWQ rows.

## How "reported VRAM" is computed

Each row's reported VRAM is **weights + KV cache for a 16k context window + small overhead**, served via vLLM at single-batch concurrency. It's there to tell you what hardware a model needs — approximate by design, since peak VRAM varies with batch size, context length, and runner.

```
Reported VRAM (GB) ≈ published checkpoint size                               # weights
                   + (n_layers × n_kv_heads × head_dim × 2 × 16384 × 2) / 1e9   # KV @ 16k, fp16
                   + ~2 GB headroom (activations, runner overhead)
```

For **MoE models**, the full checkpoint loads into VRAM — active params reduce compute, not memory.

### Sanity-checking a number yourself

[`starter/scripts/estimate_vram.py`](starter/scripts/estimate_vram.py) computes the formula above from a HuggingFace repo id — weights from the published checkpoint's actual file sizes (so quantized checkpoints are handled automatically), KV cache from the model's config. No GPU or model download needed:

```bash
python starter/scripts/estimate_vram.py Qwen/Qwen2.5-Coder-32B-Instruct-AWQ
# weights 19.4 GB + KV @ 16k 4.3 GB + 2 GB headroom ≈ 25.7 GB  (table row: 28 GB)
```

Landing within a few GB of the table row is expected and fine. (Don't compare against `nvidia-smi` — most serving stacks preallocate a large memory pool at startup, so the reading reflects your GPU, not the model.)

To verify the whole table at once, [`starter/scripts/check_vram_table.py`](starter/scripts/check_vram_table.py) parses every row above and prints table vs. estimate side by side — anyone can run it, which is how the numbers stay honest.

## Requesting an addition

The list is meant to stay short, but it isn't frozen. If a model materially changes what's possible for participants (a new open-weight coder release, a hardware tier the list doesn't serve), post in the **Kaggle Discussion tab** with the HuggingFace id, the quantization, and the case for adding it. Additions should land at or under ~48 GB reported VRAM — a single serious GPU. Organizers respond within a day or two; once listed, the model is available to every team.
