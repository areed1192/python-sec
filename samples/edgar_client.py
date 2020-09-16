import pprint
from datetime import date
from pysec.edgar import EDGARQuery
from pysec.filing_types import FILING_TYPES

# Initalize the client.
edgar_client = EDGARQuery()

# Grab the EDGAR Taxonomies File.
edgar_taxonomies = edgar_client.get_edgar_taxonomies()
pprint.pprint(edgar_taxonomies)

# Grab a specific Quarterly Archive Indexes.
quarterly_archives = edgar_client.get_quarterly_index(year=2000, quarter=4)
pprint.pprint(quarterly_archives)

# Grab ALL of the Quarterly Archive Indexes.
quarterly_archives = edgar_client.get_quarterly_indexes()
pprint.pprint(quarterly_archives)

# Grab all the directories belonging to a specific CIK number.
# In this case the CIK number `1326801` is Facebook.
company_filings = edgar_client.company_directories(cik='1326801')
pprint.pprint(company_filings[:2])

# Grab all the items for a particular directory.
company_items = edgar_client.company_directory(
    cik='1326801',
    filing_id='000110465919038688'
)
pprint.pprint(company_items[:2])

# Grab all the filings belonging to a certain type.
filings_10K = edgar_client.company_filings_by_type(
    cik='1326801',
    filing_type='10-k'
)
pprint.pprint(filings_10K)

# Grab all the Companies that are based in a certain US State.
state_content = edgar_client.companies_by_state(
    state='CA',
    return_count=120
)
pprint.pprint(state_content[:4])

# Grab all the Companies that are based in a certain Country. In the example below, "Q2" represents 'New Zealand'
# ALEX NOTE: THIS IS BROKEN, HAVE TO MANUALLY CREATE NEXT URL SINCE DEFAULTED ONE ISN'T RIGHT.
country_content = edgar_client.companies_by_country(
    country='Q2',
    return_count=120
)
pprint.pprint(country_content[:4])

# Grab all the Ownership filings for a particular CIK falling under a certain date range.
cik_ownership_filings = edgar_client.ownership_filings_by_cik(
    cik='1326801',
    before="20200301",
    after="20200101"
)
pprint.pprint(cik_ownership_filings)

# Grab the companies that fall under a certain SIC Code.
sic_companies = edgar_client.companies_by_sic(
    sic_code="3841",
    return_count=300,
    start=200
)
pprint.pprint(sic_companies)

# Grab all non-ownership filigns by company name.
sic_companies = edgar_client.non_ownership_filings_by_company_name(
    company_name="facebook",
    before="20200301",
    after="20200101"
)
pprint.pprint(sic_companies)

# Grab all ownership filigns by company name.
sic_companies = edgar_client.ownership_filings_by_company_name(
    company_name="facebook",
    before="20200301",
    after="20200101"
)
pprint.pprint(sic_companies)

# Grab all non-ownership filigns by CIK.
sic_companies = edgar_client.non_ownership_filings_by_cik(
    cik='1326801',
    before="20200301",
    after="20200101"
)
pprint.pprint(sic_companies)

# Grab all ownership filigns by CIK.
sic_companies = edgar_client.ownership_filings_by_cik(
    cik='1326801',
    before="20200301",
    after="20200101"
)
pprint.pprint(sic_companies)

# Grab all the issuers.
issuers_table = edgar_client.get_issuers_by_cik(cik='0001084869')
pprint.pprint(issuers_table)

# Grab all the Mutual Funds by name.
mutual_funds_name = edgar_client.get_mutual_funds_by_name(
    company_name='Goldman Sachs'
)
pprint.pprint(mutual_funds_name)

# Grab all the Mutual Funds Prospectus by CIK.
mutual_funds_prospectus = edgar_client.get_mutual_funds_prospectus_by_cik(
    cik='0000860118'
)
pprint.pprint(mutual_funds_prospectus)

# Grab all the Mutual Funds Proxy Records
mutual_funds_proxy_records = edgar_client.get_mutual_funds_proxy_records_by_cik(
    cik='0001039001'
)
pprint.pprint(mutual_funds_proxy_records)

# Grab all the Mutual Funds Shareholder Reports
mutual_funds_shareholder_reports = edgar_client.get_mutual_funds_shareholder_reports_by_cik(
    cik='0001039001'
)
pprint.pprint(mutual_funds_shareholder_reports)

# Grab all the Mutual Funds Statutory Prospectus
mutual_funds_statutory_prospectus = edgar_client.get_mutual_funds_statutory_prospectus_by_cik(
    cik='0001039001'
)
pprint.pprint(mutual_funds_statutory_prospectus)

# Grab all the Mutual Funds Summary Prospectus
mutual_funds_summary_prospectus = edgar_client.get_mutual_funds_summary_prospectus_by_cik(
    cik='0001039001'
)
pprint.pprint(mutual_funds_summary_prospectus)

# Grab all the Mutual Funds Effectiveness Notices
mutual_funds_effectiveness_notices = edgar_client.get_mutual_funds_effectiveness_notices_by_cik(
    cik='0001039001'
)
pprint.pprint(mutual_funds_effectiveness_notices)

# Grab Variable Products, by Name.
variable_products = edgar_client.get_variable_insurance_products_by_name(
    product_name='Goldman Sachs'
)
pprint.pprint(variable_products)

# Grab current event filings.
current_event_filings = edgar_client.get_current_event_filings(
    days_prior=5,
    form='10-k-annual'
)
pprint.pprint(current_event_filings)
