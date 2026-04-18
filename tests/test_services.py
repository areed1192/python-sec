"""Unit tests for service methods with mocked HTTP responses."""

import copy
import json
from unittest.mock import MagicMock

import pytest
import requests as req

from edgar.enums import StateCodes
from edgar.enums import FilingTypeCodes
from edgar.exceptions import EdgarRequestError
from tests.conftest import (
    SAMPLE_ATOM_FEED,
    SAMPLE_SUBMISSIONS_JSON,
    SAMPLE_XBRL_COMPANY_FACTS,
    SAMPLE_DIRECTORY_JSON,
    SAMPLE_FILING_DIRECTORY_JSON,
    TEST_USER_AGENT,
)


def _mock_response(
    content_type="application/atom+xml", text="", json_data=None, status_code=200
):
    """Create a mock requests.Response."""
    resp = MagicMock()
    resp.status_code = status_code
    resp.ok = status_code == 200
    resp.headers = {"Content-Type": content_type}
    resp.text = text
    resp.content = text.encode("utf-8") if isinstance(text, str) else text
    if json_data is not None:
        # Deep-copy to prevent mutation of shared fixture data.
        resp.json.return_value = copy.deepcopy(json_data)
        resp.content = json.dumps(json_data).encode("utf-8")
    return resp


def _patch_session_request(edgar_client, mock_resp):
    """Patch the http_session.request on an existing EdgarClient's session."""
    edgar_client.edgar_session.http_session.request = MagicMock(
        return_value=mock_resp
    )


# ---------------------------------------------------------------------------
# Session / make_request tests
# ---------------------------------------------------------------------------


class TestSession:
    """Tests for EdgarSession.make_request and build_url."""

    def test_build_url_default(self, edgar_session):
        """build_url should use the SEC resource by default."""
        url = edgar_session.build_url(endpoint="/cgi-bin/browse-edgar")
        assert url == "https://www.sec.gov/cgi-bin/browse-edgar"

    def test_build_url_api(self, edgar_session):
        """build_url with use_api=True should use the API resource."""
        url = edgar_session.build_url(
            endpoint="/submissions/CIK0001326801.json", use_api=True
        )
        assert url == "https://data.sec.gov/submissions/CIK0001326801.json"

    def test_make_request_returns_json(self, edgar_client):
        """make_request should return parsed JSON for application/json responses."""
        _patch_session_request(
            edgar_client,
            _mock_response(
                content_type="application/json",
                json_data=SAMPLE_SUBMISSIONS_JSON,
            ),
        )
        result = edgar_client.edgar_session.make_request(
            method="get",
            endpoint="/submissions/CIK0001326801.json",
            use_api=True,
        )
        assert result == SAMPLE_SUBMISSIONS_JSON

    def test_make_request_returns_xml(self, edgar_client):
        """make_request should return raw text for XML responses."""
        _patch_session_request(
            edgar_client,
            _mock_response(
                content_type="text/xml",
                text=SAMPLE_ATOM_FEED,
            ),
        )
        result = edgar_client.edgar_session.make_request(
            method="get",
            endpoint="/cgi-bin/browse-edgar",
        )
        assert "10-K" in result

    def test_make_request_raises_on_connection_error(self, edgar_client):
        """make_request should raise EdgarRequestError on connection failure."""

        edgar_client.edgar_session.http_session.request = MagicMock(
            side_effect=req.ConnectionError("Connection refused")
        )
        with pytest.raises(EdgarRequestError, match="Connection refused"):
            edgar_client.edgar_session.make_request(
                method="get",
                endpoint="/cgi-bin/browse-edgar",
            )

    def test_user_agent_set_on_session(self, edgar_session):
        """The session should have the user-agent header set."""
        assert (
            edgar_session.http_session.headers["user-agent"] == TEST_USER_AGENT
        )


# ---------------------------------------------------------------------------
# Companies service tests
# ---------------------------------------------------------------------------


class TestCompaniesService:
    """Tests for the Companies service with mocked HTTP."""

    def test_get_companies_by_state(self, edgar_client):
        """get_companies_by_state should call the endpoint and parse XML."""
        _patch_session_request(
            edgar_client,
            _mock_response(
                content_type="application/atom+xml",
                text=SAMPLE_ATOM_FEED,
            ),
        )
        companies = edgar_client.companies()
        result = companies.get_companies_by_state(state_code="TX")
        assert isinstance(result, list)
        assert len(result) == 2

    def test_get_companies_by_state_with_enum(self, edgar_client):
        """get_companies_by_state should accept an enum value."""

        _patch_session_request(
            edgar_client,
            _mock_response(
                content_type="application/atom+xml",
                text=SAMPLE_ATOM_FEED,
            ),
        )
        companies = edgar_client.companies()
        result = companies.get_companies_by_state(state_code=StateCodes.TEXAS)
        assert isinstance(result, list)

    def test_get_company_by_cik(self, edgar_client):
        """get_company_by_cik should parse entries."""
        _patch_session_request(
            edgar_client,
            _mock_response(
                content_type="application/atom+xml",
                text=SAMPLE_ATOM_FEED,
            ),
        )
        companies = edgar_client.companies()
        result = companies.get_company_by_cik(cik="1326801")
        assert isinstance(result, list)


