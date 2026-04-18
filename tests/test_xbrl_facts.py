"""Tests for the Facts and Fact XBRL response models."""

# pylint: disable=redefined-outer-name

from unittest.mock import MagicMock

import pytest

from edgar.models import Fact, Facts
from edgar.company import Company
from edgar.xbrl import Xbrl


# ---------------------------------------------------------------------------
# Sample raw data fixtures
# ---------------------------------------------------------------------------

SAMPLE_COMPANY_FACTS = {
    "cik": 320193,
    "entityName": "Apple Inc.",
    "facts": {
        "dei": {
            "EntityCommonStockSharesOutstanding": {
                "label": "Entity Common Stock, Shares Outstanding",
                "description": "Indicate number of shares outstanding.",
                "units": {
                    "shares": [
                        {
                            "end": "2023-10-27",
                            "val": 15550061000,
                            "accn": "0000320193-23-000106",
                            "fy": 2023,
                            "fp": "FY",
                            "form": "10-K",
                            "filed": "2023-11-03",
                            "frame": "CY2023Q4I",
                        },
                    ]
                },
            }
        },
        "us-gaap": {
            "Revenue": {
                "label": "Revenue",
                "description": "Amount of revenue recognized.",
                "units": {
                    "USD": [
                        {
                            "start": "2021-09-26",
                            "end": "2022-09-24",
                            "val": 394328000000,
                            "accn": "0000320193-22-000108",
                            "fy": 2022,
                            "fp": "FY",
                            "form": "10-K",
                            "filed": "2022-10-28",
                            "frame": "CY2022",
                        },
                        {
                            "start": "2022-09-25",
                            "end": "2023-09-30",
                            "val": 383285000000,
                            "accn": "0000320193-23-000106",
                            "fy": 2023,
                            "fp": "FY",
                            "form": "10-K",
                            "filed": "2023-11-03",
                            "frame": "CY2023",
                        },
                    ]
                },
            },
            "AccountsPayableCurrent": {
                "label": "Accounts Payable, Current",
                "description": "Carrying value of accounts payable.",
                "units": {
                    "USD": [
                        {
                            "end": "2022-09-24",
                            "val": 64115000000,
                            "accn": "0000320193-22-000108",
                            "fy": 2022,
                            "fp": "FY",
                            "form": "10-K",
                            "filed": "2022-10-28",
                            "frame": "CY2022Q4I",
                        },
                        {
                            "end": "2023-09-30",
                            "val": 62611000000,
                            "accn": "0000320193-23-000106",
                            "fy": 2023,
                            "fp": "FY",
                            "form": "10-K",
                            "filed": "2023-11-03",
                            "frame": "CY2023Q4I",
                        },
                    ],
                    "EUR": [
                        {
                            "end": "2023-09-30",
                            "val": 59000000000,
                            "accn": "0000320193-23-000106",
                            "fy": 2023,
                            "fp": "FY",
                            "form": "10-K",
                            "filed": "2023-11-03",
                        },
                    ],
                },
            },
        },
        "ifrs-full": {
            "Revenue": {
                "label": "Revenue",
                "description": "IFRS revenue.",
                "units": {
                    "USD": [
                        {
                            "end": "2023-12-31",
                            "val": 100000000,
                            "accn": "0000320193-24-000001",
                            "fy": 2023,
                            "fp": "FY",
                            "form": "20-F",
                            "filed": "2024-03-01",
                        },
                    ]
                },
            }
        },
    },
}

SAMPLE_EMPTY_FACTS = {
    "cik": 999999,
    "entityName": "Empty Corp",
    "facts": {},
}


# ---------------------------------------------------------------------------
# Fact model tests
# ---------------------------------------------------------------------------


