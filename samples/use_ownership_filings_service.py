from pprint import pprint
from edgar.client import EdgarClient

# Initialize the Edgar Client
edgar_client = EdgarClient()

# Initialize the `OwnershipFilings` Services.
filings_service = edgar_client.ownership_filings()

# Grab all the Ownership Filings that fall under a certain CIK number.
pprint(
    filings_service.get_ownership_filings_by_cik(
        cik='1326801'
    )
)

# Grab all the Ownership Filings that fall under a certain company name.
pprint(
    filings_service.get_ownership_filings_by_name(
        company_name='Facebook'
    )
)

# Grab all the Non-Ownership Filings that fall under a certain CIK number.
pprint(
    filings_service.get_non_ownership_filings_by_cik(
        cik='1326801'
    )
)

# Grab all the Non-Ownership Filings that fall under a certain company name.
pprint(
    filings_service.get_non_ownership_filings_by_name(
        company_name='Facebook'
    )
)

# Complex Query for Ownership Filings.
pprint(
    filings_service.query_ownership_filings(
        company_name='Facebook',
        after_date='2019-12-01'
    )
)

# Complex Query for Ownership Filings.
pprint(
    filings_service.query_non_ownership_filings(
        company_name='Facebook',
        after_date='2019-12-01'
    )
)