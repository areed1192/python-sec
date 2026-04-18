# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- **edgar/models.py**: `Fact` and `Facts` XBRL dataclass models.
  - `Facts` wraps the deeply nested `company_facts` JSON (4 levels) with `get(taxonomy, concept, unit=None)` returning a flat `list[Fact]` sorted by end date.
  - `Facts.taxonomies` lists available namespaces (e.g. `['dei', 'us-gaap', 'ifrs-full']`).
  - `Facts.concepts(taxonomy)` lists concept names within a taxonomy.
  - `Facts.label()`, `Facts.description()`, `Facts.units()` for concept metadata.
  - `Fact` wraps a single data point with `value`, `end`, `start`, `fiscal_year`, `fiscal_period`, `form`, `filed`, `frame` properties.
- **xbrl.py**: `get_facts(cik)` method returning a structured `Facts` model.
- **company.py**: `get_facts()` method returning a structured `Facts` model.
- **tests/test_xbrl_facts.py**: 39 unit tests for `Fact`, `Facts`, `Company.get_facts()`, `Xbrl.get_facts()`, and taxonomy parameter support.

### Changed

- **xbrl.py**: `company_concepts()` and `frames()` now accept an optional `taxonomy` parameter (default `"us-gaap"`). Previously hardcoded to `us-gaap`, now supports `"ifrs-full"`, `"dei"`, or any other taxonomy.
- **edgar/tickers.py**: New `Tickers` service for ticker/CIK/company name resolution via `sec.gov/files/company_tickers.json`.
  - `resolve_ticker("AAPL")` → zero-padded CIK string (`"0000320193"`).
  - `resolve_cik(320193)` → list of company entries (ticker, title, CIK).
  - `search("Apple")` → case-insensitive fuzzy search across tickers and company names.
  - Data is fetched once and cached in memory for the session lifetime.
- **session.py**: `download(url, path=None)` method to fetch filing documents (HTML, XML, PDF) from any SEC URL. Auto-detects text vs binary content. Optional `path` parameter saves directly to file.
- **client.py**: Convenience methods `resolve_ticker()`, `resolve_cik()`, `tickers()`, and `download()` on `EdgarClient`.
- **samples/use_tickers_and_download.py**: Sample file demonstrating ticker resolution, company search, and filing download.
- **tests/test_tickers.py**: 14 unit tests for the `Tickers` service (resolve, reverse lookup, search, caching, error handling).
- **tests/test_download.py**: 9 unit tests for `download()` (text/binary content, save-to-file, error handling, client delegation).
- **edgar/company.py**: New fluent `Company` class for ticker-based SEC EDGAR access.
  - `client.company("AAPL")` resolves ticker or CIK → `Company` object with `cik`, `ticker`, `name` properties.
  - `company.filings(form="10-K")` — fluent chaining to get filings without separate service objects.
  - `company.submissions()` — fetch full submission history.
  - `company.xbrl_facts()` — fetch XBRL company facts.
  - `company.download(url)` — download filing documents.
  - Accepts both ticker symbols (`"AAPL"`) and CIK numbers (`"320193"`).
- **client.py**: `company()` method on `EdgarClient` for fluent company access. Existing `filings()` / `companies()` methods remain for backward compatibility.
- **tests/test_company.py**: 21 unit tests for the `Company` class (construction, properties, fluent methods, client integration, backward compat).
- **edgar/models.py**: New structured dataclass response models — `Filing`, `CompanyInfo`, `Submission`.
  - `Filing` wraps filing search result dicts with `form_type`, `filing_date`, `url`, `accession_number`, `title`, `summary` properties.
  - `CompanyInfo` wraps submissions metadata with `name`, `cik`, `tickers`, `sic`, `sic_description`, `recent_filings`, `recent_submissions` properties.
  - `Submission` wraps individual filing records with `form`, `filing_date`, `accession_number`, `report_date`, `is_xbrl`, `size` properties.
  - All models expose `.raw` attribute for backward compatibility with raw dict access.
  - All models are frozen (immutable) with `__repr__` for REPL/notebook discoverability.
