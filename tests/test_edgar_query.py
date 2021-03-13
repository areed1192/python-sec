"""Unit test module for the EDGAR Session.

Will perform an instance test to make sure it creates it.
"""

import unittest
import requests

from typing import List
from unittest import TestCase
from pysec.edgar import EDGARQuery


class EDGARSessionTest(TestCase):

    """Will perform a unit test for the `EDGARQuery` session."""

    def setUp(self) -> None:
        """Set up the `EDGARQuery` Client."""

        # Initialize a new instance.
        self.edgar = EDGARQuery()

        # This is Facebook.
        self.cik_number = '1265107'

    def test_creates_instance_of_session(self):
        """Create an instance and make sure it's a `EDGARQuery`."""

        # Make sure it matches.
        self.assertIsInstance(self.edgar, EDGARQuery)

    def test_grab_company_directories(self):
        """Test pulling the directories for a particular CIK number."""

        # Grab the Company Directories.
        company_directories = self.edgar.company_directories(
            cik=self.cik_number
        )

        # Make sure they match.
        self.assertIsInstance(company_directories[:2], list)
        self.assertIn("filing_id", company_directories[0])

    def test_grab_company_directory(self):
        """Test grabbing a single filing for a particular CIK number."""

        # Grab for a specific Directory.
        company_directory = self.edgar.company_directory(
            cik=self.cik_number,
            filing_id="000110465919038688"
        )

        # Make sure they match.
        self.assertIsInstance(company_directory, list)
        self.assertIn("item_id", company_directory[0])

    def test_grab_filing_by_type(self):
        """Test grabbing a specific filing type for a particular company."""

        # Grab the 10Ks for Facebook.
        facebook_10ks = self.edgar.company_filings_by_type(
            cik=self.cik_number,
            filing_type='10-K'
        )

        # Make sure they match.
        self.assertIsInstance(facebook_10ks, list)
        self.assertIn("form_name", facebook_10ks[0])

    def test_grab_cik_ownership_filings(self):
        """Test grabbing the ownership filings."""

        # Grab it.
        facebook_ownership = self.edgar.ownership_filings_by_cik(
            cik='1326801',
            before="20200301",
            after="20200101"
        )

        # Make sure they match.
        self.assertIsInstance(facebook_ownership, list)
        self.assertIn("form_name", facebook_ownership[0])

    def test_grab_companies_by_sic(self):
        """Test grabbing companies by SIC."""

        # Grab the Companies.
        sic_content = self.edgar.companies_by_sic(
            sic_code="3841",
            return_count=300
        )

        self.assertIsInstance(sic_content, list)
        self.assertIn("link_href", sic_content[0])

    def tearDown(self) -> None:
        """Teardown the `Edgar` Client."""

        del self.edgar


if __name__ == '__main__':
    unittest.main()
