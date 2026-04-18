"""Tests for the EDGAR Full-Text Search (EFTS) service and SearchResult model."""

# pylint: disable=redefined-outer-name
# pylint: disable=protected-access

from unittest.mock import MagicMock, patch

import pytest

from edgar.models import SearchResult
from edgar.search import Search, EFTS_BASE_URL
from edgar.client import EdgarClient


# ---------------------------------------------------------------------------
# Sample raw data fixtures
# ---------------------------------------------------------------------------

SAMPLE_HIT = {
    "_index": "edgar_file",
    "_id": "0001193125-24-047930:d123456dex993.htm",
    "_score": 8.5,
    "_source": {
        "ciks": ["0001418076"],
        "display_names": ["SLR Investment Corp.  (SLRC)  (CIK 0001418076)"],
        "file_date": "2024-02-27",
        "form": "10-K",
        "root_forms": ["10-K"],
        "adsh": "0001193125-24-047930",
        "file_type": "EX-99.3",
        "file_description": "EX-99.3",
        "period_ending": "2023-12-31",
        "sics": [],
        "biz_locations": ["New York, NY"],
        "biz_states": ["NY"],
        "inc_states": ["MD"],
        "items": [],
        "sequence": 18,
    },
}

SAMPLE_HIT_MINIMAL = {
    "_id": "0000320193-24-000123:aapl-20240928.htm",
    "_score": 7.2,
    "_source": {
        "ciks": ["0000320193"],
        "display_names": ["Apple Inc.  (AAPL)  (CIK 0000320193)"],
        "file_date": "2024-11-01",
        "form": "10-K",
        "adsh": "0000320193-24-000123",
        "file_type": "10-K",
        "file_description": "10-K",
        "period_ending": "2024-09-28",
    },
}

SAMPLE_HIT_EMPTY_SOURCE = {
    "_id": "",
    "_score": 0,
    "_source": {},
}

SAMPLE_EFTS_RESPONSE = {
    "took": 150,
    "timed_out": False,
    "hits": {
        "total": {"value": 5079, "relation": "eq"},
        "max_score": 8.5,
        "hits": [SAMPLE_HIT, SAMPLE_HIT_MINIMAL],
    },
}


# ---------------------------------------------------------------------------
# SearchResult model tests
# ---------------------------------------------------------------------------


class TestSearchResult:
    """Tests for the SearchResult dataclass."""

    def test_company_name(self):
        """Verify company_name extracts the first display name."""
        result = SearchResult(raw=SAMPLE_HIT)
        assert result.company_name == "SLR Investment Corp.  (SLRC)  (CIK 0001418076)"

    def test_cik(self):
        """Verify cik extracts the first CIK string."""
        result = SearchResult(raw=SAMPLE_HIT)
        assert result.cik == "0001418076"

    def test_form(self):
        """Verify form extracts the specific form type."""
        result = SearchResult(raw=SAMPLE_HIT)
        assert result.form == "10-K"

    def test_filing_date(self):
        """Verify filing_date extracts the file_date."""
        result = SearchResult(raw=SAMPLE_HIT)
        assert result.filing_date == "2024-02-27"

    def test_accession_number(self):
        """Verify accession_number extracts the adsh field."""
        result = SearchResult(raw=SAMPLE_HIT)
        assert result.accession_number == "0001193125-24-047930"

    def test_file_type(self):
        """Verify file_type extracts correctly."""
        result = SearchResult(raw=SAMPLE_HIT)
        assert result.file_type == "EX-99.3"

    def test_file_description(self):
        """Verify file_description extracts correctly."""
        result = SearchResult(raw=SAMPLE_HIT)
        assert result.file_description == "EX-99.3"

    def test_period_ending(self):
        """Verify period_ending extracts correctly."""
        result = SearchResult(raw=SAMPLE_HIT)
        assert result.period_ending == "2023-12-31"

    def test_url_construction(self):
        """Verify url is constructed from _id, CIK, and accession number."""
        result = SearchResult(raw=SAMPLE_HIT)
        expected = (
            "https://www.sec.gov/Archives/edgar/data/"
            "1418076/000119312524047930/d123456dex993.htm"
        )
        assert result.url == expected

    def test_url_construction_minimal(self):
        """Verify url works with a minimal hit."""
        result = SearchResult(raw=SAMPLE_HIT_MINIMAL)
        expected = (
            "https://www.sec.gov/Archives/edgar/data/"
            "320193/000032019324000123/aapl-20240928.htm"
        )
        assert result.url == expected

    def test_repr(self):
        """Verify __repr__ contains form, date, and company."""
        result = SearchResult(raw=SAMPLE_HIT)
        text = repr(result)
        assert "10-K" in text
        assert "2024-02-27" in text
        assert "SLR Investment Corp." in text

    def test_raw_access(self):
        """Verify raw attribute returns the original hit dict."""
        result = SearchResult(raw=SAMPLE_HIT)
        assert result.raw is SAMPLE_HIT

    def test_frozen(self):
        """Verify frozen dataclass prevents attribute assignment."""
        result = SearchResult(raw=SAMPLE_HIT)
        with pytest.raises(AttributeError):
            result.raw = {}


