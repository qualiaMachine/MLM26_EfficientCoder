# Maintainer notes

Internal working notes for organizers (Chris, Scott, Kevin). Participants can ignore this file — nothing here changes the rules.

## Decision log

Decisions settled in the planning doc + email thread (June–July 2026):

- **Challenge dataset is UW samples only.** External public datasets moved from "benchmark components" to a suggested-resources section participants pull themselves. Rationale: effort savings, and assembling a calibration set becomes part of the challenge itself. Fallback if in-house sample prep falls flat: pivot back to building in auxiliary data (Bentham/IAM subsets).
- **Ground truth strategy:** at least one transcribed sample from as many collections as staff time allows this year; Sternberger & Seifert letters already have MKI Kurrent-group transcriptions (free GT for the Kade category). Sample selection aims for diversity: different hands, tabular vs. prose, microfilm vs. direct scans. Scoring may weight UW docs more heavily if needed — currently moot since the eval set is 100% UW.
- **Resources list:** Bentham, BLN600, NARA RG 109 as best matches; IAM kept as calibration-only with its modern-handwriting limitation noted; Alfred Escher correspondence added for period German (Kurrent).
- **Metric:** CER primary, verbatim (no normalization), whitespace collapsed; macro-average across categories; WER as diagnostic only. Cap per-page CER at 1.0.
- **Rules:** open-weight <70B per model, honor-system up front, top-10 code review before winners announced; code link (public GitHub, pinned commit) required with every submission; no prize, collaborative framing.
- **Starter notebooks (Kevin):** (1) traditional pipeline from scratch (layout detection → language routing → recognition), (2) open-source tools (Kraken segmentation + PyLaia recognition), (3) small open-weight VLM. Optional fine-tuning angle: ~100 curated drawn-table pages from the survey notebooks.

## Open questions

- [ ] Reading-order convention for marginalia (survey notebooks) — Chris, with Scott
- [ ] Whether `#` illegibility markers count toward reference length in scoring — Chris
- [ ] Final collection list: do all four categories get enough GT pages this year, or does a category drop? — Scott
- [ ] Kaggle slug + launch dates (kickoff Fall 2026) — Chris
- [ ] License file for this repo (code MIT? UW image derivatives need their own rights statement) — Chris + Scott
- [ ] Whether hosted endpoints serving named open-weight checkpoints count for the *submitted* run or prototyping only (FAQ currently says prototyping; on-prem spirit suggests submitted runs should at least be reproducible on-prem) — Chris

## Launch checklist

- [ ] GT pages transcribed + double-checked per `docs/transcription_conventions.md`; conventions doc updated with per-collection quirks and de-drafted
- [ ] Package Kaggle dataset (`test/images/`, `metadata.csv`, `sample_submission.csv`) — well under the 20 GB cap; JPEG derivatives of the TIFFs
- [ ] Build real `solution.csv` (page_id, text, category, Usage) with Public/Private split; upload metric from `evaluation/metric.py`; verify Kaggle scores match `score_local.py` on a dummy submission
- [ ] Kevin: fill in the three starter notebooks against the released sample pages; run end-to-end on Kaggle Notebooks free tier; record baseline CERs per category (also gives us the difficulty read)
- [ ] Baseline comparison table (Tesseract / Kraken+PyLaia / small VLM) posted to Discussion at launch
- [ ] Copy README sections to the Kaggle Overview/Data tabs; RULES.md to the rules section
- [ ] Everyone joined the ML+X Kaggle organization (invite link in the planning doc — not committed here)
- [ ] Announce soft launch; official UW–Madison kickoff Fall 2026

## Repo conventions

- README.md mirrors the Kaggle home-page section layout (same convention as the Efficient Coder repo); DATA.md is the Data tab; RULES.md the rules section.
- `evaluation/metric.py` is the single source of truth for scoring — Kaggle metric and `score_local.py` both use it; it carries a self-test (`python evaluation/metric.py`).
- Placeholders that must be resolved before launch are marked `TBD` or tracked above.
