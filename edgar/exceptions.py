"""Custom exceptions for the python-sec EDGAR client."""


class EdgarError(Exception):
    """Base exception for all EDGAR client errors."""


class EdgarRequestError(EdgarError):
    """Raised when an HTTP request to the SEC EDGAR API fails."""


class EdgarParseError(EdgarError):
    """Raised when parsing an SEC EDGAR response fails."""
