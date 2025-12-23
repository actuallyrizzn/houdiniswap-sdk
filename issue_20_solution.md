## Proposed Solution

1. **Add type checking before list operations**:
   - Check `isinstance(response, list)` before iterating
   - Raise `APIError` with descriptive message if type is unexpected

2. **Handle empty lists gracefully**:
   - Return empty list for `get_dex_quote()` (no routes available)
   - Return empty list for `post_dex_approve()` (approval not needed)

3. **Apply to both methods**:
   - `get_dex_quote()` at line ~414
   - `post_dex_approve()` at line ~627

This prevents `AttributeError` when API structure changes and handles edge cases properly.

