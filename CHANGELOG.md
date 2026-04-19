# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed

- **edgar/\_\_init\_\_.py**: Added `NullHandler` to the `edgar` logger — follows Python library logging best practice so applications control log output.
- **edgar/session.py**: Downgraded per-request URL, parameter, and rate-limit sleep logs from `info` to `debug`.
- **edgar/async_session.py**: Same `info` → `debug` log-level fix as `session.py`.
- **edgar/parser.py**: Downgraded pagination URL and entry-count logs from `info` to `debug`.
- **edgar/client.py**: Added `logger` — logs `debug` on init (rate_limit, cache settings).
- **edgar/cache.py**: Added `logger` — logs `debug` on cache hit, miss, expired, set, and invalidate.
- **edgar/tickers.py**: Added `debug` logging for cache hit/miss and successful resolution; `warning` on failed ticker/CIK lookup.
- **edgar/submissions.py**: Added `logger` — logs `debug` on submissions cache hit.
- **edgar/xbrl.py**: Added `logger` — logs `debug` on company_facts cache hit.
- **edgar/datasets.py**: Added `logger` — logs `info` on bulk download start, `debug` on per-file extraction with row counts.
- **edgar/search.py**: Added `logger` — logs `debug` with EFTS search params before request.
- **edgar/company.py**: Added `logger` — logs `debug` on identifier resolution path (CIK vs ticker).
- **edgar/async_session.py**: Added `logger.error()` before each `raise EdgarRequestError`, matching `session.py` pattern for consistent error observability.

### Added

- **tests/test_logging.py**: 7 unit tests for logging output (cache hit/miss/set/invalidate, session error, rate-limit sleep, async session error).

### Fixed

- **edgar/parser.py**: Changed `except KeyError` to `except IndexError` in ticker symbol extraction — `values[2]` is a list index, not a dict key.

### Removed

- **edgar/utilis.py**: Deleted dead duplicate of `utils.py` (nothing imported it).
- **edgar/parser.py**: Removed 3 commented-out `print()` debug lines.

## [0.2.0] - 2026-04-19

### Added

- **edgar/async_client.py**: `EdgarAsyncClient` — async counterpart of `EdgarClient` using `httpx`.
  - Same API surface with `await`: `resolve_ticker()`, `resolve_cik()`, `get_company_info()`, `get_filings()`, `get_facts()`, `search()`, `download()`.
  - Async context manager support (`async with EdgarAsyncClient(...) as client`).
  - Enables `asyncio.gather()` for concurrent requests in web apps and data pipelines.
- **edgar/async_session.py**: `EdgarAsyncSession` — async HTTP session with `httpx.AsyncClient`.
  - Sliding-window rate limiter using `asyncio.sleep()`.
  - Retry logic with exponential backoff on non-200 responses.
  - `make_request()`, `fetch_page()`, `download()`, `close()` coroutines.
- **pyproject.toml**: Added `[async]` optional dependency group (`pip install python-sec[async]`).
  - Requires `httpx>=0.28`.
- **edgar/\_\_init\_\_.py**: Exports `EdgarAsyncClient` from the top-level package.
- **tests/test_async_client.py**: 28 unit tests for async session and client (init, rate limiting, URL building, make_request, download, fetch_page, ticker/CIK resolution, search, context manager).
- **samples/use_async_client.py**: Sample demonstrating async client usage with concurrent requests.
- **edgar/datasets.py**: Bulk DERA financial statement dataset download and extraction.
  - `Datasets.get_financial_statements(year, quarter)` downloads quarterly ZIP from SEC DERA and returns parsed TSV data as `dict[str, list[dict]]` (keys: `sub`, `num`, `tag`, `pre`).
  - `Datasets.get_financial_statements_dataframes(year, quarter)` returns the same data as `dict[str, pandas.DataFrame]` (requires `pandas` optional dep).
  - Internal `_extract_tsv_zip()` helper handles ZIP extraction and tab-separated parsing.
