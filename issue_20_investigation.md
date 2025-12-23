## Investigation

Current code issues:
1. `get_dex_quote()` at line ~366: Assumes response is always a list
2. `post_dex_approve()` at line ~566: Assumes response is always a list
3. No handling for empty lists
4. Will raise `AttributeError` if API structure changes

**Example:**
```python
response = self._request("GET", ENDPOINT_DEX_QUOTE, params=params)
return [DEXQuote.from_dict(quote_data) for quote_data in response]
# What if response is {} or None?
```

## Proposed Solution

1. Add type checking before list comprehension:
   - Check `isinstance(response, list)` before iterating
   - Handle empty lists gracefully
   - Handle unexpected types (dict, None) with clear error messages

2. Add validation helpers for expected response types

3. Return empty lists for empty responses (or raise appropriate errors)

