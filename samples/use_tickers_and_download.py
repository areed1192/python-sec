"""Example usage of the Ticker Resolution and Filing Download features."""

from pprint import pprint
from edgar.client import EdgarClient

# Initialize the client.
# SEC EDGAR requires a User-Agent in the format "Company/Name email@example.com".
edgar_client = EdgarClient(user_agent="Your Name your-email@example.com")


# ---------------------------------------------------------------------------
# Ticker Resolution — look up CIK numbers by ticker symbol
# ---------------------------------------------------------------------------

# Resolve a ticker symbol to a CIK number.
cik = edgar_client.resolve_ticker("AAPL")
print(f"AAPL CIK: {cik}")
# Output: AAPL CIK: 0000320193

# Resolve another ticker.
cik = edgar_client.resolve_ticker("MSFT")
print(f"MSFT CIK: {cik}")

# ---------------------------------------------------------------------------
# Reverse Lookup — CIK to company info
# ---------------------------------------------------------------------------

# Look up company info from a CIK number.
entries = edgar_client.resolve_cik("320193")
pprint(entries)
# Output: [{'cik_str': 320193, 'ticker': 'AAPL', 'title': 'Apple Inc.'}, ...]

# ---------------------------------------------------------------------------
# Company Search — find companies by name or ticker
# ---------------------------------------------------------------------------

# Access the full Tickers service for search.
tickers_service = edgar_client.tickers()

# Search by company name (case-insensitive).
results = tickers_service.search("Tesla")
print(f"\nFound {len(results)} results for 'Tesla':")
for entry in results[:5]:
    print(f"  {entry['ticker']:10s}  CIK {entry['cik_str']:>10}  {entry['title']}")

# Search by partial ticker.
results = tickers_service.search("GOOG")
print(f"\nFound {len(results)} results for 'GOOG':")
for entry in results:
    print(f"  {entry['ticker']:10s}  CIK {entry['cik_str']:>10}  {entry['title']}")

# ---------------------------------------------------------------------------
# Combine: Ticker → CIK → Filings
# ---------------------------------------------------------------------------

# Use resolve_ticker to get a CIK, then fetch filings.
cik = edgar_client.resolve_ticker("META")
print(f"\nMETA CIK: {cik}")

# Strip leading zeros for service methods that expect unpadded CIK.
cik_unpadded = cik.lstrip("0")
filings = edgar_client.filings().get_filings_by_cik(cik=cik_unpadded)
pprint(filings[:2] if filings else "No filings found")

# ---------------------------------------------------------------------------
# Filing Download — fetch actual document content
# ---------------------------------------------------------------------------

# Download a filing document by URL (returns text for HTML/XML, bytes for PDF).
FILING_URL = "https://www.sec.gov/Archives/edgar/data/320193/000032019321000105/aapl-20210925.htm"
content = edgar_client.download(FILING_URL)
print(f"\nDownloaded {len(content)} characters")

# Download and save to a file.
edgar_client.download(FILING_URL, path="aapl-10k.html")
print("Saved to aapl-10k.html")

# NOTE: The download lines above are commented out to avoid making live
# requests when running this sample. Uncomment them to test with real data.
