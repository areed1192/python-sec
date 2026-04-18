"""Example usage of the EDGAR Issuers service."""

from pprint import pprint
from edgar.client import EdgarClient

# Initialize the Edgar Client
# SEC EDGAR requires a User-Agent in the format "Company/Name email@example.com".
edgar_client = EdgarClient(user_agent="Your Name your-email@example.com")

# Initialize the Issuers Services.
issuers_service = edgar_client.issuers()

# Grab all the companies that are based in Texas.
pprint(issuers_service.get_issuers_by_cik(cik='0001084869'))
