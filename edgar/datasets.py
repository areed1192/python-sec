"""Service for downloading SEC EDGAR XBRL datasets."""

from __future__ import annotations

import csv
import io
import zipfile

from edgar.session import EdgarSession

_DERA_BASE = "/files/dera/data/financial-statement-data-sets"


def _require_pandas():
    """Import and return the ``pandas`` module, raising a helpful error if missing."""
    try:
        import pandas as pd  # pylint: disable=import-outside-toplevel
        return pd
    except ImportError as exc:
        raise ImportError(
            "pandas is required for DataFrame conversion. "
            "Install it with: pip install python-sec[pandas]"
        ) from exc


class Datasets():

    """
    ## Overview
    ----
    The SEC offers free datasets for individuals and companies to use
    in their own research. The `Datasets` client helps users query these
    datasets.
    """

    def __init__(self, session: EdgarSession) -> None:
        """Initializes the `Datasets` object.

        ### Parameters
        ----
        session : `EdgarSession`
            An initialized session of the `EdgarSession`.

        ### Usage
        ----
            >>> edgar_client = EdgarClient(user_agent="Your Name your-email@example.com")
            >>> datasets_services = edgar_client.Datasets()
        """

        # Set the session.
        self.edgar_session: EdgarSession = session
        self.edgar_parser = session.edgar_parser

    def __repr__(self) -> str:
        """String representation of the `EdgarClient.Datasets` object."""

        # define the string representation
        str_representation = '<EdgarClient.Datasets (active=True, connected=True)>'

        return str_representation

    def get_sec_datasets(self) -> dict | None:
        """Grabs all the Public datasets provided by the SEC.

        ### Returns
        ----
        dict:
            A collection of `Dataset` resources.

        ### Usage
        ----
            >>> edgar_client = EdgarClient(user_agent="Your Name your-email@example.com")
            >>> datasets_services = edgar_client.Datasets()
            >>> datasets_services.get_sec_datasets()
        """

        # Make the request.
        response = self.edgar_session.make_request(
            method='get',
            endpoint='/data.json'
        )

        return response

    def get_edgar_taxonomies(self) -> list[dict]:
        """Grabs all the Public taxonomies datasets provided by the SEC.

        ### Returns
        ----
        dict:
            A collection of `Dataset` taxonomy resources.

        ### Usage
        ----
            >>> edgar_client = EdgarClient(user_agent="Your Name your-email@example.com")
            >>> datasets_services = edgar_client.Datasets()
            >>> datasets_services.get_sec_datasets()
        """

        # Make the request.
        response = self.edgar_session.make_request(
            method='get',
            endpoint='/info/edgar/edgartaxonomies.xml'
        )

        if response is None:
            return []

        response = self.edgar_parser.parse_loc_elements(
            response_text=response
        )

        return response

    def get_financial_statements(
        self,
        year: int,
        quarter: int,
    ) -> dict[str, list[dict]]:
        """Downloads a SEC DERA bulk financial statement dataset.

        The SEC publishes quarterly ZIP archives containing four
        tab-separated files (``sub.txt``, ``num.txt``, ``tag.txt``,
        ``pre.txt``) covering all XBRL filings for a given period.

        ### Parameters
        ----
        year : int
            The calendar year (e.g. ``2023``).

        quarter : int
            The calendar quarter (1-4).

        ### Returns
        ----
        dict[str, list[dict]]:
            A dictionary keyed by filename (without ``.txt`` extension)
            with values being lists of row dictionaries. Keys are
            typically ``"sub"``, ``"num"``, ``"tag"``, ``"pre"``.

        ### Raises
        ----
        ValueError:
            If quarter is not between 1 and 4.

        ### Usage
        ----
            >>> edgar_client = EdgarClient(user_agent="Your Name your-email@example.com")
            >>> datasets = edgar_client.datasets()
            >>> data = datasets.get_financial_statements(2023, 4)
            >>> len(data["sub"])  # number of submissions
            7654
            >>> data["num"][0].keys()
            dict_keys(['adsh', 'tag', 'version', 'coreg', ...])
        """
        if not 1 <= quarter <= 4:
            raise ValueError(f"quarter must be between 1 and 4, got {quarter}")

        endpoint = f"{_DERA_BASE}/{year}q{quarter}.zip"
        zip_bytes = self.edgar_session.fetch_page(
            self.edgar_session.build_url(endpoint=endpoint)
        )

        if zip_bytes is None:
            return {}

        return _extract_tsv_zip(zip_bytes)

    def get_financial_statements_dataframes(
        self,
        year: int,
        quarter: int,
    ) -> dict:
        """Downloads a DERA dataset and returns DataFrames.

        Same as ``get_financial_statements()`` but returns a dict of
        ``pandas.DataFrame`` objects instead of lists of dicts.

        Requires the ``pandas`` optional dependency. Install with
        ``pip install python-sec[pandas]``.

        ### Parameters
        ----
        year : int
            The calendar year (e.g. ``2023``).

        quarter : int
            The calendar quarter (1–4).

        ### Returns
        ----
        dict[str, pandas.DataFrame]:
            A dictionary keyed by filename (e.g. ``"sub"``, ``"num"``,
            ``"tag"``, ``"pre"``) with DataFrame values.

        ### Usage
        ----
            >>> datasets = edgar_client.datasets()
            >>> dfs = datasets.get_financial_statements_dataframes(2023, 4)
            >>> dfs["num"].head()
        """
        pd = _require_pandas()
        data = self.get_financial_statements(year, quarter)

        if not data:
            return {}

        return {name: pd.DataFrame(rows) for name, rows in data.items()}


def _extract_tsv_zip(zip_bytes: bytes) -> dict[str, list[dict]]:
    """Extract all TSV (.txt) files from a ZIP archive into row dicts.

    ### Parameters
    ----
    zip_bytes : bytes
        Raw bytes of a ZIP archive.

    ### Returns
    ----
    dict[str, list[dict]]:
        Mapping from filename stem to list of row dictionaries.
    """
    result: dict[str, list[dict]] = {}

    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
        for name in zf.namelist():
            if not name.endswith(".txt"):
                continue

            key = name.rsplit(".", 1)[0]
            with zf.open(name) as f:
                text = io.TextIOWrapper(f, encoding="utf-8")
                reader = csv.DictReader(text, delimiter="\t")
                result[key] = list(reader)

    return result
