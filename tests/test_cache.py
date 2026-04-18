"""Tests for the in-memory TTL cache and its integration with services."""

# pylint: disable=redefined-outer-name
# pylint: disable=protected-access
# pylint: disable=import-outside-toplevel

from unittest.mock import MagicMock, patch

from edgar.cache import TTLCache, TTL_TICKERS, TTL_TAXONOMY, TTL_SUBMISSIONS
from edgar.tickers import Tickers
from edgar.submissions import Submissions
from edgar.xbrl import Xbrl


# ---------------------------------------------------------------------------
# Sample data fixtures
# ---------------------------------------------------------------------------

SAMPLE_TICKERS_JSON = {
    "0": {"cik_str": 320193, "ticker": "AAPL", "title": "Apple Inc."},
    "1": {"cik_str": 789019, "ticker": "MSFT", "title": "MICROSOFT CORP"},
}

SAMPLE_SUBMISSIONS_RESPONSE = {
    "cik": "320193",
    "entityType": "operating",
    "sic": "3571",
    "name": "Apple Inc.",
}

SAMPLE_COMPANY_FACTS = {
    "cik": 320193,
    "entityName": "Apple Inc.",
    "facts": {"us-gaap": {}},
}


# ---------------------------------------------------------------------------
# TTLCache unit tests
# ---------------------------------------------------------------------------


class TestTTLCacheGetSet:
    """Tests for basic get/set operations."""

    def test_get_returns_none_for_missing_key(self):
        """Verify get() returns None when key is absent."""
        cache = TTLCache()
        assert cache.get("nonexistent") is None

    def test_set_and_get_returns_value(self):
        """Verify a value can be stored and retrieved."""
        cache = TTLCache()
        cache.set("key", {"data": 1}, ttl=60)
        assert cache.get("key") == {"data": 1}

    def test_set_overwrites_existing_key(self):
        """Verify set() overwrites a previous value for the same key."""
        cache = TTLCache()
        cache.set("key", "old", ttl=60)
        cache.set("key", "new", ttl=60)
        assert cache.get("key") == "new"

    def test_get_returns_none_for_expired_entry(self):
        """Verify get() returns None after TTL expires."""
        cache = TTLCache()
        with patch("edgar.cache.time.monotonic", return_value=1000.0):
            cache.set("key", "value", ttl=10)
        with patch("edgar.cache.time.monotonic", return_value=1010.0):
            assert cache.get("key") is None

    def test_get_returns_value_before_expiration(self):
        """Verify get() returns the value before TTL expires."""
        cache = TTLCache()
        with patch("edgar.cache.time.monotonic", return_value=1000.0):
            cache.set("key", "value", ttl=10)
        with patch("edgar.cache.time.monotonic", return_value=1009.9):
            assert cache.get("key") == "value"

    def test_expired_entry_is_removed_from_store(self):
        """Verify expired entries are removed from internal store on access."""
        cache = TTLCache()
        with patch("edgar.cache.time.monotonic", return_value=1000.0):
            cache.set("key", "value", ttl=5)
        with patch("edgar.cache.time.monotonic", return_value=1005.0):
            cache.get("key")
        assert "key" not in cache._store


# ---------------------------------------------------------------------------
# TTLCache invalidate / clear tests
# ---------------------------------------------------------------------------


class TestTTLCacheInvalidateClear:
    """Tests for invalidate() and clear() operations."""

    def test_invalidate_removes_key(self):
        """Verify invalidate() removes a specific key."""
        cache = TTLCache()
        cache.set("a", 1, ttl=60)
        cache.set("b", 2, ttl=60)
        cache.invalidate("a")
        assert cache.get("a") is None
        assert cache.get("b") == 2

    def test_invalidate_missing_key_is_noop(self):
        """Verify invalidate() on a missing key does not raise."""
        cache = TTLCache()
        cache.invalidate("missing")

    def test_clear_removes_all_entries(self):
        """Verify clear() empties the entire cache."""
        cache = TTLCache()
        cache.set("a", 1, ttl=60)
        cache.set("b", 2, ttl=60)
        cache.clear()
        assert cache.get("a") is None
        assert cache.get("b") is None
        assert len(cache) == 0


# ---------------------------------------------------------------------------
# TTLCache __len__ and __repr__ tests
# ---------------------------------------------------------------------------


