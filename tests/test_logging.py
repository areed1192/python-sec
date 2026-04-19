"""Tests for logging output across key edgar modules."""

# pylint: disable=redefined-outer-name
# pylint: disable=protected-access
# pylint: disable=import-outside-toplevel

import importlib.util
import logging
from unittest.mock import MagicMock, patch, AsyncMock

import pytest

from edgar.cache import TTLCache
from edgar.session import EdgarSession


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def session():
    """Return an EdgarSession with a mock client."""
    mock_client = MagicMock()
    return EdgarSession(client=mock_client, user_agent="Test Agent test@example.com")


# ---------------------------------------------------------------------------
# Cache logging tests
# ---------------------------------------------------------------------------


class TestCacheLogging:
    """Tests that TTLCache emits debug logs on hit, miss, and expiry."""

    def test_cache_miss_logs_debug(self, caplog):
        """Verify cache miss emits a debug log."""
        cache = TTLCache()
        with caplog.at_level(logging.DEBUG, logger="edgar.cache"):
            cache.get("nonexistent")
        assert any("Cache miss" in m and "nonexistent" in m for m in caplog.messages)

    def test_cache_hit_logs_debug(self, caplog):
        """Verify cache hit emits a debug log."""
        cache = TTLCache()
        cache.set("key1", "value1", 60)
        caplog.clear()
        with caplog.at_level(logging.DEBUG, logger="edgar.cache"):
            cache.get("key1")
        assert any("Cache hit" in m and "key1" in m for m in caplog.messages)

    def test_cache_set_logs_debug(self, caplog):
        """Verify cache set emits a debug log with TTL."""
        cache = TTLCache()
        with caplog.at_level(logging.DEBUG, logger="edgar.cache"):
            cache.set("mykey", "myval", 300)
        assert any("Cache set" in m and "mykey" in m and "300" in m for m in caplog.messages)

    def test_cache_invalidate_logs_debug(self, caplog):
        """Verify cache invalidate emits a debug log."""
        cache = TTLCache()
        cache.set("k", "v", 60)
        caplog.clear()
        with caplog.at_level(logging.DEBUG, logger="edgar.cache"):
            cache.invalidate("k")
        assert any("Cache invalidated" in m and "k" in m for m in caplog.messages)


# ---------------------------------------------------------------------------
# Session error logging tests
# ---------------------------------------------------------------------------


class TestSessionErrorLogging:
    """Tests that EdgarSession logs errors on request failures."""

    def test_request_failure_logs_error(self, session, caplog):
        """Verify that a request exception is logged at error level."""
        import requests

        session.http_session = MagicMock()
        session.http_session.request.side_effect = requests.RequestException("connection refused")

        with caplog.at_level(logging.ERROR, logger="edgar.session"):
            with pytest.raises(Exception):
                session.make_request(method="get", endpoint="/test")

        assert any("Request failed" in m for m in caplog.messages)


# ---------------------------------------------------------------------------
# Rate-limit logging tests
# ---------------------------------------------------------------------------


class TestRateLimitLogging:
    """Tests that rate-limit sleep is logged at debug level."""

    def test_throttle_logs_debug_when_sleeping(self, session, caplog):
        """Verify rate-limit sleep emits a debug log."""
        import time

        # Fill the request window to trigger a sleep.
        now = time.monotonic()
        for _ in range(session._rate_limit):
            session._request_times.append(now)

        with caplog.at_level(logging.DEBUG, logger="edgar.session"):
            with patch("edgar.session.time.sleep"):
                session._throttle()

        assert any("Rate limit" in m and "sleeping" in m for m in caplog.messages)


# ---------------------------------------------------------------------------
# Async session error logging tests
# ---------------------------------------------------------------------------


class TestAsyncSessionErrorLogging:
    """Tests that EdgarAsyncSession logs errors on request failures."""

    @pytest.mark.skipif(
        not importlib.util.find_spec("pytest_asyncio"),
        reason="pytest-asyncio not installed",
    )
    @pytest.mark.asyncio
    async def test_async_request_failure_logs_error(self, caplog):
        """Verify async request exception is logged at error level."""
        try:
            import httpx  # pylint: disable=import-outside-toplevel
        except ImportError:
            pytest.skip("httpx not installed")

        from edgar.async_session import EdgarAsyncSession

        mock_client = MagicMock()
        async_session = EdgarAsyncSession(
            client=mock_client,
            user_agent="Test Agent test@example.com",
        )
        async_session.http_client = AsyncMock()
        async_session.http_client.request.side_effect = httpx.HTTPError("timeout")

        with caplog.at_level(logging.ERROR, logger="edgar.async_session"):
            with pytest.raises(Exception):
                await async_session.make_request(method="get", endpoint="/test")

        assert any("Request failed" in m for m in caplog.messages)
