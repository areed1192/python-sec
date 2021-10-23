import xml.etree.ElementTree as ET

from typing import List
from typing import Dict
from typing import Union

import requests

from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup
from bs4 import Tag


class EdgarParser():

    """
    ## Overview:
    ----
    Handles all the parsing operations of the library
    and will reorganize data into more structured formats.
    """

    def __init__(self):
        """Initalizes the `EdgarParser` Object.

        Parsing filings, can change depending on the filing you're working with
        and whether you're grabbing the raw filing text or the directory of the filings.
        Regardless of what you're parsing, the `EdgarParser` object will handle most of
        the finer details for you.

        In cases, where the user needs to parse RSS feeds for the company search, then the
        parser will grab all the XML content and convert it to a Python dictionary. Additionally,
        it will grab all the next pages and parse thoses if specified.
        """

        self.entries_namespace = {
            'atom': "http://www.w3.org/2005/Atom",
            'atom_with_quote': '{http://www.w3.org/2005/Atom}',
            '': ''
        }

        self.retry_strategy = Retry(
            total=3,
            backoff_factor=0.2,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        self.adapter = HTTPAdapter(max_retries=self.retry_strategy)

    def parse_entries(
        self,
        response_text: str,
        num_of_items: int = None,
        start: int = None,
        path: str = 'atom:entry'
    ) -> List[Dict]:
        """Parses all the entries from an entry element list.

        ### Parameters
        ----
        response_text : str
            The raw string returned from the response.

        ### Returns
        ----
        List[Dict] :
            A dictionary containing all the information from the
            original entry element.
        """

        # Parse the text.
        root = ET.fromstring(response_text)
        entries = []
        keep_going = True

        if start:
            current_count = start
        else:
            current_count = 0

        while keep_going:

            # Check for the next page Link, if there is one.
            next_page = self._check_for_next_page(root_document=root)

            # Grab the next page.
            if next_page and start:
                current_count = (int(next_page.split('&start=')[1]) - start)
            elif next_page:
                current_count = int(next_page.split('&start=')[1])

            # Find all the entries.
            for entry in root.findall(path=path, namespaces=self.entries_namespace):

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

        ### Parameters
        ----
        next_url : str
            URL redirecting to the next rounds of files.

        ### Returns
        ----
        ET.ElementTree :
            A parsed version of the RSS Feed.
        """

        # Create a new session.
        http = requests.Session()

        # Set the retry strategy.
        http.mount("https://", self.adapter)

        # Make the request.
        try:
            entries_response = http.get(url=next_url)
        except requests.exceptions.HTTPError:
            return None

        # If it was successful, get the data.
        if entries_response.status_code == 200:
            root = ET.fromstring(entries_response.content)
            return root
        else:
            return None

    def parse_entry_element(self, entry: ET.ElementTree, path: str = './') -> dict:
        """Converts the XML entry element into a python dictionary.

        ### Parameters
        ----
        entry : ET.ElementTree
            An entry element, that contains filing information.

        ### Returns
        ----
        dict :
            A dictionary version of the entry element.
        """

        entry_element_dict = {}
        replace_tag = self.entries_namespace['atom_with_quote']

        for entry in entry.findall(path=path, namespaces=self.entries_namespace):

            for element in entry.iter():
                name = element.tag.replace(replace_tag, '')

                if element.text:
                    name = name.replace('-', '_')
                    entry_element_dict[name] = element.text.strip()

                if element.attrib:
                    for key, value in element.attrib.items():
                        key = key.replace('-', '_')
                        entry_element_dict[name + "_{}".format(key)] = value

        return entry_element_dict

    def _check_for_next_page(self, root_document: ET.Element) -> Union[str, None]:
        """Checks if the RSS Feed has a next page.

        ### Parameters
        ----
        root_document : ET.Element
            The Parsed root document, which contains entry elements.

        ### Returns
        ----
        Union[str, None]:
            The URL if it was found otherwise nothing.
        """

        next_page = root_document.findall(
            "atom:link[@rel='next']", namespaces=self.entries_namespace)

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

        ### Parameters
        ----
        button_soup : Tag
            The raw HTML of the page with the button included.

        ### Returns
        ----
        Union[str]:
            The link to the next page or nothing.
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
                next_page_link = next_page.replace(
                    "parent.location='", "https://www.sec.gov").replace("'", "")

                return next_page_link

    def parse_issuer_table(self, response_text: str) -> List[Dict]:
        """Parses the Issuer tables found from a query to owner distribtuion page.

        ### Parameters
        ----
        response_text : str
            The raw HTML content to be parsed.

        num_of_items : int (optional, Default=None):
            The number of items to return from the query.

        ### Returns
        ----
        List[Dict]:
            A list of dictionaries where each dictionary contains
            the `ownership_report` and the `ownership_transaction_report`.
        """

        master_list = []
        ownership_report_for_issuers = []

        soup = BeautifulSoup(response_text, 'html.parser')
        next_page_link = self._parse_issuer_next_button(button_soup=soup)

        while soup is not None:

            # table_rows = soup.find_all(name='tr')
            table = soup.find_all(name='table')

            issuers_table: Tag = table[4]
            issuers_transaction_report_table: Tag = soup.find_all(
                name='table',
                attrs={
                    'id': 'transaction-report'
                }
            )
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
            master_dict['ownership_transaction_report'] = self.parse_transaction_report(
                table=issuers_transaction_report_table[0]
            )

            master_list.append(master_dict)

            print("Pulling URL: {url}".format(url=next_page_link))

            if next_page_link:
                response_text = requests.get(next_page_link).content
                soup = BeautifulSoup(response_text, 'html.parser')
                next_page_link = self._parse_issuer_next_button(
                    button_soup=soup)
            else:
                soup = None

        return master_list

    def parse_transaction_report(self, table: Tag) -> List[Dict]:
        """Parse the transaction table report.

        ### Parameters
        ----
        table : Tag
            The raw HTML table.

        ### Returns
        ----
        List[Dict] :
            A list of ownership transaction reports.
        """

        master_list = []

        all_rows = table.find_all('tr')
        first_row = all_rows[0]
        all_other_rows = all_rows[1:]

        headers = [header.replace(' ', '_').lower()
                   for header in first_row.strings if header != '\n']

        headers.insert(5, 'link')

        for row in all_other_rows:

            link = row.find_all('a')[0]
            href = 'https://www.sec.gov' + link['href']

            values = [value.strip() for value in row.strings if value != '\n']
            values.insert(5, href)

            master_list.append(dict(zip(headers, values)))
            # print([header.strip() for header in row.strings if header != '\n'])

        return master_list

    def _check_center_tag(self, product_table_soup: Tag) -> Union[List[str]]:
        """Grabs all the links that are in the Center tag of the Product Page.

        ### Parameters
        ----
        product_table_soup : Tag
            The product page HTML that has been parsed.

        ### Returns
        ----
        Union[List[str]] :
            A list of URL links to the other pages.
        """

        links = []

        # Find the <center> tag.
        center_tag: Tag = product_table_soup.find(name='center')

        # Grab the <A> tags.
        center_tag_hrefs = center_tag.find_all('a', href=True)

        # We need to clean up the links, cause they're broken.
        for href in center_tag_hrefs:

            # Split by the ampersand.
            split_href: list = href['href'].split('&')

            # Remove the CIK parameters.
            split_href.pop(1)

            # and add a clean one.
            split_href.insert(1, 'CIK=')

            # Create a new URL.
            links.append('https://www.sec.gov' + '&'.join(split_href))

        # Don't care about the last one, just a duplicate.
        return links[:-1]

    def parse_variable_products_company_table(self, response_text: str) -> List[Dict]:
        """Parses the Variable Product page of all the different products and companies.

        ### Parameters
        ----
        response_text : str
            The raw HTML of the Product query result page.

        ### Returns
        ----
        List[Dict] :
            A list of variable products.
        """
        # Parse the Page.
        product_page_soup = BeautifulSoup(response_text, 'html.parser')

        # Check for the other links.
        href_links = self._check_center_tag(
            product_table_soup=product_page_soup)

        # Parse the table.
        product_list_all = self._parse_variable_product_page(
            product_page_soup=product_page_soup)

        # Loop through all the pages, and grab those entries.
        for link in href_links:

            product_page_soup = BeautifulSoup(
                requests.get(url=link).text, 'html.parser')
            product_list = self._parse_variable_product_page(
                product_page_soup=product_page_soup)
            product_list_all = product_list_all + product_list

            print("Pulling URL: {url}".format(url=link))
            print("Total Entries Scraped: {quant}".format(
                quant=len(product_list_all)))

        return product_list_all

    def _parse_variable_product_page(self, product_page_soup: Tag) -> List[Dict]:
        """This parses the actual table. It will grab the table with the entires and parse each row.

        ### Parameters
        ----
        product_page_soup :Tag
            The parsed page with product tables.

        ### Returns
        ----
        List[Dict] :
            A list of variable products.
        """

        # Grab all the Summary Tables.
        summary_table = product_page_soup.find_all(
            name='table', attrs={'summary': '.'})

        master_list = []

        # Loop through each table.
        for table in summary_table:

            table: Tag = table

            # Define a matching table.
            criteria_1 = len(table.attrs) == 1
            criteria_2 = table.attrs['summary'] == '.'
            criteria_3 = len(table.find_all('input')) == 0

            if criteria_1 and criteria_2 and criteria_3:

                # Grab all the Rows.
                table_rows: List[Tag] = table.find_all(
                    'tr', attrs={'valign': 'top'}
                )

                # Loop through each Row.
                for row in table_rows:

                    # Grab Row links
                    row_links = [
                        row_link['href']
                        for row_link in row.find_all('a', href=True)
                    ]

                    # Grab the Strings, with text and filter our line breaks.
                    values = [
                        string for string in row.strings if string != '\n'
                    ]

                    if values:

                        # Create the dictionary & store the values.
                        row_dict = {}
                        product_id: str = values[0]
                        product_name: str = values[1]

                        row_dict['id'] = product_id
                        row_dict['name'] = product_name

                        # Define the product ID based on the first Character.
                        if product_id.startswith('S'):
                            row_dict['id_type'] = 'Series'
                        elif product_id.startswith('C'):
                            row_dict['id_type'] = 'Contract'
                        else:
                            row_dict['id_type'] = 'CIK'

                        # Set the Ticker symbol.
                        try:
                            row_dict['ticker_symbol'] = values[2]
                        except KeyError:
                            row_dict['ticker_symbol'] = "null"

                        for link in row_links:

                            if '&scd' in link:
                                row_dict['series_link'] = 'https://www.sec.gov' + link
                            elif 'getcompany' in link and row_dict['id_type'] == 'Contract':
                                row_dict['contract_id_link'] = 'https://www.sec.gov' + link
                            elif 'getcompany' in link and row_dict['id_type'] == 'Series':
                                row_dict['series_id_link'] = 'https://www.sec.gov' + link
                            else:
                                row_dict['cik_id_link'] = 'https://www.sec.gov' + link

                        master_list.append(row_dict)

        return master_list

    def parse_current_event_table(self, response_text: str) -> List[Dict]:
        """Parses the Current Event page of all the forms.

        ### Parameters
        ----
        response_text : str
            The raw HTML of the current event query page.

        ### Returns
        ----
        List[Dict] :
            A list of SEC filings.
        """

        master_list = []

        # Parse the Page.
        current_event_soup = BeautifulSoup(response_text, 'html.parser')

        # Grab the <Pre> tag.
        current_event_pre: Tag = current_event_soup.find('pre')

        # In this case, split along Line breaks.
        all_rows = current_event_pre.text.splitlines()

        # Define the headers
        keys = ['date_filed', 'form', 'cik', 'company_name']

        # Clean up the header to get the first row.
        header_row = all_rows[0].replace(
            'Date Filed   Form        CIK Code     Company Name',
            ''
        )

        new_string = " ".join(header_row.split()).split(' ', 3)

        # add to the list.
        master_list.append(dict(zip(keys, new_string)))

        # Clean up the rest of the rows.
        for row in all_rows[1:]:
            new_string = " ".join(row.split()).split(' ', 3)
            master_list.append(dict(zip(keys, new_string)))

        return master_list

    def parse_loc_elements(self, response_text: str) -> List[dict]:
        """Parses the `Loc` elements found in the Taxonomies XML content.

        ### Parameters
        ----
        response_text : str
            The raw XML of the Taxonomy query.

        ### Returns
        ----
        List[Dict] :
            A list of taxonomy objects.
        """

        # Parse the text.
        root = ET.fromstring(response_text)
        entries = []

        # Grab all the location elements.
        for location in root.findall('Loc'):
            location_dict = {
                element.tag: element.text for element in location.iter()
            }
            del location_dict['Loc']
            entries.append(location_dict)

        return entries

    # def parse_series_filings(self, response_text: str) -> List[dict]:

    #     root = ET.fromstring(response_text)

    #     for elem in root.iterfind(
    #         '.atom:entry/atom:content/atom:company-info/atom:sids/atom:sid',
    #         namespaces=self.entries_namespace
    #     ):
    #         print(elem)

        # soup = BeautifulSoup(response_text, 'html.parser')

        # sid_data = []

        # for sid in soup.find_all(name='sid'):

        #     sid: Tag = sid
        #     element_dict = {}

        #     print(len(list(sid.children)))

        #     for element in sid.children:

        #         if not isinstance(element, NavigableString) and element.name != 'cids':
        #             element_dict[
        #                 element.name.replace('-', '_')
        #             ] = element.text.strip()

        #         elif not isinstance(element, NavigableString) and element.name == 'cids':
        #             element_dict['cids'] = []

        #             for cid in element.find_all('cid'):
        #                 cid_dict = {}
        #                 cid_dict['cid_id'] = cid['id']

        #                 for cid_element in cid.find_all():
        #                     cid_dict[
        #                         cid_element.name.replace('-', '_').strip()
        #                     ] = cid_element.text.strip()

        #                 element_dict['cids'].append(
        #                     cid_dict
        #                 )

        #     sid_data.append(
        #         element_dict
        #     )

        # return sid_data

    def parse_series_table(self, response_text: str) -> List[Dict]:
        """Parses the series table returned from a Series query.

        ### Parameters
        ----
        response_text : str
            The raw HTML of the Product query result page.

        ### Returns
        ----
        List[Dict] :
            A list of variable products.
        """
        # Parse the Page.
        series_page_soup = BeautifulSoup(response_text, 'html.parser')
        series_table: Tag = series_page_soup.find_all(name='table')[5]

        # Find all the rows.
        series_table_rows = series_table.find_all(
            name='tr',
            attrs={'valign': 'top', 'align': 'left'}
        )

        records = []

        for row in series_table_rows:

            # Grab all the table elements.
            row: Tag = row
            row_elements = row.find_all('td')
            series_record = {}

            for row_element in row_elements:
                row_element: Tag = row_element

                # Most of the time this will capture the CIK number.
                if row_element.find(name='a'):
                    series_record['cik'] = row_element.a.text.strip()
                    series_record['link'] = 'https://www.sec.gov' + \
                        row_element.a['href']

                # this will capture the company name.
                elif row_element.text.strip() != '':
                    series_record['company'] = row_element.text.strip()

            # edge case, the first record is incorrect, but it just involves swapping
            # out the company and the cik.
            if 'company' not in series_record:
                series_record['company'] = series_record['cik']
                series_record['cik'] = series_record['link'].split('CIK=')[
                    1].split('&')[0]

            records.append(series_record)

        return records