- **company.py**: `get_filings(form=None)` → `list[Filing]` and `get_info()` → `CompanyInfo` convenience methods returning structured models.
- **tests/test_models.py**: 23 unit tests for all three models and the Company integration methods.
- **README.md**: Complete rewrite with hero example, full service table (15 services), usage examples for ticker resolution, fluent Company API, XBRL, filing search, downloads, response models, and badge row.
- **samples/use_company.py**: Sample file demonstrating the fluent Company interface (creation by ticker/CIK, filings, submissions, XBRL, download).
- **samples/use_models.py**: Sample file demonstrating structured dataclass response models (`Filing`, `CompanyInfo`, `Submission`).
- **samples/use_xbrl_facts.py**: Sample file demonstrating `Facts` and `Fact` XBRL dataclass models (taxonomy browsing, concept retrieval, unit filtering, metadata, cross-taxonomy access).
- **tests/test_rate_limiter.py**: 9 unit tests for the sliding-window rate limiter (under-limit, at-limit sleep, timestamp expiry, integration checks for all three request paths).

### Changed

- **session.py**: Replaced counter-based rate limiter (`sleep 5s every 10 requests`) with a sliding-window algorithm using `collections.deque` of `time.monotonic()` timestamps. Sleeps only the minimum time needed when the 1-second window is full. `MAX_REQUESTS_PER_SECOND = 10` enforced per SEC policy.
- **session.py**: Rate limiting now applies to all three outgoing request paths (`make_request()`, `fetch_page()`, `download()`). Previously `fetch_page()` and `download()` bypassed rate limiting entirely.

### Changed

- Migrated from `setup.py` to `pyproject.toml` for modern packaging.
- Relaxed dependency version pins to use minimum ranges instead of exact versions.
- Updated minimum Python version to 3.9.
- Excluded `samples/` and `tests/` from distributed package.

### Fixed

