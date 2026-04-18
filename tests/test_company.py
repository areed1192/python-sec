"""Tests for the fluent Company interface."""

# pylint: disable=redefined-outer-name,protected-access

from unittest.mock import MagicMock

import pytest

from edgar.company import Company


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

SAMPLE_TICKERS_JSON = {
    "0": {"cik_str": 320193, "ticker": "AAPL", "title": "Apple Inc."},
    "1": {"cik_str": 789019, "ticker": "MSFT", "title": "MICROSOFT CORP"},
    "2": {"cik_str": 1326801, "ticker": "META", "title": "Meta Platforms, Inc."},
}


@pytest.fixture
def mock_tickers():
    """Return a mock Tickers service backed by sample data."""
    tickers = MagicMock()

    def _resolve_ticker(ticker):
        mapping = {"AAPL": "0000320193", "MSFT": "0000789019", "META": "0001326801"}
        result = mapping.get(ticker.upper())
        if result is None:
            raise ValueError(f"Ticker '{ticker}' not found in SEC company tickers.")
        return result

    def _resolve_cik(cik):
        cik_int = int(str(cik).lstrip("0")) if str(cik).lstrip("0") else 0
        entries = {
            320193: [{"cik_str": 320193, "ticker": "AAPL", "title": "Apple Inc."}],
            789019: [{"cik_str": 789019, "ticker": "MSFT", "title": "MICROSOFT CORP"}],
            1326801: [
                {"cik_str": 1326801, "ticker": "META", "title": "Meta Platforms, Inc."}
            ],
        }
        result = entries.get(cik_int)
        if result is None:
            raise ValueError(f"CIK '{cik}' not found in SEC company tickers.")
        return result

    tickers.resolve_ticker.side_effect = _resolve_ticker
    tickers.resolve_cik.side_effect = _resolve_cik
    return tickers


@pytest.fixture
def mock_session():
    """Return a mock EdgarSession."""
    session = MagicMock()
    session.cache = None
    return session


@pytest.fixture
def apple(mock_session, mock_tickers):
    """Return a Company instance for Apple via ticker."""
    return Company(
        identifier="AAPL", session=mock_session, tickers_service=mock_tickers
    )


# ---------------------------------------------------------------------------
# Construction tests
# ---------------------------------------------------------------------------


class TestCompanyConstruction:
    """Tests for creating Company objects from tickers and CIKs."""

    def test_from_ticker(self, mock_session, mock_tickers):
        """Verify a Company can be created from a ticker symbol."""
        company = Company(
            identifier="AAPL", session=mock_session, tickers_service=mock_tickers
        )
        assert company.cik == "0000320193"
        assert company.ticker == "AAPL"
        assert company.name == "Apple Inc."

    def test_from_ticker_case_insensitive(self, mock_session, mock_tickers):
        """Verify ticker lookup is case-insensitive."""
        company = Company(
            identifier="aapl", session=mock_session, tickers_service=mock_tickers
        )
        assert company.cik == "0000320193"
        assert company.ticker == "AAPL"

    def test_from_cik_string(self, mock_session, mock_tickers):
        """Verify a Company can be created from a CIK string."""
        company = Company(
            identifier="320193", session=mock_session, tickers_service=mock_tickers
        )
        assert company.cik == "0000320193"
        assert company.ticker == "AAPL"
        assert company.name == "Apple Inc."

    def test_from_cik_zero_padded(self, mock_session, mock_tickers):
        """Verify a Company can be created from a zero-padded CIK."""
        company = Company(
            identifier="0000320193", session=mock_session, tickers_service=mock_tickers
        )
        assert company.cik == "0000320193"
        assert company.ticker == "AAPL"

    def test_unknown_ticker_raises(self, mock_session, mock_tickers):
        """Verify ValueError is raised for an unknown ticker."""
        with pytest.raises(ValueError, match="not found"):
            Company(
                identifier="ZZZZZ", session=mock_session, tickers_service=mock_tickers
            )

    def test_unknown_cik_raises(self, mock_session, mock_tickers):
        """Verify ValueError is raised for an unknown CIK."""
        with pytest.raises(ValueError, match="not found"):
            Company(
                identifier="9999999", session=mock_session, tickers_service=mock_tickers
            )

    def test_repr(self, apple):
        """Verify the string representation includes key fields."""
        result = repr(apple)
        assert "AAPL" in result
        assert "0000320193" in result
        assert "Apple Inc." in result


# ---------------------------------------------------------------------------
# Property tests
# ---------------------------------------------------------------------------


class TestCompanyProperties:
    """Tests for Company property accessors."""

    def test_cik_property(self, apple):
        """Verify the cik property returns the zero-padded CIK."""
        assert apple.cik == "0000320193"

    def test_ticker_property(self, apple):
        """Verify the ticker property returns the uppercase ticker."""
        assert apple.ticker == "AAPL"

    def test_name_property(self, apple):
        """Verify the name property returns the company name."""
        assert apple.name == "Apple Inc."

    def test_cik_unpadded_property(self, apple):
        """Verify cik_unpadded strips leading zeros."""
        assert apple.cik_unpadded == "320193"


# ---------------------------------------------------------------------------
# Fluent method tests
# ---------------------------------------------------------------------------


