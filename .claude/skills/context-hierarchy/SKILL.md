---
name: context-hierarchy
description: Build or refresh a leaves-to-root context hierarchy of nested CLAUDE.md files so Claude Code auto-loads the right context per directory
---

# Context Hierarchy

Recursive summarization, leaves to root, as nested `CLAUDE.md` files — Claude Code loads a
directory's `CLAUDE.md` automatically once it reads a file there, so context loading stops
being something anyone has to remember to do by hand.

## Why CLAUDE.md, not README.md

`README.md` is usually reserved for human-facing "how do I get started" docs. Using `CLAUDE.md`
for the hierarchy instead means it never competes with an existing README, and gets automatic
on-demand loading for free.

## Scope

Covers the source tree, not the repo root's own README/setup docs. The hierarchy's root is the
top of the actual codebase (e.g. a package or service directory), not necessarily the directory
Claude Code was launched from.

## Procedure

1. Start at the deepest source directories. For each, write a `CLAUDE.md`:
   - **Purpose** — one or two sentences
   - **Contents** — one line per file, what it does
   - **How it fits in** — its role relative to the parent
   - **Gotchas** — anything incomplete, a TODO, an invariant not to assume away
2. Confirm each file with the user before moving up — a quick check, not a rubber stamp.
3. One level up, write that directory's `CLAUDE.md` by reading the child files just written —
   not by re-reading their source. Re-deriving from source at every level defeats the
   compression.
4. Repeat to the root of the source tree.

## Refreshing

Don't regenerate the whole tree. Update only the directories that actually changed, and their
ancestors only if the change affects the parent's summary.

## Deliberate vs. automatic loads

When another skill needs to scope context explicitly (e.g. before a design discussion or a
zero-context test), read the relevant `CLAUDE.md` files directly rather than relying on
automatic on-demand loading — that's a bonus during implementation, not a substitute for
deliberately choosing what to load.
