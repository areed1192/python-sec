import pprint
from pysec.edgar import EDGARQuery

# Initalize the client.
edgar_client = EDGARQuery()

# # Grab all the directories belonging to a specific CIK number.
# # In this case the CIK number `1326801` is Facebook.
# company_filings = edgar_client.company_directories(cik='1326801')
# pprint.pprint(company_filings[:2])

# # Grab all the items for a particular directory.
# company_items = edgar_client.company_directory(cik='1326801', filing_id='000110465919038688')
# pprint.pprint(company_items[:2])

# # Grab all the filings belonging to a certain type.
# filings_10K = edgar_client.company_filings_by_type(cik='1326801', filing_type='10-K')
# pprint.pprint(filings_10K)

# # Grab all the Companies that are based in a certain US State.
# state_content = edgar_client.companies_by_state(state='CA', num_of_companies=120)
# pprint.pprint(state_content[:4])

# Grab all the Companies that are based in a certain Country. In the example below, "Q2" represents 'New Zealand'
# ALEX NOTE: THIS IS BROKEN, HAVE TO MANUALLY CREATE NEXT URL SINCE DEFAULTED ONE ISN'T RIGHT.
country_content = edgar_client.companies_by_country(country='Q2', num_of_companies=120)
pprint.pprint(country_content[:4])