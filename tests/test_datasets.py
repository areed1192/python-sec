"""Tests for bulk financial dataset download and extraction."""

# pylint: disable=redefined-outer-name

import io
import zipfile
from unittest.mock import MagicMock, patch

import pytest

from edgar.datasets import _extract_tsv_zip


# ---------------------------------------------------------------------------
# Sample TSV data fixtures
# ---------------------------------------------------------------------------

SAMPLE_SUB_TSV = (
    "adsh\tcik\tname\tsic\tcountryba\tform\tperiod\tfy\tfp\n"
    "0001193125-24-047930\t320193\tApple Inc.\t3571\tUS\t10-K\t20230930\t2023\tFY\n"
    "0001193125-24-048000\t789019\tMicrosoft Corp\t7372\tUS\t10-K\t20230630\t2023\tFY\n"
)

SAMPLE_NUM_TSV = (
    "adsh\ttag\tversion\tcoreg\tddate\tqtrs\tuom\tvalue\n"
    "0001193125-24-047930\tRevenues\tus-gaap/2023\t\t20230930\t4\tUSD\t383285000000\n"
    "0001193125-24-048000\tRevenues\tus-gaap/2023\t\t20230630\t4\tUSD\t211915000000\n"
)

SAMPLE_TAG_TSV = (
    "tag\tversion\tcustom\tabstract\tdatatype\tiord\tcrdr\ttlabel\tdoc\n"
    "Revenues\tus-gaap/2023\t0\t0\tmonetaryItemType\tI\tC\tRevenues\tAmount of revenue.\n"
)

SAMPLE_PRE_TSV = (
    "adsh\treport\tline\tstmt\tinpth\trfile\ttag\tversion\tplabel\n"
    "0001193125-24-047930\t1\t1\tIS\t0\tR1.htm\tRevenues\tus-gaap/2023\tRevenues\n"
)


def _build_zip_bytes(
    files: dict[str, str] | None = None,
) -> bytes:
    """Build a ZIP file in memory from a dict of filename → content."""
    if files is None:
        files = {
            "sub.txt": SAMPLE_SUB_TSV,
            "num.txt": SAMPLE_NUM_TSV,
            "tag.txt": SAMPLE_TAG_TSV,
            "pre.txt": SAMPLE_PRE_TSV,
        }
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for name, content in files.items():
            zf.writestr(name, content)
    return buf.getvalue()


SAMPLE_ZIP_BYTES = _build_zip_bytes()


# ---------------------------------------------------------------------------
# _extract_tsv_zip tests
# ---------------------------------------------------------------------------


class TestExtractTsvZip:
    """Tests for the _extract_tsv_zip helper function."""

    def test_extracts_all_txt_files(self):
        """Verify all .txt files in ZIP are extracted."""
        result = _extract_tsv_zip(SAMPLE_ZIP_BYTES)
        assert set(result.keys()) == {"sub", "num", "tag", "pre"}

    def test_sub_file_parsed_correctly(self):
        """Verify sub.txt rows are parsed as dicts with correct keys."""
        result = _extract_tsv_zip(SAMPLE_ZIP_BYTES)
        subs = result["sub"]
        assert len(subs) == 2
        assert subs[0]["adsh"] == "0001193125-24-047930"
        assert subs[0]["cik"] == "320193"
        assert subs[0]["name"] == "Apple Inc."
        assert subs[1]["name"] == "Microsoft Corp"

    def test_num_file_parsed_correctly(self):
        """Verify num.txt rows are parsed as dicts with correct values."""
        result = _extract_tsv_zip(SAMPLE_ZIP_BYTES)
        nums = result["num"]
        assert len(nums) == 2
        assert nums[0]["tag"] == "Revenues"
        assert nums[0]["value"] == "383285000000"

    def test_ignores_non_txt_files(self):
        """Verify non-.txt files in the ZIP are ignored."""
        files = {
            "sub.txt": SAMPLE_SUB_TSV,
            "readme.md": "# README\nThis is not data.",
            "metadata.json": '{"version": 1}',
        }
        result = _extract_tsv_zip(_build_zip_bytes(files))
        assert set(result.keys()) == {"sub"}

    def test_empty_zip(self):
        """Verify empty ZIP returns empty dict."""
        result = _extract_tsv_zip(_build_zip_bytes({}))
        assert not result

    def test_single_row_file(self):
        """Verify single-row TSV files are handled correctly."""
        result = _extract_tsv_zip(SAMPLE_ZIP_BYTES)
        assert len(result["tag"]) == 1
        assert result["tag"][0]["tag"] == "Revenues"


