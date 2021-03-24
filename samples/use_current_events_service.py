from pprint import pprint
from edgar.client import EdgarClient

# Initialize the Edgar Client
edgar_client = EdgarClient()

# Initialize the Current Events Services.
current_events_services = edgar_client.current_events()

# Grab all the companies that are based in Texas.
pprint(current_events_services.get_current_event_filings(days_prior=0, form='10-k-annual'))
