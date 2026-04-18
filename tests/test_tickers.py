"""Tests for the Tickers service (ticker/CIK/company name resolution)."""

# pylint: disable=redefined-outer-name

from unittest.mock import MagicMock

import pytest

from edgar.tickers import Tickers
from edgar.exceptions import EdgarRequestError


# ---------------------------------------------------------------------------
# Sample SEC company_tickers.json payload
# ---------------------------------------------------------------------------

SAMPLE_TICKERS_JSON = {
    "0": {"cik_str": 320193, "ticker": "AAPL", "title": "Apple Inc."},
    "1": {"cik_str": 789019, "ticker": "MSFT", "title": "MICROSOFT CORP"},
    "2": {"cik_str": 1326801, "ticker": "META", "title": "Meta Platforms, Inc."},
    "3": {"cik_str": 320193, "ticker": "AAPL34", "title": "Apple Inc."},
}


@pytest.fixture
def mock_session():
    """Return a mock EdgarSession whose make_request returns sample tickers."""
    session = MagicMock()
    session.make_request.return_value = SAMPLE_TICKERS_JSON
    return session


@pytest.fixture
def tickers_service(mock_session):
    """Return a Tickers instance backed by the mock session."""
    return Tickers(session=mock_session)


# ---------------------------------------------------------------------------
# resolve_ticker tests
# ---------------------------------------------------------------------------


class TestResolveTicker:
    """Tests for resolving ticker symbols to CIK numbers."""

    def test_resolve_known_ticker(self, tickers_service):
        """Verify a known ticker returns the correct zero-padded CIK."""
        cik = tickers_service.resolve_ticker("AAPL")
        assert cik == "0000320193"

    def test_resolve_ticker_case_insensitive(self, tickers_service):
        """Verify ticker lookup is case-insensitive."""
        cik = tickers_service.resolve_ticker("aapl")
        assert cik == "0000320193"

    def test_resolve_ticker_not_found(self, tickers_service):
        """Verify an unknown ticker raises ValueError."""
        with pytest.raises(ValueError, match="not found"):
            tickers_service.resolve_ticker("ZZZZZ")

    def test_resolve_ticker_meta(self, tickers_service):
        """Verify META resolves to its expected CIK."""
        cik = tickers_service.resolve_ticker("META")
        assert cik == "0001326801"


# ---------------------------------------------------------------------------
# resolve_cik tests
# ---------------------------------------------------------------------------


class TestResolveCik:
    """Tests for reverse-resolving CIK numbers to company entries."""

    def test_resolve_cik_as_int(self, tickers_service):
        """Verify CIK passed as an int returns all matching entries."""
        entries = tickers_service.resolve_cik(320193)
        assert len(entries) == 2
        tickers = [e["ticker"] for e in entries]
        assert "AAPL" in tickers
        assert "AAPL34" in tickers

    def test_resolve_cik_as_string(self, tickers_service):
        """Verify CIK passed as a string is handled correctly."""
        entries = tickers_service.resolve_cik("320193")
        assert entries[0]["title"] == "Apple Inc."

    def test_resolve_cik_zero_padded(self, tickers_service):
        """Verify a zero-padded CIK string is resolved correctly."""
        entries = tickers_service.resolve_cik("0000320193")
        assert entries[0]["cik_str"] == 320193

    def test_resolve_cik_not_found(self, tickers_service):
        """Verify an unknown CIK raises ValueError."""
        with pytest.raises(ValueError, match="not found"):
            tickers_service.resolve_cik(9999999)


# ---------------------------------------------------------------------------
# search tests
# ---------------------------------------------------------------------------


class TestSearch:
    """Tests for case-insensitive company name and ticker search."""

    def test_search_by_company_name(self, tickers_service):
        """Verify searching by company name returns matching entries."""
        results = tickers_service.search("Apple")
        assert len(results) == 2
        assert all("Apple" in r["title"] for r in results)

    def test_search_by_ticker(self, tickers_service):
        """Verify searching by ticker symbol returns the correct entry."""
        results = tickers_service.search("MSFT")
        assert len(results) == 1
        assert results[0]["ticker"] == "MSFT"

    def test_search_case_insensitive(self, tickers_service):
        """Verify search is case-insensitive."""
        results = tickers_service.search("meta")
        assert len(results) == 1
        assert results[0]["ticker"] == "META"

    def test_search_no_results(self, tickers_service):
        """Verify search returns an empty list when nothing matches."""
        results = tickers_service.search("xyznonexistent")
        assert results == []


# ---------------------------------------------------------------------------
# caching tests
# ---------------------------------------------------------------------------


class TestCaching:
    """Tests for lazy-loading and in-memory caching behavior."""

    def test_data_loaded_once(self, mock_session, tickers_service):
        """Verify the tickers endpoint is fetched only once across multiple calls."""
        tickers_service.resolve_ticker("AAPL")
        tickers_service.resolve_ticker("MSFT")
        tickers_service.search("Apple")

        # make_request should only be called once despite multiple API calls.
        mock_session.make_request.assert_called_once()

    def test_bad_response_raises(self):
        """Verify a None response from the API raises EdgarRequestError."""
        session = MagicMock()
        session.make_request.return_value = None
        service = Tickers(session=session)

        with pytest.raises(EdgarRequestError):
            service.resolve_ticker("AAPL")
