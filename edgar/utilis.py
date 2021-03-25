from datetime import datetime
from datetime import date

from typing import Union


class EdgarUtilities():

    """
    Overview:
    ----
    Offers different utilities to help standardize filings
    and even parse the content.
    """

    def __init__(self) -> None:
        """Initializes the `EdgarUtilities` object."""
        self.resource = 'https://www.sec.gov'

    def clean_directories(self, directories: list, service_url: str, cik: str = None) -> dict:
        """Used to clean the directories and add additional fields.

        ### Parameters
        ----
        directories : list
            A list of `CompanyDirectory` resources.

        cik : str
            The CIK number associated with the request.

        service_url : str
            The service URL requested.

        ### Returns
        ----
        dict
            A collection of `CompanyDirectory` resources that
            have been cleaned.
        """

        directories_cleaned = []
        directory_name = directories['directory']['name']

        # Loop through each item.
        for directory in directories['directory']['item']:

            if cik:
                directory['cik'] = cik

            if '/' not in directory['name']:
                directory['name'] = "/" + directory['name']

            # Create the URL.
            directory['url'] = (
                self.resource + directory_name +
                directory['name'] + "/index.json"
            ).replace('//', '/')
            directory['filing_id'] = directory.pop('name')
            directory['last_modified'] = directory.pop('last-modified')
            directories_cleaned.append(directory)

        return directories_cleaned

    def clean_filing_directory(self, directory: list, cik: str = None) -> dict:
        """Used to clean the directories and add additional fields.

        ### Parameters
        ----
        directories : list
            A list of `CompanyDirectory` resources.

        cik : str
            The CIK number associated with the request.

        ### Returns
        ----
        dict
            A collection of `CompanyDirectory` resources that
            have been cleaned.
        """

        files_cleaned = []
        directory_name = directory['directory']['name']

        # Loop through each item.
        for file in directory['directory']['item']:

            if cik:
                file['cik'] = cik

            if '/' not in file['name']:
                file['name'] = "/" + file['name']

            file['url'] = (self.resource + directory_name +
                           file['name']).replace("//", "/")
            file['filing_id'] = file.pop('name')
            file['last_modified'] = file.pop('last-modified')
            files_cleaned.append(file)

        return files_cleaned

    def parse_dates(self, date_or_datetime: Union[date, datetime, str]) -> str:
        """Parses the date or datetime object to the correct format. For
        strings, it will validate if it's the correct format.

        ### Parameters
        ----
        date_or_datetime : Union[date, datetime, str]
            The date you want to parse or check.

        ### Returns
        ----
        str
            An ISO Formatted String (`YYYY-MM-DD`).

        ### Raises
        ------
        ValueError
            If the date does not match an ISO-Format it will raise an error.
            Also, if the object isn't a `date`, `datetime`, or `str` it will
            raise an error.

        """

        if isinstance(date_or_datetime, date) or isinstance(date_or_datetime, datetime):
            return date_or_datetime.isoformat()
        elif isinstance(date_or_datetime, str):
            try:
                datetime.strptime(date_or_datetime, '%Y-%m-%d')
                return date_or_datetime
            except:
                raise ValueError(
                    "Date is not the correct format, must be ISO-Format."
                )
        else:
            raise ValueError(
                "Must pass through date, datetime, or date string."
            )
