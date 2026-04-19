# React Native SDK

Source: https://docs.cactuscompute.com/latest/react-native/

The Cactus React Native SDK builds AI-powered applications with language models, speech-to-text, audio processing, and vector indexing.

## Installation

```bash
npm install cactus-react-native react-native-nitro-modules
```

## Quick Start

### Class-Based Usage

```typescript
import { CactusLM, type CactusLMMessage } from 'cactus-react-native';

const cactusLM = new CactusLM();

await cactusLM.download({
  onProgress: (progress) => console.log(`Download: ${Math.round(progress * 100)}%`)
});

const messages: CactusLMMessage[] = [
  { role: 'user', content: 'What is the capital of France?' }
];

const result = await cactusLM.complete({ messages });
console.log(result.response);

await cactusLM.destroy();
```

### Hook-Based Usage

```typescript
import { useCactusLM } from 'cactus-react-native';

const App = () => {
  const cactusLM = useCactusLM();

  useEffect(() => {
    if (!cactusLM.isDownloaded) {
      cactusLM.download();
    }
  }, []);

  const handleGenerate = () => {
    cactusLM.complete({
      messages: [{ role: 'user', content: 'Hello!' }],
    });
  };

  if (cactusLM.isDownloading) {
    return (
      <Text>
        Downloading model: {Math.round(cactusLM.downloadProgress * 100)}%
      </Text>
    );
  }

  return (
    <>
      <Button onPress={handleGenerate} title="Generate" />
      <Text>{cactusLM.completion}</Text>
    </>
  );
};
```

## Language Model

### Model Options

```typescript
import { CactusLM } from 'cactus-react-native';

// Int8 quantization (default, better accuracy)
const cactusLM = new CactusLM({
  model: 'lfm2-vl-450m',
  options: {
    quantization: 'int8',
    pro: false
  }
});

// Pro models with NPU acceleration
const cactusPro = new CactusLM({
  model: 'lfm2-vl-450m',
  options: {
    quantization: 'int8',
    pro: true
  }
});
```

### Completion (Class)

```typescript
import { CactusLM, type CactusLMMessage } from 'cactus-react-native';

const cactusLM = new CactusLM();

const messages: CactusLMMessage[] = [{ role: 'user', content: 'Hello, World!' }];
const onToken = (token: string) => { console.log('Token:', token) };

const result = await cactusLM.complete({ messages, onToken });
console.log('Completion result:', result);
```

### Completion (Hook)

```typescript
import { useCactusLM, type CactusLMMessage } from 'cactus-react-native';

const App = () => {
  const cactusLM = useCactusLM();

  const handleComplete = async () => {
    const messages: CactusLMMessage[] = [{ role: 'user', content: 'Hello, World!' }];
    const result = await cactusLM.complete({ messages });
    console.log('Completion result:', result);
  };

  return (
    <>
      <Button title="Complete" onPress={handleComplete} />
      <Text>{cactusLM.completion}</Text>
    </>
  );
};
```

### Vision (Class)

```typescript
import { CactusLM, type CactusLMMessage } from 'cactus-react-native';

const cactusLM = new CactusLM({ model: 'lfm2-vl-450m' });

const messages: CactusLMMessage[] = [
  {
    role: 'user',
    content: "What's in the image?",
    images: ['path/to/your/image'],
  },
];

const result = await cactusLM.complete({ messages });
console.log('Response:', result.response);
```

### Vision (Hook)

```typescript
import { useCactusLM, type CactusLMMessage } from 'cactus-react-native';

const App = () => {
  const cactusLM = useCactusLM({ model: 'lfm2-vl-450m' });

  const handleAnalyze = async () => {
    const messages: CactusLMMessage[] = [
      {
        role: 'user',
        content: "What's in the image?",
        images: ['path/to/your/image'],
      },
    ];

    await cactusLM.complete({ messages });
  };

  return (
    <>
      <Button title="Analyze Image" onPress={handleAnalyze} />
      <Text>{cactusLM.completion}</Text>
    </>
  );
};
```

### Tool Calling (Class)

```typescript
import { CactusLM, type CactusLMMessage, type CactusLMTool } from 'cactus-react-native';

const tools: CactusLMTool[] = [
  {
    name: 'get_weather',
    description: 'Get current weather for a location',
    parameters: {
      type: 'object',
      properties: {
        location: { type: 'string', description: 'City name' },
      },
      required: ['location'],
    },
  },
];

const cactusLM = new CactusLM();

const messages: CactusLMMessage[] = [
  { role: 'user', content: "What's the weather in San Francisco?" },
];

const result = await cactusLM.complete({ messages, tools });
console.log('Response:', result.response);
console.log('Function calls:', result.functionCalls);
```

### RAG (Class)

