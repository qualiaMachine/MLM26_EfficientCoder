# starter/plan_docs/context_management/

## Purpose
Planning docs for the **Context Management and History Compaction** feature: stop resending the
agent's full transcript every turn by separating an append-only raw history from a bounded,
deliberately built active context. Docs only — no source lives here.

## Contents
- `design.md` — the full target architecture, invariants, and definition of done (§ numbered). **Not an implementation request.**
- `roadmap.md` — phase list, dependencies, and status (`proposed | discussing | ready | implementing | completed`). Source of truth for what may be built now.
- `decisions.md` — append-only log of accepted decisions (`DEC-NNN`). Check it before re-opening a settled question.
- `phases/00-…05-*.md` — one spec per phase (Phase 5 is a conditional stub). Starts incomplete; refined in discussion; becomes the implementation contract once its roadmap status is `ready`.

## How to work here
1. Read `roadmap.md` first. Find the lowest-numbered phase that is not `completed`.
2. Read `design.md` only for the sections that phase cites, plus `decisions.md`.
3. Implement **only** a phase whose status is `ready`. Never implement a later phase early, and never treat `design.md` as one big task. Phase 5 is conditional on measurement gate G2, and retrieval is a backlog item behind G3 (both in `roadmap.md`): leave them as stubs and do not spend discussion time on them until the gate passes.
4. If a phase is `proposed`/`discussing`, the job is to refine its spec (use the `design-discussion` / `write-spec` skills), not to write code. The repo's no-code-during-design rule applies. I will use the grill me skills for further discussions and clarifications and I would like for you to ask me one question at a time and not list all questions at once. 
5. After any meaningful discussion, write the outcome to the phase spec and/or `decisions.md` before ending the session — chat history is not the record. Keep the two from duplicating each other: the phase spec says **what to build**; `decisions.md` says **why, and what was rejected**. A spec references `DEC-NNN` instead of restating it.
6. When a phase's status changes, update `roadmap.md` and its GitHub issue.

## How it fits in
Code changes land in `starter/agent/` (`agent.py` loop, `tools.py`, `prompts.py`, `llm.py`); see `starter/agent/CLAUDE.md`. Measurement uses `starter/scripts/` and Harbor's `jobs/`. Each phase has a GitHub issue under the milestone **Context Management and History Compaction**; issues link here, not the other way round.

## Gotchas
- Competition rules bind every phase: no task-specific hardcoding, approved open-weight models only (this includes any model used for compaction), endpoint config only via `.env`/`.env.op`. Root `CLAUDE.md` has the details.
- Scoring is `TB_score − 0.01 × (total_tokens / 1M)`, and compaction calls count as tokens. Success is completion rate first, tokens second (`design.md` §3). A simple rolling-window baseline (variant B, §30) is the bar structured compaction must beat.
- `context.metadata` must stay updated every turn (see `starter/agent/CLAUDE.md`); raw history must remain the thing that gets written there.
- Phase numbers here (0–5) do **not** match the "Phase 1–7" rollout list in `design.md` §31; `roadmap.md` has the mapping. Phases are ordered by dependence on an LLM call (DEC-004): 0–4 are deterministic and built in order; 5 and the retrieval backlog item are gated bets. A phase boundary is a point where we measure and can stop (DEC-007).
- Behavior-changing pieces (canonicalization, nudges, completion guard) must be individually switchable and measured on/off — a change that lowers completion rate is not done, whatever it does to tokens.
