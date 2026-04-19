# Linting

All Python files must pass lint checks before work is considered complete.

## Tooling

This project uses **Pylint** via the VS Code Python extension. Project-level pylint config lives in `pyproject.toml` under `[tool.pylint.*]` sections.

### Project-level config (`pyproject.toml`)

- **Max line length**: 120 characters
- **Max function args**: 8
- **Ignored paths**: `resources/`, `samples/`
- **Globally disabled rules**: `missing-module-docstring`, `missing-class-docstring`, `too-few-public-methods`, `too-many-arguments`, `too-many-instance-attributes`, `import-error`

Do **not** modify the project-level disables without good reason. If a rule is disabled globally, it should not also be disabled per-file.

## Per-File Disables

These are the accepted per-file disables:

| Disable                                       | Where                                  | Why                                                           |
| --------------------------------------------- | -------------------------------------- | ------------------------------------------------------------- |
| `# pylint: disable=redefined-outer-name`      | Top of every `tests/test_*.py`         | pytest fixtures redefine outer names by design                |
| `# pylint: disable=protected-access`          | Test files that verify `_repr_html_()` or internal helpers | Testing underscore-prefixed methods that are part of the public contract (e.g. Jupyter protocol) |
| `# pylint: disable=import-outside-toplevel`   | Modules with optional deps (`pandas`, `httpx`) and their tests | Deferred imports inside functions to avoid hard dependency     |
| `# pylint: disable=too-many-positional-arguments` | Methods with many parameters (e.g. `search()`) | SEC endpoints sometimes require many parameters               |
| `# pylint: disable=global-statement`          | `edgar/__init__.py`                    | Module-level singleton pattern for lazy client init           |
| `# pylint: disable=missing-function-docstring`| Async test files with many small tests | Acceptable in test files where the test name is self-documenting |

Do **not** add blanket disables for other rules. Fix the underlying issue instead.

## Common Rules to Watch For

### Unused imports

- Remove any import that is not used in the file.
- `TYPE_CHECKING` imports are fine — they're used for type hints only.

### Protected access (`protected-access`)

- Prefer public API in tests when possible.
- Acceptable exceptions where `# pylint: disable=protected-access` is allowed at file level:
  - `_repr_html_()` — part of the Jupyter display protocol, tested across all model types.
  - `_throttle()` — internal rate-limiter method being directly unit-tested.
  - `_get_client()` — convenience module internals.
- For anything else, refactor to use public API or pass the dependency via constructor/fixture.

### Line length

- Target **120 characters** per line (matching `max-line-length` in `pyproject.toml`). Break long strings, dict literals, and function signatures across multiple lines.

### Import ordering

- Standard library first, then third-party, then local `edgar.*` imports.
- Separate groups with a blank line.

```python
import logging
import time
from collections import deque

import requests
from urllib3.util.retry import Retry

from edgar.exceptions import EdgarRequestError
from edgar.parser import EdgarParser
```

### Type hints

- Use `from __future__ import annotations` at the top of modules that use `X | Y` union syntax.
- Use `TYPE_CHECKING` guard for imports only needed for type hints to avoid circular imports.

```python
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from edgar.session import EdgarSession
```

### f-string formatting

- Prefer f-strings over `.format()` or `%` formatting.
- Use `!r` for values that should show their repr: `f"Got: {value!r}"`.

## Validation Workflow

After completing any code change:

1. Check for lint errors in modified files using the editor's problem panel.
2. Fix all errors and warnings before committing.
3. If a new per-file disable is genuinely needed, document why in a comment.

## Files That Must Be Lint-Clean

- All files under `edgar/` (source code)
- All files under `tests/` (test code)
- Sample files under `samples/` are best-effort but should still be clean.
