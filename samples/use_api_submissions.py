"""Example usage of the SEC EDGAR Submissions API."""

from pprint import pprint
from edgar.client import EdgarClient

# Initialize the Edgar Client
# SEC EDGAR requires a User-Agent in the format "Company/Name email@example.com".
edgar_client = EdgarClient(user_agent="Your Name your-email@example.com")

# Initialize the `Submissions` Services.
submissions_services = edgar_client.submissions()

# Grab all the submissions.
pprint(
    submissions_services.get_submissions(cik='1326801')
)
