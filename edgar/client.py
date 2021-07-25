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

    def __init__(self) -> None:
        """Initializes the `EdgarClient`.

        ### Usage
        ----
            >>> edgar_client = EdgarClient()
        """

        self.edgar_session = EdgarSession(client=self)

    def __repr__(self) -> str:
        """String representation of the `EdgarClient` object."""

        # define the string representation
        str_representation = '<EdgarClient (active=True, connected=True)>'

        return str_representation

    def archives(self) -> Archives:
        """Used to access the `Archives` services.

        ### Returns
        ---
        Archives:
            The `Archives` services Object.
        """

        # Grab the `Archives` object.
        object = Archives(session=self.edgar_session)

        return object

    def companies(self) -> Companies:
        """Used to access the `Companies` services.

        ### Returns
        ---
        Companies:
            The `Companies` services Object.
        """

        # Grab the `Archives` object.
        object = Companies(session=self.edgar_session)

        return object

    def series(self) -> Series:
        """Used to access the `Series` services.

        ### Returns
        ---
        Series:
            The `Series` services Object.
        """

        # Grab the `Series` object.
        object = Series(session=self.edgar_session)

        return object

    def mutual_funds(self) -> MutualFunds:
        """Used to access the `MutualFunds` services.

        ### Returns
        ---
        MutualFunds:
            The `MutualFunds` services Object.
        """

        # Grab the `MutualFunds` object.
        object = MutualFunds(session=self.edgar_session)

        return object

    def variable_insurance_products(self) -> VariableInsuranceProducts:
        """Used to access the `VariableInsuranceProducts` services.

        ### Returns
        ---
        VariableInsuranceProducts:
            The `VariableInsuranceProducts` services Object.
        """

        # Grab the `VariableInsuranceProducts` object.
        object = VariableInsuranceProducts(session=self.edgar_session)

        return object

    def datasets(self) -> Datasets:
        """Used to access the `Datasets` services.

        ### Returns
        ---
        Datasets:
            The `Datasets` services Object.
        """

        # Grab the `Datasets` object.
        object = Datasets(session=self.edgar_session)

        return object

    def filings(self) -> Filings:
        """Used to access the `Filings` services.

        ### Returns
        ---
        Filings:
            The `Filings` services Object.
        """

        # Grab the `Filings` object.
        object = Filings(session=self.edgar_session)

        return object

    def current_events(self) -> CurrentEvents:
        """Used to access the `CurrentEvents` services.

        ### Returns
        ---
        CurrentEvents:
            The `CurrentEvents` services Object.
        """

        # Grab the `CurrentEvents` object.
        object = CurrentEvents(session=self.edgar_session)

        return object

    def issuers(self) -> Issuers:
        """Used to access the `Issuers` services.

        ### Returns
        ---
        Issuers:
            The `Issuers` services Object.
        """

        # Grab the `Issuers` object.
        object = Issuers(session=self.edgar_session)

        return object

    def ownership_filings(self) -> OwnershipFilings:
        """Used to access the `OwnershipFilings` services.

        ### Returns
        ---
        OwnershipFilings:
            The `OwnershipFilings` services Object.
        """

        # Grab the `OwnershipFilings` object.
        object = OwnershipFilings(session=self.edgar_session)

        return object

    def submissions(self) -> Submissions:
        """Used to access the `Submissions` services.

        ### Returns
        ---
        Submissions:
            The `Submissions` services Object.
        """

        # Grab the `Submissions` object.
        object = Submissions(session=self.edgar_session)

        return object

    def xbrl(self) -> Xbrl:
        """Used to access the `Xbrl` services.

        ### Returns
        ---
        Xbrl:
            The `Xbrl` services Object.
        """

        # Grab the `Xbrl` object.
        object = Xbrl(session=self.edgar_session)

        return object
