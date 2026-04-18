"""Tests for _repr_html_() Jupyter/REPL rendering on all response models."""

# pylint: disable=redefined-outer-name
# pylint: disable=protected-access

import pytest

from edgar.models import (
    CompanyInfo,
    Fact,
    Facts,
    Filing,
    SearchResult,
    Submission,
)


# ---------------------------------------------------------------------------
# Sample raw data fixtures
# ---------------------------------------------------------------------------

SAMPLE_FILING_RAW = {
    "title": "10-K - Annual report [aapl-20210925.htm]",
    "link_href": "https://www.sec.gov/Archives/edgar/data/320193/0000320193-21-000105.txt",
    "summary": "Annual report for fiscal year ended September 25, 2021",
    "updated": "2021-10-29T00:00:00-05:00",
    "category_term": "10-K",
    "id": "urn:tag:sec.gov,2021:accession-number=0000320193-21-000105",
}

SAMPLE_COMPANY_INFO_RAW = {
    "cik": "320193",
    "name": "Apple Inc.",
    "entityType": "operating",
    "sic": "3571",
    "sicDescription": "ELECTRONIC COMPUTERS",
    "tickers": ["AAPL"],
    "exchanges": ["NASDAQ"],
    "fiscalYearEnd": "0925",
    "filings": {
        "recent": {
            "accessionNumber": ["0000320193-24-000123"],
            "form": ["10-K"],
            "filingDate": ["2024-11-01"],
            "reportDate": ["2024-09-28"],
            "primaryDocument": ["aapl-20240928.htm"],
            "primaryDocDescription": ["10-K"],
            "isXBRL": [1],
            "isInlineXBRL": [1],
            "size": [15000000],
        }
    },
}

SAMPLE_SUBMISSION_RAW = {
    "accessionNumber": "0000320193-23-000106",
    "form": "10-K",
    "filingDate": "2023-11-03",
    "reportDate": "2023-09-30",
    "primaryDocument": "aapl-20230930.htm",
    "primaryDocDescription": "10-K",
    "isXBRL": 1,
    "isInlineXBRL": 1,
    "size": 15000000,
}

SAMPLE_FACT_RAW = {
    "start": "2022-09-25",
    "end": "2023-09-30",
    "val": 383285000000,
    "accn": "0000320193-23-000106",
    "fy": 2023,
    "fp": "FY",
    "form": "10-K",
    "filed": "2023-11-03",
    "frame": "CY2023",
}

SAMPLE_COMPANY_FACTS = {
    "cik": 320193,
    "entityName": "Apple Inc.",
    "facts": {
        "dei": {
            "EntityCommonStockSharesOutstanding": {
                "label": "Shares Outstanding",
                "units": {"shares": []},
            }
        },
        "us-gaap": {
            "Revenue": {
                "label": "Revenue",
                "units": {"USD": [SAMPLE_FACT_RAW]},
            },
            "AccountsPayable": {
                "label": "Accounts Payable",
                "units": {"USD": []},
            },
        },
    },
}

SAMPLE_SEARCH_HIT = {
    "_id": "0001193125-24-047930:d123456dex993.htm",
    "_score": 8.5,
    "_source": {
        "ciks": ["0001418076"],
        "display_names": ["SLR Investment Corp.  (SLRC)  (CIK 0001418076)"],
        "file_date": "2024-02-27",
        "form": "10-K",
        "adsh": "0001193125-24-047930",
        "file_type": "EX-99.3",
        "file_description": "EX-99.3",
        "period_ending": "2023-12-31",
    },
}


# ---------------------------------------------------------------------------
# Filing._repr_html_() tests
# ---------------------------------------------------------------------------


