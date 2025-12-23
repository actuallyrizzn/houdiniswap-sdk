## Investigation

Current code at `houdiniswap/client.py:110`:
```python
"Authorization": f"{api_key}:{api_secret}",
```

**Issues found:**
1. No validation that `api_key` or `api_secret` don't contain `:` character
2. If credentials contain `:`, the header format breaks (e.g., `key:with:colon:secret` becomes invalid)
3. No length validation (HTTP headers typically have 8KB limit)
4. No URL encoding for special characters

**Security implications:**
- Malformed headers could cause authentication failures
- Potential header injection if credentials are not properly sanitized
- No protection against extremely long credentials

## Proposed Solution

1. Add credential validation in `__init__`:
   - Check for `:` character and raise ValidationError
   - Validate length (reasonable limit, e.g., 1000 chars)
   - Optionally: URL encode credentials (though API may expect plain text)

2. Add helper method `_validate_credentials()` to centralize validation logic

3. Document the credential format requirements in docstrings

