# Resources

A submitted run has two separate compute needs: **the machine that runs Harbor + your agent** (needs Docker host access), and **the endpoint that serves the model** (any OpenAI-compatible HTTP endpoint). They can be the same machine or different machines. Options for each below.

## Where to run Harbor + your agent (needs Docker)

Harbor spins up a fresh Docker container per Terminal-Bench task, so the machine you run `harbor run` from needs host Docker. That rules out Kaggle Notebooks and Google Colab — both explicitly block the privileged access Docker requires. Viable options:

- **Your own machine** — laptop, workstation, or lab machine with Docker Desktop (macOS/Windows) or Docker Engine (Linux). Cheapest option. Give Docker at least ~30 GB of disk for task images.
- **A rented Linux VM** — Lambda Labs, RunPod, Vast.ai, Hetzner, EC2, GCE. Any VM you have root on and can install Docker on. If you're also self-hosting the model on the same box, get one with a GPU that fits your approved model's reported VRAM.
- **UW–Madison hosted LLMs** — available to UW–Madison participants only. Details will be provided at the in-person kickoff.

## Where to serve the model (any OpenAI-compatible endpoint)

The model server is independent. Any endpoint your agent code can HTTP-POST to works.

**Hosted (no GPU required):**

- **NVIDIA API catalog** ([build.nvidia.com](https://build.nvidia.com/)) — Free, OpenAI-compatible endpoints for 100+ open-weight models including Qwen2.5-Coder-32B. Free tier: 1,000 inference credits on signup (up to 5,000 on request), shared ~40 RPM across all calls. Good for prompt iteration and small eval runs; the rate cap makes a full 89-task sweep slow but doable. 
- **Amazon Bedrock** — Pay-per-token, fully-managed `qwen3-coder-30b-a3b`, which counts as the approved `Qwen3-Coder-30B-A3B-Instruct-FP8` row (AWS doesn't formally publish serving precision; FP8 assumed). Bedrock's other models aren't on the approved list. [aws.amazon.com/bedrock](https://aws.amazon.com/bedrock/)

**Self-hosted on your own GPU or a rented one:**

- Any GPU large enough to fit the reported VRAM of your chosen approved model. The anchor (`Qwen3.6-27B-FP8`, 37 GB) wants a 48 GB card (RTX A6000, L40S) or an A100; the smaller rows cover 12–24 GB cards. Ollama or vLLM setup in [`starter/docs/byo_model.md`](https://github.com/qualiaMachine/MLM26_EfficientCoder/blob/main/starter/docs/byo_model.md).



