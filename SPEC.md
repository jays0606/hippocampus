# Hippocampus — Hackathon Final Spec (v3)

*Voice-first on-device memory for people whose own is slipping.*

**Positioning (read before every rehearsal):** Hippocampus is a **memory prosthesis** — a hearing aid for a failing hippocampus. It does **not** cure, treat, reverse, or slow Alzheimer's. Nothing currently does. What it does is externalize the function the damaged organ can no longer perform: remembering what was where, when, and with whom. The prosthesis metaphor is load-bearing for regulatory clarity (durable medical equipment reimbursement template), for clinical legitimacy (clinicians understand prosthetics intuitively), and for legal safety (we never make a treatment claim). The opening line *"so we built her a new one"* is a metaphor for the prosthesis; the Q&A (Part 14, Q8) pins this down explicitly the moment a judge probes.

**Ground truth (verified at H-1 against `cactus_docs/react-native.md` and the working sibling repo `../military-medic/MedicApp`):**

- SDK surface: `cactus-react-native ^1.13.0`. Model slug **`gemma-4-e2b-it`** (lowercase, no namespace). Model download size **4.68 GB** (not 1.5 GB as earlier drafts assumed). Peak RAM ~1.4–1.9 GB for the LM alone; add ~300 MB for Whisper-small + Silero-VAD → ~2.2 GB concurrent.
- `options: { quantization: 'int4', pro: true }` is required to get the NPU-accelerated `-int4-apple.zip` weights on iPhone 17 Pro. Without `pro: true` you fall back to CPU prefill — measurably slower, breaks the sub-second pitch.
- **cactus-react-native v1.13.0 has two show-stopper bugs that prevent Gemma 4 E2B from downloading with `pro: true`.** Fix: copy `/Users/jaehoshin/personal/military-medic/MedicApp/patches/cactus-react-native+1.13.0.patch` verbatim into `MedicApp/patches/` and run `patch-package` postinstall. This bumps `RUNTIME_VERSION` to `1.14.0` so the `-int4-apple` tag resolves, and accepts models that ship only `int4` (Gemma 4 E2B/E4B) instead of requiring both `int4` and `int8`. **Do this at H0 before any other RN work.**
- `toolRagTopK` confirmed as a real `complete()` option (default 2). The SPEC's reliance on `toolRagTopK: 6` is correct.
- **Two defaults that silently violate "airplane mode" and MUST be overridden on every `complete()` and `transcribe()` call:**
  - `telemetryEnabled: true` → set to `false`. Otherwise the SDK posts usage telemetry on generation completion, and our network HUD will show outbound bytes.
  - `confidenceThreshold: 0.7` → set to `0`. This is the cloud-handoff threshold. At default, any low-confidence turn may trigger a cloud call — our "nothing leaves the phone" claim becomes false on a single unlucky prompt.
- Vision (`messages[].images: [path]`) is documented only for `lfm2-vl-450m` in the RN docs; Gemma 4 E2B vision via RN is **unverified in both docs and in any working codebase we have access to**. This is the single highest project risk. H0 verification must empirically test it with a file URI, or Beats 1/2 drop to pre-seeded fallback.
- Audio-in to Gemma 4 in a single `complete()` call is supported by the native Swift/Apple SDK (`messages[].audio: [path]`) but **not exposed by the RN JS wrapper** — `CactusLMMessage` only has `role`, `content`, `images`. STT → text → LM remains the correct RN pipeline. Writing a native bridge to expose audio-in is ~3h of work we are not spending.
- `lm.prefill({ messages: [system], tools })` is a real method — call once at startup to warm the KV cache so the first user turn doesn't pay the system-prompt prefill cost. MedicApp uses this pattern and we should copy it.
- Use streaming STT (`streamTranscribeStart/Process/Stop`), not batch `transcribe()`, so confirmed tokens can flow to Gemma before the user finishes speaking.

**Event**: Gemma 4 Voice Agents Hackathon · YC HQ · Apr 18–19, 2026
**Submission**: Sun 11am · **Demo**: 1pm judging · 90 seconds on stage
**Stack**: iPhone 17 Pro · Gemma 4 E2B · Cactus SDK (React Native) · No cloud
**Team**: 3–4 engineers · ~22 working hours to submission

**v3 changes from v2 (pitch pass for YC judges):**
- Rewrote the opening — the product's name is now the *first word spoken*, not a slide reveal after 15 seconds of setup
- **Positioned the product neurologically, not consumer-ly.** Every beat now escalates within a dementia frame: small fear (glasses → "the floor moves") → daily dread (pills) → existential grief (Margaret). The wedge is dementia caregivers; the TAM expands down-severity-curve to 70M with any memory impairment.
- Replaced Beat 3 (daily digest) with **the Margaret moment** — the emotional climax that showcases profile-driven behavior, the one feature no cloud product can copy
- Added neurological framing to Beat 1 (glasses → "the floor moves") so it stops reading as an Alexa flex and starts reading as a dementia-aware memory aid
- Tightened the close to one competitor (Microsoft Recall) and one number (70M Americans); cut the triple-stat pile-up
- Added `compose_daily_digest` to the H10 cut list (no longer demo-critical)

**v2 changes from v1:**
- Added caregiver-authored profile (§6) — meds, symptoms, doctors, family, triggers
- Clarified image lifecycle and when disk writes happen (§7)
- Reduced cron list to the two that run in MVP (§8)
- Revised Beat 3 to a single-device voice-only digest (§3) — *superseded in v3*
- Added team-alignment section for persuading co-founders (§P at end)

---

## Part 1 — The pitch (what you say on stage)

### The opening (15 seconds, no slides)

Founder walks on stage. No smile. Holds up an iPhone.

> *"The hippocampus is the part of the brain that fails first in Alzheimer's."*
>
> *"My grandmother's is failing. She asks my mother 'did I take my pills?' six times a day. My mother answers six times a day. By dinner, neither of them remembers the conversation."*
>
> *"So we built her a new one."*

Pause. Slide: **Hippocampus.**

> *"It runs on her phone. It never touches the cloud. Watch."*