class TestFilingReprHtml:
    """Tests for Filing._repr_html_()."""

    def test_returns_html_string(self):
        """Verify _repr_html_ returns an HTML string."""
        html = Filing(raw=SAMPLE_FILING_RAW)._repr_html_()
        assert isinstance(html, str)
        assert "<table" in html

    def test_contains_form_type(self):
        """Verify HTML contains the form type."""
        html = Filing(raw=SAMPLE_FILING_RAW)._repr_html_()
        assert "10-K" in html

    def test_contains_filing_date(self):
        """Verify HTML contains the filing date."""
        html = Filing(raw=SAMPLE_FILING_RAW)._repr_html_()
        assert "2021-10-29" in html

    def test_contains_url_as_link(self):
        """Verify HTML renders the URL as a clickable link."""
        html = Filing(raw=SAMPLE_FILING_RAW)._repr_html_()
        assert "<a href=" in html
        assert "0000320193-21-000105" in html

    def test_contains_caption(self):
        """Verify HTML includes a caption."""
        html = Filing(raw=SAMPLE_FILING_RAW)._repr_html_()
        assert "Filing" in html

    def test_empty_url_no_link(self):
        """Verify no anchor tag when URL is empty."""
        html = Filing(raw={"title": "test"})._repr_html_()
        assert "<a href=" not in html

    def test_html_escapes_values(self):
        """Verify special characters are HTML-escaped."""
        raw = {**SAMPLE_FILING_RAW, "title": '<script>alert("xss")</script>'}
        html = Filing(raw=raw)._repr_html_()
        assert "<script>" not in html
        assert "&lt;script&gt;" in html


# ---------------------------------------------------------------------------
# CompanyInfo._repr_html_() tests
# ---------------------------------------------------------------------------


class TestCompanyInfoReprHtml:
    """Tests for CompanyInfo._repr_html_()."""

    def test_returns_html_string(self):
        """Verify _repr_html_ returns an HTML string."""
        html = CompanyInfo(raw=SAMPLE_COMPANY_INFO_RAW)._repr_html_()
        assert isinstance(html, str)
        assert "<table" in html

    def test_contains_company_name(self):
        """Verify HTML contains the company name."""
        html = CompanyInfo(raw=SAMPLE_COMPANY_INFO_RAW)._repr_html_()
        assert "Apple Inc." in html

    def test_contains_ticker(self):
        """Verify HTML contains the ticker symbol."""
        html = CompanyInfo(raw=SAMPLE_COMPANY_INFO_RAW)._repr_html_()
        assert "AAPL" in html

    def test_contains_sic_with_description(self):
        """Verify HTML contains the SIC code and description."""
        html = CompanyInfo(raw=SAMPLE_COMPANY_INFO_RAW)._repr_html_()
        assert "3571" in html
        assert "ELECTRONIC COMPUTERS" in html

    def test_contains_recent_filings_table(self):
        """Verify HTML includes a recent filings sub-table."""
        html = CompanyInfo(raw=SAMPLE_COMPANY_INFO_RAW)._repr_html_()
        assert "Recent Filings" in html
        assert "0000320193-24-000123" in html

    def test_no_filings_table_when_empty(self):
        """Verify no filings table when recent filings are empty."""
        raw = {**SAMPLE_COMPANY_INFO_RAW, "filings": {"recent": {}}}
        html = CompanyInfo(raw=raw)._repr_html_()
        assert "Recent Filings" not in html


# ---------------------------------------------------------------------------
# Submission._repr_html_() tests
# ---------------------------------------------------------------------------


class TestSubmissionReprHtml:
    """Tests for Submission._repr_html_()."""

    def test_returns_html_string(self):
        """Verify _repr_html_ returns an HTML string."""
        html = Submission(raw=SAMPLE_SUBMISSION_RAW)._repr_html_()
        assert isinstance(html, str)
        assert "<table" in html

    def test_contains_form(self):
        """Verify HTML contains the form type."""
        html = Submission(raw=SAMPLE_SUBMISSION_RAW)._repr_html_()
        assert "10-K" in html

    def test_contains_filing_date(self):
        """Verify HTML contains the filing date."""
        html = Submission(raw=SAMPLE_SUBMISSION_RAW)._repr_html_()
        assert "2023-11-03" in html

    def test_xbrl_shows_yes(self):
        """Verify XBRL field shows Yes."""
        html = Submission(raw=SAMPLE_SUBMISSION_RAW)._repr_html_()
        assert "Yes" in html

    def test_size_formatted(self):
        """Verify size is formatted with commas."""
        html = Submission(raw=SAMPLE_SUBMISSION_RAW)._repr_html_()
        assert "15,000,000" in html


# ---------------------------------------------------------------------------
# Fact._repr_html_() tests
# ---------------------------------------------------------------------------


