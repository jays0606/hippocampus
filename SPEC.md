# Hippocampus — Hackathon Final Spec (v2)

*Voice-first on-device memory for people whose own is slipping.*

**Event**: Gemma 4 Voice Agents Hackathon · YC HQ · Apr 18–19, 2026
**Submission**: Sun 11am · **Demo**: 1pm judging · 90 seconds on stage
**Stack**: iPhone 17 Pro · Gemma 4 E2B · Cactus SDK (React Native) · No cloud
**Team**: 3–4 engineers · ~22 working hours to submission

**v2 changes from v1:**
- Added caregiver-authored profile (§6) — meds, symptoms, doctors, family, triggers
- Clarified image lifecycle and when disk writes happen (§7)
- Reduced cron list to the two that run in MVP (§8)
- Revised Beat 3 to a single-device voice-only digest (§3)
- Added team-alignment section for persuading co-founders (§P at end)

---

## Part 1 — The pitch (what you say on stage)

### The opening (15 seconds, no slides)

Founder walks on stage. No smile. Holds up an iPhone.

> *"My grandmother asks my mother 'did I take my pills?' six times every day. My mother answers six times every day. By dinner, neither of them remembers the conversation.*
>
> *Fifteen million Americans live this loop."*

Pause. Slide: **Hippocampus.**

> *"Named after the part of the brain that fails first in Alzheimer's. We built the digital version. It runs on her phone. It never touches the cloud. Watch."*

---

## Part 2 — The demo arc, 60 seconds, three beats

### Staging (done 30 minutes before judging)

- iPhone 17 Pro on MagSafe dock, camera facing a small "kitchen" scene on a table: coffee mug, pill bottle, keys on a napkin, reading glasses, a plant.
- Airplane mode on. Network monitor visible on laptop next to dock, showing 0 bytes.
- App running. The vision loop has been observing the table for 30 min. `memory.db` contains real entries: *mug placed 12:15, keys placed 12:33, pill_bottle tipped+drunk 12:40 (event: kind=med_taken, certainty=observed), glasses placed 1:02.*
- Caregiver profile file loaded at app launch — *"Helen, 79, mid-stage Alzheimer's, takes Donepezil 10mg at 8am, daughter Sarah, late sister Margaret (do not confuse)."*

### Beat 1 — Spatial recall (20s)

Founder picks up the glasses, walks two steps, sets them on a chair behind him. Walks back. Doesn't touch the phone.

> *"Hey Hippo — where are my glasses?"*

Sub-second. Hippo's premium voice:

> *"On the chair behind you. You set them there eight seconds ago."*

Room reacts. Founder hasn't touched the screen.

### Beat 2 — The meds moment (20s)

Founder turns to face the room, hands at his sides.

> *"Hey Hippo — did I take my pills?"*

> *"Yes Helen. At 12:40. I watched."*

One-second silence. Then:

> *"This is the answer my grandmother needs six times a day. Not an alarm. Not a reminder. An answer — from someone who was watching."*

### Beat 3 — The digest and the family bridge (20s)

Founder to the room:

> *"Hey Hippo — what happened today?"*

Hippo speaks a 15-second summary:

> *"Today you took your morning pills at 12:40. You asked about your glasses twice. You've been calm. No visitors. Nothing left on the stove."*

Founder to audience:

> *"This is the digest her daughter hears from me every evening. No video. No transcript of what Mom said. Just the facts. The peace of mind goes to her daughter. Mom's life stays with Mom."*

Founder gestures to the network HUD on the laptop.

> *"Everything you just heard ran in airplane mode. Gemma 4 on Cactus. On-device. Zero bytes out. Not because we chose privacy as a feature — because we built the architecture that makes every other choice impossible."*

### Why Beat 3 is single-device now (diff from v1)

v1 had a second phone showing a notification. v2 has Hippo speaking the digest directly. Reasons:
- Voice-first throughout (no screen touches, no phone pickups)
- One device = cleaner narrative in judges' minds
- Removes the BLE/fake-sync surface entirely — less to defend under questioning
- Pitch line carries the TAM expansion: *"this is what her daughter hears every evening"* — implies two-device system without having to prove it on stage

### Close (15s)

> *"Microsoft tried to ship a memory layer last year. They called it Recall. They killed it twice because they built it in the cloud. We built it where a memory belongs — on the device in her pocket.*
>
> *Seventy million Americans live with some form of memory impairment. Their families spend two hundred sixty billion dollars a year trying to help. Nothing today actually remembers for them. We do.*
>
> *Hippocampus. Thank you."*

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
- Network HUD on demo laptop
- Spoken digest (generated from `memory.db` + profile, voice only)

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
2. `describe_current_scene` tool → cut (saves 1h)
3. `forget_last_minutes` tool → stub (saves 30m)