- **tests/test_datasets.py**: 15 unit tests for bulk dataset download, extraction, DataFrame conversion, and error handling.
- **samples/use_dataset_service.py**: Added bulk financial statements sections demonstrating `get_financial_statements()` and DataFrame variant.
- **edgar/models.py**: `to_json()` and `to_csv()` serialization methods on all model classes (`Filing`, `CompanyInfo`, `Submission`, `Fact`, `Facts`, `SearchResult`).
  - `result.to_json(path=None, indent=2)` serializes to a JSON string; optionally writes to file.
  - `result.to_csv(path=None)` serializes to a CSV string (header + one row); optionally writes to file.
  - Module-level `to_json(items, path=None)` and `to_csv(items, path=None)` for serializing lists of models.
  - List/dict properties are JSON-encoded in CSV cells for lossless round-tripping.
- **tests/test_serialization.py**: 35 unit tests for JSON/CSV serialization (instance methods, module-level functions, file writing, edge cases).
- **samples/use_models.py**: Added JSON and CSV serialization sections demonstrating `to_json()` and `to_csv()`.
- **samples/cookbook_company_research.ipynb**: Cookbook notebook — company research workflow (ticker lookup, metadata, filings, XBRL facts, DataFrame export, multi-company comparison).
- **samples/cookbook_xbrl_analysis.ipynb**: Cookbook notebook — XBRL financial analysis (taxonomy browsing, concept retrieval, unit filtering, time-series DataFrames, frames cross-company comparison).
- **samples/cookbook_filing_search.ipynb**: Cookbook notebook — filing search & download (full-text search, form/date filters, pagination, document download, save to file).
- **samples/cookbook_bulk_pipeline.ipynb**: Cookbook notebook — bulk data pipeline (batch processing, multi-company aggregation, SEC datasets, rate limiting, caching, CSV export).
- **edgar/cache.py**: In-memory TTL cache for SEC EDGAR API responses.
  - `TTLCache` class with `get()`, `set()`, `invalidate()`, `clear()`, `__len__()`, `__repr__()`.
  - Uses `time.monotonic()` for expiration immune to wall-clock adjustments.
  - Module-level TTL constants: `TTL_TICKERS` (24h), `TTL_TAXONOMY` (24h), `TTL_SUBMISSIONS` (1h).
- **tests/test_cache.py**: 29 unit tests for `TTLCache` (get/set, expiration, invalidate, clear, len/repr, constants) and cache integration with `Tickers`, `Submissions`, and `Xbrl` services.
- **edgar/\_\_init\_\_.py**: Top-level convenience functions for reduced boilerplate.
  - `edgar.company("AAPL")` — create a `Company` without instantiating `EdgarClient`.
  - `edgar.get_filings("AAPL", form="10-K")` — fetch filings in one call.
  - `edgar.search("revenue recognition")` — full-text search in one call.
  - `edgar.set_user_agent()` — set user-agent programmatically.
  - `SEC_EDGAR_USER_AGENT` environment variable auto-detected as fallback.
  - Lazy singleton `EdgarClient` created on first use and cached.
- **tests/test_convenience.py**: 17 unit tests for convenience functions (`set_user_agent`, `_get_client`, `company`, `get_filings`, `search`, env var fallback, caching, exports).
- **samples/use_convenience.py**: Sample file demonstrating top-level convenience functions (env var, `set_user_agent`, `company`, `get_filings`, `search`).
- **edgar/models.py**: `Fact` and `Facts` XBRL dataclass models.
  - `Facts` wraps the deeply nested `company_facts` JSON (4 levels) with `get(taxonomy, concept, unit=None)` returning a flat `list[Fact]` sorted by end date.
  - `Facts.taxonomies` lists available namespaces (e.g. `['dei', 'us-gaap', 'ifrs-full']`).
  - `Facts.concepts(taxonomy)` lists concept names within a taxonomy.
  - `Facts.label()`, `Facts.description()`, `Facts.units()` for concept metadata.
  - `Fact` wraps a single data point with `value`, `end`, `start`, `fiscal_year`, `fiscal_period`, `form`, `filed`, `frame` properties.
