# FAQ

**Can I use a closed-weight model just for planning, with a local model for execution?**
No. If part of your system calls GPT, Claude, or Gemini, it's out of scope.

**Can I use Amazon Bedrock?**
Yes, for the open-weight models it serves under a named checkpoint — e.g. the fully-managed pay-per-token `qwen3-coder-30b-a3b`, which counts as `Qwen3-Coder-30B-A3B-Instruct-FP8` (AWS doesn't officially state serving precision; FP8 assumed, corrected if AWS confirms otherwise). Bedrock's closed-weight models are out, as everywhere. **Bedrock Custom Model Import** is not viable (Provisioned-Throughput-only at $21–50/hr with a 1- or 6-month commit). If you want AWS for self-hosting, rent an EC2 or SageMaker GPU instance and self-host with vLLM — that's just cloud compute, fine like any other rented GPU. **But be extremely careful with costs:** GPU instances run $1–5+/hr and bill while idle, so a forgotten instance over a weekend is a three-figure surprise. Set a billing alarm before launching anything, stop instances the moment a run finishes, and consider the flat-rate marketplaces (Lambda, RunPod, Vast.ai) first — they're cheaper for this and easier to reason about.

**Which models can I use?**
Any open-weight checkpoint whose total reported VRAM fits the 96 GB budget, quantized no lower than 4-bit. There is no approved list to wait on — if a new open-weight coder drops next week, run `python starter/scripts/estimate_vram.py <repo-id>`, and if it fits, use it. Posting what you find in the Kaggle Discussion tab is encouraged (it saves everyone else the search), but it isn't an approval step.

**Can I fine-tune a model for this?**
Yes, as long as the result is open-weight and fits the budget. Document it in the writeup; weights must be either public or reproducible from the public base + your published LoRA/adapter. Fine-tuning on Terminal-Bench task solutions is task-specific hardcoding by another name and disqualifies.

**Should I just use the biggest model that fits in 96 GB?**
Not necessarily, and finding out is part of the challenge. Bigger checkpoints are slower per turn and usually more verbose, and every million tokens costs 0.01 of leaderboard score — so a model that solves one more task but takes three times the tokens can come out behind. Spending some of the budget on headroom instead (longer context, a second model, more turns per task) is a legitimate strategy. Report what you compared in the writeup.

**Can I use multiple models (e.g., a small planner + a larger coder)?**
Yes. The 96 GB budget is a system budget: sum the reported VRAM of every model you serve and the total must fit. List all of them on the submission card, with the combined `reported_vram`; token counts sum across models too.

**Can I submit my agent to the public Terminal-Bench leaderboard?**
Yes, please. It's independent of this challenge — a real leaderboard and a real artifact.

**Do I need to use the entire Terminal-Bench task set during the competition?**
No — work with whatever subset is useful for debugging. For the leaderboard, your submission must report results on all 89 tasks; after the deadline, organizers re-run the top 5 and review their code for task-specific hardcoding.

**My team is just me. / My team is five people.**
Both fine. Teams of 1–5. Reflect honestly on contributions in the writeup.

**I don't have a GPU.**
See [RESOURCES.md](https://github.com/qualiaMachine/MLM26_EfficientCoder/blob/main/RESOURCES.md) — NVIDIA's API catalog and the other hosted endpoints listed there work for development without local hardware. Whatever model you finally submit must be open-weight and within the 96 GB budget — note that a hosted endpoint still has to name the exact checkpoint it serves.

**I'm not at UW–Madison.**
Welcome. The challenge is fully open. You won't have access to the UW–Madison-only compute in [RESOURCES.md](https://github.com/qualiaMachine/MLM26_EfficientCoder/blob/main/RESOURCES.md), but the leaderboard is the leaderboard — you compete on equal footing.

**Will there be a live leaderboard during the competition?**
Standings are visible throughout: submissions are Kaggle Writeups with a submission card, public from the moment they're submitted, and organizers keep a standings post in the Discussion tab updated from the submitted cards. Scores are self-reported from your own Harbor runs — organizers spot-check periodically during the competition, and the top 5 get re-run and code-reviewed after the deadline, so submit numbers you can reproduce. You can also submit independently to the [public Terminal-Bench leaderboard](https://www.tbench.ai/leaderboard/terminal-bench/2.1).

**What's the relationship to the upstream Terminal-Bench project?**
We're users and fans — but this challenge is a separate event. We don't speak for the Terminal-Bench maintainers.


