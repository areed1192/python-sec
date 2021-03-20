from typing import Dict
from typing import List
from typing import Union
from datetime import datetime

from enum import Enum
from edgar.session import EdgarSession
from edgar.utilis import EdgarUtilities
from edgar.parser import EdgarParser


class Companies():

    """
    ## Overview:
    ----

    """

    def __init__(self, session: EdgarSession) -> None:
        """Initializes the `Comapnies` object.

        ### Parameters
        ----
        session : `EdgarSession`
            An initialized session of the `EdgarSession`.

        ### Usage
        ----
            >>> edgar_client = EdgarClient()
            >>> company_services = edgar_client.companies()
        """

        # Set the session.
        self.edgar_session: EdgarSession = session
        self.edgar_utilities: EdgarUtilities = EdgarUtilities()
        self.edgar_parser: EdgarParser = EdgarParser()

        # Set the endpoint.
        self.endpoint = '/cgi-bin/browse-edgar'
        self.params = {
            'action': 'getcompany',
            'output': 'atom',
            'State': '',
            'Country': '',
            'SIC': '',
            'CIK': '',
            'type': '',
            'company': '',
            'start': '',
            'datea': '',
            'dateb': ''
        }

    def __repr__(self) -> str:
        """String representation of the `EdgarClient.Companies` object."""

        # define the string representation
        str_representation = '<EdgarClient.Comapnies (active=True, connected=True)>'

        return str_representation

    def get_companies_by_state(self, state_code: Union[str, Enum], number_of_companies: int = 1000, start: int = None) -> dict:
        """Grabs all the companies that fall in a specific state.

        ### Arguments:
        ----
        state_code : Union[str, Enum]
            The two letter state code you want to query.

        number_of_companies : int (optional, Default=1000)
            Specifices the number of companies to return. If you want all companies
            then set to `None`. Be cautious though becuase you may be requesting
            100s of URLs.

        start: int (optional, Default=None)
            If you want to pick up where you left off from a previous parse, then
            set the `start` argument. This will start parsing the companies that come
            after this and up until the `number_of_companies`.

        ### Returns:
        ----
        dict :
            A collection of `Comapny` resource objects.

        ### Usage:
        ----
            >>> edgar_client = EdgarClient()
            >>> company_services = edgar_client.companies()
            >>> company_services.get_companies_by_state(state_code='tx')
        """

        # Grab the enumeration value if an Enum object was passed through.
        if isinstance(state_code, Enum):
            state_code = state_code.value

        self.params['State'] = state_code.upper()

        # Grab the Data.
        response = self.edgar_session.make_request(
            method='get',
            endpoint=self.endpoint,
            params=self.params
        )

        # Parse it.
        response = self.edgar_parser.parse_entries(
            response_text=response,
            num_of_items=number_of_companies,
            start=start
        )

        return response

    def get_companies_by_country(self, country_code: Union[str, Enum], number_of_companies: int = 1000, start: int = None) -> dict:
        """Grabs all the companies that fall in a specific country.

        ### Arguments:
        ----
        country_code : Union[str, Enum]
            The two letter country code or country name you want to query.

        number_of_companies : int (optional, Default=1000)
            Specifices the number of companies to return. If you want all companies
            then set to `None`. Be cautious though becuase you may be requesting
            100s of URLs.

        start: int (optional, Default=None)
            If you want to pick up where you left off from a previous parse, then
            set the `start` argument. This will start parsing the companies that come
            after this and up until the `number_of_companies`.

        ### Returns:
        ----
        dict :
            A collection of `Comapny` resource objects.

        ### Usage:
        ----
            >>> edgar_client = EdgarClient()
            >>> company_services = edgar_client.companies()
            >>> company_services.get_companies_by_country(country_code='q1')
            >>> company_services.get_companies_by_country(country_code=CountryCode.AUSTRALIA)
        """

        # Grab the enumeration value if an Enum object was passed through.
        if isinstance(country_code, Enum):
            country_code = country_code.value

        self.params['Country'] = country_code.upper()

        # Grab the Data.
        response = self.edgar_session.make_request(
            method='get',
            endpoint=self.endpoint,
            params=self.params
        )

        # Parse it.
        response = self.edgar_parser.parse_entries(
            response_text=response,
            num_of_items=number_of_companies,
            start=start
        )

        return response

    def get_companies_by_sic(self, sic_code: Union[str, Enum], number_of_companies: int = 1000, start: int = None) -> dict:
        """Grabs all the companies that fall under a specific SIC code.

        ### Arguments:
        ----
        sic_code : Union[str, Enum]
            The 3 or 4 number SIC code you want to query.

        number_of_companies : int (optional, Default=1000)
            Specifices the number of companies to return. If you want all companies
            then set to `None`. Be cautious though becuase you may be requesting
            100s of URLs.

        start: int (optional, Default=None)
            If you want to pick up where you left off from a previous parse, then
            set the `start` argument. This will start parsing the companies that come
            after this and up until the `number_of_companies`.

        ### Returns:
        ----
        dict :
            A collection of `Comapny` resource objects.

        ### Usage:
        ----
            >>> edgar_client = EdgarClient()
            >>> company_services = edgar_client.companies()
            >>> company_services.get_companies_by_sic(sic_code='800')
            >>> company_services.get_companies_by_sic(
                sic_code=StandardIndustrialClassificationCodes.OIL_AND_GAS_FIELD_SERVICES_NEC
            )
        """

        # Grab the enumeration value if an Enum object was passed through.
        if isinstance(sic_code, Enum):
            sic_code = sic_code.value

        self.params['SIC'] = sic_code.upper()

        # Grab the Data.
        response = self.edgar_session.make_request(
            method='get',
            endpoint=self.endpoint,
            params=self.params
        )

        # Parse it.
        response = self.edgar_parser.parse_entries(
            response_text=response,
            num_of_items=number_of_companies,
            start=start
        )

        return response

    def get_company_by_file_number(self, file_number: str) -> dict:
        """Finds the company by doing a reverse look based on the file number.

        ### Arguments:
        ----
        file_number : str
            The filing number you want to use in order to do the reverse
            lookup.

        ### Returns:
        ----
        dict :
            A `Comapny` resource object.

        ### Usage:
        ----
            >>> edgar_client = EdgarClient()
            >>> company_services = edgar_client.companies()
            >>> company_services.get_companies_by_file_number(file_number='021-230507')
        """

        self.params['filenum'] = file_number

        # Grab the Data.
        response = self.edgar_session.make_request(
            method='get',
            endpoint=self.endpoint,
            params=self.params
        )

        # Parse it.
        response = self.edgar_parser.parse_entries(
            response_text=response
        )

        return response

    def get_company_by_cik(self, cik: str) -> dict:
        """Searches for a company using their CIK number.

        ### Arguments:
        ----
        cik : str
            The CIK number you want to lookup.

        ### Returns:
        ----
        dict :
            A `Comapny` resource object.

        ### Usage:
        ----
            >>> edgar_client = EdgarClient()
            >>> company_services = edgar_client.companies()
            >>> company_services.get_company_by_cik(cik='1628533')
        """

        self.params['CIK'] = cik

        # Grab the Data.
        response = self.edgar_session.make_request(
            method='get',
            endpoint=self.endpoint,
            params=self.params
        )

        # Parse it.
        response = self.edgar_parser.parse_entries(
            response_text=response
        )

        return response

    def get_companies_by_name(self, name: str) -> dict:
        """Searches for a company by looking for it's name. Can
        return multiple results depending on how simply you make
        the search.

        ### Arguments:
        ----
        name : str
            The name you can to lookup.

        ### Returns:
        ----
        dict :
            A `Comapny` resource object.

        ### Usage:
        ----
            >>> edgar_client = EdgarClient()
            >>> company_services = edgar_client.companies()
            >>> company_services.get_companies_by_name(name='Microsoft')
        """

        self.params['company'] = name

        # Grab the Data.
        response = self.edgar_session.make_request(
            method='get',
            endpoint=self.endpoint,
            params=self.params
        )

        # Parse it.
        response = self.edgar_parser.parse_entries(
            response_text=response
        )

        return response