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
                'filing_id': '000126510720000016',
                'last_modified': '2020-05-06 16:24:37',
                'size': '',
                'type': 'folder.gif',
                'url': 'https://www.sec.gov/Archives/edgar/data/1265107/000126510720000016/index.json'
            }
        ]

        company_directories = self.edgar.company_directories(
            cik=self.cik_number)

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

        company_directory = self.edgar.company_directory(
            cik=self.cik_number, filing_id="000110465919038688")

        self.assertIsInstance(company_directory, list)
        self.assertDictEqual(company_directory[0], directory_match[0])

    def test_grab_filing_by_type(self):
        """Test grabbing a specific filing type for a particular company."""

        filing_types_match = [
            {   
                'accession-nunber': '0001265107-20-000007',
                'act': '34',
                'category_label': 'form type',
                'category_scheme': 'https://www.sec.gov/',
                'category_term': '10-K',
                'content': '',
                'content_type': 'text/xml',
                'file-number': '333-110025',
                'file-number-href': 'https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&filenum=333-110025&owner=include&count=40',
                'filing-date': '2020-03-30',
                'filing-href': 'https://www.sec.gov/Archives/edgar/data/1265107/000126510720000007/0001265107-20-000007-index.htm',
                'filing-type': '10-K',
                'film-number': '20755403',
                'form-name': 'Annual report [Section 13 and 15(d), not S-K Item 405]',
                'id': 'urn:tag:sec.gov,2008:accession-number=0001265107-20-000007',
                'size': '12 MB',
                'link_href': 'https://www.sec.gov/Archives/edgar/data/1265107/000126510720000007/0001265107-20-000007-index.htm',
                'link_rel': 'alternate',
                'link_type': 'text/html',
                'summary': '<b>Filed:</b> 2020-03-30 <b>AccNo:</b> 0001265107-20-000007 '
                            '<b>Size:</b> 12 MB',
                'summary_type': 'html',
                'title': '10-K  - Annual report [Section 13 and 15(d), not S-K Item 405]',
                'updated': '2020-03-30T12:24:51-04:00',
                'xbrl_href': 'https://www.sec.gov/cgi-bin/viewer?action=view&cik=1265107&accession_number=0001265107-20-000007&xbrl_type=v'
            }
        ]

        facebook_10ks = self.edgar.company_filings_by_type(cik=self.cik_number, filing_type='10-K')

        self.assertIsInstance(facebook_10ks, list)
        self.assertDictEqual(facebook_10ks[0], filing_types_match[0])

    def test_grab_cik_ownership_filings(self):

        match = [
            {
                'accession-nunber': '0000950103-20-003878',
                'category_label': 'form type',
                'category_scheme': 'https://www.sec.gov/',
                'category_term': '4',
                'content': '',
                'content_type': 'text/xml',
                'filing-date': '2020-02-28',
                'filing-href': 'https://www.sec.gov/Archives/edgar/data/1326801/000095010320003878/0000950103-20-003878-index.htm',
                'filing-type': '4',
                'form-name': 'Statement of changes in beneficial ownership of securities',
                'id': 'urn:tag:sec.gov,2008:accession-number=0000950103-20-003878',
                'link_href': 'https://www.sec.gov/Archives/edgar/data/1326801/000095010320003878/0000950103-20-003878-index.htm',
                'link_rel': 'alternate',
                'link_type': 'text/html',
                'size': '5 KB',
                'summary': '<b>Filed:</b> 2020-02-28 <b>AccNo:</b> 0000950103-20-003878 '
                '<b>Size:</b> 5 KB',
                'summary_type': 'html',
                'title': '4  - Statement of changes in beneficial ownership of securities',
                'updated': '2020-02-28T20:19:46-05:00'
            }
        ]

        facebook_ownership = self.edgar.ownership_filings_by_cik(cik='1326801', before="20200301", after="20200101")

        self.assertIsInstance(facebook_ownership, list)
        self.assertDictEqual(facebook_ownership[0], match[0])

    def tearDown(self) -> None:
        """Teardown the Robot."""

        self.robot = None


if __name__ == '__main__':
    unittest.main()