```typescript
import { CactusLM, type CactusLMMessage } from 'cactus-react-native';

const cactusLM = new CactusLM({
  corpusDir: 'path/to/your/corpus',
});

const messages: CactusLMMessage[] = [
  { role: 'user', content: 'What information is in the documents?' },
];

const result = await cactusLM.complete({ messages });
console.log(result.response);
```

### RAG (Hook)

```typescript
import { useCactusLM, type CactusLMMessage } from 'cactus-react-native';

const App = () => {
  const cactusLM = useCactusLM({
    corpusDir: 'path/to/your/corpus',
  });

  const handleAsk = async () => {
    const messages: CactusLMMessage[] = [
      { role: 'user', content: 'What information is in the documents?' },
    ];

    await cactusLM.complete({ messages });
  };

  return (
    <>
      <Button title="Ask Question" onPress={handleAsk} />
      <Text>{cactusLM.completion}</Text>
    </>
  );
};
```

### Tokenization

```typescript
const result = await cactusLM.tokenize({ text: 'Hello, World!' });
console.log('Token IDs:', result.tokens);
```

### Score Window

```typescript
const tokens = [123, 456, 789, 101, 112];
const result = await cactusLM.scoreWindow({
  tokens,
  start: 1,
  end: 3,
  context: 2
});
console.log('Score:', result.score);
```

### Text Embedding

```typescript
const result = await cactusLM.embed({ text: 'Hello, World!' });
console.log('Embedding vector:', result.embedding);
```

### Image Embedding

```typescript
const cactusLM = new CactusLM({ model: 'lfm2-vl-450m' });
const result = await cactusLM.imageEmbed({ imagePath: 'path/to/your/image.jpg' });
console.log('Image embedding vector:', result.embedding);
```

## Speech-to-Text (STT)

The `CactusSTT` class provides audio transcription and embedding using models like Whisper and Moonshine.

### Transcription (Class)

```typescript
import { CactusSTT } from 'cactus-react-native';

const cactusSTT = new CactusSTT({ model: 'whisper-small' });

// From file path
const result = await cactusSTT.transcribe({
  audio: 'path/to/audio.wav',
  onToken: (token) => console.log('Token:', token)
});
console.log('Transcription:', result.response);

// From PCM samples
const pcmSamples: number[] = [/* ... */];
const result2 = await cactusSTT.transcribe({
  audio: pcmSamples,
  onToken: (token) => console.log('Token:', token)
});
console.log('Transcription:', result2.response);
```

### Transcription (Hook)

```typescript
import { useCactusSTT } from 'cactus-react-native';

const App = () => {
  const cactusSTT = useCactusSTT({ model: 'whisper-small' });

  const handleTranscribe = async () => {
    const result = await cactusSTT.transcribe({ audio: 'path/to/audio.wav' });
    console.log('Transcription:', result.response);
  };

  return (
    <>
      <Button onPress={handleTranscribe} title="Transcribe" />
      <Text>{cactusSTT.transcription}</Text>
    </>
  );
};
```

### Streaming Transcription (Class)

```typescript
import { CactusSTT } from 'cactus-react-native';

const cactusSTT = new CactusSTT({ model: 'whisper-small' });

await cactusSTT.streamTranscribeStart({
  confirmationThreshold: 0.99,
  minChunkSize: 32000,
});

const audioChunk: number[] = [/* PCM samples as bytes */];
const result = await cactusSTT.streamTranscribeProcess({ audio: audioChunk });

console.log('Confirmed:', result.confirmed);
console.log('Pending:', result.pending);

const final = await cactusSTT.streamTranscribeStop();
console.log('Final confirmed:', final.confirmed);
```

### Streaming Transcription (Hook)

```typescript
import { useCactusSTT } from 'cactus-react-native';

const App = () => {
  const cactusSTT = useCactusSTT({ model: 'whisper-small' });

  const handleStart = async () => {
    await cactusSTT.streamTranscribeStart({ confirmationThreshold: 0.99 });
  };

  const handleChunk = async (audioChunk: number[]) => {
    const result = await cactusSTT.streamTranscribeProcess({ audio: audioChunk });
    console.log('Confirmed:', result.confirmed);
    console.log('Pending:', result.pending);
  };

  const handleStop = async () => {
    const final = await cactusSTT.streamTranscribeStop();
    console.log('Final:', final.confirmed);
  };

  return (
    <>
      <Button onPress={handleStart} title="Start" />
      <Button onPress={handleStop} title="Stop" />
      <Text>{cactusSTT.streamTranscribeConfirmed}</Text>
      <Text>{cactusSTT.streamTranscribePending}</Text>
    </>
  );
};
```

### Audio Embedding

```typescript
const result = await cactusSTT.audioEmbed({ audioPath: 'path/to/audio.wav' });
console.log('Audio embedding vector:', result.embedding);
```

### Language Detection (Class only)