# ---------------------------------------------------------------------------
# SearchResult defaults / edge cases
# ---------------------------------------------------------------------------


class TestSearchResultDefaults:
    """Tests for SearchResult with missing or empty data."""

    def test_empty_source_defaults(self):
        """Verify all properties return sensible defaults for empty _source."""
        result = SearchResult(raw=SAMPLE_HIT_EMPTY_SOURCE)
        assert result.company_name == ""
        assert result.cik == ""
        assert result.form == ""
        assert result.filing_date == ""
        assert result.accession_number == ""
        assert result.file_type == ""
        assert result.file_description == ""
        assert result.period_ending == ""

    def test_empty_source_url(self):
        """Verify url returns empty string when data is missing."""
        result = SearchResult(raw=SAMPLE_HIT_EMPTY_SOURCE)
        assert result.url == ""

    def test_null_file_description(self):
        """Verify None file_description is coerced to empty string."""
        hit = {
            "_id": "0000320193-24-000123:file.htm",
            "_source": {
                "ciks": ["0000320193"],
                "file_description": None,
                "adsh": "0000320193-24-000123",
            },
        }
        result = SearchResult(raw=hit)
        assert result.file_description == ""

    def test_missing_source_key(self):
        """Verify properties work when _source key is entirely missing."""
        result = SearchResult(raw={"_id": "test:file.htm"})
        assert result.company_name == ""
        assert result.cik == ""

    def test_url_missing_filename(self):
        """Verify url returns empty when _id has no colon separator."""
        hit = {
            "_id": "0000320193-24-000123",
            "_source": {
                "ciks": ["0000320193"],
                "adsh": "0000320193-24-000123",
            },
        }
        result = SearchResult(raw=hit)
        assert result.url == ""


# ---------------------------------------------------------------------------
# Search service tests
# ---------------------------------------------------------------------------


