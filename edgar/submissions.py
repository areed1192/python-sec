from edgar.session import EdgarSession
from edgar.utilis import EdgarUtilities


class Submissions():

    """
    ## Overview:
    ----
    Allows a user to query each entity’s current filing
    history using the SEC Restful API.
    """

    def __init__(self, session: EdgarSession) -> None:
        """Initializes the `Submissions` object.

        ### Parameters
        ----
        session : `EdgarSession`
            An initialized session of the `EdgarSession`.

        ### Usage
        ----
            >>> edgar_client = EdgarClient()
            >>> submissions_service = edgar_client.submissions()
        """

        # Set the session.
        self.edgar_session: EdgarSession = session
        self.edgar_utilities: EdgarUtilities = EdgarUtilities()

    def __repr__(self) -> str:
        """String representation of the `EdgarClient.Submissions` object."""

        # define the string representation
        str_representation = '<EdgarClient.Submissions(active=True, connected=True)>'

        return str_representation

    def get_submissions(self, cik: str) -> dict:
        """Returns all the ownership filings for a given CIK number.

        ### Arguments:
        ----
        cik : str
            The CIK number you want to query.

        ### Returns:
        ----
        dict :
            A collection of `Submission` resource objects.

        ### Usage:
        ----
            >>> edgar_client = EdgarClient()
            >>> submissions_service = edgar_client.submissions()
            >>> submissions_service.get_submissions(
                cik='1326801'
            )
        """

        if len(cik) < 10:
            num_of_zeros = 10 - len(cik)
            cik = num_of_zeros*"0" + cik

        # Grab the Data.
        response = self.edgar_session.make_request(
            method='get',
            endpoint=f'/submissions/CIK{cik}.json',
            use_api=True
        )

        return response
