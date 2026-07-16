# Starter notebooks

Three notebooks, one per solution family, each running the full path from page image to scored CER. They are deliberately minimal — fork the one closest to your approach and rebuild it. All of them score with [`../evaluation/metric.py`](../evaluation/metric.py), the official scoring code.

| Notebook | Approach | Where it shines / struggles |
|---|---|---|
| [`01_traditional_pipeline.ipynb`](01_traditional_pipeline.ipynb) | From-scratch OCR pipeline: layout detection → language routing → line recognition | Every stage measurable and fixable; naive segmentation breaks on drawn tables |
| [`02_open_source_tools.ipynb`](02_open_source_tools.ipynb) | [Kraken](https://kraken.re/) segmentation + [PyLaia](https://gitlab.teklia.com/atr/pylaia) recognition | Production-grade historical-document tooling, very fine-tunable; more setup |
| [`03_vlm_transcription.ipynb`](03_vlm_transcription.ipynb) | Small open-weight VLM (Qwen2.5-VL-7B) prompted per page | Shortest path to a full submission; normalizes/hallucinates by default, weakest on Kurrent |

The families compose: chaining models is allowed as long as every model is open-weight and under 70B parameters (see [RULES.md](../RULES.md)) — e.g., Kraken segmentation feeding a VLM per region, or VLM fallback for low-confidence PyLaia lines.

> **Status: skeletons.** The pipeline structure, scoring hookup, and submission-file cells are in place; model-dependent cells are stubs marked `TODO(kevin)` and will be filled in (with baseline CERs per category) before launch.

## Fine-tuning

All three families benefit from fine-tuning on curated in-domain samples — even ~100 transcribed pages of the survey notebooks' drawn tables might yield significant gains on that category. The UW collections are publicly browsable for building your own training pairs (the evaluation pages are for measuring, not training); see [RESOURCES.md](../RESOURCES.md).
