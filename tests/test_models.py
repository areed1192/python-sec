"""Tests for the structured response models (Filing, CompanyInfo, Submission)."""

# pylint: disable=redefined-outer-name

from unittest.mock import MagicMock

import pytest

from edgar.models import Filing, CompanyInfo, Submission
from edgar.company import Company


# ---------------------------------------------------------------------------
# Sample raw data fixtures
# ---------------------------------------------------------------------------

SAMPLE_FILING_RAW = {
    "title": "10-K - Annual report [aapl-20210925.htm]",
    "link_href": "https://www.sec.gov/Archives/edgar/data/320193/0000320193-21-000105.txt",
    "summary": "Annual report for fiscal year ended September 25, 2021",
    "updated": "2021-10-29T00:00:00-05:00",
    "category_term": "10-K",
    "category_label": "form-type",
    "category_scheme": "https://www.sec.gov/",
    "id": "urn:tag:sec.gov,2021:accession-number=0000320193-21-000105",
}

SAMPLE_FILING_MINIMAL = {
    "title": "8-K",
}

SAMPLE_SUBMISSIONS_RAW = {
    "cik": "320193",
    "entityType": "operating",
    "sic": "3571",
    "sicDescription": "ELECTRONIC COMPUTERS",
    "name": "Apple Inc.",
    "tickers": ["AAPL"],
    "exchanges": ["NASDAQ"],
    "fiscalYearEnd": "0925",
    "filings": {
        "recent": {
            "accessionNumber": ["0000320193-21-000105", "0000320193-21-000088"],
            "filingDate": ["2021-10-29", "2021-07-28"],
            "reportDate": ["2021-09-25", "2021-06-26"],
            "form": ["10-K", "10-Q"],
            "primaryDocument": ["aapl-20210925.htm", "aapl-20210626.htm"],
            "primaryDocDescription": ["10-K", "10-Q"],
            "isXBRL": [1, 1],
            "isInlineXBRL": [1, 1],
            "size": [15000000, 12000000],
        },
        "files": [],
    },
}

SAMPLE_SUBMISSIONS_EMPTY_FILINGS = {
    "cik": "999999",
    "name": "Empty Corp",
    "filings": {"recent": {}},
}

SAMPLE_TICKERS_JSON = {
    "0": {"cik_str": 320193, "ticker": "AAPL", "title": "Apple Inc."},
}


# ---------------------------------------------------------------------------
# Filing model tests
# ---------------------------------------------------------------------------


class TestFiling:
    """Tests for the Filing dataclass model."""

    def test_properties_from_full_entry(self):
        """Verify all properties extract from a complete filing dict."""
        filing = Filing(raw=SAMPLE_FILING_RAW)
        assert filing.title == "10-K - Annual report [aapl-20210925.htm]"
        assert filing.form_type == "10-K"
        assert filing.url == "https://www.sec.gov/Archives/edgar/data/320193/0000320193-21-000105.txt"
        assert filing.summary == "Annual report for fiscal year ended September 25, 2021"
        assert filing.filing_date == "2021-10-29T00:00:00-05:00"
        assert filing.accession_number == "0000320193-21-000105"

    def test_properties_default_to_empty(self):
        """Verify missing keys default to empty strings."""
        filing = Filing(raw=SAMPLE_FILING_MINIMAL)
        assert filing.title == "8-K"
        assert filing.form_type == ""
        assert filing.url == ""
        assert filing.summary == ""
        assert filing.filing_date == ""

    def test_accession_number_without_prefix(self):
        """Verify accession_number falls back to full ID if no prefix."""
        filing = Filing(raw={"id": "some-other-format"})
        assert filing.accession_number == "some-other-format"

    def test_raw_attribute(self):
        """Verify the raw dict is accessible."""
        filing = Filing(raw=SAMPLE_FILING_RAW)
        assert filing.raw is SAMPLE_FILING_RAW
        assert filing.raw["category_term"] == "10-K"

    def test_repr(self):
        """Verify repr contains key fields."""
        filing = Filing(raw=SAMPLE_FILING_RAW)
        result = repr(filing)
        assert "10-K" in result
        assert "2021-10-29" in result

    def test_frozen(self):
        """Verify the dataclass is immutable."""
        filing = Filing(raw=SAMPLE_FILING_RAW)
        with pytest.raises(AttributeError):
            filing.raw = {}


