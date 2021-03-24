from pprint import pprint
from edgar.client import EdgarClient

# Initialize the Edgar Client
edgar_client = EdgarClient()

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
