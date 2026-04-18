"""Example usage of the Fact and Facts XBRL dataclass models."""

from edgar.client import EdgarClient

# Initialize the client.
# SEC EDGAR requires a User-Agent in the format "Company/Name email@example.com".
edgar_client = EdgarClient(user_agent="Your Name your-email@example.com")


# ---------------------------------------------------------------------------
# Fetch XBRL facts for a company via the fluent Company interface
# ---------------------------------------------------------------------------

company = edgar_client.company("AAPL")

# get_facts() returns a Facts model wrapping the deeply nested company_facts JSON.
facts = company.get_facts()

print("=== Facts Overview ===")
print(facts)
# <Facts entity='Apple Inc.' cik=320193 taxonomies=['dei', 'us-gaap']>

print(f"\nEntity name: {facts.entity_name}")
print(f"CIK:         {facts.cik}")
print(f"Taxonomies:  {facts.taxonomies}")
# Output: Taxonomies: ['dei', 'us-gaap']


# ---------------------------------------------------------------------------
# Browse available concepts within a taxonomy
# ---------------------------------------------------------------------------

print("\n=== Concepts in us-gaap ===")
concepts = facts.concepts("us-gaap")
print(f"Total concepts: {len(concepts)}")
print(f"First 10:       {concepts[:10]}")
# Output: ['AccountsPayableCurrent', 'AccountsReceivableNetCurrent', ...]


# ---------------------------------------------------------------------------
# Retrieve Fact objects for a specific concept
# ---------------------------------------------------------------------------

print("\n=== Revenue Facts (us-gaap) ===")
revenue = facts.get("us-gaap", "Revenues", unit="USD")
print(f"Total data points: {len(revenue)}")

for fact in revenue[-5:]:
    print(fact)
    # <Fact end='2024-09-28' value=391035000000 form='10-K' fy=2024>

# Access typed properties on individual Fact objects.
if revenue:
    latest = revenue[-1]
    print("\nLatest revenue fact:")
    print(f"  End date:         {latest.end}")
    print(f"  Start date:       {latest.start}")
    print(f"  Value:            {latest.value:,}")
    print(f"  Form:             {latest.form}")
    print(f"  Filed:            {latest.filed}")
    print(f"  Fiscal year:      {latest.fiscal_year}")
    print(f"  Fiscal period:    {latest.fiscal_period}")
    print(f"  Accession number: {latest.accession_number}")
    print(f"  Frame:            {latest.frame}")

    # Raw dict is always available for any field not exposed as a property.
    print(f"  Raw keys:         {list(latest.raw.keys())}")


# ---------------------------------------------------------------------------
# Concept metadata — label, description, and available units
# ---------------------------------------------------------------------------

print("\n=== Concept Metadata ===")
label = facts.label("us-gaap", "Revenues")
desc = facts.description("us-gaap", "Revenues")
units = facts.units("us-gaap", "Revenues")

print(f"Label:       {label}")
print(f"Description: {desc[:100]}...")
print(f"Units:       {units}")
# Output: Units: ['USD']


# ---------------------------------------------------------------------------
# Filter by unit — get only share-denominated facts
# ---------------------------------------------------------------------------

print("\n=== Shares Outstanding ===")
shares = facts.get("us-gaap", "CommonStockSharesOutstanding", unit="shares")
print(f"Total data points: {len(shares)}")
for fact in shares[-3:]:
    print(f"  {fact.end}  {fact.value:>15,}  {fact.form}")


# ---------------------------------------------------------------------------
# Cross-taxonomy access — DEI (Document and Entity Information)
# ---------------------------------------------------------------------------

print("\n=== DEI Taxonomy ===")
dei_concepts = facts.concepts("dei")
print(f"DEI concepts: {len(dei_concepts)}")
print(f"Sample:       {dei_concepts[:5]}")

# EntityCommonStockSharesOutstanding from the dei taxonomy.
dei_shares = facts.get("dei", "EntityCommonStockSharesOutstanding")
if dei_shares:
    print(f"\nDEI shares outstanding ({len(dei_shares)} data points):")
    for fact in dei_shares[-3:]:
        print(f"  {fact.end}  {fact.value}  {fact.form}")