# ---------------------------------------------------------------------------
# CompanyInfo model tests
# ---------------------------------------------------------------------------


class TestCompanyInfo:
    """Tests for the CompanyInfo dataclass model."""

    def test_properties(self):
        """Verify all properties extract from a complete submissions dict."""
        info = CompanyInfo(raw=SAMPLE_SUBMISSIONS_RAW)
        assert info.cik == "320193"
        assert info.name == "Apple Inc."
        assert info.entity_type == "operating"
        assert info.sic == "3571"
        assert info.sic_description == "ELECTRONIC COMPUTERS"
        assert info.tickers == ["AAPL"]
        assert info.exchanges == ["NASDAQ"]
        assert info.fiscal_year_end == "0925"

    def test_recent_filings_as_dicts(self):
        """Verify recent_filings converts column-oriented data to row dicts."""
        info = CompanyInfo(raw=SAMPLE_SUBMISSIONS_RAW)
        filings = info.recent_filings
        assert len(filings) == 2
        assert filings[0]["form"] == "10-K"
        assert filings[1]["form"] == "10-Q"
        assert filings[0]["filingDate"] == "2021-10-29"

    def test_recent_submissions_as_models(self):
        """Verify recent_submissions returns Submission objects."""
        info = CompanyInfo(raw=SAMPLE_SUBMISSIONS_RAW)
        submissions = info.recent_submissions
        assert len(submissions) == 2
        assert isinstance(submissions[0], Submission)
        assert submissions[0].form == "10-K"
        assert submissions[1].form == "10-Q"

    def test_empty_recent_filings(self):
        """Verify empty filings return empty lists."""
        info = CompanyInfo(raw=SAMPLE_SUBMISSIONS_EMPTY_FILINGS)
        assert info.recent_filings == []
        assert info.recent_submissions == []

    def test_missing_filings_key(self):
        """Verify missing 'filings' key returns empty lists."""
        info = CompanyInfo(raw={"cik": "1", "name": "Test"})
        assert info.recent_filings == []

    def test_raw_attribute(self):
        """Verify the raw dict is accessible."""
        info = CompanyInfo(raw=SAMPLE_SUBMISSIONS_RAW)
        assert info.raw is SAMPLE_SUBMISSIONS_RAW

    def test_repr(self):
        """Verify repr contains key fields."""
        result = repr(CompanyInfo(raw=SAMPLE_SUBMISSIONS_RAW))
        assert "Apple Inc." in result
        assert "320193" in result
        assert "AAPL" in result

    def test_defaults_for_missing_keys(self):
        """Verify properties default gracefully for minimal dicts."""
        info = CompanyInfo(raw={})
        assert info.cik == ""
        assert info.name == ""
        assert info.entity_type == ""
        assert info.tickers == []
        assert info.exchanges == []


# ---------------------------------------------------------------------------
# Submission model tests
# ---------------------------------------------------------------------------


