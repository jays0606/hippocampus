# Python SDK

Source: https://docs.cactuscompute.com/latest/python/

The Cactus Python SDK provides Python bindings for the Cactus Engine via FFI, automatically installed during setup. Pre-converted weights are available at https://huggingface.co/Cactus-Compute.

## Getting Started

```bash
git clone https://github.com/cactus-compute/cactus && cd cactus && source ./setup
cactus build --python
```

Download models:
```bash
cactus download LiquidAI/LFM2-VL-450M
cactus download openai/whisper-small
cactus auth  # Optional: set Cactus Cloud API key
```

## Quick Example

```python
from src.downloads import ensure_model
from src.cactus import cactus_init, cactus_complete, cactus_destroy
import json

weights = ensure_model("LiquidAI/LFM2-VL-450M")
model = cactus_init(str(weights), None, False)
messages = json.dumps([{"role": "user", "content": "What is 2+2?"}])
result = json.loads(cactus_complete(model, messages, None, None, None))
print(result["response"])
cactus_destroy(model)
```

## API Reference

All functions are module-level, mirroring the C FFI directly. Handles are plain `int` values (C pointers).

### Model Downloads

```python
from src.downloads import ensure_model, get_weights_dir, download_from_hf

weights = ensure_model("openai/whisper-tiny")
weights_dir = get_weights_dir("openai/whisper-tiny")
download_from_hf("openai/whisper-tiny", weights_dir, precision="INT4")
```

### Init / Lifecycle

```python
model = cactus_init(model_path: str, corpus_dir: str | None, cache_index: bool) -> int
cactus_destroy(model: int)
cactus_reset(model: int)   # clear KV cache
cactus_stop(model: int)    # abort ongoing generation
cactus_get_last_error() -> str | None
```

### Completion

```python
result_json = cactus_complete(
    model: int,
    messages_json: str,              # JSON array of {role, content}
    options_json: str | None,        # optional inference options
    tools_json: str | None,          # optional tool definitions
    callback: Callable[[str, int], None] | None,  # streaming token callback
    pcm_data: list[int] | None = None              # optional raw audio bytes
) -> str
```

With options and streaming:
```python
options = json.dumps({"max_tokens": 256, "temperature": 0.7})

def on_token(token, token_id):
    print(token, end="", flush=True)

result = json.loads(cactus_complete(model, messages_json, options, None, on_token))
if result["cloud_handoff"]:
    pass
```

Response:
```json
{
    "success": true,
    "error": null,
    "cloud_handoff": false,
    "response": "4",
    "function_calls": [],
    "segments": [],
    "confidence": 0.92,
    "time_to_first_token_ms": 45.2,
    "total_time_ms": 163.7,
    "prefill_tps": 619.5,
    "decode_tps": 168.4,
    "ram_usage_mb": 512.3,
    "prefill_tokens": 28,
    "decode_tokens": 12,
    "total_tokens": 40
}
```

### Prefill

Pre-processes input text and populates KV cache without generating tokens, reducing latency for subsequent calls.

```python
cactus_prefill(
    model: int,
    messages_json: str,
    options_json: str | None,
    tools_json: str | None,
    pcm_data: list[int] | None = None
) -> None
```

Tool definition example:
```python
tools = json.dumps([{
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get weather for a location",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {"type": "string", "description": "City, State, Country"}
            },
            "required": ["location"]
        }
    }
}])

messages = json.dumps([
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What is the weather in Paris?"},
    {"role": "assistant", "content": "<|tool_call_start|>get_weather(location=\"Paris\")<|tool_call_end|>"},
    {"role": "tool", "content": "{\"name\": \"get_weather\", \"content\": \"Sunny, 72°F\"}"},
    {"role": "assistant", "content": "It's sunny and 72°F in Paris!"}
])
cactus_prefill(model, messages, None, tools)
```

Response:
```json
{
    "success": true,
    "error": null,
    "prefill_tokens": 25,
    "prefill_tps": 166.1,
    "total_time_ms": 150.5,
    "ram_usage_mb": 245.67
}
```

