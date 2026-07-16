# Evaluation

Single source of truth for scoring. There is no auto-scored leaderboard — you run this code against the released evaluation set and report the numbers on your writeup's submission card; organizers re-run the same code when verifying the top 10.

- **[`metric.py`](metric.py)** — macro-averaged CER (lower is better), verbatim comparison with whitespace collapsed. Entry point is `score(solution, submission, "page_id")`. Self-test: `python metric.py`.
- **[`score_local.py`](score_local.py)** — CLI: `python score_local.py --solution eval/solution.csv --submission my_predictions.csv`. Prints per-category CER, diagnostic WER, and the overall macro CER — the values that go on your submission card.
- **[`sample_submission.csv`](sample_submission.csv)** — the shape of a valid predictions file (`page_id,text`). The real page ids ship with the evaluation set in the Kaggle dataset.
- **[`example_solution.csv`](example_solution.csv)** — a fabricated mini ground-truth file (illustrative text only, **not** real UWDC transcriptions) so the tooling is runnable today. The real `eval/solution.csv` ships in the Kaggle dataset and follows [`../docs/transcription_conventions.md`](../docs/transcription_conventions.md).

Requires Python 3.9+ and pandas (`pip install pandas`).

Note the scoring properties worth knowing before you optimize:

- Per-page CER is capped at 1.0, so a garbage dump costs no more than an empty prediction.
- A missing `page_id` row counts as an empty prediction (CER 1.0), not a submission error.
- Categories are macro-averaged: with four categories, each is worth a quarter of your score regardless of page counts.
- Casing, punctuation, and historical spelling are scored verbatim; "correcting" the writer costs you characters.
- The evaluation pages are for measuring, not training ([RULES.md](../RULES.md)) — the numbers only mean something if everyone plays it straight.