### Do not cut under any circumstance

- Voice I/O pipeline
- `memory.db` + four query tools
- Caregiver profile loader
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
- Gemma 4 E2B weights cache — ~1.5 GB
- Whisper / Silero cache — ~200 MB

Total disk ~2 GB, all local, nothing syncs.

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

Gemma 4 E2B native function calling via `CactusLM.complete({ messages, tools, toolRagTopK: 6 })`.

**`toolRagTopK: 6` is load-bearing** — the RN SDK default is 2, which picks the two embedding-closest tools and silently hides the rest. Without this override, `query_meds_today` can vanish from the tool list on a prompt the embedding happens to score lower. Pass all six every turn.

**Contingency if Gemma 4 E2B tool calling is unreliable on Cactus RN** (to be verified at H0): switch to a two-model setup — FunctionGemma-270m as router emitting the tool call, Gemma 4 E2B as responder composing natural language. Weights for both are already cached. Do not discover this at H10.

No web RAG. No router model in the happy path.

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
| **D** | Voice agent core — Gemma 4 E2B loader + tool loop (`toolRagTopK: 6`) + system prompt + **profile loader** | 1 eng | 6h | Gemma 4 E2B loaded via `CactusLM` RN. Profile JSON parsed into prompt + seeded into memory.db. Full STT → `complete()` → tool call → tool response → follow-up `complete()` → `react-native-tts` voice-out loop running. **H0 smoke test: confirm `functionCalls` fires and `images` works on Gemma 4 E2B; if tool calling is unreliable, pivot to FunctionGemma-270m router.** **Assign strongest engineer.** |
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

## Part 13 — Verification items (clear by H2)

Each item must produce a real artifact (log line, screenshot, or commit) before H2 closes.

1. **Cactus RN model slug for Gemma 4 E2B.** `await getRegistry()` on device; confirm exact slug (likely `gemma-4-e2b-it`). HF weights are cached at `models--Cactus-Compute--gemma-4-E2B-it`, so the Cactus-packaged build exists — we just need the registry key.
2. **Tool calling returns `functionCalls` on Gemma 4 E2B.** One `CactusLM.complete({ messages, tools: HIPPO_TOOLS, toolRagTopK: 6 })` call where the message is *"did I take my pills?"* must produce `functionCalls[0].name === 'query_meds_today'`. If it doesn't, pivot to FunctionGemma-270m router (weights already cached) before H6.
3. **Vision on Gemma 4 E2B.** `complete({ messages: [{ role: 'user', content: 'list objects', images: [jpg] }] })` must return a non-empty response. RN docs show the vision example using `lfm2-vl-450m`; confirm E2B also accepts `images`. If not, keep scene-tagging on a small vision model and pipe JSON into Gemma.
4. **Audio-in to Gemma 4 E2B in a single call** — *deleted as MVP goal.* RN's `CactusLMMessage` exposes only `role`, `content`, `images`. We ship STT → text → LM. Drop any pitch line implying "Gemma hears directly."
5. **RAM headroom on iPhone 17 Pro** — Gemma 4 E2B + Whisper-small + Silero VAD loaded concurrently. Target <6 GB peak on the 12 GB device. Read `ramUsageMb` from `CactusLMCompleteResult` as cheap continuous evidence.
6. **Docked-mode always-on** — `UIBackgroundModes: audio` in Info.plist. Verify battery drain <15% over 30 min with screen on at min brightness.
7. **Streaming TTS latency** — token → `AVSpeechSynthesizer` speaking within 250ms of first sentence boundary. `react-native-tts` `tts-start` fires within expected window.

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
| "The second-phone digest was cool, why cut it" | "Because it breaks voice-first flow and adds a BLE surface we can't build in time. Voice-only digest delivers the same TAM expansion in one device." |
| "This isn't technically impressive enough" | "Native voice+vision+tool-calling in one forward pass on-device with <500ms response time on a phone IS the technical feat. DeepMind judges will see it instantly. We don't need more." |
| "Dementia feels exploitative" | "Every caregiver I've talked to is desperate for this. Exploitative is putting a cloud camera in Grandma's kitchen. Respectful is giving her an answer to 'did I take my pills' without ever uploading her life." |
| "Profile JSON isn't a real admin app" | "It's the DATA the admin app would produce. We're skipping the UI. The product is the file + the behavior it produces, which is what matters." |

---

*End of final spec v2. Commit this. Build this. Ship this.*
