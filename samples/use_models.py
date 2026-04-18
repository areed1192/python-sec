"""Example usage of structured dataclass response models.

The models (Filing, CompanyInfo, Submission) wrap raw API dicts with
typed properties, making results easier to work with in code, REPLs,
and notebooks.
"""

from edgar.client import EdgarClient

# Initialize the client.
# SEC EDGAR requires a User-Agent in the format "Company/Name email@example.com".
edgar_client = EdgarClient(user_agent="Your Name your-email@example.com")


# ---------------------------------------------------------------------------
# Filing models — via Company.get_filings()
# ---------------------------------------------------------------------------

company = edgar_client.company("AAPL")

# get_filings() returns Filing objects instead of raw dicts.
filings = company.get_filings(form="10-K")

print("=== Filing Objects ===")
for f in filings[:3]:
    print(f)
    # <Filing form='10-K' date='2024-11-01' title='10-K - Annual report ...'>

# Access typed properties.
if filings:
    filing = filings[0]
    print(f"\nForm type:        {filing.form_type}")
    print(f"Filing date:      {filing.filing_date}")
    print(f"URL:              {filing.url}")
    print(f"Title:            {filing.title}")
    print(f"Summary:          {filing.summary[:80]}...")
    print(f"Accession number: {filing.accession_number}")

    # The original raw dict is always available.
    print(f"\nRaw keys: {list(filing.raw.keys())}")


# ---------------------------------------------------------------------------
# CompanyInfo model — via Company.get_info()
# ---------------------------------------------------------------------------

print("\n=== CompanyInfo Object ===")
info = company.get_info()

if info:
    print(info)
    # <CompanyInfo name='Apple Inc.' cik='320193' tickers=['AAPL']>

    # Typed property access.
    print(f"\nName:            {info.name}")
    print(f"CIK:             {info.cik}")
    print(f"Entity type:     {info.entity_type}")
    print(f"SIC:             {info.sic} — {info.sic_description}")
    print(f"Tickers:         {info.tickers}")
    print(f"Exchanges:       {info.exchanges}")
    print(f"Fiscal year end: {info.fiscal_year_end}")


# ---------------------------------------------------------------------------
# Recent filings as plain dicts (column-oriented → row-oriented)
# ---------------------------------------------------------------------------

if info:
    recent = info.recent_filings
    print(f"\n=== Recent Filings (dicts) — {len(recent)} total ===")
    for row in recent[:5]:
        print(
            f"  {row.get('form', ''):8s}  {row.get('filingDate', '')}  {row.get('primaryDocDescription', '')}"
        )


# ---------------------------------------------------------------------------
# Submission models — structured objects from recent filings
# ---------------------------------------------------------------------------

if info:
    submissions = info.recent_submissions
    print(f"\n=== Recent Submissions (models) — {len(submissions)} total ===")
    for sub in submissions[:5]:
        print(sub)
        # <Submission form='10-K' date='2024-11-01' accession='0000320193-24-000123'>

    # Access typed properties on a Submission.
    if submissions:
        sub = submissions[0]
        print(f"\nForm:              {sub.form}")
        print(f"Filing date:       {sub.filing_date}")
        print(f"Report date:       {sub.report_date}")
        print(f"Accession number:  {sub.accession_number}")
        print(f"Primary document:  {sub.primary_document}")
        print(f"Description:       {sub.primary_doc_description}")
        print(f"Is XBRL:           {sub.is_xbrl}")
        print(f"Is inline XBRL:    {sub.is_inline_xbrl}")
        print(f"Size:              {sub.size:,} bytes")

        # Raw dict access.
        print(f"\nRaw keys: {list(sub.raw.keys())}")


# ---------------------------------------------------------------------------
# Combine: get filings → download a document
# ---------------------------------------------------------------------------

print("\n=== Download via Filing model ===")
filings = company.get_filings(form="10-K")
if filings and filings[0].url:
    content = company.download(filings[0].url)
    print(f"Downloaded {len(content):,} characters from filing: {filings[0].form_type}")
