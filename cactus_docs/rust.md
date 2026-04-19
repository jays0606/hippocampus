# Rust SDK

Source: https://docs.cactuscompute.com/latest/rust/

Raw FFI bindings to the Cactus C API. Auto-generated via `bindgen`. Model weights at https://huggingface.co/Cactus-Compute.

## Installation

`Cargo.toml`:
```toml
[dependencies]
cactus-sys = { path = "rust/cactus-sys" }
```

### Build Requirements

- CMake
- C++20 compiler
- Platform tools:
  - macOS: Xcode CLI
  - Linux: `build-essential`, `libcurl4-openssl-dev`, `libclang-dev`

## Usage

The Rust bindings mirror the C API documented in `docs/cactus_engine.md`.

### Multimodal Support

- **Vision** (LFM2-VL, LFM2.5-VL, Gemma4, Qwen3.5): add `"images": ["path/to/image.png"]` to messages.
- **Audio** (Gemma4): add `"audio": ["path/to/audio.wav"]` to messages.

### Reference Materials

- Test files: `rust/cactus-sys/tests/`
- C API documentation: `docs/cactus_engine.md`
- Other SDK examples: `python/README.md`, `apple/README.md`

## Testing

```bash
export CACTUS_MODEL_PATH=/path/to/model
export CACTUS_STT_MODEL_PATH=/path/to/whisper-model
export CACTUS_STT_AUDIO_PATH=/path/to/audio.wav
cargo test --manifest-path rust/Cargo.toml -- --nocapture
```
