# Approved models

The MLM26 leaderboard scores submissions by a function of **Terminal-Bench score**, **reported VRAM**, and **total tokens consumed**. To make the VRAM input verifiable without forcing every team to run nvidia-smi, we publish a canonical table of `(model, quantization)` → reported VRAM. **Submissions must use a model listed here.**

> Want to use a model that isn't listed? Open a pull request adding a row. PRs that include a HuggingFace link, the published quantization, and a quick VRAM justification (weights size + KV at 16k context) merge quickly — usually same-day during the semester. There is no penalty for being first to add a model; the leaderboard formula is the same for everyone.

## How "reported VRAM" is computed

Each row's reported VRAM is **weights + KV cache for a 16k context window + small overhead**, served via vLLM at single-batch concurrency. This is approximate by design — peak VRAM in practice varies with batch size, context length, and runner — but it's *consistent across teams*, which is what scoring requires.

```
Reported VRAM (GB) ≈ params × (bits / 8) / 1e9     # weights
                   + (n_layers × n_kv_heads × head_dim × 2 × 16384 × bytes_per_elem) / 1e9   # KV @ 16k
                   + ~2 GB headroom (activations, runner overhead)
```

For **MoE models**: use *total* params for the weights term, not active params — you have to load every expert into VRAM. Active params don't reduce memory, only compute.

For **GGUF/Q4_K_M** equivalents (Ollama users), use the AWQ 4-bit row for the same model — they're within ~10% of each other and the table's resolution doesn't care.

## Reported VRAM table

### Qwen2.5-Coder family

| Model | Quantization | Reported VRAM | Notes |
|---|---|---|---|
| `Qwen/Qwen2.5-Coder-0.5B-Instruct` | bf16 | 2 GB | Tiny — useful for testing the harness on CPU/iGPU. |
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
| `Qwen/Qwen3-Coder-Next` | bf16 | TBD | Recently released; PR with exact config. |
| `Qwen/Qwen3-Coder-480B-A35B-Instruct-FP8` | FP8 | 500 GB | Hosted-only (NRP, Bedrock-via-CMI). |
| `Qwen/Qwen3-Coder-480B-A35B-Instruct` | bf16 | ~1000 GB | Hosted-only. |

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
| `THUDM/GLM-4.5` | bf16 | TBD | PR with exact size when finalized. |

### Hosted-only / NRP managed LLM catalog

These models are too large to run on consumer or single-card research hardware. They're available via NRP's managed-LLM endpoint (UW participants via CILogon) and several are mirrored on NVIDIA build / Bedrock.

| Model | Quantization | Reported VRAM | Notes |
|---|---|---|---|
| `openai/gpt-oss-120b` | MXFP4 (native) | 70 GB | Fits on a single A100 80 GB. |
| `MiniMaxAI/MiniMax-M2.7` | FP8 (native) | 240 GB | 230B dense. NRP-hosted. |
| `nvidia/GLM-5.2-NVFP4` | NVFP4 | 380 GB | 744B MoE. NRP-hosted. |
| `Qwen/Qwen3.5-397B-A17B-FP8` | FP8 | 410 GB | NRP-hosted. |
| `moonshotai/Kimi-K2.7-Code` | Int4 (native) | 510 GB | 1T MoE. NRP-hosted. |

## License caveats

A couple of widely-discussed coder models have license terms that block competition use:

- **Codestral 22B / Codestral Mamba** — Mistral's non-production license. Not eligible.
- Anything with a "research only" or "non-commercial" tag that doesn't permit benchmark publication. PR-add only after confirming the license.

The rest of the rows above are MIT, Apache-2.0, or model-specific permissive licenses that permit benchmark submission.

## What's not eligible

- **Bedrock fully-managed inference** — AWS doesn't publish the GPU class or serving quantization for fully-managed endpoints, so a hosted call to `Qwen3-Coder-30B-A3B-Instruct` on Bedrock can't be mapped to a `MODELS.md` row. Use Bedrock freely for development, but pick a transparent endpoint for your final run.
- **Bedrock Custom Model Import (CMI)** — CMI does let you bring your own weights, but it's Provisioned-Throughput-only ($21–50/hr per model unit, 1- or 6-month commit), not a serverless pay-per-token option. Not practical for a hackathon team. If you want to use AWS, rent an EC2 or SageMaker GPU instance directly and run vLLM yourself — that's just self-hosting on cloud compute, which is fine.
- **Generic OpenAI-compatible APIs that don't disclose `(model, quantization)`.** Same problem. If the provider doesn't say what's under the hood, your VRAM number can't be verified.
- **Closed-weight models** (GPT, Claude, Gemini) anywhere in your system, including "just the planner."
- **Multi-GPU tensor parallelism within a single model's forward pass** *claimed as part of your footprint*. Picking a row that maps to >48 GB and serving it on a multi-GPU box is fine — your scored footprint is the table value, not your hardware.

## Requesting an addition

1. Open a PR editing this file. Add a row with the HuggingFace model id, quantization, reported VRAM, and a one-line note.
2. In the PR description, show your VRAM math (params × bits / 8 + KV estimate) or link to a model card that publishes the footprint.
3. We'll merge fast — generally same-day during the semester. Once merged, your model is eligible for any team.