class TestFact:
    """Tests for the Fact dataclass model."""

    def test_properties(self):
        """Verify all properties extract correctly."""
        raw = {
            "start": "2022-09-25",
            "end": "2023-09-30",
            "val": 383285000000,
            "accn": "0000320193-23-000106",
            "fy": 2023,
            "fp": "FY",
            "form": "10-K",
            "filed": "2023-11-03",
            "frame": "CY2023",
        }
        fact = Fact(raw=raw)
        assert fact.start == "2022-09-25"
        assert fact.end == "2023-09-30"
        assert fact.value == 383285000000
        assert fact.accession_number == "0000320193-23-000106"
        assert fact.fiscal_year == 2023
        assert fact.fiscal_period == "FY"
        assert fact.form == "10-K"
        assert fact.filed == "2023-11-03"
        assert fact.frame == "CY2023"

    def test_defaults_for_missing_keys(self):
        """Verify graceful defaults for empty dicts."""
        fact = Fact(raw={})
        assert fact.start == ""
        assert fact.end == ""
        assert fact.value is None
        assert fact.accession_number == ""
        assert fact.fiscal_year == 0
        assert fact.fiscal_period == ""
        assert fact.form == ""
        assert fact.filed == ""
        assert fact.frame == ""

    def test_raw_attribute(self):
        """Verify the raw dict is accessible."""
        raw = {"val": 42, "end": "2023-01-01"}
        assert Fact(raw=raw).raw is raw

    def test_repr(self):
        """Verify repr contains key fields."""
        fact = Fact(raw={"end": "2023-09-30", "val": 100, "form": "10-K", "fy": 2023})
        result = repr(fact)
        assert "2023-09-30" in result
        assert "100" in result
        assert "10-K" in result

    def test_frozen(self):
        """Verify the dataclass is immutable."""
        fact = Fact(raw={"val": 1})
        with pytest.raises(AttributeError):
            fact.raw = {}


# ---------------------------------------------------------------------------
# Facts model tests
# ---------------------------------------------------------------------------


