# Phase 2: Add state-free loop controls

Status: proposed — **spec incomplete**
Depends on: Phase 1
Design: [`../design.md`](../design.md) §25 (turn/context feedback only), §26 (signals computable from events alone), §29
Roadmap: [`../roadmap.md`](../roadmap.md)
Issue: —
Decisions: DEC-006

## Goal

Give the model targeted feedback about turn budget, context use, and unproductive repetition using
only the raw event history — no task state and no extra model calls. These behavioral controls do
not depend on compaction, so they come before it (DEC-006).

## Scope (draft)

- Turn and context-budget line each turn; a targeted warning at a configurable turn threshold (§25).
- Repeated-command detection: same command again with no intervening state-changing command.
- Consecutive read-only actions with no state change in between.
- Targeted, pattern-specific messages instead of the generic `NUDGE_MESSAGE` (§26).
- A generic `action_may_modify_state(command)` classifier, conservative direction (errs toward "may modify"). Phase 4 reuses it for the stale flag.

## Out of scope

- "Completed / remaining work" display (§25) and "no new recorded finding" (§26): both need task state (Phase 5).
- Detecting "returning to a rejected approach" (needs `failed_approaches`, Phase 5).

## Open questions

- Classifier design without any per-task rules (competition rule): command-text heuristics? What is an acceptable false-positive rate?
- Legitimate repeats (re-running tests after an edit) must not warn. Is "no intervening state-changing command" enough, or does it still misfire?
- Thresholds: how many repeats / read-only actions before warning? Tuned on which data?
- Do warnings change behavior for the better, or does the model ignore or over-obey them? Needs an on/off measurement.
- Where do messages sit in active context (last user turn vs. appended to the observation)?

## Exit criteria (draft)

- Repeated-command and consecutive-read-only counts are measured per run and drop vs. Phase 1 on long tasks.
- No completion-rate regression vs. Phase 1; controls are individually switchable.

## Tests (draft)

Classifier on representative commands; repeat detection with and without intervening modification; threshold boundaries; message selection.

## Notes

If nudges measure as neutral, ship only the telemetry (counts) and drop the messages.
