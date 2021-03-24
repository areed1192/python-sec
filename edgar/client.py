from edgar.session import EdgarSession
from edgar.archives import Archives
from edgar.companies import Companies
from edgar.series import Series
from edgar.mutual_funds import MutualFunds
from edgar.variable_insurance_products import VariableInsuranceProducts
from edgar.datasets import Datasets
from edgar.current_events import CurrentEvents


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

    # def company_filings(self, cik: str = None, filing_type: str = None, sic_code: str = None, filing_number: str = None, company_name: str = None,
    #                     state: str = None, country: str = None, return_count: int = 100, start: int = 0, before: Union[str, date] = None,
    #                     after: Union[str, date] = None) -> List[dict]:
    #     """Returns all the filings of certain type for a particular company.

    #     Arguments:
    #     ----
    #     cik {str} -- The company CIK Number.

    #     filing_type {str} -- The filing type ID.

    #     Returns:
    #     ----
    #     dict -- A Dictionary containing the filing items.

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