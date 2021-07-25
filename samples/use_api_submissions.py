from pprint import pprint
from edgar.client import EdgarClient

# Initialize the Edgar Client
edgar_client = EdgarClient()

# Initialize the `Submissions` Services.
submissions_services = edgar_client.submissions()

# Grab all the submissions.
pprint(
    submissions_services.get_submissions(cik='1326801')
)
