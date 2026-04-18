"""Ticker and company name resolution via SEC EDGAR."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from edgar.cache import TTL_TICKERS
from edgar.exceptions import EdgarRequestError

if TYPE_CHECKING:
    from edgar.session import EdgarSession

logger = logging.getLogger(__name__)

TICKERS_ENDPOINT = "/files/company_tickers.json"
_CACHE_KEY = "tickers"


class Tickers:
    """Resolves tickers, CIK numbers, and company names using the SEC company_tickers.json file."""

    def __init__(self, session: EdgarSession) -> None:
        self._session = session
        self._data: list[dict] | None = None
        self._ticker_to_cik: dict[str, int] | None = None
        self._cik_to_entries: dict[int, list[dict]] | None = None

    def _load(self) -> None:
        """Fetches and indexes the company tickers data from SEC."""

        if self._data is not None:
            return

        # Check TTL cache for previously fetched data.
        cache = self._session.cache
        if cache is not None:
            cached = cache.get(_CACHE_KEY)
            if cached is not None:
                self._data, self._ticker_to_cik, self._cik_to_entries = cached
                return

        raw = self._session.make_request(
            method="GET",
            endpoint=TICKERS_ENDPOINT,
            use_api=False,
        )

        if not isinstance(raw, dict):
            raise EdgarRequestError("Failed to fetch company tickers data from SEC.")

        self._data = list(raw.values())

        self._ticker_to_cik = {}
        self._cik_to_entries = {}

        for entry in self._data:
            ticker = entry["ticker"].upper()
            cik = entry["cik_str"]

            if ticker not in self._ticker_to_cik:
                self._ticker_to_cik[ticker] = cik

            self._cik_to_entries.setdefault(cik, []).append(entry)

        # Store in TTL cache for reuse across service re-instantiations.
        if cache is not None:
            cache.set(
                _CACHE_KEY,
                (self._data, self._ticker_to_cik, self._cik_to_entries),
                TTL_TICKERS,
            )

    def resolve_ticker(self, ticker: str) -> str:
        """Resolves a ticker symbol to a zero-padded CIK string.

        ### Parameters
        ----
        ticker : str
            A stock ticker symbol (e.g. "AAPL").

        ### Returns
        ----
        str:
            The zero-padded 10-digit CIK string.

        ### Raises
        ----
        ValueError:
            If the ticker is not found.
        """

        self._load()
        ticker_upper = ticker.upper()
        cik = self._ticker_to_cik.get(ticker_upper)

        if cik is None:
            raise ValueError(f"Ticker '{ticker}' not found in SEC company tickers.")

        return str(cik).zfill(10)

    def resolve_cik(self, cik: str | int) -> list[dict]:
        """Resolves a CIK number to company information.

        ### Parameters
        ----
        cik : str | int
            A CIK number (e.g. "320193" or 320193).

        ### Returns
        ----
        list[dict]:
            A list of entries with keys: cik_str, ticker, title.

        ### Raises
        ----
        ValueError:
            If the CIK is not found.
        """

        self._load()
        cik_int = int(str(cik).lstrip("0")) if str(cik).lstrip("0") else 0
        entries = self._cik_to_entries.get(cik_int)

        if entries is None:
            raise ValueError(f"CIK '{cik}' not found in SEC company tickers.")

        return entries

    def search(self, query: str) -> list[dict]:
        """Searches company names and tickers for a query string.

        ### Parameters
        ----
        query : str
            A case-insensitive search string.

        ### Returns
        ----
        list[dict]:
            Matching entries with keys: cik_str, ticker, title.
        """

        self._load()
        query_lower = query.lower()

        return [
            entry
            for entry in self._data
            if query_lower in entry["title"].lower()
            or query_lower in entry["ticker"].lower()
        ]
