# app/utils/time.py

from datetime import datetime, timezone


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def now_ms() -> int:
    return int(now_utc().timestamp() * 1000)
