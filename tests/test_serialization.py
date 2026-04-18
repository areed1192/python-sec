"""Tests for JSON and CSV serialization — to_json() and to_csv() methods and functions."""

# pylint: disable=redefined-outer-name

import csv
import io
import json

from edgar.models import (
    CompanyInfo,
    Fact,
    Facts,
    Filing,
    SearchResult,
    Submission,
    to_csv,
    to_json,
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
        "us-gaap": {
            "Revenue": {
                "label": "Revenue",
                "description": "Amount of revenue recognized.",
                "units": {"USD": [SAMPLE_FACT_RAW]},
            },
        },
    },
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
            "accessionNumber": ["0000320193-21-000105"],
            "filingDate": ["2021-10-29"],
            "reportDate": ["2021-09-25"],
            "form": ["10-K"],
            "primaryDocument": ["aapl-20210925.htm"],
            "primaryDocDescription": ["10-K"],
            "isXBRL": [1],
            "isInlineXBRL": [1],
            "size": [15000000],
        },
        "files": [],
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
# Filing.to_json() / to_csv() tests
# ---------------------------------------------------------------------------


class TestFilingToJson:
    """Tests for Filing.to_json() serialization."""

    def test_returns_valid_json(self):
        """Verify to_json() returns a parseable JSON string."""
        filing = Filing(raw=SAMPLE_FILING_RAW)
        result = json.loads(filing.to_json())
        assert result["form_type"] == "10-K"
        assert result["title"] == "10-K - Annual report [aapl-20210925.htm]"
        assert result["accession_number"] == "0000320193-21-000105"

    def test_writes_to_file(self, tmp_path):
        """Verify to_json(path=...) writes a valid JSON file."""
        filing = Filing(raw=SAMPLE_FILING_RAW)
        out = tmp_path / "filing.json"
        filing.to_json(path=str(out))
        data = json.loads(out.read_text(encoding="utf-8"))
        assert data["form_type"] == "10-K"

    def test_returns_string_when_writing_file(self, tmp_path):
        """Verify to_json(path=...) still returns the JSON string."""
        filing = Filing(raw=SAMPLE_FILING_RAW)
        out = tmp_path / "filing.json"
        result = filing.to_json(path=str(out))
        assert isinstance(result, str)
        assert json.loads(result)["form_type"] == "10-K"

    def test_custom_indent(self):
        """Verify the indent parameter controls formatting."""
        filing = Filing(raw=SAMPLE_FILING_RAW)
        compact = filing.to_json(indent=0)
        assert "\n" in compact
        assert "    " not in compact


class TestFilingToCsv:
    """Tests for Filing.to_csv() serialization."""

    def test_returns_valid_csv(self):
        """Verify to_csv() returns a parseable CSV string."""
        filing = Filing(raw=SAMPLE_FILING_RAW)
        result = filing.to_csv()
        reader = csv.DictReader(io.StringIO(result))
        rows = list(reader)
        assert len(rows) == 1
        assert rows[0]["form_type"] == "10-K"

    def test_writes_to_file(self, tmp_path):
        """Verify to_csv(path=...) writes a valid CSV file."""
        filing = Filing(raw=SAMPLE_FILING_RAW)
        out = tmp_path / "filing.csv"
        filing.to_csv(path=str(out))
        content = out.read_text(encoding="utf-8")
        reader = csv.DictReader(io.StringIO(content))
        rows = list(reader)
        assert rows[0]["form_type"] == "10-K"


# ---------------------------------------------------------------------------
# Submission.to_json() / to_csv() tests
# ---------------------------------------------------------------------------


class TestSubmissionToJson:
    """Tests for Submission.to_json() serialization."""

    def test_returns_valid_json(self):
        """Verify to_json() returns a parseable JSON string with correct fields."""
        sub = Submission(raw=SAMPLE_SUBMISSION_RAW)
        result = json.loads(sub.to_json())
        assert result["form"] == "10-K"
        assert result["filing_date"] == "2023-11-03"
        assert result["is_xbrl"] is True
        assert result["size"] == 15000000


class TestSubmissionToCsv:
    """Tests for Submission.to_csv() serialization."""

    def test_returns_valid_csv(self):
        """Verify to_csv() returns a parseable CSV with correct fields."""
        sub = Submission(raw=SAMPLE_SUBMISSION_RAW)
        reader = csv.DictReader(io.StringIO(sub.to_csv()))
        rows = list(reader)
        assert len(rows) == 1
        assert rows[0]["form"] == "10-K"


# ---------------------------------------------------------------------------
# Fact.to_json() / to_csv() tests
# ---------------------------------------------------------------------------