### Transcription

Returns JSON with `response` (transcribed text), `segments` array of `{"start": <sec>, "end": <sec>, "text": <str>}`, and metadata.

```python
result_json = cactus_transcribe(
    model: int,
    audio_path: str | None,
    prompt: str | None,
    options_json: str | None,
    callback: Callable[[str, int], None] | None,
    pcm_data: bytes | None
) -> str
```

Custom vocabulary biases the decoder toward domain-specific words (Whisper and Moonshine):
```python
options = json.dumps({
    "custom_vocabulary": ["Omeprazole", "HIPAA", "Cactus"],
    "vocabulary_boost": 3.0
})
result = json.loads(cactus_transcribe(model, "medical_notes.wav", None, options, None, None))
```

Streaming transcription:
```python
stream       = cactus_stream_transcribe_start(model: int, options_json: str | None) -> int
partial_json = cactus_stream_transcribe_process(stream: int, pcm_data: bytes) -> str
final_json   = cactus_stream_transcribe_stop(stream: int) -> str
```

In streaming responses: `confirmed` is stable finalized text; `confirmed_local` is the same before cloud substitution; `pending` is unconfirmed window text; `segments` contains timestamped segments.

Parse segments:
```python
result = json.loads(cactus_transcribe(model, "/path/to/audio.wav", None, None, None, None))
print(result["response"])
for seg in result["segments"]:
    print(f"[{seg['start']:.3f}s - {seg['end']:.3f}s] {seg['text']}")
```

### Embeddings

```python
embedding = cactus_embed(model: int, text: str, normalize: bool) -> list[float]
embedding = cactus_image_embed(model: int, image_path: str) -> list[float]
embedding = cactus_audio_embed(model: int, audio_path: str) -> list[float]
```

### Tokenization

```python
tokens     = cactus_tokenize(model: int, text: str) -> list[int]
result_json = cactus_score_window(model: int, tokens: list[int], start: int, end: int, context: int) -> str
```

### Detect Language

```python
result_json = cactus_detect_language(
    model: int,
    audio_path: str | None,
    options_json: str | None,
    pcm_data: bytes | None
) -> str
```

Returns JSON with `success`, `error`, `language` (BCP-47 code), `language_token`, `token_id`, `confidence`, `entropy`, `total_time_ms`, `ram_usage_mb`.

### VAD

```python
result_json = cactus_vad(
    model: int,
    audio_path: str | None,
    options_json: str | None,
    pcm_data: bytes | None
) -> str
```

Returns: `{"success":true,"error":null,"segments":[{"start":<sample_index>,"end":<sample_index>},...],"total_time_ms":...,"ram_usage_mb":...}`. VAD segment indices are integer sample indices.

### Diarize

```python
result_json = cactus_diarize(
    model: int,
    audio_path: str | None,
    options_json: str | None,
    pcm_data: bytes | None
) -> str
```

Options (all optional):
- `step_ms` (int, default 1000) — sliding window stride in milliseconds
- `threshold` (float) — zero out per-speaker scores below this value
- `num_speakers` (int) — keep only the N most active speakers
- `min_speakers` (int) — minimum speaker count to retain
- `max_speakers` (int) — maximum speaker count to retain
- `raw_powerset` (bool, default false) — return raw 7-class powerset scores instead of 3-speaker probabilities

Returns: `{"success":true,"error":null,"num_speakers":3,"scores":[...],"total_time_ms":...,"ram_usage_mb":...}`. The `scores` field is a flat array of T×3 float32 values (index `f*3+s`), each in [0,1]. With `raw_powerset=true`, `num_speakers` is 7 and scores contains T×7 raw powerset class scores.

### Embed Speaker

```python
result_json = cactus_embed_speaker(
    model: int,
    audio_path: str | None,
    options_json: str | None,
    pcm_data: bytes | None,
    mask_weights: list[float] | None = None
) -> str
```

