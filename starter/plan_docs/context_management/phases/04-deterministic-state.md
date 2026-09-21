# Phase 4: Add deterministic task state and completion guard v1

Status: proposed — **spec incomplete**
Depends on: Phase 1, Phase 2 (Phase 3 recommended)
Design: [`../design.md`](../design.md) §10 (deterministic subset), §19 (conservative flag), §20, §21, §23, §27 (v1), §33 invariants 6, 7, 14
Roadmap: [`../roadmap.md`](../roadmap.md)
Issue: —
Decisions: DEC-004

## Goal

Track only what code can derive without an LLM, render it into active context, keep the latest
failure in exact detail, and block the most obviously premature `TASK_COMPLETE`. Semantic fields
(objective, criteria, decisions, causes) are deliberately absent — they need Phase 5.

## Scope (draft)

- Deterministic subset of `TaskState`: commands run with exit codes, paths observable from command text, recognized test/build commands, dependency/environment-changing commands (as recorded strings), evidence references to event ids and output paths.
- Current-failure record (§20): exact command, exit code, error block, output path; replaced by a one-line resolution when a later run succeeds.
- Conservative `verification_may_be_stale` flag (§19) using the Phase 2 classifier.
- Completion guard v1 (§27, deterministic part): reject `TASK_COMPLETE` if the flag is set and nothing has run since the last state-changing command; message says exactly what is unverified. Capped so it cannot deadlock a run.
- Rendering into the active-context order of §23 within a token budget.

## Out of scope

- LLM-derived fields, compaction, per-criterion staleness, and the full guard (all Phase 5).

## Open questions

- **Without acceptance criteria, what counts as "verification"?** Any command after the last change is weak evidence. Is a guard that can only enforce "something ran" worth its extra turns? It may need to be dropped or made advisory.
- Reject cap: how many rejections before completion is allowed anyway?
- How to identify "the error" in a failed run generically (no per-language or per-task hardcoding)? Shares work with Phase 3 previews.
- Rendering format (JSON vs. prose) and budget (design suggests 2–6K for full state; this subset should be much smaller).
- Which §10 fields are truly derivable deterministically, and is the resulting state useful enough to justify its tokens?

## Exit criteria (draft)

- The latest unresolved failure stays available in actionable detail through window eviction.
- The agent cannot complete immediately after an unverified state-changing command.
- The guard cannot deadlock a run and shows no completion-rate regression vs. Phase 3.
- **Gate G2 measurement:** Tier A agent vs. Phase 0, per roadmap.

## Tests (draft)

Failure record lifecycle; flag set/clear; guard accept/reject/cap; evidence-reference validation; rendered state stays within budget.

## Notes

This replaces the earlier standalone "structured state" phase, which was not useful without an LLM
to populate it (DEC-004). Consider a `prototype` pass on the rendered state before finalizing.
