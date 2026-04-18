"""Unit tests for EdgarParser XML and HTML parsing."""

import defusedxml.ElementTree as DefusedET
import pytest

from edgar.exceptions import EdgarParseError
from tests.conftest import (
    SAMPLE_ATOM_FEED,
    SAMPLE_ATOM_FEED_NO_NEXT,
    SAMPLE_ATOM_FEED_WITH_NEXT,
    SAMPLE_MALFORMED_XML,
)


class TestParseEntries:
    """Tests for EdgarParser.parse_entries."""

    def test_parses_two_entries(self, edgar_parser):
        """parse_entries should return one dict per <entry> element."""
        entries = edgar_parser.parse_entries(response_text=SAMPLE_ATOM_FEED)
        assert len(entries) == 2

    def test_entry_contains_expected_keys(self, edgar_parser):
        """Each parsed entry should contain title, summary, updated, and link data."""
        entries = edgar_parser.parse_entries(response_text=SAMPLE_ATOM_FEED)
        first = entries[0]
        assert "title" in first
        assert "summary" in first
        assert "updated" in first

    def test_entry_title_value(self, edgar_parser):
        """The first entry title should match the XML content."""
        entries = edgar_parser.parse_entries(response_text=SAMPLE_ATOM_FEED)
        assert entries[0]["title"] == "10-K - Annual report"

    def test_second_entry_title(self, edgar_parser):
        """The second entry should be the 10-Q."""
        entries = edgar_parser.parse_entries(response_text=SAMPLE_ATOM_FEED)
        assert entries[1]["title"] == "10-Q - Quarterly report"

    def test_malformed_xml_raises_parse_error(self, edgar_parser):
        """Malformed XML should raise EdgarParseError."""
        with pytest.raises(EdgarParseError, match="Failed to parse XML"):
            edgar_parser.parse_entries(response_text=SAMPLE_MALFORMED_XML)

    def test_empty_feed_returns_empty_list(self, edgar_parser):
        """A feed with no entries should return an empty list."""
        xml = '<?xml version="1.0"?><feed xmlns="http://www.w3.org/2005/Atom"></feed>'
        entries = edgar_parser.parse_entries(response_text=xml)
        assert entries == []


class TestParseEntriesPagination:
    """Tests for pagination handling in parse_entries."""

    def test_follows_next_page(self, edgar_parser):
        """parse_entries should follow next-page links via fetch_page callback."""
        call_count = {"n": 0}

        def fake_fetch(_url):
            call_count["n"] += 1
            # Return second page (no next link) on first call.
            return SAMPLE_ATOM_FEED_NO_NEXT.encode("utf-8")

        entries = edgar_parser.parse_entries(
            response_text=SAMPLE_ATOM_FEED_WITH_NEXT,
            fetch_page=fake_fetch,
        )
        # One entry from page 1, one from page 2.
        assert len(entries) == 2
        assert call_count["n"] == 1

    def test_stops_when_no_fetch_page(self, edgar_parser):
        """Without fetch_page, pagination should stop after the first page."""
        entries = edgar_parser.parse_entries(
            response_text=SAMPLE_ATOM_FEED_WITH_NEXT,
            fetch_page=None,
        )
        assert len(entries) == 1

    def test_stops_when_fetch_returns_none(self, edgar_parser):
        """If fetch_page returns None, pagination should stop."""
        entries = edgar_parser.parse_entries(
            response_text=SAMPLE_ATOM_FEED_WITH_NEXT,
            fetch_page=lambda url: None,
        )
        assert len(entries) == 1


class TestCheckForNextPage:
    """Tests for EdgarParser.check_for_next_page."""

    def test_finds_next_page_url(self, edgar_parser):
        """Should extract the href from a rel='next' link element."""
        root = DefusedET.fromstring(SAMPLE_ATOM_FEED_WITH_NEXT)
        url = edgar_parser.check_for_next_page(root_document=root)
        assert url is not None
        assert "start=40" in url

    def test_returns_none_when_no_next(self, edgar_parser):
        """Should return None when there is no next-page link."""
        root = DefusedET.fromstring(SAMPLE_ATOM_FEED_NO_NEXT)
        url = edgar_parser.check_for_next_page(root_document=root)
        assert url is None


class TestParseEntryElement:
    """Tests for EdgarParser.parse_entry_element."""

    def test_converts_entry_to_dict(self, edgar_parser):
        """An entry element should be converted to a flat dict."""
        root = DefusedET.fromstring(SAMPLE_ATOM_FEED)
        ns = edgar_parser.entries_namespace
        entry = root.findall("atom:entry", namespaces=ns)[0]
        result = edgar_parser.parse_entry_element(entry=entry)
        assert isinstance(result, dict)
        assert "title" in result
