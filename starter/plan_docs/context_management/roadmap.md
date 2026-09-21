# Roadmap — Context Management and History Compaction

> **Rule:** implement only a phase whose status is `ready`, in order, one at a time. Do not
> implement later phases early, and do not treat `design.md` as a single task. A phase becomes
> `ready` only when its spec has no unresolved open questions and the user has approved it.

Statuses: `proposed` → `discussing` → `ready` → `implementing` → `completed`

## Structure: deterministic first, LLM compaction as a gated bet

Phases are ordered by what they *depend on*, not by topic. Everything that needs no extra model
call comes first; LLM-based compaction is only built if measurements say the cheaper agent still
loses runs to context growth (DEC-004). A phase boundary is a point where we measure and can stop
(DEC-007).

| Tier | Phases | Extra LLM calls? | Commitment |
|------|--------|------------------|------------|
| A — Foundation and deterministic wins | 0–4 | No | Committed, built in order |
| B — LLM compaction | 5 | Yes | **Conditional** on Gate G2 |
| Backlog — Retrieval | — | No (metadata only) | Not a phase; opened only if Gate G3 passes |

| # | Phase | Spec | Depends on | Status | Issue |
|---|-------|------|-----------|--------|-------|
| 0 | Establish baseline and price the tokens | [00](phases/00-baseline.md) | — | proposed | #1 |
| 1 | Separate raw history from active context; canonicalize actions | [01](phases/01-history-separation.md) | 0 | proposed | #2 |
| 2 | Add state-free loop controls | [02](phases/02-loop-controls.md) | 1 | proposed | #3 |
| 3 | Offload large tool outputs | [03](phases/03-output-offloading.md) | 1 | proposed | #4 |
| 4 | Add deterministic task state and completion guard v1 | [04](phases/04-deterministic-state.md) | 1, 2 (3 recommended) | proposed | #5 |
| 5 | Add semantic task state, compaction, and criteria-aware verification *(conditional)* | [05](phases/05-compaction.md) | 4, G2 | proposed | #6 |

Phases 2 and 3 are independent of each other and may be done in either order after Phase 1.

**Do not spend spec-refinement time on Phase 5 or the backlog until their gate passes.** Their
specs stay as stubs; discussing them early is how a plan grows past what the evidence supports.
When G2 passes, Phase 5 is expected to be split using the measurements in hand (DEC-007).

## Gates

- **G1 — after Phase 1.** Phase 1's active context *is* the rolling-window baseline (design §30 variant B), so it is measured against Phase 0 as part of that phase. Its canonicalization flag is also measured on/off. If dropping history or narration hurts completion, fix that before adding anything else.
- **G2 — after Phase 4, before Phase 5 becomes `ready`.** Re-measure the Tier A agent against Phase 0. Proceed only if runs still fail or lose meaningful score because of context growth or forgotten details (overflow, lost constraints, repeated work) *and* the Phase 0 token pricing shows the remaining cost is worth an extra model call per compaction. If Tier A already solves it, close Phase 5 and the backlog as not needed.
- **G3 — before the retrieval backlog item becomes a phase.** Traces from Phase 5 must show forgotten-detail failures that re-reading files or the offloaded logs does not fix (design §21: "preserve pointers, reread").
- **Every phase.** Re-run the Phase 0 measurement protocol. A phase that lowers completion rate is not done, whatever it does to tokens.

## Backlog — metadata retrieval (design §22)

Not a phase and has no spec or issue. Metadata/keyword retrieval of older exact evidence (file,
symbol, test, error type), with targeted reinsertion and budget tuning; the full §30 comparison
(variants A–E); embeddings only if metadata retrieval demonstrably fails. It is the most
speculative piece, and "not shipped" is a valid outcome. If Gate G3 passes, write a phase spec
(depends on Phase 5) and open an issue at that point.

## Mapping to `design.md` §31

`design.md` §31 lists seven rollout phases; this roadmap re-slices them by dependency.

| Roadmap phase | design.md source |
|---|---|
| 0 | (new) — prerequisite for §30 evaluation and for pricing token savings |
| 1 | §31 Phase 1 (raw/active separation, telemetry, recent window, canonicalization) |
| 2 | §25 turn/context feedback and §26 signals that need only events (§31 Phase 6, state-free part) |
| 3 | §31 Phase 2 |
| 4 | §31 Phase 3 (deterministic subset), §19 conservative stale flag, §20, §27 v1 (§31 Phase 5, deterministic part) |
| 5 | §31 Phase 3 (semantic fields), Phase 4, Phase 5 (criteria-aware part), §25 completed/remaining, §26 "no new finding" |
| Backlog | §31 Phase 7 |
