#!/usr/bin/env python3
"""Status line: model | context size (colored) | per-turn cost | session cost."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from context_constants import CACHE_READ_PRICE, DIM, GREEN, RED, RED_AT, RESET, YELLOW, YELLOW_AT  # noqa: E402
from context_usage import fmt_k, last_usage  # noqa: E402

data = json.load(sys.stdin)
parts = [(data.get("model") or {}).get("display_name") or "?"]

usage = last_usage(data.get("transcript_path"))
if usage:
    ctx = usage[0]
    color = GREEN if ctx < YELLOW_AT else YELLOW if ctx < RED_AT else RED
    parts.append(f"{color}ctx {fmt_k(ctx)}{RESET}")
    parts.append(f"{DIM}~${ctx * CACHE_READ_PRICE / 1e6:.2f}/turn{RESET}")
else:
    parts.append(f"{GREEN}ctx 0K{RESET}")

cost = (data.get("cost") or {}).get("total_cost_usd")
if cost is not None:
    parts.append(f"session ${cost:.2f}")

print(" | ".join(parts))
