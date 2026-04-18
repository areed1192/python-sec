"""Tests for the EdgarAsyncClient and EdgarAsyncSession."""

# pylint: disable=redefined-outer-name
# pylint: disable=protected-access
# pylint: disable=import-outside-toplevel
# pylint: disable=missing-function-docstring

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from edgar.async_session import EdgarAsyncSession, MAX_REQUESTS_PER_SECOND, _require_httpx
from edgar.async_client import EdgarAsyncClient
from edgar.exceptions import EdgarRequestError


# ---------------------------------------------------------------------------
# Skip the entire module if httpx is not installed
# ---------------------------------------------------------------------------

httpx = pytest.importorskip("httpx")


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def async_client():
    """Return an EdgarAsyncClient for testing."""
    return EdgarAsyncClient(user_agent="TestSuite test@example.com")


@pytest.fixture
def async_session(async_client):
    """Return the EdgarAsyncSession from the test client."""
    return async_client.edgar_session


# ---------------------------------------------------------------------------
# EdgarAsyncSession Tests
# ---------------------------------------------------------------------------


class TestAsyncSessionInit:
    """Tests for EdgarAsyncSession initialization."""

    def test_creates_instance(self, async_session):
        assert isinstance(async_session, EdgarAsyncSession)

    def test_default_rate_limit(self, async_session):
        assert async_session._rate_limit == MAX_REQUESTS_PER_SECOND

    def test_custom_rate_limit(self):
        client = EdgarAsyncClient(user_agent="Test test@example.com", rate_limit=5)
        assert client.edgar_session._rate_limit == 5

    def test_rate_limit_too_low_raises(self):
        with pytest.raises(ValueError, match="rate_limit must be between 1 and"):
            EdgarAsyncClient(user_agent="Test test@example.com", rate_limit=0)

    def test_rate_limit_too_high_raises(self):
        with pytest.raises(ValueError, match="rate_limit must be between 1 and"):
            EdgarAsyncClient(user_agent="Test test@example.com", rate_limit=11)

    def test_repr(self, async_session):
        assert "EdgarAsyncSession" in repr(async_session)

    def test_user_agent_stored(self, async_session):
        assert async_session.user_agent == "TestSuite test@example.com"


class TestAsyncSessionBuildUrl:
    """Tests for URL building."""

    def test_default_url(self, async_session):
        url = async_session.build_url("/test/endpoint")
        assert url == "https://www.sec.gov/test/endpoint"

    def test_api_url(self, async_session):
        url = async_session.build_url("/test/endpoint", use_api=True)
        assert url == "https://data.sec.gov/test/endpoint"

    def test_custom_base_url(self, async_session):
        url = async_session.build_url("/search", base_url="https://efts.sec.gov")
        assert url == "https://efts.sec.gov/search"


class TestAsyncSessionThrottle:
    """Tests for the async rate limiter."""

    @pytest.mark.asyncio
    async def test_throttle_allows_within_limit(self, async_session):
        """Requests within the rate limit should not sleep."""
        async_session._rate_limit = 10
        async_session._request_times.clear()
        # Should complete without error.
        await async_session._throttle()
        assert len(async_session._request_times) == 1

    @pytest.mark.asyncio
    async def test_throttle_sleeps_at_capacity(self, async_session):
        """Should sleep when at rate limit capacity."""
        async_session._rate_limit = 2
        loop = asyncio.get_event_loop()
        now = loop.time()
        async_session._request_times.clear()
        async_session._request_times.append(now)
        async_session._request_times.append(now)

        with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
            await async_session._throttle()
            mock_sleep.assert_called_once()


