# Competition rules

## 1. Competition sponsor

This challenge is organized by the [ML+X](https://mlx.wisc.edu/) community at UW–Madison with support from its sponsors.

## 2. Prizes

This is a non-monetary educational challenge. There are no cash or material prizes. Top teams may be invited to present at the ML+X showcase or contribute to open-source outputs.

## 3. Team limits

- Maximum team size: 5 participants.
- Team mergers are allowed as long as the merged team stays within the submission limits and the maximum team size.

## 4. Submission integrity

- **Approved open-weight models only.** Your submitted run must use a model listed in [`MODELS.md`](https://github.com/qualiaMachine/MLM26_EfficientCoder/blob/main/MODELS.md). Closed-weight models (GPT, Claude, Gemini) are out of scope anywhere in your system, including "just the planner." Development and prototyping on any model is fine — the rule binds the submitted run.
- **No task-specific hardcoding.** One system prompt, one agent loop, no per-task branching, no hardcoded solutions or prompts written for individual tasks. Detecting task *categories* and adjusting strategy is fine. All 89 tasks are public; the top 5 submissions are code-reviewed after the deadline, and hardcoding disqualifies.
- **Scores must be reproducible.** Leaderboard scores are self-reported from your own Harbor runs. Your submission card points at a public repo and commit; organizers re-run the top 5 with the declared model and check the reported score and token count. Significant discrepancies disqualify.
- **Writeup required.** A submission without a writeup covering all sections of [`WRITEUP_TEMPLATE.md`](https://github.com/qualiaMachine/MLM26_EfficientCoder/blob/main/WRITEUP_TEMPLATE.md) is ineligible. It is checked pass/fail for completeness, not graded.

## 5. Submission limits

- Up to 5 submissions per day.
- Your most recent submission at the deadline is your final result.

## 6. Benchmark data

Terminal-Bench 2.0 tasks come from the upstream [Terminal-Bench project](https://tbench.ai) under its own license. This challenge is a separate event; we don't speak for the Terminal-Bench maintainers.

## 7. License

Submission repos must be public and licensed MIT or Apache 2.0.
