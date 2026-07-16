#!/usr/bin/env python3
"""Score a submission locally, exactly as the leaderboard will.

Usage:
    python evaluation/score_local.py --solution solution.csv --submission my_predictions.csv

solution.csv   columns: page_id, text, category
submission.csv columns: page_id, text

Prints overall macro CER (the leaderboard number) plus per-category CER and
diagnostic WER. Use it against your own calibration set — the hidden test
solution is, well, hidden.
"""

import argparse
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from metric import ParticipantVisibleError, page_wer, per_category_cer, score  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--solution", required=True, help="ground-truth CSV (page_id,text,category)")
    parser.add_argument("--submission", required=True, help="predictions CSV (page_id,text)")
    args = parser.parse_args()

    solution = pd.read_csv(args.solution, keep_default_na=False)
    submission = pd.read_csv(args.submission, keep_default_na=False)

    try:
        by_cat = per_category_cer(solution, submission)
        overall = score(solution, submission)
    except ParticipantVisibleError as e:
        print(f"submission error: {e}", file=sys.stderr)
        return 1

    merged = solution.merge(submission.drop_duplicates("page_id", keep="last"),
                            on="page_id", how="left", suffixes=("_ref", "_pred"))
    merged["text_pred"] = merged["text_pred"].fillna("")
    wer_by_cat = merged.assign(
        wer=[page_wer(p, r) for p, r in zip(merged["text_pred"], merged["text_ref"])]
    ).groupby("category")["wer"].mean()

    print(f"{'category':<24}{'pages':>6}{'CER':>9}{'WER':>9}")
    counts = solution.groupby("category")["page_id"].count()
    for cat in sorted(by_cat.index):
        print(f"{cat:<24}{counts[cat]:>6}{by_cat[cat]:>9.4f}{wer_by_cat[cat]:>9.4f}")
    print("-" * 48)
    print(f"{'macro CER (leaderboard)':<30}{overall:>9.4f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
