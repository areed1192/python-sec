"""Structured response models wrapping raw SEC EDGAR dictionaries."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Filing:
    """A single SEC filing entry returned by the EDGAR search/browse feeds.

    Wraps the raw dictionary from ``parse_entries()`` and exposes common
    fields as typed properties. The original data is always available via
    the ``.raw`` attribute.

    ### Usage
    ----
        >>> filings = edgar_client.company("AAPL").filings(form="10-K")
        >>> filing = filings[0]
        >>> filing.form_type
        '10-K'
        >>> filing.url
        'https://www.sec.gov/Archives/edgar/data/320193/...'
    """

    raw: dict = field(repr=False)

    @property
    def title(self) -> str:
        """The filing title (e.g. ``'10-K - Annual report'``)."""
        return self.raw.get("title", "")

    @property
    def form_type(self) -> str:
        """The filing form type (e.g. ``'10-K'``, ``'10-Q'``, ``'8-K'``)."""
        return self.raw.get("category_term", "")

    @property
    def url(self) -> str:
        """The URL to the filing document on SEC EDGAR."""
        return self.raw.get("link_href", "")

    @property
    def summary(self) -> str:
        """A brief description of the filing."""
        return self.raw.get("summary", "")

    @property
    def filing_date(self) -> str:
        """The filing date as an ISO-8601 string."""
        return self.raw.get("updated", "")

    @property
    def accession_number(self) -> str:
        """The SEC accession number extracted from the entry ID."""
        entry_id = self.raw.get("id", "")
        if "accession-number=" in entry_id:
            return entry_id.split("accession-number=")[-1]
        return entry_id

    def __repr__(self) -> str:
        return f"<Filing form={self.form_type!r} date={self.filing_date[:10]!r} title={self.title!r}>"


@dataclass(frozen=True)
class CompanyInfo:
    """Company metadata from the SEC EDGAR submissions API.

    Wraps the raw dictionary from ``submissions.get_submissions()``
    and exposes common identification fields as typed properties.

    ### Usage
    ----
        >>> info = edgar_client.company("AAPL").get_info()
        >>> info.name
        'Apple Inc.'
        >>> info.cik
        '320193'
    """

    raw: dict = field(repr=False)

    @property
    def cik(self) -> str:
        """The CIK number as a string."""
        return str(self.raw.get("cik", ""))

    @property
    def name(self) -> str:
        """The company name as registered with the SEC."""
        return self.raw.get("name", "")

    @property
    def entity_type(self) -> str:
        """The entity type (e.g. ``'operating'``)."""
        return self.raw.get("entityType", "")

    @property
    def sic(self) -> str:
        """The Standard Industrial Classification (SIC) code."""
        return str(self.raw.get("sic", ""))

    @property
    def sic_description(self) -> str:
        """The human-readable SIC industry description."""
        return self.raw.get("sicDescription", "")

    @property
    def tickers(self) -> list[str]:
        """The stock ticker symbol(s)."""
        return self.raw.get("tickers", [])

    @property
    def exchanges(self) -> list[str]:
        """The stock exchange(s) (e.g. ``['NASDAQ']``)."""
        return self.raw.get("exchanges", [])

    @property
    def fiscal_year_end(self) -> str:
        """The fiscal year-end month and day (e.g. ``'1231'`` for Dec 31)."""
        return self.raw.get("fiscalYearEnd", "")

    @property
    def recent_filings(self) -> list[dict]:
        """The recent filings as a list of row-dicts (one per filing).

        Transforms the SEC's column-oriented format into a more usable
        row-oriented list of dictionaries.
        """
        filings_data = self.raw.get("filings", {})
        recent = filings_data.get("recent", {})
        if not recent:
            return []

        keys = list(recent.keys())
        if not keys:
            return []

        num_rows = len(recent[keys[0]])
        return [
            {key: recent[key][i] for key in keys}
            for i in range(num_rows)
        ]

    @property
    def recent_submissions(self) -> list[Submission]:
        """The recent filings as structured ``Submission`` model objects.

        Same data as ``recent_filings`` but wrapped in ``Submission``
        dataclass instances for typed property access.
        """
        return [Submission(raw=row) for row in self.recent_filings]

    def __repr__(self) -> str:
        ticker_str = ", ".join(self.tickers[:3]) if self.tickers else "N/A"
        return f"<CompanyInfo name={self.name!r} cik={self.cik!r} tickers={ticker_str!r}>"


@dataclass(frozen=True)
class Submission:
    """A single filing record from the submissions API ``recent`` array.

    Wraps one row from the column-oriented ``filings.recent`` structure
    after it has been converted into a flat dictionary.

    ### Usage
    ----
        >>> info = edgar_client.company("AAPL").get_info()
        >>> sub = info.recent_submissions[0]
        >>> sub.form
        '10-K'
        >>> sub.filing_date
        '2021-01-28'
    """

    raw: dict = field(repr=False)

    @property
    def accession_number(self) -> str:
        """The SEC accession number."""
        return self.raw.get("accessionNumber", "")

    @property
    def form(self) -> str:
        """The filing form type (e.g. ``'10-K'``, ``'10-Q'``)."""
        return self.raw.get("form", "")

    @property
    def filing_date(self) -> str:
        """The date the filing was submitted."""
        return self.raw.get("filingDate", "")

    @property
    def report_date(self) -> str:
        """The reporting period end date."""
        return self.raw.get("reportDate", "")

    @property
    def primary_document(self) -> str:
        """The filename of the primary document."""
        return self.raw.get("primaryDocument", "")

    @property
    def primary_doc_description(self) -> str:
        """Description of the primary document."""
        return self.raw.get("primaryDocDescription", "")

    @property
    def is_xbrl(self) -> bool:
        """Whether the filing contains XBRL data."""
        return bool(self.raw.get("isXBRL", 0))

    @property
    def is_inline_xbrl(self) -> bool:
        """Whether the filing uses inline XBRL."""
        return bool(self.raw.get("isInlineXBRL", 0))

    @property
    def size(self) -> int:
        """The filing size in bytes."""
        return self.raw.get("size", 0)

    def __repr__(self) -> str:
        return f"<Submission form={self.form!r} date={self.filing_date!r} accession={self.accession_number!r}>"
