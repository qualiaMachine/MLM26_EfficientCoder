# Data

The scored test set is a small, curated sample of pages from four UW Digital Collections, chosen for diversity across hands, layouts (prose vs. tables), scan media (direct scan vs. microfilm), and languages (English and German). Collection backgrounds are in [`docs/collections.md`](docs/collections.md). There is **no provided training set** — see [RESOURCES.md](RESOURCES.md) for suggested public datasets and the public UWDC browsers for curating your own.

## What you get

The Kaggle dataset attached to the competition contains:

```
test/
  images/
    <page_id>.jpg          one image per test page
  metadata.csv             page_id + category (nothing that leaks the answer)
sample_submission.csv      every test page_id, placeholder text column
```

`metadata.csv` columns:

| column | meaning |
|---|---|
| `page_id` | unique page identifier, e.g. `survey_0012` |
| `category` | document category used for macro-averaging: `survey_notes`, `kade_letters`, `dominy_accounts`, `treaties_microfilm` |

Ground-truth transcriptions for the test pages are hidden; they follow the conventions in [`docs/transcription_conventions.md`](docs/transcription_conventions.md), which you should read before building anything — it defines exactly what your pipeline is being scored against (verbatim casing, punctuation, historical spelling; whitespace collapsed for scoring).

## Submission format

A CSV with one row per test page:

| column | meaning |
|---|---|
| `page_id` | must match `metadata.csv` exactly, every page present |
| `text` | your predicted transcription for the page |

Line breaks inside `text` may be encoded either as real newlines (in a properly quoted CSV field) or as the two-character escape `\n` — the metric collapses all whitespace runs to single spaces before scoring, so both are equivalent. See [`evaluation/sample_submission.csv`](evaluation/sample_submission.csv) for a valid file, and score yourself locally with:

```bash
python evaluation/score_local.py --solution <your_gt.csv> --submission <your_predictions.csv>
```

## Scoring

Per-page CER (Levenshtein distance over the ground-truth length, capped at 1.0), averaged within each category, then averaged across categories. Lower is better. Exact implementation: [`evaluation/metric.py`](evaluation/metric.py) — the same file the leaderboard runs.

An empty or missing prediction scores CER 1.0 for that page; dumping unrelated text scores no worse than 1.0 (the cap), so there is nothing to game by padding.
