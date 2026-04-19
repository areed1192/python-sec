"""HTTP session management for SEC EDGAR requests."""

from __future__ import annotations

import logging
import time
from collections import deque
from typing import TYPE_CHECKING, Union

import requests
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

from edgar.exceptions import EdgarRequestError
from edgar.parser import EdgarParser
from edgar.utils import EdgarUtilities

if TYPE_CHECKING:
    from edgar.client import EdgarClient

logger = logging.getLogger(__name__)

MAX_RETRIES = 5
MAX_REQUESTS_PER_SECOND = 10


class EdgarSession:
    """
    Overview
    ----
    Serves as the main Session for the
    `EDGARClient`. The `EdgarSession` object
    handles all the requests made to EDGAR.
    """

    def __init__(
        self,
        client: EdgarClient,
        user_agent: str,
        rate_limit: int = MAX_REQUESTS_PER_SECOND,
        cache: object | None = None,
    ) -> None:
        """Initializes the `EdgarSession` client.

        ### Parameters
        ----
        client : EdgarClient
            The `edgar.EdgarClient` Python Client.

        user_agent : str
            SEC EDGAR User-Agent header value.

        rate_limit : int (optional, Default=MAX_REQUESTS_PER_SECOND)
            Maximum requests per second. Must be between 1 and 10.

        cache : TTLCache | None (optional, Default=None)
            Shared TTL cache instance. ``None`` disables caching.

        ### Usage
        ----
            >>> edgar_client = EdgarClient(user_agent="Your Name your-email@example.com")
            >>> edgar_session = EdgarSession(client=edgar_client, user_agent="your_user_agent")
        """

        if not 1 <= rate_limit <= MAX_REQUESTS_PER_SECOND:
            raise ValueError(
                f"rate_limit must be between 1 and {MAX_REQUESTS_PER_SECOND}, "
                f"got {rate_limit}"
            )

        self.client: EdgarClient = client
        self.resource = "https://www.sec.gov"
        self.api_resource = "https://data.sec.gov"
        self.user_agent = user_agent
        self.cache = cache

        # Sliding-window rate limiter: track timestamps of recent requests.
        self._request_times: deque[float] = deque()
        self._rate_limit = rate_limit

        # Create a single reusable session with connection pooling.
        self.http_session = requests.Session()
        self.http_session.verify = True
        self.http_session.headers.update({"user-agent": self.user_agent})

        # Mount retry adapter for resilience.
        retry_strategy = Retry(
            total=MAX_RETRIES,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.http_session.mount("https://", adapter)
        self.http_session.mount("http://", adapter)

        # Shared service dependencies.
        self.edgar_parser = EdgarParser()
        self.edgar_utilities = EdgarUtilities()

    def __repr__(self) -> str:
        """String representation of the `EdgarClient.EdgarSession` object."""

        # define the string representation
        str_representation = "<EdgarClient.EdgarSession (active=True, connected=True)>"

        return str_representation

    def build_url(
        self,
        endpoint: str,
        use_api: bool = False,
        base_url: str | None = None,
    ) -> str:
        """Builds the full url for the endpoint.

        ### Parameters
        ----
        endpoint : str
            The endpoint being requested.

        use_api : bool (optional, Default=False)
            If `True` use the API resource URL, `False`
            use the filings resource URL.

        base_url : str | None (optional, Default=None)
            If provided, overrides both ``use_api`` and the
            default resource URL.

        ### Returns
        ----
        str:
            The full URL with the endpoint needed.
        """

        if base_url:
            url = base_url + endpoint
        elif use_api:
            url = self.api_resource + endpoint
        else:
            url = self.resource + endpoint

        return url

    def make_request(
        self,
        method: str,
        endpoint: str,
        params: dict = None,
        data: dict = None,
        json_payload: dict = None,
        use_api: bool = False,
        base_url: str | None = None,
    ) -> Union[dict, str, None]:
        """Handles all the requests in the library.

        ### Overview
        ---
        A central function used to handle all the requests made in the library,
        this function handles building the URL, defining Content-Type, passing
        through payloads, and handling any errors that may arise during the request.

        ### Parameters
        ----
        method : str
            The Request method, can be one of the
            following: ['get','post','put','delete','patch']

        endpoint : str
            The API URL endpoint.

        params : dict (optional, Default=None)
            The URL params for the request.

        data : dict (optional, Default=None)
            A data payload for a request.

        json : dict (optional, Default=None)
            A json data payload for a request

        use_api : bool (optional, Default=False)
            If `True` use the API resource URL, `False`
            use the filings resource URL.

        ### Returns
        ----
            A Dictionary object containing the JSON values.
        """

        # Build the URL.
        url = self.build_url(endpoint=endpoint, use_api=use_api, base_url=base_url)

        logger.debug("URL: %s", url)
        logger.debug("Parameters: %s", params)

        # Build the request kwargs.
        request_kwargs = {
            "method": method.upper(),
            "url": url,
            "params": params,
            "data": data,
            "json": json_payload,
        }

        # Enforce SEC rate limit before sending.
        self._throttle()

        # Send the request with retry logic.
        try:
            response: requests.Response = self.http_session.request(**request_kwargs)
        except requests.RequestException as exc:
            logger.error("Request failed: %s", exc)
            raise EdgarRequestError(f"Request to {url} failed: {exc}") from exc

        # Retry on non-200 with backoff, up to MAX_RETRIES.
        retries = 0
        while response.status_code != 200 and retries < MAX_RETRIES:
            retries += 1
            sleep_time = 2**retries
            logger.warning(
                "Non-200 status %s, retry %s/%s in %ss",
                response.status_code,
                retries,
                MAX_RETRIES,
                sleep_time,
            )
            time.sleep(sleep_time)

            try:
                response = self.http_session.request(**request_kwargs)
            except requests.RequestException as exc:
                logger.error("Retry %s failed: %s", retries, exc)
                if retries >= MAX_RETRIES:
                    raise EdgarRequestError(
                        f"Request to {url} failed after {MAX_RETRIES} retries: {exc}"
                    ) from exc
                continue

        if response.status_code != 200:
            try:
                response.raise_for_status()
            except requests.HTTPError as exc:
                raise EdgarRequestError(
                    f"Request to {url} returned status {response.status_code}"
                ) from exc

        # Grab the headers.
        response_headers = response.headers
        content_type = response_headers.get("Content-Type", "")

        # If it's okay and has content.
        if response.ok and len(response.content) > 0:

            if "application/json" in content_type:
                return response.json()
            elif any(
                ct in content_type
                for ct in [
                    "application/atom+xml",
                    "application/xml",
                    "text/xml",
                    "text/html",
                ]
            ):
                return response.text

        return None

    def _throttle(self) -> None:
        """Enforces the SEC rate limit using a sliding-window algorithm.

        Tracks the timestamp of each outgoing request in a deque.
        If ``MAX_REQUESTS_PER_SECOND`` requests have been made within
        the last 1-second window, sleeps until the oldest one falls
        outside the window.
        """

        now = time.monotonic()

        # Discard timestamps older than 1 second.
        while self._request_times and (now - self._request_times[0]) >= 1.0:
            self._request_times.popleft()

        # If at capacity, wait until the oldest request exits the window.
        if len(self._request_times) >= self._rate_limit:
            sleep_duration = 1.0 - (now - self._request_times[0])
            if sleep_duration > 0:
                logger.debug(
                    "Rate limit: %d requests in window, sleeping %.3fs",
                    len(self._request_times),
                    sleep_duration,
                )
                time.sleep(sleep_duration)
            # After sleeping, discard expired timestamps again.
            now = time.monotonic()
            while self._request_times and (now - self._request_times[0]) >= 1.0:
                self._request_times.popleft()

        self._request_times.append(time.monotonic())

    def fetch_page(self, url: str) -> bytes | None:
        """Fetches a raw page by URL, returning bytes or None on failure.

        Used as a callback for parser pagination so the parser
        does not need its own HTTP session.
        """

        self._throttle()

        try:
            response = self.http_session.get(url)
        except requests.RequestException as exc:
            raise EdgarRequestError(f"Failed to fetch page {url}: {exc}") from exc

        if response.status_code == 200:
            return response.content
        return None

    def download(self, url: str, path: str | None = None) -> str | bytes:
        """Downloads a filing document from a full SEC URL.

        ### Parameters
        ----
        url : str
            The full URL to the filing document.

        path : str | None (optional, Default=None)
            If provided, saves the content to this file path
            and returns the path. Otherwise returns the content.

        ### Returns
        ----
        str | bytes:
            The document content as text (for HTML/XML/text)
            or bytes (for binary content like PDF).
            If ``path`` is given, returns the path string.
        """

        self._throttle()

        try:
            response = self.http_session.get(url)
        except requests.RequestException as exc:
            raise EdgarRequestError(f"Failed to download {url}: {exc}") from exc

        if response.status_code != 200:
            raise EdgarRequestError(
                f"Download from {url} returned status {response.status_code}"
            )

        content_type = response.headers.get("Content-Type", "")
        is_text = any(
            ct in content_type for ct in ["text/", "application/json", "application/xml"]
        )
        content = response.text if is_text else response.content

        if path is not None:
            mode = "w" if is_text else "wb"
            encoding = "utf-8" if is_text else None
            with open(path, mode, encoding=encoding) as f:
                f.write(content)
            return path

        return content
