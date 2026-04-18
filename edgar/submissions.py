"""Service for retrieving SEC EDGAR company submission histories."""

from __future__ import annotations

from edgar.cache import TTL_SUBMISSIONS
from edgar.session import EdgarSession


class Submissions():

    """
    ## Overview
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
            >>> edgar_client = EdgarClient(user_agent="Your Name your-email@example.com")
            >>> submissions_service = edgar_client.submissions()
        """

        # Set the session.
        self.edgar_session: EdgarSession = session
        self.edgar_utilities = session.edgar_utilities

    def __repr__(self) -> str:
        """String representation of the `EdgarClient.Submissions` object."""

        # define the string representation
        str_representation = '<EdgarClient.Submissions(active=True, connected=True)>'

        return str_representation

    def get_submissions(self, cik: str) -> dict | None:
        """Returns all the ownership filings for a given CIK number.

        ### Parameters
        ----
        cik : str
            The CIK number you want to query.

        ### Returns
        ----
        dict :
            A collection of `Submission` resource objects.

        ### Usage
        ----
            >>> edgar_client = EdgarClient(user_agent="Your Name your-email@example.com")
            >>> submissions_service = edgar_client.submissions()
            >>> submissions_service.get_submissions(
                cik='1326801'
            )
        """

        if not cik.isdigit():
            raise ValueError(f"CIK must contain only digits, got: {cik!r}")

        if len(cik) < 10:
            num_of_zeros = 10 - len(cik)
            cik = num_of_zeros*"0" + cik

        # Check TTL cache.
        cache = self.edgar_session.cache
        cache_key = f"submissions:{cik}"
        if cache is not None:
            cached = cache.get(cache_key)
            if cached is not None:
                return cached

        # Grab the Data.
        response = self.edgar_session.make_request(
            method='get',
            endpoint=f'/submissions/CIK{cik}.json',
            use_api=True
        )

        # Store in TTL cache.
        if cache is not None and response is not None:
            cache.set(cache_key, response, TTL_SUBMISSIONS)

        return response
