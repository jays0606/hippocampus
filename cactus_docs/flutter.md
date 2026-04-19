# Flutter SDK

Source: https://docs.cactuscompute.com/latest/flutter/

On-device AI through Dart FFI bindings for iOS, macOS, and Android. Pre-converted weights at https://huggingface.co/Cactus-Compute.

## Building

```bash
git clone https://github.com/cactus-compute/cactus && cd cactus && source ./setup
cactus build --flutter
```

Outputs:
- `libcactus.so` — Android (arm64-v8a)
- `cactus-ios.xcframework` — iOS
- `cactus-macos.xcframework` — macOS

## Integration

### Android
1. Copy `libcactus.so` → `android/app/src/main/jniLibs/arm64-v8a/`
2. Copy `cactus.dart` → `lib/`

### iOS
1. Copy `cactus-ios.xcframework` → `ios/`
2. Open `ios/Runner.xcworkspace` in Xcode
3. Drag xcframework into the project
4. Set "Embed & Sign"
5. Copy `cactus.dart` → `lib/`

### macOS
Same flow but with `cactus-macos.xcframework` in `macos/`.

## Usage Examples

### Basic Completion

```dart
import 'cactus.dart';

final model = cactusInit('/path/to/model', null, false);
final messages = '[{"role":"user","content":"What is the capital of France?"}]';
final resultJson = cactusComplete(model, messages, null, null, null);
print(resultJson);
cactusDestroy(model);
```

For vision models, add `"images": ["path/to/image.png"]`. For audio models (Gemma4), add `"audio": ["path/to/audio.wav"]`.

### Completion with Options and Streaming

```dart
import 'cactus.dart';
import 'dart:io';

final options = '{"max_tokens":256,"temperature":0.7}';

final resultJson = cactusComplete(model, messages, options, null, (token, tokenId) {
  stdout.write(token);
});
print(resultJson);
```

### Prefill

```dart
String cactusPrefill(
  CactusModelT model,
  String messagesJson,
  String? optionsJson,
  String? toolsJson,
)
```

Example:
```dart
final tools = '[{"type":"function","function":{"name":"get_weather",...}}]';
final messages = '[{"role":"system","content":"You are a helpful assistant."},'
  '{"role":"user","content":"What is the weather in Paris?"}]';

final resultJson = cactusPrefill(model, messages, null, tools);
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

### Audio Transcription

```dart
import 'cactus.dart';
import 'dart:typed_data';

// From file
final resultJson = cactusTranscribe(model, '/path/to/audio.wav', null, null, null, null);
print(resultJson);

// From PCM (16 kHz mono)
final pcmData = Uint8List.fromList([...]);
final resultJson2 = cactusTranscribe(model, null, null, null, null, pcmData);
print(resultJson2);
```

Process segments:
```dart
import 'dart:convert';

final result = jsonDecode(resultJson) as Map<String, dynamic>;
for (final seg in result['segments'] as List) {
  print('[${seg['start']}s - ${seg['end']}s] ${seg['text']}');
}
```

Custom vocabulary:
```dart
final options = '{"custom_vocabulary": ["Omeprazole", "HIPAA", "Cactus"], "vocabulary_boost": 3.0}';
final result = cactusTranscribe(model, '/path/to/audio.wav', '', options, null, null);
```

### Streaming Transcription

```dart
import 'cactus.dart';
import 'dart:typed_data';

final stream = cactusStreamTranscribeStart(model, null);

final Uint8List audioChunk = ...;
final partialJson = cactusStreamTranscribeProcess(stream, audioChunk);
print(partialJson);

final finalJson = cactusStreamTranscribeStop(stream);
print(finalJson);
```

### Embeddings

```dart
final Float32List embedding      = cactusEmbed(model, 'Hello, world!', true);
final Float32List imageEmbedding = cactusImageEmbed(model, '/path/to/image.jpg');
final Float32List audioEmbedding = cactusAudioEmbed(model, '/path/to/audio.wav');
```

### Tokenization

```dart
final List<int> tokens = cactusTokenize(model, 'Hello, world!');
final String scores = cactusScoreWindow(model, tokens, 0, tokens.length, 512);
```

### Detect Language

```dart
final resultJson = cactusDetectLanguage(model, '/path/to/audio.wav', null, null);
```

### VAD / Diarize / Embed Speaker

```dart
final vadJson = cactusVad(model, '/path/to/audio.wav', null, null);
final diarizeJson = cactusDiarize(model, '/path/to/audio.wav', null, null);
final embedJson = cactusEmbedSpeaker(model, '/path/to/audio.wav', null, null);
final embedJsonWeighted = cactusEmbedSpeaker(model, '/path/to/audio.wav', null, null, maskWeights);
```

Diarize options: `step_ms` (default 1000), `threshold`, `num_speakers`, `min_speakers`, `max_speakers`, `raw_powerset`.

### RAG

```dart
final String result = cactusRagQuery(model, 'What is machine learning?', 5);
print(result);
```

### Vector Index

```dart
final embDim = 4;
final index = cactusIndexInit('/path/to/index', embDim);

