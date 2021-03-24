from typing import Dict
from edgar.session import EdgarSession
from edgar.utilis import EdgarUtilities
from edgar.parser import EdgarParser


class CurrentEvents():

    """
    ## Overview:
    ----
    """

    def __init__(self, session: EdgarSession) -> None:
        """Initializes the `CurrentEvents` object.

        ### Parameters
        ----
        session : `EdgarSession`
            An initialized session of the `EdgarSession`.

        ### Usage
        ----
            >>> edgar_client = EdgarClient()
            >>> current_events_services = edgar_client.CurrentEvents()
        """

        # Set the session.
        self.edgar_session: EdgarSession = session
        self.edgar_utilities: EdgarUtilities = EdgarUtilities()
        self.edgar_parser: EdgarParser = EdgarParser()

        # Set the endpoint.
        self.browse_endpoint = '/cgi-bin/current'

    def __repr__(self) -> str:
        """String representation of the `EdgarClient.CurrentEvents` object."""

        # define the string representation
        str_representation = '<EdgarClient.CurrentEvents (active=True, connected=True)>'

        return str_representation

    def get_current_event_filings(self, days_prior: int, form: str, form_id: str = '') -> Dict:
        """Query current filigns by type.

        ### Arguments:
        ----
        day : int
            The number of days prior you would like to analyze. Can be one
            of the following: [0, 1, 2, 3, 4, 5]

        form : str
            The form you would like to analyze. Can be one of the following: 
            ['10-k-annual', '10-k-quarterly', '14-proxies', '485-fund-prosp.',
             '8-k', 's-8', 'all']

        form_id : str (optional, Default=None)
            Represents the Form-ID and can be used to override the `form` 
            argument.

        ### Returns:
        ----
        dict :
            A collection of `CurrentEvents` resources.

        ### Usage:
        ----
            >>> edgar_client = EdgarClient()
            >>> current_events_services = edgar_client.CurrentEvents()
            >>> current_events_services.get_current_event_filings(
                days_prior=0,
                form='10-k-annual'
            )
        """

        form_dict = {
            '10-k-annual': 0,
            '10-k-quarterly': 1,
            '14-proxies': 2,
            '485-fund-prosp.': 3,
            '8-k': 4,
            's-8': 5,
            'all': 6
        }

        if form in form_dict:
            form_id_arg = form_dict[form]
        else:
            raise ValueError(
                "The argument you've provided for form is incorrect."
            )

        # define the arguments of the request
        search_params = {
            'q1': days_prior,
            'q2': form_id_arg,
            'q3': form_id
        }

        # Grab the Data.
        response = self.edgar_session.make_request(
            method='get',
            endpoint=self.browse_endpoint,
            params=search_params
        )

        # Parse it.
        response = self.edgar_parser.parse_current_event_table(
            response_text=response
        )

        return response
