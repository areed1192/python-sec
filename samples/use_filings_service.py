"""Example usage of the EDGAR Filings service."""

from pprint import pprint
from edgar.client import EdgarClient
from edgar.enums import FilingTypeCodes

# Initialize the Edgar Client
# SEC EDGAR requires a User-Agent in the format "Company/Name email@example.com".
edgar_client = EdgarClient(user_agent="Your Name your-email@example.com")

# Initialize the `Filings` Services.
filings_service = edgar_client.filings()

# Grab some filings for Facebook.
pprint(
    filings_service.get_filings_by_cik(cik='1326801')
)

# Grab the 10-Ks for Facebook,
pprint(
    filings_service.get_filings_by_type(
        cik='1326801',
        filing_type=FilingTypeCodes.FILING_10K
    )
)

# Grab some filings for Facebook using the advance query.
pprint(
    filings_service.query(
        cik='1326801',
        filing_type='10-k'
    )
)
