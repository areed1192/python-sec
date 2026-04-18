"""Tests for pandas integration — to_dataframe() and Facts.to_dataframe()."""

# pylint: disable=redefined-outer-name

from unittest.mock import patch

import pytest

pd = pytest.importorskip("pandas", reason="pandas required for DataFrame tests")

from edgar.models import (
    Fact,
    Facts,
    Filing,
    CompanyInfo,
    SearchResult,
    Submission,
    to_dataframe,
    _require_pandas,
)


# ---------------------------------------------------------------------------
# Sample raw data fixtures
# ---------------------------------------------------------------------------

SAMPLE_FACT_RAW_1 = {
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

SAMPLE_FACT_RAW_2 = {
    "start": "2021-09-26",
    "end": "2022-09-24",
    "val": 394328000000,
    "accn": "0000320193-22-000108",
    "fy": 2022,
    "fp": "FY",
    "form": "10-K",
    "filed": "2022-10-28",
    "frame": "CY2022",
}

SAMPLE_FILING_RAW = {
    "title": "10-K - Annual report",
    "link_href": "https://www.sec.gov/Archives/edgar/data/320193/0000320193-21-000105.txt",
    "summary": "Annual report for fiscal year ended September 25, 2021",
    "updated": "2021-10-29T00:00:00-05:00",
    "category_term": "10-K",
    "id": "urn:tag:sec.gov,2021:accession-number=0000320193-21-000105",
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

SAMPLE_COMPANY_FACTS = {
    "cik": 320193,
    "entityName": "Apple Inc.",
    "facts": {
        "us-gaap": {
            "Revenue": {
                "label": "Revenue",
                "description": "Amount of revenue recognized.",
                "units": {
                    "USD": [SAMPLE_FACT_RAW_2, SAMPLE_FACT_RAW_1],
                },
            },
        },
    },
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
    "filings": {"recent": {}},
}


# ---------------------------------------------------------------------------
# to_dataframe() — standalone function tests
# ---------------------------------------------------------------------------


class TestToDataFrame:
    """Tests for the standalone to_dataframe() function."""

    def test_facts_list(self):
        """Verify to_dataframe converts a list of Fact objects."""
        facts = [Fact(raw=SAMPLE_FACT_RAW_1), Fact(raw=SAMPLE_FACT_RAW_2)]
        df = to_dataframe(facts)

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 2
        assert "end" in df.columns
        assert "value" in df.columns
        assert "form" in df.columns
        assert "filed" in df.columns
        assert "fiscal_year" in df.columns

    def test_fact_values_correct(self):
        """Verify DataFrame values match property values."""
        facts = [Fact(raw=SAMPLE_FACT_RAW_1)]
        df = to_dataframe(facts)

        row = df.iloc[0]
        assert row["end"] == "2023-09-30"
        assert row["value"] == 383285000000
        assert row["form"] == "10-K"
        assert row["fiscal_year"] == 2023
        assert row["fiscal_period"] == "FY"

    def test_filings_list(self):
        """Verify to_dataframe converts a list of Filing objects."""
        filings = [Filing(raw=SAMPLE_FILING_RAW)]
        df = to_dataframe(filings)

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 1
        assert "form_type" in df.columns
        assert "filing_date" in df.columns
        assert "url" in df.columns

    def test_submissions_list(self):
        """Verify to_dataframe converts a list of Submission objects."""
        subs = [Submission(raw=SAMPLE_SUBMISSION_RAW)]
        df = to_dataframe(subs)

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 1
        assert "form" in df.columns
        assert "filing_date" in df.columns
        assert "accession_number" in df.columns

    def test_search_results_list(self):
        """Verify to_dataframe converts a list of SearchResult objects."""
        results = [SearchResult(raw=SAMPLE_SEARCH_HIT)]
        df = to_dataframe(results)

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 1
        assert "company_name" in df.columns
        assert "form" in df.columns
        assert "url" in df.columns

    def test_company_info_list(self):
        """Verify to_dataframe converts a list of CompanyInfo objects."""
        infos = [CompanyInfo(raw=SAMPLE_COMPANY_INFO_RAW)]
        df = to_dataframe(infos)

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 1
        assert "name" in df.columns
        assert "cik" in df.columns

    def test_empty_list(self):
        """Verify to_dataframe returns an empty DataFrame for an empty list."""
        df = to_dataframe([])

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 0

    def test_excludes_raw_column(self):
        """Verify the 'raw' attribute is not included as a column."""
        facts = [Fact(raw=SAMPLE_FACT_RAW_1)]
        df = to_dataframe(facts)

        assert "raw" not in df.columns

    def test_excludes_private_properties(self):
        """Verify private properties (e.g. _source) are excluded."""
        results = [SearchResult(raw=SAMPLE_SEARCH_HIT)]
        df = to_dataframe(results)

        assert "_source" not in df.columns

    def test_multiple_rows(self):
        """Verify multiple items produce multiple rows."""
        facts = [Fact(raw=SAMPLE_FACT_RAW_1), Fact(raw=SAMPLE_FACT_RAW_2)]
        df = to_dataframe(facts)

        assert len(df) == 2
        assert df.iloc[0]["end"] == "2023-09-30"
        assert df.iloc[1]["end"] == "2022-09-24"


# ---------------------------------------------------------------------------
# Facts.to_dataframe() method tests
# ---------------------------------------------------------------------------


class TestFactsToDataFrame:
    """Tests for the Facts.to_dataframe() method."""

    def test_returns_dataframe(self):
        """Verify Facts.to_dataframe returns a DataFrame."""
        facts = Facts(raw=SAMPLE_COMPANY_FACTS)
        df = facts.to_dataframe("us-gaap", "Revenue")

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 2

    def test_has_expected_columns(self):
        """Verify DataFrame has Fact property columns."""
        facts = Facts(raw=SAMPLE_COMPANY_FACTS)
        df = facts.to_dataframe("us-gaap", "Revenue")

        assert "end" in df.columns
        assert "value" in df.columns
        assert "form" in df.columns
        assert "fiscal_year" in df.columns

    def test_with_unit_filter(self):
        """Verify unit parameter is forwarded."""
        facts = Facts(raw=SAMPLE_COMPANY_FACTS)
        df = facts.to_dataframe("us-gaap", "Revenue", unit="USD")

        assert len(df) == 2

    def test_nonexistent_concept_returns_empty(self):
        """Verify empty DataFrame for a concept that doesn't exist."""
        facts = Facts(raw=SAMPLE_COMPANY_FACTS)
        df = facts.to_dataframe("us-gaap", "NonexistentConcept")

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 0

    def test_nonexistent_unit_returns_empty(self):
        """Verify empty DataFrame when unit doesn't match."""
        facts = Facts(raw=SAMPLE_COMPANY_FACTS)
        df = facts.to_dataframe("us-gaap", "Revenue", unit="EUR")

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 0

    def test_values_match_facts(self):
        """Verify DataFrame values match underlying Fact objects."""
        facts_obj = Facts(raw=SAMPLE_COMPANY_FACTS)
        df = facts_obj.to_dataframe("us-gaap", "Revenue", unit="USD")
        fact_list = facts_obj.get("us-gaap", "Revenue", unit="USD")

        for i, fact in enumerate(fact_list):
            assert df.iloc[i]["end"] == fact.end
            assert df.iloc[i]["value"] == fact.value


# ---------------------------------------------------------------------------
# Graceful error when pandas is missing
# ---------------------------------------------------------------------------


class TestRequirePandas:
    """Tests for the _require_pandas helper and graceful error message."""

    def test_returns_pandas_when_available(self):
        """Verify _require_pandas returns the pandas module normally."""
        result = _require_pandas()
        assert result is pd

    def test_raises_import_error_with_message(self):
        """Verify helpful error message when pandas is not installed."""
        with patch.dict("sys.modules", {"pandas": None}):
            with pytest.raises(ImportError, match="pip install python-sec\\[pandas\\]"):
                _require_pandas()

    def test_to_dataframe_raises_when_pandas_missing(self):
        """Verify to_dataframe() raises helpful error without pandas."""
        with patch.dict("sys.modules", {"pandas": None}):
            with pytest.raises(ImportError, match="pip install python-sec\\[pandas\\]"):
                to_dataframe([Fact(raw=SAMPLE_FACT_RAW_1)])

    def test_facts_to_dataframe_raises_when_pandas_missing(self):
        """Verify Facts.to_dataframe() raises helpful error without pandas."""
        facts = Facts(raw=SAMPLE_COMPANY_FACTS)
        with patch.dict("sys.modules", {"pandas": None}):
            with pytest.raises(ImportError, match="pip install python-sec\\[pandas\\]"):
                facts.to_dataframe("us-gaap", "Revenue")
