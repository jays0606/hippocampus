# Runtime & Weights Compatibility

Source: https://docs.cactuscompute.com/latest/docs/compatibility/

Some Cactus releases change the internal weight format. When this happens, cached weights from an older version will not load with a newer runtime and must be re-downloaded.

## Versioning

Weights are published to Hugging Face and only re-tagged when they actually change.

**Rule:** use the latest HF weight tag that is **≤ your runtime version**.

Example:
- Runtime v1.7 → weights tagged v1.7
- Runtime v1.8–1.14 → no new tag (still use v1.7)
- Runtime v1.15 → new tag v1.15 (changed)

## Checking Compatibility

1. Open your model on https://huggingface.co/Cactus-Compute
2. Files and versions → branch dropdown (Main)
3. Find the latest tag ≤ your runtime version; re-download if outdated

Breaking weight changes are documented in the official GitHub release notes.
