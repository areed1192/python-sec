"""Structured response models wrapping raw SEC EDGAR dictionaries."""

from __future__ import annotations

from dataclasses import dataclass, field
from html import escape as _html_escape


_TABLE_STYLE = (
    "border-collapse:collapse;font-family:monospace;font-size:13px;"
)
_TH_STYLE = (
    "text-align:left;padding:4px 10px;border:1px solid #ccc;"
    "background:#f4f4f4;font-weight:600;"
)
_TD_STYLE = "text-align:left;padding:4px 10px;border:1px solid #ccc;"
_CAPTION_STYLE = (
    "caption-side:top;text-align:left;font-weight:700;"
    "font-size:14px;padding-bottom:4px;"
)


def _html_kv_table(pairs: list[tuple[str, str]], caption: str = "") -> str:
    """Build an HTML key-value table (two columns: Field / Value)."""
    rows = "".join(
        f"<tr><th style=\"{_TH_STYLE}\">{_html_escape(str(k))}</th>"
        f"<td style=\"{_TD_STYLE}\">{v}</td></tr>"
        for k, v in pairs
    )
    cap = f"<caption style=\"{_CAPTION_STYLE}\">{_html_escape(caption)}</caption>" if caption else ""
    return f"<table style=\"{_TABLE_STYLE}\">{cap}{rows}</table>"


def _html_row_table(
    headers: list[str],
    rows: list[list[str]],
    caption: str = "",
) -> str:
    """Build an HTML table with column headers and multiple data rows."""
    hdr = "".join(f"<th style=\"{_TH_STYLE}\">{_html_escape(h)}</th>" for h in headers)
    body = ""
    for row in rows:
        cells = "".join(f"<td style=\"{_TD_STYLE}\">{v}</td>" for v in row)
        body += f"<tr>{cells}</tr>"
    cap = f"<caption style=\"{_CAPTION_STYLE}\">{_html_escape(caption)}</caption>" if caption else ""
    return f"<table style=\"{_TABLE_STYLE}\">{cap}<tr>{hdr}</tr>{body}</table>"


def _esc(value) -> str:
    """Escape a value for safe HTML display."""
    return _html_escape(str(value))


def _require_pandas():
    """Import and return the ``pandas`` module, raising a helpful error if missing."""
    try:
        import pandas as pd  # pylint: disable=import-outside-toplevel
        return pd
    except ImportError as exc:
        raise ImportError(
            "pandas is required for to_dataframe(). "
            "Install it with: pip install python-sec[pandas]"
        ) from exc


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

    def _repr_html_(self) -> str:
        url_cell = (
            f"<a href=\"{_esc(self.url)}\">{_esc(self.url)}</a>"
            if self.url else ""
        )
        return _html_kv_table(
            [
                ("Form Type", _esc(self.form_type)),
                ("Filing Date", _esc(self.filing_date[:10])),
                ("Accession #", _esc(self.accession_number)),
                ("Title", _esc(self.title)),
                ("Summary", _esc(self.summary)),
                ("URL", url_cell),
            ],
            caption="Filing",
        )


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
        return [{key: recent[key][i] for key in keys} for i in range(num_rows)]

    @property
    def recent_submissions(self) -> list[Submission]:
        """The recent filings as structured ``Submission`` model objects.

        Same data as ``recent_filings`` but wrapped in ``Submission``
        dataclass instances for typed property access.
        """
        return [Submission(raw=row) for row in self.recent_filings]

    def __repr__(self) -> str:
        ticker_str = ", ".join(self.tickers[:3]) if self.tickers else "N/A"
        return (
            f"<CompanyInfo name={self.name!r} cik={self.cik!r} tickers={ticker_str!r}>"
        )

    def _repr_html_(self) -> str:
        ticker_str = ", ".join(self.tickers) if self.tickers else "—"
        exchange_str = ", ".join(self.exchanges) if self.exchanges else "—"
        info = _html_kv_table(
            [
                ("Name", _esc(self.name)),
                ("CIK", _esc(self.cik)),
                ("Entity Type", _esc(self.entity_type)),
                ("SIC", f"{_esc(self.sic)} — {_esc(self.sic_description)}"),
                ("Tickers", _esc(ticker_str)),
                ("Exchanges", _esc(exchange_str)),
                ("Fiscal Year End", _esc(self.fiscal_year_end)),
            ],
            caption="Company Info",
        )
        subs = self.recent_submissions[:10]
        if subs:
            rows = [
                [
                    _esc(s.form),
                    _esc(s.filing_date),
                    _esc(s.accession_number),
                    _esc(s.primary_doc_description),
                ]
                for s in subs
            ]
            info += _html_row_table(
                ["Form", "Filing Date", "Accession #", "Description"],
                rows,
                caption=f"Recent Filings (showing {len(subs)})",
            )
        return info


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

    def _repr_html_(self) -> str:
        return _html_kv_table(
            [
                ("Form", _esc(self.form)),
                ("Filing Date", _esc(self.filing_date)),
                ("Report Date", _esc(self.report_date)),
                ("Accession #", _esc(self.accession_number)),
                ("Primary Document", _esc(self.primary_document)),
                ("Description", _esc(self.primary_doc_description)),
                ("XBRL", "Yes" if self.is_xbrl else "No"),
                ("Inline XBRL", "Yes" if self.is_inline_xbrl else "No"),
                ("Size", f"{self.size:,} bytes" if self.size else "—"),
            ],
            caption="Submission",
        )


