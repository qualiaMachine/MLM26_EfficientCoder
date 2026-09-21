# Phase 3: Offload large tool outputs

Status: proposed — **spec incomplete**
Depends on: Phase 1
Design: [`../design.md`](../design.md) §8, §12, §20 (preview selection); invariants 7, 8
Roadmap: [`../roadmap.md`](../roadmap.md)
Issue: —

## Goal

Keep large command output out of active context while keeping the full output recoverable inside
the task container, with failure-aware previews so current errors stay actionable.

## Scope (draft)

- Capture full output to a file in the task container when it exceeds the inline limit.
- Bounded previews: larger and error-focused for failures, small for successes.
- Observation metadata: exit code, original size, truncated flag, output path.
- Replace today's blunt first/last-half truncation (`MAX_OBSERVATION_CHARS`).

## Out of scope

- Deciding which findings matter (Phase 5).

## Open questions

- Capture mechanism: wrap the command (tee/redirect) or run a second `exec`? Wrapping can change exit-code and quoting semantics.
- Files written into the container may be visible to task verifiers or change directory listings. Where is safe, and is cleanup needed?
- Can the container's `/tmp` be read-only or wiped on some tasks? Fallback if the write fails?
- Failure-preview heuristics: how to find "the error" in a log without task- or language-specific hardcoding (competition rule)?
- Per-stream (stdout/stderr) vs. combined handling.
- Should the agent's prompt tell it about the output path, and how does that interact with token cost?

## Exit criteria (draft, from §31 Phase 2)

- Large outputs no longer dominate active context.
- Full output remains recoverable.
- Current errors remain detailed enough to diagnose.

## Tests (draft)

Offload threshold; preview selection with the error mid-log; success vs. failure previews; path recorded; write-failure fallback.

## Notes

Independent of Phase 2 (loop controls). Phase 4 reuses the failure-preview extraction built here.
