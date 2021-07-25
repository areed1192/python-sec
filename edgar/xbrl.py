from typing import Dict
from typing import List
from typing import Union
from datetime import date
from datetime import datetime

from enum import Enum
from edgar.session import EdgarSession
from edgar.utilis import EdgarUtilities
from edgar.parser import EdgarParser


class Xbrl():

    """
    ## Overview:
    ----
    Extensible Business Markup Language (XBRL) is an XML-based format for
    reporting financial statements used by the SEC and financial regulatory
    agencies across the world. XBRL, in a separate XML file or more recently
    embedded in quarterly and annual HTML reports as inline XBRL, was first
    required by the SEC in 2009. XBRL facts must be associated for a
    standard US-GAAP or IFRS taxonomy. Companies can also extend standard
    taxonomies with their own custom taxonomies.
    """

    def __init__(self, session: EdgarSession) -> None:
        """Initializes the `Xbrl` object.

        ### Parameters
        ----
        session : `EdgarSession`
            An initialized session of the `EdgarSession`.

        ### Usage
        ----
            >>> edgar_client = EdgarClient()
            >>> xbrl_services = edgar_client.xbrl()
        """

        # Set the session.
        self.edgar_session: EdgarSession = session
        self.edgar_utilities: EdgarUtilities = EdgarUtilities()

    def __repr__(self) -> str:
        """String representation of the `EdgarClient.Xbrl` object."""

        # define the string representation
        str_representation = '<EdgarClient.Xbrl(active=True, connected=True)>'

        return str_representation

    def company_concepts(self, cik: str, concept: Union[str, Enum]) -> dict:
        """Returns all the XBRL disclosures from a single company and concept.

        ### Arguments:
        ----
        cik : str
            The CIK number you want to query.

        concept : Union[str, Enum]
            A taxonomy and tag you want to retrieve data for.

        ### Returns:
        ----
        dict :
            A collection of `CompanyConcept` resource objects.

        ### Usage:
        ----
            >>> edgar_client = EdgarClient()
            >>> xbrl_services = edgar_client.xbrl()
            >>> xbrl_services.company_concepts(
               cik='1326801',
               concept='AccountsPayableCurrent'
            )
        """
        if len(cik) < 10:
            num_of_zeros = 10 - len(cik)
            cik = num_of_zeros*"0" + cik

        endpoint = f'/api/xbrl/companyconcept/CIK{cik}/us-gaap/{concept}.json'

        # Grab the Data.
        response = self.edgar_session.make_request(
            method='get',
            endpoint=endpoint,
            use_api=True
        )

        return response

    def company_facts(self, cik: str) -> dict:
        """Returns all the company concepts data for a company.

        ### Arguments:
        ----
        cik : str
            The CIK number you want to query.

        ### Returns:
        ----
        dict :
            A collection of `CompanyFact` resource objects.

        ### Usage:
        ----
            >>> edgar_client = EdgarClient()
            >>> xbrl_services = edgar_client.xbrl()
            >>> xbrl_services.company_facts(
               cik='1326801'
            )
        """
        if len(cik) < 10:
            num_of_zeros = 10 - len(cik)
            cik = num_of_zeros*"0" + cik

        endpoint = f'/api/xbrl/companyfacts/CIK{cik}.json'

        # Grab the Data.
        response = self.edgar_session.make_request(
            method='get',
            endpoint=endpoint,
            use_api=True
        )

        return response

    def frames(self, concept: Union[str, Enum], unit_of_measure: Union[str, Enum], period: str) -> dict:
        """Aggregates one fact for each reporting entity that is last filed that most closely
        fits the calendrical period requested.

        ### Overview:
        ----
        This API supports for annual, quarterly and instantaneous data. Where the units of measure
        specified in the XBRL contains a numerator and a denominator, these are separated by “-per-”
        such as “USD-per-shares”. Note that the default unit in XBRL is “pure”. 

        The period format is CY#### for annual data (duration 365 days +/- 30 days), CY####Q# for
        quarterly data (duration 91 days +/- 30 days), and CY####Q#I for instantaneous data. Because
        company financial calendars can start and end on any month or day and even change in length
        from quarter to quarter to according to the day of the week, the frame data is assembled by
        the dates that best align with a calendar quarter or year. Data users should be mindful
        different reporting start and end dates for facts contained in a frame.

        ### Arguments:
        ----
        concept : Union[str, Enum]
            A taxonomy and tag you want to retrieve data for.

        unit_of_measure : Union[str, Enum]
            The unit of measure you want the data to be in for example,
            "USD" or "USD-per-shares".

        period. : Union[str, Enum]
            The period format, for example grabbing 2020 would look like
            CY2020. If I want Q1 of 2020 then it would look like CY2020Q1.
            Instantaneous data would look like CY2020Q1I.

        ### Returns:
        ----
        dict :
            A collection of `AggregatedCompanyFact` resource objects.

        ### Usage:
        ----
            >>> edgar_client = EdgarClient()
            >>> xbrl_services = edgar_client.xbrl()
            >>> xbrl_services.frames(
               concept='AccountsPayableCurrent',
               unit_of_measure='USD',
               period='CY2019Q1'
            )
        """

        endpoint = f'/api/xbrl/frames/us-gaap/{concept}/{unit_of_measure}/{period}.json'

        # Grab the Data.
        response = self.edgar_session.make_request(
            method='get',
            endpoint=endpoint,
            use_api=True
        )

        return response
