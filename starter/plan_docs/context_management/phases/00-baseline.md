# Phase 0: Establish context-management baseline

Status: proposed — **spec incomplete**
Depends on: —
Design: [`../design.md`](../design.md) §2, §29, §30 (variant A)
Roadmap: [`../roadmap.md`](../roadmap.md)
Issue: —

## Goal

Measure how the current full-history agent behaves so every later phase has something to be
compared against. No agent behavior changes in this phase.

## Scope (draft)

- Run the unmodified `BaselineAgent` on a fixed task set with a fixed model config.
- Record per task: reward, turns, input/output tokens, per-turn context size, max context size, whether the run hit the model context limit or turn limit.
- **Price the tokens:** convert baseline totals into leaderboard-score terms (`0.01 × tokens / 1M`, extrapolated to 89 tasks) so we know what a given token reduction is actually worth. Gate G2 uses this number.
- Write down the measurement protocol so it can be re-run identically after each phase.

## Out of scope

- Any change under `starter/agent/`.
- Building the rolling-window variant (that needs Phase 1).

## Open questions

- Which task set: the 10-task sample, the public subset (currently 3 placeholders), or both?
- What is the hosted model's real context limit? Every budget in `design.md` §24/§34 depends on it.
- Token counting: trust the endpoint's `usage`, or add a local tokenizer? (Approved models may not share a tokenizer with any available library.)
- How many repeats per task, given run-to-run variance? One run cannot distinguish a real regression from noise.
- Where do results live so later phases can diff against them (committed summary vs. `jobs/` only)?
- Can `starter/scripts/build_dashboard.py` already produce the per-turn context curve, or is a script needed?

## Exit criteria (draft)

- Baseline numbers exist for the chosen task set: completion rate, tokens, turns, max context.
- The protocol is documented well enough that someone else could reproduce it.
- We know whether context growth causes failures (context overflow, lost details) or only cost.
- The baseline token cost is expressed as a score penalty, so token savings can be compared with completion-rate changes on the same scale.

## Tests

None (measurement only).

## Notes

The last two exit criteria feed Gate G2 and decide whether Tier B (Phase 5) is built at all.
