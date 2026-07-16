# Ground-truth transcription conventions

> **Status: draft.** These conventions are what the metric implements today. They get finalized alongside the ground-truth transcriptions themselves; anything that changes will be announced in the Discussion tab. Owner: Chris.

Faithful transcription only works as a scored task if "faithful" is pinned down character-by-character. These conventions govern how the released reference transcriptions (eval/solution.csv) are written — and therefore what your pipeline is scored against. The design principle throughout: **the reference records what is on the page, verbatim; scoring is insensitive only to whitespace layout.**

## Verbatim, no normalization

- **Casing** as written. `Section` and `section` differ.
- **Punctuation** as written, including historical usage (`Mr` without period, long dashes, etc.).
- **Spelling** as written — historical and idiosyncratic spelling is preserved (`concenrs`, `favour`, `Octbr`). A pipeline that "corrects" the writer's spelling is making errors.
- **Abbreviations** as written, not expanded: `Sec.` stays `Sec.`, `do` (ditto) stays `do`.
- **Numerals** as written: `40` stays `40`, `forty` stays `forty`.

## Whitespace and line breaks

- Reference transcripts are UTF-8 plain text. Lines follow the visual lines of the page, separated by `\n`, in natural reading order.
- **For scoring, all whitespace runs (spaces, tabs, newlines) in both prediction and reference collapse to a single space**, and leading/trailing whitespace is stripped. You are never scored on how you encoded a line break — only on the characters.
- End-of-line hyphenation is kept as written (`sur-` at line end stays `sur-`); no de-hyphenation.

## Characters and scripts

- German material is transcribed to standard modern German orthography's *characters* (Latin alphabet with umlauts and ß as written), not transliterated: Kurrent letterforms map to their Latin equivalents, `ä ö ü ß` preserved.
- Ligatures are transcribed as their component letters unless a distinct Unicode character is standard.
- Unicode is NFC-normalized on both sides by the metric, so `ä` composed and decomposed are equivalent.

## Tables, diagrams, and non-text content

- Tabular field-note and ledger content is transcribed cell-by-cell in reading order (row-major), cells separated by whitespace — since scoring collapses whitespace, any reasonable cell separator (space, tab, newline, pipe-free) scores identically. Do not emit markdown table syntax (`|`, `---`); those characters count as errors unless on the page.
- Drawings, sketches, plat-map fragments, and blank regions are **not transcribed** — no `[sketch]` placeholders. Only text on the page appears in the reference.
- Struck-through text that remains legible is transcribed as written (the strikethrough itself is not encoded). Interlinear insertions are transcribed at their insertion point in reading order.

## Illegible content

- Characters the human transcriber could not read are recorded as `#`, one per illegible character where countable, in the reference. Evaluation pages are selected to keep illegible content minimal, so this should rarely matter.

## Open questions being finalized

- Reading-order rule for marginalia on the survey notebooks (transcribe-after-main-text vs. skip).
- Whether `#` illegibility markers are excluded from the reference length in scoring.
- Per-collection quirks discovered while producing the ground truth (will be documented here per collection).