@dataclass(frozen=True)
class Fact:
    """A single XBRL fact data point.

    Each fact represents one reported value for a specific concept,
    unit, and period.

    ### Usage
    ----
        >>> facts = edgar_client.company("AAPL").get_facts()
        >>> revenue = facts.get("us-gaap", "Revenue")
        >>> revenue[0].value
        274515000000
    """

    raw: dict = field(repr=False)

    @property
    def end(self) -> str:
        """The period end date."""
        return self.raw.get("end", "")

    @property
    def start(self) -> str:
        """The period start date (empty for instant facts)."""
        return self.raw.get("start", "")

    @property
    def value(self):
        """The reported numeric value."""
        return self.raw.get("val")

    @property
    def accession_number(self) -> str:
        """The filing accession number."""
        return self.raw.get("accn", "")

    @property
    def fiscal_year(self) -> int:
        """The fiscal year."""
        return self.raw.get("fy", 0)

    @property
    def fiscal_period(self) -> str:
        """The fiscal period (e.g. ``'FY'``, ``'Q1'``, ``'Q2'``)."""
        return self.raw.get("fp", "")

    @property
    def form(self) -> str:
        """The form type that reported this fact (e.g. ``'10-K'``)."""
        return self.raw.get("form", "")

    @property
    def filed(self) -> str:
        """The date the filing was submitted."""
        return self.raw.get("filed", "")

    @property
    def frame(self) -> str:
        """The XBRL frame identifier (e.g. ``'CY2020Q4I'``), if present."""
        return self.raw.get("frame", "")

    def __repr__(self) -> str:
        return (
            f"<Fact end={self.end!r} value={self.value!r}"
            f" form={self.form!r} fy={self.fiscal_year}>"
        )

    def _repr_html_(self) -> str:
        val = f"{self.value:,}" if isinstance(self.value, (int, float)) else _esc(self.value)
        return _html_kv_table(
            [
                ("End", _esc(self.end)),
                ("Start", _esc(self.start)),
                ("Value", val),
                ("Form", _esc(self.form)),
                ("Filed", _esc(self.filed)),
                ("Fiscal Year", _esc(self.fiscal_year)),
                ("Fiscal Period", _esc(self.fiscal_period)),
                ("Frame", _esc(self.frame)),
            ],
            caption="Fact",
        )


