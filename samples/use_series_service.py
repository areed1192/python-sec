"""Example usage of the EDGAR Series service."""

from pprint import pprint
from edgar.client import EdgarClient

# Initialize the Edgar Client
# SEC EDGAR requires a User-Agent in the format "Company/Name email@example.com".
edgar_client = EdgarClient(user_agent="Your Name your-email@example.com")

# Initialize the `Series` Services.
series_services = edgar_client.series()

# Grab a series by the CIK number.
pprint(series_services.get_series_by_cik(cik='814679'))

# Grab all the series that belong to a particular series ID.
pprint(series_services.get_series_by_series_id(series_id='S000001976'))

# Get the filings that belong to a particular Series ID.
pprint(series_services.get_series_filings_by_series_id(series_id='S000001976'))
