# Dataset Description

This competition has no dataset to download in the usual sense. The 89 benchmark tasks come from [Terminal-Bench 2.0](https://www.tbench.ai/) — they're public, and Harbor (the evaluation framework) pulls them automatically when you run it on your own machine. Scores are self-reported: you run the benchmark yourself and submit the resulting numbers in the format below.

Everything you need to get running — the starter agent, an end-to-end setup walkthrough, the approved model list, and the scoring rules — lives in the challenge repo: **https://github.com/qualiaMachine/MLM26_EfficientCoder** (start with `starter/docs/walkthrough.md`).

## Files

- **sample_submission.csv** — a one-row submission in the correct format. Copy it, replace the example values with your own, and upload it via Submit Prediction.

## Columns

- `id` — literally `1` (row identifier; required by the platform)
- `github_repo` — public repo containing your agent code
- `commit_ref` — tag or commit SHA of the exact code you ran (`git rev-parse HEAD`; see the Overview page for how to verify it)
- `model` — approved checkpoint id (see **Approved models** on the Overview page)
- `quantization` — `FP8`, `AWQ 4-bit`, or `GGUF Q4_K_M` (must match the approved entry for your model)
- `tb_score` — your mean Terminal-Bench reward across all 89 tasks, single attempt each, between 0 and 1
- `total_tokens` — input + output tokens summed across all 89 tasks, taken from Harbor's per-task `result.json`
- `gpu` — hardware you ran on (informational, not scored)
- `mean_wallclock_per_task` — informational, not scored
- `writeup_url` — link to your writeup posted in this competition's Discussion tab (required)

Your leaderboard score is computed from your own columns: `tb_score − 0.01 × (total_tokens / 1,000,000)`. Malformed rows — an unapproved model, an implausible token count, missing links — are rejected at upload with a visible error.

## Submitting properly

1. **Commit and push everything first.** Your `commit_ref` only captures code that's actually on GitHub — check `git status` is clean, then push.
2. **Get your `commit_ref`.** Either the commit SHA:
   ```
   git rev-parse HEAD
   ```
   or, friendlier, tag the submission and use the tag name:
   ```
   git tag v1.0-submission && git push origin v1.0-submission
   ```
3. **Verify it's fetchable.** Open `https://github.com/<you>/<repo>/tree/<commit_ref>` in a private/incognito browser window. If it loads, organizers can reconstruct exactly the code you ran; if it 404s, your repo is private or the commit isn't pushed.
4. **Pull your numbers from Harbor, not memory.** `tb_score` and `total_tokens` come from the `result.json` files of your full 89-task run — the exact commands are in the Overview page under *Computing your submission numbers*. Keep that `jobs/` directory: top-5 verification re-runs your agent and compares.
5. **Post the writeup before submitting.** The `writeup_url` column must point at your writeup in this competition's Discussion tab, so publish it first, then paste its URL into the CSV.
6. **Copy the header exactly.** Column names and order must match `sample_submission.csv`; spellings like `AWQ 4-bit` matter.
7. **Resubmit freely** (up to 5/day) — your most recent submission at the deadline is your final result.
