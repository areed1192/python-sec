"""SEC EDGAR API client library.

Top-level convenience functions let you skip the ``EdgarClient`` boilerplate::

    import edgar

    company = edgar.company("AAPL")
    filings = edgar.get_filings("AAPL", form="10-K")
    results = edgar.search("revenue recognition")

Set the ``SEC_EDGAR_USER_AGENT`` environment variable to avoid passing
``user_agent`` on every call::

    export SEC_EDGAR_USER_AGENT="Your Name your-email@example.com"
"""

from __future__ import annotations

import os

from edgar.client import EdgarClient
from edgar.exceptions import EdgarError, EdgarRequestError, EdgarParseError

__all__ = [
    "EdgarClient",
    "EdgarError",
    "EdgarRequestError",
    "EdgarParseError",
    "company",
    "get_filings",
    "search",
    "set_user_agent",
]

_ENV_VAR = "SEC_EDGAR_USER_AGENT"
_user_agent: str | None = None
_client: EdgarClient | None = None


def set_user_agent(user_agent: str) -> None:
    """Set the default user-agent for module-level convenience functions.

    This value takes priority over the ``SEC_EDGAR_USER_AGENT``
    environment variable.
    """

    global _user_agent, _client  # pylint: disable=global-statement
    _user_agent = user_agent
    _client = None  # force re-creation on next call


def _get_client() -> EdgarClient:
    """Return a lazily-initialised shared ``EdgarClient``.

    Resolution order for the user-agent string:

    1. Value set via ``set_user_agent()``.
    2. The ``SEC_EDGAR_USER_AGENT`` environment variable.

    Raises ``EdgarError`` if neither is available.
    """

    global _client  # pylint: disable=global-statement
    if _client is not None:
        return _client

    agent = _user_agent or os.environ.get(_ENV_VAR)
    if not agent:
        raise EdgarError(
            "No user-agent configured. Either call edgar.set_user_agent() "
            f"or set the {_ENV_VAR} environment variable."
        )
    _client = EdgarClient(user_agent=agent)
    return _client


def company(identifier: str) -> object:
    """Return a ``Company`` object for the given ticker or CIK.

    >>> import edgar
    >>> edgar.company("AAPL").name
    'Apple Inc.'
    """

    return _get_client().company(identifier)


def get_filings(
    identifier: str,
    form: str | None = None,
    start: int = 0,
    number_of_filings: int = 100,
) -> list:
    """Return filings for a company as ``Filing`` model objects.

    >>> import edgar
    >>> edgar.get_filings("AAPL", form="10-K")[0].form_type
    '10-K'
    """

    return _get_client().company(identifier).get_filings(
        form=form, start=start, number_of_filings=number_of_filings
    )


def search(
    q: str,
    form_types: list[str] | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    start: int = 0,
    size: int = 100,
) -> list:
    """Full-text search across SEC EDGAR filings.

    >>> import edgar
    >>> edgar.search("revenue recognition", form_types=["10-K"])[0].company_name
    'Apple Inc. ...'
    """

    return _get_client().search(
        q=q,
        form_types=form_types,
        start_date=start_date,
        end_date=end_date,
        start=start,
        size=size,
    )