class TestAsyncSessionMakeRequest:
    """Tests for async make_request."""

    @pytest.mark.asyncio
    async def test_make_request_json(self, async_session):
        """Should parse JSON response correctly."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "application/json"}
        mock_response.content = b'{"key": "value"}'
        mock_response.json.return_value = {"key": "value"}

        async_session.http_client.request = AsyncMock(return_value=mock_response)
        async_session._throttle = AsyncMock()

        result = await async_session.make_request("get", "/test")
        assert result == {"key": "value"}

    @pytest.mark.asyncio
    async def test_make_request_xml(self, async_session):
        """Should return text for XML content types."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "application/xml"}
        mock_response.content = b"<root/>"
        mock_response.text = "<root/>"

        async_session.http_client.request = AsyncMock(return_value=mock_response)
        async_session._throttle = AsyncMock()

        result = await async_session.make_request("get", "/test")
        assert result == "<root/>"

    @pytest.mark.asyncio
    async def test_make_request_empty_content(self, async_session):
        """Should return None for empty responses."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "application/json"}
        mock_response.content = b""

        async_session.http_client.request = AsyncMock(return_value=mock_response)
        async_session._throttle = AsyncMock()

        result = await async_session.make_request("get", "/test")
        assert result is None

    @pytest.mark.asyncio
    async def test_make_request_error_raises(self, async_session):
        """Should raise EdgarRequestError on HTTP errors."""
        async_session.http_client.request = AsyncMock(
            side_effect=httpx.HTTPError("Connection failed")
        )
        async_session._throttle = AsyncMock()

        with pytest.raises(EdgarRequestError, match="failed"):
            await async_session.make_request("get", "/test")


class TestAsyncSessionDownload:
    """Tests for async download."""

    @pytest.mark.asyncio
    async def test_download_text(self, async_session):
        """Should download text content."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "text/html"}
        mock_response.text = "<html>test</html>"

        async_session.http_client.get = AsyncMock(return_value=mock_response)
        async_session._throttle = AsyncMock()

        result = await async_session.download("https://www.sec.gov/test.html")
        assert result == "<html>test</html>"

    @pytest.mark.asyncio
    async def test_download_to_file(self, async_session, tmp_path):
        """Should save content to file when path given."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "text/html"}
        mock_response.text = "<html>test</html>"

        async_session.http_client.get = AsyncMock(return_value=mock_response)
        async_session._throttle = AsyncMock()

        file_path = str(tmp_path / "output.html")
        result = await async_session.download("https://www.sec.gov/test.html", path=file_path)
        assert result == file_path
        with open(file_path, encoding="utf-8") as f:
            assert f.read() == "<html>test</html>"

    @pytest.mark.asyncio
    async def test_download_non_200_raises(self, async_session):
        """Should raise on non-200 status."""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.headers = {"content-type": "text/html"}

        async_session.http_client.get = AsyncMock(return_value=mock_response)
        async_session._throttle = AsyncMock()

        with pytest.raises(EdgarRequestError, match="returned status 404"):
            await async_session.download("https://www.sec.gov/missing.html")


class TestAsyncSessionFetchPage:
    """Tests for async fetch_page."""

    @pytest.mark.asyncio
    async def test_fetch_page_success(self, async_session):
        """Should return bytes on success."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"page content"

        async_session.http_client.get = AsyncMock(return_value=mock_response)
        async_session._throttle = AsyncMock()

        result = await async_session.fetch_page("https://www.sec.gov/page")
        assert result == b"page content"

    @pytest.mark.asyncio
    async def test_fetch_page_not_found(self, async_session):
        """Should return None on non-200."""
        mock_response = MagicMock()
        mock_response.status_code = 404

        async_session.http_client.get = AsyncMock(return_value=mock_response)
        async_session._throttle = AsyncMock()

        result = await async_session.fetch_page("https://www.sec.gov/missing")
        assert result is None


# ---------------------------------------------------------------------------
# EdgarAsyncClient Tests
# ---------------------------------------------------------------------------


class TestAsyncClientInit:
    """Tests for EdgarAsyncClient initialization."""

    def test_creates_instance(self, async_client):
        assert isinstance(async_client, EdgarAsyncClient)

    def test_repr(self, async_client):
        assert "EdgarAsyncClient" in repr(async_client)


class TestAsyncClientContextManager:
    """Tests for the async context manager."""

    @pytest.mark.asyncio
    async def test_context_manager(self):
        """Should close cleanly."""
        async with EdgarAsyncClient(user_agent="Test test@example.com") as client:
            assert isinstance(client, EdgarAsyncClient)


class TestAsyncClientResolveTicker:
    """Tests for ticker resolution."""

    @pytest.mark.asyncio
    async def test_resolve_ticker(self, async_client):
        """Should resolve a ticker to a CIK."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "application/json"}
        mock_response.content = b'{"0": {"cik_str": 320193, "ticker": "AAPL", "title": "Apple Inc."}}'
        mock_response.json.return_value = {
            "0": {"cik_str": 320193, "ticker": "AAPL", "title": "Apple Inc."}
        }

        async_client.edgar_session.http_client.request = AsyncMock(return_value=mock_response)
        async_client.edgar_session._throttle = AsyncMock()

        result = await async_client.resolve_ticker("AAPL")
        assert result == "0000320193"

    @pytest.mark.asyncio
    async def test_resolve_ticker_not_found(self, async_client):
        """Should raise on unknown ticker."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "application/json"}
        mock_response.content = b'{"0": {"cik_str": 320193, "ticker": "AAPL", "title": "Apple Inc."}}'
        mock_response.json.return_value = {
            "0": {"cik_str": 320193, "ticker": "AAPL", "title": "Apple Inc."}
        }

        async_client.edgar_session.http_client.request = AsyncMock(return_value=mock_response)
        async_client.edgar_session._throttle = AsyncMock()

        with pytest.raises(EdgarRequestError, match="Ticker not found"):
            await async_client.resolve_ticker("ZZZZ")


