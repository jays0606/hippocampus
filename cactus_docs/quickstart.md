# Quickstart

Source: https://docs.cactuscompute.com/latest/docs/quickstart/

> You're viewing docs for **v1.14**. If you are cloning the repository, make sure to check out this release: `git checkout v1.14`

Install Cactus and run your first on-device AI completion.

## Installation

### React Native
```
npm install cactus-react-native react-native-nitro-modules
```

### Flutter
```
git clone https://github.com/cactus-compute/cactus && cd cactus && source ./setup
cactus build --flutter
```

Build output:

| File | Platform |
|------|----------|
| libcactus.so | Android (arm64-v8a) |
| cactus-ios.xcframework | iOS |
| cactus-macos.xcframework | macOS |

#### Platform Integration - Android
1. Copy `libcactus.so` to `android/app/src/main/jniLibs/arm64-v8a/`
2. Copy `cactus.dart` to your `lib/` folder

#### Platform Integration - iOS
1. Copy `cactus-ios.xcframework` to your `ios/` folder
2. Open `ios/Runner.xcworkspace` in Xcode
3. Drag the xcframework into the project
4. In Runner target > General > "Frameworks, Libraries, and Embedded Content", set to "Embed & Sign"
5. Copy `cactus.dart` to your `lib/` folder

#### Platform Integration - macOS
1. Copy `cactus-macos.xcframework` to your `macos/` folder
2. Open `macos/Runner.xcworkspace` in Xcode
3. Drag the xcframework into the project
4. In Runner target > General > "Frameworks, Libraries, and Embedded Content", set to "Embed & Sign"
5. Copy `cactus.dart` to your `lib/` folder

### Kotlin/Android
```
git clone https://github.com/cactus-compute/cactus && cd cactus && source ./setup
cactus build --android
```

Build output: `android/libcactus.so` (and `android/libcactus.a`)

#### Android-only Integration
1. Copy `libcactus.so` to `app/src/main/jniLibs/arm64-v8a/`
2. Copy `Cactus.kt` to `app/src/main/java/com/cactus/`

#### Kotlin Multiplatform Integration

Source files:

| File | Copy to |
|------|---------|
| Cactus.common.kt | shared/src/commonMain/kotlin/com/cactus/ |
| Cactus.android.kt | shared/src/androidMain/kotlin/com/cactus/ |
| Cactus.ios.kt | shared/src/iosMain/kotlin/com/cactus/ |
| cactus.def | shared/src/nativeInterop/cinterop/ |

Binary files:

| Platform | Location |
|----------|----------|
| Android | libcactus.so → app/src/main/jniLibs/arm64-v8a/ |
| iOS | libcactus-device.a → link via cinterop |

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

### Swift/Apple
```
git clone https://github.com/cactus-compute/cactus && cd cactus && source ./setup
cactus build --apple
```

Build outputs (in `apple/`):

| File | Description |
|------|-------------|
| cactus-ios.xcframework/ | iOS framework (device + simulator) |
| cactus-macos.xcframework/ | macOS framework |
| libcactus-device.a | Static library for iOS device |
| libcactus-simulator.a | Static library for iOS simulator |

#### iOS/macOS: XCFramework (Recommended)
1. Drag `cactus-ios.xcframework` (or `cactus-macos.xcframework`) into your Xcode project
2. Ensure "Embed & Sign" is selected in "Frameworks, Libraries, and Embedded Content"
3. Copy `Cactus.swift` into your project

#### iOS/macOS: Static Library
1. Add `libcactus-device.a` (or `libcactus-simulator.a`) to "Link Binary With Libraries"
2. Create a folder with `cactus_ffi.h` and `module.modulemap`, add to Build Settings:
3. "Header Search Paths" → path to folder
4. "Import Paths" (Swift) → path to folder
5. Copy `Cactus.swift` into your project

### Python
```
git clone https://github.com/cactus-compute/cactus && cd cactus && source ./setup
cactus build --python
```

### Rust
Add to `Cargo.toml`:
```toml
[dependencies]
cactus-sys = { path = "rust/cactus-sys" }
```

Build requirements: CMake, C++20 compiler, and platform tools (Xcode CLI on macOS, `build-essential` + `libcurl4-openssl-dev` + `libclang-dev` on Linux).

**Homebrew (macOS):**
```
brew install cactus-compute/cactus/cactus
```

**From Source (macOS):**
```
git clone https://github.com/cactus-compute/cactus && cd cactus && source ./setup
```

**From Source (Linux):**
```
sudo apt-get install python3 python3-venv python3-pip cmake build-essential libcurl4-openssl-dev
git clone https://github.com/cactus-compute/cactus && cd cactus && source ./setup
```

