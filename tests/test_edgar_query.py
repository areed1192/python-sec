"""Unit test module for the Azure Session.

Will perform an instanc test to make sure it creates it.
"""

import unittest
from unittest import TestCase
from pysec.edgar import EDGARQuery
from typing import List

class PyRobotSession(TestCase):

    """Will perform a unit test for the Azure session."""

    maxDiff = None

    def setUp(self) -> None:
        """Set up the Robot."""

        self.edgar = EDGARQuery()

        # This is Facebook.
        self.cik_number = '1265107'

    def test_creates_instance_of_session(self):
        """Create an instance and make sure it's a robot."""

        self.assertIsInstance(self.edgar, EDGARQuery)

    def test_grab_company_directories(self):
        """Test pulling the directories for a particular CIK number."""

        directories_match = [
            {
                'filing_id': '000126510720000011',
                'last_modified': '2020-04-09 17:07:11',
                'size': '',
                'type': 'folder.gif',
                'url': 'https://www.sec.gov/Archives/edgar/data/1265107/000126510720000011/index.json'
            }
        ]

        company_directories = self.edgar.company_directories(cik=self.cik_number)

        self.assertIsInstance(company_directories[:2], list)
        self.assertDictEqual(company_directories[0], directories_match[0])

    def test_grab_company_directory(self):
        """Test grabbing a single filing for a particular CIK number."""

        directory_match = [
            {
                'item_id': '0001104659-19-038688-index-headers.html',
                'last_modified': '2019-07-01 17:17:26',
                'size': '',
                'type': 'text.gif',
                'url': 'https://www.sec.gov/Archives/edgar/data/1265107/000110465919038688/0001104659-19-038688-index-headers.html'
            }
        ]

        company_directory = self.edgar.company_directory(cik=self.cik_number, filing_id="000110465919038688")

        self.assertIsInstance(company_directory, list)
        self.assertDictEqual(company_directory[0], directory_match[0])
    
    def test_grab_filing_by_type(self):
        """Test grabbing a specific filing type for a particular company."""

        filing_types_match = [
            {
                'category': '',
                'category_label': 'form type',
                'category_scheme': 'https://www.sec.gov/',
                'category_term': '10-K',
                'content': '',
                'content_type': 'text/xml',
                'id': 'urn:tag:sec.gov,2008:accession-number=0001265107-20-000007',
                'link': '',
                'link_href': 'https://www.sec.gov/Archives/edgar/data/1265107/000126510720000007/0001265107-20-000007-index.htm',
                'link_rel': 'alternate',
                'link_type': 'text/html',
                'summary': '<b>Filed:</b> 2020-03-30 <b>AccNo:</b> 0001265107-20-000007 '
                            '<b>Size:</b> 12 MB',
                'summary_type': 'html',
                'title': '10-K  - Annual report [Section 13 and 15(d), not S-K Item 405]',
                'updated': '2020-03-30T12:24:51-04:00'
            }
        ]

        facebook_10ks = self.edgar.company_filings_by_type(cik=self.cik_number, filing_type='10-K')

        self.assertIsInstance(facebook_10ks, list)
        self.assertDictEqual(facebook_10ks[0], filing_types_match[0])


    def tearDown(self) -> None:
        """Teardown the Robot."""

        self.robot = None


if __name__ == '__main__':
    unittest.main()