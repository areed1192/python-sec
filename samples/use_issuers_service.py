from pprint import pprint
from edgar.client import EdgarClient
from edgar.enums import StateCodes
from edgar.enums import CountryCodes
from edgar.enums import StandardIndustrialClassificationCodes

# Initialize the Edgar Client
edgar_client = EdgarClient()

# Initialize the Issuers Services.
issuers_service = edgar_client.issuers()

# Grab all the companies that are based in Texas.
pprint(issuers_service.get_issuers_by_cik(cik='0001084869'))
