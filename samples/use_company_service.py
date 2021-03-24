from pprint import pprint
from edgar.client import EdgarClient
from edgar.enums import StateCodes
from edgar.enums import CountryCodes
from edgar.enums import StandardIndustrialClassificationCodes

# Initialize the Edgar Client
edgar_client = EdgarClient()

# Initialize the Company Services.
company_services = edgar_client.companies()

# Grab all the companies that are based in Texas.
pprint(company_services.get_companies_by_state(state_code='TX'))

# Alternatively, if you didn't know the 2 letter code you coude pass through an Enum.
pprint(
    company_services.get_companies_by_state(
        state_code=StateCodes.West_Virginia
    )
)

# Grab all the companies that are based in Australia, same logic here with the Enums.
pprint(
    company_services.get_companies_by_country(
        country_code=CountryCodes.AUSTRALIA
    )
)

# Grab all the companies that are Oil & Gas Services Companies, same logic here with the Enums.
pprint(
    company_services.get_companies_by_sic(
        sic_code=StandardIndustrialClassificationCodes.OIL_AND_GAS_FIELD_SERVICES_NEC
    )
)

# Return a company by the file number.
pprint(
    company_services.get_company_by_file_number(file_number='021-230507')
)

# Return a company by their CIK Number.
pprint(
    company_services.get_company_by_cik(cik='1628533')
)

# Search a company using their name.
pprint(
    company_services.get_companies_by_name(name='Microsoft')
)


pprint(
    company_services.query(
        company_name='Superior Well Services, INC',
        sic_code=StandardIndustrialClassificationCodes.OIL_AND_GAS_FIELD_SERVICES_NEC
    )
)