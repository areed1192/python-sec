"""Tests for the filing download functionality (EdgarSession.download)."""

# pylint: disable=redefined-outer-name

import os
from unittest.mock import MagicMock

import pytest
import requests

from edgar.exceptions import EdgarRequestError


@pytest.fixture
def edgar_session(edgar_client):
    """Return the EdgarSession from the test client."""
    return edgar_client.edgar_session


# ---------------------------------------------------------------------------
# EdgarSession.download tests
# ---------------------------------------------------------------------------


class TestSessionDownload:
    """Tests for EdgarSession.download with various content types and error conditions."""

    def test_download_text_content(self, edgar_session):
        """Verify text/html response is returned as a string."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "text/html; charset=utf-8"}
        mock_response.text = "<html><body>Filing content</body></html>"

        edgar_session.http_session.get = MagicMock(return_value=mock_response)

        result = edgar_session.download("https://www.sec.gov/Archives/edgar/data/320193/filing.htm")
        assert result == "<html><body>Filing content</body></html>"

    def test_download_binary_content(self, edgar_session):
        """Verify application/pdf response is returned as bytes."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/pdf"}
        mock_response.content = b"%PDF-1.4 binary content"

        edgar_session.http_session.get = MagicMock(return_value=mock_response)

        result = edgar_session.download("https://www.sec.gov/Archives/edgar/data/320193/filing.pdf")
        assert result == b"%PDF-1.4 binary content"

    def test_download_saves_to_file(self, edgar_session, tmp_path):
        """Verify text content is saved to disk when a path is provided."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "text/html"}
        mock_response.text = "<html>saved</html>"

        edgar_session.http_session.get = MagicMock(return_value=mock_response)

        output_path = str(tmp_path / "filing.html")
        result = edgar_session.download(
            "https://www.sec.gov/Archives/edgar/data/320193/filing.htm",
            path=output_path,
        )

        assert result == output_path
        assert os.path.exists(output_path)
        with open(output_path, encoding="utf-8") as f:
            assert f.read() == "<html>saved</html>"

    def test_download_saves_binary_to_file(self, edgar_session, tmp_path):
        """Verify binary content is saved to disk when a path is provided."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/pdf"}
        mock_response.content = b"%PDF-binary"

        edgar_session.http_session.get = MagicMock(return_value=mock_response)

        output_path = str(tmp_path / "filing.pdf")
        result = edgar_session.download(
            "https://www.sec.gov/Archives/edgar/data/320193/filing.pdf",
            path=output_path,
        )

        assert result == output_path
        with open(output_path, "rb") as f:
            assert f.read() == b"%PDF-binary"

    def test_download_non_200_raises(self, edgar_session):
        """Verify a non-200 status code raises EdgarRequestError."""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.headers = {"Content-Type": "text/html"}

        edgar_session.http_session.get = MagicMock(return_value=mock_response)

        with pytest.raises(EdgarRequestError, match="status 404"):
            edgar_session.download("https://www.sec.gov/nonexistent")

    def test_download_request_exception_raises(self, edgar_session):
        """Verify a connection failure raises EdgarRequestError."""
        edgar_session.http_session.get = MagicMock(
            side_effect=requests.RequestException("connection error")
        )

        with pytest.raises(EdgarRequestError, match="Failed to download"):
            edgar_session.download("https://www.sec.gov/broken")


# ---------------------------------------------------------------------------
# EdgarClient.download convenience method tests
# ---------------------------------------------------------------------------


class TestClientDownload:
    """Tests for the EdgarClient.download convenience method."""

    def test_client_download_delegates(self, edgar_client):
        """Verify EdgarClient.download delegates to EdgarSession.download."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "text/xml"}
        mock_response.text = "<xbrl>data</xbrl>"

        edgar_client.edgar_session.http_session.get = MagicMock(return_value=mock_response)

        result = edgar_client.download("https://www.sec.gov/Archives/filing.xml")
        assert result == "<xbrl>data</xbrl>"


# ---------------------------------------------------------------------------
# EdgarClient.resolve_ticker / resolve_cik convenience methods
# ---------------------------------------------------------------------------


SAMPLE_TICKERS_JSON = {
    "0": {"cik_str": 320193, "ticker": "AAPL", "title": "Apple Inc."},
}


class TestClientTickerConvenience:
    """Tests for EdgarClient.resolve_ticker and resolve_cik convenience methods."""

    def test_client_resolve_ticker(self, edgar_client):
        """Verify EdgarClient.resolve_ticker delegates to the Tickers service."""
        edgar_client.edgar_session.make_request = MagicMock(return_value=SAMPLE_TICKERS_JSON)
        cik = edgar_client.resolve_ticker("AAPL")
        assert cik == "0000320193"

    def test_client_resolve_cik(self, edgar_client):
        """Verify EdgarClient.resolve_cik delegates to the Tickers service."""
        edgar_client.edgar_session.make_request = MagicMock(return_value=SAMPLE_TICKERS_JSON)
        entries = edgar_client.resolve_cik(320193)
        assert entries[0]["ticker"] == "AAPL"
