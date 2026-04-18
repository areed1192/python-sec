"""Example usage of the EDGAR Mutual Funds service."""

from pprint import pprint
from edgar.client import EdgarClient

# Initialize the Edgar Client
# SEC EDGAR requires a User-Agent in the format "Company/Name email@example.com".
edgar_client = EdgarClient(user_agent="Your Name your-email@example.com")

# Initialize the `MutualFunds` Services.
mutual_funds_services = edgar_client.mutual_funds()

# Grab all the mutual fund filings for a specific CIK..
pprint(
    mutual_funds_services.get_mutual_fund_filings_by_type(
        cik='C000005186',
        mutual_fund_type='mutual-fund',
        number_of_filings=300
    )
)

# Grab all the mutual fund filings for a specific name..
pprint(
    mutual_funds_services.get_mutual_funds_by_name(
        company_name='ADVANCED SERIES TRUST',
    )
)

# Grab all the series and Contracts.
pprint(
    mutual_funds_services.list_series_and_contracts_by_cik(
        cik='814679'
    )
)