- **xbrl.py**: `get_facts(cik)` method returning a structured `Facts` model.
- **company.py**: `get_facts()` method returning a structured `Facts` model.
- **tests/test_xbrl_facts.py**: 39 unit tests for `Fact`, `Facts`, `Company.get_facts()`, `Xbrl.get_facts()`, and taxonomy parameter support.
- **edgar/models.py**: `to_dataframe()` standalone function and `Facts.to_dataframe()` method for pandas integration.
  - `to_dataframe(items)` converts any list of model objects (`Filing`, `Fact`, `Submission`, `SearchResult`, `CompanyInfo`) to a `pandas.DataFrame`.
  - `Facts.to_dataframe(taxonomy, concept, unit=None)` returns fact data points as a DataFrame.
  - Graceful `ImportError` with message `"pip install python-sec[pandas]"` when pandas is not installed.
- **pyproject.toml**: `[pandas]` optional dependency group (`pandas>=2.0`).
- **tests/test_to_dataframe.py**: 20 unit tests for `to_dataframe()`, `Facts.to_dataframe()`, and graceful import error handling.
- **samples/use_dataframes.py**: Sample file demonstrating DataFrame conversion for facts, filings, search results, and submissions.

### Changed

- **edgar/client.py**: `EdgarClient` now accepts `rate_limit` parameter: `EdgarClient(user_agent="...", rate_limit=5)`.
  - Defaults to 10 (SEC's maximum). Validates range 1–10.
  - Passed through to `EdgarSession` for sliding-window enforcement.
- **edgar/client.py**: `EdgarClient` now accepts `cache` parameter (`bool`, default `True`).
  - `cache=True` creates a shared `TTLCache` passed to `EdgarSession`.
  - `cache=False` disables caching; all requests hit the network.
- **edgar/session.py**: `EdgarSession` accepts optional `cache` parameter storing a `TTLCache` instance.
- **edgar/tickers.py**: `Tickers._load()` checks/stores data in the TTL cache (`TTL_TICKERS`).
- **edgar/submissions.py**: `Submissions.get_submissions()` checks/stores responses in the TTL cache (`TTL_SUBMISSIONS`).
- **edgar/xbrl.py**: `Xbrl.company_facts()` checks/stores responses in the TTL cache (`TTL_TAXONOMY`).
- **tests/test_rate_limiter.py**: 8 new tests for configurable rate limit (custom values, boundary validation, client passthrough). Total: 17 tests.
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
- **edgar/search.py**: New `Search` service wrapping the EDGAR Full-Text Search (EFTS) endpoint at `efts.sec.gov/LATEST/search-index`.
  - `full_text_search(q, form_types=None, start_date=None, end_date=None, start=0, size=100)` — query filings by keyword, form type, and date range.
- **edgar/models.py**: `SearchResult` dataclass wrapping EFTS Elasticsearch hit dicts.
  - Properties: `company_name`, `cik`, `form`, `filing_date`, `accession_number`, `file_type`, `file_description`, `period_ending`, `url`.
  - URL constructed from `_id` field (`{adsh}:{filename}`) pointing to the full filing document on SEC.gov.
- **edgar/client.py**: `search()` convenience method and `full_text_search()` service accessor for EFTS search.
- **edgar/session.py**: `build_url()` and `make_request()` accept optional `base_url` parameter to support third-party SEC endpoints (e.g. `efts.sec.gov`).
- **tests/test_search.py**: 35 unit tests for `SearchResult` model, `Search` service, `EdgarClient.search()` integration, and `build_url` base_url parameter.
- **samples/use_search.py**: Sample file demonstrating full-text search (basic query, form type filtering, date ranges, result properties, pagination).
- **edgar/models.py**: `_repr_html_()` on all six response models for Jupyter/notebook rendering.
  - `Filing`, `CompanyInfo`, `Submission`, `Fact`, `Facts`, `SearchResult` auto-render as styled HTML tables.
  - Helper functions `_html_kv_table()`, `_html_row_table()`, `_esc()` for XSS-safe HTML generation.
  - Inline CSS constants (`_TABLE_STYLE`, `_TH_STYLE`, `_TD_STYLE`, `_CAPTION_STYLE`) for consistent styling across Jupyter Lab, Notebook, VS Code, and Colab.
- **tests/test_repr_html.py**: 35 unit tests for `_repr_html_()` on all models (HTML output, key values, XSS escaping, edge cases).
- **samples/demo_jupyter_rendering.ipynb**: Jupyter notebook demonstrating auto-rendering for all model types and DataFrame conversion.

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
