from typing import Dict
from typing import List
from typing import Union
from datetime import date
from datetime import datetime

from enum import Enum
from edgar.session import EdgarSession
from edgar.utilis import EdgarUtilities
from edgar.parser import EdgarParser


class OwnershipFilings():

    """
    ## Overview:
    ----

    """

    def __init__(self, session: EdgarSession) -> None:
        """Initializes the `OwnershipFilings` object.

        ### Parameters
        ----
        session : `EdgarSession`
            An initialized session of the `EdgarSession`.

        ### Usage
        ----
            >>> edgar_client = EdgarClient()
            >>> ownership_filings_services = edgar_client.ownership_filings()
        """

        # Set the session.
        self.edgar_session: EdgarSession = session
        self.edgar_utilities: EdgarUtilities = EdgarUtilities()
        self.edgar_parser: EdgarParser = EdgarParser()

        # Set the endpoint.
        self.endpoint = '/cgi-bin/browse-edgar'
        self.params = {
            'CIK': '',
            'company': '',
            'Count': '100',
            'myowner': 'only',
            'action': 'getcompany',
            'output': 'atom',
            'start': '',
            'datea': '',
            'dateb': ''
        }

    def _reset_params(self) -> None:
        """Resets the params for the next request."""

        self.params = {
            'CIK': '',
            'company': '',
            'Count': '100',
            'myowner': 'only',
            'action': 'getcompany',
            'output': 'atom',
            'start': '',
            'datea': '',
            'dateb': ''
        }

    def __repr__(self) -> str:
        """String representation of the `EdgarClient.OwnershipFilings` object."""

        # define the string representation
        str_representation = '<EdgarClient.OwnershipFilings (active=True, connected=True)>'

        return str_representation

    def get_ownership_filings_by_cik(self, cik: str, number_of_filings: int = 100, start: int = 0) -> dict:
        """Returns all the ownership filings for a given CIK number.

        ### Arguments:
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

        ### Returns:
        ----
        dict :
            A collection of `OwnershipFiling` resource objects.

        ### Usage:
        ----
            >>> edgar_client = EdgarClient()
            >>> ownership_filings_services = edgar_client.ownership_filings()
            >>> ownership_filings_services.get_ownership_filings_by_cik(
               cik='1326801'
            )
        """

        self.params['CIK'] = cik

        # Grab the Data.
        response = self.edgar_session.make_request(
            method='get',
            endpoint=self.endpoint,
            params=self.params
        )

        # Parse it.
        response = self.edgar_parser.parse_entries(
            response_text=response,
            num_of_items=number_of_filings,
            start=start
        )

        self._reset_params()

        return response

    def get_ownership_filings_by_name(self, company_name: str, number_of_filings: int = 100, start: int = 0) -> dict:
        """Returns all the ownership filings for a given company name.

        ### Arguments:
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

        ### Returns:
        ----
        dict :
            A collection of `OwnershipFiling` resource objects.

        ### Usage:
        ----
            >>> edgar_client = EdgarClient()
            >>> ownership_filings_services = edgar_client.ownership_filings()
            >>> ownership_filings_services.get_ownership_filings_by_cik(
               company_name='facebook'
            )
        """

        self.params['company'] = company_name

        # Grab the Data.
        response = self.edgar_session.make_request(
            method='get',
            endpoint=self.endpoint,
            params=self.params
        )

        # Parse it.
        response = self.edgar_parser.parse_entries(
            response_text=response,
            num_of_items=number_of_filings,
            start=start
        )

        self._reset_params()

        return response

    def get_non_ownership_filings_by_cik(self, cik: str, number_of_filings: int = 100, start: int = 0) -> dict:
        """Returns all the non-ownership filings for a given CIK number.

        ### Arguments:
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

        ### Returns:
        ----
        dict :
            A collection of `NonOwnershipFiling` resource objects.

        ### Usage:
        ----
            >>> edgar_client = EdgarClient()
            >>> ownership_filings_services = edgar_client.ownership_filings()
            >>> ownership_filings_services.get_non_ownership_filings_by_cik(
               cik='1326801'
            )
        """

        self.params['CIK'] = cik
        self.params['myowner'] = 'exclude'

        # Grab the Data.
        response = self.edgar_session.make_request(
            method='get',
            endpoint=self.endpoint,
            params=self.params
        )

        # Parse it.
        response = self.edgar_parser.parse_entries(
            response_text=response,
            num_of_items=number_of_filings,
            start=start
        )

        self._reset_params()

        return response

    def get_non_ownership_filings_by_name(self, company_name: str, number_of_filings: int = 100, start: int = 0) -> dict:
        """Returns all the non-ownership filings for a given company name.

        ### Arguments:
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

        ### Returns:
        ----
        dict :
            A collection of `NonOwnershipFiling` resource objects.

        ### Usage:
        ----
            >>> edgar_client = EdgarClient()
            >>> ownership_filings_services = edgar_client.ownership_filings()
            >>> ownership_filings_services.get_non_ownership_filings_by_cik(
               company_name='facebook'
            )
        """

        self.params['company'] = company_name
        self.params['myowner'] = 'exclude'

        # Grab the Data.
        response = self.edgar_session.make_request(
            method='get',
            endpoint=self.endpoint,
            params=self.params
        )

        # Parse it.
        response = self.edgar_parser.parse_entries(
            response_text=response,
            num_of_items=number_of_filings,
            start=start
        )

        self._reset_params()

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
    ) -> List[dict]:
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

        ### Returns:
        ----
        List[dict]:
            A collection of `OwnershipFilings` resources.

        ### Usage
        ----
            >>> edgar_client = EdgarClient()
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

        self.params['start'] = start
        self.params['CIK'] = cik
        self.params['SIC'] = sic
        self.params['type'] = filing_type
        self.params['company'] = company_name
        self.params['datea'] = after_date
        self.params['dateb'] = before_date

        # Grab the Data.
        response = self.edgar_session.make_request(
            method='get',
            endpoint=self.endpoint,
            params=self.params
        )

        # Parse the entries.
        entries = self.edgar_parser.parse_entries(
            response_text=response,
            num_of_items=number_of_filings,
            start=start
        )

        self._reset_params()

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
    ) -> List[dict]:
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

        ### Returns:
        ----
        List[dict]:
            A collection of `NonOwnershipFilings` resources.

        ### Usage
        ----
            >>> edgar_client = EdgarClient()
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

        self.params['start'] = start
        self.params['CIK'] = cik
        self.params['SIC'] = sic
        self.params['type'] = filing_type
        self.params['company'] = company_name
        self.params['datea'] = after_date
        self.params['dateb'] = before_date

        # Grab the Data.
        response = self.edgar_session.make_request(
            method='get',
            endpoint=self.endpoint,
            params=self.params
        )

        # Parse the entries.
        entries = self.edgar_parser.parse_entries(
            response_text=response,
            num_of_items=number_of_filings,
            start=start
        )

        self._reset_params()

        return entries
