"""Example usage of the fluent Company interface.

The Company class lets you work with a single company by ticker or CIK
without managing service objects or CIK numbers manually.
"""

from pprint import pprint
from edgar.client import EdgarClient

# Initialize the client.
# SEC EDGAR requires a User-Agent in the format "Company/Name email@example.com".
edgar_client = EdgarClient(user_agent="Your Name your-email@example.com")


# ---------------------------------------------------------------------------
# Create a Company — by ticker or CIK
# ---------------------------------------------------------------------------

# By ticker symbol.
apple = edgar_client.company("AAPL")
print(apple)
# <Company ticker='AAPL' cik='0000320193' name='Apple Inc.'>

# By CIK number.
microsoft = edgar_client.company("789019")
print(microsoft)

# Access company properties.
print(f"Ticker: {apple.ticker}")
print(f"CIK:    {apple.cik}")
print(f"Name:   {apple.name}")


# ---------------------------------------------------------------------------
# Filings — raw dict results (backward compatible)
# ---------------------------------------------------------------------------

# Get recent filings (all types).
all_filings = apple.filings()
print(f"\nTotal filings returned: {len(all_filings)}")
pprint(all_filings[0])

# Filter by form type.
annual_reports = apple.filings(form="10-K")
print(f"\n10-K filings: {len(annual_reports)}")

quarterly_reports = apple.filings(form="10-Q")
print(f"10-Q filings: {len(quarterly_reports)}")


# ---------------------------------------------------------------------------
# Submissions — full filing history
# ---------------------------------------------------------------------------

subs = apple.submissions()
if subs:
    print(f"\nEntity: {subs.get('name')}")
    print(f"SIC:    {subs.get('sicDescription')}")


# ---------------------------------------------------------------------------
# XBRL Facts — financial data
# ---------------------------------------------------------------------------

facts = apple.xbrl_facts()
if facts:
    print(f"\nXBRL entity: {facts.get('entityName')}")
    taxonomies = list(facts.get("facts", {}).keys())
    print(f"Taxonomies: {taxonomies}")


# ---------------------------------------------------------------------------
# Download a filing document
# ---------------------------------------------------------------------------

# Get filings, then download the first one.
filings = apple.filings(form="10-K")
if filings:
    url = filings[0].get("link_href", "")
    if url:
        content = apple.download(url)
        print(f"\nDownloaded {len(content)} characters from {url[:60]}...")

        # Save to file.
        # apple.download(url, path="apple_10k.html")
