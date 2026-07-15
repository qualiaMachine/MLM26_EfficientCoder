# Dataset Description

This competition has no dataset to download in the usual sense. The 89 benchmark tasks come from [Terminal-Bench 2.0](https://www.tbench.ai/) — they're public, and Harbor (the evaluation framework) pulls them automatically when you run it on your own machine. Scores are self-reported: you run the benchmark yourself and submit the resulting numbers in the format below. How scoring, verification, and the writeup work is covered in the [Evaluation section](https://www.kaggle.com/competitions/efficient-coding-agent/overview/evaluation); everything you need to get running lives in the challenge repo: **https://github.com/qualiaMachine/MLM26_EfficientCoder** (start with `starter/docs/walkthrough.md`).

## Files

- **sample_submission.csv** — a one-row submission in the correct format. Copy it, replace the example values with your own, and upload it via Submit Prediction. Column names, order, and spellings (e.g. `AWQ 4-bit`) must match exactly.

## Columns

- `id` — always `1`. Kaggle scores a submission by matching its rows to the host's solution file on this column; since your submission is a single row, it's just this constant. (It's not your team name — Kaggle knows your team from the account that submits.)
- `github_repo` — public repo containing your agent code
- `commit_ref` — tag or commit SHA of the exact code you ran (see below)
- `model` — approved checkpoint id (Approved models list, Overview page)
- `quantization` — `FP8`, `AWQ 4-bit`, `GGUF Q4_K_M`, or `GPTQ-Int4` — write what you actually ran; GGUF and GPTQ-Int4 count as the model's AWQ 4-bit entry
- `tb_score` — your mean Terminal-Bench reward across all 89 tasks, single attempt each, between 0 and 1
- `total_tokens` — input + output tokens summed across all 89 tasks, from Harbor's per-task `result.json` (extraction commands: [Computing your submission numbers](https://www.kaggle.com/competitions/efficient-coding-agent/overview/evaluation))
- `gpu` — hardware you ran on (informational, not scored)
- `mean_wallclock_per_task` — informational, not scored
- `writeup_url` — link to your writeup in this competition's Discussion tab (required — post it before submitting)

## Getting your `commit_ref`

Commit and push everything (`git status` should be clean), then either use the commit SHA:

```
git rev-parse HEAD
```

or, friendlier, tag the submission and use the tag name:

```
git tag v1.0-submission && git push origin v1.0-submission
```

Confirm it's fetchable: open `https://github.com/<you>/<repo>/tree/<commit_ref>` in a private/incognito browser window. If it loads, organizers can reconstruct exactly the code you ran; if it 404s, your repo is private or the commit isn't pushed.
