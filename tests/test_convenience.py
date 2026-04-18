"""Tests for top-level convenience functions in edgar/__init__.py."""

# pylint: disable=redefined-outer-name
# pylint: disable=protected-access

from unittest.mock import MagicMock, patch

import pytest

import edgar
from edgar.exceptions import EdgarError


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def _reset_module_state():
    """Reset the module-level singleton between tests."""
    edgar._user_agent = None
    edgar._client = None
    yield
    edgar._user_agent = None
    edgar._client = None


# ---------------------------------------------------------------------------
# set_user_agent tests
# ---------------------------------------------------------------------------


class TestSetUserAgent:
    """Tests for edgar.set_user_agent()."""

    def test_stores_user_agent(self):
        """Verify set_user_agent stores the value."""
        edgar.set_user_agent("Test Agent test@example.com")
        assert edgar._user_agent == "Test Agent test@example.com"

    def test_clears_cached_client(self):
        """Verify set_user_agent resets the cached client."""
        edgar._client = MagicMock()
        edgar.set_user_agent("New Agent new@example.com")
        assert edgar._client is None


# ---------------------------------------------------------------------------
# _get_client tests
# ---------------------------------------------------------------------------


class TestGetClient:
    """Tests for the _get_client() helper."""

    def test_uses_set_user_agent_value(self):
        """Verify _get_client uses the programmatic user-agent."""
        edgar.set_user_agent("Test Agent test@example.com")
        client = edgar._get_client()
        assert isinstance(client, edgar.EdgarClient)

    def test_uses_env_var(self):
        """Verify _get_client falls back to SEC_EDGAR_USER_AGENT env var."""
        with patch.dict("os.environ", {"SEC_EDGAR_USER_AGENT": "Env Agent env@example.com"}):
            client = edgar._get_client()
            assert isinstance(client, edgar.EdgarClient)

    def test_set_user_agent_overrides_env_var(self):
        """Verify set_user_agent takes priority over env var."""
        edgar.set_user_agent("Programmatic Agent prog@example.com")
        with patch.dict("os.environ", {"SEC_EDGAR_USER_AGENT": "Env Agent env@example.com"}):
            client = edgar._get_client()
            # The client was created with the programmatic agent
            assert client.edgar_session.user_agent == "Programmatic Agent prog@example.com"

    def test_raises_without_user_agent(self):
        """Verify _get_client raises EdgarError when no user-agent is set."""
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(EdgarError, match="No user-agent configured"):
                edgar._get_client()

    def test_caches_client_instance(self):
        """Verify _get_client returns the same instance on repeated calls."""
        edgar.set_user_agent("Test Agent test@example.com")
        client1 = edgar._get_client()
        client2 = edgar._get_client()
        assert client1 is client2

    def test_set_user_agent_forces_new_client(self):
        """Verify changing user-agent creates a new client."""
        edgar.set_user_agent("Agent One one@example.com")
        client1 = edgar._get_client()
        edgar.set_user_agent("Agent Two two@example.com")
        client2 = edgar._get_client()
        assert client1 is not client2


# ---------------------------------------------------------------------------
# edgar.company() tests
# ---------------------------------------------------------------------------


class TestCompanyConvenience:
    """Tests for the module-level edgar.company() function."""

    @patch.object(edgar.EdgarClient, "company")
    def test_delegates_to_client(self, mock_company):
        """Verify edgar.company() calls EdgarClient.company()."""
        edgar.set_user_agent("Test Agent test@example.com")
        mock_company.return_value = MagicMock(name="CompanyMock")
        result = edgar.company("AAPL")
        mock_company.assert_called_once_with("AAPL")
        assert result is mock_company.return_value

    def test_raises_without_user_agent(self):
        """Verify edgar.company() raises when no user-agent is configured."""
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(EdgarError):
                edgar.company("AAPL")


# ---------------------------------------------------------------------------
# edgar.get_filings() tests
# ---------------------------------------------------------------------------