@dataclass(frozen=True)
class Facts:
    """Structured wrapper around the SEC EDGAR company_facts XBRL response.

    Navigates the deeply nested ``facts`` JSON (4 levels deep) and
    provides convenient access by taxonomy and concept name.

    ### Usage
    ----
        >>> facts = edgar_client.company("AAPL").get_facts()
        >>> facts.entity_name
        'Apple Inc.'
        >>> revenue = facts.get("us-gaap", "Revenues")
        >>> revenue[0].value
        274515000000
        >>> facts.taxonomies
        ['dei', 'us-gaap']
        >>> facts.concepts("us-gaap")
        ['AccountsPayableCurrent', 'AccountsReceivableNetCurrent', ...]
    """

    raw: dict = field(repr=False)

    @property
    def cik(self) -> int:
        """The CIK number."""
        return self.raw.get("cik", 0)

    @property
    def entity_name(self) -> str:
        """The entity name as reported in XBRL."""
        return self.raw.get("entityName", "")

    @property
    def taxonomies(self) -> list[str]:
        """List of taxonomy namespaces present (e.g. ``['dei', 'us-gaap']``)."""
        return list(self.raw.get("facts", {}).keys())

    def concepts(self, taxonomy: str = "us-gaap") -> list[str]:
        """List of concept names within a taxonomy.

        ### Parameters
        ----
        taxonomy : str (optional, Default=``"us-gaap"``)
            The taxonomy namespace.

        ### Returns
        ----
        list[str]:
            Sorted list of concept names.
        """
        return sorted(self.raw.get("facts", {}).get(taxonomy, {}).keys())

    def get(
        self,
        taxonomy: str,
        concept: str,
        unit: str | None = None,
    ) -> list[Fact]:
        """Retrieves fact data points for a given taxonomy/concept pair.

        ### Parameters
        ----
        taxonomy : str
            The taxonomy namespace (e.g. ``"us-gaap"``, ``"dei"``,
            ``"ifrs-full"``).

        concept : str
            The concept tag name (e.g. ``"Revenue"``,
            ``"AccountsPayableCurrent"``).

        unit : str | None (optional, Default=None)
            If provided, returns only facts in this unit of measure
            (e.g. ``"USD"``, ``"shares"``). If ``None``, returns
            facts from all units combined.

        ### Returns
        ----
        list[Fact]:
            A flat list of ``Fact`` objects, sorted by end date.
        """
        concept_data = self.raw.get("facts", {}).get(taxonomy, {}).get(concept, {})
        if not concept_data:
            return []

        units_data = concept_data.get("units", {})

        results: list[dict] = []
        if unit is not None:
            results = units_data.get(unit, [])
        else:
            for entries in units_data.values():
                results.extend(entries)

        results.sort(key=lambda d: d.get("end", ""))
        return [Fact(raw=entry) for entry in results]

    def label(self, taxonomy: str, concept: str) -> str:
        """Returns the human-readable label for a concept.

        ### Parameters
        ----
        taxonomy : str
            The taxonomy namespace.

        concept : str
            The concept tag name.

        ### Returns
        ----
        str:
            The label string, or empty string if not found.
        """
        return (
            self.raw.get("facts", {})
            .get(taxonomy, {})
            .get(concept, {})
            .get("label", "")
        )

    def description(self, taxonomy: str, concept: str) -> str:
        """Returns the description for a concept.

        ### Parameters
        ----
        taxonomy : str
            The taxonomy namespace.

        concept : str
            The concept tag name.

        ### Returns
        ----
        str:
            The description string, or empty string if not found.
        """
        return (
            self.raw.get("facts", {})
            .get(taxonomy, {})
            .get(concept, {})
            .get("description", "")
        )

    def units(self, taxonomy: str, concept: str) -> list[str]:
        """Returns the available units of measure for a concept.

        ### Parameters
        ----
        taxonomy : str
            The taxonomy namespace.

        concept : str
            The concept tag name.

        ### Returns
        ----
        list[str]:
            List of unit names (e.g. ``["USD", "USD-per-shares"]``).
        """
        return list(
            self.raw.get("facts", {})
            .get(taxonomy, {})
            .get(concept, {})
            .get("units", {})
            .keys()
        )

    def to_dataframe(
        self,
        taxonomy: str,
        concept: str,
        unit: str | None = None,
    ):
        """Returns fact data points as a pandas DataFrame.

        Requires the ``pandas`` optional dependency. Install with
        ``pip install python-sec[pandas]``.

        ### Parameters
        ----
        taxonomy : str
            The taxonomy namespace (e.g. ``"us-gaap"``).

        concept : str
            The concept tag name (e.g. ``"Revenues"``).

        unit : str | None (optional, Default=None)
            If provided, filter to a specific unit of measure.

        ### Returns
        ----
        pandas.DataFrame:
            DataFrame with columns: ``end``, ``start``, ``value``,
            ``form``, ``filed``, ``fiscal_year``, ``fiscal_period``,
            ``accession_number``, ``frame``.
        """
        pd = _require_pandas()
        facts = self.get(taxonomy, concept, unit=unit)
        return to_dataframe(facts) if facts else pd.DataFrame()

    def __repr__(self) -> str:
        tax_count = len(self.taxonomies)
        total = sum(len(self.concepts(t)) for t in self.taxonomies)
        return (
            f"<Facts entity={self.entity_name!r} cik={self.cik}"
            f" taxonomies={tax_count} concepts={total}>"
        )

    def _repr_html_(self) -> str:
        info = _html_kv_table(
            [
                ("Entity", _esc(self.entity_name)),
                ("CIK", _esc(self.cik)),
                ("Taxonomies", _esc(", ".join(self.taxonomies))),
            ],
            caption="Facts",
        )
        rows = [
            [_esc(t), str(len(self.concepts(t)))]
            for t in self.taxonomies
        ]
        if rows:
            info += _html_row_table(
                ["Taxonomy", "Concepts"],
                rows,
                caption="Taxonomy Summary",
            )
        return info


