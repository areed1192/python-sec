from typing import Dict
from typing import List
from typing import Union
from enum import Enum
from datetime import datetime
from datetime import date
from edgar.session import EdgarSession
from edgar.utilis import EdgarUtilities
from edgar.parser import EdgarParser


class Filings():

    """
    ## Overview:
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
            >>> edgar_client = EdgarClient()
            >>> filings_services = edgar_client.Filings()
        """

        # Set the session.
        self.edgar_session: EdgarSession = session
        self.edgar_utilities: EdgarUtilities = EdgarUtilities()
        self.edgar_parser: EdgarParser = EdgarParser()

        # Set the endpoint.
        self.filings_endpoint = '/cgi-bin/filings'
        self.browse_endpoint = '/cgi-bin/browse-edgar'

        self.params = {
            'action': 'getcompany',
            'output': 'atom',
            'company': '',
            'CIK': '',
            'start': '0',
            'Count': '100',
            'datea': '',
            'dateb': ''
        }

    def _reset_params(self) -> None:
        """Resets the params for the next request."""

        self.params = {
            'CIK': '',
            'company': '',
            'Count': '100',
            'action': 'getcompany',
            'output': 'atom',
            'start': '',
            'datea': '',
            'dateb': ''
        }

    def __repr__(self) -> str:
        """String representation of the `EdgarClient.Filings` object."""

        # define the string representation
        str_representation = '<EdgarClient.Filings (active=True, connected=True)>'

        return str_representation

    def get_filings_by_cik(self, cik: str, start: int = 0, number_of_filings: int = 100) -> Dict:
        """Returns a list of filings that fall under a specific CIK number.

        ### Arguments:
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

        ### Returns:
        ----
        dict :
            A collection of `Filings` resources.

        ### Usage:
        ----
            >>> edgar_client = EdgarClient()
            >>> filings_services = edgar_client.filings()
            >>> filings_services.get_filings_by_cik(cik='814679')
        """

        self.params['CIK'] = cik
        self.params['start'] = start

        # Grab the Data.
        response = self.edgar_session.make_request(
            method='get',
            endpoint=self.browse_endpoint,
            params=self.params
        )

        # Parse it.
        response = self.edgar_parser.parse_entries(
            response_text=response,
            start=start,
            num_of_items=number_of_filings
        )

        self._reset_params()

        return response

    def get_filings_by_type(self, cik: str, filing_type: Union[str, Enum], start: int = 0, number_of_filings: int = 100) -> Dict:
        """Returns a list of filings that fall under a specific CIK number.

        ### Arguments:
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

        ### Returns:
        ----
        dict :
            A collection of `Filings` resources.

        ### Usage:
        ----
            >>> edgar_client = EdgarClient()
            >>> filings_services = edgar_client.filings()
            >>> filings_services.get_filings_by_type(
                cik='814679',
                filing_type='10-k'
            )
        """

        if isinstance(filing_type, Enum):
            filing_type = filing_type.value

        self.params['CIK'] = cik
        self.params['type'] = filing_type
        self.params['start'] = start

        # Grab the Data.
        response = self.edgar_session.make_request(
            method='get',
            endpoint=self.browse_endpoint,
            params=self.params
        )

        # Parse it.
        response = self.edgar_parser.parse_entries(
            response_text=response,
            start=start,
            num_of_items=number_of_filings
        )

        self._reset_params()

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
            A collection of `Filing` resources.

        ### Usage
        ----
            >>> edgar_client = EdgarClient()
            >>> filings_services = edgar_client.filings()
            >>> filings_services.query(
                cik='C000005193'
                filing_type='10-k'
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
            endpoint=self.browse_endpoint,
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

    def get_filings_by_company_name(
        self,
        company_name: str,
        number_of_filings: int = 100,
        start: int = 0
    ) -> List[dict]:
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

        self.params['company'] = company_name

        # Grab the Data.
        response = self.edgar_session.make_request(
            method='get',
            endpoint=self.browse_endpoint,
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
