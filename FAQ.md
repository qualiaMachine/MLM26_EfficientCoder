# FAQ

**Can I use a closed-weight model just for planning, with a local model for execution?**
No. If part of your system calls GPT, Claude, or Gemini, it's out of scope.

**Can I use Amazon Bedrock?**
Narrowly, yes. The fully-managed pay-per-token `qwen3-coder-30b-a3b` counts as the approved `Qwen3-Coder-30B-A3B-Instruct-FP8` entry (AWS doesn't officially state serving precision; FP8 assumed, corrected if AWS confirms otherwise). Bedrock's other models aren't on the approved list. **Bedrock Custom Model Import** is not viable (Provisioned-Throughput-only at $21–50/hr with a 1- or 6-month commit). If you want AWS for self-hosting, rent an EC2 or SageMaker GPU instance and self-host with vLLM — that's just cloud compute, fine like any other rented GPU. **But be extremely careful with costs:** GPU instances run $1–5+/hr and bill while idle, so a forgotten instance over a weekend is a three-figure surprise. Set a billing alarm before launching anything, stop instances the moment a run finishes, and consider the flat-rate marketplaces (Lambda, RunPod, Vast.ai) first — they're cheaper for this and easier to reason about.

**The model I want isn't on the approved list. What do I do?**
The list is deliberately short — the competition is about the scaffold, not model shopping. If you think a model materially changes what's possible (a new open-weight coder release, a hardware tier the list doesn't serve), post the case in the Kaggle Discussion tab with the HuggingFace link and quantization. Organizers respond within a day or two.

**Can I fine-tune a model for this?**
Yes, if the base is an approved model. The fine-tune counts as its base model's entry. Document it in the writeup; weights must be either public or reproducible from the public base + your published LoRA/adapter.

**Can I use multiple models (e.g., a small planner + a larger coder)?**
Yes, as long as every model involved is on the approved list. The submission card carries the largest model's entry; token counts sum across all models, and you should be ready to defend the setup when your submission is verified.

**Can I submit my agent to the public Terminal-Bench leaderboard?**
Yes, please. It's independent of this challenge — a real leaderboard and a real artifact.

**Do I need to use the entire Terminal-Bench task set during the competition?**
No — work with whatever subset is useful for debugging. For the leaderboard, your submission must report results on all 89 tasks; after the deadline, organizers re-run the top 5 and review their code for task-specific hardcoding.

**My team is just me. / My team is five people.**
Both fine. Teams of 1–5. Reflect honestly on contributions in the writeup.

**I don't have a GPU.**
See [RESOURCES.md](https://github.com/qualiaMachine/MLM26_EfficientCoder/blob/main/RESOURCES.md) — NVIDIA's API catalog and the other hosted endpoints listed there work for development without local hardware. Whatever model you finally submit must be on the [approved list](https://www.kaggle.com/competitions/efficient-coding-agent/overview).

**I'm not at UW–Madison.**
Welcome. The challenge is fully open. You won't have access to the UW–Madison-only compute in [RESOURCES.md](https://github.com/qualiaMachine/MLM26_EfficientCoder/blob/main/RESOURCES.md), but the leaderboard is the leaderboard — you compete on equal footing.

**Will there be a live leaderboard during the competition?**
Yes. Submissions are a standardized `submission.csv` uploaded to Kaggle; the leaderboard recomputes scores as they land, and you can resubmit throughout the competition. Scores are self-reported from your own Harbor runs — the top 5 get re-run and code-reviewed after the deadline, so submit numbers you can reproduce. You can also submit independently to the [public Terminal-Bench leaderboard](https://tbench.ai/leaderboard).

**What's the relationship to the upstream Terminal-Bench project?**
We're users and fans — but this challenge is a separate event. We don't speak for the Terminal-Bench maintainers.


