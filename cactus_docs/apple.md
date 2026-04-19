# Swift / Apple SDK

Source: https://docs.cactuscompute.com/latest/apple/

Run AI models on-device with a simple Swift API on iOS, macOS, and Android.

## Building

```bash
git clone https://github.com/cactus-compute/cactus && cd cactus && source ./setup
cactus build --apple
```

Outputs:
- `cactus-ios.xcframework/` (iOS device + simulator)
- `cactus-macos.xcframework/` (macOS)
- Static libraries for iOS device and simulator

### Vendored libcurl Configuration

To bundle libcurl from the repository instead of using system curl, place artifacts in:
- `libs/curl/include/curl/*.h`
- `libs/curl/ios/device/libcurl.a`
- `libs/curl/ios/simulator/libcurl.a`
- `libs/curl/macos/libcurl.a`

Override default path:
```bash
CACTUS_CURL_ROOT=/absolute/path/to/curl cactus build --apple
```

## Integration Methods

### iOS/macOS: XCFramework (Recommended)

1. Drag `cactus-ios.xcframework` or `cactus-macos.xcframework` into Xcode project
2. Set "Embed & Sign" in "Frameworks, Libraries, and Embedded Content"
3. Copy `Cactus.swift` into project

### iOS/macOS: Static Library

1. Add `libcactus-device.a` or `libcactus-simulator.a` to "Link Binary With Libraries"
2. Create folder with `cactus_ffi.h` and `module.modulemap`
3. Build Settings:
   - "Header Search Paths" → folder path
   - "Import Paths" (Swift) → folder path
4. Copy `Cactus.swift` into project

### Android (Swift SDK)

Requires the Swift SDK for Android.

1. Copy to Swift project:
   - `libcactus.so` → library path
   - `cactus_ffi.h` → include path
   - `module.android.modulemap` → rename to `module.modulemap`
   - `Cactus.swift` → sources

2. Build:
```bash
swift build --swift-sdk aarch64-unknown-linux-android28 \
    -Xswiftc -I/path/to/include \
    -Xlinker -L/path/to/lib \
    -Xlinker -lcactus
```

3. Bundle `libcactus.so` in APK at `jniLibs/arm64-v8a/`

## Usage Examples

### Basic Completion

```swift
import Foundation

let model = try cactusInit("/path/to/model", nil, false)
defer { cactusDestroy(model) }

let messages = #"[{"role":"user","content":"What is the capital of France?"}]"#
let resultJson = try cactusComplete(model, messages, nil, nil, nil)
print(resultJson)
```

For vision models, add `"images": ["path/to/image.png"]` to messages. For audio models, add `"audio": ["path/to/audio.wav"]`.

### Completion with Options and Streaming

```swift
let options = #"{"max_tokens":256,"temperature":0.7}"#

let resultJson = try cactusComplete(model, messages, options, nil as String?) { token, _ in
    print(token, terminator: "")
}
print(resultJson)
```

### Prefill

```swift
func cactusPrefill(
    _ model: CactusModelT,
    _ messagesJson: String,
    _ optionsJson: String?,
    _ toolsJson: String?
) throws -> String
```

Example:
```swift
let tools = #"[
    {
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
    }
]"#

let messages = #"[
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What is the weather in Paris?"},
    {"role": "assistant", "content": "<|tool_call_start|>get_weather(location=\"Paris\")<|tool_call_end|>"},
    {"role": "tool", "content": "{\"name\": \"get_weather\", \"content\": \"Sunny, 72°F\"}"},
    {"role": "assistant", "content": "It's sunny and 72°F in Paris!"}
]"#

let resultJson = try cactusPrefill(model, messages, nil, tools)
```

### Audio Transcription

From file:
```swift
let resultJson = try cactusTranscribe(model, "/path/to/audio.wav", nil, nil, nil as ((String, UInt32) -> Void)?, nil as Data?)
print(resultJson)
```

From PCM data (16 kHz mono):
```swift
let pcmData: Data = ...
let resultJson2 = try cactusTranscribe(model, nil, nil, nil, nil as ((String, UInt32) -> Void)?, pcmData)
print(resultJson2)
```