Returns: `{"success":true,"error":null,"embedding":[<float>, ...],"total_time_ms":...,"ram_usage_mb":...}`. The 256-dim speaker vector comes from WeSpeaker ResNet34-LM. With `mask_weights` from diarization, embedding uses weighted stats pooling.

### RAG

```python
result_json = cactus_rag_query(model: int, query: str, top_k: int) -> str
```

Returns chunks with `score`, `source`, `content`:
```json
{
    "chunks": [
        {"score": 0.0142, "source": "doc.txt", "content": "relevant passage..."}
    ]
}
```

### Vector Index

```python
index = cactus_index_init(index_dir: str, embedding_dim: int) -> int
cactus_index_add(index: int, ids: list[int], documents: list[str],
                 embeddings: list[list[float]], metadatas: list[str] | None)
cactus_index_delete(index: int, ids: list[int])
result_json = cactus_index_get(index: int, ids: list[int]) -> str
result_json = cactus_index_query(index: int, embedding: list[float], options_json: str | None) -> str
cactus_index_compact(index: int)
cactus_index_destroy(index: int)
```

`cactus_index_query` returns `{"results":[{"id":<int>,"score":<float>}, ...]}`.
`cactus_index_get` returns `{"results":[{"document":"...","metadata":<str|null>,"embedding":[...]}, ...]}`.

### Logging

```python
cactus_log_set_level(level: int)  # 0=DEBUG 1=INFO 2=WARN (default) 3=ERROR 4=NONE
cactus_log_set_callback(callback: Callable[[int, str, str], None] | None)
```

### Telemetry

```python
cactus_set_telemetry_environment(cache_location: str)
cactus_set_app_id(app_id: str)
cactus_telemetry_flush()
cactus_telemetry_shutdown()
```

## Error Handling

Functions that return values raise `RuntimeError` on failure. `cactus_prefill`, `cactus_index_add`, `cactus_index_delete`, and `cactus_index_compact` also raise `RuntimeError` despite not returning values. Void functions that never raise: `cactus_destroy`, `cactus_reset`, `cactus_stop`, `cactus_index_destroy`, logging and telemetry functions.

## Vision (VLM)

Pass images in message content for vision-language models (LFM2-VL, LFM2.5-VL, Gemma4, Qwen3.5):

```python
messages = json.dumps([{
    "role": "user",
    "content": "Describe this image",
    "images": ["path/to/image.png"]
}])
result = json.loads(cactus_complete(model, messages, None, None, None))
print(result["response"])
```

## Audio (Multimodal)

Pass audio files in messages for models with native audio understanding (Gemma4):

```python
messages = json.dumps([{
    "role": "user",
    "content": "Transcribe the audio.",
    "audio": ["path/to/audio.wav"]
}])
result = json.loads(cactus_complete(model, messages, None, None, None))
print(result["response"])

# Combined vision + audio
messages = json.dumps([{
    "role": "user",
    "content": "Describe the image and transcribe the audio.",
    "images": ["path/to/image.png"],
    "audio": ["path/to/audio.wav"]
}])
result = json.loads(cactus_complete(model, messages, None, None, None))
```

## Compute Graph

```python
from src.graph import Graph
import numpy as np

g = Graph()
a = g.input((2, 2))
b = g.input((2, 2))
y = ((a - b) * (a + b)).abs().pow(2.0).view((4,))

g.set_input(a, np.array([[2, 4], [6, 8]], dtype=np.float16))
g.set_input(b, np.array([[1, 2], [3, 4]], dtype=np.float16))
g.execute()

print(y.numpy())  # [9. 36. 81. 144.]
```

Supported ops: `+`, `-`, `*`, `/`, `abs`, `pow`, `view`, `flatten`, `concat`, `cat`, `relu`, `sigmoid`, `tanh`, `gelu`, `softmax`.

## Testing

```bash
python python/test.py        # compact output
python python/test.py -v     # verbose
```

Tests in `python/tests/`:
- `test_graph.py` — Graph elementwise, composed, tensor, activation, softmax ops
- `test_model.py` — VLM completion/embeddings, Whisper transcription/embeddings (auto-downloads weights)