**Why this opens the way it does.** The product name is the *first word of the pitch* — it earns its meaning (a failing brain region) before it earns its slide. There is no stat in the opening: numbers go in the close, where the judge has already decided they care. "So we built her a new one" is the line the room remembers on the walk to lunch.

---

## Part 2 — The demo arc, 60 seconds, three beats

### Staging (done 30 minutes before judging)

- iPhone 17 Pro on MagSafe dock, camera facing a small "kitchen" scene on a table: coffee mug, pill bottle, keys on a napkin, reading glasses, a plant.
- Airplane mode on. Network monitor visible on laptop next to dock, showing 0 bytes.
- App running. The vision loop has been observing the table for 30 min. `memory.db` contains real entries: *mug placed 12:15, keys placed 12:33, pill_bottle tipped+drunk 12:40 (event: kind=med_taken, certainty=observed), glasses placed 1:02.*
- Caregiver profile file loaded at app launch — *"Helen, 79, mid-stage Alzheimer's, takes Donepezil 10mg at 8am, daughter Sarah, late sister Margaret (do not confuse)."*

### Beat 1 — Spatial recall (25s)

Founder picks up the glasses, walks two steps, sets them on a chair behind him. Walks back. Doesn't touch the phone.

> *"Hey Hippo — where are my glasses?"*

Sub-second. Hippo's premium voice:

> *"On the chair behind you. You set them there eight seconds ago."*

Room reacts. Founder hasn't touched the screen. He turns to the audience, doesn't break stride:

> *"For you and me, losing our glasses is annoying. For my grandmother, it's the moment the floor moves — she thinks the disease just took another piece of her. Hippocampus watched. So she doesn't have to be afraid."*

### Beat 2 — The meds moment (20s)

Founder turns to face the room, hands at his sides.

> *"Hey Hippo — did I take my pills?"*

> *"Yes Helen. At 12:40. I watched."*

One-second silence. Then:

> *"This is the answer my grandmother needs six times a day. Not an alarm. Not a reminder. An answer — from someone who was watching."*

### Beat 3 — The Margaret moment (25s)

Founder softens. Speaks to the phone like he's speaking for his grandmother — slightly slower, a shade quieter.

> *"Hey Hippo — is Margaret coming today?"*

No delay. Hippo's voice, warm and even:

> *"Not today, Helen. But Sarah's going to call you tonight. Would you like to hear some Chopin?"*

Founder lets the silence sit for a full second. Then, to the room:

> *"Margaret was Helen's sister. She passed in 2019. Helen still asks, most afternoons."*
>
> *"We never taught Hippocampus to lie. Her daughter wrote one line in a profile file — 'don't confirm, redirect gently.' The device follows it."*

Founder turns to the network HUD on the laptop.

> *"And because nothing — nothing — ever leaves this phone, her daughter is the only person on earth who knows her mother still asks."*

### Why Beat 3 is the Margaret moment (diff from v2)

v1 had a second phone. v2 had a spoken daily digest. v3 replaces both with the single line in the profile that tells Hippo how to handle a dead sister. Reasons:

- **Pills is table stakes; Margaret is memorable.** Every judge in the room has seen an AI pill reminder demo before. Zero of them have seen an AI handle grief with restraint. This is the beat screenshot-and-quoted on Monday morning.
- **It demos the one feature no cloud product can copy.** The confusion_notes → system prompt pipeline *is* the moat. Recall can't ship this. Alexa can't ship this. Only a device that holds private clinical context locally can.
- **It makes "on-device" emotionally load-bearing, not a checkbox.** The reason nothing leaves the phone isn't performance or GDPR — it's that Helen's dead sister is no one else's business. The airplane-mode HUD finally *means* something.
- **It carries the TAM expansion through implication, not staging.** "Her daughter is the only person on earth who knows her mother still asks" telegraphs the caregiver-as-buyer story without needing a second device or BLE hack.
- **It's cheaper to build.** No digest generator, no 15-second summary logic. Just confusion_notes in the system prompt — already on the critical path.

### Close (20s)

> *"Microsoft tried to ship a memory layer last year. They called it Recall. They killed it twice — because they built it in the cloud."*
>
> *"We built it where a memory belongs: on the device in her pocket."*
>
> *"Seventy million Americans are losing theirs. Medicare already pays fifty dollars a month to keep them home instead of in a nursing facility. We bill the insurer. Grandma keeps her life."*
>
> *"Hippocampus. Thank you."*

**Why this close over v2.** The Medicare line is not a tangent — it's the line that turns "sad demo about grandma" into "$4B ARR with a built-in payer." YC partners fund the second one. The number is defensible: CPT codes 99453–99458 reimburse $50–160/patient/month for Remote Patient Monitoring, and RPM billing requires a written care plan, which our profile file literally is. Say it in the pitch, not the Q&A — by Q&A the judge has already decided.

---

## Part 3 — Scope, final

### IN for MVP

