from edgar.session import EdgarSession
from edgar.parser import EdgarParser


class Datasets():

    """
    ## Overview:
    ----
    The SEC offers free datasets for individuals and companies to use
    in their own research. The `Datasets` client helps users query these
    datasets.
    """

    def __init__(self, session: EdgarSession) -> None:
        """Initializes the `Datasets` object.

        ### Parameters
        ----
        session : `EdgarSession`
            An initialized session of the `EdgarSession`.

        ### Usage
        ----
            >>> edgar_client = EdgarClient()
            >>> datasets_services = edgar_client.Datasets()
        """

        # Set the session.
        self.edgar_session: EdgarSession = session
        self.edgar_parser: EdgarParser = EdgarParser()

    def __repr__(self) -> str:
        """String representation of the `EdgarClient.Datasets` object."""

        # define the string representation
        str_representation = '<EdgarClient.Datasets (active=True, connected=True)>'

        return str_representation

    def get_sec_datasets(self) -> dict:
        """Grabs all the Public datasets provided by the SEC.

        ### Returns:
        ----
        dict: 
            A collection of `Dataset` resources.

        ### Usage:
        ----
            >>> edgar_client = EdgarClient()
            >>> datasets_services = edgar_client.Datasets()
            >>> datasets_services.get_sec_datasets()
        """

        # Make the request.
        response = self.edgar_session.make_request(
            method='get',
            endpoint='/data.json'
        )

        return response

    def get_edgar_taxonomies(self) -> dict:
        """Grabs all the Public taxonomies datasets provided by the SEC.

        ### Returns:
        ----
        dict: 
            A collection of `Dataset` taxonomy resources.

        ### Usage:
        ----
            >>> edgar_client = EdgarClient()
            >>> datasets_services = edgar_client.Datasets()
            >>> datasets_services.get_sec_datasets()
        """

        # Make the request.
        response = self.edgar_session.make_request(
            method='get',
            endpoint='/info/edgar/edgartaxonomies.xml'
        )

        response = self.edgar_parser.parse_loc_elements(
            response_text=response
        )

        return response
