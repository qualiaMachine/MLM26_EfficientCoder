---
name: write-spec
description: Turn an agreed design into a durable, precisely-implementable spec, one file per feature
---

# Write Spec

Write the design down precisely enough that a zero-context test can succeed against it. Still
no code (see the `no-code-during-design` rule).

## Where it lives

`docs/plans/<feature-slug>.md` — one file per feature, kebab-case (e.g.
`add-search-filter.md`), kept forever. Never a single shared file that the next feature
overwrites — a design doc is only useful as history if later work doesn't erase it.

## Structure

- **Problem** — what's being solved, in a sentence or two
- **Technical Plan** — the agreed approach
- **Alternatives** — what else was considered, and why it lost
- **Detailed Implementation** — specific enough to name what changes and how

## The test to write against

Could someone (or some fresh session) with *zero* memory of this conversation implement this
correctly from the doc alone, using only the context hierarchy for architecture context? If the
doc leans on something only this conversation knows, write it down or cut it.

## Mechanics

Draft the content in conversation first. In Plan Mode, pull the plan into an editor (e.g.
`Ctrl+G`) rather than writing the file directly — Plan Mode blocks file writes by design, and
that's correct here too.
