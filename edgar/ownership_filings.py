"""Service for querying SEC EDGAR ownership and non-ownership filings."""

from __future__ import annotations

from typing import Union
from datetime import date
from datetime import datetime

from enum import Enum
from edgar.session import EdgarSession


class OwnershipFilings():

    """
    ## Overview
    ----
    Queries the SEC EDGAR full-text search system for ownership
    (Section 16) and non-ownership filings, with support for
    filtering by CIK, company name, SIC code, and filing type.
    """

    def __init__(self, session: EdgarSession) -> None:
        """Initializes the `OwnershipFilings` object.

        ### Parameters
        ----
        session : `EdgarSession`
            An initialized session of the `EdgarSession`.

        ### Usage
        ----
            >>> edgar_client = EdgarClient(user_agent="Your Name your-email@example.com")
            >>> ownership_filings_services = edgar_client.ownership_filings()
        """

        # Set the session.
        self.edgar_session: EdgarSession = session
        self.edgar_utilities = session.edgar_utilities
        self.edgar_parser = session.edgar_parser

        # Set the endpoint.
        self.endpoint = '/cgi-bin/browse-edgar'

    def __repr__(self) -> str:
        """String representation of the `EdgarClient.OwnershipFilings` object."""

        # define the string representation
        str_representation = '<EdgarClient.OwnershipFilings (active=True, connected=True)>'

        return str_representation

    def get_ownership_filings_by_cik(
        self,
        cik: str,
        number_of_filings: int = 100,
        start: int = 0
    ) -> list[dict]:
        """Returns all the ownership filings for a given CIK number.

        ### Parameters
        ----
        cik : str
            The CIK number you want to query ownership filings for.

        number_of_filings : int (optional, Default=100)
            Specifices the number of filings to return. If you want all filings
            then set to `None`. Be cautious though becuase you may be requesting
            100s of URLs.

        start: int (optional, Default=0)
            If you want to pick up where you left off from a previous parse, then
            set the `start` argument. This will start parsing the companies that come
            after this and up until the `number_of_filings`.

        ### Returns
        ----
        dict :
            A collection of `OwnershipFiling` resource objects.

        ### Usage
        ----
            >>> edgar_client = EdgarClient(user_agent="Your Name your-email@example.com")
            >>> ownership_filings_services = edgar_client.ownership_filings()
            >>> ownership_filings_services.get_ownership_filings_by_cik(
               cik='1326801'
            )
        """

        params = {
            'action': 'getcompany',
            'output': 'atom',
            'Count': '100',
            'myowner': 'only',
            'CIK': cik,
        }

        # Grab the Data.
        response = self.edgar_session.make_request(
            method='get',
            endpoint=self.endpoint,
            params=params,
        )

        # Parse it.
        response = self.edgar_parser.parse_entries(
            response_text=response,
            num_of_items=number_of_filings,
            start=start,
            fetch_page=self.edgar_session.fetch_page,
        )

        return response

    def get_ownership_filings_by_name(
        self,
        company_name: str,
        number_of_filings: int = 100,
        start: int = 0
    ) -> list[dict]:
        """Returns all the ownership filings for a given company name.

        ### Parameters
        ----
        company_name : str
            The company nameyou want to query ownership filings for.

        number_of_filings : int (optional, Default=100)
            Specifices the number of filings to return. If you want all filings
            then set to `None`. Be cautious though becuase you may be requesting
            100s of URLs.

        start: int (optional, Default=0)
            If you want to pick up where you left off from a previous parse, then
            set the `start` argument. This will start parsing the companies that come
            after this and up until the `number_of_filings`.

        ### Returns
        ----
        dict :
            A collection of `OwnershipFiling` resource objects.

        ### Usage
        ----
            >>> edgar_client = EdgarClient(user_agent="Your Name your-email@example.com")
            >>> ownership_filings_services = edgar_client.ownership_filings()
            >>> ownership_filings_services.get_ownership_filings_by_cik(
               company_name='facebook'
            )
        """

        params = {
            'action': 'getcompany',
            'output': 'atom',
            'Count': '100',
            'myowner': 'only',
            'company': company_name,
        }

        # Grab the Data.
        response = self.edgar_session.make_request(
            method='get',
            endpoint=self.endpoint,
            params=params,
        )

        # Parse it.
        response = self.edgar_parser.parse_entries(
            response_text=response,
            num_of_items=number_of_filings,
            start=start,
            fetch_page=self.edgar_session.fetch_page,
        )

        return response

    def get_non_ownership_filings_by_cik(
        self,
        cik: str,
        number_of_filings: int = 100,
        start: int = 0
    ) -> list[dict]:
        """Returns all the non-ownership filings for a given CIK number.

        ### Parameters
        ----
        cik : str
            The CIK number you want to query ownership filings for.

        number_of_filings : int (optional, Default=100)
            Specifices the number of filings to return. If you want all filings
            then set to `None`. Be cautious though becuase you may be requesting
            100s of URLs.

        start: int (optional, Default=0)
            If you want to pick up where you left off from a previous parse, then
            set the `start` argument. This will start parsing the companies that come
            after this and up until the `number_of_filings`.

        ### Returns
        ----
        dict :
            A collection of `NonOwnershipFiling` resource objects.

        ### Usage
        ----
            >>> edgar_client = EdgarClient(user_agent="Your Name your-email@example.com")
            >>> ownership_filings_services = edgar_client.ownership_filings()
            >>> ownership_filings_services.get_non_ownership_filings_by_cik(
               cik='1326801'
            )
        """

        params = {
            'action': 'getcompany',
            'output': 'atom',
            'Count': '100',
            'myowner': 'exclude',
            'CIK': cik,
        }

        # Grab the Data.
        response = self.edgar_session.make_request(
            method='get',
            endpoint=self.endpoint,
            params=params,
        )

        # Parse it.
        response = self.edgar_parser.parse_entries(
            response_text=response,
            num_of_items=number_of_filings,
            start=start,
            fetch_page=self.edgar_session.fetch_page,
        )

        return response

    def get_non_ownership_filings_by_name(
        self,
        company_name: str,
        number_of_filings: int = 100,
        start: int = 0
    ) -> list[dict]:
        """Returns all the non-ownership filings for a given company name.

        ### Parameters
        ----
        company_name : str
            The company nameyou want to query ownership filings for.

        number_of_filings : int (optional, Default=100)
            Specifices the number of filings to return. If you want all filings
            then set to `None`. Be cautious though becuase you may be requesting
            100s of URLs.

        start: int (optional, Default=0)
            If you want to pick up where you left off from a previous parse, then
            set the `start` argument. This will start parsing the companies that come
            after this and up until the `number_of_filings`.

        ### Returns
        ----
        dict :
            A collection of `NonOwnershipFiling` resource objects.

        ### Usage
        ----
            >>> edgar_client = EdgarClient(user_agent="Your Name your-email@example.com")
            >>> ownership_filings_services = edgar_client.ownership_filings()
            >>> ownership_filings_services.get_non_ownership_filings_by_cik(
               company_name='facebook'
            )
        """

        params = {
            'action': 'getcompany',
            'output': 'atom',
            'Count': '100',
            'myowner': 'exclude',
            'company': company_name,
        }

        # Grab the Data.
        response = self.edgar_session.make_request(
            method='get',
            endpoint=self.endpoint,
            params=params,
        )

        # Parse it.
        response = self.edgar_parser.parse_entries(
            response_text=response,
            num_of_items=number_of_filings,
            start=start,
            fetch_page=self.edgar_session.fetch_page,
        )

        return response

    def query_ownership_filings(
        self,
        cik: str = None,
        sic: str = None,
        filing_type: Union[str, Enum] = None,
        company_name: str = None,
        start: int = 0,
        number_of_filings: int = 100,
        after_date: Union[str, datetime, date] = None,
        before_date: Union[str, datetime, date] = None
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
            A collection of `OwnershipFilings` resources.

        ### Usage
        ----
            >>> edgar_client = EdgarClient(user_agent="Your Name your-email@example.com")
            >>> ownership_filings_services = edgar_client.ownership_filings()
            >>> ownership_filings_services.query_ownership_filings(
               cik='1326801',
               after='2019-12-01'
            )
        """

        if isinstance(filing_type, Enum):
            filing_type = filing_type.value

        if before_date:
            before_date = self.edgar_utilities.parse_dates(
                date_or_datetime=before_date
            )

        if after_date:
            after_date = self.edgar_utilities.parse_dates(
                date_or_datetime=after_date
            )

        params = {
            'action': 'getcompany',
            'output': 'atom',
            'Count': '100',
            'myowner': 'only',
            'start': start,
            'CIK': cik or '',
            'SIC': sic or '',
            'type': filing_type or '',
            'company': company_name or '',
            'datea': after_date or '',
            'dateb': before_date or '',
        }

        # Grab the Data.
        response = self.edgar_session.make_request(
            method='get',
            endpoint=self.endpoint,
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

    def query_non_ownership_filings(
        self,
        cik: str = None,
        sic: str = None,
        filing_type: Union[str, Enum] = None,
        company_name: str = None,
        start: int = 0,
        number_of_filings: int = 100,
        after_date: Union[str, datetime, date] = None,
        before_date: Union[str, datetime, date] = None
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
            A collection of `NonOwnershipFilings` resources.

        ### Usage
        ----
            >>> edgar_client = EdgarClient(user_agent="Your Name your-email@example.com")
            >>> ownership_filings_services = edgar_client.ownership_filings()
            >>> ownership_filings_services.query_non_ownership_filings(
               cik='1326801',
               after_date='2019-12-01'
            )
        """

        if isinstance(filing_type, Enum):
            filing_type = filing_type.value

        if before_date:
            before_date = self.edgar_utilities.parse_dates(
                date_or_datetime=before_date
            )

        if after_date:
            after_date = self.edgar_utilities.parse_dates(
                date_or_datetime=after_date
            )

        params = {
            'action': 'getcompany',
            'output': 'atom',
            'Count': '100',
            'myowner': 'exclude',
            'start': start,
            'CIK': cik or '',
            'SIC': sic or '',
            'type': filing_type or '',
            'company': company_name or '',
            'datea': after_date or '',
            'dateb': before_date or '',
        }

        # Grab the Data.
        response = self.edgar_session.make_request(
            method='get',
            endpoint=self.endpoint,
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
