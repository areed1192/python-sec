"""Async entry-point client for the SEC EDGAR API.

Provides the same API surface as ``EdgarClient`` but with
``async``/``await`` support using ``httpx``. Install with::

    pip install python-sec[async]
"""

from __future__ import annotations

from enum import Enum
from typing import Union

from edgar.async_session import EdgarAsyncSession
from edgar.exceptions import EdgarRequestError
from edgar.models import CompanyInfo, Facts, Filing, SearchResult


class EdgarAsyncClient:
    """Async counterpart of ``EdgarClient``.

    Mirrors the synchronous client's API surface but all network
    methods are coroutines. Use within an ``async with`` block
    for proper resource cleanup.

    ### Usage
    ----
        >>> async with EdgarAsyncClient(user_agent="You you@example.com") as client:
        ...     filings = await client.get_filings("AAPL", form="10-K")
        ...     info = await client.get_company_info("AAPL")
    """

    def __init__(self, user_agent: str, rate_limit: int = 10) -> None:
        """Initializes the ``EdgarAsyncClient``.

        ### Parameters
        ----
        user_agent : str
            SEC EDGAR requires a User-Agent header in the format
            ``"Company/Name email@example.com"``.

        rate_limit : int (optional, Default=10)
            Maximum requests per second. SEC allows 10 req/s.
        """

        self.edgar_session = EdgarAsyncSession(
            client=self, user_agent=user_agent, rate_limit=rate_limit,
        )
        self._tickers_data: list[dict] | None = None
        self._ticker_to_cik: dict[str, int] | None = None
        self._cik_to_entries: dict[int, list[dict]] | None = None

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def close(self) -> None:
        """Closes the underlying HTTP client."""
        await self.edgar_session.close()

    def __repr__(self) -> str:
        return "<EdgarAsyncClient (active=True, connected=True)>"

    # ------------------------------------------------------------------
    # Ticker resolution
    # ------------------------------------------------------------------

    async def _load_tickers(self) -> None:
        """Fetches and indexes the company tickers data from SEC."""

        if self._tickers_data is not None:
            return

        raw = await self.edgar_session.make_request(
            method="get",
            endpoint="/files/company_tickers.json",
        )

        if raw is None:
            raise EdgarRequestError("Failed to load company tickers from SEC.")

        entries = list(raw.values())
        self._tickers_data = entries
        self._ticker_to_cik = {
            e["ticker"].upper(): e["cik_str"] for e in entries
        }
        self._cik_to_entries = {}
        for entry in entries:
            cik_int = int(entry["cik_str"])
            self._cik_to_entries.setdefault(cik_int, []).append(entry)

    async def resolve_ticker(self, ticker: str) -> str:
        """Resolves a ticker symbol to a zero-padded 10-digit CIK string.

        ### Parameters
        ----
        ticker : str
            A stock ticker symbol (e.g. ``"AAPL"``).

        ### Returns
        ----
        str:
            The zero-padded CIK string.
        """

        await self._load_tickers()
        upper = ticker.upper()
        cik_int = self._ticker_to_cik.get(upper)
        if cik_int is None:
            raise EdgarRequestError(f"Ticker not found: {ticker!r}")
        return str(cik_int).zfill(10)

    async def resolve_cik(self, cik: str | int) -> list[dict]:
        """Resolves a CIK to company information.

        ### Parameters
        ----
        cik : str | int
            A CIK number.

        ### Returns
        ----
        list[dict]:
            Entries with keys: ``cik_str``, ``ticker``, ``title``.
        """

        await self._load_tickers()
        cik_int = int(str(cik).lstrip("0"))
        entries = self._cik_to_entries.get(cik_int, [])
        if not entries:
            raise EdgarRequestError(f"CIK not found: {cik!r}")
        return entries

    # ------------------------------------------------------------------
    # Company info
    # ------------------------------------------------------------------

    async def get_company_info(self, identifier: str) -> CompanyInfo | None:
        """Returns company metadata for a ticker or CIK.

        ### Parameters
        ----
        identifier : str
            A stock ticker (e.g. ``"AAPL"``) or CIK number.

        ### Returns
        ----
        CompanyInfo | None
        """

        cik = await self._resolve_to_cik(identifier)
        padded = cik.zfill(10)
        raw = await self.edgar_session.make_request(
            method="get",
            endpoint=f"/submissions/CIK{padded}.json",
            use_api=True,
        )
        if raw is None:
            return None
        return CompanyInfo(raw=raw)

    # ------------------------------------------------------------------
    # Filings
    # ------------------------------------------------------------------

    async def get_filings(
        self,
        identifier: str,
        form: Union[str, Enum, None] = None,
        start: int = 0,
        count: int = 100,
    ) -> list[Filing]:
        """Returns filings for a company, optionally filtered by form type.

        ### Parameters
        ----
        identifier : str
            A stock ticker (e.g. ``"AAPL"``) or CIK number.

        form : str | Enum | None (optional, Default=None)
            Filter by form type (e.g. ``"10-K"``).

        start : int (optional, Default=0)
            Pagination offset.

        count : int (optional, Default=100)
            Maximum number of filings to return.

        ### Returns
        ----
        list[Filing]
        """

        cik = await self._resolve_to_cik(identifier)
        cik_unpadded = cik.lstrip("0")

        params = {
            "action": "getcompany",
            "CIK": cik_unpadded,
            "start": start,
            "count": count,
            "output": "atom",
        }
        if form is not None:
            form_value = form.value if isinstance(form, Enum) else form
            params["type"] = form_value

        raw = await self.edgar_session.make_request(
            method="get",
            endpoint="/cgi-bin/browse-edgar",
            params=params,
        )

        if raw is None:
            return []

        entries = self.edgar_session.edgar_parser.parse_entries(
            response_text=raw,
            fetch_page=None,
        )
        return [Filing(raw=entry) for entry in entries]

    # ------------------------------------------------------------------
    # XBRL facts
    # ------------------------------------------------------------------

    async def get_facts(self, identifier: str) -> Facts | None:
        """Returns XBRL company facts for a ticker or CIK.

        ### Parameters
        ----
        identifier : str
            A stock ticker (e.g. ``"AAPL"``) or CIK number.

        ### Returns
        ----
        Facts | None
        """

        cik = await self._resolve_to_cik(identifier)
        padded = cik.zfill(10)
        raw = await self.edgar_session.make_request(
            method="get",
            endpoint=f"/api/xbrl/companyfacts/CIK{padded}.json",
            use_api=True,
        )
        if raw is None:
            return None
        return Facts(raw=raw)

    # ------------------------------------------------------------------
    # Search
    # ------------------------------------------------------------------

    async def search(  # pylint: disable=too-many-positional-arguments
        self,
        q: str,
        form_types: list[str] | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        start: int = 0,
        size: int = 100,
    ) -> list[SearchResult]:
        """Full-text search across SEC EDGAR filings.

        ### Parameters
        ----
        q : str
            The search query.

        form_types : list[str] | None (optional)
            Filter by form types (e.g. ``["10-K", "10-Q"]``).

        start_date : str | None (optional)
            Start of date range (``YYYY-MM-DD``).

        end_date : str | None (optional)
            End of date range (``YYYY-MM-DD``).

        start : int (optional, Default=0)
            Pagination offset.

        size : int (optional, Default=100)
            Results per page.

        ### Returns
        ----
        list[SearchResult]
        """

        params: dict = {"q": q, "from": start, "size": size}
        if form_types:
            params["forms"] = ",".join(form_types)
        if start_date or end_date:
            params["dateRange"] = "custom"
            if start_date:
                params["startdt"] = start_date
            if end_date:
                params["enddt"] = end_date

        raw = await self.edgar_session.make_request(
            method="get",
            endpoint="/LATEST/search-index",
            params=params,
            base_url="https://efts.sec.gov",
        )

        if raw is None:
            return []

        hits = raw.get("hits", {}).get("hits", [])
        return [SearchResult(raw=hit) for hit in hits]

    # ------------------------------------------------------------------
    # Download
    # ------------------------------------------------------------------

    async def download(self, url: str, path: str | None = None) -> str | bytes:
        """Downloads a filing document from a full SEC URL.

        ### Parameters
        ----
        url : str
            The full URL to the filing document.

        path : str | None (optional, Default=None)
            If provided, saves content to this file path.

        ### Returns
        ----
        str | bytes
        """

        return await self.edgar_session.download(url=url, path=path)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    async def _resolve_to_cik(self, identifier: str) -> str:
        """Resolves a ticker or CIK string to a CIK string."""

        stripped = str(identifier).lstrip("0")
        if stripped.isdigit():
            return stripped.zfill(10)
        return await self.resolve_ticker(identifier)
