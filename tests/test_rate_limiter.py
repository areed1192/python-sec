"""Tests for the sliding-window rate limiter in EdgarSession."""

# Disable protected access warnings since we're testing internal behavior.
# pylint: disable=redefined-outer-name
# pylint: disable=protected-access
# pylint: disable=import-outside-toplevel

from unittest.mock import MagicMock, patch

import pytest

from edgar.session import EdgarSession, MAX_REQUESTS_PER_SECOND


@pytest.fixture
def session():
    """Return an EdgarSession with a mock client."""
    mock_client = MagicMock()
    return EdgarSession(client=mock_client, user_agent="Test Agent test@example.com")


# ---------------------------------------------------------------------------
# Configurable rate_limit tests
# ---------------------------------------------------------------------------


class TestConfigurableRateLimit:
    """Tests for the configurable rate_limit parameter."""

    def test_default_rate_limit(self, session):
        """Verify the default rate limit is MAX_REQUESTS_PER_SECOND."""
        assert session._rate_limit == MAX_REQUESTS_PER_SECOND

    def test_custom_rate_limit(self):
        """Verify a custom rate limit is stored."""
        mock_client = MagicMock()
        sess = EdgarSession(
            client=mock_client,
            user_agent="Test test@example.com",
            rate_limit=5,
        )
        assert sess._rate_limit == 5

    def test_custom_rate_limit_throttles_at_custom_value(self):
        """Verify throttle triggers at the custom rate, not the default."""
        mock_client = MagicMock()
        sess = EdgarSession(
            client=mock_client,
            user_agent="Test test@example.com",
            rate_limit=3,
        )
        with patch("edgar.session.time") as mock_time:
            mock_time.monotonic.return_value = 100.0
            for _ in range(3):
                sess._throttle()
            # 4th request at same time should trigger sleep.
            mock_time.monotonic.return_value = 100.0
            sess._throttle()
            mock_time.sleep.assert_called()

    def test_rate_limit_of_one(self):
        """Verify rate_limit=1 allows only one request per second."""
        mock_client = MagicMock()
        sess = EdgarSession(
            client=mock_client,
            user_agent="Test test@example.com",
            rate_limit=1,
        )
        with patch("edgar.session.time") as mock_time:
            mock_time.monotonic.return_value = 100.0
            sess._throttle()
            # Second request in the same instant should sleep.
            mock_time.monotonic.return_value = 100.0
            sess._throttle()
            mock_time.sleep.assert_called()

    def test_rate_limit_too_low_raises(self):
        """Verify rate_limit=0 raises ValueError."""
        mock_client = MagicMock()
        with pytest.raises(ValueError, match="rate_limit must be between 1 and"):
            EdgarSession(
                client=mock_client,
                user_agent="Test test@example.com",
                rate_limit=0,
            )

    def test_rate_limit_too_high_raises(self):
        """Verify rate_limit above MAX_REQUESTS_PER_SECOND raises ValueError."""
        mock_client = MagicMock()
        with pytest.raises(ValueError, match="rate_limit must be between 1 and"):
            EdgarSession(
                client=mock_client,
                user_agent="Test test@example.com",
                rate_limit=20,
            )

    def test_rate_limit_negative_raises(self):
        """Verify negative rate_limit raises ValueError."""
        mock_client = MagicMock()
        with pytest.raises(ValueError, match="rate_limit must be between 1 and"):
            EdgarSession(
                client=mock_client,
                user_agent="Test test@example.com",
                rate_limit=-1,
            )

    def test_client_passes_rate_limit_to_session(self):
        """Verify EdgarClient forwards rate_limit to EdgarSession."""
        from edgar.client import EdgarClient
        client = EdgarClient(
            user_agent="Test test@example.com", rate_limit=5
        )
        assert client.edgar_session._rate_limit == 5


