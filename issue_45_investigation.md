## Investigation

Current code has list comprehensions that don't validate response first:
- `get_cex_tokens()`: `[Token.from_dict(token_data) for token_data in response]`
- `get_dex_quote()`: `[DEXQuote.from_dict(quote_data) for quote_data in response]`
- `post_dex_approve()`: `[DexApproveResponse.from_dict(item) for item in response]`
- `get_weekly_volume()`: `[WeeklyVolume.from_dict(item) for item in response]`

**Issue:** If API returns unexpected format (not a list), these will fail or create empty lists silently.

## Proposed Solution

1. **Validate response is list** before list comprehension (already done for some in #20)
2. **Add validation helper** `_ensure_list_response()` 
3. **Apply to all list comprehensions** that parse API responses