# ---------------------------------------------------------------------------
# Datasets.get_financial_statements tests
# ---------------------------------------------------------------------------


class TestGetFinancialStatements:
    """Tests for Datasets.get_financial_statements()."""

    @pytest.fixture
    def datasets_service(self, edgar_client):
        """Return a Datasets service from the test client."""
        return edgar_client.datasets()

    def test_returns_parsed_data(self, datasets_service):
        """Verify get_financial_statements returns parsed TSV dicts."""
        datasets_service.edgar_session.fetch_page = MagicMock(
            return_value=SAMPLE_ZIP_BYTES
        )
        result = datasets_service.get_financial_statements(2023, 4)

        assert "sub" in result
        assert "num" in result
        assert len(result["sub"]) == 2
        assert result["sub"][0]["name"] == "Apple Inc."

    def test_calls_correct_url(self, datasets_service):
        """Verify the correct DERA URL is constructed."""
        datasets_service.edgar_session.fetch_page = MagicMock(
            return_value=SAMPLE_ZIP_BYTES
        )
        datasets_service.get_financial_statements(2023, 4)

        call_url = datasets_service.edgar_session.fetch_page.call_args[0][0]
        assert "2023q4.zip" in call_url
        assert "financial-statement-data-sets" in call_url

    def test_different_year_quarter(self, datasets_service):
        """Verify different year/quarter combinations build correct URLs."""
        datasets_service.edgar_session.fetch_page = MagicMock(
            return_value=SAMPLE_ZIP_BYTES
        )
        datasets_service.get_financial_statements(2021, 1)

        call_url = datasets_service.edgar_session.fetch_page.call_args[0][0]
        assert "2021q1.zip" in call_url

    def test_invalid_quarter_raises(self, datasets_service):
        """Verify ValueError is raised for invalid quarter values."""
        with pytest.raises(ValueError, match="quarter must be between 1 and 4"):
            datasets_service.get_financial_statements(2023, 0)
        with pytest.raises(ValueError, match="quarter must be between 1 and 4"):
            datasets_service.get_financial_statements(2023, 5)

    def test_returns_empty_dict_on_none(self, datasets_service):
        """Verify empty dict returned when fetch_page returns None."""
        datasets_service.edgar_session.fetch_page = MagicMock(return_value=None)
        result = datasets_service.get_financial_statements(2023, 4)
        assert result == {}


# ---------------------------------------------------------------------------
# Datasets.get_financial_statements_dataframes tests
# ---------------------------------------------------------------------------


class TestGetFinancialStatementsDataframes:
    """Tests for Datasets.get_financial_statements_dataframes()."""

    @pytest.fixture
    def datasets_service(self, edgar_client):
        """Return a Datasets service from the test client."""
        return edgar_client.datasets()

    def test_returns_dataframes(self, datasets_service):
        """Verify the method returns pandas DataFrames."""
        pd = pytest.importorskip("pandas", reason="pandas required")
        datasets_service.edgar_session.fetch_page = MagicMock(
            return_value=SAMPLE_ZIP_BYTES
        )
        result = datasets_service.get_financial_statements_dataframes(2023, 4)

        assert "sub" in result
        assert "num" in result
        assert isinstance(result["sub"], pd.DataFrame)
        assert len(result["sub"]) == 2
        assert result["sub"].iloc[0]["name"] == "Apple Inc."

    def test_dataframe_columns(self, datasets_service):
        """Verify DataFrames have the expected columns."""
        pytest.importorskip("pandas", reason="pandas required")
        datasets_service.edgar_session.fetch_page = MagicMock(
            return_value=SAMPLE_ZIP_BYTES
        )
        result = datasets_service.get_financial_statements_dataframes(2023, 4)

        assert "adsh" in result["sub"].columns
        assert "cik" in result["sub"].columns
        assert "tag" in result["num"].columns
        assert "value" in result["num"].columns

    def test_returns_empty_dict_on_none(self, datasets_service):
        """Verify empty dict returned when fetch_page returns None."""
        pytest.importorskip("pandas", reason="pandas required")
        datasets_service.edgar_session.fetch_page = MagicMock(return_value=None)
        result = datasets_service.get_financial_statements_dataframes(2023, 4)
        assert result == {}

    def test_raises_without_pandas(self, datasets_service):
        """Verify ImportError is raised when pandas is not installed."""
        datasets_service.edgar_session.fetch_page = MagicMock(
            return_value=SAMPLE_ZIP_BYTES
        )
        with patch.dict("sys.modules", {"pandas": None}):
            with pytest.raises(ImportError, match="pandas"):
                datasets_service.get_financial_statements_dataframes(2023, 4)
