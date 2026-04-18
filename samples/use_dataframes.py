"""Example usage of pandas integration — to_dataframe() on response models."""

from edgar.client import EdgarClient
from edgar.models import to_dataframe

# Initialize the client.
# SEC EDGAR requires a User-Agent in the format "Company/Name email@example.com".
edgar_client = EdgarClient(user_agent="Your Name your-email@example.com")


# ---------------------------------------------------------------------------
# Convert XBRL facts to a DataFrame via Facts.to_dataframe()
# ---------------------------------------------------------------------------

company = edgar_client.company("AAPL")
facts = company.get_facts()

df = facts.to_dataframe("us-gaap", "Revenues", unit="USD")
print("=== Apple Revenue (USD) ===")
print(df[["end", "value", "form", "fiscal_year"]].tail())
# Output:
#           end         value  form  fiscal_year
#   2023-09-30  383285000000  10-K         2023
#   2024-09-28  391035000000  10-K         2024


# ---------------------------------------------------------------------------
# Convert any model list using the standalone to_dataframe()
# ---------------------------------------------------------------------------

# Filings
filings = company.get_filings(form="10-K")
df_filings = to_dataframe(filings)
print("\n=== 10-K Filings DataFrame ===")
print(df_filings[["form_type", "filing_date", "accession_number"]].head())
# Output:
#   form_type                  filing_date      accession_number
#       10-K  2024-11-01T18:04:51-04:00  0000320193-24-000123


# ---------------------------------------------------------------------------
# Convert search results to a DataFrame
# ---------------------------------------------------------------------------

results = edgar_client.search(
    q='"artificial intelligence"',
    form_types=["10-K"],
    start_date="2024-01-01",
    end_date="2024-12-31",
    size=10,
)

df_search = to_dataframe(results)
print("\n=== Search Results DataFrame ===")
print(df_search[["company_name", "form", "filing_date"]].head())
# Output:
#                                  company_name  form filing_date
#   Apple Inc.  (AAPL)  (CIK 0000320193)  10-K  2024-11-01


# ---------------------------------------------------------------------------
# Convert submissions to a DataFrame
# ---------------------------------------------------------------------------

info = company.get_info()
df_subs = to_dataframe(info.recent_submissions[:10])
print("\n=== Recent Submissions DataFrame ===")
print(df_subs[["form", "filing_date", "accession_number"]].head())
# Output:
#    form filing_date            accession_number
#   10-K  2024-11-01  0000320193-24-000123
