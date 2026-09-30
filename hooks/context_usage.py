"""Shared helpers: read the last main-thread API usage from a Claude Code transcript."""
import json
import os
from datetime import datetime, timezone

from context_constants import TAIL_BYTES


def last_usage(transcript_path):
    """Return (context_tokens, timestamp, ttl_minutes) of the last main-thread assistant turn, or None."""
    if not transcript_path or not os.path.exists(transcript_path):
        return None
    with open(transcript_path, "rb") as f:
        f.seek(0, os.SEEK_END)
        size = f.tell()
        f.seek(max(0, size - TAIL_BYTES))
        lines = f.read().decode("utf-8", errors="ignore").splitlines()
    for line in reversed(lines):
        if '"usage"' not in line:
            continue
        try:
            d = json.loads(line)
        except ValueError:
            continue
        m = d.get("message")
        if d.get("isSidechain") or not isinstance(m, dict) or "usage" not in m or m.get("model") == "<synthetic>":
            continue
        u = m["usage"]
        ctx = (u.get("input_tokens") or 0) + (u.get("cache_read_input_tokens") or 0) + (u.get("cache_creation_input_tokens") or 0)
        cc = u.get("cache_creation") or {}
        ttl = 60 if (cc.get("ephemeral_1h_input_tokens") or 0) > 0 else 5
        ts = d.get("timestamp")
        t = datetime.fromisoformat(ts.replace("Z", "+00:00")) if ts else None
        return ctx, t, ttl
    return None


def minutes_since(t):
    return (datetime.now(timezone.utc) - t).total_seconds() / 60 if t else 0.0


def fmt_idle(minutes):
    if minutes >= 1440:
        return f"{minutes / 1440:.1f} days"
    if minutes >= 60:
        return f"{minutes / 60:.1f} h"
    return f"{minutes:.0f} min"


def fmt_k(tokens):
    return f"{tokens / 1000:.0f}K"
