# Cactus

Source: https://docs.cactuscompute.com/latest/

Cactus is a low-latency AI engine for mobile devices and wearables.

## Primary Features

- **Fast** — fastest inference on ARM CPU
- **Low RAM** — zero-copy memory mapping ensures 10x lower RAM use than other engines
- **Multimodal** — one SDK for speech, vision, and language models
- **Cloud fallback** — automatically route requests to cloud models if needed
- **Energy-efficient** — NPU-accelerated prefill

## Architecture

Three layers:

1. **Cactus Engine** — OpenAI-compatible APIs for chat, vision, STT, RAG, and tool calling
2. **Cactus Graph** — Computation graph optimized for mobile (PyTorch equivalent)
3. **Cactus Kernels** — ARM SIMD implementations for various processors

## Quick Demo (Mac)

```bash
brew install cactus-compute/cactus/cactus
cactus transcribe
cactus run
```

## CLI Commands

- `cactus auth` — API key management
- `cactus run` — Model playground
- `cactus transcribe` — Audio transcription
- `cactus download` / `cactus convert` — Model management
- `cactus build` — Platform-specific compilation
- `cactus test` — Testing and benchmarking

## Setup

**Linux prerequisites:**
```bash
sudo apt-get install python3 python3-venv python3-pip cmake build-essential libcurl4-openssl-dev
```

**Clone & setup:**
```bash
git clone https://github.com/cactus-compute/cactus && cd cactus && source ./setup
```

## API & SDK References

- Engine API (C)
- Graph API (C++)
- Python SDK
- Swift SDK
- Kotlin SDK
- Flutter SDK
- Rust SDK

## Supported Models

**Transcription:** Moonshine-Base, Whisper variants, Parakeet CTC/TDT, Silero VAD, WeSpeaker speaker recognition.

**LLMs:** Gemma variants, Qwen, LiquidAI LFM series, embeddings.

Features include vision, tools, and NPU acceleration.

## External Resources

- GitHub: https://github.com/cactus-compute/cactus
- Website: https://cactuscompute.com/
- HuggingFace Models: https://huggingface.co/Cactus-Compute
