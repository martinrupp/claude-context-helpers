#!/usr/bin/env python3
"""UserPromptSubmit hook: warn on large context, and stop once before rewriting an expired cache.

- Context >= WARN_AT: show a warning, prompt goes through.
- Cache expired and context >= EXPIRED_AT: block the prompt once. Resubmitting
  within RESUBMIT_WINDOW_S sends it anyway (or run /clear first).
"""
import json
import os
import sys
import tempfile
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from context_constants import (  # noqa: E402
    CACHE_READ_PRICE, CACHE_WRITE_1H_PRICE, CACHE_WRITE_5M_PRICE, EXPIRED_AT, RESUBMIT_WINDOW_S, WARN_AT,
)
from context_usage import fmt_idle, fmt_k, last_usage, minutes_since  # noqa: E402

data = json.load(sys.stdin)
usage = last_usage(data.get("transcript_path"))
if not usage:
    sys.exit(0)
ctx, t, ttl = usage
idle = minutes_since(t)

if idle >= ttl and ctx >= EXPIRED_AT:
    marker = os.path.join(tempfile.gettempdir(), f"claude-ctx-warn-{data.get('session_id', 'x')}")
    if os.path.exists(marker) and time.time() - os.path.getmtime(marker) < RESUBMIT_WINDOW_S:
        os.remove(marker)
        sys.exit(0)
    open(marker, "w").close()
    rewrite = ctx * (CACHE_WRITE_1H_PRICE if ttl == 60 else CACHE_WRITE_5M_PRICE) / 1e6
    print(json.dumps({
        "decision": "block",
        "reason": (
            f"Idle {fmt_idle(idle)}, the {ttl}-min prompt cache has expired. Sending now rewrites "
            f"{fmt_k(ctx)} tokens (~${rewrite:.2f}). New task? /clear first. "
            f"Otherwise resubmit (up arrow) within {RESUBMIT_WINDOW_S // 60} min to send anyway."
        ),
    }))
    sys.exit(0)

if ctx >= WARN_AT:
    print(json.dumps({
        "systemMessage": (
            f"Context {fmt_k(ctx)}, ~${ctx * CACHE_READ_PRICE / 1e6:.2f} per API call. "
            "If this is a new task, consider /clear (or /compact)."
        ),
    }))
