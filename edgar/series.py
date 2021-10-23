from typing import Dict
from edgar.session import EdgarSession
from edgar.utilis import EdgarUtilities
from edgar.parser import EdgarParser


class Series():

    """
    ## Overview:
    ----

    """

    def __init__(self, session: EdgarSession) -> None:
        """Initializes the `Series` object.

        ### Parameters
        ----
        session : `EdgarSession`
            An initialized session of the `EdgarSession`.

        ### Usage
        ----
            >>> edgar_client = EdgarClient()
            >>> series_services = edgar_client.series()
        """

        # Set the session.
        self.edgar_session: EdgarSession = session
        self.edgar_utilities: EdgarUtilities = EdgarUtilities()
        self.edgar_parser: EdgarParser = EdgarParser()

        # Set the endpoint.
        self.series_endpoint = '/cgi-bin/series'
        self.browse_endpoint = '/cgi-bin/browse-edgar'

        self.series_params = {
            'company': ''
        }

        self.browse_params = {
            'action': 'getcompany',
            'scd': 'series',
            'output': 'atom',
            'CIK': '',
            'start': '',
            'count': '100'
        }

        self.browse_params_filings = {
            'action': 'getcompany',
            'scd': 'filings',
            'output': 'atom',
            'CIK': '',
            'start': '',
            'count': '100'
        }


    def _reset_params(self) -> None:
        """Resets the params for the next request."""

        self.series_params = {
            'company': ''
        }

        self.browse_params = {
            'action': 'getcompany',
            'scd': 'series',
            'output': 'atom',
            'CIK': '',
            'start': '',
            'count': '100'
        }

        self.browse_params_filings = {
            'action': 'getcompany',
            'scd': 'filings',
            'output': 'atom',
            'CIK': '',
            'start': '',
            'count': '100'
        }

    def __repr__(self) -> str:
        """String representation of the `EdgarClient.Series` object."""

        # define the string representation
        str_representation = '<EdgarClient.Series (active=True, connected=True)>'

        return str_representation

    def get_series_by_cik(self, cik: str) -> Dict:
        """Returns a list of series that fall under a specific CIK number.

        ### Arguments:
        ----
        cik : str
            The company CIK number, defined by the SEC.

        ### Returns:
        ----
        dict :
            A collection of `Series` resources.

        ### Usage:
        ----
            >>> edgar_client = EdgarClient()
            >>> series_services = edgar_client.series(
            >>> series_services.get_series_by_cik(cik='814679')
        """

        self.browse_params['CIK'] = cik

        # Grab the Data.
        response = self.edgar_session.make_request(
            method='get',
            endpoint=self.browse_endpoint,
            params=self.browse_params
        )

        # Parse it.
        response = self.edgar_parser.parse_entries(
            response_text=response
        )

        self._reset_params()

        return response

    def get_series_by_series_id(self, series_id: str) -> Dict:
        """Returns a list of series that fall under a specific CIK number.

        ### Arguments:
        ----
        series_id : str
            The Series ID you want to query, defined by the SEC.

        ### Returns:
        ----
        dict :
            A collection of `Series` resources.

        ### Usage:
        ----
            >>> edgar_client = EdgarClient()
            >>> series_services = edgar_client.series(
            >>> series_services.get_series_by_series_id(series_id='S000001976')
        """

        self.browse_params['CIK'] = series_id

        # Grab the Data.
        response = self.edgar_session.make_request(
            method='get',
            endpoint=self.browse_endpoint,
            params=self.browse_params
        )
        print(response)

        # Parse it.
        response = self.edgar_parser.parse_entries(
            response_text=response
        )

        self._reset_params()

        return response


    def get_series_filings_by_series_id(
        self,
        series_id: str,
        start: int = None
    ) -> Dict:
        """Returns a list of series that fall under a specific CIK number.

        ### Arguments:
        ----
        series_id : str
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
            A collection of `Series` resources.

        ### Usage:
        ----
            >>> edgar_client = EdgarClient()
            >>> series_services = edgar_client.series(
            >>> series_services.get_series_by_series_id(series_id='S000001976')
        """

        self.browse_params_filings['CIK'] = series_id
        self.browse_params_filings['start'] = start

        # Grab the Data.
        response = self.edgar_session.make_request(
            method='get',
            endpoint=self.series_endpoint,
            params=self.browse_params_filings
        )

        # Parse it.
        response = self.edgar_parser.parse_series_table(
            response_text=response,
        )

        self._reset_params()

        return response