cactusIndexAdd(
  index,
  [1, 2],
  ['Document 1', 'Document 2'],
  [[0.1, 0.2, 0.3, 0.4], [0.5, 0.6, 0.7, 0.8]],
  null,
);

final resultsJson = cactusIndexQuery(index, [0.1, 0.2, 0.3, 0.4], null);
final getJson = cactusIndexGet(index, [1, 2]);

cactusIndexDelete(index, [2]);
cactusIndexCompact(index);
cactusIndexDestroy(index);
```

## API Reference

### Types

```dart
typedef CactusModelT            = Pointer<Void>;
typedef CactusIndexT            = Pointer<Void>;
typedef CactusStreamTranscribeT = Pointer<Void>;
```

### Init / Lifecycle

```dart
CactusModelT cactusInit(String modelPath, String? corpusDir, bool cacheIndex)
void cactusDestroy(CactusModelT model)
void cactusReset(CactusModelT model)
void cactusStop(CactusModelT model)
String cactusGetLastError()
```

### Prefill / Completion

```dart
String cactusPrefill(CactusModelT model, String messagesJson, String? optionsJson, String? toolsJson, {Uint8List? pcmData})
String cactusComplete(CactusModelT model, String messagesJson, String? optionsJson, String? toolsJson, void Function(String token, int tokenId)? callback, {Uint8List? pcmData})
```

### Transcription

```dart
String cactusTranscribe(CactusModelT model, String? audioPath, String? prompt, String? optionsJson, void Function(String, int)? callback, Uint8List? pcmData)

CactusStreamTranscribeT cactusStreamTranscribeStart(CactusModelT model, String? optionsJson)
String cactusStreamTranscribeProcess(CactusStreamTranscribeT stream, Uint8List pcmData)
String cactusStreamTranscribeStop(CactusStreamTranscribeT stream)
```

### Embeddings

```dart
Float32List cactusEmbed(CactusModelT model, String text, bool normalize)
Float32List cactusImageEmbed(CactusModelT model, String imagePath)
Float32List cactusAudioEmbed(CactusModelT model, String audioPath)
```

### Tokenization / Scoring

```dart
List<int> cactusTokenize(CactusModelT model, String text)
String cactusScoreWindow(CactusModelT model, List<int> tokens, int start, int end, int context)
```

### Audio / Detect Language / VAD / Diarize / Embed Speaker

```dart
String cactusDetectLanguage(CactusModelT model, String? audioPath, String? optionsJson, Uint8List? pcmData)
String cactusVad(CactusModelT model, String? audioPath, String? optionsJson, Uint8List? pcmData)
String cactusDiarize(CactusModelT model, String? audioPath, String? optionsJson, Uint8List? pcmData)
String cactusEmbedSpeaker(CactusModelT model, String? audioPath, String? optionsJson, Uint8List? pcmData, [Float32List? maskWeights])
```

### RAG

```dart
String cactusRagQuery(CactusModelT model, String query, int topK)
```

### Vector Index

```dart
CactusIndexT cactusIndexInit(String indexDir, int embeddingDim)
void cactusIndexDestroy(CactusIndexT index)
int cactusIndexAdd(CactusIndexT index, List<int> ids, List<String> documents, List<List<double>> embeddings, List<String>? metadatas)
int cactusIndexDelete(CactusIndexT index, List<int> ids)
String cactusIndexGet(CactusIndexT index, List<int> ids)
String cactusIndexQuery(CactusIndexT index, List<double> embedding, String? optionsJson)
int cactusIndexCompact(CactusIndexT index)
```

### Logging / Telemetry

```dart
void cactusLogSetLevel(int level)  // 0=DEBUG 1=INFO 2=WARN 3=ERROR 4=NONE
void cactusLogSetCallback(void Function(int level, String component, String message)? onLog)

void cactusSetTelemetryEnvironment(String cacheLocation)
void cactusSetAppId(String appId)
void cactusTelemetryFlush()
void cactusTelemetryShutdown()
```

## Bundling Model Weights

### Android — copy from assets to internal storage

```dart
import 'package:flutter/services.dart';
import 'package:path_provider/path_provider.dart';
import 'dart:io';

Future<String> getModelPath() async {
  final dir = await getApplicationDocumentsDirectory();
  final modelFile = File('${dir.path}/model');

  if (!await modelFile.exists()) {
    final data = await rootBundle.load('assets/model');
    await modelFile.writeAsBytes(data.buffer.asUint8List());
  }

  return modelFile.path;
}
```

### iOS / macOS

```dart
import 'dart:io';

final path = '${Directory.current.path}/model';
```

## Requirements

- Flutter 3.0+
- Dart 2.17+
- iOS 13.0+ / macOS 13.0+
- Android API 21+ / arm64-v8a
