"""Example usage of the EDGAR Variable Insurance Products service."""

from pprint import pprint
from edgar.client import EdgarClient

# Initialize the Edgar Client
# SEC EDGAR requires a User-Agent in the format "Company/Name email@example.com".
edgar_client = EdgarClient(user_agent="Your Name your-email@example.com")

# Initialize the `VariableInsuranceProducts` Services.
insurance_prods_services = edgar_client.variable_insurance_products()

# Grab all the products that fall under a certain name.
response = insurance_prods_services.get_products_by_name(
    company_name='goldman sachs'
)

# Print the response.
pprint(response)
