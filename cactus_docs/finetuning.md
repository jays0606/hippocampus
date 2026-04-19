# Deploying Unsloth Fine-Tunes to Cactus

Source: https://docs.cactuscompute.com/latest/docs/finetuning/

Cactus is an inference engine for mobile devices, Macs, and ARM chips like Raspberry Pi. INT8 quantization runs Qwen3-0.6B and LFM2-1.2B at 60–70 toks/sec on iPhone 17 Pro.

## Workflow

### 1. Train on GPU with Unsloth

```python
from unsloth import FastLanguageModel

model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="unsloth/gemma-3-4b-it",
    max_seq_length=2048,
    load_in_4bit=True,
)

model = FastLanguageModel.get_peft_model(
    model,
    r=16,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                    "gate_proj", "up_proj", "down_proj"],
    lora_alpha=16,
    lora_dropout=0,
    use_gradient_checkpointing="unsloth",
)

# ... train with SFTTrainer ...

model.save_pretrained("my-lora-adapter")
tokenizer.save_pretrained("my-lora-adapter")

# Optional
model.push_to_hub("username/my-lora-adapter")
```

### 2. Set up Cactus

```bash
git clone https://github.com/cactus-compute/cactus && cd cactus && source ./setup
```

### 3. Convert the adapter

```bash
# From local adapter — base model must match
cactus convert Qwen/Qwen3-0.6B ./my-qwen3-0.6b --lora ./my-lora-adapter

# From HF Hub
cactus convert Qwen/Qwen3-0.6B ./my-qwen3-0.6b --lora username/my-lora-adapter
```

### 4. Test locally

```bash
cactus build
cactus run ./my-qwen3-0.6b
```

### 5. iOS / macOS

```bash
cactus build --apple
```

Build artifacts:
```
Static libraries:
  Device: apple/libcactus-device.a
  Simulator: apple/libcactus-simulator.a
XCFrameworks:
  iOS: apple/cactus-ios.xcframework
  macOS: apple/cactus-macos.xcframework
```

Use in Swift:
```swift
import Foundation
import cactus

let modelPath = Bundle.main.path(forResource: "my-model", ofType: nil)!
let model = try cactusInit(modelPath, nil, false)

let messages = "[{\"role\":\"user\",\"content\":\"Hello!\"}]"
let resultJson = try cactusComplete(model, messages, nil, nil, nil)
if let data = resultJson.data(using: .utf8),
   let obj = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
   let response = obj["response"] as? String {
    print(response)
}

cactusDestroy(model)
```

Device testing:
```bash
cactus test --model <model-path-or-name> --ios
```

### 6. Android

```bash
cactus build --android
```

Place `libcactus.so` in `app/src/main/jniLibs/arm64-v8a/`, then:

```kotlin
import com.cactus.*
import org.json.JSONObject

val model = cactusInit("/data/local/tmp/my-model", null, false)
val resultJson = cactusComplete(model, """[{"role":"user","content":"Hello!"}]""", null, null, null)
val response = JSONObject(resultJson).getString("response")
println(response)
cactusDestroy(model)
```

Device testing:
```bash
cactus test --model <model-path-or-name> --android
```

## Compatible Base Models

Qwen3, Qwen3.5, Gemma3, LFM2, LFM2.5