- **enums.py**: Renamed `StateCodes` members from mixed-case (`Alabama`, `New_York`) to UPPER_CASE (`ALABAMA`, `NEW_YORK`) to follow Python enum naming conventions.
- **utils.py**: Exception chaining — `except ValueError as exc` / `raise ... from exc` in `parse_dates`.
- **session.py**: Replaced infinite retry loop with bounded retry (max 5) and exponential backoff.
- **session.py**: Broadened exception handling from `HTTPError` to `RequestException` to catch connection and timeout errors.
- **session.py**: Reuse a single `requests.Session` with connection pooling instead of creating a new session per request.
- **session.py**: Added `application/json` content-type handler so JSON API responses are returned correctly.
- **session.py**: Changed rate-limit check from `== 9` to `>= RATE_LIMIT_INTERVAL` to prevent missed triggers.
- **session.py**: Replaced `print()` calls with `logging` module.
- **session.py**: Removed dead code that caused `SyntaxError`.
- **session.py**: Now raises `EdgarRequestError` instead of raw `requests` exceptions.
- **parser.py**: Replaced `ET.fromstring()` with `defusedxml.ElementTree.fromstring()` to prevent XXE attacks.
- **parser.py**: Routed all HTTP requests through a shared session with the required SEC `User-Agent` header.
- **parser.py**: Replaced `print()` calls with `logging` module.
- **parser.py**: Now raises `EdgarParseError` on XML parse failures instead of raw `ET.ParseError`.
- **submissions.py**: Added CIK input validation (`isdigit()`) to prevent path traversal.
- **xbrl.py**: Added CIK input validation (`isdigit()`) in `company_concepts` and `company_facts`.
- **utilis.py**: `parse_dates` now raises `ValueError` on invalid date strings instead of silently returning `None`.
- **Service methods**: All 26 methods across 7 service files now use `try/finally` to ensure `_reset_params()` cleanup on errors.
- **session.py**: Typed `client` parameter as `EdgarClient` (forward reference) instead of `object`; `make_request` return type now `Union[dict, str, None]`.
- **14 service/utility files**: Added `from __future__ import annotations` and corrected all return type annotations to match actual return values (`list[dict]`, `dict | None`, PEP 604 syntax).
- **parser.py**: Added `from __future__ import annotations`; replaced `List[Dict]`/`List[str]` with `list[dict]`/`list[str]`; fixed `_grab_next_page` return type to `ET.Element | None`, `_parse_issuer_next_button` to `str | None`.
- **archives.py**: Removed redundant `.format()` call on f-string in `get_company_directory`.
- **session.py**: Removed unused `pathlib`, `sys` imports and log directory creation + `logging.basicConfig()` calls (libraries should not configure logging).
- **6 service classes**: Filled in empty class-level docstrings (`Archives`, `CurrentEvents`, `Issuers`, `Series`, `OwnershipFilings`, `VariableInsuranceProducts`).
- **15 files**: Standardized all 120 docstring section headings — `### Arguments:` → `### Parameters`, removed trailing colons from `### Returns:`, `### Usage:`, `### Overview:`.
- **README.md**: Removed duplicate "Setup - PyPi Install" and "Setup - PyPi Upgrade" sections.
- **client.py**: Service factory methods now cache instances (lazy-init) so repeated calls return the same object.
- **All service files**: Replaced mutable `self.params` instance state with local `params` dicts in every method, removing `_reset_params()` entirely. Fixes thread-safety and state-leak bugs.
- **session.py**: Now creates shared `EdgarParser` and `EdgarUtilities` instances; all services reference these instead of creating their own.
- **parser.py**: Removed direct HTTP calls (`requests`/`urllib3` imports); pagination now uses a `fetch_page` callback injected by the caller. Session provides `fetch_page()` method.
- **utilis.py → utils.py**: Renamed module from `utilis.py` to `utils.py` (typo fix); updated import in `session.py`.
- **companies.py**: Fixed "Comapnies" typo → "Companies" in `__repr__` and `__init__` docstring.
- **samples/**: Added module docstrings to all 13 sample files.
- **samples/use_client.py**: Fixed "Initalize" typo → "Initialize"; removed unused imports (`pprint`, `date`, `FilingTypeCodes`).
- **samples/use_issuers_service.py**: Removed unused imports (`StateCodes`, `CountryCodes`, `StandardIndustrialClassificationCodes`).
- **samples/use_company_service.py**: Sorted imports alphabetically; updated `StateCodes.West_Virginia` → `StateCodes.WEST_VIRGINIA`.
- **All examples**: Updated `EdgarClient()` → `EdgarClient(user_agent=...)` across 13 sample files, README.md, test file, and 55 docstring examples in 14 `edgar/` modules to reflect the required `user_agent` parameter.

### Removed

- **`edgar/parser/xbrl.py`**: Deleted `XbrlFiling` stub class — never imported or referenced.
- **`edgar/parser/`**: Removed empty directory that conflicted with `parser.py` module.
- **`edgar/enums.py`**: Replaced monolithic 1581-line file with `edgar/enums/` package — one module per enum class (`state_codes.py`, `country_codes.py`, `filing_type_codes.py`, `sic_codes.py`, `other_filing_types.py`) plus `__init__.py` re-exporting all names. All existing `from edgar.enums import X` imports continue to work.

### Added

- `py.typed` marker for PEP 561 type checker support.
- `CHANGELOG.md` to track version history.
- `.gitignore` file.
- `defusedxml>=0.7.1` dependency for safe XML parsing.
- `edgar/exceptions.py` module with `EdgarError`, `EdgarRequestError`, `EdgarParseError` custom exceptions.
- `edgar/__init__.py` with public API exports (`from edgar import EdgarClient`).
- `tests/conftest.py` with shared fixtures (`edgar_client`, `edgar_session`, `edgar_parser`, `edgar_utilities`) and sample data constants (Atom feeds, JSON submissions, XBRL facts, directory listings).
- `tests/test_parser.py` — 12 unit tests for `EdgarParser` covering `parse_entries`, pagination, `check_for_next_page`, and `parse_entry_element`.
- `tests/test_services.py` — 17 mocked HTTP tests for session URL building, `make_request`, and service methods (companies, submissions, XBRL, archives, filings).
- `tests/test_utils.py` — 13 tests for `parse_dates`, `clean_directories`, and `clean_filing_directory`.
- `.github/workflows/ci.yml` — GitHub Actions CI workflow testing Python 3.9–3.13 on push/PR to master.
- **Test class rename**: `Edg` → `TestEdgarClient` in `test_edgar_client.py`.

## [0.1.6] - 2021-01-01

### Added

- Initial public release.
- EDGAR client with services: Archives, Companies, CurrentEvents, Datasets, Filings, Issuers, MutualFunds, OwnershipFilings, Series, Submissions, VariableInsuranceProducts, XBRL.
