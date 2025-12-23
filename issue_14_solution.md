## Proposed Solution

1. **Add type guard functions** using `TypeGuard` from `typing`:
   - `_is_list_response()`: Type guard for list responses
   - `_is_dict_response()`: Type guard for dict responses

2. **Replace `isinstance()` checks** with type guard functions in:
   - `get_volume()`: Use `_is_list_response()` and `_is_dict_response()`
   - `get_weekly_volume()`: Use `_is_list_response()` and `_is_dict_response()`
   - `post_dex_confirm_tx()`: Use `_is_dict_response()`

3. **Add error handling** for unexpected types (raise APIError)

This helps type checkers (mypy, pyright) understand type narrowing and improves type safety.

