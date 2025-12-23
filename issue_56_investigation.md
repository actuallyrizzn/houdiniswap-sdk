## Investigation

Current code:
- `get_dex_tokens()` requires manual pagination
- Users must call multiple times with different page numbers
- No convenience method to get all tokens

## Proposed Solution

1. **Add `get_all_dex_tokens()` method**:
   - Iterates through all pages automatically
   - Returns generator/iterator for memory efficiency
   - Handles pagination internally

2. **Add pagination helper**:
   - `iter_dex_tokens()` generator method
   - Yields tokens page by page
   - Stops when no more pages

3. **Add pagination metadata**:
   - Return total pages, current page info