```typescript
const cactusSTT = new CactusSTT({ model: 'whisper-small' });

const result = await cactusSTT.detectLanguage({
  audio: 'path/to/audio.wav',
  options: { useVad: true },
});

console.log('Language:', result.language);
console.log('Confidence:', result.confidence);
```

## Audio Processing

The `CactusAudio` class provides voice activity detection, speaker diarization, and speaker embeddings.

### Voice Activity Detection

```typescript
import { CactusAudio } from 'cactus-react-native';

const cactusAudio = new CactusAudio({ model: 'silero-vad' });

const result = await cactusAudio.vad({
  audio: 'path/to/audio.wav',
  options: {
    threshold: 0.5,
    minSpeechDurationMs: 250,
    minSilenceDurationMs: 100,
  }
});

console.log('Speech segments:', result.segments);
console.log('Total time (ms):', result.totalTime);
```

### Speaker Diarization

```typescript
const result = await cactusAudio.diarize({
  audio: 'path/to/audio.wav',
  options: {
    numSpeakers: 2,
    minSpeakers: 1,
    maxSpeakers: 4,
  }
});

console.log('Number of speakers:', result.numSpeakers);
console.log('Scores:', result.scores);
```

### Speaker Embedding

```typescript
const result = await cactusAudio.embedSpeaker({ audio: 'path/to/audio.wav' });
console.log('Speaker embedding:', result.embedding);
```

### Hook Implementation

```typescript
import { useCactusAudio } from 'cactus-react-native';

const App = () => {
  const cactusAudio = useCactusAudio({ model: 'silero-vad' });

  const handleVAD = async () => {
    const result = await cactusAudio.vad({ audio: 'path/to/audio.wav' });
    console.log('Speech segments:', result.segments);
  };

  const handleDiarize = async () => {
    const result = await cactusAudio.diarize({ audio: 'path/to/audio.wav' });
    console.log('Speakers:', result.numSpeakers);
  };

  return (
    <>
      <Button title="Detect Speech" onPress={handleVAD} />
      <Button title="Diarize" onPress={handleDiarize} />
    </>
  );
};
```

## Vector Index

The `CactusIndex` class provides vector storage and similarity search.

### Initialize

```typescript
import { CactusIndex } from 'cactus-react-native';

const cactusIndex = new CactusIndex('my-index', 1024);
await cactusIndex.init();
```

Hook:
```typescript
import { useCactusIndex } from 'cactus-react-native';

const App = () => {
  const cactusIndex = useCactusIndex({ name: 'my-index', embeddingDim: 1024 });
  const handleInit = async () => { await cactusIndex.init(); };
  return <Button title="Initialize Index" onPress={handleInit} />;
};
```

### Add Documents

```typescript
await cactusIndex.add({
  ids: [1, 2, 3],
  documents: ['First document', 'Second document', 'Third document'],
  embeddings: [[0.1, 0.2, ...], [0.3, 0.4, ...], [0.5, 0.6, ...]],
  metadatas: ['metadata1', 'metadata2', 'metadata3']
});
```

### Query

```typescript
const result = await cactusIndex.query({
  embeddings: [[0.1, 0.2, ...]],
  options: { topK: 5, scoreThreshold: 0.7 }
});

console.log('IDs:', result.ids);
console.log('Scores:', result.scores);
```

### Get / Delete / Compact

```typescript
const result = await cactusIndex.get({ ids: [1, 2, 3] });
console.log('Documents:', result.documents);

await cactusIndex.delete({ ids: [1, 2, 3] });
await cactusIndex.compact();
```

## API Reference

### CactusLM Class

#### Constructor

`new CactusLM(params?: CactusLMParams)`

- `model` — Model identifier or file path (default: `'qwen3-0.6b'`)
- `corpusDir` — Directory with text files for RAG (default: `undefined`)
- `cacheIndex` — Cache RAG corpus index on disk (default: `false`)
- `options.quantization` — `'int4'` | `'int8'` (default: `'int8'`)
- `options.pro` — Enable NPU acceleration (default: `false`)

#### Methods

- `download(params?)` — Downloads model. Optional `onProgress(progress: number)` callback.
- `init()` — Initializes the model (idempotent).
- `complete(params)` — Text generation with optional streaming and tool calling.
- `prefill(params)` — Runs prompt prefill without generating output tokens.
- `tokenize(params)` — Converts text into token IDs.
- `scoreWindow(params)` — Calculates log-probability scores.
- `embed(params)` — Generates text embeddings.
- `imageEmbed(params)` — Generates image embeddings (vision model required).
- `stop()` — Stops ongoing generation.
- `reset()` — Resets internal state and cached context.
- `destroy()` — Releases all resources.
- `getModels()` — Returns available models.
- `getModelName()` — Returns model identifier with quantization/pro suffix.

