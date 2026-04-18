"""Service for querying SEC EDGAR mutual fund filings."""

from __future__ import annotations

from typing import Union
from datetime import date
from datetime import datetime

from edgar.session import EdgarSession


class MutualFunds():

    """
    ## Overview
    ----
    Used to interact with the `MutualFunds` service.
    """

    def __init__(self, session: EdgarSession) -> None:
        """Initializes the `MutualFunds` object.

        ### Parameters
        ----
        session : `EdgarSession`
            An initialized session of the `EdgarSession`.

        ### Usage
        ----
            >>> edgar_client = EdgarClient(user_agent="Your Name your-email@example.com")
            >>> mutual_funds_services = edgar_client.mutual_funds()
        """

        # Set the session.
        self.edgar_session: EdgarSession = session
        self.edgar_utilities = session.edgar_utilities
        self.edgar_parser = session.edgar_parser

        # Set the endpoint.
        self.endpoint = '/cgi-bin/browse-edgar'

    def __repr__(self) -> str:
        """String representation of the `EdgarClient.Companies` object."""

        # define the string representation
        str_representation = '<EdgarClient.MutualFunds (active=True, connected=True)>'

        return str_representation

    def query(
        self,
        cik: str = None,
        sic: str = None,
        mutual_fund_type: str = None,
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
            Can be either the Series ID or CIK ID that you want to query.

        mutual_fund_type : str (optional, Default=None)
            The type of mutual fund you want to query. The type is
            defined by the Filing code you pass through. For example,
            `N-PX` represents proxy records.

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
            A collection of `MutualFundDocument` resources.

        ### Usage
        ----
            >>> edgar_client = EdgarClient(user_agent="Your Name your-email@example.com")
            >>> mutual_funds_services = edgar_client.mutual_funds()
            >>> mutual_funds_services.query(
                cik='C000005193'
                mutual_fund_type='N-PX'
            )
        """

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
            'myowner': 'include',
            'start': start or '',
            'CIK': cik or '',
            'SIC': sic or '',
            'type': mutual_fund_type or '',
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

    def get_mutual_fund_filings_by_type(
        self,
        cik: str,
        mutual_fund_type: str,
        start: int = 0,
        number_of_filings: int = 100
    ) -> list[dict]:
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

        ### Returns
        ----
        List[dict]:
            A collection of `MutualFundDocument` resources.

        ### Usage
        ----
            >>> edgar_client = EdgarClient(user_agent="Your Name your-email@example.com")
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

        # Build local params.
        params = {
            'action': 'getcompany',
            'output': 'atom',
            'Count': '100',
            'myowner': 'include',
            'start': start,
            'CIK': cik,
        }
        params.update(query_params['query_params'])

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

    def get_mutual_funds_by_name(
        self,
        company_name: str,
        start: int = 0,
        number_of_filings: int = 100
    ) -> list[dict]:
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

        ### Returns
        ----
        List[dict]:
            A collection of `MutualFundDocument` resources.

        ### Usage
        ----
            >>> edgar_client = EdgarClient(user_agent="Your Name your-email@example.com")
            >>> mutual_funds_services = edgar_client.mutual_funds()
            >>> mutual_funds_services.get_mutual_funds_by_name(
                company_name='ADVANCED SERIES TRUST'
            )
        """

        params = {
            'action': 'getcompany',
            'output': 'atom',
            'Count': '100',
            'myowner': 'include',
            'company': company_name,
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

    def list_series_and_contracts_by_cik(self, cik: str) -> list[dict]:
        """Returns all the Series IDs and Contract IDs that fall under
        a specific Series ID for the specific CIK number.

        ### Parameters
        ----
        cik : str
            The CIK number you want to query Series ID for

        ### Returns
        ----
        List[dict]:
            A collection of `Series` and `Contract` resources.

        ### Usage
        ----
            >>> edgar_client = EdgarClient(user_agent="Your Name your-email@example.com")
            >>> mutual_funds_services = edgar_client.mutual_funds()
            >>> mutual_funds_services.list_series_and_contracts_by_cik(cik='814679')
        """

        params = {
            'action': 'getcompany',
            'output': 'atom',
            'Count': '100',
            'myowner': 'include',
            'CIK': cik,
            'scd': 'series',
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
            num_of_items=300,
            start=0,
            path='.atom:entry/atom:content/atom:company-info/atom:sids/atom:sid',
            fetch_page=self.edgar_session.fetch_page,
        )

        return entries
