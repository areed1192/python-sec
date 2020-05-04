import xml.etree.ElementTree as ET
import requests

from typing import List
from typing import Dict
from typing import Union

from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

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
                # print(name)
                # print(element.tag)
                # print(element.attrib)
                
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

        

