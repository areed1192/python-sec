"""In-memory TTL cache for SEC EDGAR API responses."""

from __future__ import annotations

import time


# Default TTLs in seconds.
TTL_TICKERS = 86400       # 24 hours — ticker data changes ~quarterly
TTL_TAXONOMY = 86400      # 24 hours — static reference data
TTL_SUBMISSIONS = 3600    # 1 hour — changes on new filings


class TTLCache:
    """Simple in-memory cache with per-key time-to-live expiration.

    Uses ``time.monotonic()`` so expiration is immune to wall-clock
    adjustments.
    """

    def __init__(self) -> None:
        self._store: dict[str, tuple[object, float]] = {}

    def get(self, key: str) -> object | None:
        """Return the cached value for *key*, or ``None`` if missing/expired."""

        entry = self._store.get(key)
        if entry is None:
            return None
        value, expires_at = entry
        if time.monotonic() >= expires_at:
            del self._store[key]
            return None
        return value

    def set(self, key: str, value: object, ttl: float) -> None:
        """Store *value* under *key* with a TTL of *ttl* seconds."""

        self._store[key] = (value, time.monotonic() + ttl)

    def invalidate(self, key: str) -> None:
        """Remove a single key from the cache."""

        self._store.pop(key, None)

    def clear(self) -> None:
        """Remove all entries from the cache."""

        self._store.clear()

    def __len__(self) -> int:
        """Return the count of non-expired entries."""

        now = time.monotonic()
        return sum(1 for _, (_, exp) in self._store.items() if now < exp)

    def __repr__(self) -> str:
        return f"<TTLCache entries={len(self)}>"
