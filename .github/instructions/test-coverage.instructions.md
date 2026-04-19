# Test Coverage

Every new feature, model, or public method **must** have unit tests before the work is considered complete.

## File Naming

- `tests/test_<module_name>.py` — one test file per logical module.
- If the module is large (e.g. `models.py` with many classes), split by domain: `tests/test_models.py`, `tests/test_xbrl_facts.py`.

## Required Structure

```python
"""Tests for <description>."""

# pylint: disable=redefined-outer-name

from unittest.mock import MagicMock

import pytest

from edgar.<module> import <Class>


# ---------------------------------------------------------------------------
# Sample raw data fixtures
# ---------------------------------------------------------------------------

SAMPLE_DATA = { ... }


# ---------------------------------------------------------------------------
# <ClassName> tests
# ---------------------------------------------------------------------------


class Test<ClassName>:
    """Tests for the <ClassName> <type>."""

    def test_<behavior>(self):
        """Verify <what is being tested>."""
        ...
```

## Test Categories

Every new class or public method needs tests in these categories:

### For dataclass models (Filing, CompanyInfo, Facts, etc.)

| Category       | What to test                                                        |
| -------------- | ------------------------------------------------------------------- |
| **Properties** | All typed properties extract correctly from a complete raw dict     |
| **Defaults**   | Missing keys return sensible defaults (empty string, 0, empty list) |
| **Raw access** | `.raw` attribute returns the original dict                          |
| **Repr**       | `__repr__` contains key identifying fields                          |
| **Frozen**     | Assigning to `.raw` raises `AttributeError`                         |
| **Edge cases** | Empty dicts, None values, missing nested keys                       |

### For service methods (get_filings, get_facts, etc.)

| Category        | What to test                                                 |
| --------------- | ------------------------------------------------------------ |
| **Happy path**  | Returns the expected model type with correct data            |
| **None/empty**  | Returns None or empty list when upstream returns None        |
| **Filtering**   | Parameters (form, unit, taxonomy) filter correctly           |
| **Integration** | Called through the right chain (Company → Service → Session) |

## Rules

1. **Module-level docstring** — one sentence describing what the file tests.
2. **`# pylint: disable=redefined-outer-name`** — at the top of every test file (pytest fixtures trigger this).
3. **Class-based grouping** — group related tests in `class Test<Name>:` with a class docstring.
4. **Docstring on every test** — `"""Verify <what>."""` on each test method.
5. **Section dividers** — use `# ---` comment blocks between test classes.
6. **Mock at the boundary** — mock `session.make_request` or `http_session.get`, not internal methods.
7. **Sample data at module level** — define `SAMPLE_*` constants as module-level dicts, not inside fixtures.
8. **Fixtures use `@pytest.fixture`** — shared setup goes in fixtures, not `setUp()`.
9. **No live API calls** — all tests must run offline with mocked responses.
10. **Run the full suite** — after writing tests, run `python -m pytest --tb=short -q` to verify no regressions.

## Test Count Tracking

When adding tests, note the count in the changelog entry:

```markdown
- **tests/test_xbrl_facts.py**: 39 unit tests for XBRL Facts models and integration.
```

Run `python -m pytest --tb=short -q` and confirm the total passes before marking work complete.