`complete` options:
- `temperature`, `topP`, `topK`
- `maxTokens` (default: 512)
- `stopSequences`
- `forceTools` (default: false)
- `telemetryEnabled` (default: true)
- `confidenceThreshold` (default: 0.7) — cloud handoff threshold
- `toolRagTopK` (default: 2) — tool selection count
- `includeStopSequences` (default: false)
- `useVad` (default: true)
- `enableThinking`

### useCactusLM Hook

State:
- `completion: string` — Accumulated generated text
- `isGenerating`, `isInitializing`, `isDownloaded`, `isDownloading`
- `downloadProgress: number` (0-1)
- `error: string | null`

Methods mirror `CactusLM`. `complete`, `reset`, and `destroy` clear `completion`.

### CactusSTT Class

Constructor: `new CactusSTT(params?: CactusSTTParams)`
- `model` (default: `'whisper-small'`)
- `options.quantization` — `'int4'` | `'int8'` (default: `'int8'`)
- `options.pro` — NPU acceleration (default: false)

Methods:
- `download`, `init`, `transcribe`, `audioEmbed`
- `streamTranscribeStart(options?)` — start streaming session
- `streamTranscribeProcess({audio})` — feed PCM chunk
- `streamTranscribeStop()` — finalize
- `detectLanguage`, `stop`, `reset`, `destroy`, `getModels`, `getModelName`

`transcribe` options:
- `temperature`, `topP`, `topK`
- `maxTokens` (default: 384)
- `stopSequences`
- `useVad` (default: true)
- `telemetryEnabled` (default: true)
- `confidenceThreshold` (default: 0.7)
- `cloudHandoffThreshold`
- `includeStopSequences` (default: false)

`streamTranscribeStart` options:
- `confirmationThreshold` (default: 0.99)
- `minChunkSize` (default: 32000)
- `telemetryEnabled` (default: true)
- `language` (auto-detect if unset)

### useCactusSTT Hook

State:
- `transcription`, `streamTranscribeConfirmed`, `streamTranscribePending`
- `isGenerating`, `isStreamTranscribing`, `isInitializing`, `isDownloaded`, `isDownloading`
- `downloadProgress`, `error`

### CactusAudio Class

Constructor: `new CactusAudio(params?: CactusAudioParams)`
- `model` (default: `'silero-vad'`)
- `options.quantization`, `options.pro`

Methods: `download`, `init`, `vad`, `diarize`, `embedSpeaker`, `destroy`, `getModels`, `getModelName`

VAD options: `threshold`, `negThreshold`, `minSpeechDurationMs`, `maxSpeechDurationS`, `minSilenceDurationMs`, `speechPadMs`, `windowSizeSamples`, `samplingRate`, `minSilenceAtMaxSpeech`, `useMaxPossSilAtMaxSpeech`.

Diarize options: `stepMs`, `threshold`, `numSpeakers`, `minSpeakers`, `maxSpeakers`.

### CactusIndex Class

Constructor: `new CactusIndex(name: string, embeddingDim: number)`

Methods: `init`, `add`, `query`, `get`, `delete`, `compact`, `destroy`

Query options:
- `topK` (default: 10)
- `scoreThreshold` (default: -1.0)

### getRegistry

```typescript
import { getRegistry } from 'cactus-react-native';

const registry = await getRegistry();
const model = registry['qwen3-0.6b'];
```

## Type Definitions (selected)

### CactusLMMessage

```typescript
interface CactusLMMessage {
  role: 'user' | 'assistant' | 'system';
  content?: string;
  images?: string[];
}
```

### CactusLMTool

```typescript
interface CactusLMTool {
  name: string;
  description: string;
  parameters: {
    type: 'object';
    properties: { [key: string]: { type: string; description: string } };
    required: string[];
  };
}
```

### CactusLMCompleteResult

```typescript
interface CactusLMCompleteResult {
  success: boolean;
  response: string;
  thinking?: string;
  functionCalls?: { name: string; arguments: { [key: string]: any } }[];
  cloudHandoff?: boolean;
  confidence?: number;
  timeToFirstTokenMs: number;
  totalTimeMs: number;
  prefillTokens: number;
  prefillTps: number;
  decodeTokens: number;
  decodeTps: number;
  totalTokens: number;
  ramUsageMb?: number;
}
```

### CactusModel

```typescript
interface CactusModel {
  slug: string;
  capabilities: string[];
  quantization: {
    int4: { sizeMb: number; url: string; pro?: { apple: string } };
    int8: { sizeMb: number; url: string; pro?: { apple: string } };
  };
}
```

### CactusAudioVADResult

```typescript
interface CactusAudioVADResult {
  segments: { start: number; end: number }[];
  totalTime: number;
  ramUsage: number;
}
```

### CactusIndexQueryResult

```typescript
interface CactusIndexQueryResult {
  ids: number[][];
  scores: number[][];
}
```
