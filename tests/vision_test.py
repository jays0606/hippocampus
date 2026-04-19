#!/usr/bin/env python3
"""Phase A.4 — Vision smoke test on Gemma 4 E2B.

The single highest-risk assumption: Cactus's Gemma 4 E2B build accepts
`messages[].images: [path]` on the Python SDK the same way it does on
the Swift/Apple SDK (cactus_docs/apple.md:84). Cactus RN docs only show
the vision example on lfm2-vl-450m.

Strategy:
  1) Try Gemma 4 E2B with images=[scene_small.jpg]. Pass if response is
     non-empty and references something recognizable from the image.
  2) If Gemma rejects or returns empty, try lfm2-vl-450m as fallback
     scene-tagger — this becomes the production path per SPEC Part 13
     item 3 failure contingency.

Run:  source ./activate && python tests/vision_test.py
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

CACTUS_ROOT = Path("/Users/jaehoshin/personal/yc-hackathon/cactus")
sys.path.insert(0, str(CACTUS_ROOT / "python"))

from src.downloads import ensure_model  # noqa: E402
from src.cactus import cactus_init, cactus_complete, cactus_destroy  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
IMAGE_PATH = REPO_ROOT / "tests" / "fixtures" / "scene_small.jpg"

PROMPT = (
    "List the objects and any visible text you can see in this image as a "
    "short JSON object with an \"objects\" array of strings. Keep it under "
    "20 items. Just the JSON, no preamble."
)

OPTIONS = json.dumps({
    "temperature": 0.2,
    "telemetry_enabled": False,
    "confidence_threshold": 0.0,
})


def run_vision(model_id: str, label: str) -> dict:
    print(f"\n{'=' * 72}")
    print(f" {label}  ({model_id})")
    print("=" * 72)

    if not IMAGE_PATH.exists():
        raise FileNotFoundError(f"Test image missing: {IMAGE_PATH}")
    print(f" image: {IMAGE_PATH}  ({IMAGE_PATH.stat().st_size // 1024} KB)")

    weights = ensure_model(model_id)
    t0 = time.time()
    model = cactus_init(str(weights), None, False)
    print(f" load: {time.time() - t0:.2f}s")

    messages = json.dumps([
        {
            "role": "user",
            "content": PROMPT,
            "images": [str(IMAGE_PATH)],
        },
    ])

    t0 = time.time()
    err = None
    response = ""
    success = False
    try:
        raw = cactus_complete(model, messages, OPTIONS, None, None)
        elapsed = time.time() - t0
        try:
            result = json.loads(raw)
            response = (result.get("response") or "").strip()
            success = bool(result.get("success"))
        except json.JSONDecodeError:
            response = raw.strip()
            success = bool(response)
    except Exception as exc:  # noqa: BLE001
        elapsed = time.time() - t0
        err = str(exc)
    finally:
        cactus_destroy(model)

    print(f" elapsed: {elapsed:.2f}s")
    if err:
        print(f" ERROR: {err}")
    print(f" response ({len(response)} chars):")
    print(" " + "-" * 70)
    for line in response.splitlines() or [""]:
        print(f"   {line}")
    print(" " + "-" * 70)

    return {
        "label": label,
        "model_id": model_id,
        "success": success and bool(response) and not err,
        "response": response,
        "error": err,
        "elapsed": elapsed,
    }


def main() -> None:
    # 1) Gemma 4 E2B — the primary, load-bearing attempt.
    primary = run_vision("google/gemma-4-E2B-it", "PRIMARY: Gemma 4 E2B")

    fallback = None
    if not primary["success"]:
        print("\n ⚠ Gemma 4 E2B vision failed or returned empty. Trying fallback.")
        fallback = run_vision("cactus-compute/lfm2-vl-450m", "FALLBACK: lfm2-vl-450m")

    print("\n" + "=" * 72)
    print(" SUMMARY")
    print("=" * 72)
    print(f"  Gemma 4 E2B vision: {'✅ works' if primary['success'] else '❌ failed'}")
    if fallback is not None:
        print(f"  lfm2-vl-450m vision: {'✅ works (use as scene-tagger)' if fallback['success'] else '❌ also failed'}")

    if primary["success"]:
        print("\n ✅ PASS — ship single-model vision on Gemma 4 E2B.")
    elif fallback and fallback["success"]:
        print("\n ⚠  FALLBACK ACTIVATED — scene-tag on lfm2-vl-450m, pipe JSON into Gemma 4 for language.")
    else:
        print("\n ❌ FAIL — investigate before H0. Neither primary nor fallback worked.")


if __name__ == "__main__":
    main()
