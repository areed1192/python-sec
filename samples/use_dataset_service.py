"""Example usage of the EDGAR Datasets service."""

from pprint import pprint
from edgar.client import EdgarClient

# Initialize the Edgar Client
# SEC EDGAR requires a User-Agent in the format "Company/Name email@example.com".
edgar_client = EdgarClient(user_agent="Your Name your-email@example.com")

# Initialize the `Datasets` Services.
datasets_service = edgar_client.datasets()

# Grab all the SEC Datasets.
pprint(
    datasets_service.get_sec_datasets()
)

# Grab all the Edgar Taxonomies used in SEC filings..
pprint(
    datasets_service.get_edgar_taxonomies()
)
