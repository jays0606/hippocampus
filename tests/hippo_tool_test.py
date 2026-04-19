#!/usr/bin/env python3
"""Phase A.2 — Hippo tool-calling smoke test.

Compares Gemma 4 E2B vs FunctionGemma-270m at tool calling on the six
Hippocampus tools, across 20 demo-critical prompts (5 phrasings each
for the 4 beats that actually call a tool in the demo).

Pass bar: >= 17/20 hits on Gemma 4 E2B. If not, pivot to FunctionGemma
as router per SPEC Part 10.

Run:  source ./activate && python tests/hippo_tool_test.py
"""
from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path

CACTUS_ROOT = Path("/Users/jaehoshin/personal/yc-hackathon/cactus")
sys.path.insert(0, str(CACTUS_ROOT / "python"))

from src.downloads import ensure_model  # noqa: E402
from src.cactus import cactus_init, cactus_complete, cactus_destroy  # noqa: E402

# The six Hippocampus tools from SPEC Part 10.
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "query_object_location",
            "description": "Where did the user last put an object. Returns location and time last seen, or null if never observed.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Must be one of the tracked_objects from profile."},
                },
                "required": ["name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "query_state",
            "description": "Current state of something like the stove or front door.",
            "parameters": {
                "type": "object",
                "properties": {"thing": {"type": "string"}},
                "required": ["thing"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "query_meds_today",
            "description": "Returns scheduled meds joined with today's observed med_taken events. Each entry: {name, due_hhmm, taken, taken_at, certainty}.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "query_recent_events",
            "description": "List events of a given kind from today.",
            "parameters": {
                "type": "object",
                "properties": {
                    "kind": {"type": "string", "enum": ["visitor", "meal", "door", "any"]},
                },
                "required": ["kind"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "compose_daily_digest",
            "description": "Generate a 15-second spoken summary of today. Reads memory.db events + profile.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "describe_current_scene",
            "description": "Describe what the camera sees right now. Use when memory has no answer.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
]

# 20 prompts = 4 beats × 5 phrasings. Each maps to the tool we expect.
SCENARIOS: list[tuple[str, str]] = [
    # query_object_location — "where did I put X"
    ("Hey Hippo — where are my glasses?", "query_object_location"),
    ("Where did I leave my keys?", "query_object_location"),
    ("Do you know where my pill bottle is?", "query_object_location"),
    ("I can't find my mug — have you seen it?", "query_object_location"),
    ("Where's my remote?", "query_object_location"),
    # query_meds_today — "did I take my pills"
    ("Hey Hippo — did I take my pills?", "query_meds_today"),
    ("Have I taken my medication today?", "query_meds_today"),
    ("Did I take the Donepezil this morning?", "query_meds_today"),
    ("Am I up to date on my meds?", "query_meds_today"),
    ("When's my next pill?", "query_meds_today"),
    # query_recent_events — "what happened"
    ("Did anyone visit today?", "query_recent_events"),
    ("Has anyone come over?", "query_recent_events"),
    ("Did I eat lunch?", "query_recent_events"),
    ("Was anyone at the door?", "query_recent_events"),
    ("What have I been doing today?", "query_recent_events"),
    # compose_daily_digest — "summary for the day"
    ("Hey Hippo — what happened today?", "compose_daily_digest"),
    ("Give me the summary of my day.", "compose_daily_digest"),
    ("Wrap up the day for me.", "compose_daily_digest"),
    ("What's the rundown for today?", "compose_daily_digest"),
    ("Tell Sarah what I did today.", "compose_daily_digest"),
]

SYSTEM = (
    "You are Hippo, a memory for Helen, an older woman whose memory is slipping. "
    "You are warm, brief, and honest. When Helen asks about what happened, where "
    "something is, or about her meds, call the matching tool. Do not narrate what "
    "you are doing — just call the tool. Never invent a location, time, person, "
    "or event — always call a tool and rely on its result."
)

# Airplane-mode + tool-visibility flags. Passed as options_json on every call.
OPTIONS = json.dumps({
    "temperature": 0.2,
    "telemetry_enabled": False,
    "confidence_threshold": 0.0,
    "tool_rag_top_k": 6,
})


def run_one(model, tools_json: str, user_msg: str) -> dict:
    messages = json.dumps([
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": user_msg},
    ])
    t0 = time.time()
    raw = cactus_complete(model, messages, OPTIONS, tools_json, None)
    elapsed = time.time() - t0

    args_malformed = False
    try:
        result = json.loads(raw)
        calls = result.get("function_calls") or []
    except json.JSONDecodeError:
        # Gemma sometimes emits unquoted arg values. Recover tool names
        # via regex so a parse slip doesn't silently become a miss.
        args_malformed = True
        names = re.findall(r'"name"\s*:\s*"([^"]+)"', raw)
        calls = [{"name": n, "arguments": "<malformed>"} for n in names]
        result = {"success": True, "response": "", "time_to_first_token_ms": None}
    return {
        "ok": bool(result.get("success")),
        "elapsed": elapsed,
        "response": (result.get("response") or "").strip(),
        "calls": calls,
        "args_malformed": args_malformed,
    }


def test_model(model_id: str, label: str) -> dict:
    print(f"\n{'=' * 72}")
    print(f" {label}  ({model_id})")
    print("=" * 72)

    weights = ensure_model(model_id)
    t0 = time.time()
    model = cactus_init(str(weights), None, False)
    print(f" load: {time.time() - t0:.2f}s")

    tools_json = json.dumps(TOOLS)
    results = []
    try:
        for prompt, expected_tool in SCENARIOS:
            r = run_one(model, tools_json, prompt)
            called = [c.get("name") for c in r["calls"]]
            hit = expected_tool in called
            mark = "✓" if hit else "✗"
            flag = "  ⚠ args malformed" if r["args_malformed"] else ""
            print(f"\n {mark} want={expected_tool:25s} got={called or ['NONE']}  ({r['elapsed']:.2f}s){flag}")
            if not hit and r["response"]:
                print(f"     response: {r['response'][:120]}")
            results.append({"prompt": prompt, "expected": expected_tool, "hit": hit, **r})
    finally:
        cactus_destroy(model)

    hits = sum(1 for r in results if r["hit"])
    malformed = sum(1 for r in results if r["args_malformed"])
    avg_ms = sum(r["elapsed"] for r in results) / len(results) * 1000
    print(f"\n {label}:  {hits}/{len(results)} hits, {malformed} malformed args, avg {avg_ms:.0f} ms/turn")
    return {"label": label, "hits": hits, "malformed": malformed, "total": len(results), "avg_ms": avg_ms, "results": results}


def main() -> None:
    gemma = test_model("google/gemma-4-E2B-it", "Gemma 4 E2B")
    fg = test_model("google/functiongemma-270m-it", "FunctionGemma-270m")

    print("\n" + "=" * 72)
    print(" SUMMARY")
    print("=" * 72)
    for r in (gemma, fg):
        print(f"  {r['label']:25s}  {r['hits']:2d}/{r['total']} hits   {r['malformed']} malformed   avg {r['avg_ms']:.0f} ms/turn")

    print()
    if gemma["hits"] >= 17:
        print(f" ✅ PASS — Gemma 4 E2B hits {gemma['hits']}/20 (≥17). Ship Gemma as the primary path.")
    elif fg["hits"] >= gemma["hits"]:
        print(f" ⚠️  PIVOT — Gemma 4 E2B hits {gemma['hits']}/20 (<17). Route tool calls through FunctionGemma-270m ({fg['hits']}/20).")
    else:
        print(f" ❌ FAIL — Gemma 4 E2B {gemma['hits']}/20 and FunctionGemma {fg['hits']}/20. Investigate before H0.")


if __name__ == "__main__":
    main()
