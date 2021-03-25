from typing import Dict
from edgar.session import EdgarSession
from edgar.utilis import EdgarUtilities
from edgar.parser import EdgarParser


class Issuers():

    """
    ## Overview:
    ----
    """

    def __init__(self, session: EdgarSession) -> None:
        """Initializes the `Issuers` object.

        ### Parameters
        ----
        session : `EdgarSession`
            An initialized session of the `EdgarSession`.

        ### Usage
        ----
            >>> edgar_client = EdgarClient()
            >>> issuers_services = edgar_client.issuers()
        """

        # Set the session.
        self.edgar_session: EdgarSession = session
        self.edgar_utilities: EdgarUtilities = EdgarUtilities()
        self.edgar_parser: EdgarParser = EdgarParser()

        # Set the endpoint.
        self.browse_endpoint = '/cgi-bin/own-disp'

        # define the arguments of the request
        self.params = {
            'count': '100',
            'CIK': '',
            'action': 'getissuer',
            'output': 'atom'
        }

    def _reset_params(self) -> None:
        """Resets the params for the next request."""

        # define the arguments of the request
        self.params = {
            'count': '100',
            'CIK': '',
            'action': 'getissuer',
            'output': 'atom'
        }

    def __repr__(self) -> str:
        """String representation of the `EdgarClient.Issuers` object."""

        # define the string representation
        str_representation = '<EdgarClient.Issuers (active=True, connected=True)>'

        return str_representation

    def get_issuers_by_cik(self, cik: str, number_of_issuers: int = 100) -> list:
        """Returns all the issuers for a given CIK number.

        ### Arguments:
        ----
        cik : str
            The CIK you want to query for issuers.

        number_of_issuers : int (optional, Default=100)
            Specifices the number of issuers to return. If you want all issuers
            then set to `None`. Be cautious though becuase you may be requesting
            100s of URLs.

        ### Returns:
        ----
        dict :
            A collection of `Issuers` resources.

        ### Usage:
        ----
            >>> edgar_client = EdgarClient()
            >>> issuers_services = edgar_client.issuers()
            >>> issuers_services.get_issuers_by_cik(                
                cik=''
            )
        """

        self.params['CIK'] = cik

        # Grab the Data.
        response = self.edgar_session.make_request(
            method='get',
            endpoint=self.browse_endpoint,
            params=self.params
        )

        # Parse it.
        response = self.edgar_parser.parse_issuer_table(
            response_text=response,
            num_of_items=number_of_issuers
        )

        self._reset_params()

        return response