class TestFacts:
    """Tests for the Facts dataclass model."""

    def test_cik(self):
        """Verify CIK extraction."""
        facts = Facts(raw=SAMPLE_COMPANY_FACTS)
        assert facts.cik == 320193

    def test_entity_name(self):
        """Verify entity name extraction."""
        facts = Facts(raw=SAMPLE_COMPANY_FACTS)
        assert facts.entity_name == "Apple Inc."

    def test_taxonomies(self):
        """Verify taxonomy list includes all namespaces."""
        facts = Facts(raw=SAMPLE_COMPANY_FACTS)
        taxonomies = facts.taxonomies
        assert "dei" in taxonomies
        assert "us-gaap" in taxonomies
        assert "ifrs-full" in taxonomies

    def test_concepts_us_gaap(self):
        """Verify concept names for us-gaap taxonomy."""
        facts = Facts(raw=SAMPLE_COMPANY_FACTS)
        concepts = facts.concepts("us-gaap")
        assert "Revenue" in concepts
        assert "AccountsPayableCurrent" in concepts
        assert concepts == sorted(concepts)

    def test_concepts_default_taxonomy(self):
        """Verify concepts() defaults to us-gaap."""
        facts = Facts(raw=SAMPLE_COMPANY_FACTS)
        assert facts.concepts() == facts.concepts("us-gaap")

    def test_concepts_empty_taxonomy(self):
        """Verify concepts returns empty list for missing taxonomy."""
        facts = Facts(raw=SAMPLE_COMPANY_FACTS)
        assert facts.concepts("nonexistent") == []

    def test_get_returns_fact_objects(self):
        """Verify get() returns Fact model instances."""
        facts = Facts(raw=SAMPLE_COMPANY_FACTS)
        revenue = facts.get("us-gaap", "Revenue")
        assert len(revenue) == 2
        assert all(isinstance(f, Fact) for f in revenue)

    def test_get_sorted_by_end_date(self):
        """Verify get() returns facts sorted by end date."""
        facts = Facts(raw=SAMPLE_COMPANY_FACTS)
        revenue = facts.get("us-gaap", "Revenue")
        dates = [f.end for f in revenue]
        assert dates == sorted(dates)

    def test_get_with_unit_filter(self):
        """Verify get() filters by unit when specified."""
        facts = Facts(raw=SAMPLE_COMPANY_FACTS)
        usd_only = facts.get("us-gaap", "AccountsPayableCurrent", unit="USD")
        assert len(usd_only) == 2
        eur_only = facts.get("us-gaap", "AccountsPayableCurrent", unit="EUR")
        assert len(eur_only) == 1

    def test_get_without_unit_returns_all(self):
        """Verify get() without unit returns facts from all units."""
        facts = Facts(raw=SAMPLE_COMPANY_FACTS)
        all_facts = facts.get("us-gaap", "AccountsPayableCurrent")
        # 2 USD + 1 EUR = 3
        assert len(all_facts) == 3

    def test_get_nonexistent_concept(self):
        """Verify get() returns empty list for missing concept."""
        facts = Facts(raw=SAMPLE_COMPANY_FACTS)
        assert facts.get("us-gaap", "NonexistentConcept") == []

    def test_get_nonexistent_taxonomy(self):
        """Verify get() returns empty list for missing taxonomy."""
        facts = Facts(raw=SAMPLE_COMPANY_FACTS)
        assert facts.get("nonexistent", "Revenue") == []

    def test_get_nonexistent_unit(self):
        """Verify get() returns empty list for missing unit."""
        facts = Facts(raw=SAMPLE_COMPANY_FACTS)
        assert facts.get("us-gaap", "Revenue", unit="GBP") == []

    def test_get_ifrs_taxonomy(self):
        """Verify get() works with IFRS taxonomy."""
        facts = Facts(raw=SAMPLE_COMPANY_FACTS)
        ifrs_revenue = facts.get("ifrs-full", "Revenue")
        assert len(ifrs_revenue) == 1
        assert ifrs_revenue[0].value == 100000000

    def test_get_dei_taxonomy(self):
        """Verify get() works with DEI taxonomy."""
        facts = Facts(raw=SAMPLE_COMPANY_FACTS)
        shares = facts.get("dei", "EntityCommonStockSharesOutstanding")
        assert len(shares) == 1
        assert shares[0].value == 15550061000

    def test_label(self):
        """Verify label() returns the concept label."""
        facts = Facts(raw=SAMPLE_COMPANY_FACTS)
        assert facts.label("us-gaap", "Revenue") == "Revenue"
        assert facts.label("us-gaap", "AccountsPayableCurrent") == "Accounts Payable, Current"

    def test_label_missing(self):
        """Verify label() returns empty string for missing concept."""
        facts = Facts(raw=SAMPLE_COMPANY_FACTS)
        assert facts.label("us-gaap", "Nonexistent") == ""

    def test_description(self):
        """Verify description() returns the concept description."""
        facts = Facts(raw=SAMPLE_COMPANY_FACTS)
        assert "revenue" in facts.description("us-gaap", "Revenue").lower()

    def test_description_missing(self):
        """Verify description() returns empty string for missing concept."""
        facts = Facts(raw=SAMPLE_COMPANY_FACTS)
        assert facts.description("us-gaap", "Nonexistent") == ""

    def test_units(self):
        """Verify units() returns available units for a concept."""
        facts = Facts(raw=SAMPLE_COMPANY_FACTS)
        assert facts.units("us-gaap", "Revenue") == ["USD"]
        units = facts.units("us-gaap", "AccountsPayableCurrent")
        assert "USD" in units
        assert "EUR" in units

    def test_units_missing(self):
        """Verify units() returns empty list for missing concept."""
        facts = Facts(raw=SAMPLE_COMPANY_FACTS)
        assert facts.units("us-gaap", "Nonexistent") == []

    def test_raw_attribute(self):
        """Verify the raw dict is accessible."""
        facts = Facts(raw=SAMPLE_COMPANY_FACTS)
        assert facts.raw is SAMPLE_COMPANY_FACTS

    def test_repr(self):
        """Verify repr contains key fields."""
        facts = Facts(raw=SAMPLE_COMPANY_FACTS)
        result = repr(facts)
        assert "Apple Inc." in result
        assert "320193" in result
        assert "taxonomies=3" in result

    def test_empty_facts(self):
        """Verify empty facts dict works gracefully."""
        facts = Facts(raw=SAMPLE_EMPTY_FACTS)
        assert facts.cik == 999999
        assert facts.entity_name == "Empty Corp"
        assert facts.taxonomies == []
        assert facts.concepts() == []

    def test_defaults_for_missing_keys(self):
        """Verify graceful defaults for fully empty raw dict."""
        facts = Facts(raw={})
        assert facts.cik == 0
        assert facts.entity_name == ""
        assert facts.taxonomies == []

    def test_frozen(self):
        """Verify the dataclass is immutable."""
        facts = Facts(raw=SAMPLE_COMPANY_FACTS)
        with pytest.raises(AttributeError):
            facts.raw = {}


# ---------------------------------------------------------------------------
# Company.get_facts() integration tests
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_tickers():
    """Return a mock Tickers service."""
    tickers = MagicMock()
    tickers.resolve_ticker.return_value = "0000320193"
    tickers.resolve_cik.return_value = [
        {"cik_str": 320193, "ticker": "AAPL", "title": "Apple Inc."}
    ]
    return tickers


