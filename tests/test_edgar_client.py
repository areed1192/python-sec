"""Unit test module for the EDGAR Client.

Will perform an instance test to make sure it creates it.
"""

import unittest
from unittest import TestCase

from edgar.xbrl import Xbrl
from edgar.series import Series
from edgar.filings import Filings
from edgar.issuers import Issuers
from edgar.archives import Archives
from edgar.datasets import Datasets
from edgar.client import EdgarClient
from edgar.companies import Companies
from edgar.session import EdgarSession
from edgar.submissions import Submissions
from edgar.current_events import CurrentEvents
from edgar.ownership_filings import OwnershipFilings


class Edg(TestCase):

    """Will perform a unit test for the `EdgarClient` session."""

    def setUp(self) -> None:
        """Set up the `EdgarClient` Client."""

        # Initialize a new instance.
        self.edgar_client = EdgarClient()

        # This is Facebook.
        self.cik_number = '1265107'

    def test_creates_instance_of_client(self):
        """Create an instance and make sure it's a `EdgarClient` object."""

        # Make sure it matches.
        self.assertIsInstance(self.edgar_client, EdgarClient)

    def test_creates_instance_of_session(self):
        """Create an instance and make sure it's a `EdgarSession` object."""

        # Make sure it matches.
        self.assertIsInstance(self.edgar_client.edgar_session, EdgarSession)

    def test_creates_instance_of_series(self):
        """Create an instance and make sure it's a `Series` object."""

        # Make sure it matches.
        self.assertIsInstance(self.edgar_client.series(), Series)

    def test_creates_instance_of_archives(self):
        """Create an instance and make sure it's a `Archives` object."""

        # Make sure it matches.
        self.assertIsInstance(self.edgar_client.archives(), Archives)

    def test_creates_instance_of_companies(self):
        """Create an instance and make sure it's a `Companies` object."""

        # Make sure it matches.
        self.assertIsInstance(self.edgar_client.companies(), Companies)

    def test_creates_instance_of_datasets(self):
        """Create an instance and make sure it's a `Datasets` object."""

        # Make sure it matches.
        self.assertIsInstance(self.edgar_client.datasets(), Datasets)

    def test_creates_instance_of_current_events(self):
        """Create an instance and make sure it's a `CurrentEvents` object."""

        # Make sure it matches.
        self.assertIsInstance(
            self.edgar_client.current_events(),
            CurrentEvents
        )

    def test_creates_instance_of_filings(self):
        """Create an instance and make sure it's a `Filing` object."""

        # Make sure it matches.
        self.assertIsInstance(self.edgar_client.filings(), Filings)

    def test_creates_instance_of_issuers(self):
        """Create an instance and make sure it's a `Issuers` object."""

        # Make sure it matches.
        self.assertIsInstance(self.edgar_client.issuers(), Issuers)

    def test_creates_instance_of_ownership_filings(self):
        """Create an instance and make sure it's a `OwnershipFilings` object."""

        # Make sure it matches.
        self.assertIsInstance(
            self.edgar_client.ownership_filings(),
            OwnershipFilings
        )

    def test_creates_instance_of_submissions(self):
        """Create an instance and make sure it's a `Submissions` object."""

        # Make sure it matches.
        self.assertIsInstance(self.edgar_client.submissions(), Submissions)

    def test_creates_instance_of_xbrl(self):
        """Create an instance and make sure it's a `Xbrl` object."""

        # Make sure it matches.
        self.assertIsInstance(self.edgar_client.xbrl(), Xbrl)

    def tearDown(self) -> None:
        """Teardown the `Edgar` Client."""

        del self.edgar_client


if __name__ == '__main__':
    unittest.main()
