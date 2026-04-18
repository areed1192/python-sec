"""Service for querying SEC EDGAR mutual fund series and contracts."""

from __future__ import annotations

from edgar.session import EdgarSession


class Series():

    """
    ## Overview
    ----
    Queries the SEC EDGAR series and contracts system to retrieve
    investment-company series data by CIK or series identifier.
    """

    def __init__(self, session: EdgarSession) -> None:
        """Initializes the `Series` object.

        ### Parameters
        ----
        session : `EdgarSession`
            An initialized session of the `EdgarSession`.

        ### Usage
        ----
            >>> edgar_client = EdgarClient(user_agent="Your Name your-email@example.com")
            >>> series_services = edgar_client.series()
        """

        # Set the session.
        self.edgar_session: EdgarSession = session
        self.edgar_utilities = session.edgar_utilities
        self.edgar_parser = session.edgar_parser

        # Set the endpoint.
        self.series_endpoint = '/cgi-bin/series'
        self.browse_endpoint = '/cgi-bin/browse-edgar'

    def __repr__(self) -> str:
        """String representation of the `EdgarClient.Series` object."""

        # define the string representation
        str_representation = '<EdgarClient.Series (active=True, connected=True)>'

        return str_representation

    def get_series_by_cik(self, cik: str) -> list[dict]:
        """Returns a list of series that fall under a specific CIK number.

        ### Parameters
        ----
        cik : str
            The company CIK number, defined by the SEC.

        ### Returns
        ----
        dict :
            A collection of `Series` resources.

        ### Usage
        ----
            >>> edgar_client = EdgarClient(user_agent="Your Name your-email@example.com")
            >>> series_services = edgar_client.series(
            >>> series_services.get_series_by_cik(cik='814679')
        """

        params = {
            'action': 'getcompany',
            'scd': 'series',
            'output': 'atom',
            'CIK': cik,
            'count': '100',
        }

        # Grab the Data.
        response = self.edgar_session.make_request(
            method='get',
            endpoint=self.browse_endpoint,
            params=params,
        )

        # Parse it.
        response = self.edgar_parser.parse_entries(
            response_text=response,
            fetch_page=self.edgar_session.fetch_page,
        )

        return response

    def get_series_by_series_id(self, series_id: str) -> list[dict]:
        """Returns a list of series that fall under a specific CIK number.

        ### Parameters
        ----
        series_id : str
            The Series ID you want to query, defined by the SEC.

        ### Returns
        ----
        dict :
            A collection of `Series` resources.

        ### Usage
        ----
            >>> edgar_client = EdgarClient(user_agent="Your Name your-email@example.com")
            >>> series_services = edgar_client.series(
            >>> series_services.get_series_by_series_id(series_id='S000001976')
        """

        params = {
            'action': 'getcompany',
            'scd': 'series',
            'output': 'atom',
            'CIK': series_id,
            'count': '100',
        }

        # Grab the Data.
        response = self.edgar_session.make_request(
            method='get',
            endpoint=self.browse_endpoint,
            params=params,
        )

        # Parse it.
        response = self.edgar_parser.parse_entries(
            response_text=response,
            fetch_page=self.edgar_session.fetch_page,
        )

        return response


    def get_series_filings_by_series_id(
        self,
        series_id: str,
        start: int = None
    ) -> list[dict]:
        """Returns a list of series that fall under a specific CIK number.

        ### Parameters
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

        ### Returns
        ----
        dict :
            A collection of `Series` resources.

        ### Usage
        ----
            >>> edgar_client = EdgarClient(user_agent="Your Name your-email@example.com")
            >>> series_services = edgar_client.series(
            >>> series_services.get_series_by_series_id(series_id='S000001976')
        """

        params = {
            'action': 'getcompany',
            'scd': 'filings',
            'output': 'atom',
            'CIK': series_id,
            'start': start or '',
            'count': '100',
        }

        # Grab the Data.
        response = self.edgar_session.make_request(
            method='get',
            endpoint=self.series_endpoint,
            params=params,
        )

        # Parse it.
        response = self.edgar_parser.parse_series_table(
            response_text=response,
        )

        return response
