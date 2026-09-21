# Decisions — Context Management and History Compaction

Append-only. New decisions get the next `DEC-NNN`. To change a decision, add a new entry that
supersedes it and set the old one's status to `Superseded by DEC-NNN`; do not rewrite history.

Entry format: Status (`Proposed | Accepted | Superseded`), Phase, Date, then Decision / Rationale /
Alternatives Considered / Why Rejected / Consequences.

---

## DEC-001: Plan docs live in `starter/plan_docs/context_management/` with a CLAUDE.md entry point

Status: Accepted  
Phase: All  
Date: 2026-09-21

### Decision

Keep the feature's design, roadmap, decisions, and per-phase specs under
`starter/plan_docs/context_management/`. The entry point is a `CLAUDE.md` (not a `README.md`) so
Claude Code loads it automatically when working in that directory.

### Rationale

`starter/plan_docs/` already held the planning docs, and the repo's other directories use the
nested-`CLAUDE.md` convention for auto-loaded context.

### Alternatives Considered

1. `docs/context-management/` at the repo root, with a `README.md`.
2. `starter/docs/` (existing human-facing guides).

### Why Rejected

1. There is no root `docs/`; it would split planning docs across two places. A `README.md` is not auto-loaded.
2. `starter/docs/` holds finished how-to guides, not in-flight plans.

### Consequences

A subdirectory `CLAUDE.md` loads when files in that directory are read, not at session start. To
load it every session, reference it from `starter/CLAUDE.md`.

---

## DEC-002: Eight phases (0–7) instead of the seven in `design.md` §31

Status: Superseded by DEC-004 and DEC-007 (only the baseline-phase idea stands; the slicing and the count changed to six phases, 0–5)  
Phase: All  
Date: 2026-09-21

### Decision

Track the work as Phases 0–7, one GitHub issue each, mapped to `design.md` §31 in `roadmap.md`.

### Rationale

A baseline-measurement phase is needed before any change can be judged (`design.md` §30), and
finer phases give smaller, independently reviewable contracts.

### Alternatives Considered

1. Use §31's seven phases as written.

### Why Rejected

§31 has no baseline phase, and its Phase 1 bundles history separation with canonicalization.

### Consequences

Numbers in issues and specs refer to the roadmap, not §31. Both are cross-referenced in `roadmap.md`.

---

## DEC-003: Maintain separate raw and active histories

Status: Accepted  
Phase: 1  
Date: 2026-09-21

### Decision

Keep a complete append-only raw event history and construct active model messages separately.

### Rationale

Compaction must reduce model input without destroying audit and evaluation data (`design.md` §5,
invariants 1 and 15).

### Alternatives Considered

1. Mutate the existing `messages` list in place.
2. Keep the full history and add a summary on top.

### Why Rejected

Mutating the only history destroys evidence. Sending the full history with a summary does not
reduce context usage.

### Consequences

Later features must build active context through the context manager rather than appending
directly to raw history. Anything that reads `context.metadata["messages"]` (e.g.
`starter/scripts/build_dashboard.py`) must be revisited in Phase 1.

---

## DEC-004: Slice phases by LLM dependence; make LLM compaction a gated bet

Status: Accepted (the Phase 5–7 layout it describes was changed by DEC-007; the tiering and gates stand)  
Phase: All (esp. 4–7)  
Date: 2026-09-21

### Decision

Order phases by what they depend on. Tier A (Phases 0–4) needs no extra model call and is built in
order. Tier B (Phases 5–6, semantic state and compaction) and Tier C (Phase 7, retrieval) are
conditional on measurement gates G2 and G3 in `roadmap.md`. Phase 4 holds only the deterministic
state and completion guard v1; the former standalone "structured state" phase is merged into
Phase 5. Phase 0 also prices baseline tokens in score terms.

### Rationale

The first draft made structured state (old Phase 4) a standalone phase, but deterministic code
cannot extract objectives or acceptance criteria from free text, so it would have little content
until an LLM populates it. More generally, compaction only pays off if context growth is actually
costing completion rate or meaningful score, and the scoring formula makes token savings small
next to capability. Evidence should decide whether the expensive phases happen.

### Alternatives Considered