class TestCompanyGetFacts:
    """Tests for Company.get_facts() returning Facts model."""

    def test_get_facts_returns_facts_model(self, mock_tickers):
        """Verify get_facts() returns a Facts model instance."""
        session = MagicMock()
        session.make_request.return_value = SAMPLE_COMPANY_FACTS
        session.edgar_utilities = MagicMock()

        company = Company(identifier="AAPL", session=session, tickers_service=mock_tickers)
        facts = company.get_facts()

        assert isinstance(facts, Facts)
        assert facts.entity_name == "Apple Inc."
        assert "us-gaap" in facts.taxonomies

    def test_get_facts_returns_none_when_no_data(self, mock_tickers):
        """Verify get_facts() returns None when xbrl_facts returns None."""
        session = MagicMock()
        session.make_request.return_value = None
        session.edgar_utilities = MagicMock()

        company = Company(identifier="AAPL", session=session, tickers_service=mock_tickers)
        assert company.get_facts() is None


# ---------------------------------------------------------------------------
# Xbrl.get_facts() integration tests
# ---------------------------------------------------------------------------


class TestXbrlGetFacts:
    """Tests for Xbrl.get_facts() returning Facts model."""

    def test_get_facts_returns_facts_model(self):
        """Verify Xbrl.get_facts() returns a Facts model instance."""
        session = MagicMock()
        session.make_request.return_value = SAMPLE_COMPANY_FACTS
        session.edgar_utilities = MagicMock()

        xbrl = Xbrl(session=session)
        facts = xbrl.get_facts(cik="320193")

        assert isinstance(facts, Facts)
        assert facts.entity_name == "Apple Inc."

    def test_get_facts_returns_none_when_no_data(self):
        """Verify Xbrl.get_facts() returns None when company_facts returns None."""
        session = MagicMock()
        session.make_request.return_value = None
        session.edgar_utilities = MagicMock()

        xbrl = Xbrl(session=session)
        assert xbrl.get_facts(cik="320193") is None


# ---------------------------------------------------------------------------
# Xbrl taxonomy parameter tests
# ---------------------------------------------------------------------------


class TestXbrlTaxonomyParam:
    """Tests that company_concepts and frames accept a taxonomy parameter."""

    def test_company_concepts_default_taxonomy(self):
        """Verify company_concepts uses us-gaap by default."""
        session = MagicMock()
        session.make_request.return_value = {"units": {}}
        session.edgar_utilities = MagicMock()

        xbrl = Xbrl(session=session)
        xbrl.company_concepts(cik="320193", concept="Revenue")

        call_kwargs = session.make_request.call_args
        endpoint = call_kwargs[1]["endpoint"] if "endpoint" in call_kwargs[1] else call_kwargs[0][1]
        assert "/us-gaap/" in endpoint

    def test_company_concepts_custom_taxonomy(self):
        """Verify company_concepts accepts ifrs-full taxonomy."""
        session = MagicMock()
        session.make_request.return_value = {"units": {}}
        session.edgar_utilities = MagicMock()

        xbrl = Xbrl(session=session)
        xbrl.company_concepts(cik="320193", concept="Revenue", taxonomy="ifrs-full")

        call_kwargs = session.make_request.call_args
        endpoint = call_kwargs[1]["endpoint"] if "endpoint" in call_kwargs[1] else call_kwargs[0][1]
        assert "/ifrs-full/" in endpoint
        assert "/us-gaap/" not in endpoint

    def test_frames_default_taxonomy(self):
        """Verify frames uses us-gaap by default."""
        session = MagicMock()
        session.make_request.return_value = {"data": []}
        session.edgar_utilities = MagicMock()

        xbrl = Xbrl(session=session)
        xbrl.frames(concept="Revenue", unit_of_measure="USD", period="CY2023")

        call_kwargs = session.make_request.call_args
        endpoint = call_kwargs[1]["endpoint"] if "endpoint" in call_kwargs[1] else call_kwargs[0][1]
        assert "/us-gaap/" in endpoint

    def test_frames_custom_taxonomy(self):
        """Verify frames accepts ifrs-full taxonomy."""
        session = MagicMock()
        session.make_request.return_value = {"data": []}
        session.edgar_utilities = MagicMock()

        xbrl = Xbrl(session=session)
        xbrl.frames(
            concept="Revenue",
            unit_of_measure="USD",
            period="CY2023",
            taxonomy="ifrs-full",
        )

        call_kwargs = session.make_request.call_args
        endpoint = call_kwargs[1]["endpoint"] if "endpoint" in call_kwargs[1] else call_kwargs[0][1]
        assert "/ifrs-full/" in endpoint
