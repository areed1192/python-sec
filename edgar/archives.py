from typing import Dict
from typing import List
from typing import Union
from datetime import datetime
from edgar.session import EdgarSession
from edgar.utilis import EdgarUtilities


class Archives():

    """
    ## Overview:
    ----

    """

    def __init__(self, session: EdgarSession) -> None:
        """Initializes the `Archives` object.

        ### Parameters
        ----
        session : `EdgarSession`
            An initialized session of the `EdgarSession`.

        ### Usage
        ----
            >>> edgar_client = EdgarClient()
            >>> archives_services = edgar_client.archives()
        """

        # Set the session.
        self.edgar_session: EdgarSession = session
        self.edgar_utilities: EdgarUtilities = EdgarUtilities()

        # Set the endpoint.
        self.endpoint = '/Archives/edgar'

    def __repr__(self) -> str:
        """String representation of the `EdgarClient.Archives` object."""

        # define the string representation
        str_representation = '<EdgarClient.Archives (active=True, connected=True)>'

        return str_representation

    def get_company_directories(self, cik: str) -> dict:
        """Grabs all the filing directories for a company.

        ### Overview:
        ----
        Companies often file many SEC disclosures, so this endpoint
        makes grabbing all the endpoints associated with a company
        easy, by only requiring the CIK number.

        ### Arguments:
        ----
        cik : str
            The company CIK number, defined by the SEC.

        ### Returns:
        ----
        dict :
            A collection of `CompanyDirectory` resources.

        ### Usage:
        ----
            >>> edgar_client = EdgarClient()
            >>> archives_services = edgar_client.archives()
            >>> archives_services.get_company_directories(cik='1265107')
        """

        url = self.endpoint + "/data/{cik_number}/index.json".format(
            cik_number=cik
        )

        response = self.edgar_session.make_request(
            method='get',
            endpoint=url
        )

        directories = self.edgar_utilities.clean_directories(
            directories=response,
            cik=cik,
            service_url=self.endpoint
        )

        return directories

    def get_company_directory(self, cik: str, filing_id: str) -> dict:
        """Grabs all the filing directories for a company.

        ### Overview:
        ----
        Companies often file many SEC disclosures, so this endpoint
        makes grabbing all the endpoints associated with a company
        easy, by only requiring the CIK number.

        ### Arguments:
        ----
        cik : str
            The company CIK number, defined by the SEC.

        filing_id : str
            The filing ID you want to query.

        ### Returns:
        ----
        dict :
            A `CompanyDirectory` resource.

        ### Usage:
        ----
            >>> edgar_client = EdgarClient()
            >>> archives_services = edgar_client.archives()
            >>> archives_services.get_company_directory(
                cik='1265107',
                filing_id='000095010321003805'
            )
        """

        url = self.endpoint + f"/data/{cik}/{filing_id}/index.json".format(
            cik_number=cik
        )

        response = self.edgar_session.make_request(
            method='get',
            endpoint=url
        )

        directories = self.edgar_utilities.clean_filing_directory(
            directory=response,
            cik=cik
        )

        return directories

    def get_feed(self, year: int, quarter: str = None) -> dict:
        """Grabs old Tar and Zip files that can be downloaded.

        ### Arguments:
        ----
        year : int
            The year you wish to query. Cannot be lower than 1995.

        quarter : str
            Specifies the quarter you want to query. Can be one
            of 4 options: ['qtr1', 'qtr2', 'qtr3', 'qtr4']

        ### Returns:
        ----
        dict :
            A collection of `CompanyDirectory` resources.

        ### Usage:
        ----
            >>> edgar_client = EdgarClient()
            >>> archives_services = edgar_client.archives()
            >>> archives_services.get_feed(year=1996)
            >>> archives_services.get_feed(year=1996, quarter='qtr4')
        """

        if not quarter:
            url = self.endpoint + f"/Feed/{year}/index.json"
        else:
            quarter = quarter.upper()
            url = self.endpoint + f"/Feed/{year}/{quarter}/index.json"

        response = self.edgar_session.make_request(
            method='get',
            endpoint=url
        )

        if not quarter:
            directories = self.edgar_utilities.clean_directories(
                directories=response,
                service_url=self.endpoint
            )
        else:
            directories = self.edgar_utilities.clean_filing_directory(
                directory=response
            )

        return directories

    def get_old_loads(self, year: int, quarter: str = None) -> dict:
        """Grabs old file loads, Tar and Zip files that can be downloaded.

        ### Arguments:
        ----
        year : int
            The year you wish to query. Cannot be lower than 1995.

        quarter : str
            Specifies the quarter you want to query. Can be one
            of 4 options: ['qtr1', 'qtr2', 'qtr3', 'qtr4']

        ### Returns:
        ----
        dict :
            A collection of `CompanyDirectory` resources.

        ### Usage:
        ----
            >>> edgar_client = EdgarClient()
            >>> archives_services = edgar_client.archives()
            >>> archives_services.get_old_loads(year=1996)
            >>> archives_services.get_old_loads(year=1996, quarter='qtr4')
        """

        if not quarter:
            url = self.endpoint + f"/Oldloads/{year}/index.json"
        else:
            quarter = quarter.upper()
            url = self.endpoint + f"/Oldloads/{year}/{quarter}/index.json"

        response = self.edgar_session.make_request(
            method='get',
            endpoint=url
        )

        if not quarter:
            directories = self.edgar_utilities.clean_directories(
                directories=response,
                service_url=self.endpoint
            )
        else:
            directories = self.edgar_utilities.clean_filing_directory(
                directory=response
            )

        return directories

    def get_virtual_private_reference_rooms(self) -> dict:
        """Returns all the VPRR rooms indexed by the SEC.

        ### Returns:
        ----
        dict :
            A collection of `VPRR` resources.

        ### Usage:
        ----
            >>> edgar_client = EdgarClient()
            >>> archives_services = edgar_client.archives()
            >>> archives_services.get_virtual_private_reference_rooms()
        """

        url = self.endpoint + "/vprr/index.json"
        response = self.edgar_session.make_request(
            method='get',
            endpoint=url
        )

        directories = self.edgar_utilities.clean_directories(
            directories=response,
            service_url=url
        )

        return directories

    def get_virtual_private_reference_room(self, film_number: str) -> dict:
        """Grabs a specific VPRR.

        ### Arguments:
        ----
        film_number : str
            Each directory name is a 4-digit number corresponding to the first
            four digits of the Film Number/DCN.

        ### Returns:
        ----
        dict :
            A collection of `VPRR` resources.

        ### Usage:
        ----
            >>> edgar_client = EdgarClient()
            >>> archives_services = edgar_client.archives()
            >>> archives_services.get_virtual_private_reference_room(
                film_number='1403'
            )
        """

        url = self.endpoint + f"/vprr/{film_number}/index.json"
        response = self.edgar_session.make_request(
            method='get',
            endpoint=url
        )

        directories = self.edgar_utilities.clean_filing_directory(
            directory=response
        )

        return directories

    def get_daily_indexes(self) -> dict:
        """Gets All the daily indexes. The daily index files
        are through the current year.

        ### Returns:
        ----
        dict :
            A collection of `DailyIndexFeed` resources.

        ### Usage:
        ----
            >>> edgar_client = EdgarClient()
            >>> archives_services = edgar_client.archives()
            >>> archives_services.get_daily_indexes()
        """


        url = self.endpoint + f"/daily-index/index.json"

        response = self.edgar_session.make_request(
            method='get',
            endpoint=url
        )

        directories = self.edgar_utilities.clean_directories(
            directories=response,
            service_url=url
        )

        return directories

    def get_daily_index(self, year: int, quarter: str = None) -> dict:
        """Gets the daily indexes. The daily index files
        are through the current year.

        ### Arguments:
        ----
        year : int
            The year you wish to query. Cannot be lower than 1995.

        quarter : str (optional, Default=None)
            Specifies the quarter you want to query. Can be one
            of 4 options: ['qtr1', 'qtr2', 'qtr3', 'qtr4']

        ### Returns:
        ----
        dict :
            A collection of `DailyIndexFeed` resources.

        ### Usage:
        ----
            >>> edgar_client = EdgarClient()
            >>> archives_services = edgar_client.archives()
            >>> archives_services.get_daily_index(year=2002, quarter='qtr4')
        """

        if quarter:
            quarter = quarter.upper()
            url = self.endpoint + f"/daily-index/{year}/{quarter}/index.json"
        else:
            url = self.endpoint + f"/daily-index/{year}/index.json"

        response = self.edgar_session.make_request(
            method='get',
            endpoint=url
        )

        if not quarter:
            directories = self.edgar_utilities.clean_directories(
                directories=response,
                service_url=url
            )
        else:
            directories = self.edgar_utilities.clean_filing_directory(
                directory=response
            )

        return directories

    def get_full_indexes(self) -> dict:
        """Gets all the full indexes. 

        ### Overview:
        ----
        Full indexes offer a "bridge" between quarterly and daily indexes,
        compiling filings from the beginning of the current quarter through
        the previous business day. At the end of the quarter, the full 
        index is rolled into a static quarterly index.

        ### Returns:
        ----
        dict :
            A collection of `FullIndexFeed` resources.

        ### Usage:
        ----
            >>> edgar_client = EdgarClient()
            >>> archives_services = edgar_client.archives()
            >>> archives_services.get_full_index(year=2002, quarter='qtr4')
        """

        url = self.endpoint + f"/full-index/index.json"

        response = self.edgar_session.make_request(
            method='get',
            endpoint=url
        )


        directories = self.edgar_utilities.clean_directories(
            directories=response,
            service_url=url
        )

        return directories

    def get_full_index(self, year: int, quarter: str = None) -> dict:
        """Gets the full indexes. 

        ### Overview:
        ----
        Full indexes offer a "bridge" between quarterly and daily indexes,
        compiling filings from the beginning of the current quarter through
        the previous business day. At the end of the quarter, the full 
        index is rolled into a static quarterly index.

        ### Arguments:
        ----
        year : int
            The year you wish to query. Cannot be lower than 1995.

        quarter : str (optional, Default=None)
            Specifies the quarter you want to query. Can be one
            of 4 options: ['qtr1', 'qtr2', 'qtr3', 'qtr4']

        ### Returns:
        ----
        dict :
            A collection of `FullIndexFeed` resources.

        ### Usage:
        ----
            >>> edgar_client = EdgarClient()
            >>> archives_services = edgar_client.archives()
            >>> archives_services.get_full_index(year=2002, quarter='qtr4')
        """

        if quarter:
            quarter = quarter.upper()
            url = self.endpoint + f"/full-index/{year}/{quarter}/index.json"
        else:
            url = self.endpoint + f"/full-index/{year}/index.json"

        response = self.edgar_session.make_request(
            method='get',
            endpoint=url
        )

        if not quarter:
            directories = self.edgar_utilities.clean_directories(
                directories=response,
                service_url=url
            )
        else:
            directories = self.edgar_utilities.clean_filing_directory(
                directory=response
            )

        return directories
