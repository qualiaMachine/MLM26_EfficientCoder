# Data layout

All challenge data ships via the Kaggle dataset attached to the competition, not in this repo (format spec: [DATA.md](../DATA.md)). This directory defines where you place it locally so the starter notebooks and scoring commands find it — image files are git-ignored.

```
data/
  eval/                    place the released evaluation set here (from the Kaggle dataset)
    images/                git-ignored
      <page_id>.jpg
    metadata.csv           page_id,category
    solution.csv           page_id,text,category — the released ground truth
```

`page_id` prefixes map to categories: `survey_*` → `survey_notes`, `kade_*` → `kade_letters`, `dominy_*` → `dominy_accounts`, `treaties_*` → `treaties_microfilm`.

`solution.csv` follows [`docs/transcription_conventions.md`](../docs/transcription_conventions.md) exactly — treat it as the authoritative worked example of what "faithful" means, and remember the deal: the evaluation pages are for measuring, not training ([RULES.md](../RULES.md)). Until the evaluation set is released, [`evaluation/example_solution.csv`](../evaluation/example_solution.csv) (fabricated text) keeps the tooling runnable.

**Do not commit UWDC images to this repo** — they are distributed only via the Kaggle dataset, alongside the appropriate rights statements.