class TestSearchService:
    """Tests for the Search service."""

    def test_repr(self):
        """Verify string representation."""
        session = MagicMock()
        service = Search(session=session)
        assert "Search" in repr(service)

    def test_full_text_search_basic(self):
        """Verify basic query passes correct parameters."""
        session = MagicMock()
        session.make_request.return_value = SAMPLE_EFTS_RESPONSE
        service = Search(session=session)

        result = service.full_text_search(q="revenue recognition")

        session.make_request.assert_called_once_with(
            method="get",
            endpoint="/LATEST/search-index",
            params={"q": "revenue recognition", "from": 0, "size": 100},
            base_url=EFTS_BASE_URL,
        )
        assert result == SAMPLE_EFTS_RESPONSE

    def test_full_text_search_with_form_types(self):
        """Verify form_types are joined with commas."""
        session = MagicMock()
        session.make_request.return_value = SAMPLE_EFTS_RESPONSE
        service = Search(session=session)

        service.full_text_search(q="test", form_types=["10-K", "10-Q"])

        call_params = session.make_request.call_args[1]["params"]
        assert call_params["forms"] == "10-K,10-Q"

    def test_full_text_search_with_date_range(self):
        """Verify date range parameters are set correctly."""
        session = MagicMock()
        session.make_request.return_value = SAMPLE_EFTS_RESPONSE
        service = Search(session=session)

        service.full_text_search(
            q="test", start_date="2024-01-01", end_date="2024-12-31"
        )

        call_params = session.make_request.call_args[1]["params"]
        assert call_params["dateRange"] == "custom"
        assert call_params["startdt"] == "2024-01-01"
        assert call_params["enddt"] == "2024-12-31"

    def test_full_text_search_with_start_date_only(self):
        """Verify only start_date triggers custom dateRange."""
        session = MagicMock()
        session.make_request.return_value = SAMPLE_EFTS_RESPONSE
        service = Search(session=session)

        service.full_text_search(q="test", start_date="2024-01-01")

        call_params = session.make_request.call_args[1]["params"]
        assert call_params["dateRange"] == "custom"
        assert call_params["startdt"] == "2024-01-01"
        assert "enddt" not in call_params

    def test_full_text_search_pagination(self):
        """Verify pagination params are passed through."""
        session = MagicMock()
        session.make_request.return_value = SAMPLE_EFTS_RESPONSE
        service = Search(session=session)

        service.full_text_search(q="test", start=50, size=25)

        call_params = session.make_request.call_args[1]["params"]
        assert call_params["from"] == 50
        assert call_params["size"] == 25

    def test_full_text_search_returns_none(self):
        """Verify None is returned when the API returns nothing."""
        session = MagicMock()
        session.make_request.return_value = None
        service = Search(session=session)

        result = service.full_text_search(q="nonexistent")
        assert result is None

    def test_full_text_search_no_optional_params(self):
        """Verify no forms or date params when not provided."""
        session = MagicMock()
        session.make_request.return_value = SAMPLE_EFTS_RESPONSE
        service = Search(session=session)

        service.full_text_search(q="test")

        call_params = session.make_request.call_args[1]["params"]
        assert "forms" not in call_params
        assert "dateRange" not in call_params
        assert "startdt" not in call_params
        assert "enddt" not in call_params

    def test_full_text_search_uses_efts_base_url(self):
        """Verify the EFTS base URL is passed to make_request."""
        session = MagicMock()
        session.make_request.return_value = SAMPLE_EFTS_RESPONSE
        service = Search(session=session)

        service.full_text_search(q="test")

        call_kwargs = session.make_request.call_args[1]
        assert call_kwargs["base_url"] == "https://efts.sec.gov"


# ---------------------------------------------------------------------------
# EdgarClient.search() integration tests
# ---------------------------------------------------------------------------