# ---------------------------------------------------------------------------
# Submissions service tests
# ---------------------------------------------------------------------------


class TestSubmissionsService:
    """Tests for the Submissions service with mocked HTTP."""

    def test_get_submissions(self, edgar_client):
        """get_submissions should return JSON data from the API."""
        _patch_session_request(
            edgar_client,
            _mock_response(
                content_type="application/json",
                json_data=SAMPLE_SUBMISSIONS_JSON,
            ),
        )
        subs = edgar_client.submissions()
        result = subs.get_submissions(cik="1326801")
        assert result["cik"] == "1326801"
        assert result["name"] == "Facebook, Inc."

    def test_get_submissions_invalid_cik(self, edgar_client):
        """get_submissions should reject non-numeric CIK values."""
        subs = edgar_client.submissions()
        with pytest.raises(ValueError, match="digits"):
            subs.get_submissions(cik="../etc/passwd")


# ---------------------------------------------------------------------------
# XBRL service tests
# ---------------------------------------------------------------------------


class TestXbrlService:
    """Tests for the XBRL service with mocked HTTP."""

    def test_company_facts(self, edgar_client):
        """company_facts should return JSON data from the API."""
        _patch_session_request(
            edgar_client,
            _mock_response(
                content_type="application/json",
                json_data=SAMPLE_XBRL_COMPANY_FACTS,
            ),
        )
        xbrl = edgar_client.xbrl()
        result = xbrl.company_facts(cik="1326801")
        assert result["entityName"] == "Facebook, Inc."

    def test_company_facts_invalid_cik(self, edgar_client):
        """company_facts should reject non-numeric CIK values."""
        xbrl = edgar_client.xbrl()
        with pytest.raises(ValueError, match="digits"):
            xbrl.company_facts(cik="../../bad")

    def test_company_concepts(self, edgar_client):
        """company_concepts should make a request with the correct params."""
        _patch_session_request(
            edgar_client,
            _mock_response(
                content_type="application/json",
                json_data={"units": {"USD": []}},
            ),
        )
        xbrl = edgar_client.xbrl()
        result = xbrl.company_concepts(cik="1326801", concept="AccountsPayableCurrent")
        assert isinstance(result, dict)


# ---------------------------------------------------------------------------
# Archives service tests
# ---------------------------------------------------------------------------


class TestArchivesService:
    """Tests for the Archives service with mocked HTTP."""

    def test_get_company_directories(self, edgar_client):
        """get_company_directories should return cleaned directory data."""
        _patch_session_request(
            edgar_client,
            _mock_response(
                content_type="application/json",
                json_data=SAMPLE_DIRECTORY_JSON,
            ),
        )
        archives = edgar_client.archives()
        result = archives.get_company_directories(cik="1326801")
        assert isinstance(result, list)
        assert len(result) == 1
        assert "filing_id" in result[0]

    def test_get_company_directory(self, edgar_client):
        """get_company_directory should return cleaned file data."""
        _patch_session_request(
            edgar_client,
            _mock_response(
                content_type="application/json",
                json_data=SAMPLE_FILING_DIRECTORY_JSON,
            ),
        )
        archives = edgar_client.archives()
        result = archives.get_company_directory(
            cik="1326801", filing_id="000132680121000003"
        )
        assert isinstance(result, list)
        assert "filing_id" in result[0]


# ---------------------------------------------------------------------------
# Filings service tests
# ---------------------------------------------------------------------------


class TestFilingsService:
    """Tests for the Filings service with mocked HTTP."""

    def test_get_filings_by_cik(self, edgar_client):
        """get_filings_by_cik should parse XML entries."""
        _patch_session_request(
            edgar_client,
            _mock_response(
                content_type="application/atom+xml",
                text=SAMPLE_ATOM_FEED,
            ),
        )
        filings = edgar_client.filings()
        result = filings.get_filings_by_cik(cik="1326801")
        assert isinstance(result, list)
        assert len(result) == 2

    def test_get_filings_by_type(self, edgar_client):
        """get_filings_by_type should accept a FilingTypeCodes enum."""


        _patch_session_request(
            edgar_client,
            _mock_response(
                content_type="application/atom+xml",
                text=SAMPLE_ATOM_FEED,
            ),
        )
        filings = edgar_client.filings()
        result = filings.get_filings_by_type(
            cik="1326801",
            filing_type=FilingTypeCodes.FILING_10K,
        )
        assert isinstance(result, list)