class TestTTLCacheLenRepr:
    """Tests for __len__() and __repr__()."""

    def test_len_counts_non_expired_entries(self):
        """Verify __len__ counts only non-expired entries."""
        cache = TTLCache()
        with patch("edgar.cache.time.monotonic", return_value=1000.0):
            cache.set("fresh", "v1", ttl=60)
            cache.set("stale", "v2", ttl=5)
        with patch("edgar.cache.time.monotonic", return_value=1010.0):
            assert len(cache) == 1

    def test_len_empty_cache(self):
        """Verify __len__ returns 0 for an empty cache."""
        cache = TTLCache()
        assert len(cache) == 0

    def test_repr_contains_entry_count(self):
        """Verify __repr__ shows the number of entries."""
        cache = TTLCache()
        cache.set("a", 1, ttl=60)
        assert "entries=1" in repr(cache)


# ---------------------------------------------------------------------------
# TTL constants tests
# ---------------------------------------------------------------------------


class TestTTLConstants:
    """Tests for the module-level TTL constants."""

    def test_ttl_tickers_is_24_hours(self):
        """Verify TTL_TICKERS equals 86400 seconds."""
        assert TTL_TICKERS == 86400

    def test_ttl_taxonomy_is_24_hours(self):
        """Verify TTL_TAXONOMY equals 86400 seconds."""
        assert TTL_TAXONOMY == 86400

    def test_ttl_submissions_is_1_hour(self):
        """Verify TTL_SUBMISSIONS equals 3600 seconds."""
        assert TTL_SUBMISSIONS == 3600


# ---------------------------------------------------------------------------
# EdgarClient cache parameter tests
# ---------------------------------------------------------------------------


class TestEdgarClientCacheParam:
    """Tests for EdgarClient cache=True/False behaviour."""

    def test_cache_true_creates_ttl_cache(self):
        """Verify EdgarClient(cache=True) creates a TTLCache on the session."""
        from edgar.client import EdgarClient

        client = EdgarClient(user_agent="Test test@test.com", cache=True)
        assert isinstance(client._ttl_cache, TTLCache)

    def test_cache_false_sets_none(self):
        """Verify EdgarClient(cache=False) sets _ttl_cache to None."""
        from edgar.client import EdgarClient

        client = EdgarClient(user_agent="Test test@test.com", cache=False)
        assert client._ttl_cache is None


# ---------------------------------------------------------------------------
# Tickers cache integration tests
# ---------------------------------------------------------------------------


class TestTickersCaching:
    """Tests for cache integration in the Tickers service."""

    def test_cache_hit_skips_http(self):
        """Verify a cache hit returns data without calling make_request."""
        cache = TTLCache()
        data = list(SAMPLE_TICKERS_JSON.values())
        ticker_to_cik = {"AAPL": 320193, "MSFT": 789019}
        cik_to_entries = {
            320193: [data[0]],
            789019: [data[1]],
        }
        cache.set("tickers", (data, ticker_to_cik, cik_to_entries), TTL_TICKERS)

        session = MagicMock()
        session.cache = cache
        service = Tickers(session=session)
        result = service.resolve_ticker("AAPL")

        assert result == "0000320193"
        session.make_request.assert_not_called()

    def test_cache_miss_fetches_and_stores(self):
        """Verify a cache miss fetches via HTTP and stores in cache."""
        cache = TTLCache()
        session = MagicMock()
        session.cache = cache
        session.make_request.return_value = SAMPLE_TICKERS_JSON

        service = Tickers(session=session)
        service.resolve_ticker("AAPL")

        session.make_request.assert_called_once()
        assert cache.get("tickers") is not None

    def test_cache_disabled_still_works(self):
        """Verify tickers work normally when cache is None."""
        session = MagicMock()
        session.cache = None
        session.make_request.return_value = SAMPLE_TICKERS_JSON

        service = Tickers(session=session)
        result = service.resolve_ticker("AAPL")

        assert result == "0000320193"
        session.make_request.assert_called_once()


# ---------------------------------------------------------------------------
# Submissions cache integration tests
# ---------------------------------------------------------------------------


