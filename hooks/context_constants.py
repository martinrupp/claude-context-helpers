"""All tunable constants for the context hooks."""

# Opus 5 list prices, $/MTok (only used for the rough per-turn / rewrite estimates)
INPUT_PRICE = 5.0
CACHE_READ_PRICE = INPUT_PRICE * 0.1
CACHE_WRITE_5M_PRICE = INPUT_PRICE * 1.25
CACHE_WRITE_1H_PRICE = INPUT_PRICE * 2.0

# How much of the transcript's end to scan for the last usage entry
TAIL_BYTES = 4 * 1024 * 1024

# context_warn.py
WARN_AT = 200_000
EXPIRED_AT = 100_000
RESUBMIT_WINDOW_S = 180

# statusline.py
YELLOW_AT = 150_000
RED_AT = 300_000

GREEN, YELLOW, RED, DIM, RESET = "\033[32m", "\033[33m", "\033[31m", "\033[2m", "\033[0m"
