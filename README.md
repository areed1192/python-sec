# Python SEC

[![PyPI version](https://img.shields.io/pypi/v/python-sec.svg)](https://pypi.org/project/python-sec/)
[![Python versions](https://img.shields.io/pypi/pyversions/python-sec.svg)](https://pypi.org/project/python-sec/)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

A lightweight Python client for the SEC EDGAR API. Look up companies by ticker, search filings, download documents, and query XBRL financial data — all in a few lines of code.

## Quick Start

```bash
pip install python-sec
```

```python
from edgar.client import EdgarClient

# SEC requires a User-Agent identifying you.
client = EdgarClient(user_agent="Your Name your-email@example.com")

# Look up Apple's 10-K filings — by ticker, no CIK needed.
company = client.company("AAPL")
filings = company.get_filings(form="10-K")

print(filings[0])
# <Filing form='10-K' date='2024-11-01' title='10-K - Annual report ...'>

# Get structured company metadata.
info = company.get_info()
print(info.name, info.tickers, info.sic_description)
# Apple Inc. ['AAPL'] ELECTRONIC COMPUTERS

# Access XBRL facts.
facts = company.xbrl_facts()
```

## Installation

```bash
pip install python-sec          # from PyPI
pip install --upgrade python-sec  # upgrade
pip install -e .                 # local dev (editable mode)
```

## Services

| Service                | Access                                 | Description                                                |
| ---------------------- | -------------------------------------- | ---------------------------------------------------------- |
| **Company**            | `client.company("AAPL")`               | Fluent interface — ticker/CIK → filings, submissions, XBRL |
| **Tickers**            | `client.resolve_ticker("AAPL")`        | Resolve tickers ↔ CIK numbers, search by company name      |
| **Filings**            | `client.filings()`                     | Search filings by CIK, form type, date range, company name |
| **Companies**          | `client.companies()`                   | Query companies by state, country, SIC code, name          |
| **Submissions**        | `client.submissions()`                 | Full filing history for any entity via the REST API        |
| **XBRL**               | `client.xbrl()`                        | Company facts, concepts, and cross-company frames          |
| **Archives**           | `client.archives()`                    | Browse EDGAR archive directories                           |
| **Current Events**     | `client.current_events()`              | Recent RSS filing feeds                                    |
| **Datasets**           | `client.datasets()`                    | DERA financial datasets                                    |
| **Issuers**            | `client.issuers()`                     | Issuer information                                         |
| **Mutual Funds**       | `client.mutual_funds()`                | Mutual fund filings                                        |
| **Series**             | `client.series()`                      | Investment company series                                  |
| **Ownership Filings**  | `client.ownership_filings()`           | Insider ownership (Forms 3/4/5)                            |
| **Variable Insurance** | `client.variable_insurance_products()` | Variable insurance product filings                         |
| **Download**           | `client.download(url)`                 | Fetch any filing document (HTML, XML, PDF)                 |

## Usage Examples

### Ticker Resolution

```python
# Ticker → CIK
cik = client.resolve_ticker("MSFT")  # "0000789019"

# CIK → company info
entries = client.resolve_cik("789019")
# [{'cik_str': 789019, 'ticker': 'MSFT', 'title': 'MICROSOFT CORP'}]

# Search by company name
results = client.tickers().search("Tesla")
```

### Company Research (Fluent API)

```python
company = client.company("META")

# Structured Filing objects with typed properties.
filings = company.get_filings(form="10-K")
for f in filings[:3]:
    print(f.form_type, f.filing_date[:10], f.url)

# Structured CompanyInfo with typed properties.
info = company.get_info()
print(info.name, info.sic_description, info.fiscal_year_end)

# Recent submissions as Submission objects.
for sub in info.recent_submissions[:5]:
    print(sub.form, sub.filing_date, sub.accession_number)
```

### Filing Search

```python
filings_service = client.filings()

# By CIK
filings_service.get_filings_by_cik(cik="320193")

# By form type
filings_service.get_filings_by_type(cik="320193", filing_type="10-K")

# Complex query with date range
filings_service.query(
    cik="320193",
    filing_type="10-Q",
    after_date="2023-01-01",
    before_date="2024-01-01",
)
```

### XBRL Financial Data

```python
xbrl = client.xbrl()

# All facts for a company.
facts = xbrl.company_facts(cik="320193")

# A single concept across time.
revenue = xbrl.company_concepts(cik="320193", concept="us-gaap/Revenue")

# Cross-company comparison for a single period.
frame = xbrl.frames(taxonomy="us-gaap", concept="AccountsPayableCurrent", uom="USD", period="CY2023Q1I")
```

### Download Filing Documents

```python
# Download as text.
html = client.download("https://www.sec.gov/Archives/edgar/data/320193/filing.htm")

# Download and save to file.
client.download("https://www.sec.gov/Archives/edgar/data/320193/filing.htm", path="filing.html")

# Download through the Company interface.
company = client.company("AAPL")
filings = company.get_filings(form="10-K")
content = company.download(filings[0].url)
```

## Response Models

The library provides structured dataclass models alongside raw dictionary access:

| Model         | Wraps                     | Key Properties                                                            |
| ------------- | ------------------------- | ------------------------------------------------------------------------- |
| `Filing`      | Filing search results     | `form_type`, `filing_date`, `url`, `accession_number`, `title`, `summary` |
| `CompanyInfo` | Submissions metadata      | `name`, `cik`, `tickers`, `sic`, `sic_description`, `recent_submissions`  |
| `Submission`  | Individual filing records | `form`, `filing_date`, `accession_number`, `report_date`, `is_xbrl`       |

All models expose a `.raw` attribute containing the original dictionary for backward compatibility.

## Support These Projects

**Patreon:**
Help support this project and future projects by donating to my [Patreon Page](https://www.patreon.com/sigmacoding). I'm
always looking to add more content for individuals like yourself, unfortunately some of the APIs would require me to
pay monthly fees.

**YouTube:**
If you'd like to watch more of my content, feel free to visit my YouTube channel [Sigma Coding](https://www.youtube.com/c/SigmaCoding).

**Questions:**
If you have questions please feel free to reach out to me at [coding.sigma@gmail.com](mailto:coding.sigma@gmail.com?subject=[GitHub]%20Fred%20Library)
