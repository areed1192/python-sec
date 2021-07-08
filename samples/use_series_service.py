from pprint import pprint
from edgar.client import EdgarClient

# Initialize the Edgar Client
edgar_client = EdgarClient()

# Initialize the `Series` Services.
series_services = edgar_client.series()

# Grab a series by the CIK number.
pprint(series_services.get_series_by_cik(cik='814679'))

# Grab all the series that belong to a particular series ID.
pprint(series_services.get_series_by_series_id(series_id='S000001976'))

# Get the filings that belong to a particular Series ID.
pprint(series_services.get_series_filings_by_series_id(series_id='S000001976'))
