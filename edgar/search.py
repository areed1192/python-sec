"""Service for full-text search across SEC EDGAR filings via EFTS."""

from __future__ import annotations

from edgar.session import EdgarSession

EFTS_BASE_URL = "https://efts.sec.gov"


class Search:
    """
    ## Overview
    ----
    Wraps the SEC EDGAR Full-Text Search System (EFTS) at
    ``efts.sec.gov/LATEST/search-index``. This is a free,
    public endpoint — no API key required.

    Supports keyword and phrase search across all EDGAR filings,
    with optional filtering by form type, date range, and pagination.
    """

    def __init__(self, session: EdgarSession) -> None:
        """Initializes the ``Search`` service.

        ### Parameters
        ----
        session : EdgarSession
            An initialized session of the ``EdgarSession``.
        """

        self.edgar_session: EdgarSession = session

    def __repr__(self) -> str:
        """String representation of the ``Search`` service."""

        return "<EdgarClient.Search (active=True, connected=True)>"

    def full_text_search(
        self,
        q: str,
        form_types: list[str] | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        start: int = 0,
        size: int = 100,
    ) -> dict | None:
        """Searches EDGAR filings by keyword or phrase.

        ### Parameters
        ----
        q : str
            The search query. Use double quotes for exact
            phrase matching (e.g. ``'"revenue recognition"'``).

        form_types : list[str] | None (optional, Default=None)
            Filter by form types (e.g. ``["10-K", "10-Q"]``).
            If ``None``, searches across all form types.

        start_date : str | None (optional, Default=None)
            Start of date range filter (``YYYY-MM-DD``).

        end_date : str | None (optional, Default=None)
            End of date range filter (``YYYY-MM-DD``).

        start : int (optional, Default=0)
            Pagination offset.

        size : int (optional, Default=100)
            Number of results per page (max 100).

        ### Returns
        ----
        dict | None:
            The raw EFTS JSON response containing ``hits``,
            ``aggregations``, and query metadata.

        ### Usage
        ----
            >>> search_service = edgar_client.full_text_search()
            >>> results = search_service.full_text_search(
            ...     q='"revenue recognition"',
            ...     form_types=["10-K"],
            ...     start_date="2024-01-01",
            ...     end_date="2024-12-31",
            ... )
        """

        params: dict = {
            "q": q,
            "from": start,
            "size": size,
        }

        if form_types:
            params["forms"] = ",".join(form_types)

        if start_date or end_date:
            params["dateRange"] = "custom"
            if start_date:
                params["startdt"] = start_date
            if end_date:
                params["enddt"] = end_date

        return self.edgar_session.make_request(
            method="get",
            endpoint="/LATEST/search-index",
            params=params,
            base_url=EFTS_BASE_URL,
        )
