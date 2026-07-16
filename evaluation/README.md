# Evaluation

Single source of truth for scoring. The Kaggle leaderboard runs [`metric.py`](metric.py); [`score_local.py`](score_local.py) wraps the same code so a local score IS the leaderboard score.

- **[`metric.py`](metric.py)** — macro-averaged CER (lower is better), verbatim comparison with whitespace collapsed. Kaggle entry point is `score(solution, submission, "page_id")`. Self-test: `python metric.py`.
- **[`score_local.py`](score_local.py)** — CLI: `python score_local.py --solution example_solution.csv --submission sample_submission.csv`. Prints per-category CER, diagnostic WER, and the overall macro CER.
- **[`sample_submission.csv`](sample_submission.csv)** — the shape of a valid submission (`page_id,text`). The real one, with actual test ids, ships in the Kaggle dataset.
- **[`example_solution.csv`](example_solution.csv)** — a fabricated mini ground-truth file (illustrative text only, **not** real UWDC transcriptions) so the tooling is runnable today. The real hidden solution follows [`../docs/transcription_conventions.md`](../docs/transcription_conventions.md).

Requires Python 3.9+ and pandas (`pip install pandas`).

Note the scoring properties worth knowing before you optimize:

- Per-page CER is capped at 1.0, so a garbage dump costs no more than an empty prediction.
- A missing `page_id` row counts as an empty prediction (CER 1.0), not a submission error.
- Categories are macro-averaged: with four categories, each is worth a quarter of your score regardless of page counts.
- Casing, punctuation, and historical spelling are scored verbatim; "correcting" the writer costs you characters.