The `segments` field contains timestamps in seconds. For Whisper, timestamps are phrase-level; for Parakeet TDT, word-level; for Parakeet CTC and Moonshine, one segment per VAD speech window (up to 30 seconds).

Parse segments:
```swift
if let data = resultJson.data(using: .utf8),
   let obj = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
   let segments = obj["segments"] as? [[String: Any]] {
    for seg in segments {
        let start = seg["start"] as? Double ?? 0
        let end = seg["end"] as? Double ?? 0
        let text = seg["text"] as? String ?? ""
        print(String(format: "[%.3fs - %.3fs] %@", start, end, text))
    }
}
```

### Custom Vocabulary

```swift
let options = #"{"custom_vocabulary": ["Omeprazole", "HIPAA", "Cactus"], "vocabulary_boost": 3.0}"#
let result = try cactusTranscribe(model, "/path/to/audio.wav", nil, options, nil as ((String, UInt32) -> Void)?, nil as Data?)
```

### Streaming Transcription

```swift
let stream = try cactusStreamTranscribeStart(model, nil as String?)

let partialJson = try cactusStreamTranscribeProcess(stream, audioChunk)
print(partialJson)

let finalJson = try cactusStreamTranscribeStop(stream)
print(finalJson)
```

### Embeddings

```swift
let embedding      = try cactusEmbed(model, "Hello, world!", true)
let imageEmbedding = try cactusImageEmbed(model, "/path/to/image.jpg")
let audioEmbedding = try cactusAudioEmbed(model, "/path/to/audio.wav")
```

### Tokenization

```swift
let tokens = try cactusTokenize(model, "Hello, world!")
let scoresJson = try cactusScoreWindow(model, tokens, 0, tokens.count, min(tokens.count, 512))
print(scoresJson)
```

### Detect Language

```swift
let langJson = try cactusDetectLanguage(model, "/path/to/audio.wav", nil, nil)
print(langJson)
```

### VAD

```swift
let vadJson = try cactusVad(model, "/path/to/audio.wav", nil as String?, nil as Data?)
print(vadJson)
```

### Diarize

```swift
let diarizeJson = try cactusDiarize(model, "/path/to/audio.wav", nil, nil as Data?)
print(diarizeJson)
```

Options: `step_ms`, `threshold`, `num_speakers`, `min_speakers`, `max_speakers`, `raw_powerset`.

### Embed Speaker

```swift
let embedJson = try cactusEmbedSpeaker(model, "/path/to/audio.wav", nil, nil as Data?)
print(embedJson)

// With diarization mask for speaker-specific embedding
let embedJson2 = try cactusEmbedSpeaker(model, "/path/to/audio.wav", nil, nil as Data?, maskWeights)
```

Returns a 256-dim speaker embedding.

### RAG

```swift
let ragJson = try cactusRagQuery(model, "What is machine learning?", 5)
print(ragJson)
```

### Vector Index

```swift
let index = try cactusIndexInit("/path/to/index", 384)
defer { cactusIndexDestroy(index) }

try cactusIndexAdd(index, [Int32(1), Int32(2)], ["doc1", "doc2"],
                   [[Float(0.1), Float(0.2), ...], [Float(0.3), Float(0.4), ...]], nil)

let results = try cactusIndexQuery(index, [Float(0.1), Float(0.2), ...], nil)

try cactusIndexDelete(index, [Int32(2)])
try cactusIndexCompact(index)
```

## API Reference

### Type Aliases

```swift
public typealias CactusModelT            = UnsafeMutableRawPointer
public typealias CactusIndexT            = UnsafeMutableRawPointer
public typealias CactusStreamTranscribeT = UnsafeMutableRawPointer
```

All `throws` functions throw `NSError` (domain `"cactus"`) on failure.

### Init / Lifecycle

```swift
func cactusInit(_ modelPath: String, _ corpusDir: String?, _ cacheIndex: Bool) throws -> CactusModelT
func cactusDestroy(_ model: CactusModelT)
func cactusReset(_ model: CactusModelT)
func cactusStop(_ model: CactusModelT)
func cactusGetLastError() -> String
```

### Prefill