class TestThrottleBasics:
    """Tests for the _throttle sliding-window algorithm."""

    def test_under_limit_no_sleep(self, session):
        """Requests under the limit should not trigger any sleep."""
        with patch("edgar.session.time") as mock_time:
            mock_time.monotonic.return_value = 100.0
            # Under the limit — no sleep should be called.
            for _ in range(MAX_REQUESTS_PER_SECOND - 1):
                session._throttle()
            mock_time.sleep.assert_not_called()

    def test_at_limit_triggers_sleep(self, session):
        """Hitting the limit within 1 second should trigger a sleep."""
        with patch("edgar.session.time") as mock_time:
            # All requests at the same instant.
            mock_time.monotonic.return_value = 100.0
            for _ in range(MAX_REQUESTS_PER_SECOND):
                session._throttle()

            # The next request should trigger a sleep.
            mock_time.monotonic.return_value = 100.5
            session._throttle()
            mock_time.sleep.assert_called()
            # Sleep duration should be ~0.5s (1.0 - 0.5 since oldest is at 100.0).
            sleep_arg = mock_time.sleep.call_args[0][0]
            assert 0.4 <= sleep_arg <= 0.6

    def test_expired_timestamps_are_discarded(self, session):
        """Timestamps older than 1 second should be pruned."""
        with patch("edgar.session.time") as mock_time:
            # Fill to capacity at t=100.
            mock_time.monotonic.return_value = 100.0
            for _ in range(MAX_REQUESTS_PER_SECOND):
                session._throttle()

            # At t=101.1, all prior timestamps are >1s old — should not sleep.
            mock_time.monotonic.return_value = 101.1
            session._throttle()
            mock_time.sleep.assert_not_called()

    def test_sliding_window_partial_expiry(self, session):
        """Only expired timestamps should be pruned; recent ones remain."""
        with patch("edgar.session.time") as mock_time:
            # 5 requests at t=100.0
            mock_time.monotonic.return_value = 100.0
            for _ in range(5):
                session._throttle()

            # 5 requests at t=100.6
            mock_time.monotonic.return_value = 100.6
            for _ in range(5):
                session._throttle()

            # At t=100.8 — the t=100.0 group is still within 1s.
            # Window has 10 requests, so the 11th should trigger sleep.
            mock_time.monotonic.return_value = 100.8
            session._throttle()
            mock_time.sleep.assert_called()

    def test_deque_tracks_request_count(self, session):
        """The internal deque should accurately track request timestamps."""
        with patch("edgar.session.time") as mock_time:
            mock_time.monotonic.return_value = 100.0
            for _ in range(5):
                session._throttle()
            assert len(session._request_times) == 5

    def test_rate_limit_value(self):
        """Verify MAX_REQUESTS_PER_SECOND is 10 per SEC policy."""
        assert MAX_REQUESTS_PER_SECOND == 10


class TestThrottleIntegration:
    """Tests that _throttle is called from all request paths."""

    def test_make_request_calls_throttle(self, session):
        """make_request() should invoke _throttle before sending."""
        session.http_session = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.ok = True
        mock_response.content = b'{"key": "value"}'
        mock_response.json.return_value = {"key": "value"}
        mock_response.headers = {"Content-Type": "application/json"}
        session.http_session.request.return_value = mock_response

        with patch.object(session, "_throttle") as mock_throttle:
            session.make_request(method="GET", endpoint="/test")
            mock_throttle.assert_called_once()

    def test_fetch_page_calls_throttle(self, session):
        """fetch_page() should invoke _throttle before sending."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"<html/>"
        session.http_session = MagicMock()
        session.http_session.get.return_value = mock_response

        with patch.object(session, "_throttle") as mock_throttle:
            session.fetch_page("https://www.sec.gov/test")
            mock_throttle.assert_called_once()

    def test_download_calls_throttle(self, session):
        """download() should invoke _throttle before sending."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "text/html"}
        mock_response.text = "<html/>"
        session.http_session = MagicMock()
        session.http_session.get.return_value = mock_response

        with patch.object(session, "_throttle") as mock_throttle:
            session.download("https://www.sec.gov/test")
            mock_throttle.assert_called_once()
