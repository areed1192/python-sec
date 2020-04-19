import requests
import xml.etree.ElementTree as ET

# https://www.sec.gov/cgi-bin/srch-edgar?text=form-type%3D%2810-q*+OR+10-k*%29&first=2020&last=2020


class EDGARQuery():

    def __init__(self):

        # base URL for the SEC EDGAR browser
        self.endpoint = r"https://www.sec.gov/cgi-bin/browse-edgar"
        self.browse_service = 'browse-edgar'
        self.search_service = 'srch-edgar'
        self.cik_lookup = 'cik_lookup'
        self.mutal_fund_search = 'series'


        # define our parameters dictionary
        self.query_dict = {
            'action':'getcompany',
            'CIK':'1265107',
            'type':'10-k',
            'dateb':'20190101',
            'owner':'exclude',
            'start':'',
            'output':'',
            'count':'100'
        }

    def query_filing_type(self, filing_type: str) -> list[dict]:
        """[summary]
        
        Arguments:
            filing_type {str} -- [description]
        
        Returns:
            list[dict] -- [description]
        """

        params = {
            'action':'getcompany',
            'type':'10-k'
        }

    def companies_by_state(self, state: str) -> list[dict]:

        # define the endpoint to do filing searches.
        browse_edgar = r"https://www.sec.gov/cgi-bin/browse-edgar"

        # define the arguments of the request
        search_sic_params = {
            'State':state,
            'Count':'100',
            'action':'getcompany',
            'output':'atom'
        }     

    def companies_by_country(self, country: str) -> list[dict]:

        # define the endpoint to do filing searches.
        browse_edgar = r"https://www.sec.gov/cgi-bin/browse-edgar"

        # define the arguments of the request
        search_sic_params = {
            'Country':country,
            'Count':'100',
            'action':'getcompany',
            'output':'atom'
        } 

    def companies_by_sic(self, sic_code: str, state: str = None, country: str = None, after: str = None, before: str = None) -> list[dict]:
        """Grabs all companies with a certain SIC code.

        Returns all companies, that fall under a particular SIC code. The information returned
        by this endpoint depends on the infromation available on the company.

        Arguments:
        ----
            sic_code {str} -- The SIC code for a particular Industry.
    
        Keyword Arguments:
        ----
            state {str} -- A filter which returns companies that are based 
                in a certain state. (default: {None})

            country {str} -- A filter which returns companies that are based
                in a certain country (default: {None})

            after {str} -- Returns filings after a certain date.
                (default: {None})
                
            before {str} -- Returns filings before a certain date. 
                (default: {None})

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

        sic_company_list = []

        parse_dict = {
            r"{http://www.w3.org/2005/Atom}title":'title',
            r"{http://www.w3.org/2005/Atom}updated":'updated',
            r"{http://www.w3.org/2005/Atom}id":'id',
            r"{http://www.w3.org/2005/Atom}cik":'cik',
            r"{http://www.w3.org/2005/Atom}last-date":'last-date',
            r"{http://www.w3.org/2005/Atom}name":'name',
            r"{http://www.w3.org/2005/Atom}sic":'sic-code',
            r"{http://www.w3.org/2005/Atom}state":'state',
            r"{http://www.w3.org/2005/Atom}summary":'summary',
        }

        loop_dict = {
            r"{http://www.w3.org/2005/Atom}link":'loop',
            r"{http://www.w3.org/2005/Atom}summary":'loop',
            r"{http://www.w3.org/2005/Atom}category":'loop'
        }

        # initalize our constants
        next_page = True
        start = '0'

        # define the endpoint to do filing searches.
        browse_edgar = r"https://www.sec.gov/cgi-bin/browse-edgar"

        # define the arguments of the request
        search_sic_params = {
            'company':'',
            'match':'',
            'filenum':'',
            'State':'',
            'Country':'',
            'Count':'100',
            'SIC':sic_code,
            'myowner':'only',
            'action':'getcompany',
            'output':'atom'
        }
        
        # make the request
        sic_type_response = requests.get(url = browse_edgar, params = search_sic_params)

        while next_page:

            # as long as we get a good status code keep pulling the next url
            if sic_type_response.status_code != 200:
                break
            
            # Print the URL
            print("SIC CODE: {} | PULLED COMPANY SIC URL: {}".format(self.sic_code, sic_type_response.url))

            # Try to find the next link.
            next_link = ET.fromstring(sic_type_response.text).findall(r"{http://www.w3.org/2005/Atom}link[@rel='next']")

            # Grab all the Entry elements.
            entry_elements = ET.fromstring(sic_type_response.text).findall(r'{http://www.w3.org/2005/Atom}entry')

            # loop through them.
            for entry_element in entry_elements:

                # create a mini dictionary to store the content.
                entry_dict = {}

                # grab the nested elements.
                for child_element in entry_element.iter():
                   
                    # parse certain ones.
                    if child_element.tag in parse_dict:
                        key = parse_dict[child_element.tag]
                        entry_dict[key] = child_element.text
                    
                    # loop other ones.
                    if child_element.tag in loop_dict:
                        for attrib_k in child_element.attrib:
                            entry_dict[attrib_k] = child_element.attrib[attrib_k]

                entry_dict['atom_owner_only'] = entry_dict['href'].replace('&owner=exclude','&owner=only') + '&output=atom'
                entry_dict['atom_owner_exclude'] = entry_dict['href'] + '&output=atom'
                entry_dict['atom_owner_include'] = entry_dict['href'].replace('&owner=exclude','&owner=include') + '&output=atom'

                entry_dict['html_owner_only'] = entry_dict['href'].replace('&owner=exclude','&owner=only')
                entry_dict['html_owner_exclude'] = entry_dict['href']
                entry_dict['html_owner_include'] = entry_dict['href'].replace('&owner=exclude','&owner=include')

                # Add the filtered query if needed.
                if self.after_date is not None:

                    arg_xml = '&output=atom' + '&datea={date_after}'.format(date_after = self.after_date.isoformat())
                    arg_htm = '&datea={date_after}'.format(date_after = self.after_date.isoformat())

                    entry_dict['atom_owner_only_filtered_date'] = entry_dict['href'].replace('&owner=exclude','&owner=only') + arg_xml
                    entry_dict['atom_owner_exclude_filtered_date'] = entry_dict['href'] + arg_xml
                    entry_dict['atom_owner_include_filtered_date'] = entry_dict['href'].replace('&owner=exclude','&owner=include') + arg_xml

                    entry_dict['html_owner_only_filtered_date'] = entry_dict['href'].replace('&owner=exclude','&owner=only') + arg_htm
                    entry_dict['html_owner_exclude_filtered_date'] = entry_dict['href'] + arg_htm
                    entry_dict['html_owner_include_filtered_date'] = entry_dict['href'].replace('&owner=exclude','&owner=include') + arg_htm

                # store in master list.
                sic_company_list.append(entry_dict)
           
            if next_link:
                next_url = next_link[0].attrib['href']

                if self.after_date is not None:
                    next_url = next_url + '&datea={date_after}'.format(date_after = self.after_date.isoformat())

                sic_type_response = requests.get(url = next_url)
            else:
                next_page = False

        print('')
        print('='*80)
        print('')

        return sic_company_list

    def ownership_filings_by_cik(self, cik: str, before: str = None, after: str = None) -> list[dict]:
        
        # define the endpoint to do filing searches.
        browse_edgar = r"https://www.sec.gov/cgi-bin/browse-edgar"

        # define the arguments of the request
        search_params = {
            'CIK':cik,
            'Count':'100',
            'myowner':'only',
            'action':'getcompany',
            'output':'atom',
            'datea':after,
            'dateb':before
        }
    
    def non_ownership_filings_by_cik(self, cik: str, before: str = None, after: str = None) -> list[dict]:
        
        # define the endpoint to do filing searches.
        browse_edgar = r"https://www.sec.gov/cgi-bin/browse-edgar"

        # define the arguments of the request
        search_params = {
            'CIK':cik,
            'Count':'100',
            'myowner':'exclude',
            'action':'getcompany',
            'output':'atom',
            'datea':after,
            'dateb':before
        }

    def all_filings_by_cik(self, cik: str, before: str = None, after: str = None) -> list[dict]:
        
        # define the endpoint to do filing searches.
        browse_edgar = r"https://www.sec.gov/cgi-bin/browse-edgar"

        # define the arguments of the request
        search_params = {
            'CIK':cik,
            'Count':'100',
            'myowner':'include',
            'action':'getcompany',
            'output':'atom',
            'datea':after,
            'dateb':before
        }

    def ownership_filings_by_company_name(self, company_name: str, before: str = None, after: str = None) -> list[dict]:
        
        # define the endpoint to do filing searches.
        browse_edgar = r"https://www.sec.gov/cgi-bin/browse-edgar"

        # define the arguments of the request
        search_params = {
            'CIK':company_name,
            'Count':'100',
            'myowner':'only',
            'action':'getcompany',
            'output':'atom',
            'datea':after,
            'dateb':before
        }
    
    def non_ownership_filings_by_company_name(self, company_name: str, before: str = None, after: str = None) -> list[dict]:
        
        # define the endpoint to do filing searches.
        browse_edgar = r"https://www.sec.gov/cgi-bin/browse-edgar"

        # define the arguments of the request
        search_params = {
            'CIK':company_name,
            'Count':'100',
            'myowner':'exclude',
            'action':'getcompany',
            'output':'atom',
            'datea':after,
            'dateb':before
        }

    def all_filings_by_company_name(self, company_name: str, before: str = None, after: str = None) -> list[dict]:
        
        # define the endpoint to do filing searches.
        browse_edgar = r"https://www.sec.gov/cgi-bin/browse-edgar"

        # define the arguments of the request
        search_params = {
            'company':company_name,
            'Count':'100',
            'myowner':'include',
            'action':'getcompany',
            'output':'atom',
            'datea':after,
            'dateb':before
        }