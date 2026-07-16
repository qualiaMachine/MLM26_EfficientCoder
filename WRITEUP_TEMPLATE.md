<!-- Maintainer note: Kaggle's writeup-template field is limited to 300
words (saving anything longer fails with an internal error). The template
configured on Kaggle is a ~160-word compact version of this file —
submission card plus a one-line-per-section outline — that links here for
full guidance.
Keep the submission card block below in sync with the Kaggle version and
the Submission Requirements section of the README. -->

# Writeup template

The **Kaggle Writeup is your submission** — create it with the "New Writeup" button on the competition page and submit it before the deadline. This template is a suggested structure for those who want guidance, not a form to fill out. Organize yours however you like and fill it with whatever insights you learned. The one real expectation: explain your learning journey along the way — what you tried, what worked, what didn't, and where you ended up. Aim for 2,500 words or fewer.

Why we require it: this is an educational challenge, and the writeup is how your work outlives the leaderboard. The goal is that another team can read it and reproduce your thinking, not just your score.

The one part that is **not optional** is the submission card — the block below, filled in with your values, at the top of your Writeup. It's what your score is computed from and how your result is verified. Everything after it is yours to shape.

---

### Submission card (required, at the top)

```
code_url: https://github.com/team/agent/tree/v1.0-submission
model: Qwen/Qwen2.5-Coder-32B-Instruct-AWQ
quantization: AWQ 4-bit
tb_score: 0.42
total_tokens: 1263800
leaderboard_score: 0.407
gpu: RTX A6000 48 GB
mean_wallclock_per_task: 3m 12s
```

- `code_url` — your public repo at the exact tag or commit SHA you ran (see below)
- `model` and `quantization` — must match an approved entry; quantization is `FP8`, `AWQ 4-bit`, or `GGUF Q4_K_M`
- `tb_score` — mean reward across all 89 tasks, 0–1
- `total_tokens` — `n_input_tokens + n_output_tokens` summed from Harbor's `result.json`
- `leaderboard_score` — `tb_score − 0.01 × (total_tokens / 1,000,000)`
- `gpu` and `mean_wallclock_per_task` — informational, not scored

Also add a **cover image** — Kaggle requires one to submit a Writeup; a screenshot of your `harbor view jobs` results works. Full details in the Submission Requirements section of the competition page.

The sections below are a starting point if a blank page is unhelpful:

---

### 1. Summary

> 3–5 sentences: what you built, the one or two ideas that mattered most, and your final numbers (Terminal-Bench score, total tokens, leaderboard score).

### 2. Architecture

> How your scaffold works. Walk through one task's lifecycle: what the model sees in its first prompt, how responses are parsed into commands, how the conversation/context is managed as turns accumulate, how errors are handled, and how the agent decides it's done. Name your approved model checkpoint and any serving details that matter (quantization, context length, sampling). A diagram is welcome but not required.

### 3. What we tried

> The experiments, roughly in the order you ran them — including the ones that failed or changed nothing. For each: what you changed, what you expected, what actually happened to the score. Negative results are explicitly in scope; they save the next team a week.

### 4. Results

> Final Terminal-Bench score, total tokens, and leaderboard score, plus the exact command and job name of the submitted run. If you looked at per-category or per-task results, what patterns did you see (e.g., strong on debugging, weak on system administration)?

### 5. Failure analysis

> Pick 2–3 tasks your agent fails and dig into why. Wrong plan? Lost context? Bad command parsing? Gave up early? Declared success prematurely? This section is usually the most instructive part of a writeup.

### 6. Borrowed and built

> What you took from others — starter code, other teams' published findings, papers, blog posts — with credit, and what you added on top. Building on shared work is encouraged; claiming it isn't.

### 7. Limitations and next steps

> What doesn't work, what you'd do with another month, and anything you suspect but couldn't verify.

### 8. Team contributions

> One line per team member on who did what. Solo teams: one line is fine.