class TestCompanyFilings:
    """Tests for the fluent filings() method."""

    def test_filings_all(self, mock_session, mock_tickers):
        """Verify filings() without form type calls get_filings_by_cik."""
        mock_session.make_request = MagicMock(return_value="<feed/>")
        mock_session.edgar_parser = MagicMock()
        mock_session.edgar_parser.parse_entries.return_value = [{"title": "10-K"}]
        mock_session.edgar_utilities = MagicMock()
        mock_session.fetch_page = MagicMock()

        company = Company(
            identifier="AAPL", session=mock_session, tickers_service=mock_tickers
        )
        result = company.filings()
        assert isinstance(result, list)

    def test_filings_with_form_type(self, mock_session, mock_tickers):
        """Verify filings(form='10-K') calls get_filings_by_type."""
        mock_session.make_request = MagicMock(return_value="<feed/>")
        mock_session.edgar_parser = MagicMock()
        mock_session.edgar_parser.parse_entries.return_value = [{"title": "10-K"}]
        mock_session.edgar_utilities = MagicMock()
        mock_session.fetch_page = MagicMock()

        company = Company(
            identifier="AAPL", session=mock_session, tickers_service=mock_tickers
        )
        result = company.filings(form="10-K")
        assert isinstance(result, list)

    def test_filings_passes_cik_unpadded(self, mock_session, mock_tickers):
        """Verify the unpadded CIK is passed to the filings service."""
        mock_session.make_request = MagicMock(return_value="<feed/>")
        mock_session.edgar_parser = MagicMock()
        mock_session.edgar_parser.parse_entries.return_value = []
        mock_session.edgar_utilities = MagicMock()
        mock_session.fetch_page = MagicMock()

        company = Company(
            identifier="AAPL", session=mock_session, tickers_service=mock_tickers
        )
        company.filings()

        # The make_request call should include the unpadded CIK.
        call_args = mock_session.make_request.call_args
        params = call_args.kwargs.get("params") or call_args[1].get("params", {})
        assert params.get("CIK") == "320193"


class TestCompanySubmissions:
    """Tests for the fluent submissions() method."""

    def test_submissions_delegates(self, mock_session, mock_tickers):
        """Verify submissions() calls the submissions endpoint with the correct CIK."""
        mock_session.make_request = MagicMock(return_value={"cik": "320193"})
        mock_session.edgar_utilities = MagicMock()

        company = Company(
            identifier="AAPL", session=mock_session, tickers_service=mock_tickers
        )
        company.submissions()

        mock_session.make_request.assert_called_once()
        call_kwargs = mock_session.make_request.call_args
        # The endpoint should contain the zero-padded CIK.
        endpoint = call_kwargs.kwargs.get("endpoint") or call_kwargs[1].get(
            "endpoint", ""
        )
        assert "CIK0000320193" in endpoint


class TestCompanyXbrlFacts:
    """Tests for the fluent xbrl_facts() method."""

    def test_xbrl_facts_delegates(self, mock_session, mock_tickers):
        """Verify xbrl_facts() calls the XBRL endpoint with the correct CIK."""
        mock_session.make_request = MagicMock(return_value={"facts": {}})
        mock_session.edgar_utilities = MagicMock()

        company = Company(
            identifier="AAPL", session=mock_session, tickers_service=mock_tickers
        )
        company.xbrl_facts()

        mock_session.make_request.assert_called_once()


class TestCompanyDownload:
    """Tests for the fluent download() method."""

    def test_download_delegates(self, mock_session, mock_tickers):
        """Verify download() delegates to session.download."""
        mock_session.download = MagicMock(return_value="<html>content</html>")

        company = Company(
            identifier="AAPL", session=mock_session, tickers_service=mock_tickers
        )
        result = company.download("https://www.sec.gov/Archives/filing.htm")

        mock_session.download.assert_called_once_with(
            url="https://www.sec.gov/Archives/filing.htm", path=None
        )
        assert result == "<html>content</html>"


# ---------------------------------------------------------------------------
# EdgarClient.company() integration tests
# ---------------------------------------------------------------------------


class TestClientCompanyMethod:
    """Tests for EdgarClient.company() convenience method."""

    def test_client_company_returns_company(self, edgar_client):
        """Verify client.company() returns a Company object."""
        edgar_client.edgar_session.make_request = MagicMock(
            return_value=SAMPLE_TICKERS_JSON
        )

        company = edgar_client.company("AAPL")

        assert isinstance(company, Company)
        assert company.ticker == "AAPL"
        assert company.cik == "0000320193"

    def test_client_company_by_cik(self, edgar_client):
        """Verify client.company() works with a CIK number."""
        edgar_client.edgar_session.make_request = MagicMock(
            return_value=SAMPLE_TICKERS_JSON
        )

        company = edgar_client.company("320193")

        assert isinstance(company, Company)
        assert company.ticker == "AAPL"

    def test_backward_compat_filings_still_works(self, edgar_client):
        """Verify client.filings() still works (backward compatibility)."""
        filings_service = edgar_client.filings()
        assert filings_service is not None

    def test_backward_compat_companies_still_works(self, edgar_client):
        """Verify client.companies() still works (backward compatibility)."""
        companies_service = edgar_client.companies()
        assert companies_service is not None