class TestAsyncClientResolveCik:
    """Tests for CIK resolution."""

    @pytest.mark.asyncio
    async def test_resolve_cik(self, async_client):
        """Should resolve a CIK to company entries."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "application/json"}
        mock_response.content = b'{"0": {"cik_str": 320193, "ticker": "AAPL", "title": "Apple Inc."}}'
        mock_response.json.return_value = {
            "0": {"cik_str": 320193, "ticker": "AAPL", "title": "Apple Inc."}
        }

        async_client.edgar_session.http_client.request = AsyncMock(return_value=mock_response)
        async_client.edgar_session._throttle = AsyncMock()

        result = await async_client.resolve_cik("320193")
        assert len(result) == 1
        assert result[0]["ticker"] == "AAPL"


class TestAsyncClientSearch:
    """Tests for async search."""

    @pytest.mark.asyncio
    async def test_search_returns_results(self, async_client):
        """Should return SearchResult list."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "application/json"}
        mock_response.content = b'{"hits": {"hits": [{"_source": {"file_name": "test.htm"}}]}}'
        mock_response.json.return_value = {
            "hits": {"hits": [{"_source": {"file_name": "test.htm"}}]}
        }

        async_client.edgar_session.http_client.request = AsyncMock(return_value=mock_response)
        async_client.edgar_session._throttle = AsyncMock()

        results = await async_client.search("revenue recognition")
        assert len(results) == 1

    @pytest.mark.asyncio
    async def test_search_empty(self, async_client):
        """Should return empty list when no hits."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "application/json"}
        mock_response.content = b'{"hits": {"hits": []}}'
        mock_response.json.return_value = {"hits": {"hits": []}}

        async_client.edgar_session.http_client.request = AsyncMock(return_value=mock_response)
        async_client.edgar_session._throttle = AsyncMock()

        results = await async_client.search("nonexistent query xyz123")
        assert results == []


class TestAsyncClientDownload:
    """Tests for async download."""

    @pytest.mark.asyncio
    async def test_download_delegates_to_session(self, async_client):
        """Should delegate download to session."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "text/html"}
        mock_response.text = "<html>content</html>"

        async_client.edgar_session.http_client.get = AsyncMock(return_value=mock_response)
        async_client.edgar_session._throttle = AsyncMock()

        result = await async_client.download("https://www.sec.gov/test.html")
        assert result == "<html>content</html>"


class TestAsyncClientGetCompanyInfo:
    """Tests for async get_company_info."""

    @pytest.mark.asyncio
    async def test_get_company_info_by_cik(self, async_client):
        """Should return CompanyInfo for a CIK."""
        from edgar.models import CompanyInfo

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "application/json"}
        raw = {"cik": "320193", "entityType": "company", "name": "Apple Inc."}
        mock_response.content = b'{"cik": "320193"}'
        mock_response.json.return_value = raw

        async_client.edgar_session.http_client.request = AsyncMock(return_value=mock_response)
        async_client.edgar_session._throttle = AsyncMock()

        result = await async_client.get_company_info("320193")
        assert isinstance(result, CompanyInfo)


class TestAsyncClientGetFacts:
    """Tests for async get_facts."""

    @pytest.mark.asyncio
    async def test_get_facts(self, async_client):
        """Should return Facts object."""
        from edgar.models import Facts

        tickers_response = MagicMock()
        tickers_response.status_code = 200
        tickers_response.headers = {"content-type": "application/json"}
        tickers_response.content = b'{"0": {"cik_str": 320193, "ticker": "AAPL", "title": "Apple Inc."}}'
        tickers_response.json.return_value = {
            "0": {"cik_str": 320193, "ticker": "AAPL", "title": "Apple Inc."}
        }

        facts_raw = {"cik": 320193, "entityName": "Apple Inc.", "facts": {}}
        facts_response = MagicMock()
        facts_response.status_code = 200
        facts_response.headers = {"content-type": "application/json"}
        facts_response.content = b'{"cik": 320193}'
        facts_response.json.return_value = facts_raw

        call_count = 0

        async def side_effect(**kwargs): # pylint: disable=unused-argument
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return tickers_response
            return facts_response

        async_client.edgar_session.http_client.request = AsyncMock(side_effect=side_effect)
        async_client.edgar_session._throttle = AsyncMock()

        result = await async_client.get_facts("AAPL")
        assert isinstance(result, Facts)


class TestRequireHttpx:
    """Tests for the _require_httpx helper."""

    def test_require_httpx_succeeds(self):
        """Should return the httpx module when installed."""
        result = _require_httpx()
        assert result is httpx

    def test_require_httpx_missing(self):
        """Should raise ImportError with install instructions when missing."""
        with patch.dict("sys.modules", {"httpx": None}):
            with pytest.raises(ImportError, match="pip install python-sec"):
                _require_httpx()