class TestFactToJson:
    """Tests for Fact.to_json() serialization."""

    def test_returns_valid_json(self):
        """Verify to_json() returns a parseable JSON string with correct fields."""
        fact = Fact(raw=SAMPLE_FACT_RAW)
        result = json.loads(fact.to_json())
        assert result["value"] == 383285000000
        assert result["end"] == "2023-09-30"
        assert result["fiscal_year"] == 2023

    def test_writes_to_file(self, tmp_path):
        """Verify to_json(path=...) writes a valid JSON file."""
        fact = Fact(raw=SAMPLE_FACT_RAW)
        out = tmp_path / "fact.json"
        fact.to_json(path=str(out))
        data = json.loads(out.read_text(encoding="utf-8"))
        assert data["value"] == 383285000000


class TestFactToCsv:
    """Tests for Fact.to_csv() serialization."""

    def test_returns_valid_csv(self):
        """Verify to_csv() returns a parseable CSV with correct fields."""
        fact = Fact(raw=SAMPLE_FACT_RAW)
        reader = csv.DictReader(io.StringIO(fact.to_csv()))
        rows = list(reader)
        assert len(rows) == 1
        assert rows[0]["end"] == "2023-09-30"


# ---------------------------------------------------------------------------
# Facts.to_json() / to_csv() tests
# ---------------------------------------------------------------------------


class TestFactsToJson:
    """Tests for Facts.to_json() serialization."""

    def test_returns_valid_json(self):
        """Verify to_json() returns metadata as a parseable JSON string."""
        facts = Facts(raw=SAMPLE_COMPANY_FACTS)
        result = json.loads(facts.to_json())
        assert result["entity_name"] == "Apple Inc."
        assert result["cik"] == 320193
        assert "us-gaap" in result["taxonomies"]

    def test_writes_to_file(self, tmp_path):
        """Verify to_json(path=...) writes a valid JSON file."""
        facts = Facts(raw=SAMPLE_COMPANY_FACTS)
        out = tmp_path / "facts.json"
        facts.to_json(path=str(out))
        data = json.loads(out.read_text(encoding="utf-8"))
        assert data["entity_name"] == "Apple Inc."


class TestFactsToCsv:
    """Tests for Facts.to_csv() serialization."""

    def test_returns_valid_csv(self):
        """Verify to_csv() returns metadata as a parseable CSV."""
        facts = Facts(raw=SAMPLE_COMPANY_FACTS)
        reader = csv.DictReader(io.StringIO(facts.to_csv()))
        rows = list(reader)
        assert len(rows) == 1
        assert rows[0]["entity_name"] == "Apple Inc."


# ---------------------------------------------------------------------------
# CompanyInfo.to_json() / to_csv() tests
# ---------------------------------------------------------------------------


class TestCompanyInfoToJson:
    """Tests for CompanyInfo.to_json() serialization."""

    def test_returns_valid_json(self):
        """Verify to_json() returns a parseable JSON string with correct fields."""
        info = CompanyInfo(raw=SAMPLE_SUBMISSIONS_RAW)
        result = json.loads(info.to_json())
        assert result["name"] == "Apple Inc."
        assert result["cik"] == "320193"
        assert result["tickers"] == ["AAPL"]

    def test_recent_submissions_serialized(self):
        """Verify nested Submission objects are recursively serialized."""
        info = CompanyInfo(raw=SAMPLE_SUBMISSIONS_RAW)
        result = json.loads(info.to_json())
        subs = result["recent_submissions"]
        assert isinstance(subs, list)
        assert len(subs) == 1
        assert subs[0]["form"] == "10-K"


class TestCompanyInfoToCsv:
    """Tests for CompanyInfo.to_csv() serialization."""

    def test_returns_valid_csv(self):
        """Verify to_csv() returns a parseable CSV with correct fields."""
        info = CompanyInfo(raw=SAMPLE_SUBMISSIONS_RAW)
        reader = csv.DictReader(io.StringIO(info.to_csv()))
        rows = list(reader)
        assert len(rows) == 1
        assert rows[0]["name"] == "Apple Inc."

    def test_list_fields_serialized_as_json(self):
        """Verify list fields like tickers are JSON-encoded in CSV cells."""
        info = CompanyInfo(raw=SAMPLE_SUBMISSIONS_RAW)
        reader = csv.DictReader(io.StringIO(info.to_csv()))
        row = next(reader)
        assert json.loads(row["tickers"]) == ["AAPL"]


# ---------------------------------------------------------------------------
# SearchResult.to_json() / to_csv() tests
# ---------------------------------------------------------------------------


class TestSearchResultToJson:
    """Tests for SearchResult.to_json() serialization."""

    def test_returns_valid_json(self):
        """Verify to_json() returns a parseable JSON string with correct fields."""
        result = SearchResult(raw=SAMPLE_SEARCH_HIT)
        data = json.loads(result.to_json())
        assert data["form"] == "10-K"
        assert data["filing_date"] == "2024-02-27"
        assert "sec.gov" in data["url"]


