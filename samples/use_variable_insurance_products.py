from pprint import pprint
from edgar.client import EdgarClient

# Initialize the Edgar Client
edgar_client = EdgarClient()

# Initialize the `VariableInsuranceProducts` Services.
insurance_prods_services = edgar_client.variable_insurance_products()

# Grab all the products that fall under a certain name.
insurance_prods_services.get_products_by_name(
    company_name='goldman sachs'
)