class TestSubmissionsCaching:
    """Tests for cache integration in the Submissions service."""

    def test_cache_hit_skips_http(self):
        """Verify a cache hit returns data without calling make_request."""
        cache = TTLCache()
        padded_cik = "0000320193"
        cache.set(f"submissions:{padded_cik}", SAMPLE_SUBMISSIONS_RESPONSE, TTL_SUBMISSIONS)

        session = MagicMock()
        session.cache = cache
        session.edgar_utilities = MagicMock()

        service = Submissions(session=session)
        result = service.get_submissions(cik="320193")

        assert result == SAMPLE_SUBMISSIONS_RESPONSE
        session.make_request.assert_not_called()

    def test_cache_miss_fetches_and_stores(self):
        """Verify a cache miss fetches via HTTP and stores in cache."""
        cache = TTLCache()
        session = MagicMock()
        session.cache = cache
        session.make_request.return_value = SAMPLE_SUBMISSIONS_RESPONSE
        session.edgar_utilities = MagicMock()

        service = Submissions(session=session)
        service.get_submissions(cik="320193")

        session.make_request.assert_called_once()
        assert cache.get("submissions:0000320193") == SAMPLE_SUBMISSIONS_RESPONSE

    def test_cache_disabled_still_works(self):
        """Verify submissions work normally when cache is None."""
        session = MagicMock()
        session.cache = None
        session.make_request.return_value = SAMPLE_SUBMISSIONS_RESPONSE
        session.edgar_utilities = MagicMock()

        service = Submissions(session=session)
        result = service.get_submissions(cik="320193")

        assert result == SAMPLE_SUBMISSIONS_RESPONSE
        session.make_request.assert_called_once()

    def test_none_response_is_not_cached(self):
        """Verify a None response from the API is not stored in cache."""
        cache = TTLCache()
        session = MagicMock()
        session.cache = cache
        session.make_request.return_value = None
        session.edgar_utilities = MagicMock()

        service = Submissions(session=session)
        service.get_submissions(cik="320193")

        assert cache.get("submissions:0000320193") is None


# ---------------------------------------------------------------------------
# XBRL company_facts cache integration tests
# ---------------------------------------------------------------------------


class TestXbrlCaching:
    """Tests for cache integration in the Xbrl.company_facts method."""

    def test_cache_hit_skips_http(self):
        """Verify a cache hit returns data without calling make_request."""
        cache = TTLCache()
        padded_cik = "0000320193"
        cache.set(f"company_facts:{padded_cik}", SAMPLE_COMPANY_FACTS, TTL_TAXONOMY)

        session = MagicMock()
        session.cache = cache
        session.edgar_utilities = MagicMock()

        xbrl = Xbrl(session=session)
        result = xbrl.company_facts(cik="320193")

        assert result == SAMPLE_COMPANY_FACTS
        session.make_request.assert_not_called()

    def test_cache_miss_fetches_and_stores(self):
        """Verify a cache miss fetches via HTTP and stores in cache."""
        cache = TTLCache()
        session = MagicMock()
        session.cache = cache
        session.make_request.return_value = SAMPLE_COMPANY_FACTS
        session.edgar_utilities = MagicMock()

        xbrl = Xbrl(session=session)
        xbrl.company_facts(cik="320193")

        session.make_request.assert_called_once()
        assert cache.get("company_facts:0000320193") == SAMPLE_COMPANY_FACTS

    def test_cache_disabled_still_works(self):
        """Verify company_facts works normally when cache is None."""
        session = MagicMock()
        session.cache = None
        session.make_request.return_value = SAMPLE_COMPANY_FACTS
        session.edgar_utilities = MagicMock()

        xbrl = Xbrl(session=session)
        result = xbrl.company_facts(cik="320193")

        assert result == SAMPLE_COMPANY_FACTS
        session.make_request.assert_called_once()

    def test_none_response_is_not_cached(self):
        """Verify a None response from the API is not stored in cache."""
        cache = TTLCache()
        session = MagicMock()
        session.cache = cache
        session.make_request.return_value = None
        session.edgar_utilities = MagicMock()

        xbrl = Xbrl(session=session)
        xbrl.company_facts(cik="320193")

        assert cache.get("company_facts:0000320193") is None

    def test_cache_uses_padded_cik(self):
        """Verify the cache key uses the zero-padded CIK."""
        cache = TTLCache()
        session = MagicMock()
        session.cache = cache
        session.make_request.return_value = SAMPLE_COMPANY_FACTS
        session.edgar_utilities = MagicMock()

        xbrl = Xbrl(session=session)
        xbrl.company_facts(cik="320193")

        # Should be stored under the padded key.
        assert cache.get("company_facts:0000320193") is not None
        # Short CIK should not be in cache.
        assert cache.get("company_facts:320193") is None