class TestSubmission:
    """Tests for the Submission dataclass model."""

    def test_properties(self):
        """Verify all properties extract from a submission row dict."""
        row = {
            "accessionNumber": "0000320193-21-000105",
            "form": "10-K",
            "filingDate": "2021-10-29",
            "reportDate": "2021-09-25",
            "primaryDocument": "aapl-20210925.htm",
            "primaryDocDescription": "10-K",
            "isXBRL": 1,
            "isInlineXBRL": 1,
            "size": 15000000,
        }
        sub = Submission(raw=row)
        assert sub.accession_number == "0000320193-21-000105"
        assert sub.form == "10-K"
        assert sub.filing_date == "2021-10-29"
        assert sub.report_date == "2021-09-25"
        assert sub.primary_document == "aapl-20210925.htm"
        assert sub.primary_doc_description == "10-K"
        assert sub.is_xbrl is True
        assert sub.is_inline_xbrl is True
        assert sub.size == 15000000

    def test_boolean_conversion(self):
        """Verify is_xbrl handles 0 and 1 correctly."""
        assert Submission(raw={"isXBRL": 0}).is_xbrl is False
        assert Submission(raw={"isXBRL": 1}).is_xbrl is True

    def test_defaults_for_missing_keys(self):
        """Verify properties default gracefully for empty dicts."""
        sub = Submission(raw={})
        assert sub.accession_number == ""
        assert sub.form == ""
        assert sub.filing_date == ""
        assert sub.is_xbrl is False
        assert sub.size == 0

    def test_raw_attribute(self):
        """Verify the raw dict is accessible."""
        row = {"form": "8-K", "filingDate": "2021-06-15"}
        sub = Submission(raw=row)
        assert sub.raw is row

    def test_repr(self):
        """Verify repr contains key fields."""
        sub = Submission(raw={"form": "10-Q", "filingDate": "2021-07-28", "accessionNumber": "123"})
        result = repr(sub)
        assert "10-Q" in result
        assert "2021-07-28" in result


# ---------------------------------------------------------------------------
# Company.get_filings() / get_info() integration tests
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_tickers():
    """Return a mock Tickers service."""
    tickers = MagicMock()
    tickers.resolve_ticker.return_value = "0000320193"
    tickers.resolve_cik.return_value = [
        {"cik_str": 320193, "ticker": "AAPL", "title": "Apple Inc."}
    ]
    return tickers


class TestCompanyGetFilings:
    """Tests for Company.get_filings() returning Filing models."""

    def test_get_filings_returns_filing_objects(self, mock_tickers):
        """Verify get_filings() returns Filing model instances."""
        session = MagicMock()
        session.make_request.return_value = "<feed/>"
        session.edgar_parser = MagicMock()
        session.edgar_parser.parse_entries.return_value = [
            SAMPLE_FILING_RAW,
            SAMPLE_FILING_MINIMAL,
        ]
        session.edgar_utilities = MagicMock()
        session.fetch_page = MagicMock()

        company = Company(identifier="AAPL", session=session, tickers_service=mock_tickers)
        filings = company.get_filings()

        assert len(filings) == 2
        assert isinstance(filings[0], Filing)
        assert filings[0].form_type == "10-K"
        assert isinstance(filings[1], Filing)

    def test_get_filings_with_form_filter(self, mock_tickers):
        """Verify get_filings(form='10-K') filters correctly."""
        session = MagicMock()
        session.make_request.return_value = "<feed/>"
        session.edgar_parser = MagicMock()
        session.edgar_parser.parse_entries.return_value = [SAMPLE_FILING_RAW]
        session.edgar_utilities = MagicMock()
        session.fetch_page = MagicMock()

        company = Company(identifier="AAPL", session=session, tickers_service=mock_tickers)
        filings = company.get_filings(form="10-K")

        assert len(filings) == 1
        assert filings[0].form_type == "10-K"


class TestCompanyGetInfo:
    """Tests for Company.get_info() returning CompanyInfo model."""

    def test_get_info_returns_company_info(self, mock_tickers):
        """Verify get_info() returns a CompanyInfo model."""
        session = MagicMock()
        session.make_request.return_value = SAMPLE_SUBMISSIONS_RAW
        session.edgar_utilities = MagicMock()

        company = Company(identifier="AAPL", session=session, tickers_service=mock_tickers)
        info = company.get_info()

        assert isinstance(info, CompanyInfo)
        assert info.name == "Apple Inc."
        assert info.cik == "320193"

    def test_get_info_returns_none_when_no_data(self, mock_tickers):
        """Verify get_info() returns None when submissions returns None."""
        session = MagicMock()
        session.make_request.return_value = None
        session.edgar_utilities = MagicMock()

        company = Company(identifier="AAPL", session=session, tickers_service=mock_tickers)
        info = company.get_info()

        assert info is None
