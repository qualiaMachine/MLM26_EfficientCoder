# Approved models

Submissions must use a model listed here with a reported VRAM of **48 GB or less**. Ranking is by Terminal-Bench score (ties broken by fewer total tokens). To make the VRAM limit verifiable without forcing every team to run nvidia-smi, we publish a canonical table of `(model, quantization)` → reported VRAM — you pick a row, and the row decides eligibility. Rows above 48 GB stay listed for prototyping reference but can't be submitted.

> Want to use a model that isn't listed? Post in the Kaggle Discussion tab with the HuggingFace link, the published quantization, and (if you have it) a quick VRAM estimate — organizers will add it to the table, usually within a day or two. There is no penalty for being first to ask; the eligibility rule is the same for everyone, and we'd rather expand the catalog than gatekeep it.

> A note on VRAM numbers: the values in this table are **approximate but good enough for eligibility**. They assume a 16k-token context window, single-batch serving, and the published checkpoint as released — peak VRAM in practice can be a few GB higher or lower depending on your runner and how much context you push. Eligibility is decided by the table value, not by anything you measure, so that noise never affects your submission.

## How "reported VRAM" is computed

Each row's reported VRAM is **weights + KV cache for a 16k context window + small overhead**, served via vLLM at single-batch concurrency. This is approximate by design — peak VRAM in practice varies with batch size, context length, and runner — but it's *consistent across teams*, which is what scoring requires.

```
Reported VRAM (GB) ≈ params × (bits / 8) / 1e9     # weights
                   + (n_layers × n_kv_heads × head_dim × 2 × 16384 × bytes_per_elem) / 1e9   # KV @ 16k
                   + ~2 GB headroom (activations, runner overhead)
```

For **MoE models**: use *total* params for the weights term, not active params — you have to load every expert into VRAM. Active params don't reduce memory, only compute.

For **GGUF/Q4_K_M** equivalents (Ollama users), use the AWQ 4-bit row for the same model — they're within ~10% of each other and the table's resolution doesn't care.

### Sanity-checking a number yourself

[`starter/scripts/estimate_vram.py`](starter/scripts/estimate_vram.py) computes the formula above from a HuggingFace repo id — weights from the published checkpoint's actual file sizes (so quantized checkpoints are handled automatically), KV cache from the model's config. No GPU or model download needed:

```bash
python starter/scripts/estimate_vram.py Qwen/Qwen2.5-Coder-32B-Instruct-AWQ
# weights 19.4 GB + KV @ 16k 4.3 GB + 2 GB headroom ≈ 25.7 GB  (table row: 28 GB)
```

Landing within a few GB of the table row is expected and fine. When proposing a new row, include this output in your Kaggle Discussion post.

Don't sanity-check with `nvidia-smi` alone: serving stacks preallocate. vLLM grabs ~90% of visible GPU memory at startup and turns the surplus into KV-cache pool, so the reading sits near the card's ceiling regardless of the model. If you want a live number, take the "model weights take X GiB" line from vLLM's startup log and add the KV term from the script.

## Reported VRAM table

### Qwen2.5-Coder family

| Model | Quantization | Reported VRAM | Notes |
|---|---|---|---|
| `Qwen/Qwen2.5-Coder-0.5B-Instruct` | bf16 | 2 GB | Tiny — useful for testing your scaffold end-to-end on CPU/iGPU. |
| `Qwen/Qwen2.5-Coder-1.5B-Instruct` | bf16 | 4 GB | |
| `Qwen/Qwen2.5-Coder-3B-Instruct` | bf16 | 7 GB | Smallest one that can solve easy tasks unaided. |
| `Qwen/Qwen2.5-Coder-7B-Instruct-AWQ` | AWQ 4-bit | 7 GB | |
| `Qwen/Qwen2.5-Coder-7B-Instruct` | bf16 | 18 GB | |
| `Qwen/Qwen2.5-Coder-14B-Instruct-AWQ` | AWQ 4-bit | 12 GB | Strong speed/quality balance. |
| `Qwen/Qwen2.5-Coder-14B-Instruct` | bf16 | 32 GB | |
| `Qwen/Qwen2.5-Coder-32B-Instruct-AWQ` | AWQ 4-bit | 28 GB | **Suggested anchor.** |
| `Qwen/Qwen2.5-Coder-32B-Instruct-GPTQ-Int4` | GPTQ 4-bit | 28 GB | Functionally equivalent VRAM to AWQ. |
| `Qwen/Qwen2.5-Coder-32B-Instruct` | bf16 | 76 GB | |

### Qwen3-Coder family

