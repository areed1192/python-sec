"""Service for querying SEC EDGAR variable insurance product filings."""

from __future__ import annotations

from edgar.session import EdgarSession


class VariableInsuranceProducts():

    """
    ## Overview
    ----
    Queries the SEC EDGAR system for variable insurance product
    filings, including series and contract information.
    """

    def __init__(self, session: EdgarSession) -> None:
        """Initializes the `VariableInsuranceProducts` object.

        ### Parameters
        ----
        session : `EdgarSession`
            An initialized session of the `EdgarSession`.

        ### Usage
        ----
            >>> edgar_client = EdgarClient(user_agent="Your Name your-email@example.com")
            >>> insurance_prods_services = edgar_client.variable_insurance_products()
        """

        # Set the session.
        self.edgar_session: EdgarSession = session
        self.edgar_utilities = session.edgar_utilities
        self.edgar_parser = session.edgar_parser

        # Set the endpoint.
        self.endpoint = '/cgi-bin/browse-edgar'

    def __repr__(self) -> str:
        """String representation of the `EdgarClient.VariableInsuranceProducts` object."""

        # define the string representation
        str_representation = '<EdgarClient.VariableInsuranceProducts (active=True, connected=True)>'

        return str_representation

    def get_products_by_name(
        self,
        company_name: str,
        start: int = 0,
        number_of_filings: int = None
    ) -> list[dict]:
        """Returns all the variable insurance products for a specific name.

        ### Parameters
        ----
        company_name : str
            The name of the company you want to query. For example,
            `goldman sachs`.

        ### Returns
        ----
        List[dict]:
            A collection of `InsuranceProduct` resources.

        ### Usage
        ----
            >>> edgar_client = EdgarClient(user_agent="Your Name your-email@example.com")
            >>> insurance_prods_services = edgar_client.variable_insurance_products()
            >>> insurance_prods_services.get_products_by_name(
                company_name='goldman sachs'
            )
        """

        params = {
            'sc': 'companyseries',
            'company': company_name,
            'count': '500',
            'start': start,
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