class TestClientSearch:
    """Tests for EdgarClient.search() convenience method."""

    @patch("edgar.session.EdgarSession")
    def test_search_returns_search_results(self, mock_session_cls):
        """Verify search() returns a list of SearchResult objects."""
        mock_session = MagicMock()
        mock_session.make_request.return_value = SAMPLE_EFTS_RESPONSE
        mock_session_cls.return_value = mock_session

        client = EdgarClient.__new__(EdgarClient)
        client.edgar_session = mock_session
        client._services = {}

        results = client.search(q="revenue recognition", form_types=["10-K"])

        assert len(results) == 2
        assert all(isinstance(r, SearchResult) for r in results)
        assert results[0].form == "10-K"
        assert results[1].company_name == "Apple Inc.  (AAPL)  (CIK 0000320193)"

    @patch("edgar.session.EdgarSession")
    def test_search_returns_empty_on_none(self, mock_session_cls):
        """Verify search() returns empty list when API returns None."""
        mock_session = MagicMock()
        mock_session.make_request.return_value = None
        mock_session_cls.return_value = mock_session

        client = EdgarClient.__new__(EdgarClient)
        client.edgar_session = mock_session
        client._services = {}

        results = client.search(q="nonexistent")
        assert results == []

    @patch("edgar.session.EdgarSession")
    def test_search_returns_empty_on_no_hits(self, mock_session_cls):
        """Verify search() returns empty list when response has no hits."""
        mock_session = MagicMock()
        mock_session.make_request.return_value = {"hits": {"total": {"value": 0}, "hits": []}}
        mock_session_cls.return_value = mock_session

        client = EdgarClient.__new__(EdgarClient)
        client.edgar_session = mock_session
        client._services = {}

        results = client.search(q="nonexistent")
        assert results == []

    @patch("edgar.session.EdgarSession")
    def test_search_passes_all_params(self, mock_session_cls):
        """Verify all parameters are forwarded to the Search service."""
        mock_session = MagicMock()
        mock_session.make_request.return_value = SAMPLE_EFTS_RESPONSE
        mock_session_cls.return_value = mock_session

        client = EdgarClient.__new__(EdgarClient)
        client.edgar_session = mock_session
        client._services = {}

        client.search(
            q="test",
            form_types=["10-K", "8-K"],
            start_date="2024-01-01",
            end_date="2024-12-31",
            start=10,
            size=50,
        )

        call_params = mock_session.make_request.call_args[1]["params"]
        assert call_params["q"] == "test"
        assert call_params["forms"] == "10-K,8-K"
        assert call_params["startdt"] == "2024-01-01"
        assert call_params["enddt"] == "2024-12-31"
        assert call_params["from"] == 10
        assert call_params["size"] == 50

    @patch("edgar.session.EdgarSession")
    def test_full_text_search_service_accessor(self, mock_session_cls):
        """Verify full_text_search() returns a cached Search service."""
        mock_session = MagicMock()
        mock_session_cls.return_value = mock_session

        client = EdgarClient.__new__(EdgarClient)
        client.edgar_session = mock_session
        client._services = {}

        service1 = client.full_text_search()
        service2 = client.full_text_search()

        assert isinstance(service1, Search)
        assert service1 is service2


# ---------------------------------------------------------------------------
# Session build_url base_url tests
# ---------------------------------------------------------------------------


class TestBuildUrlBaseUrl:
    """Tests for the base_url parameter on EdgarSession.build_url."""

    def test_base_url_overrides_default(self):
        """Verify base_url takes priority over use_api."""
        mock_client = MagicMock()
        mock_session = MagicMock()
        mock_session.resource = "https://www.sec.gov"
        mock_session.api_resource = "https://data.sec.gov"

        from edgar.session import EdgarSession

        session = EdgarSession.__new__(EdgarSession)
        session.resource = "https://www.sec.gov"
        session.api_resource = "https://data.sec.gov"

        url = session.build_url(
            "/LATEST/search-index", base_url="https://efts.sec.gov"
        )
        assert url == "https://efts.sec.gov/LATEST/search-index"

    def test_base_url_none_uses_default(self):
        """Verify None base_url falls through to normal logic."""
        from edgar.session import EdgarSession

        session = EdgarSession.__new__(EdgarSession)
        session.resource = "https://www.sec.gov"
        session.api_resource = "https://data.sec.gov"

        url = session.build_url("/test", base_url=None)
        assert url == "https://www.sec.gov/test"

    def test_base_url_none_with_use_api(self):
        """Verify use_api still works when base_url is None."""
        from edgar.session import EdgarSession

        session = EdgarSession.__new__(EdgarSession)
        session.resource = "https://www.sec.gov"
        session.api_resource = "https://data.sec.gov"

        url = session.build_url("/test", use_api=True, base_url=None)
        assert url == "https://data.sec.gov/test"
