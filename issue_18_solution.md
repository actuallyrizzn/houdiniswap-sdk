## Proposed Solution

1. **Initialize `error_data = None`** before the try block

2. **Always use `error_data` variable** (remove `locals()` check)

3. **Include raw response text** in error message when JSON parsing fails (limit to 500 chars)

4. **Improve error messages** to indicate when JSON parsing failed

This ensures `error_data` is always defined and provides better error information when JSON parsing fails.

