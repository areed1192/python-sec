
from typing import Dict
from typing import List
from typing import Union
from datetime import date
from datetime import datetime

from enum import Enum
from edgar.session import EdgarSession
from edgar.utilis import EdgarUtilities
from edgar.parser import EdgarParser


class VariableInsuranceProducts():

    """
    ## Overview:
    ----

    """

    def __init__(self, session: EdgarSession) -> None:
        """Initializes the `VariableInsuranceProducts` object.

        ### Parameters
        ----
        session : `EdgarSession`
            An initialized session of the `EdgarSession`.

        ### Usage
        ----
            >>> edgar_client = EdgarClient()
            >>> insurance_prods_services = edgar_client.variable_insurance_products()
        """

        # Set the session.
        self.edgar_session: EdgarSession = session
        self.edgar_utilities: EdgarUtilities = EdgarUtilities()
        self.edgar_parser: EdgarParser = EdgarParser()

        # Set the endpoint.
        self.endpoint = '/cgi-bin/browse-edgar'
        self.params = {
            'sc': 'companyseries',
            'company': '',
            'count': '500',
            'start': ''
        }

    def _reset_params(self) -> None:
        """Resets the params for the next request.""" 

        self.params = {
            'sc': 'companyseries',
            'company': '',
            'count': '500',
            'start': ''
        }

    def __repr__(self) -> str:
        """String representation of the `EdgarClient.VariableInsuranceProducts` object."""

        # define the string representation
        str_representation = '<EdgarClient.VariableInsuranceProducts (active=True, connected=True)>'

        return str_representation

    def get_products_by_name(self, company_name: str, start: int = 0, number_of_filings: int = None) -> List[Dict]:
        """Returns all the variable insurance products for a specific name.

        ### Parameters
        ----
        company_name : str
            The name of the company you want to query. For example,
            `goldman sachs`.

        ### Returns:
        ----
        List[dict]:
            A collection of `InsuranceProduct` resources.

        ### Usage
        ----
            >>> edgar_client = EdgarClient()
            >>> insurance_prods_services = edgar_client.variable_insurance_products()
            >>> insurance_prods_services.get_products_by_name(
                company_name='goldman sachs'
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

        self._reset_params()

        return entries


    # def get_variable_insurance_products_by_cik(self, cik: str, before: str = None, after: str = None) -> List[dict]:
    #     """Returns all the filings (ownership and non-ownership) for a given company in a given date range.

    #     Arguments:
    #     ----
    #     cik {str} -- The CIK number of the company to be queried.

    #     Keyword Arguments:
    #     ----
    #     before {Union[str, date]} -- Represents filings that you want before a certain
    #         date. For example, "2019-12-01" means return all the filings BEFORE
    #         Decemeber 1, 2019. (default: {None})

    #     after {Union[str, date]} -- Represents filings that you want after a certain
    #         date. For example, "2019-12-01" means return all the filings AFTER
    #         Decemeber 1, 2019. (default: {None})

    #     Returns:
    #     ----
    #     List[dict] -- A list of mutual fund prospectus.
    #     """

    #     # define the arguments of the request
    #     search_params = {
    #         'CIK': cik,
    #         'Count': '100',
    #         'myowner': 'include',
    #         'action': 'getcompany',
    #         'type': '485',
    #         'hidefilings': '0',
    #         'output': 'atom',
    #         'datea': after,
    #         'dateb': before
    #     }

    #     # Make the response.
    #     response = requests.get(
    #         url=self.series_service,
    #         params=search_params
    #     )

    #     # Parse the entries.
    #     entries = self.parser_client.parse_entries(entries_text=response.text)

    #     return entries