"""This module provides access to the different endpoint services of Edgar."""

from edgar.session import EdgarSession
from edgar.archives import Archives
from edgar.companies import Companies
from edgar.series import Series
from edgar.mutual_funds import MutualFunds
from edgar.variable_insurance_products import VariableInsuranceProducts
from edgar.datasets import Datasets
from edgar.filings import Filings
from edgar.current_events import CurrentEvents
from edgar.issuers import Issuers
from edgar.ownership_filings import OwnershipFilings
from edgar.submissions import Submissions
from edgar.xbrl import Xbrl


class EdgarClient():

    """
    ## Overview:
    ----
    Represents the main Edgar client which is used to
    instantiate the different endpoints.
    """

    def __init__(self) -> None:
        """Initializes the `EdgarClient`.

        ### Usage
        ----
            >>> edgar_client = EdgarClient()
        """

        self.edgar_session = EdgarSession(client=self)

    def __repr__(self) -> str:
        """String representation of the `EdgarClient` object."""

        return '<EdgarClient (active=True, connected=True)>'

    def archives(self) -> Archives:
        """Used to access the `Archives` services.

        ### Returns
        ---
        Archives:
            The `Archives` services Object.
        """

        return Archives(session=self.edgar_session)

    def companies(self) -> Companies:
        """Used to access the `Companies` services.

        ### Returns
        ---
        Companies:
            The `Companies` services Object.
        """

        return Companies(session=self.edgar_session)

    def series(self) -> Series:
        """Used to access the `Series` services.

        ### Returns
        ---
        Series:
            The `Series` services Object.
        """

        return Series(session=self.edgar_session)

    def mutual_funds(self) -> MutualFunds:
        """Used to access the `MutualFunds` services.

        ### Returns
        ---
        MutualFunds:
            The `MutualFunds` services Object.
        """

        return MutualFunds(session=self.edgar_session)

    def variable_insurance_products(self) -> VariableInsuranceProducts:
        """Used to access the `VariableInsuranceProducts` services.

        ### Returns
        ---
        VariableInsuranceProducts:
            The `VariableInsuranceProducts` services Object.
        """

        return VariableInsuranceProducts(session=self.edgar_session)

    def datasets(self) -> Datasets:
        """Used to access the `Datasets` services.

        ### Returns
        ---
        Datasets:
            The `Datasets` services Object.
        """

        return Datasets(session=self.edgar_session)

    def filings(self) -> Filings:
        """Used to access the `Filings` services.

        ### Returns
        ---
        Filings:
            The `Filings` services Object.
        """

        return Filings(session=self.edgar_session)

    def current_events(self) -> CurrentEvents:
        """Used to access the `CurrentEvents` services.

        ### Returns
        ---
        CurrentEvents:
            The `CurrentEvents` services Object.
        """

        return CurrentEvents(session=self.edgar_session)

    def issuers(self) -> Issuers:
        """Used to access the `Issuers` services.

        ### Returns
        ---
        Issuers:
            The `Issuers` services Object.
        """

        return Issuers(session=self.edgar_session)

    def ownership_filings(self) -> OwnershipFilings:
        """Used to access the `OwnershipFilings` services.

        ### Returns
        ---
        OwnershipFilings:
            The `OwnershipFilings` services Object.
        """

        return OwnershipFilings(session=self.edgar_session)

    def submissions(self) -> Submissions:
        """Used to access the `Submissions` services.

        ### Returns
        ---
        Submissions:
            The `Submissions` services Object.
        """

        return Submissions(session=self.edgar_session)

    def xbrl(self) -> Xbrl:
        """Used to access the `Xbrl` services.

        ### Returns
        ---
        Xbrl:
            The `Xbrl` services Object.
        """

        return Xbrl(session=self.edgar_session)
