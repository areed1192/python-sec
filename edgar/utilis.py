
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
                directory['name'] = "/" +directory['name']

            # Create the URL.
            directory['url'] = (self.resource + directory_name +  directory['name'] + "/index.json").replace('//','/')
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
                
            file['url'] = (self.resource + directory_name + file['name']).replace("//","/")
            file['filing_id'] = file.pop('name')
            file['last_modified'] = file.pop('last-modified')
            files_cleaned.append(file)

        return files_cleaned
