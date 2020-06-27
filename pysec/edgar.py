import requests
import xml.etree.ElementTree as ET

from typing import List
from typing import Union
from datetime import datetime
from datetime import date

from pysec.parser import EDGARParser

# https://www.sec.gov/cgi-bin/srch-edgar?text=form-type%3D%2810-q*+OR+10-k*%29&first=2020&last=2020

class EDGARQuery():

    def __init__(self):
        """Initalizes the EDGAR Client with the different endpoints used."""        

        # base URL for the SEC EDGAR browser
        self.sec_url = "https://www.sec.gov"

        self.archive_service = "https://www.sec.gov/Archives/edgar"
        self.browse_service = "https://www.sec.gov/cgi-bin/browse-edgar"
        self.issuer_service = "https://www.sec.gov/cgi-bin/own-disp"
        self.search_service = "https://www.sec.gov/cgi-bin/srch-edgar"
        self.series_service = "https://www.sec.gov/cgi-bin/series"
        self.current_service = "https://www.sec.gov/cgi-bin/current"

        self.sec_cgi_endpoint = "https://www.sec.gov/cgi-bin"
        self.cik_lookup = 'cik_lookup'
        self.mutal_fund_search = 'series'

        self.parser_client = EDGARParser()

    def company_directories(self, cik: str) -> dict:
        """Grabs all the filing directories for a company.

        Overview:
        ----
        Companies often file many SEC disclosures, so this endpoint
        makes grabbing all the endpoints associated with a company
        easy, by only requiring the CIK number.

        Arguments:
        ----
        cik {str} -- The company CIK number, defined by the SEC.

        Returns:
        ----
        dict -- A Dictionary containing the directory filings path.

        Usage:
        ----
            >>> edgar_client = EDGARQuery()
            >>> company_filings = edgar_client.company_directories(cik='1265107')
            [
                {
                    'last-modified': '2019-07-02 12:27:42',
                    'name': '000000000019010655',
                    'size': '',
                    'type': 'folder.gif',
                    'url': 'https://www.sec.gov/Archives/edgar/data/1265107/000000000019010655/index.json'
                },
                {
                    'last-modified': '2019-07-01 17:17:26',
                    'name': '000110465919038688',
                    'size': '',
                    'type': 'folder.gif',
                    'url': 'https://www.sec.gov/Archives/edgar/data/1265107/000110465919038688/index.json'
                }
            ]
        """

        # Build the URL.
        url = self.archive_service + "/data/{cik_number}/index.json".format(
            cik_number=cik
        )

        cleaned_directories = []
        directories = requests.get(url=url).json()

        # Loop through each item.
        for directory in directories['directory']['item']:

            # Create the URL.
            directory['url'] = self.archive_service + "/data/{cik_number}/{directory_id}/index.json".format(
                cik_number=cik,
                directory_id=directory['name']
            )

            directory['filing_id'] = directory.pop('name')
            directory['last_modified'] = directory.pop('last-modified')

            cleaned_directories.append(directory)

        return cleaned_directories

    def company_directory(self, cik: str, filing_id: str) -> dict:
        """Grabs all the items from a specific filing.

        Overview:
        ----
        The SEC organizes filings by CIK number which represent a single
        entity. Each entity can have multiple filings, which is identified
        by a filing ID. That filing can contain multiple items in it.

        This endpoint will return all the items from a specific filing that
        belongs to a single company.

        Arguments:
        ----
        cik {str} -- The company CIK number, defined by the SEC.

        filing_id {str} -- The ID of filing to pull.

        Returns:
        ----
        dict -- A Dictionary containing the filing items.

        Usage:
        ----
            >>> edgar_client = EDGARQuery()
            >>> company_filings = edgar_client.company_directory(cik='1265107', filing_id='000110465919038688')
            [
                {
                    'item_id': '0001104659-19-038688.txt',
                    'last_modified': '2019-07-01 17:17:26',
                    'size': '',
                    'type': 'text.gif',
                    'url': 'https://www.sec.gov/Archives/edgar/data/1265107/000110465919038688/0001104659-19-038688.txt'
                },
                {
                    'item_id': 'a19-12321_2425.htm',
                    'last_modified': '2019-07-01 17:17:26',
                    'size': '37553',
                    'type': 'text.gif',
                    'url': 'https://www.sec.gov/Archives/edgar/data/1265107/000110465919038688/a19-12321_2425.htm'
                }
            ]
        """

        url = self.archive_service + "/data/{cik_number}/{filing_number}/index.json".format(
            cik_number=cik,
            filing_number=filing_id
        )

        cleaned_items = []
        directory = requests.get(url=url).json()

        for item in directory['directory']['item']:

            item['url'] = self.archive_service + "/data/{cik_number}/{directory_id}/{file_id}".format(
                cik_number=cik,
                directory_id=filing_id,
                file_id=item['name']
            )

            item['item_id'] = item.pop('name')
            item['last_modified'] = item.pop('last-modified')
            cleaned_items.append(item)

        return cleaned_items

    def company_filings_by_type(self, cik: str, filing_type: str) -> List[dict]:
        """Returns all the filings of certain type for a particular company.

        Arguments:
        ----
        cik {str} -- The company CIK Number.

        filing_type {str} -- The filing type ID.

        Returns:
        ----
        dict -- A Dictionary containing the filing items.

        Usage:
        ----
            >>> edgar_client = EDGARQuery()
            >>> company_filings = edgar_client.company_directory(cik='1265107', filing_id='000110465919038688')
            [
                {
                    'item_id': '0001104659-19-038688.txt',
                    'last_modified': '2019-07-01 17:17:26',
                    'size': '',
                    'type': 'text.gif',
                    'url': 'https://www.sec.gov/Archives/edgar/data/1265107/000110465919038688/0001104659-19-038688.txt'
                },
                {
                    'item_id': 'a19-12321_2425.htm',
                    'last_modified': '2019-07-01 17:17:26',
                    'size': '37553',
                    'type': 'text.gif',
                    'url': 'https://www.sec.gov/Archives/edgar/data/1265107/000110465919038688/a19-12321_2425.htm'
                }
            ]
        """

        # Set the params
        params = {
            'action': 'getcompany',
            'CIK': cik,
            'type': filing_type,
            'output': 'atom'
        }

        # Grab the response.
        response = requests.get(
            url=self.browse_service,
            params=params
        )

        # Parse the entries.
        entries = self.parser_client.parse_entries(entries_text=response.text)

        return entries

    def companies_by_state(self, state: str, num_of_companies: int = None) -> List[dict]:
        """Returns all the companies that fall under a given state.

        Arguments:
        ----
        state {str} -- [description]

        Returns:
        ----
        List[dict] -- [description]
        """

        # define the arguments of the request
        search_sic_params = {
            'State': state,
            'Count': '100',
            'action': 'getcompany',
            'output': 'atom'
        }

        response = requests.get(
            url=self.browse_service,
            params=search_sic_params
        )

        # Parse the entries.
        entries = self.parser_client.parse_entries(
            entries_text=response.text,
            num_of_items=num_of_companies
        )

        return entries

    def companies_by_country(self, country: str, num_of_companies: int = None) -> List[dict]:
        """Grabs all the companies that fall under a particular country code.

        Arguments:
        ----
        country {str} -- The country code.

        Keyword Arguments:
        ----
        num_of_companies {int} -- If you would like to limit the number of results, then
            specify the number of companies you want back. (default: {None})

        Returns:
        ----
        List[dict] -- A list of Entry resources.
        """

        # define the arguments of the request
        search_sic_params = {
            'Country': country,
            'Count': '100',
            'action': 'getcompany',
            'output': 'atom'
        }

        # Grab the Response.
        response = requests.get(
            url=self.browse_service,
            params=search_sic_params
        )

        # Parse the entries.
        entries = self.parser_client.parse_entries(
            entries_text=response.text,
            num_of_items=num_of_companies
        )

        return entries

    def companies_by_sic(self, sic_code: str, num_of_companies: int = None) -> List[dict]:
        """Grabs all companies with a certain SIC code.

        Returns all companies, that fall under a particular SIC code. The information returned
        by this endpoint depends on the infromation available on the company.

        Arguments:
        ----
        sic_code {str} -- The SIC code for a particular Industry.

        Keyword Arguments:
        ----
        num_of_companies {int} -- If you would like to limit the number of results, then
            specify the number of companies you want back. (default: {None})

        Returns:
        ----
            list[dict] -- A list of companies with the following attributes:

            [
                {
                    "state": "MN",
                    "cik": "0000066740",
                    "last-date": "",
                    "name": "3M CO",
                    "sic-code": "3841",
                    "id": "urn:tag:www.sec.gov:cik=0000066740",
                    "href": "URL",
                    "type": "html",
                    "summary": "<strong>CIK:</strong> 0000066740, <strong>State:</strong> MN",
                    "title": "3M CO",
                    "updated": "2020-04-05T15:21:24-04:00",
                    "atom_owner_only": "URL",
                    "atom_owner_exclude": "URL",
                    "atom_owner_include": "URL",
                    "html_owner_only": "URL",
                    "html_owner_exclude": "URL",
                    "html_owner_include": "URL",
                    "atom_owner_only_filtered_date": "URL",
                    "atom_owner_exclude_filtered_date": "URL",
                    "atom_owner_include_filtered_date": "URL",
                    "html_owner_only_filtered_date": "URL",
                    "html_owner_exclude_filtered_date": "URL",
                    "html_owner_include_filtered_date": "URL",
                }
            ]
        """

        # define the arguments of the request
        search_sic_params = {
            'Count': '100',
            'SIC': sic_code,
            'Count': '100',
            'action': 'getcompany',
            'output': 'atom'
        }

        # Make the response.
        response = requests.get(
            url=self.browse_service,
            params=search_sic_params
        )

        # Parse the entries.
        entries = self.parser_client.parse_entries(entries_text=response.text)

        return entries

    def ownership_filings_by_cik(self, cik: str, before: Union[str, date] = None, after: Union[str, date] = None) -> List[dict]:
        """Returns all the ownership filings for a given CIK number in a given date range.

        Arguments:
        ----
        cik {str} -- The CIK number of the company to be queried.

        Keyword Arguments:
        ----
        before {Union[str, date]} -- Represents filings that you want before a certain
            date. For example, "2019-12-01" means return all the filings BEFORE
            Decemeber 1, 2019. (default: {None})

        after {Union[str, date]} -- Represents filings that you want after a certain
            date. For example, "2019-12-01" means return all the filings AFTER 
            Decemeber 1, 2019. (default: {None})

        Returns:
        ----
        List[dict] -- A list of ownership filings.
        """

        # define the arguments of the request
        search_params = {
            'CIK': cik,
            'Count': '100',
            'myowner': 'only',
            'action': 'getcompany',
            'output': 'atom',
            'datea': after,
            'dateb': before
        }

        # Make the response.
        response = requests.get(
            url=self.browse_service,
            params=search_params
        )

        # Parse the entries.
        entries = self.parser_client.parse_entries(entries_text=response.text)

        return entries

    def non_ownership_filings_by_cik(self, cik: str, before: str = None, after: str = None) -> List[dict]:
        """Returns all the non-ownership filings for a given CIK number in a given date range.

        Arguments:
        ----
        cik {str} -- The CIK number of the company to be queried.

        Keyword Arguments:
        ----
        before {Union[str, date]} -- Represents filings that you want before a certain
            date. For example, "2019-12-01" means return all the filings BEFORE
            Decemeber 1, 2019. (default: {None})

        after {Union[str, date]} -- Represents filings that you want after a certain
            date. For example, "2019-12-01" means return all the filings AFTER 
            Decemeber 1, 2019. (default: {None})

        Returns:
        ----
        List[dict] -- A list of ownership filings.
        """

        # define the arguments of the request
        search_params = {
            'CIK': cik,
            'Count': '100',
            'myowner': 'exclude',
            'action': 'getcompany',
            'output': 'atom',
            'datea': after,
            'dateb': before
        }

        # Make the response.
        response = requests.get(
            url=self.browse_service,
            params=search_params
        )

        # Parse the entries.
        entries = self.parser_client.parse_entries(entries_text=response.text)

        return entries

    def all_filings_by_cik(self, cik: str, before: str = None, after: str = None) -> List[dict]:
        """Returns all the filings (ownership and non-ownership) for a given CIK number in a given date range.

        Arguments:
        ----
        cik {str} -- The CIK number of the company to be queried.

        Keyword Arguments:
        ----
        before {Union[str, date]} -- Represents filings that you want before a certain
            date. For example, "2019-12-01" means return all the filings BEFORE
            Decemeber 1, 2019. (default: {None})

        after {Union[str, date]} -- Represents filings that you want after a certain
            date. For example, "2019-12-01" means return all the filings AFTER 
            Decemeber 1, 2019. (default: {None})

        Returns:
        ----
        List[dict] -- A list of ownership filings.
        """

        # define the arguments of the request
        search_params = {
            'CIK': cik,
            'Count': '100',
            'myowner': 'include',
            'action': 'getcompany',
            'output': 'atom',
            'datea': after,
            'dateb': before
        }

        # Make the response.
        response = requests.get(
            url=self.browse_service,
            params=search_params
        )

        # Parse the entries.
        entries = self.parser_client.parse_entries(entries_text=response.text)

        return entries

    def ownership_filings_by_company_name(self, company_name: str, before: str = None, after: str = None) -> List[dict]:
        """Returns all the filings ownership for a given company in a given date range.

        Arguments:
        ----
        company_name {str} -- The name of the company to be queried.

        Keyword Arguments:
        ----
        before {Union[str, date]} -- Represents filings that you want before a certain
            date. For example, "2019-12-01" means return all the filings BEFORE
            Decemeber 1, 2019. (default: {None})

        after {Union[str, date]} -- Represents filings that you want after a certain
            date. For example, "2019-12-01" means return all the filings AFTER 
            Decemeber 1, 2019. (default: {None})

        Returns:
        ----
        List[dict] -- A list of ownership filings.
        """

        # define the arguments of the request
        search_params = {
            'company': company_name,
            'Count': '100',
            'myowner': 'only',
            'action': 'getcompany',
            'output': 'atom',
            'datea': after,
            'dateb': before
        }

        # Make the response.
        response = requests.get(
            url=self.browse_service,
            params=search_params
        )

        # Parse the entries.
        entries = self.parser_client.parse_entries(entries_text=response.text)

        return entries

    def non_ownership_filings_by_company_name(self, company_name: str, before: str = None, after: str = None) -> List[dict]:
        """Returns all the filings non-ownership for a given company in a given date range.

        Arguments:
        ----
        company_name {str} -- The name of the company to be queried.

        Keyword Arguments:
        ----
        before {Union[str, date]} -- Represents filings that you want before a certain
            date. For example, "2019-12-01" means return all the filings BEFORE
            Decemeber 1, 2019. (default: {None})

        after {Union[str, date]} -- Represents filings that you want after a certain
            date. For example, "2019-12-01" means return all the filings AFTER 
            Decemeber 1, 2019. (default: {None})

        Returns:
        ----
        List[dict] -- A list of ownership filings.
        """

        # define the arguments of the request
        search_params = {
            'company': company_name,
            'Count': '100',
            'myowner': 'exclude',
            'action': 'getcompany',
            'output': 'atom',
            'datea': after,
            'dateb': before
        }

        # Make the response.
        response = requests.get(
            url=self.browse_service,
            params=search_params
        )

        # Parse the entries.
        entries = self.parser_client.parse_entries(entries_text=response.text)

        return entries

    def all_filings_by_company_name(self, company_name: str, before: str = None, after: str = None) -> List[dict]:
        """Returns all the filings (ownership and non-ownership) for a given company in a given date range.

        Arguments:
        ----
        company_name {str} -- The name of the company to be queried.

        Keyword Arguments:
        ----
        before {Union[str, date]} -- Represents filings that you want before a certain
            date. For example, "2019-12-01" means return all the filings BEFORE
            Decemeber 1, 2019. (default: {None})

        after {Union[str, date]} -- Represents filings that you want after a certain
            date. For example, "2019-12-01" means return all the filings AFTER 
            Decemeber 1, 2019. (default: {None})

        Returns:
        ----
        List[dict] -- A list of ownership filings.
        """

        # define the arguments of the request
        search_params = {
            'company': company_name,
            'Count': '100',
            'myowner': 'include',
            'action': 'getcompany',
            'output': 'atom',
            'datea': after,
            'dateb': before
        }

        # Make the response.
        response = requests.get(
            url=self.browse_service,
            params=search_params
        )

        # Parse the entries.
        entries = self.parser_client.parse_entries(entries_text=response.text)

        return entries
    
    def get_issuers_by_cik(self, cik: str) -> List[dict]:
        """Returns all the issuers for a given CIK number.

        Arguments:
        ----
        cik {str} -- The CIK number of the company to be queried.

        Returns:
        ----
        List[dict] -- A list of Issuer documents.
        """

        # define the arguments of the request
        search_params = {
            'count': '100',
            'CIK':cik,
            'action': 'getissuer'
        }

        # Make the response.
        response = requests.get(
            url=self.issuer_service,
            params=search_params
        )

        # Parse the entries.
        entries = self.parser_client.parse_issuer_table(entries_text=response.text)

        return entries

    def get_mutual_funds_by_name(self, company_name: str, before: str = None, after: str = None) -> List[dict]:
        """Returns all mutual funds for a given name in a given date range.

        Arguments:
        ----
        company_name {str} -- The name of the company to be queried.

        Keyword Arguments:
        ----
        before {Union[str, date]} -- Represents filings that you want before a certain
            date. For example, "2019-12-01" means return all the filings BEFORE
            Decemeber 1, 2019. (default: {None})

        after {Union[str, date]} -- Represents filings that you want after a certain
            date. For example, "2019-12-01" means return all the filings AFTER 
            Decemeber 1, 2019. (default: {None})

        Returns:
        ----
        List[dict] -- A list of mutual funds.
        """

        # define the arguments of the request
        search_params = {
            'company': company_name,
            'Count': '100',
            'myowner': 'include',
            'action': 'getcompany',
            'type': '485',
            'output': 'atom',
            'datea': after,
            'dateb': before
        }

        # Make the response.
        response = requests.get(
            url=self.browse_service,
            params=search_params
        )

        # Parse the entries.
        entries = self.parser_client.parse_entries(entries_text=response.text)

        return entries

    def get_mutual_funds_prospectus_by_cik(self, cik: str, before: str = None, after: str = None) -> List[dict]:
        """Returns all the filings (ownership and non-ownership) for a given company in a given date range.

        Arguments:
        ----
        cik {str} -- The CIK number of the company to be queried.

        Keyword Arguments:
        ----
        before {Union[str, date]} -- Represents filings that you want before a certain
            date. For example, "2019-12-01" means return all the filings BEFORE
            Decemeber 1, 2019. (default: {None})

        after {Union[str, date]} -- Represents filings that you want after a certain
            date. For example, "2019-12-01" means return all the filings AFTER 
            Decemeber 1, 2019. (default: {None})

        Returns:
        ----
        List[dict] -- A list of mutual fund prospectus.
        """

        # define the arguments of the request
        search_params = {
            'CIK': cik,
            'Count': '100',
            'myowner': 'include',
            'action': 'getcompany',
            'type': '485',
            'hidefilings': '0',
            'output': 'atom',
            'datea': after,
            'dateb': before
        }

        # Make the response.
        response = requests.get(
            url=self.browse_service,
            params=search_params
        )

        # Parse the entries.
        entries = self.parser_client.parse_entries(entries_text=response.text)

        return entries

    def get_mutual_funds_proxy_records_by_cik(self, cik: str, before: str = None, after: str = None) -> List[dict]:
        """Returns all the Mutual Fund Proxy records for a given CIK number.

        Arguments:
        ----
        cik {str} -- The CIK number of the company to be queried.

        Keyword Arguments:
        ----
        before {Union[str, date]} -- Represents filings that you want before a certain
            date. For example, "2019-12-01" means return all the filings BEFORE
            Decemeber 1, 2019. (default: {None})

        after {Union[str, date]} -- Represents filings that you want after a certain
            date. For example, "2019-12-01" means return all the filings AFTER 
            Decemeber 1, 2019. (default: {None})

        Returns:
        ----
        List[dict] -- A list of mutual fund prospectus.
        """

        # define the arguments of the request
        search_params = {
            'CIK': cik,
            'Count': '100',
            'myowner': 'include',
            'action': 'getcompany',
            'type': 'N-PX',
            'hidefilings': '0',
            'output': 'atom',
            'datea': after,
            'dateb': before
        }

        # Make the response.
        response = requests.get(
            url=self.browse_service,
            params=search_params
        )

        # Parse the entries.
        entries = self.parser_client.parse_entries(entries_text=response.text)

        return entries

    def get_mutual_funds_shareholder_reports_by_cik(self, cik: str, before: str = None, after: str = None) -> List[dict]:
        """Returns all the Mutual Fund Proxy Shareholder Reports for a given CIK number.

        Arguments:
        ----
        cik {str} -- The CIK number of the company to be queried.

        Keyword Arguments:
        ----
        before {Union[str, date]} -- Represents filings that you want before a certain
            date. For example, "2019-12-01" means return all the filings BEFORE
            Decemeber 1, 2019. (default: {None})

        after {Union[str, date]} -- Represents filings that you want after a certain
            date. For example, "2019-12-01" means return all the filings AFTER 
            Decemeber 1, 2019. (default: {None})

        Returns:
        ----
        List[dict] -- A list of mutual fund prospectus.
        """

        # define the arguments of the request
        search_params = {
            'CIK': cik,
            'Count': '100',
            'myowner': 'include',
            'action': 'getcompany',
            'type': 'N-CSR',
            'hidefilings': '0',
            'output': 'atom',
            'datea': after,
            'dateb': before
        }

        # Make the response.
        response = requests.get(
            url=self.browse_service,
            params=search_params
        )

        # Parse the entries.
        entries = self.parser_client.parse_entries(entries_text=response.text)

        return entries

    def get_mutual_funds_statutory_prospectus_by_cik(self, cik: str, before: str = None, after: str = None) -> List[dict]:
        """Returns all the Mutual Fund Statutory Prospectus for a given CIK number.

        Arguments:
        ----
        cik {str} -- The CIK number of the company to be queried.

        Keyword Arguments:
        ----
        before {Union[str, date]} -- Represents filings that you want before a certain
            date. For example, "2019-12-01" means return all the filings BEFORE
            Decemeber 1, 2019. (default: {None})

        after {Union[str, date]} -- Represents filings that you want after a certain
            date. For example, "2019-12-01" means return all the filings AFTER 
            Decemeber 1, 2019. (default: {None})

        Returns:
        ----
        List[dict] -- A list of mutual fund prospectus.
        """

        # define the arguments of the request
        search_params = {
            'CIK': cik,
            'Count': '100',
            'myowner': 'include',
            'action': 'getcompany',
            'type': '485',
            'hidefilings': '0',
            'output': 'atom',
            'datea': after,
            'dateb': before
        }

        # Make the response.
        response = requests.get(
            url=self.browse_service,
            params=search_params
        )

        # Parse the entries.
        entries = self.parser_client.parse_entries(entries_text=response.text)

        return entries

    def get_mutual_funds_summary_prospectus_by_cik(self, cik: str, before: str = None, after: str = None) -> List[dict]:
        """Returns all the Mutual Fund Summary Prospectus for a given CIK number.

        Arguments:
        ----
        cik {str} -- The CIK number of the company to be queried.

        Keyword Arguments:
        ----
        before {Union[str, date]} -- Represents filings that you want before a certain
            date. For example, "2019-12-01" means return all the filings BEFORE
            Decemeber 1, 2019. (default: {None})

        after {Union[str, date]} -- Represents filings that you want after a certain
            date. For example, "2019-12-01" means return all the filings AFTER 
            Decemeber 1, 2019. (default: {None})

        Returns:
        ----
        List[dict] -- A list of mutual fund prospectus.
        """

        # define the arguments of the request
        search_params = {
            'CIK': cik,
            'Count': '100',
            'myowner': 'include',
            'action': 'getcompany',
            'type': '497K',
            'hidefilings': '0',
            'output': 'atom',
            'datea': after,
            'dateb': before
        }

        # Make the response.
        response = requests.get(
            url=self.browse_service,
            params=search_params
        )

        # Parse the entries.
        entries = self.parser_client.parse_entries(entries_text=response.text)

        return entries

    def get_mutual_funds_effectiveness_notices_by_cik(self, cik: str, before: str = None, after: str = None) -> List[dict]:
        """Returns all the Mutual Fund Summary Prospectus for a given CIK number.

        Arguments:
        ----
        cik {str} -- The CIK number of the company to be queried.

        Keyword Arguments:
        ----
        before {Union[str, date]} -- Represents filings that you want before a certain
            date. For example, "2019-12-01" means return all the filings BEFORE
            Decemeber 1, 2019. (default: {None})

        after {Union[str, date]} -- Represents filings that you want after a certain
            date. For example, "2019-12-01" means return all the filings AFTER 
            Decemeber 1, 2019. (default: {None})

        Returns:
        ----
        List[dict] -- A list of mutual fund prospectus.
        """

        # define the arguments of the request
        search_params = {
            'CIK': cik,
            'Count': '100',
            'myowner': 'include',
            'action': 'getcompany',
            'type': 'EFFECT',
            'output': 'atom',
            'datea': after,
            'dateb': before
        }

        # Make the response.
        response = requests.get(
            url=self.browse_service,
            params=search_params
        )

        # Parse the entries.
        entries = self.parser_client.parse_entries(entries_text=response.text)

        return entries

    def get_variable_insurance_products_by_name(self, product_name: str) -> List[dict]:
        """Returns all the variable insurance products defined by the given name.

        Arguments:
        ----
        product_name {str} -- Variable insurance products.

        Returns:
        ----
        List[dict] -- A list of mutual funds.
        """

        # define the arguments of the request
        search_params = {
            'company': product_name,
            'sc': 'companyseries'
        }

        # Make the response.
        response = requests.get(
            url=self.series_service,
            params=search_params
        )

        # Parse the entries.
        entries = self.parser_client.parse_variable_products_company_table(product_table_page=response.text)

        return entries

    def get_variable_insurance_products_by_cik(self, cik: str, before: str = None, after: str = None) -> List[dict]:
        """Returns all the filings (ownership and non-ownership) for a given company in a given date range.

        Arguments:
        ----
        cik {str} -- The CIK number of the company to be queried.

        Keyword Arguments:
        ----
        before {Union[str, date]} -- Represents filings that you want before a certain
            date. For example, "2019-12-01" means return all the filings BEFORE
            Decemeber 1, 2019. (default: {None})

        after {Union[str, date]} -- Represents filings that you want after a certain
            date. For example, "2019-12-01" means return all the filings AFTER 
            Decemeber 1, 2019. (default: {None})

        Returns:
        ----
        List[dict] -- A list of mutual fund prospectus.
        """

        # define the arguments of the request
        search_params = {
            'CIK': cik,
            'Count': '100',
            'myowner': 'include',
            'action': 'getcompany',
            'type': '485',
            'hidefilings': '0',
            'output': 'atom',
            'datea': after,
            'dateb': before
        }

        # Make the response.
        response = requests.get(
            url=self.series_service,
            params=search_params
        )

        # Parse the entries.
        entries = self.parser_client.parse_entries(entries_text=response.text)

        return entries

    def get_current_event_filings(self, days_prior: int, form: str, form_id: str = None) -> List[dict]:
        """Query current filigns by type.

        Arguments:
        ----
        day (int): The number of days prior you would like to analyze. Can be one of
            the following: [0, 1, 2, 3, 4, 5]
        
        form (str): The form you would like to analyze. Can be one of
            the following: ['10-k-annual', '10-k-quarterly', '14-proxies', '485-fund-prosp.', '8-k', 's-8', 'all']
        
        form_id (str, optional): Represents the Form-ID and can be used to override the `form` argument. Defaults to None.

        Returns:
        ----
        List[Dict]: A list of current event filings.
        """        
        
        form_dict = {
            '10-k-annual': 0,
            '10-k-quarterly': 1,
            '14-proxies': 2,
            '485-fund-prosp.': 3,
            '8-k': 4,
            's-8': 5,
            'all': 6            
        }

        if form in form_dict:
            form_id_arg = form_dict[form]
        else:
            raise ValueError("The argument you've provided for form is incorrect.")

        # define the arguments of the request
        search_params = {
            'q1': days_prior,
            'q2': form_id_arg,
            'q3': form_id
        }

        # Make the response.
        response = requests.get(
            url=self.current_service,
            params=search_params
        )

        # Parse the entries.
        entries = self.parser_client.parse_current_event_table(current_event_page=response.text)

        return entries

    def get_quarterly_index(self, year: int, quarter: int) -> List[dict]:
        """Grabs all the filings belong to a specific quarter and year.

        Arguments:
        ----
        year (int): The year from which to query. Must be >= 1994.

        quarter (int): The quarter from which to query. Can be one the
            following: [1, 2, 3, 4]

        Returns:
        ----
        List[dict]: A list of directory links and directory files.
        """

        if (year < 1994) or (year > datetime.now().year):
            raise ValueError("The year you specified can not be pulled.")

        if quarter not in [1, 2, 3, 4]:
            raise ValueError("The quarter you specified is incorrect.")

        quarterly_url = self.archive_service + "/full-index/{year}/{qtr}/".format(
            year=year,
            qtr="QTR" + str(quarter)
        )

        # Define the full URL.
        full_url = quarterly_url + "index.json"

        # Make the response.
        directories = requests.get(
            url = full_url
        ).json()

        cleaned_directories = []

        # Loop through each item.
        for item in directories['directory']['item']:
            new_item = {key.replace("-","_"): value for key, value in item.items()}
            new_item['url'] = quarterly_url + item['href']
            cleaned_directories.append(new_item)

        return cleaned_directories


    def get_quarterly_indexes(self) -> List[dict]:
        """Grabs all the Quarterly Index filings.

        Returns:
        ----
        List[dict]: A list of directory links and directory files.
        """        

        url = self.archive_service + "/full-index/index.json"

        cleaned_directories = []

        # Make the response.
        directories = requests.get(
            url = url
        ).json()

        # Loop through each item.
        for directory in directories['directory']['item']:

            # Create the URL for the directory.
            if directory['type'] == 'dir':

                directory['yearly_url'] = self.archive_service + "/full-index/{year}/index.json".format(
                    year=directory['name'],
                )

                print('Pulling Directory: {yearly_url}'.format(yearly_url=directory['yearly_url']))
                
                # If we have a year than grab the quarters.
                yearly_content = requests.get(url=directory['yearly_url']).json()

                directory['quarterly_directories'] = {}

                for quarter in yearly_content['directory']['item']:

                    quarterly_url = self.archive_service + "/full-index/{year}/{qtr}/index.json".format(
                        year=directory['name'],
                        qtr=quarter['name']
                    )

                    print('Pulling Directory: {qtr_url}'.format(qtr_url=quarterly_url))

                    directory['quarterly_directories'][quarter['name']] = {}
                    directory['quarterly_directories'][quarter['name']]['url'] = quarterly_url
                    directory['quarterly_directories'][quarter['name']]['items'] = []

                    quarterly_content = requests.get(url=quarterly_url).json()

                    for item in quarterly_content['directory']['item']:
                        item['url'] = quarterly_url + item['href']
                        directory['quarterly_directories'][quarter['name']]['items'].append(item)

            # Create the URL for downloads.
            else:
                directory['file_url'] = self.archive_service + "/full-index/{href}".format(
                    href=directory['href']
                )

            directory['filing_id'] = directory.pop('name')
            directory['last_modified'] = directory.pop('last-modified')

            cleaned_directories.append(directory)

        return cleaned_directories