| Model | Quantization | Reported VRAM | Notes |
|---|---|---|---|
| `Qwen/Qwen3-Coder-30B-A3B-Instruct-Int4` | Int4 | 18 GB | MoE: 30B total / ~3B active. |
| `Qwen/Qwen3-Coder-30B-A3B-Instruct-FP8` | FP8 | 35 GB | |
| `Qwen/Qwen3-Coder-30B-A3B-Instruct` | bf16 | 64 GB | |
| `Qwen/Qwen3-Coder-Next` | bf16 | TBD | Recently released; request via Kaggle Discussion. |
| `Qwen/Qwen3-Coder-480B-A35B-Instruct-FP8` | FP8 | 500 GB | Hosted-only (NRP, Bedrock-via-CMI). |
| `Qwen/Qwen3-Coder-480B-A35B-Instruct` | bf16 | ~1000 GB | Hosted-only. |

### Qwen3.6 family

| Model | Quantization | Reported VRAM | Notes |
|---|---|---|---|
| `Qwen/Qwen3.6-27B-FP8` | FP8 | 32 GB | Served on a shared hosted endpoint for participants — setup in [`starter/docs/byo_model.md`](starter/docs/byo_model.md). Reasoning model with coder tool-calling. |

### DeepSeek-Coder family

| Model | Quantization | Reported VRAM | Notes |
|---|---|---|---|
| `deepseek-ai/deepseek-coder-1.3b-instruct` | bf16 | 3 GB | |
| `deepseek-ai/deepseek-coder-6.7b-instruct` | bf16 | 16 GB | |
| `TheBloke/deepseek-coder-6.7b-instruct-AWQ` | AWQ 4-bit | 6 GB | |
| `deepseek-ai/deepseek-coder-33b-instruct` | bf16 | 72 GB | |
| `TheBloke/deepseek-coder-33b-instruct-AWQ` | AWQ 4-bit | 24 GB | |
| `deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct` | bf16 | 36 GB | 16B MoE, ~2.4B active. |
| `deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct-AWQ` | AWQ 4-bit | 12 GB | |
| `deepseek-ai/DeepSeek-Coder-V2-Instruct` | FP8 | 250 GB | 236B MoE. Hosted-only. |
| `deepseek-ai/DeepSeek-V3.1` | FP8 | 700 GB | 671B MoE. Hosted-only (Bedrock). |

### Code Llama / Llama 3 family

| Model | Quantization | Reported VRAM | Notes |
|---|---|---|---|
| `codellama/CodeLlama-7b-Instruct-hf` | bf16 | 16 GB | |
| `codellama/CodeLlama-13b-Instruct-hf` | bf16 | 28 GB | |
| `codellama/CodeLlama-34b-Instruct-hf-AWQ` | AWQ 4-bit | 22 GB | |
| `codellama/CodeLlama-34b-Instruct-hf` | bf16 | 72 GB | |
| `codellama/CodeLlama-70b-Instruct-hf` | bf16 | 152 GB | |
| `meta-llama/Meta-Llama-3.1-8B-Instruct` | bf16 | 18 GB | General-purpose; not coder-tuned but competitive. |
| `meta-llama/Llama-3.3-70B-Instruct-AWQ` | AWQ 4-bit | 42 GB | |
| `meta-llama/Llama-3.3-70B-Instruct` | bf16 | 152 GB | |

### Granite-Code (IBM)

| Model | Quantization | Reported VRAM | Notes |
|---|---|---|---|
| `ibm-granite/granite-3b-code-instruct` | bf16 | 8 GB | |
| `ibm-granite/granite-8b-code-instruct` | bf16 | 18 GB | |
| `ibm-granite/granite-20b-code-instruct` | bf16 | 44 GB | |
| `ibm-granite/granite-34b-code-instruct` | bf16 | 72 GB | |

### StarCoder2

| Model | Quantization | Reported VRAM | Notes |
|---|---|---|---|
| `bigcode/starcoder2-3b` | bf16 | 8 GB | Base only — no instruct variant. |
| `bigcode/starcoder2-7b` | bf16 | 16 GB | |
| `bigcode/starcoder2-15b` | bf16 | 32 GB | |
| `bigcode/starcoder2-15b-instruct-v0.1` | bf16 | 32 GB | |

### Yi-Coder

| Model | Quantization | Reported VRAM | Notes |
|---|---|---|---|
| `01-ai/Yi-Coder-1.5B-Chat` | bf16 | 4 GB | |
| `01-ai/Yi-Coder-9B-Chat` | bf16 | 20 GB | |

### CodeGemma / Gemma-4

| Model | Quantization | Reported VRAM | Notes |
|---|---|---|---|
| `google/codegemma-2b` | bf16 | 5 GB | |
| `google/codegemma-7b-it` | bf16 | 18 GB | |
| `google/gemma-4-12B-it-qat-w4a16-ct` | w4a16 (QAT) | 8 GB | Multimodal. NRP-hosted. |
| `google/gemma-4-31B-it-qat-w4a16-ct` | w4a16 (QAT) | 18 GB | Multimodal. NRP-hosted. |

