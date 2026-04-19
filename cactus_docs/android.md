# Kotlin / Android SDK

Source: https://docs.cactuscompute.com/latest/android/

Run AI models directly on Android devices with a Kotlin API.

## Building

```bash
git clone https://github.com/cactus-compute/cactus && cd cactus && source ./setup
cactus build --android
```

Build artifacts: `android/libcactus.so` and `android/libcactus.a`.

### Vendored libcurl (device builds)

Place artifacts at:
- `libs/curl/android/arm64-v8a/libcurl.a`
- `libs/curl/include/curl/*.h`

Override path:
```bash
CACTUS_CURL_ROOT=/absolute/path/to/curl cactus build --android
```

## Integration

### Android-only Setup

1. Copy `libcactus.so` to `app/src/main/jniLibs/arm64-v8a/`
2. Copy `Cactus.kt` to `app/src/main/java/com/cactus/`

### Kotlin Multiplatform Setup

| File | Destination |
|------|-------------|
| `Cactus.common.kt` | `shared/src/commonMain/kotlin/com/cactus/` |
| `Cactus.android.kt` | `shared/src/androidMain/kotlin/com/cactus/` |
| `Cactus.ios.kt` | `shared/src/iosMain/kotlin/com/cactus/` |
| `cactus.def` | `shared/src/nativeInterop/cinterop/` |

Binaries:
| Platform | Location |
|----------|----------|
| Android | `libcactus.so` → `app/src/main/jniLibs/arm64-v8a/` |
| iOS | `libcactus-device.a` → link via cinterop |

`build.gradle.kts`:
```kotlin
kotlin {
    androidTarget()

    listOf(iosArm64(), iosSimulatorArm64()).forEach {
        it.compilations.getByName("main") {
            cinterops {
                create("cactus") {
                    defFile("src/nativeInterop/cinterop/cactus.def")
                    includeDirs("/path/to/cactus/ffi")
                }
            }
        }
        it.binaries.framework {
            linkerOpts("-L/path/to/apple", "-lcactus-device")
        }
    }

    sourceSets {
        commonMain.dependencies {
            implementation("org.jetbrains.kotlinx:kotlinx-serialization-json:1.6.0")
        }
    }
}
```

## Usage

All functions are top-level. Handles are `Long` values (C pointers).

### Basic Completion

```kotlin
import com.cactus.*

val model = cactusInit("/path/to/model", null, false)
val messages = """[{"role":"user","content":"What is the capital of France?"}]"""
val resultJson = cactusComplete(model, messages, null, null, null)
println(resultJson)
cactusDestroy(model)
```

For vision models, add `"images": ["path/to/image.png"]`. For audio models (Gemma4), add `"audio": ["path/to/audio.wav"]`.

### Completion with Options and Streaming

```kotlin
val options = """{"max_tokens":256,"temperature":0.7}"""

val resultJson = cactusComplete(model, messages, options, null) { token, _ ->
    print(token)
}
println(resultJson)
```

### Prefill

```kotlin
fun cactusPrefill(
    model: Long,
    messagesJson: String,
    optionsJson: String?,
    toolsJson: String?
): String
```

Tool example:
```kotlin
val tools = """[
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
]"""

val messages = """[
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What is the weather in Paris?"},
    {"role": "assistant", "content": "<|tool_call_start|>get_weather(location=\"Paris\")<|tool_call_end|>"},
    {"role": "tool", "content": "{\"name\": \"get_weather\", \"content\": \"Sunny, 72°F\"}"},
    {"role": "assistant", "content": "It's sunny and 72°F in Paris!"}
]"""

val resultJson = cactusPrefill(model, messages, null, tools)
```

### Audio Transcription

```kotlin
// From file
val resultJson = cactusTranscribe(model, "/path/to/audio.wav", null, null, null, null)
println(resultJson)

// From PCM data (16 kHz mono)
val pcmData: ByteArray = ...
val resultJson2 = cactusTranscribe(model, null, null, null, null, pcmData)
println(resultJson2)
```

Segments: phrase-level for Whisper, word-level for Parakeet TDT, single-window for Parakeet CTC and Moonshine.

```kotlin
import org.json.JSONObject

val result = JSONObject(resultJson)
val segments = result.getJSONArray("segments")
for (i in 0 until segments.length()) {
    val seg = segments.getJSONObject(i)
    println("[${seg.getDouble("start")}s - ${seg.getDouble("end")}s] ${seg.getString("text")}")
}
```

Custom vocabulary (Whisper / Moonshine):
```kotlin
val options = """{"custom_vocabulary": ["Omeprazole", "HIPAA", "Cactus"], "vocabulary_boost": 3.0}"""
val result = cactusTranscribe(model, "/path/to/audio.wav", "", options, null, null)
```

### Streaming Transcription

```kotlin
val stream = cactusStreamTranscribeStart(model, null)
val partial = cactusStreamTranscribeProcess(stream, audioChunk)
val final_ = cactusStreamTranscribeStop(stream)
```

### Embeddings

```kotlin
val embedding      = cactusEmbed(model, "Hello, world!", true)   // FloatArray
val imageEmbedding = cactusImageEmbed(model, "/path/to/image.jpg")
val audioEmbedding = cactusAudioEmbed(model, "/path/to/audio.wav")
```

