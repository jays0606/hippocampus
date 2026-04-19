#!/usr/bin/env python3
"""Smoke test: Gemma 4 E2B on Cactus, Hippocampus system prompt.

Run:  source ./activate && python smoke_test.py
"""
import json
import sys
import time
from pathlib import Path

CACTUS_ROOT = Path("/Users/jaehoshin/personal/yc-hackathon/cactus")
sys.path.insert(0, str(CACTUS_ROOT / "python"))

from src.downloads import ensure_model
from src.cactus import cactus_init, cactus_complete, cactus_destroy

MODEL_ID = "google/gemma-4-E2B-it"

SYSTEM = (
    "You are Hippo. You are a memory for someone whose own memory is slipping. "
    "You speak only in voice. You are warm, brief, and honest. "
    "Never invent a location, a time, a person, or an event. "
    "Speak in one sentence when possible. Grandmother, not a tech demo."
)

USER = "Hey Hippo — where are my glasses?"


def main():
    print(f"[1/3] Ensuring model weights: {MODEL_ID}")
    weights_dir = ensure_model(MODEL_ID)
    print(f"      weights_dir = {weights_dir}")

    print("[2/3] Loading model into cactus engine...")
    t0 = time.time()
    model = cactus_init(str(weights_dir), None, False)
    print(f"      loaded in {time.time() - t0:.2f}s")

    try:
        print("[3/3] Running Hippocampus scenario completion...")
        messages = json.dumps([
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": USER},
        ])
        t0 = time.time()
        raw = cactus_complete(model, messages, None, None, None)
        elapsed = time.time() - t0
        result = json.loads(raw)

        print("\n" + "=" * 60)
        print(f"Prompt: {USER}")
        print("-" * 60)
        print(result.get("response", "<empty>"))
        print("=" * 60)
        print(f"success={result.get('success')}  elapsed={elapsed:.2f}s")

        if not result.get("success"):
            print(f"ERROR: {result}")
            sys.exit(1)
    finally:
        cactus_destroy(model)


if __name__ == "__main__":
    main()
