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
        Users:
            The `Archives` services Object.
        """

        # Grab the `Archives` object.
        object = Archives(session=self.edgar_session)

        return object

    def companies(self) -> Companies:
        """Used to access the `Companies` services.

        ### Returns
        ---
        Users:
            The `Companies` services Object.
        """

        # Grab the `Archives` object.
        object = Companies(session=self.edgar_session)

        return object

    def series(self) -> Series:
        """Used to access the `Series` services.

        ### Returns
        ---
        Users:
            The `Series` services Object.
        """

        # Grab the `Series` object.
        object = Series(session=self.edgar_session)

        return object

    def mutual_funds(self) -> MutualFunds:
        """Used to access the `MutualFunds` services.

        ### Returns
        ---
        Users:
            The `MutualFunds` services Object.
        """

        # Grab the `MutualFunds` object.
        object = MutualFunds(session=self.edgar_session)

        return object

    def variable_insurance_products(self) -> VariableInsuranceProducts:
        """Used to access the `VariableInsuranceProducts` services.

        ### Returns
        ---
        Users:
            The `VariableInsuranceProducts` services Object.
        """

        # Grab the `VariableInsuranceProducts` object.
        object = VariableInsuranceProducts(session=self.edgar_session)

        return object

    def datasets(self) -> Datasets:
        """Used to access the `Datasets` services.

        ### Returns
        ---
        Users:
            The `Datasets` services Object.
        """

        # Grab the `Datasets` object.
        object = Datasets(session=self.edgar_session)

        return object

    def filings(self) -> Filings:
        """Used to access the `Filings` services.

        ### Returns
        ---
        Users:
            The `Filings` services Object.
        """

        # Grab the `Filings` object.
        object = Filings(session=self.edgar_session)

        return object

    def current_events(self) -> CurrentEvents:
        """Used to access the `CurrentEvents` services.

        ### Returns
        ---
        Users:
            The `CurrentEvents` services Object.
        """

        # Grab the `CurrentEvents` object.
        object = CurrentEvents(session=self.edgar_session)

        return object

    def issuers(self) -> Issuers:
        """Used to access the `Issuers` services.

        ### Returns
        ---
        Users:
            The `Issuers` services Object.
        """

        # Grab the `Issuers` object.
        object = Issuers(session=self.edgar_session)

        return object

    def ownership_filings(self) -> OwnershipFilings:
        """Used to access the `OwnershipFilings` services.

        ### Returns
        ---
        Users:
            The `OwnershipFilings` services Object.
        """

        # Grab the `OwnershipFilings` object.
        object = OwnershipFilings(session=self.edgar_session)

        return object
