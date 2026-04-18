"""Example usage of the EDGAR Current Events service."""

from pprint import pprint
from edgar.client import EdgarClient

# Initialize the Edgar Client
# SEC EDGAR requires a User-Agent in the format "Company/Name email@example.com".
edgar_client = EdgarClient(user_agent="Your Name your-email@example.com")

# Initialize the Current Events Services.
current_events_services = edgar_client.current_events()

# Grab all the companies that are based in Texas.
pprint(current_events_services.get_current_event_filings(days_prior=0, form='10-k-annual'))