class TestFactReprHtml:
    """Tests for Fact._repr_html_()."""

    def test_returns_html_string(self):
        """Verify _repr_html_ returns an HTML string."""
        html = Fact(raw=SAMPLE_FACT_RAW)._repr_html_()
        assert isinstance(html, str)
        assert "<table" in html

    def test_contains_end_date(self):
        """Verify HTML contains the end date."""
        html = Fact(raw=SAMPLE_FACT_RAW)._repr_html_()
        assert "2023-09-30" in html

    def test_value_formatted(self):
        """Verify numeric value is formatted with commas."""
        html = Fact(raw=SAMPLE_FACT_RAW)._repr_html_()
        assert "383,285,000,000" in html

    def test_contains_fiscal_year(self):
        """Verify HTML contains the fiscal year."""
        html = Fact(raw=SAMPLE_FACT_RAW)._repr_html_()
        assert "2023" in html

    def test_contains_form(self):
        """Verify HTML contains the form type."""
        html = Fact(raw=SAMPLE_FACT_RAW)._repr_html_()
        assert "10-K" in html

    def test_none_value_handled(self):
        """Verify None value renders without error."""
        html = Fact(raw={})._repr_html_()
        assert "None" in html


# ---------------------------------------------------------------------------
# Facts._repr_html_() tests
# ---------------------------------------------------------------------------


class TestFactsReprHtml:
    """Tests for Facts._repr_html_()."""

    def test_returns_html_string(self):
        """Verify _repr_html_ returns an HTML string."""
        html = Facts(raw=SAMPLE_COMPANY_FACTS)._repr_html_()
        assert isinstance(html, str)
        assert "<table" in html

    def test_contains_entity_name(self):
        """Verify HTML contains the entity name."""
        html = Facts(raw=SAMPLE_COMPANY_FACTS)._repr_html_()
        assert "Apple Inc." in html

    def test_contains_taxonomy_summary(self):
        """Verify HTML includes the taxonomy summary table."""
        html = Facts(raw=SAMPLE_COMPANY_FACTS)._repr_html_()
        assert "Taxonomy Summary" in html
        assert "dei" in html
        assert "us-gaap" in html

    def test_concept_counts(self):
        """Verify taxonomy table shows concept counts."""
        html = Facts(raw=SAMPLE_COMPANY_FACTS)._repr_html_()
        # dei has 1 concept, us-gaap has 2
        assert ">1<" in html
        assert ">2<" in html

    def test_empty_facts(self):
        """Verify empty facts renders without error."""
        html = Facts(raw={})._repr_html_()
        assert "<table" in html


# ---------------------------------------------------------------------------
# SearchResult._repr_html_() tests
# ---------------------------------------------------------------------------


class TestSearchResultReprHtml:
    """Tests for SearchResult._repr_html_()."""

    def test_returns_html_string(self):
        """Verify _repr_html_ returns an HTML string."""
        html = SearchResult(raw=SAMPLE_SEARCH_HIT)._repr_html_()
        assert isinstance(html, str)
        assert "<table" in html

    def test_contains_company_name(self):
        """Verify HTML contains the company name."""
        html = SearchResult(raw=SAMPLE_SEARCH_HIT)._repr_html_()
        assert "SLR Investment Corp." in html

    def test_contains_form(self):
        """Verify HTML contains the form type."""
        html = SearchResult(raw=SAMPLE_SEARCH_HIT)._repr_html_()
        assert "10-K" in html

    def test_contains_url_as_link(self):
        """Verify HTML renders the filing URL as a link."""
        html = SearchResult(raw=SAMPLE_SEARCH_HIT)._repr_html_()
        assert "<a href=" in html
        assert "sec.gov" in html

    def test_empty_hit_no_link(self):
        """Verify no anchor tag when URL cannot be constructed."""
        html = SearchResult(raw={"_id": "", "_source": {}})._repr_html_()
        assert "<a href=" not in html

    def test_html_escapes_company_name(self):
        """Verify special characters in company names are escaped."""
        hit = {
            "_id": "0001-24-000001:f.htm",
            "_source": {
                "ciks": ["0000000001"],
                "display_names": ['<b>Evil & "Corp"</b>'],
                "form": "10-K",
                "adsh": "0001-24-000001",
                "file_date": "2024-01-01",
            },
        }
        html = SearchResult(raw=hit)._repr_html_()
        assert "<b>" not in html
        assert "&lt;b&gt;" in html
        assert "&amp;" in html