### CLI
```
cactus run LiquidAI/LFM2.5-350M
```

### C++
Include the Cactus header in your project:
```cpp
#include <cactus.h>
```

See the Cactus repository for CMake build instructions.

---

## Your First Completion

### React Native
```javascript
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
      messages: [{ role: 'user', content: 'What is the capital of France?' }],
    });
  };

  if (cactusLM.isDownloading) {
    return <Text>Downloading: {Math.round(cactusLM.downloadProgress * 100)}%</Text>;
  }

  return (
    <>
      <Button onPress={handleGenerate} title="Generate" />
      <Text>{cactusLM.completion}</Text>
    </>
  );
};
```

### Flutter
```dart
import 'cactus.dart';

final model = cactusInit('/path/to/model', null, false);
final messages = '[{"role":"user","content":"What is the capital of France?"}]';
final resultJson = cactusComplete(model, messages, null, null, null);
print(resultJson);
cactusDestroy(model);
```

### Kotlin
```kotlin
import com.cactus.*

val model = cactusInit("/path/to/model", null, false)
val messages = """[{"role":"user","content":"What is the capital of France?"}]"""
val resultJson = cactusComplete(model, messages, null, null, null)
println(resultJson)
cactusDestroy(model)
```

### Swift
```swift
import Foundation

let model = try cactusInit("/path/to/model", nil, false)
defer { cactusDestroy(model) }

let messages = #"[{"role":"user","content":"What is the capital of France?"}]"#
let resultJson = try cactusComplete(model, messages, nil, nil, nil)
print(resultJson)
```

### Python
```python
from src.downloads import ensure_model
from src.cactus import cactus_init, cactus_complete, cactus_destroy
import json

# Downloads weights from HuggingFace if not already present
weights = ensure_model("LiquidAI/LFM2-VL-450M")

model = cactus_init(str(weights), None, False)
messages = json.dumps([{"role": "user", "content": "What is 2+2?"}])
result = json.loads(cactus_complete(model, messages, None, None, None))
print(result["response"])
cactus_destroy(model)
```

### Rust
```rust
use cactus_sys::*;
use std::ffi::CString;

unsafe {
    let model_path = CString::new("path/to/weight/folder").unwrap();
    let model = cactus_init(model_path.as_ptr(), std::ptr::null(), false);

    let messages = CString::new(
        r#"[{"role": "user", "content": "What is the capital of France?"}]"#
    ).unwrap();

    let mut response = vec![0u8; 4096];
    cactus_complete(
        model, messages.as_ptr(),
        response.as_mut_ptr() as *mut i8, 4096,
        std::ptr::null(), std::ptr::null(),
        None, std::ptr::null_mut(),
    );

    println!("{}", String::from_utf8_lossy(&response));
    cactus_destroy(model);
}
```

### C++
```cpp
#include <cactus.h>

cactus_model_t model = cactus_init(
    "path/to/weight/folder",
    "path/to/rag/documents",
    false
);

const char* messages = R"([
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What is the capital of France?"}
])";

char response[4096];
int result = cactus_complete(
    model, messages, response, sizeof(response),
    nullptr, nullptr, nullptr, nullptr,
    nullptr, 0
);
```

---

## Supported Models

- **LLMs:** Gemma-3 (270M, FunctionGemma-270M, 1B), Gemma-4 (E2B, E4B), Gemma-3n (E2B, E4B), LiquidAI LFM2 (350M, 700M, 2.6B) / LFM2.5 (1.2B-Instruct, 1.2B-Thinking) / LFM2-8B-A1B, Qwen3 (0.6B, 1.7B), Tencent Youtu-LLM-2B (completion, tools, embeddings)
- **Vision:** Gemma-4 (E2B, E4B), LFM2-VL, LFM2.5-VL (450M, 1.6B) (with Apple NPU), Qwen3.5 (0.8B, 2B)
- **Audio:** Gemma-4 (E2B, E4B) with native speech understanding
- **Transcription:** Whisper (Tiny/Base/Small/Medium with Apple NPU), Parakeet (CTC-0.6B/CTC-1.1B/TDT-0.6B-v3 with Apple NPU), Moonshine-Base
- **VAD & Diarization:** Silero VAD, PyAnnote segmentation-3.0, WeSpeaker speaker embeddings
- **Embeddings:** Nomic-Embed, Qwen3-Embedding

See the full list on HuggingFace.

---

## Next Steps

- **Engine API** — Full inference API reference
- **Graph API** — Zero-copy computation graph for custom models
- **Fine-tuning & Deployment** — Convert and deploy custom fine-tunes
- **Choose Your SDK** — Help picking the right SDK for your project