### Community fine-tunes

| Model | Quantization | Reported VRAM | Notes |
|---|---|---|---|
| `Phind/Phind-CodeLlama-34B-v2` | bf16 | 72 GB | Community fine-tune of CodeLlama-34B. |
| `WizardLMTeam/WizardCoder-Python-34B-V1.0` | bf16 | 72 GB | |
| `ise-uiuc/Magicoder-S-DS-6.7B` | bf16 | 16 GB | DeepSeek-Coder-6.7B fine-tune. |

### GLM / ChatGLM

| Model | Quantization | Reported VRAM | Notes |
|---|---|---|---|
| `THUDM/GLM-4-9B-Chat` | bf16 | 20 GB | |
| `THUDM/glm-4-32b-0414` | bf16 | 72 GB | |
| `THUDM/GLM-4.5` | bf16 | TBD | Request via Kaggle Discussion once config is finalized. |

### Hosted-only / NRP managed LLM catalog

These models are too large to run on consumer or single-card research hardware. They're available via NRP's managed-LLM endpoint (UW participants via CILogon) and several are mirrored on NVIDIA build.

| Model | Quantization | Reported VRAM | Notes |
|---|---|---|---|
| `openai/gpt-oss-120b` | MXFP4 (native) | 70 GB | Fits on a single A100 80 GB. |
| `MiniMaxAI/MiniMax-M2.7` | FP8 (native) | 240 GB | 230B dense. NRP-hosted. |
| `nvidia/GLM-5.2-NVFP4` | NVFP4 | 380 GB | 744B MoE. NRP-hosted. |
| `Qwen/Qwen3.5-397B-A17B-FP8` | FP8 | 410 GB | NRP-hosted. |
| `moonshotai/Kimi-K2.7-Code` | Int4 (native) | 510 GB | 1T MoE. NRP-hosted. |

### Bedrock fully-managed (approximate)

AWS Bedrock's fully-managed pay-per-token Qwen3-Coder lineup is eligible, but **the table values below are approximate**. AWS doesn't formally state the serving quantization on its public model cards; the numbers below assume **FP8**, which is the smallest precision Qwen publishes an official checkpoint for and is consistent with Bedrock's pricing on these models. If AWS confirms a different precision (or changes it mid-semester), we'll update the table. Use these for self-reported submissions until then.

| Bedrock model id | Assumed quantization | Reported VRAM | Notes |
|---|---|---|---|
| `qwen.qwen3-coder-30b-a3b-v1:0` | FP8 (assumed) | 35 GB | 30B MoE, ~3B active. Coder-tuned. |
| `qwen.qwen3-coder-480b-a35b-v1:0` | FP8 (assumed) | 510 GB | 480B MoE, ~35B active. Coder-tuned. ~$0.22/$1.80 per 1M tokens. |
| `qwen.qwen3-coder-next-v1:0` | FP8 (assumed) | TBD | Added Feb 2026. Request via Kaggle Discussion once size is verified. |
| `qwen.qwen3-235b-a22b-instruct-2507-v1:0` | FP8 (assumed) | 245 GB | 235B MoE, ~22B active. General-purpose instruct, not coder-tuned but competitive on coding benchmarks. |
| `qwen.qwen3-32b-v1:0` | FP8 (assumed) | 38 GB | Dense 32B. Good for latency-sensitive use. |

Confirmed launch (Sep 2025): the first four Qwen3 models are the original Bedrock launch from [Danilo Poccia's announcement](https://aws.amazon.com/blogs/aws/qwen-models-are-now-available-in-amazon-bedrock/); `qwen3-coder-next` was added in the Feb 2026 expansion. Other Bedrock-hosted open-weight models (DeepSeek-V3.1, Llama 3.x, Mistral) aren't added here yet because we haven't verified an assumed-precision number — post in Kaggle Discussion if you have one you'd like added.

## What's not eligible

- **Generic OpenAI-compatible APIs that don't disclose `(model, quantization)`.** If the provider doesn't say what's under the hood, your VRAM number can't be verified.
- **Closed-weight models** (GPT, Claude, Gemini) anywhere in your system, including "just the planner."

## Requesting an addition

1. Post in the **Kaggle Discussion tab** with the HuggingFace model id, the quantization you want listed, and a one-line context note (what family, why it's interesting).
2. If you have a VRAM estimate, include it (params × bits / 8 + a few GB for KV cache at 16k context). If not, organizers will work one out from the model card.
3. Organizers add the row to this file, usually within a day or two. Once it's listed, your model is eligible for any team to use.

The numbers don't have to be perfect — see the note at the top about "approximate but good enough." We'd rather add a model with a slightly fuzzy estimate than block the catalog from growing.
