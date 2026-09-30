# claude-context-helpers

Small Python scripts for Claude Code that show how big your context is and what it costs, so you notice when it's time to `/clear` or `/compact`.

They read the session transcript (the JSONL file at `transcript_path`) and take the token usage from the last main-thread assistant turn: `input_tokens + cache_read_input_tokens + cache_creation_input_tokens`. Sidechain (subagent) and synthetic turns are skipped. Only the last 4 MB of the transcript are read, so this stays fast on long sessions.

They only use the Python standard library and need Python 3.7+.

## Files

| File | Role |
| --- | --- |
| `context_constants.py` | All tunable constants: thresholds, prices, colors. |
| `context_usage.py` | Shared helpers: `last_usage()` and formatting. Nothing is configured to call it directly. |
| `statusline.py` | Status line command. |
| `context_warn.py` | `UserPromptSubmit` hook. |

### `statusline.py`

Prints one line:

```
Opus 5.5 | ctx 182K | ~$0.09/turn | session $4.12
```

- **ctx**: current context size. Green below 150K, yellow below 300K, red from 300K (`YELLOW_AT`, `RED_AT`).
- **/turn**: rough cost to resend the context once as a cache read.
- **session**: `cost.total_cost_usd` as reported by Claude Code.

### `context_warn.py`

Runs before each prompt is sent:

- **Context ≥ 200K** (`WARN_AT`): shows a warning with the per-call cost and suggests `/clear` or `/compact`. The prompt is still sent.
- **Prompt cache expired and context ≥ 100K** (`EXPIRED_AT`): blocks the prompt once and shows how long you were idle and roughly what rewriting the cache would cost. If you resubmit (up arrow, Enter) within 3 minutes (`RESUBMIT_WINDOW_S`), it goes through. Or run `/clear` first.

The cache TTL is taken from the last turn: 60 minutes if it wrote 1-hour cache tokens, otherwise 5 minutes. The "blocked once" state is a marker file per session in the system temp dir (`claude-ctx-warn-<session_id>`).

## Setup

Add this to `~/.claude/settings.json` (or a project's `.claude/settings.json`), replacing the path with wherever you cloned this repo:

```json
{
  "statusLine": {
    "type": "command",
    "command": "python3 /path/to/claude-context-helpers/hooks/statusline.py"
  },
  "hooks": {
    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 /path/to/claude-context-helpers/hooks/context_warn.py"
          }
        ]
      }
    ]
  }
}
```

The two scripts work independently, so you can set up just one. Both import `context_constants.py` and `context_usage.py` from their own directory, so keep the four files together.

## Tuning

Everything lives in `context_constants.py`:

- **Thresholds**: `WARN_AT`, `EXPIRED_AT`, `RESUBMIT_WINDOW_S` for the hook; `YELLOW_AT`, `RED_AT` for the status line.
- **Prices**: Opus 5 list prices (`INPUT_PRICE = 5.0` $/MTok). Cache read is 0.1×, a 5-minute cache write 1.25×, and a 1-hour cache write 2× that price. Change `INPUT_PRICE` if you use a different model. The dollar figures are estimates, not billing.
