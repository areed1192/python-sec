"""Example usage of the SEC EDGAR XBRL API."""

from pprint import pprint
from edgar.client import EdgarClient

# Initialize the Edgar Client
# SEC EDGAR requires a User-Agent in the format "Company/Name email@example.com".
edgar_client = EdgarClient(user_agent="Your Name your-email@example.com")

# Initialize the `Xbrl` Services.
xbrl_services = edgar_client.xbrl()

# Grab the company facts for Virtusa Corp.
pprint(
    xbrl_services.company_facts(
        cik='0001326801'
    )
)

# Grab the Current Accounts Payable for Virtusa Corp.
pprint(
    xbrl_services.company_concepts(
        cik='1207074',
        concept='AccountsPayableCurrent'
    )
)

# Grab Aggregated data using the Frames endpoint.
pprint(
    xbrl_services.frames(
        concept='AccountsPayableCurrent',
        unit_of_measure='USD',
        period='CY2019Q1I'
    )
)
