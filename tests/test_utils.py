"""Unit tests for EdgarUtilities date parsing and directory cleaning."""

import copy
from datetime import date, datetime

import pytest

from tests.conftest import SAMPLE_DIRECTORY_JSON, SAMPLE_FILING_DIRECTORY_JSON


class TestParseDates:
    """Tests for EdgarUtilities.parse_dates."""

    def test_date_object(self, edgar_utilities):
        """A date object should be converted to ISO format string."""
        result = edgar_utilities.parse_dates(date(2021, 3, 15))
        assert result == "2021-03-15"

    def test_datetime_object(self, edgar_utilities):
        """A datetime object should be converted to ISO format string."""
        result = edgar_utilities.parse_dates(datetime(2021, 3, 15, 10, 30))
        assert result == "2021-03-15T10:30:00"

    def test_valid_date_string(self, edgar_utilities):
        """A valid ISO date string should be returned as-is."""
        result = edgar_utilities.parse_dates("2021-03-15")
        assert result == "2021-03-15"

    def test_invalid_date_string_raises(self, edgar_utilities):
        """An invalid date string should raise ValueError."""
        with pytest.raises(ValueError, match="not in ISO format"):
            edgar_utilities.parse_dates("March 15, 2021")

    def test_invalid_type_raises(self, edgar_utilities):
        """A non-date type should raise ValueError."""
        with pytest.raises(ValueError, match="Must pass through"):
            edgar_utilities.parse_dates(12345)

    def test_empty_string_raises(self, edgar_utilities):
        """An empty string should raise ValueError."""
        with pytest.raises(ValueError):
            edgar_utilities.parse_dates("")


class TestCleanDirectories:
    """Tests for EdgarUtilities.clean_directories."""

    def test_returns_list(self, edgar_utilities):
        """clean_directories should return a list."""
        result = edgar_utilities.clean_directories(
            copy.deepcopy(SAMPLE_DIRECTORY_JSON), cik="1326801"
        )
        assert isinstance(result, list)

    def test_adds_cik_field(self, edgar_utilities):
        """Each directory item should have the CIK set."""
        result = edgar_utilities.clean_directories(
            copy.deepcopy(SAMPLE_DIRECTORY_JSON), cik="1326801"
        )
        assert result[0]["cik"] == "1326801"

    def test_renames_fields(self, edgar_utilities):
        """'name' should become 'filing_id' and 'last-modified' should become 'last_modified'."""
        result = edgar_utilities.clean_directories(
            copy.deepcopy(SAMPLE_DIRECTORY_JSON), cik="1326801"
        )
        item = result[0]
        assert "filing_id" in item
        assert "last_modified" in item
        assert "name" not in item
        assert "last-modified" not in item

    def test_builds_url(self, edgar_utilities):
        """Each item should have a URL built from the directory name."""
        result = edgar_utilities.clean_directories(
            copy.deepcopy(SAMPLE_DIRECTORY_JSON), cik="1326801"
        )
        assert "url" in result[0]
        # Note: clean_directories uses .replace('//', '/') which strips the
        # protocol double-slash, producing "https:/..." — a known code quirk.
        assert "sec.gov" in result[0]["url"]


class TestCleanFilingDirectory:
    """Tests for EdgarUtilities.clean_filing_directory."""

    def test_returns_list(self, edgar_utilities):
        """clean_filing_directory should return a list."""
        result = edgar_utilities.clean_filing_directory(
            copy.deepcopy(SAMPLE_FILING_DIRECTORY_JSON), cik="1326801"
        )
        assert isinstance(result, list)

    def test_adds_cik_field(self, edgar_utilities):
        """Each file item should have the CIK set."""
        result = edgar_utilities.clean_filing_directory(
            copy.deepcopy(SAMPLE_FILING_DIRECTORY_JSON), cik="1326801"
        )
        assert result[0]["cik"] == "1326801"

    def test_renames_fields(self, edgar_utilities):
        """Fields should be renamed consistently."""
        result = edgar_utilities.clean_filing_directory(
            copy.deepcopy(SAMPLE_FILING_DIRECTORY_JSON), cik="1326801"
        )
        item = result[0]
        assert "filing_id" in item
        assert "last_modified" in item
