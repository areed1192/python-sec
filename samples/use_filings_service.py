from pprint import pprint
from edgar.client import EdgarClient
from edgar.enums import FilingTypeCodes

# Initialize the Edgar Client
edgar_client = EdgarClient()

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