### Tokenization

```kotlin
val tokens = cactusTokenize(model, "Hello, world!")  // IntArray
val scores = cactusScoreWindow(model, tokens, 0, tokens.size, 512)
```

### VAD / Diarize / Embed Speaker

```kotlin
val vad = cactusVad(model, "/path/to/audio.wav", null, null)
val diar = cactusDiarize(model, "/path/to/audio.wav", null, null)
val emb = cactusEmbedSpeaker(model, "/path/to/audio.wav", null, null)
val embWeighted = cactusEmbedSpeaker(model, "/path/to/audio.wav", null, null, maskWeights)
```

Diarize options: `step_ms` (default 1000), `threshold`, `num_speakers`, `min_speakers`, `max_speakers`, `raw_powerset`.

### RAG

```kotlin
val result = cactusRagQuery(model, "What is machine learning?", 5)
```

### Vector Index

```kotlin
val index = cactusIndexInit("/path/to/index", 3)

cactusIndexAdd(
    index,
    intArrayOf(1, 2),
    arrayOf("Document 1", "Document 2"),
    arrayOf(floatArrayOf(0.1f, 0.2f, 0.3f), floatArrayOf(0.4f, 0.5f, 0.6f)),
    null
)

val resultsJson = cactusIndexQuery(index, floatArrayOf(0.1f, 0.2f, 0.3f), null)
cactusIndexDelete(index, intArrayOf(2))
cactusIndexCompact(index)
cactusIndexDestroy(index)
```

## API Reference

### Init / Lifecycle

```kotlin
fun cactusInit(modelPath: String, corpusDir: String?, cacheIndex: Boolean): Long  // throws RuntimeException
fun cactusDestroy(model: Long)
fun cactusReset(model: Long)
fun cactusStop(model: Long)
fun cactusGetLastError(): String
```

### Prefill / Completion

```kotlin
fun cactusPrefill(model: Long, messagesJson: String, optionsJson: String?, toolsJson: String?, pcmData: ByteArray? = null): String
fun cactusComplete(model: Long, messagesJson: String, optionsJson: String?, toolsJson: String?, callback: CactusTokenCallback?, pcmData: ByteArray? = null): String
```

### Transcription

```kotlin
fun cactusTranscribe(model: Long, audioPath: String?, prompt: String?, optionsJson: String?, callback: CactusTokenCallback?, pcmData: ByteArray?): String

fun cactusStreamTranscribeStart(model: Long, optionsJson: String?): Long  // throws RuntimeException
fun cactusStreamTranscribeProcess(stream: Long, pcmData: ByteArray): String
fun cactusStreamTranscribeStop(stream: Long): String
```

### Embeddings

```kotlin
fun cactusEmbed(model: Long, text: String, normalize: Boolean): FloatArray
fun cactusImageEmbed(model: Long, imagePath: String): FloatArray
fun cactusAudioEmbed(model: Long, audioPath: String): FloatArray
```

### Tokenization / Scoring

```kotlin
fun cactusTokenize(model: Long, text: String): IntArray
fun cactusScoreWindow(model: Long, tokens: IntArray, start: Int, end: Int, context: Int): String
```

### VAD / Diarize / Detect Language / Embed Speaker

```kotlin
fun cactusDetectLanguage(model: Long, audioPath: String?, optionsJson: String?, pcmData: ByteArray?): String
fun cactusVad(model: Long, audioPath: String?, optionsJson: String?, pcmData: ByteArray?): String
fun cactusDiarize(model: Long, audioPath: String?, optionsJson: String?, pcmData: ByteArray?): String
fun cactusEmbedSpeaker(model: Long, audioPath: String?, optionsJson: String?, pcmData: ByteArray?, maskWeights: FloatArray? = null): String
```

### RAG

```kotlin
fun cactusRagQuery(model: Long, query: String, topK: Int): String
```

### Vector Index

```kotlin
fun cactusIndexInit(indexDir: String, embeddingDim: Int): Long  // throws RuntimeException
fun cactusIndexDestroy(index: Long)
fun cactusIndexAdd(index: Long, ids: IntArray, documents: Array<String>, embeddings: Array<FloatArray>, metadatas: Array<String>?): Int
fun cactusIndexDelete(index: Long, ids: IntArray): Int
fun cactusIndexGet(index: Long, ids: IntArray): String
fun cactusIndexQuery(index: Long, embedding: FloatArray, optionsJson: String?): String
fun cactusIndexCompact(index: Long): Int
```

### Logging / Telemetry

```kotlin
fun cactusLogSetLevel(level: Int)  // 0=DEBUG 1=INFO 2=WARN 3=ERROR 4=NONE
fun cactusLogSetCallback(callback: CactusLogCallback?)

fun cactusSetTelemetryEnvironment(cacheDir: String)
fun cactusSetAppId(appId: String)
fun cactusTelemetryFlush()
fun cactusTelemetryShutdown()
```

### Types

```kotlin
fun interface CactusTokenCallback {
    fun onToken(token: String, tokenId: Int)
}

fun interface CactusLogCallback {
    fun onLog(level: Int, component: String, message: String)
}
```

## Requirements

- Android API 21+ / arm64-v8a
- iOS 13+ / arm64 (KMP only)
