"""Async HTTP session management for SEC EDGAR requests."""

from __future__ import annotations

import asyncio
import logging
from collections import deque
from typing import TYPE_CHECKING, Union

from edgar.exceptions import EdgarRequestError
from edgar.parser import EdgarParser
from edgar.utils import EdgarUtilities

if TYPE_CHECKING:
    from edgar.async_client import EdgarAsyncClient

logger = logging.getLogger(__name__)

MAX_RETRIES = 5
MAX_REQUESTS_PER_SECOND = 10


def _require_httpx():
    """Import and return the ``httpx`` module, raising a helpful error if missing."""
    try:
        import httpx  # pylint: disable=import-outside-toplevel
        return httpx
    except ImportError as exc:
        raise ImportError(
            "httpx is required for the async client. "
            "Install it with: pip install python-sec[async]"
        ) from exc


class EdgarAsyncSession:
    """Async counterpart of ``EdgarSession``.

    Uses ``httpx.AsyncClient`` for non-blocking HTTP and
    ``asyncio.sleep`` for rate limiting.
    """

    def __init__(
        self,
        client: EdgarAsyncClient,
        user_agent: str,
        rate_limit: int = MAX_REQUESTS_PER_SECOND,
    ) -> None:
        """Initializes the ``EdgarAsyncSession``.

        ### Parameters
        ----
        client : EdgarAsyncClient
            The parent async client.

        user_agent : str
            SEC EDGAR User-Agent header value.

        rate_limit : int (optional, Default=10)
            Maximum requests per second (1–10).
        """

        if not 1 <= rate_limit <= MAX_REQUESTS_PER_SECOND:
            raise ValueError(
                f"rate_limit must be between 1 and {MAX_REQUESTS_PER_SECOND}, "
                f"got {rate_limit}"
            )

        httpx = _require_httpx()

        self.client = client
        self.resource = "https://www.sec.gov"
        self.api_resource = "https://data.sec.gov"
        self.user_agent = user_agent

        self._request_times: deque[float] = deque()
        self._rate_limit = rate_limit

        transport = httpx.AsyncHTTPTransport(retries=MAX_RETRIES)
        self.http_client = httpx.AsyncClient(
            headers={"user-agent": self.user_agent},
            transport=transport,
            timeout=30.0,
            follow_redirects=True,
        )

        self.edgar_parser = EdgarParser()
        self.edgar_utilities = EdgarUtilities()

    def __repr__(self) -> str:
        return "<EdgarAsyncClient.EdgarAsyncSession (active=True, connected=True)>"

    def build_url(
        self,
        endpoint: str,
        use_api: bool = False,
        base_url: str | None = None,
    ) -> str:
        """Builds the full URL for the endpoint."""

        if base_url:
            return base_url + endpoint
        if use_api:
            return self.api_resource + endpoint
        return self.resource + endpoint

    async def make_request(  # pylint: disable=too-many-positional-arguments
        self,
        method: str,
        endpoint: str,
        params: dict = None,
        data: dict = None,
        json_payload: dict = None,
        use_api: bool = False,
        base_url: str | None = None,
    ) -> Union[dict, str, None]:
        """Async equivalent of ``EdgarSession.make_request``.

        ### Parameters
        ----
        method : str
            HTTP method (``'get'``, ``'post'``, etc.).

        endpoint : str
            The API URL endpoint.

        params : dict (optional)
            URL query parameters.

        data : dict (optional)
            Form data payload.

        json_payload : dict (optional)
            JSON payload.

        use_api : bool (optional, Default=False)
            Use the ``data.sec.gov`` API resource.

        base_url : str | None (optional)
            Override the base URL entirely.

        ### Returns
        ----
        dict | str | None
        """

        url = self.build_url(endpoint=endpoint, use_api=use_api, base_url=base_url)

        logger.debug("URL: %s", url)
        logger.debug("Parameters: %s", params)

        await self._throttle()

        httpx = _require_httpx()

        try:
            response = await self.http_client.request(
                method=method.upper(),
                url=url,
                params=params,
                data=data,
                json=json_payload,
            )
        except httpx.HTTPError as exc:
            raise EdgarRequestError(f"Request to {url} failed: {exc}") from exc

        retries = 0
        while response.status_code != 200 and retries < MAX_RETRIES:
            retries += 1
            sleep_time = 2 ** retries
            logger.warning(
                "Non-200 status %s, retry %s/%s in %ss",
                response.status_code,
                retries,
                MAX_RETRIES,
                sleep_time,
            )
            await asyncio.sleep(sleep_time)

            try:
                response = await self.http_client.request(
                    method=method.upper(),
                    url=url,
                    params=params,
                    data=data,
                    json=json_payload,
                )
            except httpx.HTTPError as exc:
                if retries >= MAX_RETRIES:
                    raise EdgarRequestError(
                        f"Request to {url} failed after {MAX_RETRIES} retries: {exc}"
                    ) from exc
                continue

        if response.status_code != 200:
            raise EdgarRequestError(
                f"Request to {url} returned status {response.status_code}"
            )

        content_type = response.headers.get("content-type", "")

        if len(response.content) > 0:
            if "application/json" in content_type:
                return response.json()
            if any(
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

    async def fetch_page(self, url: str) -> bytes | None:
        """Fetches a raw page by URL, returning bytes or None."""

        await self._throttle()
        httpx = _require_httpx()

        try:
            response = await self.http_client.get(url)
        except httpx.HTTPError as exc:
            raise EdgarRequestError(f"Failed to fetch page {url}: {exc}") from exc

        if response.status_code == 200:
            return response.content
        return None

    async def download(self, url: str, path: str | None = None) -> str | bytes:
        """Downloads a filing document from a full SEC URL.

        ### Parameters
        ----
        url : str
            The full URL to the filing document.

        path : str | None (optional, Default=None)
            If provided, saves the content to this file path.

        ### Returns
        ----
        str | bytes
        """

        await self._throttle()
        httpx = _require_httpx()

        try:
            response = await self.http_client.get(url)
        except httpx.HTTPError as exc:
            raise EdgarRequestError(f"Failed to download {url}: {exc}") from exc

        if response.status_code != 200:
            raise EdgarRequestError(
                f"Download from {url} returned status {response.status_code}"
            )

        content_type = response.headers.get("content-type", "")
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

    async def close(self) -> None:
        """Closes the underlying httpx client."""
        await self.http_client.aclose()

    async def _throttle(self) -> None:
        """Async rate limiter using a sliding-window algorithm."""

        loop = asyncio.get_event_loop()
        now = loop.time()

        while self._request_times and (now - self._request_times[0]) >= 1.0:
            self._request_times.popleft()

        if len(self._request_times) >= self._rate_limit:
            sleep_duration = 1.0 - (now - self._request_times[0])
            if sleep_duration > 0:
                logger.debug(
                    "Rate limit: %d requests in window, sleeping %.3fs",
                    len(self._request_times),
                    sleep_duration,
                )
                await asyncio.sleep(sleep_duration)
            now = loop.time()
            while self._request_times and (now - self._request_times[0]) >= 1.0:
                self._request_times.popleft()

        self._request_times.append(loop.time())
