# Sample Files

Every new user-facing feature **must** ship with a sample file in `samples/`.

## Naming Convention

- `samples/use_<feature_name>.py` — matches the existing pattern.
- If the feature extends an existing service, add examples to the existing sample file instead of creating a new one.

## Required Structure

```python
"""Example usage of <feature description>."""

from edgar.client import EdgarClient

# Initialize the client.
# SEC EDGAR requires a User-Agent in the format "Company/Name email@example.com".
edgar_client = EdgarClient(user_agent="Your Name your-email@example.com")

# ---------------------------------------------------------------------------
# Section header — describe what this block demonstrates
# ---------------------------------------------------------------------------

# Inline comments showing expected output where helpful.
result = edgar_client.some_method()
print(result)
# Output: <expected shape or value>
```

## Rules

1. **Module-level docstring** — one sentence describing what the sample demonstrates.
2. **Section dividers** — use `# ---` comment blocks to separate logical sections.
3. **Inline output comments** — show `# Output: ...` after key print statements so users know what to expect without running the script.
4. **No secrets or real credentials** — always use `"Your Name your-email@example.com"` as the placeholder user agent.
5. **Runnable but safe** — samples should be runnable against the live SEC API, but never modify data. Destructive operations (file writes) should be commented out with an explanatory note.
6. **Cover the happy path** — demonstrate the primary use case, not every edge case. Keep it concise (under ~80 lines).
7. **Import from `edgar.client`** — always start from `EdgarClient`, not internal modules. Imports from other public `edgar.*` submodules (e.g. `edgar.filing_parsers`) are acceptable for features that operate independently of the client.

## When to Update vs. Create

| Scenario                                                  | Action                                    |
| --------------------------------------------------------- | ----------------------------------------- |
| New service or class (e.g. `Company`, `Facts`)            | Create `samples/use_<name>.py`            |
| New method on existing class (e.g. `company.get_facts()`) | Add a section to the existing sample file |
| Bug fix or internal refactor                              | No sample file changes needed             |
