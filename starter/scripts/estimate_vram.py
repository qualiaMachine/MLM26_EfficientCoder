#!/usr/bin/env python3
"""Check a model — or a whole multi-model system — against the 96 GB budget.

    python scripts/estimate_vram.py Qwen/Qwen2.5-Coder-32B-Instruct-AWQ
    python scripts/estimate_vram.py Qwen/Qwen2.5-Coder-7B-Instruct-AWQ Qwen/Qwen3.6-27B-FP8

Reported VRAM = published checkpoint size (weights, as released)
              + KV cache for a 16k context at fp16, single batch
              + 2 GB headroom (activations, runner overhead)

Pass every model your submitted run serves. The budget is a *system*
budget: a planner and a coder running side by side spend the sum of
their reported VRAM, and the total must land at or under 96 GB.

Weights are taken from the actual file sizes on the HuggingFace Hub, so
quantized checkpoints (AWQ, GPTQ, FP8, MXFP4, ...) are handled
automatically — no parameter counting or bits math. KV cache comes from
the model's config.json. Needs network access to huggingface.co; no GPU,
no downloads beyond two small JSON requests per model.

This is a sanity check, not a measurement. Put the printed total on your
submission card as `reported_vram`. Exits nonzero if the system is over
budget, so it can also run in CI.

Don't compare against nvidia-smi — most serving stacks preallocate a
large memory pool at startup, so the reading reflects your GPU, not the
model.
"""
import argparse
import json
import sys
import urllib.error
import urllib.request

HUB = "https://huggingface.co"
KV_CONTEXT = 16384          # tokens, the accounting basis for reported VRAM
KV_BYTES_PER_ELEM = 2       # fp16
OVERHEAD_GB = 2.0
BUDGET_GB = 96.0            # the competition's system-wide memory budget


def fetch_json(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": "estimate-vram"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def weights_bytes(repo: str) -> int:
    """Sum the sizes of the checkpoint's weight files on the Hub."""
    info = fetch_json(f"{HUB}/api/models/{repo}?blobs=true")
    sizes = {}
    for f in info.get("siblings", []):
        name, size = f.get("rfilename", ""), f.get("size")
        if size and name.endswith((".safetensors", ".bin", ".gguf")):
            sizes[name] = size
    if not sizes:
        raise SystemExit(f"No weight files found in {repo} — is the repo id right?")
    # Prefer safetensors when a repo ships both formats
    st = {n: s for n, s in sizes.items() if n.endswith(".safetensors")}
    return sum((st or sizes).values())


def kv_cache_bytes(repo: str) -> tuple[int, dict]:
    cfg = fetch_json(f"{HUB}/{repo}/resolve/main/config.json")
    # VL / multimodal checkpoints nest the language model's config
    text = cfg.get("text_config", cfg)
    layers = text["num_hidden_layers"]
    kv_heads = text.get("num_key_value_heads") or text["num_attention_heads"]
    head_dim = text.get("head_dim") or text["hidden_size"] // text["num_attention_heads"]
    per_token = layers * kv_heads * head_dim * 2 * KV_BYTES_PER_ELEM  # 2 = K and V
    detail = {"layers": layers, "kv_heads": kv_heads, "head_dim": head_dim}
    return per_token * KV_CONTEXT, detail


def report(repo: str) -> float:
    """Print one model's breakdown and return its reported VRAM in GB."""
    try:
        w = weights_bytes(repo)
        kv, detail = kv_cache_bytes(repo)
    except urllib.error.HTTPError as e:
        raise SystemExit(f"HTTP {e.code} fetching {e.url} — private/gated repo or typo?")
    except (KeyError, urllib.error.URLError) as e:
        raise SystemExit(f"Could not read {repo}: {e}")

    w_gb, kv_gb = w / 1e9, kv / 1e9
    total = w_gb + kv_gb + OVERHEAD_GB
    print(f"{repo}")
    print(f"  weights (published checkpoint): {w_gb:6.1f} GB")
    print(f"  KV cache @ {KV_CONTEXT} tokens, fp16:  {kv_gb:6.1f} GB"
          f"  ({detail['layers']} layers x {detail['kv_heads']} KV heads x {detail['head_dim']} head_dim)")
    print(f"  headroom:                       {OVERHEAD_GB:6.1f} GB")
    print(f"  reported VRAM estimate:         {total:6.1f} GB")
    return total


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "repos", nargs="+",
        help="HuggingFace repo id(s) — pass every model your run serves concurrently",
    )
    parser.add_argument(
        "--budget", type=float, default=BUDGET_GB,
        help=f"memory budget in GB (default: {BUDGET_GB:.0f}, the competition budget)",
    )
    args = parser.parse_args()

    totals = [report(repo) for repo in args.repos]
    system_total = sum(totals)

    if len(totals) > 1:
        print(f"\nsystem total across {len(totals)} models: {system_total:.1f} GB")
    over = system_total > args.budget
    print(f"{args.budget:.0f} GB budget: "
          f"{'OVER by %.1f GB' % (system_total - args.budget) if over else 'OK'}")
    if over:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
