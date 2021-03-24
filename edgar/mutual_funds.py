
from typing import Dict
from typing import List
from typing import Union
from datetime import datetime

from enum import Enum
from edgar.session import EdgarSession
from edgar.utilis import EdgarUtilities
from edgar.parser import EdgarParser


class MutualFunds():

    """
    ## Overview:
    ----

    """

    def __init__(self, session: EdgarSession) -> None:
        """Initializes the `MutualFunds` object.

        ### Parameters
        ----
        session : `EdgarSession`
            An initialized session of the `EdgarSession`.

        ### Usage
        ----
            >>> edgar_client = EdgarClient()
            >>> mutual_funds_services = edgar_client.mutual_funds()
        """

        # Set the session.
        self.edgar_session: EdgarSession = session
        self.edgar_utilities: EdgarUtilities = EdgarUtilities()
        self.edgar_parser: EdgarParser = EdgarParser()

        # Set the endpoint.
        self.endpoint = '/cgi-bin/browse-edgar'
        self.params = {
            'action': 'getcompany',
            'output': 'atom',
            'Count': '100',
            'myowner': 'include',
            'State': '',
            'Country': '',
            'SIC': '',
            'CIK': '',
            'type': '',
            'company': '',
            'start': '',
            'datea': '',
            'dateb': ''
        }

    def __repr__(self) -> str:
        """String representation of the `EdgarClient.Companies` object."""

        # define the string representation
        str_representation = '<EdgarClient.MutualFunds (active=True, connected=True)>'

        return str_representation

    def get_mutual_fund_filings_by_type(self, cik: str, mutual_fund_type: str, start: int = 0, number_of_filings: int = 100) -> List[dict]:
        """Returns all mutual fund filings matching the specified type for specific CIK.

        ### Parameters
        ----
        cik : str
            Can be either the Series ID or CIK ID that you want to query.

        mutual_fund_type : str
            The type of mutual fund you want to query. Can be one of the
            following: `['mutual-fund', 'mutual-fund-prospectus', 'mutual-fund-proxy-records',
            'mutual-fund-shareholder-reports', 'mutual-fund-summary-prospectus', 
            'mutual-fund-effectiveness-notice']`

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
        List[dict]:
            A collection of `MutualFundDocument` resources.

        ### Usage
        ----
            >>> edgar_client = EdgarClient()
            >>> mutual_funds_services = edgar_client.mutual_funds()
            >>> mutual_funds_services.get_mutual_fund_filings_by_type(
                mutual_fund_type='mutual-fund'
            )
        """

        # The common mutual fund types.
        mutual_funds_type = {
            'mutual-fund': {
                'query_params': {
                    'type': '485',
                    'hidefilings': None
                }
            },
            'mutual-fund-prospectus': {
                'query_params': {
                    'type': '485',
                    'hidefilings': '0'
                }
            },
            'mutual-fund-proxy-records': {
                'query_params': {
                    'type': 'N-PX',
                    'hidefilings': '0'
                }
            },
            'mutual-fund-shareholder-reports': {
                'query_params': {
                    'type': 'N-CSR',
                    'hidefilings': '0'
                }
            },
            'mutual-fund-summary-prospectus': {
                'query_params': {
                    'type': '497K',
                    'hidefilings': '0'
                }
            },
            'mutual-fund-effectiveness-notice': {
                'query_params': {
                    'type': 'EFFECT',
                    'hidefilings': None
                }
            }
        }

        # Grab the one specified.
        query_params = mutual_funds_type[mutual_fund_type]

        # Add the additional arguments.
        self.params.update(query_params['query_params'])
        self.params['start'] = start
        self.params['CIK'] = cik

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

        return entries

    def get_mutual_funds_by_name(self, company_name: str, start: int = 0, number_of_filings: int = 100) -> List[dict]:
        """Returns all mutual fund filings matching a specific name.

        ### Parameters
        ----
        company_name : str
            The company name you want to use as the basis of your search.

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
        List[dict]:
            A collection of `MutualFundDocument` resources.

        ### Usage
        ----
            >>> edgar_client = EdgarClient()
            >>> mutual_funds_services = edgar_client.mutual_funds()
            >>> mutual_funds_services.get_mutual_funds_by_name(
                company_name='ADVANCED SERIES TRUST'
            )
        """

        self.params['company'] = company_name
        self.params['start'] = start

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

        return entries

    def list_series_and_contracts_by_cik(self, cik: str) -> List[dict]:
        """Returns all the Series IDs and Contract IDs that fall under
        a specific Series ID for the specific CIK number.

        ### Parameters
        ----
        cik : str
            The CIK number you want to query Series ID for

        ### Returns:
        ----
        List[dict]:
            A collection of `Series` and `Contract` resources.

        ### Usage
        ----
            >>> edgar_client = EdgarClient()
            >>> mutual_funds_services = edgar_client.mutual_funds()
            >>> mutual_funds_services.list_series_and_contracts_by_cik(cik='814679')
        """

        self.params['CIK'] = cik
        self.params['scd'] = 'series'

        # Grab the Data.
        response = self.edgar_session.make_request(
            method='get',
            endpoint=self.endpoint,
            params=self.params
        )

        # Parse the entries.
        entries = self.edgar_parser.parse_entries(
            response_text=response,
            num_of_items=300,
            start=0,
            path='.atom:entry/atom:content/atom:company-info/atom:sids/atom:sid'
        )


        del self.params['scd']

        return entries


# https: // www.sec.gov/cgi-bin/browse-edgar?action = getcompany & CIK = 0000814679 & scd = series