```swift
func cactusPrefill(
    _ model: CactusModelT,
    _ messagesJson: String,
    _ optionsJson: String?,
    _ toolsJson: String?,
    _ pcmData: Data? = nil
) throws -> String
```

### Completion

```swift
func cactusComplete(
    _ model: CactusModelT,
    _ messagesJson: String,
    _ optionsJson: String?,
    _ toolsJson: String?,
    _ callback: ((String, UInt32) -> Void)?,
    _ pcmData: Data? = nil
) throws -> String
```

### Transcription

```swift
func cactusTranscribe(
    _ model: CactusModelT,
    _ audioPath: String?,
    _ prompt: String?,
    _ optionsJson: String?,
    _ callback: ((String, UInt32) -> Void)?,
    _ pcmData: Data?
) throws -> String

func cactusStreamTranscribeStart(_ model: CactusModelT, _ optionsJson: String?) throws -> CactusStreamTranscribeT
func cactusStreamTranscribeProcess(_ stream: CactusStreamTranscribeT, _ pcmData: Data) throws -> String
func cactusStreamTranscribeStop(_ stream: CactusStreamTranscribeT) throws -> String
```

### Embeddings

```swift
func cactusEmbed(_ model: CactusModelT, _ text: String, _ normalize: Bool) throws -> [Float]
func cactusImageEmbed(_ model: CactusModelT, _ imagePath: String) throws -> [Float]
func cactusAudioEmbed(_ model: CactusModelT, _ audioPath: String) throws -> [Float]
```

### Tokenization / Scoring

```swift
func cactusTokenize(_ model: CactusModelT, _ text: String) throws -> [UInt32]
func cactusScoreWindow(_ model: CactusModelT, _ tokens: [UInt32], _ start: Int, _ end: Int, _ context: Int) throws -> String
```

### Detect Language

```swift
func cactusDetectLanguage(_ model: CactusModelT, _ audioPath: String?, _ optionsJson: String?, _ pcmData: Data?) throws -> String
```

### VAD / Diarize / Embed Speaker

```swift
func cactusVad(_ model: CactusModelT, _ audioPath: String?, _ optionsJson: String?, _ pcmData: Data?) throws -> String
func cactusDiarize(_ model: CactusModelT, _ audioPath: String?, _ optionsJson: String?, _ pcmData: Data?) throws -> String
func cactusEmbedSpeaker(_ model: CactusModelT, _ audioPath: String?, _ optionsJson: String?, _ pcmData: Data?, _ maskWeights: [Float]? = nil) throws -> String
```

### RAG

```swift
func cactusRagQuery(_ model: CactusModelT, _ query: String, _ topK: Int) throws -> String
```

### Vector Index

```swift
func cactusIndexInit(_ indexDir: String, _ embeddingDim: Int) throws -> CactusIndexT
func cactusIndexDestroy(_ index: CactusIndexT)
func cactusIndexAdd(_ index: CactusIndexT, _ ids: [Int32], _ documents: [String], _ embeddings: [[Float]], _ metadatas: [String]?) throws
func cactusIndexDelete(_ index: CactusIndexT, _ ids: [Int32]) throws
func cactusIndexGet(_ index: CactusIndexT, _ ids: [Int32]) throws -> String
func cactusIndexQuery(_ index: CactusIndexT, _ embedding: [Float], _ optionsJson: String?) throws -> String
func cactusIndexCompact(_ index: CactusIndexT) throws
```

### Logging / Telemetry

```swift
func cactusLogSetLevel(_ level: Int32)  // 0=DEBUG, 1=INFO, 2=WARN (default), 3=ERROR, 4=NONE
func cactusLogSetCallback(_ callback: ((Int32, String, String) -> Void)?)

func cactusSetTelemetryEnvironment(_ path: String)
func cactusSetAppId(_ appId: String)
func cactusTelemetryFlush()
func cactusTelemetryShutdown()
```

## Requirements

**Apple Platforms:**
- iOS 13.0+ / macOS 13.0+
- Xcode 14.0+
- Swift 5.7+

**Android:**
- Swift 6.0+ with Swift SDK for Android
- Android NDK 27d+
- Android API 28+ / arm64-v8a
