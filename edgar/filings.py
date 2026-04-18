"""Service for searching and retrieving SEC EDGAR filings."""

from __future__ import annotations

from enum import Enum
from typing import Union
from datetime import date
from datetime import datetime

from edgar.session import EdgarSession


class Filings:
    """
    ## Overview
    ----
    Public companies submit multiple types of filing
    through out the year. The `Filings` client helps
    easily query these filings and allows you to build
    custom queries.
    """

    def __init__(self, session: EdgarSession) -> None:
        """Initializes the `Filings` object.

        ### Parameters
        ----
        session : `EdgarSession`
            An initialized session of the `EdgarSession`.

        ### Usage
        ----
            >>> edgar_client = EdgarClient(user_agent="Your Name your-email@example.com")
            >>> filings_services = edgar_client.Filings()
        """

        # Set the session.
        self.edgar_session: EdgarSession = session
        self.edgar_utilities = session.edgar_utilities
        self.edgar_parser = session.edgar_parser

        # Set the endpoint.
        self.filings_endpoint = "/cgi-bin/filings"
        self.browse_endpoint = "/cgi-bin/browse-edgar"

    def __repr__(self) -> str:
        """String representation of the `EdgarClient.Filings` object."""

        # define the string representation
        str_representation = "<EdgarClient.Filings (active=True, connected=True)>"

        return str_representation

    def get_filings_by_cik(
        self, cik: str, start: int = 0, number_of_filings: int = 100
    ) -> list[dict]:
        """Returns a list of filings that fall under a specific CIK number.

        ### Parameters
        ----
        cik : str
            The company CIK number, defined by the SEC.

        number_of_filings : int (optional, Default=1000)
            Specifices the number of filings to return. If you want all filings
            then set to `None`. Be cautious though becuase you may be requesting
            100s of URLs.

        start: int (optional, Default=None)
            If you want to pick up where you left off from a previous parse, then
            set the `start` argument. This will start parsing the filings that come
            after this and up until the `number_of_filings`.

        ### Returns
        ----
        dict :
            A collection of `Filings` resources.

        ### Usage
        ----
            >>> edgar_client = EdgarClient(user_agent="Your Name your-email@example.com")
            >>> filings_services = edgar_client.filings()
            >>> filings_services.get_filings_by_cik(cik='814679')
        """

        params = {
            'action': 'getcompany',
            'output': 'atom',
            'CIK': cik,
            'start': start,
            'Count': '100',
        }

        # Grab the Data.
        response = self.edgar_session.make_request(
            method='get',
            endpoint=self.browse_endpoint,
            params=params,
        )

        # Parse it.
        response = self.edgar_parser.parse_entries(
            response_text=response,
            start=start,
            num_of_items=number_of_filings,
            fetch_page=self.edgar_session.fetch_page,
        )

        return response

    def get_filings_by_type(
        self,
        cik: str,
        filing_type: Union[str, Enum],
        start: int = 0,
        number_of_filings: int = 100,
    ) -> list[dict]:
        """Returns a list of filings that fall under a specific CIK number.

        ### Parameters
        ----
        cik : str
            The company CIK number, defined by the SEC.

        filing_type : Union[str, Enum] (optional, Default=None)
            The type of filing you want to query. The type is
            defined by the Filing code you pass through. For example,
            `10-k` represents annual filings.

        number_of_filings : int (optional, Default=1000)
            Specifices the number of filings to return. If you want all filings
            then set to `None`. Be cautious though becuase you may be requesting
            100s of URLs.

        start: int (optional, Default=None)
            If you want to pick up where you left off from a previous parse, then
            set the `start` argument. This will start parsing the filings that come
            after this and up until the `number_of_filings`.

        ### Returns
        ----
        dict :
            A collection of `Filings` resources.

        ### Usage
        ----
            >>> edgar_client = EdgarClient(user_agent="Your Name your-email@example.com")
            >>> filings_services = edgar_client.filings()
            >>> filings_services.get_filings_by_type(
                cik='814679',
                filing_type='10-k'
            )
        """

        if isinstance(filing_type, Enum):
            filing_type = filing_type.value

        params = {
            'action': 'getcompany',
            'output': 'atom',
            'CIK': cik,
            'type': filing_type,
            'start': start,
            'Count': '100',
        }

        # Grab the Data.
        response = self.edgar_session.make_request(
            method='get',
            endpoint=self.browse_endpoint,
            params=params,
        )

        # Parse it.
        response = self.edgar_parser.parse_entries(
            response_text=response,
            start=start,
            num_of_items=number_of_filings,
            fetch_page=self.edgar_session.fetch_page,
        )

        return response

    def query(
        self,
        cik: str = None,
        sic: str = None,
        filing_type: Union[str, Enum] = None,
        company_name: str = None,
        start: int = 0,
        number_of_filings: int = 100,
        after_date: Union[str, datetime, date] = None,
        before_date: Union[str, datetime, date] = None,
    ) -> list[dict]:
        """Allows for complex queries by giving access to all query parameters.

        ### Parameters
        ----
        cik : str (optional, Default=None)
            The CIK ID that you want to query.

        filing_type : Union[str, Enum] (optional, Default=None)
            The type of filing you want to query. The type is
            defined by the Filing code you pass through. For example,
            `10-k` represents annual filings.

        company_name : str (optional, Default=None)
            The company name you want to use as the basis of your search.

        number_of_filings : int (optional, Default=1000)
            Specifices the number of filings to return. If you want all filings
            then set to `None`. Be cautious though becuase you may be requesting
            100s of URLs.

        start: int (optional, Default=None)
            If you want to pick up where you left off from a previous parse, then
            set the `start` argument. This will start parsing the filings that come
            after this and up until the `number_of_filings`.

        before_date: Union[str, datetime, date] (optional, Default=None)
            Represents filings that you want before a certain date. For example,
            `2019-12-01` means return all the filings `BEFORE` Decemeber 1, 2019.

        after_date : Union[str, datetime, date] (optional, Default=None)
            Represents filings that you want after a certain date. For example,
            `2019-12-01` means return all the filings `AFTER` Decemeber 1, 2019.

        ### Returns
        ----
        List[dict]:
            A collection of `Filing` resources.

        ### Usage
        ----
            >>> edgar_client = EdgarClient(user_agent="Your Name your-email@example.com")
            >>> filings_services = edgar_client.filings()
            >>> filings_services.query(
                cik='C000005193'
                filing_type='10-k'
            )
        """

        if isinstance(filing_type, Enum):
            filing_type = filing_type.value

        if before_date:
            before_date = self.edgar_utilities.parse_dates(date_or_datetime=before_date)

        if after_date:
            after_date = self.edgar_utilities.parse_dates(date_or_datetime=after_date)

        params = {
            'action': 'getcompany',
            'output': 'atom',
            'start': start,
            'CIK': cik or '',
            'SIC': sic or '',
            'type': filing_type or '',
            'company': company_name or '',
            'Count': '100',
            'datea': after_date or '',
            'dateb': before_date or '',
        }

        # Grab the Data.
        response = self.edgar_session.make_request(
            method='get',
            endpoint=self.browse_endpoint,
            params=params,
        )

        # Parse the entries.
        entries = self.edgar_parser.parse_entries(
            response_text=response,
            num_of_items=number_of_filings,
            start=start,
            fetch_page=self.edgar_session.fetch_page,
        )

        return entries

    def get_filings_by_company_name(
        self, company_name: str, number_of_filings: int = 100, start: int = 0
    ) -> list[dict]:
        """Returns all the filings (ownership and non-ownership).

        ### Parameters
        ----
        company_name : str (optional, Default=None)
            The company name you want to use as the basis of your search.

        number_of_filings : int (optional, Default=1000)
            Specifices the number of filings to return. If you want all filings
            then set to `None`. Be cautious though becuase you may be requesting
            100s of URLs.

        start: int (optional, Default=None)
            If you want to pick up where you left off from a previous parse, then
            set the `start` argument. This will start parsing the filings that come
            after this and up until the `number_of_filings`.

        Returns:
        ----
        List[dict] -- A list of ownership filings.
        """

        params = {
            'action': 'getcompany',
            'output': 'atom',
            'company': company_name,
            'Count': '100',
        }

        # Grab the Data.
        response = self.edgar_session.make_request(
            method='get',
            endpoint=self.browse_endpoint,
            params=params,
        )

        # Parse the entries.
        entries = self.edgar_parser.parse_entries(
            response_text=response,
            num_of_items=number_of_filings,
            start=start,
            fetch_page=self.edgar_session.fetch_page,
        )

        return entries
