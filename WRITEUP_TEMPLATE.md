# Writeup template

Copy this file, replace each section's prompt with your content, post it in the competition's Discussion tab, and put the link in your submission card. The writeup is **required** — a submission without one covering all sections below is ineligible. It is checked pass/fail for completeness, not judged on prose: two clear paragraphs per section beat ten padded ones. Hard cap: 5,000 words.

Why we require it: this is an educational challenge, and the writeup is how your work outlives the leaderboard. The goal is that another team can read it and reproduce your thinking, not just your score.

---

## 1. Summary

> 3–5 sentences: what you built, the one or two ideas that mattered most, and your final numbers (Terminal-Bench score, total tokens, leaderboard score).

## 2. Architecture

> How your scaffold works. Walk through one task's lifecycle: what the model sees in its first prompt, how responses are parsed into commands, how the conversation/context is managed as turns accumulate, how errors are handled, and how the agent decides it's done. Name your approved model checkpoint and any serving details that matter (quantization, context length, sampling). A diagram is welcome but not required.

## 3. What we tried

> The experiments, roughly in the order you ran them — including the ones that failed or changed nothing. For each: what you changed, what you expected, what actually happened to the score. Negative results are explicitly in scope; they save the next team a week.

## 4. Results

> Final Terminal-Bench score, total tokens, and leaderboard score, plus the exact command and job name of the submitted run. If you looked at per-category or per-task results, what patterns did you see (e.g., strong on debugging, weak on system administration)?

## 5. Failure analysis

> Pick 2–3 tasks your agent fails and dig into why. Wrong plan? Lost context? Bad command parsing? Gave up early? Declared success prematurely? This section is usually the most instructive part of a writeup.

## 6. Borrowed and built

> What you took from others — starter code, other teams' published findings, papers, blog posts — with credit, and what you added on top. Building on shared work is encouraged; claiming it isn't.

## 7. Limitations and next steps

> What doesn't work, what you'd do with another month, and anything you suspect but couldn't verify.

## 8. Team contributions

> One line per team member on who did what. Solo teams: one line is fine.
