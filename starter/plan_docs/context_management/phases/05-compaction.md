# Phase 5: Add semantic task state, compaction, and criteria-aware verification (conditional)

Status: proposed — **conditional on Gate G2; spec is a stub, do not refine yet**
Depends on: Phase 4, Gate G2 (see [`../roadmap.md`](../roadmap.md))
Design: [`../design.md`](../design.md) §9, §10 (semantic fields), §11, §14–§18, §19 (mature rules), §24, §25 (completed/remaining), §26 ("no new finding"), §27 (full guard), §34; invariants 3–6, 9–14
Roadmap: [`../roadmap.md`](../roadmap.md)
Issue: —
Decisions: DEC-004, DEC-007

## Goal

When active context nears its limit, fold older events into validated structured state via a
schema-constrained LLM call, advance a cursor, and rebuild active context. Also populate the
semantic fields Phase 4 cannot (objective, constraints, acceptance criteria, decisions, causes,
next step) and use them to upgrade Phase 4's blunt guard to per-criterion verification.

## Scope (draft)

Expected to be split into separate phases when G2 passes (DEC-007). Draft grouping:

**Semantic state and compaction**
- Semantic `TaskState` fields (§10) and who initializes objective/constraints/criteria.
- Soft/hard thresholds; forward-only compaction cursor; each event compacted once.
- Compaction prompt (§17): previous state + newly evicted events → schema-conforming state.
- Validation (§18): reject → keep previous state → retry or deterministic fallback.
- Telemetry for compaction cost and failures.

**Criteria-aware verification** (own flag, measured on/off)
- Per-criterion / per-file invalidation; `stale` on criteria and test results (§19).
- Full completion guard (§27): every criterion `passed` with current evidence.
- Completed/remaining display (§25); "no new recorded finding" signal (§26).

## Out of scope

- Retrieval (roadmap backlog, Gate G3).

## Open questions

- Which model compacts? Approved open-weight only, even for this call (competition rule). Same model as the agent?
- Does the hosted endpoint support schema-constrained/JSON output? If not, parse-and-repair strategy.
- Real thresholds given the actual context limit and the token cost of the compaction call itself.
- Which §18 checks are cheap and deterministic vs. need an LLM?
- Skip compaction on short tasks below a turn/size threshold?
- Deterministic-truncation fallback design.
- Does the full guard beat Phase 4's v1, or does it add rejections without adding correctness? What if the task states no explicit criteria — does it degrade to v1?
- Where should this be split? (Decide with G2 data, not now.)

## Exit criteria (draft)

- Old history leaves active context after being incorporated; each event compacted once.
- Constraints, changes, and unresolved bugs survive the §32 preservation tests.
- The agent cannot complete using verification made stale by later relevant changes; the guard cannot deadlock a run.
- **Beats the Tier A agent (Phase 4)** on completion or net score — otherwise do not ship.

## Tests (draft)

Compaction-preservation suite (§32): synthetic histories with decisions, multiple edits, conflicting hypotheses, resolved/unresolved bugs, a once-mentioned constraint; failure injection; per-criterion invalidation; guard accept/reject; premature-completion integration case.

## Notes

Merges the former "structured state", "compaction", and "criteria-aware verification" phases:
state without an LLM populating it has little content (DEC-004), and criteria-aware verification
only makes sense once criteria exist (DEC-007). The guard changes behavior, not just tokens, so
its completion-rate impact must be measured separately from compaction.