@dataclass(frozen=True)
class SearchResult:
    """A single EDGAR full-text search (EFTS) hit.

    Wraps a raw Elasticsearch hit dict (including ``_id``, ``_score``,
    and ``_source``) from the ``efts.sec.gov`` search-index endpoint.

    ### Usage
    ----
        >>> results = edgar_client.search(q="revenue recognition", form_types=["10-K"])
        >>> results[0].company_name
        'Apple Inc.  (AAPL)  (CIK 0000320193)'
        >>> results[0].url
        'https://www.sec.gov/Archives/edgar/data/320193/...'
    """

    raw: dict = field(repr=False)

    @property
    def _source(self) -> dict:
        """The ``_source`` sub-dict from the Elasticsearch hit."""
        return self.raw.get("_source", {})

    @property
    def company_name(self) -> str:
        """The display name of the first filer (e.g. ``'Apple Inc.  (AAPL)  (CIK 0000320193)'``)."""
        names = self._source.get("display_names", [])
        return names[0] if names else ""

    @property
    def cik(self) -> str:
        """The CIK of the first filer."""
        ciks = self._source.get("ciks", [])
        return ciks[0] if ciks else ""

    @property
    def form(self) -> str:
        """The specific form type (e.g. ``'10-K'``, ``'10-K/A'``)."""
        return self._source.get("form", "")

    @property
    def filing_date(self) -> str:
        """The filing date (``YYYY-MM-DD``)."""
        return self._source.get("file_date", "")

    @property
    def accession_number(self) -> str:
        """The accession number with dashes (e.g. ``'0001193125-24-047930'``)."""
        return self._source.get("adsh", "")

    @property
    def file_type(self) -> str:
        """The document type within the filing (e.g. ``'10-K'``, ``'EX-99.1'``)."""
        return self._source.get("file_type", "")

    @property
    def file_description(self) -> str:
        """The human-readable description of the document."""
        return self._source.get("file_description", "") or ""

    @property
    def period_ending(self) -> str:
        """The fiscal period end date (``YYYY-MM-DD``)."""
        return self._source.get("period_ending", "")

    @property
    def url(self) -> str:
        """Constructs the filing document URL from the hit ID.

        The Elasticsearch ``_id`` is ``{accession}:{filename}`` which
        maps to ``https://www.sec.gov/Archives/edgar/data/{cik}/{accession_no_dashes}/{filename}``.
        """
        hit_id = self.raw.get("_id", "")
        cik = self.cik.lstrip("0") or "0"
        adsh = self.accession_number
        adsh_clean = adsh.replace("-", "")

        parts = hit_id.split(":", 1)
        filename = parts[1] if len(parts) > 1 else ""

        if not adsh_clean or not filename:
            return ""

        return f"https://www.sec.gov/Archives/edgar/data/{cik}/{adsh_clean}/{filename}"

    def __repr__(self) -> str:
        return (
            f"<SearchResult form={self.form!r} date={self.filing_date!r}"
            f" company={self.company_name!r}>"
        )

    def _repr_html_(self) -> str:
        url_cell = (
            f"<a href=\"{_esc(self.url)}\">{_esc(self.url)}</a>"
            if self.url else ""
        )
        return _html_kv_table(
            [
                ("Company", _esc(self.company_name)),
                ("CIK", _esc(self.cik)),
                ("Form", _esc(self.form)),
                ("Filing Date", _esc(self.filing_date)),
                ("Accession #", _esc(self.accession_number)),
                ("File Type", _esc(self.file_type)),
                ("Period Ending", _esc(self.period_ending)),
                ("URL", url_cell),
            ],
            caption="Search Result",
        )


def to_dataframe(items: list):
    """Convert a list of model objects to a pandas DataFrame.

    Works with any list of ``Filing``, ``Submission``, ``Fact``,
    ``SearchResult``, or other model objects from this module.
    Columns are derived automatically from the model's public
    properties (excluding ``raw``).

    Requires the ``pandas`` optional dependency. Install with
    ``pip install python-sec[pandas]``.

    ### Parameters
    ----
    items : list
        A list of model objects (e.g. ``list[Filing]``,
        ``list[SearchResult]``).

    ### Returns
    ----
    pandas.DataFrame:
        One row per item, one column per public property.

    ### Usage
    ----
        >>> from edgar.models import to_dataframe
        >>> results = edgar_client.search(q="revenue", form_types=["10-K"])
        >>> df = to_dataframe(results)
        >>> df.columns
        Index(['company_name', 'cik', 'form', 'filing_date', ...])
    """
    pd = _require_pandas()

    if not items:
        return pd.DataFrame()

    model_cls = type(items[0])
    prop_names = [
        name
        for name in dir(model_cls)
        if not name.startswith("_")
        and name != "raw"
        and isinstance(getattr(model_cls, name, None), property)
    ]

    records = [
        {name: getattr(item, name) for name in prop_names}
        for item in items
    ]

    return pd.DataFrame(records)
