"""Fluent Company interface for ticker-based SEC EDGAR access."""

from __future__ import annotations

import logging
from enum import Enum
from typing import TYPE_CHECKING, Union

from edgar.filings import Filings
from edgar.models import CompanyInfo, Facts, Filing
from edgar.submissions import Submissions
from edgar.xbrl import Xbrl

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from edgar.session import EdgarSession
    from edgar.tickers import Tickers


class Company:
    """A convenience wrapper around a single SEC-registered company.

    Resolves a ticker symbol or CIK to company metadata and provides
    fluent access to filings, submissions, and XBRL data without
    requiring callers to manage CIK numbers or service objects directly.

    ### Usage
    ----
        >>> edgar_client = EdgarClient(user_agent="Your Name your-email@example.com")
        >>> company = edgar_client.company("AAPL")
        >>> company.filings(form="10-K")
    """

    def __init__(
        self,
        identifier: str,
        session: EdgarSession,
        tickers_service: Tickers,
    ) -> None:
        """Initializes a ``Company`` from a ticker symbol or CIK number.

        ### Parameters
        ----
        identifier : str
            A stock ticker symbol (e.g. ``"AAPL"``) or a CIK number
            (e.g. ``"320193"``).

        session : EdgarSession
            The shared HTTP session.

        tickers_service : Tickers
            A ``Tickers`` instance used for resolution.
        """

        self._session = session
        self._tickers = tickers_service

        # Detect whether the identifier is a CIK (all digits) or a ticker.
        stripped = str(identifier).lstrip("0")
        if stripped.isdigit():
            # CIK path — resolve to get metadata.
            logger.debug("Resolving identifier as CIK: %s", identifier)
            entries = tickers_service.resolve_cik(identifier)
            self._cik: str = str(entries[0]["cik_str"]).zfill(10)
            self._ticker: str = entries[0]["ticker"]
            self._name: str = entries[0]["title"]
        else:
            # Ticker path — resolve to get CIK.
            logger.debug("Resolving identifier as ticker: %s", identifier)
            self._cik = tickers_service.resolve_ticker(identifier)
            self._ticker = identifier.upper()
            # Look up the company name from the resolved CIK.
            entries = tickers_service.resolve_cik(int(self._cik))
            self._name = entries[0]["title"]

    def __repr__(self) -> str:
        """String representation of the ``Company`` object."""

        return f"<Company ticker={self._ticker!r} cik={self._cik!r} name={self._name!r}>"

    @property
    def cik(self) -> str:
        """The zero-padded 10-digit CIK string."""
        return self._cik

    @property
    def ticker(self) -> str:
        """The primary ticker symbol."""
        return self._ticker

    @property
    def name(self) -> str:
        """The company name as registered with the SEC."""
        return self._name

    @property
    def cik_unpadded(self) -> str:
        """The CIK string with leading zeros stripped (for service methods that expect it)."""
        return self._cik.lstrip("0")

    def filings(
        self,
        form: Union[str, Enum, None] = None,
        start: int = 0,
        number_of_filings: int = 100,
    ) -> list[dict]:
        """Returns filings for this company, optionally filtered by form type.

        ### Parameters
        ----
        form : str | Enum | None (optional, Default=None)
            The filing form type (e.g. ``"10-K"``, ``"10-Q"``, ``"8-K"``).
            If ``None``, returns all filing types.

        start : int (optional, Default=0)
            Pagination offset.

        number_of_filings : int (optional, Default=100)
            Maximum number of filings to return.

        ### Returns
        ----
        list[dict]:
            A collection of filing resources.

        ### Usage
        ----
            >>> company = edgar_client.company("AAPL")
            >>> company.filings(form="10-K")
        """

        filings_service = Filings(session=self._session)

        if form is not None:
            return filings_service.get_filings_by_type(
                cik=self.cik_unpadded,
                filing_type=form,
                start=start,
                number_of_filings=number_of_filings,
            )

        return filings_service.get_filings_by_cik(
            cik=self.cik_unpadded,
            start=start,
            number_of_filings=number_of_filings,
        )

    def submissions(self) -> dict | None:
        """Returns the full submission history for this company.

        ### Returns
        ----
        dict | None:
            The submission metadata from the SEC submissions API.

        ### Usage
        ----
            >>> company = edgar_client.company("AAPL")
            >>> company.submissions()
        """

        submissions_service = Submissions(session=self._session)
        return submissions_service.get_submissions(cik=self.cik_unpadded)

    def xbrl_facts(self) -> dict | None:
        """Returns all XBRL company facts for this company.

        ### Returns
        ----
        dict | None:
            The company facts from the XBRL API.

        ### Usage
        ----
            >>> company = edgar_client.company("AAPL")
            >>> company.xbrl_facts()
        """

        xbrl_service = Xbrl(session=self._session)
        return xbrl_service.company_facts(cik=self.cik_unpadded)

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

        return self._session.download(url=url, path=path)

    def get_filings(
        self,
        form: Union[str, Enum, None] = None,
        start: int = 0,
        number_of_filings: int = 100,
    ) -> list:
        """Returns filings as structured ``Filing`` model objects.

        Same parameters as ``filings()`` but returns a list of ``Filing``
        dataclass instances instead of raw dictionaries.

        ### Returns
        ----
        list[Filing]:
            A list of ``Filing`` objects with typed properties.

        ### Usage
        ----
            >>> company = edgar_client.company("AAPL")
            >>> filings = company.get_filings(form="10-K")
            >>> filings[0].form_type
            '10-K'
        """

        raw_filings = self.filings(
            form=form, start=start, number_of_filings=number_of_filings
        )
        return [Filing(raw=entry) for entry in raw_filings]

    def get_info(self) -> object:
        """Returns structured company metadata as a ``CompanyInfo`` model.

        Fetches the full submissions response and wraps it in a
        ``CompanyInfo`` dataclass with typed property access.

        ### Returns
        ----
        CompanyInfo:
            A ``CompanyInfo`` object, or ``None`` if no data was returned.

        ### Usage
        ----
            >>> company = edgar_client.company("AAPL")
            >>> info = company.get_info()
            >>> info.name
            'Apple Inc.'
        """

        raw = self.submissions()
        if raw is None:
            return None
        return CompanyInfo(raw=raw)

    def get_facts(self) -> object:
        """Returns XBRL company facts as a structured ``Facts`` model.

        Wraps the raw ``xbrl_facts()`` response in a ``Facts``
        dataclass for convenient access by taxonomy, concept, and unit.

        ### Returns
        ----
        Facts | None:
            A ``Facts`` object, or ``None`` if no data was returned.

        ### Usage
        ----
            >>> company = edgar_client.company("AAPL")
            >>> facts = company.get_facts()
            >>> facts.get("us-gaap", "Revenue")
        """

        raw = self.xbrl_facts()
        if raw is None:
            return None
        return Facts(raw=raw)
