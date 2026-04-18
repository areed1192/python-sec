"""Example usage of the EDGAR Datasets service."""

from pprint import pprint
from edgar.client import EdgarClient

# Initialize the Edgar Client
# SEC EDGAR requires a User-Agent in the format "Company/Name email@example.com".
edgar_client = EdgarClient(user_agent="Your Name your-email@example.com")

# Initialize the `Datasets` Services.
datasets_service = edgar_client.datasets()

# Grab all the SEC Datasets.
pprint(
    datasets_service.get_sec_datasets()
)

# Grab all the Edgar Taxonomies used in SEC filings..
pprint(
    datasets_service.get_edgar_taxonomies()
)


# ---------------------------------------------------------------------------
# Bulk Financial Statements — DERA quarterly datasets
# ---------------------------------------------------------------------------

# Download the 2023 Q4 financial statement dataset (ZIP of TSV files).
# Returns a dict of lists of dicts keyed by file name (sub, num, tag, pre).
data = datasets_service.get_financial_statements(year=2023, quarter=4)

print("\n=== Financial Statements 2023 Q4 ===")
print(f"Files: {list(data.keys())}")
print(f"Submissions: {len(data.get('sub', []))}")
print(f"Numeric facts: {len(data.get('num', []))}")

# Inspect a single submission row.
if data.get("sub"):
    row = data["sub"][0]
    print(f"\nFirst submission: {row.get('name')} (CIK {row.get('cik')}, form {row.get('form')})")

# Inspect a numeric fact row.
if data.get("num"):
    row = data["num"][0]
    print(f"First numeric: tag={row.get('tag')}, value={row.get('value')}, uom={row.get('uom')}")


# ---------------------------------------------------------------------------
# Bulk Financial Statements as DataFrames (requires pandas)
# ---------------------------------------------------------------------------

# Same data but returned as pandas DataFrames for analysis.
# dfs = datasets_service.get_financial_statements_dataframes(year=2023, quarter=4)
# print(dfs["sub"].head())
# print(dfs["num"].describe())