class TestGetFilingsConvenience:
    """Tests for the module-level edgar.get_filings() function."""

    @patch.object(edgar.EdgarClient, "company")
    def test_delegates_to_company_get_filings(self, mock_company):
        """Verify edgar.get_filings() chains company().get_filings()."""
        edgar.set_user_agent("Test Agent test@example.com")
        mock_co = MagicMock()
        mock_co.get_filings.return_value = [{"form": "10-K"}]
        mock_company.return_value = mock_co

        result = edgar.get_filings("AAPL", form="10-K")
        mock_company.assert_called_once_with("AAPL")
        mock_co.get_filings.assert_called_once_with(
            form="10-K", start=0, number_of_filings=100
        )
        assert result == [{"form": "10-K"}]

    @patch.object(edgar.EdgarClient, "company")
    def test_passes_pagination_params(self, mock_company):
        """Verify start and number_of_filings are forwarded."""
        edgar.set_user_agent("Test Agent test@example.com")
        mock_co = MagicMock()
        mock_co.get_filings.return_value = []
        mock_company.return_value = mock_co

        edgar.get_filings("MSFT", start=10, number_of_filings=50)
        mock_co.get_filings.assert_called_once_with(
            form=None, start=10, number_of_filings=50
        )

    @patch.object(edgar.EdgarClient, "company")
    def test_returns_all_filings_when_no_form(self, mock_company):
        """Verify form=None returns all filing types."""
        edgar.set_user_agent("Test Agent test@example.com")
        mock_co = MagicMock()
        mock_co.get_filings.return_value = [{"form": "10-K"}, {"form": "8-K"}]
        mock_company.return_value = mock_co

        result = edgar.get_filings("GOOG")
        assert len(result) == 2


# ---------------------------------------------------------------------------
# edgar.search() tests
# ---------------------------------------------------------------------------


class TestSearchConvenience:
    """Tests for the module-level edgar.search() function."""

    @patch.object(edgar.EdgarClient, "search")
    def test_delegates_to_client_search(self, mock_search):
        """Verify edgar.search() calls EdgarClient.search()."""
        edgar.set_user_agent("Test Agent test@example.com")
        mock_search.return_value = [MagicMock()]

        result = edgar.search("revenue recognition", form_types=["10-K"])
        mock_search.assert_called_once_with(
            q="revenue recognition",
            form_types=["10-K"],
            start_date=None,
            end_date=None,
            start=0,
            size=100,
        )
        assert len(result) == 1

    @patch.object(edgar.EdgarClient, "search")
    def test_passes_all_params(self, mock_search):
        """Verify all parameters are forwarded."""
        edgar.set_user_agent("Test Agent test@example.com")
        mock_search.return_value = []

        edgar.search(
            "climate risk",
            form_types=["10-K", "10-Q"],
            start_date="2024-01-01",
            end_date="2024-12-31",
            start=10,
            size=50,
        )
        mock_search.assert_called_once_with(
            q="climate risk",
            form_types=["10-K", "10-Q"],
            start_date="2024-01-01",
            end_date="2024-12-31",
            start=10,
            size=50,
        )


# ---------------------------------------------------------------------------
# __all__ exports
# ---------------------------------------------------------------------------


class TestExports:
    """Tests for the public API surface."""

    def test_all_contains_convenience_functions(self):
        """Verify __all__ includes the new convenience functions."""
        assert "company" in edgar.__all__
        assert "get_filings" in edgar.__all__
        assert "search" in edgar.__all__
        assert "set_user_agent" in edgar.__all__

    def test_all_preserves_existing_exports(self):
        """Verify __all__ still includes EdgarClient and exceptions."""
        assert "EdgarClient" in edgar.__all__
        assert "EdgarError" in edgar.__all__
        assert "EdgarRequestError" in edgar.__all__
        assert "EdgarParseError" in edgar.__all__
