import time
from collections import defaultdict, deque
from dataclasses import dataclass
from threading import Lock

from fastapi import HTTPException, status

from app.core.config import get_settings


@dataclass(frozen=True)
class RateLimitRule:
    key: str
    limit: int
    window_seconds: int = 60


class InMemoryRateLimiter:
    def __init__(self) -> None:
        self._events: dict[str, deque[float]] = defaultdict(deque)
        self._lock = Lock()

    def check(self, rules: list[RateLimitRule]) -> None:
        now = time.monotonic()
        with self._lock:
            for rule in rules:
                events = self._events[rule.key]
                while events and now - events[0] > rule.window_seconds:
                    events.popleft()
                if len(events) >= rule.limit:
                    raise HTTPException(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        detail="Rate limit exceeded. Please wait a minute and try again.",
                    )

            for rule in rules:
                self._events[rule.key].append(now)


rate_limiter = InMemoryRateLimiter()


def enforce_chat_rate_limit(ip_address: str, session_id: str | None) -> None:
    settings = get_settings()
    rules = [
        RateLimitRule(key=f"ip:{ip_address}", limit=settings.rate_limit_per_ip_per_minute),
    ]
    if session_id:
        rules.append(RateLimitRule(key=f"session:{session_id}", limit=settings.rate_limit_per_session_per_minute))
    rate_limiter.check(rules)
