import re
import xml.etree.ElementTree as ET
import requests

from pprint import pprint
from typing import List
from typing import Dict
from typing import Union

from html.parser import HTMLParser
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup
from bs4 import Tag

class EDGARParser():

    def __init__(self):
        """Initalizes the `EDGARParser()` Object.

        Parsing filings, can change depending on the filing you're working with
        and whether you're grabbing the raw filing text or the directory of the filings.
        Regardless of what you're parsing, the `EDGARParser()` object will handle most of
        the finer details for you.

        In cases, where the user needs to parse RSS feeds for the company search, then the
        parser will grab all the XML content and convert it to a Python dictionary. Additionally,
        it will grab all the next pages and parse thoses if specified.
        """

        self.entries_namespace = {
            'atom': "http://www.w3.org/2005/Atom",
            'atom_with_quote':'{http://www.w3.org/2005/Atom}'
        }

        self.retry_strategy = Retry(
            total=3,
            backoff_factor=0.2,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        self.adapter = HTTPAdapter(max_retries=self.retry_strategy)

    def parse_entries(self, entries_text: str, num_of_items: int = None) -> List[Dict]:
        """Parses all the entries from an entry element list.

        Arguments:
        ----
        entries_text {str} -- The raw string returned from the
            response.

        Returns:
        ----
        List[Dict] -- A dictionary containing all the information from the
            original entry element.
        """        

        # Parse the text.
        root = ET.fromstring(entries_text)
        entries = []
        keep_going = True

        while keep_going:

            # Check for the next page Link, if there is one.
            next_page = self._check_for_next_page(root_document=root)

            if next_page:
                current_count = int(next_page.split('&start=')[1])

            # Find all the entries.
            for entry in root.findall('atom:entry', namespaces=self.entries_namespace):
                
                # Parse the individual entry.
                entry_dict = self.parse_entry_element(entry=entry)
                entries.append(entry_dict)

            # If there is a next page continue.
            if not next_page:
                keep_going = False
            else:
                root = self._grab_next_page(next_url=next_page)
                print('Grabbed Next URL: {url}'.format(url=next_page))
                
                if not root or (num_of_items and num_of_items < current_count):
                    keep_going = False

        return entries
    
    def _grab_next_page(self, next_url: str) -> ET.ElementTree:
        """Grabs the next page text content.

        Grabbing mutliple pages can be challenging because in some
        cases the SEC will kick you back if you make too many requests
        at once and don't pause enough. This method will help control that
        by defining a retry strategy and backing off for an allotted time
        in the case of a failed request.

        Arguments:
        ----
        next_url {str} -- URL redirecting to the next rounds of files.

        Returns:
        ----
        ET.ElementTree -- A parsed version of the RSS Feed.
        """

        # Create a new session.
        http = requests.Session()

        # Set the retry strategy.
        http.mount("https://", self.adapter)

        # Make the request.
        try:
            entries_response = http.get(url=next_url)
        except:
            return None

        # If it was successful, get the data.
        if entries_response.status_code == 200:
            root = ET.fromstring(entries_response.content)
            return root
        else:
            return None

    def parse_entry_element(self, entry: ET.ElementTree) -> dict:
        """Converts the XML entry element into a python dictionary.

        Arguments:
        ----
        entry {ET.ElementTree} -- An entry element, that contains filing information.

        Returns:
        ----
        dict -- A dictionary version of the entry element.
        """        

        entry_element_dict = {}
        replace_tag = self.entries_namespace['atom_with_quote']

        for entry in entry.findall("./", namespaces=self.entries_namespace):
            for element in entry.iter():
                name = element.tag.replace(replace_tag, '')
                
                if element.text :
                    entry_element_dict[name] = element.text.strip()
                # else:
                #     entry_element_dict[name] = ""

                if element.attrib:
                    for key, value in element.attrib.items():
                        entry_element_dict[name + "_{}".format(key)] = value

        return entry_element_dict

    def _check_for_next_page(self, root_document: ET.Element) -> Union[str, None]:
        """Checks if the RSS Feed has a next page.

        Arguments:
        ----
        root_document {ET.Element} -- The Parsed root document, which contains entry
            elements.

        Returns:
        ----
        Union[str, None] -- The URL if it was found otherwise nothing.
        """        

        next_page = root_document.findall("atom:link[@rel='next']", namespaces=self.entries_namespace)

        if next_page:
            element_attributes = next_page[0].attrib
        else:
            return None

        if 'href' in element_attributes:
            next_page_url = element_attributes['href']
        else:
            return None

        return next_page_url

    def _parse_issuer_next_button(self, button_soup: Tag) -> Union[str]:
        """Parses the next button in the issuer report.

        Args:
        ----
        button_soup (Tag): The raw HTML of the page with the button included.

        Returns:
        ----
        Union[str]: The link to the next page or nothing.
        """        
        
        # Grab the button.
        buttons: Tag = button_soup.find_all(
            name='input',
            attrs={'type': 'button'}
        )

        # Loop through each of the buttons.
        for button in buttons:

            # If there is a next button, grab the link.
            if 'Next' in button['value']:
                next_page = button['onclick']

                # Build the URL
                next_page_link = next_page.replace("parent.location='","https://www.sec.gov").replace("'","")

                return next_page_link

    def parse_issuer_table(self, entries_text: str, num_of_items: int = None) -> List[Dict]:
        """Parses the Issuer tables found from a query to owner distribtuion page.

        Arguments:
        ----
        entries_text (str): The raw HTML content to be parsed.

        num_of_items (int, optional): The number of items to return from the query. Defaults to None.

        Returns:
        ----
        List[Dict]: A list of dictionaries where each dictionary contains the `ownership_report`
            and the `ownership_transaction_report`.
        """        

        master_list = []
        ownership_report_for_issuers = []

        soup = BeautifulSoup(entries_text, 'html.parser')
        next_page_link = self._parse_issuer_next_button(button_soup=soup)

        while soup is not None:

            table_rows = soup.find_all(name='tr')
            table = soup.find_all(name='table')

            issuers_table: Tag = table[4]
            issuers_transaction_report_table: Tag = soup.find_all(name='table', attrs={'id':'transaction-report'})

            issuers_table_rows = issuers_table.find_all(name='tr')
            
            for row in issuers_table_rows:

                issuer_dict = {}

                row: Tag = row
                elements = row.text.split('\n')
                links = row.find_all('a', href=True)

                issuer_dict = {
                    'issuer': elements[0],
                    'filings': elements[1],
                    'transaction_date': elements[2],
                    'type_of_owner': elements[3]
                }

                ownership_report_for_issuers.append(issuer_dict)

                for link in links:
                    new_link = 'https://www.sec.gov' + link['href']

                    if 'own-disp' in new_link:
                        issuer_dict['ownership_link'] = new_link
                    elif 'browse-edgar' in new_link:
                        issuer_dict['browse_company_link'] = new_link       
            
            master_dict = {}
            master_dict['ownership_report'] = ownership_report_for_issuers
            master_dict['ownership_transaction_report'] = self.parse_transaction_report(table=issuers_transaction_report_table[0])
            master_list.append(master_dict)

            print(next_page_link)
            
            if next_page_link:
                entries_text = requests.get(next_page_link).content
                soup = BeautifulSoup(entries_text, 'html.parser')
                next_page_link = self._parse_issuer_next_button(button_soup=soup)
            else:
                soup = None

        return master_list

    def parse_transaction_report(self, table: Tag) -> List[Dict]:
        """Parse the transaction table report.

        Args:
        ----
        table (Tag): The raw HTML table.

        Returns:
        ----
        List[Dict]: A list of ownership transaction reports.
        """        

        master_list = []
        
        all_rows = table.find_all('tr')
        first_row = all_rows[0]
        all_other_rows = all_rows[1:]

        headers = [header.replace(' ', '_').lower() for header in first_row.strings if header != '\n']

        headers.insert(5, 'link')

        for row in all_other_rows:

            link = row.find_all('a')[0]
            href = 'https://www.sec.gov' + link['href']

            values = [value.strip() for value in row.strings if value != '\n']
            values.insert(5, href)

            master_list.append(dict(zip(headers, values)))
            # print([header.strip() for header in row.strings if header != '\n'])

        return master_list

        

        

