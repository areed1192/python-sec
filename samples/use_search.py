"""Example usage of the EDGAR Full-Text Search (EFTS) service."""

from edgar.client import EdgarClient

# Initialize the client.
# SEC EDGAR requires a User-Agent in the format "Company/Name email@example.com".
edgar_client = EdgarClient(user_agent="Your Name your-email@example.com")


# ---------------------------------------------------------------------------
# Basic full-text search across all SEC filings
# ---------------------------------------------------------------------------

results = edgar_client.search(q="revenue recognition")
print(f"Results returned: {len(results)}")

for result in results[:3]:
    print(result)
    # <SearchResult form='10-K' date='2024-02-27' company='SLR Investment Corp. ...'>


# ---------------------------------------------------------------------------
# Filter by form type and date range
# ---------------------------------------------------------------------------

results = edgar_client.search(
    q='"artificial intelligence"',
    form_types=["10-K", "10-Q"],
    start_date="2024-01-01",
    end_date="2024-12-31",
)

print("\n=== AI mentions in 10-K/10-Q filings (2024) ===")
print(f"Total results: {len(results)}")

for result in results[:5]:
    print(f"  {result.filing_date}  {result.form:6s}  {result.company_name}")
    # Output: 2024-11-01  10-K    Apple Inc.  (AAPL)  (CIK 0000320193)


# ---------------------------------------------------------------------------
# Access individual SearchResult properties
# ---------------------------------------------------------------------------

if results:
    first = results[0]
    print("\n=== First Result Details ===")
    print(f"  Company:          {first.company_name}")
    print(f"  CIK:              {first.cik}")
    print(f"  Form:             {first.form}")
    print(f"  Filing date:      {first.filing_date}")
    print(f"  Accession number: {first.accession_number}")
    print(f"  File type:        {first.file_type}")
    print(f"  Period ending:    {first.period_ending}")
    print(f"  URL:              {first.url}")

    # Raw Elasticsearch hit is always available.
    print(f"  Raw score:        {first.raw.get('_score')}")


# ---------------------------------------------------------------------------
# Pagination — retrieve additional pages of results
# ---------------------------------------------------------------------------

page2 = edgar_client.search(q="climate risk", start=100, size=50)
print(f"\nPage 2 results: {len(page2)}")
