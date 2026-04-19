"""Main entry-point client for the SEC EDGAR API."""

import logging

from edgar.cache import TTLCache
from edgar.xbrl import Xbrl
from edgar.series import Series
from edgar.search import Search
from edgar.issuers import Issuers
from edgar.filings import Filings
from edgar.company import Company
from edgar.datasets import Datasets
from edgar.archives import Archives
from edgar.tickers import Tickers
from edgar.companies import Companies
from edgar.session import EdgarSession
from edgar.submissions import Submissions
from edgar.mutual_funds import MutualFunds
from edgar.current_events import CurrentEvents
from edgar.ownership_filings import OwnershipFilings
from edgar.variable_insurance_products import VariableInsuranceProducts

from edgar.models import SearchResult


logger = logging.getLogger(__name__)


class EdgarClient:
    """
    ## Overview
    ----
    Represents the main Edgar client which is used to
    instantiate the different endpoints.
    """

    def __init__(self, user_agent: str, rate_limit: int = 10, cache: bool = True) -> None:
        """Initializes the `EdgarClient`.

        ### Parameters
        ----
        user_agent : str
            SEC EDGAR requires a User-Agent header in the format
            ``"Company/Name email@example.com"``.

        rate_limit : int (optional, Default=10)
            Maximum requests per second. SEC allows 10 req/s.
            Set lower to be more conservative.

        cache : bool (optional, Default=True)
            Enable in-memory TTL caching for ticker resolution (24h),
            submission metadata (1h), and taxonomy data (24h).
            Set ``False`` to always fetch fresh data from SEC.

        ### Usage
        ----
            >>> edgar_client = EdgarClient(user_agent="Your Name your-email@example.com")
            >>> edgar_client = EdgarClient(user_agent="...", rate_limit=5)
            >>> edgar_client = EdgarClient(user_agent="...", cache=False)
        """

        self._ttl_cache = TTLCache() if cache else None
        self.edgar_session = EdgarSession(
            client=self, user_agent=user_agent, rate_limit=rate_limit,
            cache=self._ttl_cache,
        )
        self._services: dict = {}

        logger.debug(
            "EdgarClient initialized (rate_limit=%d, cache=%s)",
            rate_limit, cache,
        )

    def __repr__(self) -> str:
        """String representation of the `EdgarClient` object."""

        return "<EdgarClient (active=True, connected=True)>"

    def archives(self) -> Archives:
        """Used to access the `Archives` services.

        ### Returns
        ---
        Archives:
            The `Archives` services Object.
        """

        if "archives" not in self._services:
            self._services["archives"] = Archives(session=self.edgar_session)
        return self._services["archives"]

    def companies(self) -> Companies:
        """Used to access the `Companies` services.

        ### Returns
        ---
        Companies:
            The `Companies` services Object.
        """

        if "companies" not in self._services:
            self._services["companies"] = Companies(session=self.edgar_session)
        return self._services["companies"]

    def series(self) -> Series:
        """Used to access the `Series` services.

        ### Returns
        ---
        Series:
            The `Series` services Object.
        """

        if "series" not in self._services:
            self._services["series"] = Series(session=self.edgar_session)
        return self._services["series"]

    def mutual_funds(self) -> MutualFunds:
        """Used to access the `MutualFunds` services.

        ### Returns
        ---
        MutualFunds:
            The `MutualFunds` services Object.
        """

        if "mutual_funds" not in self._services:
            self._services["mutual_funds"] = MutualFunds(session=self.edgar_session)
        return self._services["mutual_funds"]

    def variable_insurance_products(self) -> VariableInsuranceProducts:
        """Used to access the `VariableInsuranceProducts` services.

        ### Returns
        ---
        VariableInsuranceProducts:
            The `VariableInsuranceProducts` services Object.
        """

        if "variable_insurance_products" not in self._services:
            self._services["variable_insurance_products"] = VariableInsuranceProducts(
                session=self.edgar_session
            )
        return self._services["variable_insurance_products"]

    def datasets(self) -> Datasets:
        """Used to access the `Datasets` services.

        ### Returns
        ---
        Datasets:
            The `Datasets` services Object.
        """

        if "datasets" not in self._services:
            self._services["datasets"] = Datasets(session=self.edgar_session)
        return self._services["datasets"]

    def filings(self) -> Filings:
        """Used to access the `Filings` services.

        ### Returns
        ---
        Filings:
            The `Filings` services Object.
        """

        if "filings" not in self._services:
            self._services["filings"] = Filings(session=self.edgar_session)
        return self._services["filings"]

    def current_events(self) -> CurrentEvents:
        """Used to access the `CurrentEvents` services.

        ### Returns
        ---
        CurrentEvents:
            The `CurrentEvents` services Object.
        """

        if "current_events" not in self._services:
            self._services["current_events"] = CurrentEvents(session=self.edgar_session)
        return self._services["current_events"]

    def issuers(self) -> Issuers:
        """Used to access the `Issuers` services.

        ### Returns
        ---
        Issuers:
            The `Issuers` services Object.
        """

        if "issuers" not in self._services:
            self._services["issuers"] = Issuers(session=self.edgar_session)
        return self._services["issuers"]

    def ownership_filings(self) -> OwnershipFilings:
        """Used to access the `OwnershipFilings` services.

        ### Returns
        ---
        OwnershipFilings:
            The `OwnershipFilings` services Object.
        """

        if "ownership_filings" not in self._services:
            self._services["ownership_filings"] = OwnershipFilings(
                session=self.edgar_session
            )
        return self._services["ownership_filings"]

    def submissions(self) -> Submissions:
        """Used to access the `Submissions` services.

        ### Returns
        ---
        Submissions:
            The `Submissions` services Object.
        """

        if "submissions" not in self._services:
            self._services["submissions"] = Submissions(session=self.edgar_session)
        return self._services["submissions"]

    def xbrl(self) -> Xbrl:
        """Used to access the `Xbrl` services.

        ### Returns
        ---
        Xbrl:
            The `Xbrl` services Object.
        """

        if "xbrl" not in self._services:
            self._services["xbrl"] = Xbrl(session=self.edgar_session)
        return self._services["xbrl"]

    def tickers(self) -> Tickers:
        """Used to access the `Tickers` services.

        ### Returns
        ---
        Tickers:
            The `Tickers` services Object.
        """

        if "tickers" not in self._services:
            self._services["tickers"] = Tickers(session=self.edgar_session)
        return self._services["tickers"]

    def company(self, identifier: str) -> Company:
        """Creates a ``Company`` object from a ticker symbol or CIK number.

        ### Parameters
        ----
        identifier : str
            A stock ticker symbol (e.g. ``"AAPL"``) or a CIK number
            (e.g. ``"320193"``).

        ### Returns
        ----
        Company:
            A fluent ``Company`` object for chaining.

        ### Usage
        ----
            >>> edgar_client.company("AAPL").filings(form="10-K")
        """

        return Company(
            identifier=identifier,
            session=self.edgar_session,
            tickers_service=self.tickers(),
        )

    def resolve_ticker(self, ticker: str) -> str:
        """Convenience method to resolve a ticker symbol to a CIK string.

        ### Parameters
        ----
        ticker : str
            A stock ticker symbol (e.g. "AAPL").

        ### Returns
        ----
        str:
            The zero-padded 10-digit CIK string.
        """

        return self.tickers().resolve_ticker(ticker)

    def resolve_cik(self, cik: str | int) -> list[dict]:
        """Convenience method to resolve a CIK to company information.

        ### Parameters
        ----
        cik : str | int
            A CIK number.

        ### Returns
        ----
        list[dict]:
            Entries with keys: cik_str, ticker, title.
        """

        return self.tickers().resolve_cik(cik)

    def download(self, url: str, path: str | None = None) -> str | bytes:
        """Downloads a filing document from a full SEC URL.

        ### Parameters
        ----
        url : str
            The full URL to the filing document.

        path : str | None (optional, Default=None)
            If provided, saves the content to this file path.

        ### Returns
        ----
        str | bytes:
            The document content, or the path if ``path`` was given.
        """

        return self.edgar_session.download(url=url, path=path)

    def full_text_search(self) -> Search:
        """Used to access the ``Search`` services (EDGAR Full-Text Search).

        ### Returns
        ---
        Search:
            The ``Search`` services Object.
        """

        if "search" not in self._services:
            self._services["search"] = Search(session=self.edgar_session)
        return self._services["search"]

    def search(
        self,
        q: str,
        form_types: list[str] | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        start: int = 0,
        size: int = 100,
    ) -> list:
        """Full-text search across SEC EDGAR filings.

        Convenience method wrapping the free EFTS endpoint at
        ``efts.sec.gov/LATEST/search-index``. Returns structured
        ``SearchResult`` objects with filing URLs, dates, and
        company information.

        ### Parameters
        ----
        q : str
            The search query. Use double quotes for exact phrase
            matching (e.g. ``'"revenue recognition"'``).

        form_types : list[str] | None (optional, Default=None)
            Filter by form types (e.g. ``["10-K", "10-Q"]``).

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
        list[SearchResult]:
            A list of ``SearchResult`` objects with typed properties.

        ### Usage
        ----
            >>> results = edgar_client.search(
            ...     q='"revenue recognition"',
            ...     form_types=["10-K"],
            ...     start_date="2024-01-01",
            ...     end_date="2024-12-31",
            ... )
            >>> results[0].company_name
            'Apple Inc.  (AAPL)  (CIK 0000320193)'
        """

        raw = self.full_text_search().full_text_search(
            q=q,
            form_types=form_types,
            start_date=start_date,
            end_date=end_date,
            start=start,
            size=size,
        )

        if raw is None:
            return []

        hits = raw.get("hits", {}).get("hits", [])
        return [SearchResult(raw=hit) for hit in hits]
