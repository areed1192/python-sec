"""Example usage of top-level convenience functions."""

import edgar

# ---------------------------------------------------------------------------
# Option A: Set user-agent via environment variable (recommended for scripts)
# ---------------------------------------------------------------------------

# In your shell:
#   export SEC_EDGAR_USER_AGENT="Your Name your-email@example.com"
#
# Then simply:
#   import edgar
#   company = edgar.company("AAPL")

# ---------------------------------------------------------------------------
# Option B: Set user-agent programmatically
# ---------------------------------------------------------------------------

edgar.set_user_agent("Your Name your-email@example.com")

# ---------------------------------------------------------------------------
# Quick company lookup — no EdgarClient needed
# ---------------------------------------------------------------------------

company = edgar.company("AAPL")
print(company)
# Output: <Company ticker='AAPL' cik='0000320193' name='Apple Inc.'>

# ---------------------------------------------------------------------------
# Get filings directly by ticker
# ---------------------------------------------------------------------------

filings = edgar.get_filings("AAPL", form="10-K")
print(f"Found {len(filings)} 10-K filings")
print(filings[0])
# Output: Filing(form_type='10-K', filing_date='...', accession_number='...')

# ---------------------------------------------------------------------------
# Full-text search — one line
# ---------------------------------------------------------------------------

results = edgar.search("revenue recognition", form_types=["10-K"], size=5)
print(f"Found {len(results)} search results")
for result in results[:3]:
    print(f"  {result.company_name} — {result.form} ({result.filing_date})")

# ---------------------------------------------------------------------------
# All original EdgarClient functionality still works
# ---------------------------------------------------------------------------

client = edgar.EdgarClient(user_agent="Your Name your-email@example.com")
company = client.company("MSFT")
print(company.name)
# Output: MICROSOFT CORP