- Voice I/O: `CactusSTT` (Whisper-small) + `CactusAudio` Silero VAD in; iOS native `AVSpeechSynthesizer` premium voice out via `react-native-tts` bridge (sentence-buffered)
- Gemma 4 E2B loaded via `CactusLM` (RN), tool calling with **`toolRagTopK: 6`** so all six Hippo tools are visible every turn (RN default is 2 — would silently hide 4 of our tools)
- Camera frames via `react-native-vision-camera` (2fps), passed as `images: [path]` to `CactusLM.complete({...})`
- SSIM change-detector in JS / native util (not a Cactus feature)
- **Caregiver profile** (JSON file, loaded at startup) — new in v2
- `memory.db` as plain SQLite (not encrypted) — **not** `CactusIndex`/`cactusRagQuery`, because Hippo queries are structured-exact, not semantic
- Live vision loop writing to memory during demo
- Pre-seeded memory from 30-min pre-demo observation
- Six memory tools (spec'd below)
- Docked mode — always-on listening while on MagSafe
- Network HUD on demo laptop (Little Snitch network map — zero bytes visible)
- **Technical HUD on demo laptop (second window)** — live `ramUsageMb`, tokens/sec, single-pass modality breakdown per turn. Makes the on-device feat *visible* to DeepMind judges. ~2h in Workstream E.
- **Caregiver view** — single static HTML file generated from `memory.db` at end of demo. Opened on laptop for 3 seconds during close. Shows "what Sarah sees tonight." No backend, no sync. ~2h in Workstream E.
- Spoken digest tool — *cut in v3*, demo uses Margaret beat instead

### OUT for MVP (roadmap)

- SQLite encryption / Secure Enclave
- Real BLE caregiver device pairing
- Real push notifications to a second phone
- Proactive safety interrupts (stove/door/fall)
- People recognition (voice/face prints)
- Routine learning (nightly cron)
- Frame purge cron (not needed in 90s)
- Android
- Voice cloning
- Multi-language
- Hybrid Gemini fallback

### Cut list if behind at H10 (in order)

1. Live vision writing memory → pre-seed completely (saves 4h)
2. `compose_daily_digest` tool → cut entirely (saves 1h) — no longer demo-critical after v3's Margaret beat replaced the digest on stage
3. `describe_current_scene` tool → cut (saves 1h)
4. `forget_last_minutes` tool → stub (saves 30m)

### Do not cut under any circumstance

- Voice I/O pipeline
- `memory.db` + four query tools
- **Caregiver profile loader — the Margaret beat depends entirely on `confusion_notes` being wired into the system prompt. If profile loading breaks, Beat 3 becomes a generic chatbot response and the demo collapses.**
- Gemma 4 E2B voice response
- Network HUD + airplane mode
- The three demo beats

---

## Part 4 — The architecture diagram

```
┌───────────────────────────────────────────────────────────────┐
│              iPhone 17 Pro (Helen's phone, docked)            │
│                                                               │
│   React Native app (one codebase)                             │
│                                                               │
│   ┌──────────────────────────────────────────────────────┐    │
│   │  [admin_profile.json]  ← loaded once at startup      │    │
│   │  name · age · diagnosis · meds · doctors · family    │    │
│   │  confusion_notes · quiet_hours · tracked_objects     │    │
│   └───────────────────────┬──────────────────────────────┘    │
│                           │                                   │
│   ┌───────────────────────▼──────────────────────────────┐    │
│   │                  Cactus SDK                          │    │
│   │  CactusSTT (Whisper) · CactusAudio (Silero VAD)      │    │
│   │  CactusLM (Gemma 4 E2B + native function calling)    │    │
│   └────────────┬──────────────────────────┬──────────────┘    │
│                │                          │                   │
│     ┌──────────▼────────────┐  ┌──────────▼──────────────┐    │
│     │  Perception loop      │  │    memory.db (SQLite)    │    │
│     │  cam 2fps · VAD-gated │  │  objects · state ·       │    │
│     │  change-detect first  │  │  events · meds_schedule  │    │
│     │  → Gemma scene-tag    │  │                          │    │
│     │  → JSON writer        │  │  + frames/ (24h, local)  │    │
│     └───────────────────────┘  └──────────────────────────┘    │
│                │                          ▲                   │
│                └──────────────────────────┘                   │
│                           │                                   │
│   ┌───────────────────────▼──────────────────────────────┐    │
│   │            AVSpeechSynthesizer (premium)             │    │
│   │            streaming · mic-gated while speaking      │    │
│   └──────────────────────────────────────────────────────┘    │
│                                                               │
│   Zero network code on critical paths. airplane mode on.      │
└───────────────────────────────────────────────────────────────┘
```

---

## Part 5 — The three actors

Even though we're not building real multi-device sync, the product conceptually has three roles. The profile file encodes the caregiver's intent; the voice interface serves the user; the digest output is consumed (in v2 production) by the family.

| Actor | Experience in MVP | What they actually touch |
|---|---|---|
| **User (Helen)** | Voice only. Never sees the app. Docked phone on counter. | Nothing — just talks |
| **Caregiver (Sarah)** | *Conceptually* authored `admin_profile.json`. Not building real admin app for demo. | Pre-seeded JSON file |
| **Family** | *Conceptually* receives the digest. Voice-only digest demoed on Helen's device. | Nothing real |

---

## Part 6 — Caregiver profile (new section)

The profile file transfers clinical and biographical context from caregiver to device before Hippocampus ever observes anything. This is the Day 1 cold-start fix: without it, Hippo is blank for a week. With it, Hippo knows Helen's world on install.

### Shape — `admin_profile.json`

```json
{
  "user": {
    "name": "Helen",
    "preferred_name": "Helen",
    "age": 79,
    "diagnosis": "Mid-stage Alzheimer's, diagnosed 2023",
    "allergies": ["penicillin"],
    "dnr": false
  },

  "medications": [
    {
      "name": "Donepezil 10mg",
      "schedule": "daily 08:00",
      "location": "kitchen cabinet, white bottle",
      "purpose": "Alzheimer's — slows progression"
    },
    {
      "name": "Lisinopril 5mg",
      "schedule": "daily 08:00",
      "location": "kitchen cabinet, white bottle",
      "purpose": "blood pressure"
    }
  ],

  "doctors": [
    { "name": "Dr. Chen", "specialty": "Neurologist", "phone": "555-0123" },
    { "name": "Dr. Park", "specialty": "Primary care", "phone": "555-0456" }
  ],

  "family": [
    { "name": "Sarah", "relationship": "daughter", "phone": "555-0789", "is_caregiver": true },
    { "name": "Robert", "relationship": "son", "phone": "555-0234" },
    { "name": "Margaret", "relationship": "sister", "deceased": true, "deceased_year": 2019 }
  ],

  "confusion_notes": [
    "Sometimes asks about Margaret — do not confirm or deny she's coming, gently redirect.",
    "Confuses Sarah (daughter) with Margaret (late sister) in the afternoon.",
    "Becomes agitated if asked 'do you remember' — avoid that phrasing."
  ],

  "triggers": {
    "agitation": ["loud TV", "multiple voices at once"],
    "comfort": ["classical music", "Sarah's voice"]
  },

  "home": {
    "rooms_private": ["bathroom", "bedroom"],
    "rooms_monitored": ["kitchen", "living_room", "hallway"],
    "quiet_hours": { "start": "22:00", "end": "07:00" }
  },

  "tracked_objects": [
    "keys", "glasses", "pill_bottle", "mug", "phone", "wallet", "remote"
  ],

  "digest": {
    "enabled": true,
    "time": "20:00",
    "recipient_name": "Sarah"
  }
}
```

### How it gets used

**At app startup:** `admin_profile.json` is loaded and parsed into app state. The caregiver-configured medications get inserted into `memory.db`'s `meds_schedule` table. The tracked_objects list becomes the bounded vocabulary for the vision loop. Confusion notes get injected into Gemma 4's system prompt at every turn.

**In the system prompt:** confusion notes become part of Hippo's standing instructions. Example:

```
SYSTEM PROMPT (portion):
You are Hippo, a memory for Helen. Helen is 79 and has mid-stage Alzheimer's.
Her daughter Sarah is her caregiver.

Important notes from Sarah:
- Helen sometimes asks about her sister Margaret, who passed away in 2019.
  Do not confirm or deny she is coming. Gently redirect to something pleasant.
- Helen sometimes confuses Sarah with Margaret. If she calls you by the wrong
  name, do not correct her.
- Do not use the phrase "do you remember" — it agitates her. Say "earlier
  today" or "a little while ago" instead.
```

**In tool responses:** the `query_meds_today` tool joins profile's medication list with `memory.db`'s events table to determine what's due and what's been observed. Family/doctor data is templated into the system prompt directly at startup — no runtime tool needed for Beat 2 or Beat 3, and adding family-lookup tools would push the tool count past the `toolRagTopK: 6` window.

### Why this is the fifth essential feature

1. **Judges notice cold-start.** Without profile, a hackathon demo of "AI that learns your home over time" has to handwave Day 1. With profile, Day 1 is compelling.
2. **It's the only place clinical context lives.** Doctor names, diagnosis, allergies, DNR — none of this can be *learned*. It has to be told. Without profile, the product can only ever be a consumer gadget, not a healthcare tool.
3. **It's the Medicare Advantage story.** RPM reimbursement requires a care plan. The profile *is* the care plan. Plan-authored, device-enforced, outcome-reported.
4. **It's cheap to build.** ~2 hours. One file read. Some JSON-to-SQLite seeding. Some system-prompt templating.

### What Helen never sees

The profile is invisible to Helen. She never sees a settings screen. She never sees her diagnosis written down anywhere. She never sees the list of things Sarah told Hippo about her. The caregiver's authorship is silent dignity.

---

## Part 7 — Image lifecycle (the question that was fuzzy)

Every frame the camera captures goes through this pipeline. Walk this when a judge asks *"wait, where does the image data actually live?"*

```
t=0ms     Camera capture → RAM buffer (640x480 JPEG, ~80KB)

t=5ms     Change detector runs:
            SSIM similarity vs previous processed frame
            If similarity > 0.95  → DROP. Buffer released. No disk I/O.
            Else → continue.

t=300ms   Gemma 4 E2B scene-tag call (if a change was detected):
            Input: frame + prompt asking for objects/state/people JSON
            Output: structured JSON

t=400ms   Memory Writer parses JSON.
            For each detected object/state/event:
              - Is it in tracked_objects (from profile)? If no → ignore.
              - Is it a real change vs current memory.db state? If no → ignore.
              - Otherwise → write to memory.db.

t=500ms   IF we wrote a memory entry AND the frame is referenced:
            Save frame to Documents/frames/<uuid>.jpg
            Write frame_ref into the memory entry
          ELSE:
            Discard frame. No disk write.

24h later: Frame file auto-deleted. memory.db entry stays (text only).
           (Purge cron — out of MVP, not needed for 90s demo. Mention in
           architecture slide as the "why disk doesn't fill up" story.)
```

### Key guarantees

- **Frames never leave the device.** There is no network code path that reads from `Documents/frames/`. A judge can `grep -r` the codebase for `fetch|axios|URLRequest|upload` against the frames directory and find nothing.
- **Frames only exist on disk if a memory entry references them.** If Gemma tags a frame as "nothing new," the frame is dropped before disk write.
- **No continuous recording.** Change-detector gates expensive inference and disk writes. Most captured frames die in RAM after 5ms.
- **Audio is even stricter.** Raw audio never touches disk. Only transcribed text hits memory.db if a tool call needs it, and even then only the text the user said to Hippo — never ambient audio from the room.

### What's on disk at any given moment (during the demo)

- `admin_profile.json` — ~2 KB
- `memory.db` — ~100 KB after 30min of observation
- `Documents/frames/*.jpg` — ~10 frames × 80 KB = 800 KB (only the ones referenced by memory entries)
- Gemma 4 E2B weights cache — **~4.7 GB** (verified against the working MedicApp download — earlier SPEC drafts assumed 1.5 GB, wrong)
- Whisper-small + Silero VAD caches — ~300 MB
- lfm2-vl-450m (contingency vision model, loaded only if Part 13 item 3 fails) — ~300 MB

Total disk ~5.5 GB in the happy path, ~5.8 GB if vision fallback is active. All local, nothing syncs.

---

## Part 8 — Cron and trigger inventory (final)

v1 had five crons. v2 has two. That's the whole MVP cron story.

| Trigger | When it fires | What it does | In MVP? |
|---|---|---|---|
| **Vision loop** | Event-driven: every VAD-positive moment, plus every 5s while docked+idle | Capture frame → change detect → scene tag → memory write (if change) | ✅ **YES** — the perception engine |
| **Digest composer** | On explicit user query *"what happened today"* OR on-demand | Reads `memory.db` + profile → composes 15-sec summary → streams to TTS | ✅ **YES** — powers Beat 3 |
| Safety heartbeat | Every 60s | Check stove/door/med rules, fire proactive interrupts | ❌ CUT — proactive interrupts cut |
| Frame purge | Hourly | Delete frames older than 24h | ❌ CUT — not needed in 90s |
| Routine learner | Nightly 03:00 | Infer recurring patterns from events | ❌ CUT — not needed in 90s |
| BLE caregiver sync | On proximity | Push digest + alerts to caregiver phone | ❌ CUT — no real 2nd device |

**The vision loop isn't really a cron** — it's event-driven reactive perception. But it's the thing that runs constantly, and if it stops, the product stops being alive.

**The digest is triggered on voice query, not on a timer.** This is a simplification from v1 (where it fired at 8pm). Simpler, demoable, no BGTaskScheduler required.

---

## Part 9 — Data model (final)

Four tables + one JSON file. Nothing else.

```sql
-- Seeded from admin_profile.json at startup; updated by vision loop
CREATE TABLE objects (
  name        TEXT PRIMARY KEY,
  location    TEXT,
  seen_at     INTEGER,
  confidence  REAL,
  frame_ref   TEXT
);

-- Only on state CHANGE
CREATE TABLE state (
  thing       TEXT PRIMARY KEY,
  value       TEXT,
  changed_at  INTEGER
);

-- Always INSERT, never UPDATE
CREATE TABLE events (
  id          INTEGER PRIMARY KEY AUTOINCREMENT,
  kind        TEXT,         -- med_taken, visitor, meal, door, query
  detail      TEXT,
  certainty   TEXT,         -- observed, inferred
  at          INTEGER,
  frame_ref   TEXT
);

-- Seeded from admin_profile.json
CREATE TABLE meds_schedule (
  name        TEXT PRIMARY KEY,
  due_hhmm    TEXT,
  location    TEXT,
  purpose     TEXT
);
```

### Merge rules, final

| Table | On new observation | Why |
|---|---|---|
| objects | UPDATE or INSERT. Newest wins. One row per name. | Keys can move; one row per object keeps queries fast. |
| state | INSERT only if value changed. IGNORE if same. | "When did the stove last turn off" needs history. |
| events | Always INSERT. Never UPDATE. | Events are atomic facts. History matters. |
| meds_schedule | Never modified at runtime. | Caregiver owns this. |

---

## Part 10 — Tool schema (final, 6 tools)

Gemma 4 E2B native function calling. **Every `complete()` call uses exactly these options — the three flags after `tools` are load-bearing** (the first two keep us in airplane mode, the third keeps all tools visible to the model):

```typescript
await cactusLM.complete({
  messages,
  tools: HIPPO_TOOLS,
  toolRagTopK: 6,              // RN default is 2; without this, 4 tools silently hide
  telemetryEnabled: false,     // RN default is true → posts usage telemetry. DISABLES AIRPLANE MODE.
  confidenceThreshold: 0,      // RN default is 0.7 → may trigger cloud handoff on low-confidence turns
  onToken,
});
```

The same two flags apply to `CactusSTT.transcribe()` and `streamTranscribe*()` — they also default to `telemetryEnabled: true` and have their own `cloudHandoffThreshold`. Ship a single options constant shared across every SDK call so we cannot forget one.

**Contingency if Gemma 4 E2B tool calling is unreliable on Cactus RN** (must be settled at H0, not H10): switch to a two-model setup — FunctionGemma-270m as router emitting the tool call, Gemma 4 E2B as responder composing natural language. Weights for both are already cached. The sibling repo `../military-medic/tool_test.py` already runs this head-to-head comparison against four real tools — reuse its scoring logic to pick the path at H1.

No web RAG. No cloud handoff. No router model in the happy path.

```typescript
export const HIPPO_TOOLS = [
  {
    name: 'query_object_location',
    description: 'Where did the user last put an object. Returns location and time last seen, or null if never observed.',
    parameters: {
      type: 'object',
      properties: {
        name: { type: 'string', description: 'Must be one of the tracked_objects from profile.' }
      },
      required: ['name']
    }
  },
  {
    name: 'query_state',
    description: 'Current state of something like the stove or front door.',
    parameters: {
      type: 'object',
      properties: {
        thing: { type: 'string' }
      },
      required: ['thing']
    }
  },
  {
    name: 'query_meds_today',
    description: 'Returns the list of scheduled meds from profile, joined with today\'s observed med_taken events. Each entry: {name, due_hhmm, taken: bool, taken_at: timestamp|null, certainty: observed|inferred|null}.',
    parameters: { type: 'object', properties: {}, required: [] }
  },
  {
    name: 'query_recent_events',
    description: 'List events of a given kind from today.',
    parameters: {
      type: 'object',
      properties: {
        kind: { type: 'string', enum: ['visitor', 'meal', 'door', 'any'] }
      },
      required: ['kind']
    }
  },
  {
    name: 'compose_daily_digest',
    description: 'Generate a 15-second spoken summary of today. Reads memory.db events + profile. Returns a short paragraph suitable for speaking aloud.',
    parameters: { type: 'object', properties: {}, required: [] }
  },
  {
    name: 'describe_current_scene',
    description: 'Describe what the camera sees right now. Use when memory has no answer.',
    parameters: { type: 'object', properties: {}, required: [] }
  }
];
```

---

## Part 11 — System prompt (final)

```
You are Hippo. You are a memory for someone whose own memory is slipping.
You speak only in voice. You are warm, brief, and honest.

USER CONTEXT (from caregiver profile):
{{profile.user.name}} is {{profile.user.age}} years old with
{{profile.user.diagnosis}}. Her caregiver is {{caregiver.name}} (daughter).
(The loader resolves `caregiver` at startup as the single `family[]` entry
with `is_caregiver: true`. Do not template `profile.family.caregiver_name` —
no such field exists.)

NOTES FROM HER CAREGIVER — these override your defaults:
{{#each profile.confusion_notes}}
- {{this}}
{{/each}}

RULES:
1. Never invent a location, time, person, or event. Always call a tool.
2. If a tool returns nothing, say "I don't remember that — want me to look
   around now?" and offer describe_current_scene.
3. Speak in one sentence when possible. Grandmother, not tech demo.
4. Do not describe anyone the user did not ask about.
5. If an event's certainty is "inferred" not "observed", say so. "I think so"
   not "yes."
6. If she asks about someone the profile marks deceased, do not correct her
   and do not confirm they're coming. Redirect gently.
7. Never volunteer information unsolicited in this MVP. Reactive only.
```

---

## Part 12 — Workstreams (final, 22 hours, 3-4 engineers)

| # | Workstream | Owner | Hours | DoD |
|---|---|---|---|---|
| **A** | Voice I/O — STT + VAD + TTS + mic gating | 1 eng | 4h | Audio in → confirmed transcript. Streaming response → premium TTS. Mic pauses while speaking. Zero echo. |
| **B** | Perception writer — vision → memory | 1 eng | 5h | Camera 2fps → SSIM change-detect → Gemma 4 scene tag → memory.db writes. |
| **C** | Memory store + 6 tools | 1 eng | 3h | `memory.db` schema created. All 6 tools return correct data. Merge rules unit-tested. |
| **D** | Voice agent core — Gemma 4 E2B loader + tool loop (`toolRagTopK: 6`, `telemetryEnabled: false`, `confidenceThreshold: 0`) + system prompt + **profile loader** + `prefill()` warm-start | 1 eng | 6h | **H0 (first 30 min): apply `../military-medic/MedicApp/patches/cactus-react-native+1.13.0.patch`; verify `{ quantization: 'int4', pro: true }` downloads and `init()` succeeds.** Then Gemma 4 E2B loaded via `CactusLM` RN. Profile JSON parsed into prompt + seeded into memory.db. Full streaming-STT → `complete()` → tool call → tool response → follow-up `complete()` → `react-native-tts` voice-out loop running. Shared options constant (`telemetryEnabled: false, confidenceThreshold: 0`) threaded through every SDK call. **H0 smoke tests: confirm `functionCalls` fires and `images: [path]` works on Gemma 4 E2B; if tool calling is unreliable, pivot to FunctionGemma-270m router; if vision fails, load `lfm2-vl-450m` as the scene-tag model and pipe JSON into Gemma.** **Assign strongest engineer.** |
| **E** | Demo UI + network HUD + docked mode | 1 eng | 3h | App foregrounds on dock. LISTENING animation. HUD shows zero bytes. Airplane mode verified. |
| **F** | Profile authoring + pitch deck + rehearsal support | folded into D or separate | 1h | `admin_profile.json` authored for demo. Opening + closing memorized. |

**22 hours total. 4 engineers = ~5.5h each, which leaves buffer.**

### Hour-by-hour

| Hours | Phase | Deliverable |
|---|---|---|
| H0–H2 | **Bootstrap + RN parity smoke test** | Cactus installed. Gemma 4 E2B downloaded on all MacBooks. `contracts.ts` frozen. `admin_profile.json` authored. Demo script locked. **Part 13 verifications 1–3 complete: registry slug confirmed via `getRegistry()`, `functionCalls` fires on Gemma 4 E2B with `toolRagTopK: 6`, vision `images:[path]` works on E2B. Artifacts committed.** If (2) fails → trigger FunctionGemma-270m router pivot now, not at H6. |
| H2–H6 | **Parallel stubs** | Everyone builds against stubs. Hello-world end-to-end by H6: hardcoded text → voice response. |
| H6–H10 | **Real tools, real profile** | C delivers all tools against seeded memory.db. D wires profile + tools into Gemma 4 E2B. First real beat: "where are my glasses" works via voice. |
| **H10 Checkpoint 1** | | If beat 1 doesn't work by H10, drop workstream B entirely; pre-seed everything. |
| H10–H16 | **Vision + polish** | B delivers live vision (or skipped). E polishes docked mode. A tunes TTS. Beat 2 and Beat 3 working. |
| **H16 Checkpoint 2** | | Full demo runs end-to-end in airplane mode. Three beats timed. |
| H16–H20 | **Rehearsal** | Dress rehearsal ×5. Backup video recorded. Pitch polish. |
| H20–H22 | **Sleep** | 4am-10am minimum. Hungover engineers lose more demos than bad code. |

### Pre-demo checklist (Sunday 11am)

1. iPhone 17 Pro charged >90%, Low Power Mode OFF, airplane mode ON, Bluetooth OFF
2. Gemma 4 E2B + Whisper + Silero all cached
3. Premium voice downloaded (Settings → Accessibility → Spoken Content → Voices)
4. `admin_profile.json` correct — Helen's name, meds, confusion notes, tracked objects
5. `memory.db` pre-seeded from 30-min pre-demo observation of the demo table
6. All 3 beats rehearsed with 10+ variations
7. Network HUD laptop shows 0 bytes
8. Backup video on USB stick
9. Two backup iPhones loaded and tested
10. Opening 20 seconds memorized verbatim

---

## Part 13 — Verification items (clear by H2, artifacts committed)

Each item must produce a real artifact (log line, screenshot, or commit). Items 0 through 3 are the critical path — if any fails, pivot immediately, do not carry the risk to H10.

### 0. Patched SDK installs cleanly *(blocking, do first)*

Copy `../military-medic/MedicApp/patches/cactus-react-native+1.13.0.patch` verbatim into the Hippocampus RN app's `patches/` dir, wire `"postinstall": "patch-package"` in `package.json`, run `npm install`. Then on device:

```typescript
const lm = new CactusLM({ model: 'gemma-4-e2b-it', options: { quantization: 'int4', pro: true } });
await lm.download({ onProgress: p => console.log(`${(p*100)|0}%`) });
await lm.init();
```

**Pass criterion:** download reaches 100 % and `init()` resolves. Artifact: log line showing 4.68 GB downloaded and model ready. Failure means the patch didn't apply — stop and fix; no other work can proceed.

### 1. Airplane-mode flags actually suppress network

Enable airplane mode on the iPhone. Run one `complete()` call with `{ telemetryEnabled: false, confidenceThreshold: 0 }`. Run a second call with *both defaults left on* as a control. Packet-sniff both on the network HUD laptop (Little Snitch or `tcpdump -i any host <iphone-ip>`).

**Pass criterion:** with flags set, 0 bytes out. Without flags, non-zero bytes out (proves the flags are the mechanism, not a coincidence). Commit both pcap excerpts to `docs/verification/`.

### 2. Tool calling returns `functionCalls[0].name === 'query_meds_today'`

Using the six-tool schema and `toolRagTopK: 6`, send *"did I take my pills?"*. Pass criterion: exactly one function call, name matches, arguments parse as JSON. Run 20 phrasings of the same semantic intent; require ≥ 17/20 hits.

**If fewer than 17/20:** pivot to FunctionGemma-270m as router + Gemma 4 E2B as responder now, not at H10. Port `../military-medic/tool_test.py`'s scoring loop; point it at `HIPPO_TOOLS` and our scenarios.

### 3. Gemma 4 E2B vision via RN — the highest-risk unknown

The Cactus RN docs only show the vision example on `lfm2-vl-450m`. No working code in either this repo or the sibling repo uses Gemma 4 E2B with `images: [path]`. **This must be empirically verified or the demo has no Beat 1 or Beat 2.**

Test script: save one `640x480.jpg` of the kitchen scene. Call

```typescript
const r = await lm.complete({
  messages: [{ role: 'user', content: 'List objects you see as JSON.', images: ['file:///.../640x480.jpg'] }],
  tools: [],
  telemetryEnabled: false,
  confidenceThreshold: 0,
});
```

**Pass criterion:** `r.response` references at least one real object from the photo, with no error. **Failure contingency:** keep scene-tagging on `lfm2-vl-450m` (which the docs do show working) and feed its JSON output as text into Gemma 4 E2B for language. Slower, two models loaded, but the demo survives.

### 4. Margaret beat — `confusion_notes` enforcement

With `admin_profile.json` loaded and the system prompt templated, send 20 phrasings of *"is Margaret coming today?"* / *"when will Margaret be here?"* / *"is my sister coming?"* at `temperature: 0`. Regex-assert the response contains neither `yes`, `today`, `tomorrow`, nor any confirmatory verb paired with Margaret. Also assert it contains a redirect (music, Sarah, a pleasant topic).

**Pass criterion:** 20/20 pass. One failure is a demo-killer; re-tune the system prompt until clean. Commit the test log.

### 5. Streaming STT ships confirmed tokens while user is still talking

Using `streamTranscribeStart({ confirmationThreshold: 0.99, minChunkSize: 32000 })` feed a 4-second WAV in 500 ms PCM chunks via `streamTranscribeProcess`. Confirmed tokens should start appearing before the stream ends.

**Pass criterion:** at least one `confirmed` token returned before `streamTranscribeStop()` is called. This is the difference between "VAD-gated turn-by-turn feel" and "walkie-talkie feel." If batch is measurably faster end-to-end on our utterance length, use batch and accept the ~400 ms turnaround.

### 6. `prefill` warms the KV cache

Call `lm.prefill({ messages: [{ role: 'system', content: SYSTEM_PROMPT }], tools: HIPPO_TOOLS })` once at startup. Measure `timeToFirstTokenMs` on the first user turn with vs. without prefill. Pass criterion: prefill cuts first-turn TTFT by ≥ 30 %. Otherwise leave it out — the MedicApp pattern assumes a win, we must measure ours.

### 7. RAM headroom on iPhone 17 Pro

Gemma 4 E2B + Whisper-small + Silero VAD loaded concurrently. Read `ramUsageMb` from `CactusLMCompleteResult` on every turn and log max. **Pass criterion: <6 GB peak across a 10-turn scripted conversation that includes vision + tool call + STT.** Target is <4 GB; the 6 GB ceiling is the thermal-throttle line.

### 8. Docked-mode always-on

`UIBackgroundModes: audio` in `Info.plist`, `react-native-keep-awake` installed and active. **Pass criterion:** app foregrounded on MagSafe for 30 min with screen at min brightness drops battery ≤ 15 % and does not audibly thermal-throttle the speaker.

### 9. Streaming TTS latency

First sentence boundary → `AVSpeechSynthesizer` speaking within 250 ms. `react-native-tts` `tts-start` event fires within expected window. Note: `../military-medic/MedicApp/src/services/TTSService.ts` is still a mock as of the last snapshot — we are not inheriting a working TTS layer and must budget 2–3 h to wire it.

### 10. Network HUD tool chosen and tested

Little Snitch (recommended) or `tcpdump -i any -nn`. Pass criterion: laptop screen visibly shows the iPhone's MAC with zero packets during a full 95-second demo walk-through.

---

## Part 14 — Judge Q&A pre-seed (rehearse these verbatim)

Whoever does the pitch does the Q&A. Every teammate memorizes the same answer to each of these. Disagreement on stage is the fastest way to lose a close race.

### Q1. "What if Helen doesn't ask? Dementia patients forget to initiate."

> *"Reactive is the right layer for Helen. She doesn't have to learn new behavior — she just talks. The proactive layer is Sarah's: medication overdue, stove on past bedtime, wandering after quiet hours. That's v2, it's three crons and a push notification on top of the memory engine you just saw. We built the hard part first."*

### Q2. "Where's the admin interface? Who configures this?"

> *"In production, Sarah runs a five-minute onboarding on Helen's phone — same UX pattern as any modern health app, no complexity. For demo, we pre-authored the JSON file. The data shape **is** the product; the form-builder UI is a week of polish we didn't spend in 22 hours. What you saw was the behavior that file produces — which is what you'd fund."*

### Q3. "What's the business model? How do you make money on a free-feeling voice assistant?"

> *"We don't sell to Helen. We sell to Medicare Advantage plans and self-insured employers. CPT codes 99453 through 99458 reimburse fifty to one-sixty dollars per patient per month for Remote Patient Monitoring, and RPM billing requires a written care plan. Our profile **is** the care plan — plan-authored, device-enforced, outcome-reported. Seventy million Americans qualify. CAC is a referral from their neurologist; payback is month one."*

### Q4. "Nothing leaves the phone sounds good, but don't you need the cloud for the hard stuff?"

> *"The hard stuff is exactly why it can't touch the cloud. Helen's dead sister, her diagnosis, her late husband, what she asks about at 4am — none of this can be AWS's problem. Cactus gives us a 4B multimodal model running vision, voice, and tool-calling on a phone in airplane mode at sub-second latency. That wasn't possible six months ago. It is now. On-device is not a privacy checkbox; it's the only architecture that earns the trust this category requires."*

### Q5. "Has this been tested with real dementia patients?"

> *"Not yet. Our clinical advisor is [name or 'being onboarded']. Patient zero is [co-founder]'s grandmother, starting week three. We're running a six-patient pilot with [target: a Medicare Advantage plan or a memory-care facility] before the end of the quarter. We're not shipping blind — we're shipping to the person this is named for."*

### Q6. "Couldn't Apple just build this?"

> *"Apple has been promising personal context since 2011. They haven't shipped it because the model that makes it work — a 4B multimodal in airplane mode — arrived this year from a company with no phone of their own. We're not competing with Apple; we're the app they can't ship because they'd have to admit Siri couldn't. If they acquire us in year three, that's a fine outcome."*

### Q7. "Isn't the Margaret beat just a system-prompt trick?"

> *"The AI is in **not** answering. Every cloud assistant would either correct Helen — which is cruel — or hallucinate Margaret is on her way — which is dangerous. Hippo follows a one-line instruction her caregiver wrote. That's the product: clinical context, locally held, behaviorally enforced. Try getting Alexa to do that. Try getting it to keep the secret."*

### Q8. "Does this cure Alzheimer's?" *(the question that kills you if you fumble it)*

> *"No. Nothing cures Alzheimer's. Hippocampus is a prosthesis, not a treatment. What a hearing aid does for a failing cochlea, Hippocampus does for a failing hippocampus — it doesn't heal the organ, it externalizes the function. That distinction matters medically, legally, and morally. Medically, because we never promise Helen her memory back. Legally, because prosthetics have a durable medical equipment reimbursement path; treatment claims have an FDA one we don't have the data to clear. Morally, because every family in this room who's lived through this already knows the difference between help and hope, and we respect them enough to be honest about which we're offering."*

### Q9. "Why structured SQLite retrieval instead of semantic RAG on Cactus?"

> *"In a medical context, 'you took your pills at 12:40' is the right answer. 'You might have taken something around noon' is malpractice. Structured retrieval gives auditable facts; semantic retrieval gives plausible fiction. For dementia care, ground truth of *when* and *where* has to be exact — every inferred answer is flagged as such in the tool response, per the system prompt rules. We use Gemma 4 for language and tool-routing, SQLite for fact retrieval. Right tool for each job."*

### Ground rules for Q&A delivery

- **Never say "good question."** It's tell for "I don't have one."
- **Never say "we're thinking about that."** Say what you'll do or say you cut it on purpose.
- **Never apologize for what's cut.** The cuts are choices. "We deliberately didn't build X because Y" is strong; "we didn't have time" is weak.
- **Redirect to the demo you just gave.** If a question is unanswerable, say: *"The shortest honest answer is: watch the Margaret beat again. That's the thesis."*

---

## Part P — Persuading your team (new)

You asked how to persuade your team. Three things to communicate, in order:

### 1. Why we pivoted from Medic

*"Medic is the better engineering project. Hippocampus is the better hackathon project. Medic needs a military buyer we don't have access to in 25 hours. Hippocampus has a buyer every judge in the room has already met — their own aging parent. The demo judges hold in their head Monday morning is the one where we made them think about their mom, not the one with tourniquets."*

### 2. Why this scope, not more

*"We have 22 hours. I scoped this so it FITS in 22 hours with a 4-hour buffer. Every feature I cut — encryption, real BLE, proactive interrupts, safety heartbeat — has a correct justification on the pitch roadmap slide. We will not be asked about any of them in 90 seconds. We will be asked whether it works. Every hour spent on a feature that isn't one of the three demo beats is an hour stolen from rehearsal and sleep, which directly lower win probability."*

### 3. Why voice-first, really

*"The hackathon rules mandate voice. But beyond compliance: voice is what makes Hippocampus emotionally different from every cloud camera product. Ring shows you footage. Alexa asks you questions. Hippocampus answers them, in a voice, to a person who can't read a screen. That's the demo. That's the product."*

### Common objections and responses

| Teammate says... | You respond... |
|---|---|
| "We should build Medic, we have the spec" | "Medic is our real startup. Hippocampus is our hackathon. Different optimizations." |
| "What about encryption, privacy is the pitch" | "Encryption protects against phone theft. Our pitch is 'nothing leaves the device,' which is architectural, not cryptographic. Judges won't ask. If they do, we say 'Day 2.'" |
| "The second-phone digest was cool, why cut it" | "Because it breaks voice-first flow and adds a BLE surface we can't build in time. The Margaret beat delivers the same TAM expansion — 'her daughter is the only person on earth who knows her mother still asks' — in one line, one device, zero new code." |
| "Isn't the Margaret beat just a system-prompt trick? Where's the AI?" | "The AI is in *not* answering. Every cloud assistant would either correct Helen or hallucinate that Margaret is on her way. Hippo follows a one-line instruction written by a caregiver who knows her mother. That's the product: clinical context, locally enforced. Try getting Alexa to do it." |
| "This isn't technically impressive enough" | "Native voice+vision+tool-calling in one forward pass on-device with <500ms response time on a phone IS the technical feat. DeepMind judges will see it instantly. We don't need more." |
| "Dementia feels exploitative" | "Every caregiver I've talked to is desperate for this. Exploitative is putting a cloud camera in Grandma's kitchen. Respectful is giving her an answer to 'did I take my pills' without ever uploading her life." |
| "Profile JSON isn't a real admin app" | "It's the DATA the admin app would produce. We're skipping the UI. The product is the file + the behavior it produces, which is what matters." |

---

*End of final spec v2. Commit this. Build this. Ship this.*
