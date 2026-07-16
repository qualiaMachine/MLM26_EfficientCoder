# Archival Document Transcription Challenge

Faithfully transcribe handwritten and scanned archival documents into machine-readable text — scored on real collections from the UW–Madison Libraries. Hosted by [ML+X](https://hub.datascience.wisc.edu/communities/mlx/) at UW–Madison with the [UW Digital Collections Center](https://www.library.wisc.edu/dcc/). Kickoff Fall 2026 (dates TBD). Open to everyone.

---

## Overview

Institutional archives contain vast collections of documents that remain difficult to access at scale: handwritten manuscripts, scanned reports, typed historical records, forms, and mixed-format pages. Modern vision-language models and OCR systems have improved significantly, but faithful transcription of archival documents remains challenging across a wide range of conditions — handwriting variability, degraded scans, complex layouts, and multi-format documents.

This challenge focuses on one core problem: **faithful transcription of archival document images into machine-readable text**. The UW Libraries' digital collections provide the motivating use case and the evaluation data — nineteenth-century surveyors' field notes, German immigrant correspondence, craftsmen's account books, and treaty-era government documents. The goal is not reasoning, retrieval, or question answering. Participants are evaluated purely on how accurately they convert document images into text.

This is an **educational, collaborative challenge**. There are no cash prizes and no reason to hoard ideas. The point is to surface and share transcription pipelines that libraries and archives can actually deploy — share repos early, post findings to the Discussion tab, and build on each other's approaches. Every improvement one team publishes moves real archival collections closer to being readable, searchable, and accessible.

---

## Description

### Background

The UW Digital Collections Center holds many collections of handwritten and scanned historical documents, almost all digitized as high-resolution TIFF scans, and most with no transcription at all. Without text, these materials can't be searched, can't be read by screen readers, and can't be studied at scale. Staff time for manual transcription is scarce, so what the Libraries need is not a magic one-stop tool but a **repeatable, low-staff-effort process** for transcribing a given set of documents — exactly the kind of pipeline this challenge asks you to build and share.

There is no consensus on what that pipeline should look like. A traditional OCR pipeline (layout detection → line segmentation → recognition), an assembly of open-source tools like Kraken and PyLaia, a small vision-language model prompted page-by-page, or any of those fine-tuned on a small curated sample — all are viable, and they behave very differently across handwriting styles, languages, and layouts. How you build the pipeline matters as much as which model you pick.

### The task

Given a document image (a single page or scan), produce a faithful transcription.

Inputs may include:

- Handwritten archival manuscripts (the primary anchor use case)
- Printed and scanned institutional records
- Typed historical documents
- Mixed-format archival pages (forms, reports, long tables)
- Degraded or historical documents, including microfilm scans

Outputs must be:

- A full text transcription of the page
- In natural reading order where applicable
- Minimally normalized — no summarization, paraphrasing, or "cleanup" of historical spelling

This is strictly a transcription task — no question answering, no reasoning over content, no summarization.

**Model size constraint: every model in your submitted pipeline must be an open-weight model under 70B parameters.** This keeps winning solutions runnable on-prem without exotic hardware, which is the whole point for institutional adoption — a benchmark won by a 400B frontier model doesn't help a library actually deploy anything. Closed-weight API models (GPT, Claude, Gemini) are out of scope for the submitted run; see [RULES.md](RULES.md).

### Hard cases

The evaluation set emphasizes realistic conditions where current systems struggle:

- Handwriting variability across writers and decades (the core anchor use case)
- Degraded, faded, or low-contrast scans, including microfilm
- Irregular layouts and reading-order ambiguity
- Mixed handwritten and printed content on the same page
- Dense pages, hand-drawn tables, and structured field notes
- Historical spelling and formatting variation
- Multiple languages and scripts — including nineteenth-century German handwriting (Kurrent), which is a genuinely different script from English cursive

Strong solutions demonstrate robustness across document types rather than optimizing for one clean category.

### The evaluation data

The scored test set is built **entirely from UW Digital Collections materials** with verified ground-truth transcriptions — a deliberately small, curated, rights-cleared sample chosen for diversity across what actually varies in the archives: different hands, tabular vs. prose layouts, microfilm vs. direct scans, English and German. The source collections:

| Collection | What it is | Why it's hard |
|---|---|---|
| [Wisconsin Land Survey Field Notes](https://search.library.wisc.edu/digital/ASurveyNotes) | Original surveyors' field notebooks, 1830s–1860s | Hand-drawn tables, diagrams, terse abbreviations, pencil on weathered paper |
| [Max Kade Institute German letters](https://digital.library.wisc.edu/1711.dl/KadeLetters) | Immigrant correspondence in German, 19th–early 20th c. | Kurrent script — a different alphabet from modern German cursive |
| [Dominy Craftsmen account books](https://digital.library.wisc.edu/1711.dl/Dominy) | Woodworkers' and clockmakers' account books | Tabular ledger layouts, names, currency, dense entries |
| [Native American treaty documents](https://digital.library.wisc.edu/1711.dl/TreatiesMicro) | 19th-c. handwritten documents relating to Wisconsin treaties | Microfilm scans — low contrast, artifacts |

Public OCR/HTR benchmarks are well represented in VLM training data; a held-out test set of real institutional documents is what tells you whether a system actually generalizes. See [DATA.md](DATA.md) for the exact data format and [`docs/collections.md`](docs/collections.md) for collection details.

**No training set is provided — assembling one is part of the challenge.** In the era of pretrained vision-language models, training is increasingly optional; what every team does need is calibration data that resembles the test material. [RESOURCES.md](RESOURCES.md) lists public datasets (Bentham, BLN600, NARA record groups, IAM, the Alfred Escher German correspondence, and more) matched to the UW collections, plus the public UWDC image browsers if you want to curate your own samples. Depending on your approach — VLM or traditional pipeline, off-the-shelf or fine-tuned — you'll want very different data, so finding and gathering it is left to you.

---

## Starter materials

Three starter notebooks in [`notebooks/`](notebooks/) demonstrate the main solution families end-to-end, from document image to scored CER:

- [`01_traditional_pipeline.ipynb`](notebooks/01_traditional_pipeline.ipynb) — a from-scratch traditional OCR pipeline: layout detection → language routing → line recognition/transcription.
- [`02_open_source_tools.ipynb`](notebooks/02_open_source_tools.ipynb) — the same pipeline assembled from open-source components: [Kraken](https://kraken.re/) for segmentation, [PyLaia](https://gitlab.teklia.com/atr/pylaia) for recognition.
- [`03_vlm_transcription.ipynb`](notebooks/03_vlm_transcription.ipynb) — a small open-weight vision-language model prompted for page-level transcription.

If you're ambitious, fine-tune: even ~100 curated pages of the land-survey drawn tables could yield significant gains on that category. [`evaluation/`](evaluation/) has the exact scoring code used for the leaderboard, so you can score any prediction file locally before submitting.

---

## Data

Test images and the submission format are described in [DATA.md](DATA.md). Ground-truth transcription conventions — what "faithful" means character-by-character, and how line breaks and whitespace are handled — are pinned down in [`docs/transcription_conventions.md`](docs/transcription_conventions.md).

---

## Evaluation

### Scoring

The primary metric is **Character Error Rate (CER)**, macro-averaged across document categories — lower is better:

```
page CER      = levenshtein(prediction, ground_truth) / len(ground_truth)   (capped at 1.0)
category CER  = mean of page CERs within the category
leaderboard   = mean of category CERs
```

Macro-averaging across categories means a system has to perform across the board — acing clean English prose while failing the German letters or the microfilm scans will not produce a good score. Word Error Rate (WER) and per-category CER are reported as diagnostics in the starter tooling but do not affect ranking.

**Scoring is against the verbatim ground-truth transcription.** The whole point is faithful extraction, so casing, punctuation, and original historical spelling all count — no lowercasing, no punctuation stripping, no cleanup. The one normalization applied to both prediction and reference before comparison: runs of whitespace (spaces, line breaks) collapse to a single space. That makes scoring insensitive to how you encode line breaks, while everything else stays verbatim. Full details and the exact implementation: [`evaluation/metric.py`](evaluation/metric.py).

### Verification of top submissions

Leaderboard position comes from your submitted predictions, but **sharing the pipeline is part of participating, not an afterthought**: every submission must link a public GitHub repo containing the code that produced it. Before winners are announced, organizers code-review the **top 10** leaderboard entries — confirming the model-size limit is respected, that no human hand-transcribed the test images, and that results are reproducible from the posted code. That review gate is the real backstop; the rules up front are deliberately lightweight and honor-system. Irreproducible results, over-limit or closed-weight models, or manual transcription disqualify the entry.

---

## Submission Requirements

Submit a CSV of predicted transcriptions for the test images via the Kaggle "Submit Predictions" flow — format in [DATA.md](DATA.md), example in [`evaluation/sample_submission.csv`](evaluation/sample_submission.csv).

Alongside your predictions, post a **writeup** in the Discussion tab (suggested structure: [WRITEUP_TEMPLATE.md](WRITEUP_TEMPLATE.md)) containing your **submission card** — the code link and pipeline declaration that make your entry verifiable:

```
code_url: https://github.com/team/pipeline/tree/v1.0-submission
models: Qwen/Qwen2.5-VL-7B-Instruct
largest_model_params: 7B
external_data: Bentham line pairs (calibration); 120 self-transcribed survey-notebook lines (fine-tuning)
hardware: RTX 4090 24 GB
```

`code_url` must be a public repo pinned to the exact tag or commit you ran (`git tag v1.0-submission && git push origin v1.0-submission`). Open the link in a private browser window before submitting — if it 404s, your repo is private or the commit isn't pushed.

During the challenge, share early and often via the Discussion tab: post progress, share your repo, describe what's working and what isn't. Think of Discussion as an open lab notebook for the cohort.

---

## Tracks and Awards

**Open track** — the only track. All submissions compete together, ranked by leaderboard CER.

There are no cash or material awards — this is a non-monetary educational challenge (Kaggle Kudos only). Top teams may be invited to present at the ML+X showcase, and strong pipelines may be adopted by the UW Digital Collections Center for production transcription work — which is a better trophy anyway.

---

## Organizers

- **Chris Endemann** (endemann@wisc.edu), Research Cyberinfrastructure / DoIT, UW–Madison — challenge design, evaluation, coordination
- **Scott Prater**, UW Digital Collections Center, UW–Madison Libraries — domain lead; collections, ground truth, and what "correct" means
- **Kevin Chovanec**, Division of Extension, UW–Madison — datasets, baselines, and starter notebooks

Hosted by [ML+X](https://hub.datascience.wisc.edu/communities/mlx/) at the University of Wisconsin–Madison. Sponsor info: https://hub.datascience.wisc.edu/communities/mlx/sponsorship/

---

## Citation

```
Christopher Endemann, Scott Prater, Kevin Chovanec. Archival Document Transcription Challenge.
https://kaggle.com/competitions/<slug-tbd>. Kaggle.
```