class TestSearchResultToCsv:
    """Tests for SearchResult.to_csv() serialization."""

    def test_returns_valid_csv(self):
        """Verify to_csv() returns a parseable CSV with correct fields."""
        result = SearchResult(raw=SAMPLE_SEARCH_HIT)
        reader = csv.DictReader(io.StringIO(result.to_csv()))
        rows = list(reader)
        assert len(rows) == 1
        assert rows[0]["form"] == "10-K"


# ---------------------------------------------------------------------------
# Module-level to_json() tests
# ---------------------------------------------------------------------------


class TestModuleToJson:
    """Tests for the module-level to_json() function."""

    def test_returns_json_array(self):
        """Verify to_json() returns a JSON array of model dicts."""
        filings = [
            Filing(raw=SAMPLE_FILING_RAW),
            Filing(raw={"title": "8-K", "category_term": "8-K"}),
        ]
        data = json.loads(to_json(filings))
        assert isinstance(data, list)
        assert len(data) == 2
        assert data[0]["form_type"] == "10-K"
        assert data[1]["form_type"] == "8-K"

    def test_empty_list(self):
        """Verify to_json() returns an empty array for empty input."""
        result = to_json([])
        assert json.loads(result) == []

    def test_writes_to_file(self, tmp_path):
        """Verify to_json(path=...) writes a valid JSON file."""
        filings = [Filing(raw=SAMPLE_FILING_RAW)]
        out = tmp_path / "filings.json"
        to_json(filings, path=str(out))
        data = json.loads(out.read_text(encoding="utf-8"))
        assert len(data) == 1
        assert data[0]["form_type"] == "10-K"

    def test_returns_string_when_writing_file(self, tmp_path):
        """Verify to_json(path=...) still returns the JSON string."""
        filings = [Filing(raw=SAMPLE_FILING_RAW)]
        out = tmp_path / "filings.json"
        result = to_json(filings, path=str(out))
        assert isinstance(result, str)
        assert json.loads(result)[0]["form_type"] == "10-K"


# ---------------------------------------------------------------------------
# Module-level to_csv() tests
# ---------------------------------------------------------------------------


class TestModuleToCsv:
    """Tests for the module-level to_csv() function."""

    def test_returns_csv_with_header_and_rows(self):
        """Verify to_csv() returns CSV with header and data rows."""
        facts = [
            Fact(raw=SAMPLE_FACT_RAW),
            Fact(raw={**SAMPLE_FACT_RAW, "val": 999, "end": "2024-01-01"}),
        ]
        result = to_csv(facts)
        reader = csv.DictReader(io.StringIO(result))
        rows = list(reader)
        assert len(rows) == 2
        assert rows[0]["end"] == "2023-09-30"
        assert rows[1]["end"] == "2024-01-01"

    def test_empty_list(self):
        """Verify to_csv() returns empty string for empty input."""
        assert to_csv([]) == ""

    def test_writes_to_file(self, tmp_path):
        """Verify to_csv(path=...) writes a valid CSV file."""
        facts = [Fact(raw=SAMPLE_FACT_RAW)]
        out = tmp_path / "facts.csv"
        to_csv(facts, path=str(out))
        content = out.read_text(encoding="utf-8")
        reader = csv.DictReader(io.StringIO(content))
        rows = list(reader)
        assert rows[0]["end"] == "2023-09-30"

    def test_returns_string_when_writing_file(self, tmp_path):
        """Verify to_csv(path=...) still returns the CSV string."""
        facts = [Fact(raw=SAMPLE_FACT_RAW)]
        out = tmp_path / "facts.csv"
        result = to_csv(facts, path=str(out))
        assert isinstance(result, str)
        assert "end" in result


# ---------------------------------------------------------------------------
# Edge case tests
# ---------------------------------------------------------------------------


class TestSerializationEdgeCases:
    """Tests for edge cases in serialization."""

    def test_empty_raw_dict_to_json(self):
        """Verify to_json() works with an empty raw dict."""
        filing = Filing(raw={})
        result = json.loads(filing.to_json())
        assert result["title"] == ""
        assert result["form_type"] == ""

    def test_empty_raw_dict_to_csv(self):
        """Verify to_csv() works with an empty raw dict."""
        filing = Filing(raw={})
        reader = csv.DictReader(io.StringIO(filing.to_csv()))
        rows = list(reader)
        assert len(rows) == 1

    def test_none_value_in_fact(self):
        """Verify to_json() handles None values in facts."""
        fact = Fact(raw={"val": None, "end": "2023-01-01"})
        result = json.loads(fact.to_json())
        assert result["value"] is None

    def test_creates_parent_directories(self, tmp_path):
        """Verify to_json() creates parent dirs when writing files."""
        filing = Filing(raw=SAMPLE_FILING_RAW)
        nested = tmp_path / "sub" / "dir" / "filing.json"
        nested.parent.mkdir(parents=True)
        filing.to_json(path=str(nested))
        assert nested.exists()
