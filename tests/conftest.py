"""Shared pytest fixtures for the python-sec test suite."""

import pytest

from edgar.client import EdgarClient

TEST_USER_AGENT = "TestSuite test@example.com"
TEST_CIK = "1326801"


@pytest.fixture
def edgar_client():
    """Return an EdgarClient configured with a test user-agent."""
    return EdgarClient(user_agent=TEST_USER_AGENT)


@pytest.fixture
def edgar_session(edgar_client):  # noqa: ARG001  # pylint: disable=redefined-outer-name
    """Return the EdgarSession from the test client."""
    return edgar_client.edgar_session


@pytest.fixture
def edgar_parser(edgar_session):  # noqa: ARG001  # pylint: disable=redefined-outer-name
    """Return the shared EdgarParser instance."""
    return edgar_session.edgar_parser


@pytest.fixture
def edgar_utilities(edgar_session):  # noqa: ARG001  # pylint: disable=redefined-outer-name
    """Return the shared EdgarUtilities instance."""
    return edgar_session.edgar_utilities


# ---------------------------------------------------------------------------
# Sample XML / HTML fixtures
# ---------------------------------------------------------------------------

SAMPLE_ATOM_FEED = """\
<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <title>EDGAR Company Search</title>
  <link rel="self" href="https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany"/>
  <entry>
    <title>10-K - Annual report</title>
    <link rel="alternate" type="text/html" href="https://www.sec.gov/Archives/edgar/data/1326801/0001326801-21-000003.txt"/>
    <summary>Annual report for fiscal year 2020</summary>
    <updated>2021-01-28T00:00:00-05:00</updated>
    <category scheme="https://www.sec.gov/" label="form-type" term="10-K"/>
    <id>urn:tag:sec.gov,2021:accession-number=0001326801-21-000003</id>
  </entry>
  <entry>
    <title>10-Q - Quarterly report</title>
    <link rel="alternate" type="text/html" href="https://www.sec.gov/Archives/edgar/data/1326801/0001326801-21-000004.txt"/>
    <summary>Quarterly report for Q1 2021</summary>
    <updated>2021-04-22T00:00:00-05:00</updated>
    <category scheme="https://www.sec.gov/" label="form-type" term="10-Q"/>
    <id>urn:tag:sec.gov,2021:accession-number=0001326801-21-000004</id>
  </entry>
</feed>
"""

SAMPLE_ATOM_FEED_WITH_NEXT = """\
<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <title>EDGAR Company Search</title>
  <link rel="next" type="application/atom+xml" href="https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&amp;start=40"/>
  <entry>
    <title>10-K - Annual report</title>
    <link rel="alternate" type="text/html" href="https://www.sec.gov/Archives/edgar/data/1326801/0001326801-21-000003.txt"/>
    <summary>First page entry</summary>
    <updated>2021-01-28T00:00:00-05:00</updated>
    <category scheme="https://www.sec.gov/" label="form-type" term="10-K"/>
    <id>urn:tag:sec.gov,2021:accession-number=0001326801-21-000003</id>
  </entry>
</feed>
"""

SAMPLE_ATOM_FEED_NO_NEXT = """\
<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <title>EDGAR Company Search</title>
  <entry>
    <title>8-K - Current report</title>
    <link rel="alternate" type="text/html" href="https://www.sec.gov/Archives/edgar/data/1326801/0001326801-21-000005.txt"/>
    <summary>Second page entry</summary>
    <updated>2021-06-15T00:00:00-05:00</updated>
    <category scheme="https://www.sec.gov/" label="form-type" term="8-K"/>
    <id>urn:tag:sec.gov,2021:accession-number=0001326801-21-000005</id>
  </entry>
</feed>
"""

SAMPLE_MALFORMED_XML = "<feed><broken"

SAMPLE_ISSUER_HTML = """\
<html>
<body>
<table></table>
<table></table>
<table></table>
<table></table>
<table>
<tr>
<td><a href="/cgi-bin/browse-edgar?action=getcompany&CIK=0001326801">Facebook Inc</a></td>
<td><a href="/cgi-bin/own-disp?action=getissuer&CIK=0001326801">3 filings</a></td>
<td>2021-01-15</td>
<td>Director</td>
</tr>
</table>
<table id="transaction-report">
<tr>
<td>Date</td>
<td>Reporting Owner</td>
<td>Form</td>
<td>Transaction Type</td>
<td>Shares</td>
<td>Link</td>
<td>Price</td>
</tr>
<tr>
<td>2021-01-15</td>
<td><a href="/cgi-bin/browse-edgar?action=getcompany&CIK=0001326801">John Doe</a></td>
<td>4</td>
<td>Purchase</td>
<td>1000</td>
<td>$150.00</td>
</tr>
</table>
</body>
</html>
"""

SAMPLE_XBRL_COMPANY_FACTS = {
    "cik": 1326801,
    "entityName": "Facebook, Inc.",
    "facts": {
        "dei": {
            "EntityPublicFloat": {
                "label": "Entity Public Float",
                "description": "Aggregate market value",
                "units": {
                    "USD": [
                        {
                            "end": "2012-06-29",
                            "val": 47206114899,
                            "accn": "0001326801-13-000003",
                            "fy": 2012,
                            "fp": "FY",
                            "form": "10-K",
                            "filed": "2013-02-01",
                        }
                    ]
                },
            }
        }
    },
}

SAMPLE_SUBMISSIONS_JSON = {
    "cik": "1326801",
    "entityType": "operating",
    "sic": "7372",
    "sicDescription": "SERVICES-PREPACKAGED SOFTWARE",
    "name": "Facebook, Inc.",
    "tickers": ["FB"],
    "exchanges": ["NASDAQ"],
    "filings": {
        "recent": {
            "accessionNumber": ["0001326801-21-000003"],
            "filingDate": ["2021-01-28"],
            "form": ["10-K"],
        }
    },
}

SAMPLE_DIRECTORY_JSON = {
    "directory": {
        "name": "/Archives/edgar/data/1326801",
        "item": [
            {
                "name": "000132680121000003",
                "last-modified": "2021-01-28 16:05:00",
                "size": "",
            }
        ],
    }
}

SAMPLE_FILING_DIRECTORY_JSON = {
    "directory": {
        "name": "/Archives/edgar/data/1326801/000132680121000003",
        "item": [
            {
                "name": "fb-20201231.htm",
                "last-modified": "2021-01-28 16:05:00",
                "size": "1234567",
            }
        ],
    }
}