1. Keep eight topic-ordered phases, all committed (the DEC-002 slicing).
2. Build LLM compaction unconditionally and evaluate it afterwards.

### Why Rejected

1 commits weeks of work to Phases 4–7 on assumption and leaves a standalone state phase with
almost no content. 2 is the same commitment with the evidence arriving too late to change course.

### Consequences

Specs for Phases 5–7 stay stubs until their gate passes. Gate G2 needs Phase 0's token pricing and
Phase 4's measurements. The design document is unchanged; only the order and commitment differ.

---

## DEC-005: Fold canonicalization into Phase 1, behind its own flag

Status: Accepted  
Phase: 1  
Date: 2026-09-21

### Decision

Canonicalization ships in Phase 1 with the raw/active split. It has its own config flag so it can
be measured on and off independently of the window.

### Rationale

Canonicalization is a small deterministic function of an action event and was too small to justify
its own contract. But dropping the model's narration may change its behavior (models imitate their
own prior turns), and that effect would be confounded with the window change unless separately
switchable.

### Alternatives Considered

1. Keep canonicalization as a standalone phase (previous Phase 2).
2. Fold it into Phase 1 with no flag.

### Why Rejected

1 is process overhead for a few dozen lines. 2 makes it impossible to tell which change hurt if
completion drops.

### Consequences

Phase 1 is somewhat larger. Its Gate G1 measures variant B with canonicalization on and off. If it
measures as harmful, it ships off.

---

## DEC-006: Move state-free loop controls to Phase 2

Status: Accepted  
Phase: 2  
Date: 2026-09-21

### Decision

Turn/context feedback (§25) and the §26 signals computable from raw events alone (repeated
command, consecutive read-only actions) become Phase 2, directly after Phase 1. Signals that need
task state — completed/remaining work, "no new finding", returning to a rejected approach — stay
with the state phases (5–6).

### Rationale

These controls do not depend on compaction and are likely cheaper and lower risk than it. Bundling
them with retrieval delayed them behind the most speculative work. The split is honest: only the
state-free subset can move early.

### Alternatives Considered

1. Leave them in the last phase with retrieval (original grouping).
2. Move all of §25/§26 early.

### Why Rejected

1 delays cheap wins behind gated work. 2 is impossible: some signals need state that does not exist
until Phase 4–5.

### Consequences

Phase 2 introduces a generic `action_may_modify_state` classifier that Phase 4 reuses for the stale
flag. Because nudges change behavior, they are individually switchable and measured; if they are
neutral, only the telemetry ships.

---

## DEC-007: Collapse the conditional back end to one Phase 5; demote retrieval to a backlog item

Status: Accepted  
Phase: 5 and backlog  
Date: 2026-09-21

### Decision

Reduce the roadmap from eight phases (0–7) to six (0–5). Phase 5 absorbs semantic task state,
compaction, and criteria-aware verification (the former Phases 5 and 6). Metadata retrieval (the
former Phase 7) is no longer a phase: it is a backlog section in `roadmap.md` with no spec or
issue until Gate G3 passes. Phases 0–4 are unchanged. In DEC-004 and DEC-006, "Phase 6" now means
Phase 5, and "Phase 7" means the retrieval backlog item.

### Rationale

A phase boundary is a point where we measure and can stop. Phases 0–4 each are. The former
Phases 5–7 sit behind gates G2/G3, do not exist yet, and their boundaries were guesses: criteria-aware
verification only makes sense once Phase 5 has produced criteria, and retrieval may never ship.
Separate specs and issues for work we cannot yet scope are overhead.

### Alternatives Considered

1. Keep eight phases with Phases 5–7 as conditional stubs (DEC-004 layout).
2. Also merge front-end phases (0 into 1, or 2/3 into 4).

### Why Rejected

1 keeps trackers for work that may never be built. 2 puts independent changes in one measurement, so
a completion-rate drop cannot be attributed, and it delays cheap wins behind riskier work; Phase 0
is also easy to skip if it is not its own deliverable.

### Consequences

The merged Phase 5 is large and is expected to be split again once G2 passes and there is real data
to split on. Criteria-aware verification (guard v2) must carry its own flag and on/off measurement,
since it no longer has its own phase boundary. Six GitHub issues instead of eight; retrieval gets
one only if G3 passes.
