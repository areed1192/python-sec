"""Service for querying SEC EDGAR issuer ownership data."""

from __future__ import annotations

from edgar.session import EdgarSession


class Issuers():

    """
    ## Overview
    ----
    Queries the SEC EDGAR ownership-distribution system to retrieve
    issuer information and transaction reports by CIK number.
    """

    def __init__(self, session: EdgarSession) -> None:
        """Initializes the `Issuers` object.

        ### Parameters
        ----
        session : `EdgarSession`
            An initialized session of the `EdgarSession`.

        ### Usage
        ----
            >>> edgar_client = EdgarClient(user_agent="Your Name your-email@example.com")
            >>> issuers_services = edgar_client.issuers()
        """

        # Set the session.
        self.edgar_session: EdgarSession = session
        self.edgar_utilities = session.edgar_utilities
        self.edgar_parser = session.edgar_parser

        # Set the endpoint.
        self.browse_endpoint = '/cgi-bin/own-disp'

    def __repr__(self) -> str:
        """String representation of the `EdgarClient.Issuers` object."""

        # define the string representation
        str_representation = '<EdgarClient.Issuers (active=True, connected=True)>'

        return str_representation

    def get_issuers_by_cik(self, cik: str) -> list[dict]:
        """Returns all the issuers for a given CIK number.

        ### Parameters
        ----
        cik : str
            The CIK you want to query for issuers.

        number_of_issuers : int (optional, Default=100)
            Specifices the number of issuers to return. If you want all issuers
            then set to `None`. Be cautious though becuase you may be requesting
            100s of URLs.

        ### Returns
        ----
        dict :
            A collection of `Issuers` resources.

        ### Usage
        ----
            >>> edgar_client = EdgarClient(user_agent="Your Name your-email@example.com")
            >>> issuers_services = edgar_client.issuers()
            >>> issuers_services.get_issuers_by_cik(
                cik=''
            )
        """

        params = {
            'action': 'getissuer',
            'output': 'atom',
            'count': '100',
            'CIK': cik,
        }

        # Grab the Data.
        response = self.edgar_session.make_request(
            method='get',
            endpoint=self.browse_endpoint,
            params=params,
        )

        # Parse it.
        response = self.edgar_parser.parse_issuer_table(
            response_text=response,
            fetch_page=self.edgar_session.fetch_page,
        )

        return response
