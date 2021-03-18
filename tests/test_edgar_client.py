"""Unit test module for the EDGAR Client.

Will perform an instance test to make sure it creates it.
"""

import unittest

from typing import List
from unittest import TestCase
from edgar.client import EdgarClient
from edgar.session import EdgarSession
from edgar.series import Series
from edgar.companies import Companies
from edgar.archives import Archives


class Edg(TestCase):

    """Will perform a unit test for the `EdgarClient` session."""

    def setUp(self) -> None:
        """Set up the `EdgarClient` Client."""

        # Initialize a new instance.
        self.edgar_client = EdgarClient()

        # This is Facebook.
        self.cik_number = '1265107'

    def test_creates_instance_of_client(self):
        """Create an instance and make sure it's a `EdgarClient`."""

        # Make sure it matches.
        self.assertIsInstance(self.edgar_client, EdgarClient)

    def test_creates_instance_of_session(self):
        """Create an instance and make sure it's a `EdgarSession`."""

        # Make sure it matches.
        self.assertIsInstance(self.edgar_client.edgar_session, EdgarSession)

    def test_creates_instance_of_series(self):
        """Create an instance and make sure it's a `Series`."""

        # Make sure it matches.
        self.assertIsInstance(self.edgar_client.series(), Series)

    def test_creates_instance_of_archives(self):
        """Create an instance and make sure it's a `Archives`."""

        # Make sure it matches.
        self.assertIsInstance(self.edgar_client.archives(), Archives)

    def test_creates_instance_of_companies(self):
        """Create an instance and make sure it's a `Companies`."""

        # Make sure it matches.
        self.assertIsInstance(self.edgar_client.companies(), Companies)

    def tearDown(self) -> None:
        """Teardown the `Edgar` Client."""

        del self.edgar_client


if __name__ == '__main__':
    unittest.main()