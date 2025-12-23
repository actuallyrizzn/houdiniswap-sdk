## Investigation

Current code uses `isinstance()` checks but type checkers (mypy, pyright) won't narrow types:
- `get_volume()`: `isinstance(response, list)`
- `get_weekly_volume()`: `isinstance(response, list)`
- `post_dex_confirm_tx()`: `isinstance(response, dict)`

**Issue:**
Type checkers don't understand that after `isinstance(response, list)`, `response` is a `list` - they still see it as `Dict[str, Any]`.

## Proposed Solution

1. **Add type guard functions** using `TypeGuard` from `typing`:
   ```python
   from typing import TypeGuard
   
   def is_list_response(response: Dict[str, Any]) -> TypeGuard[List[Dict[str, Any]]]:
       return isinstance(response, list)
   ```

2. **Use type guards** in methods to help type checkers:
   ```python
   if is_list_response(response):
       # Type checker now knows response is List[Dict[str, Any]]
       return [Volume.from_dict(item) for item in response]
   ```

3. **Apply to all isinstance checks** that need type narrowing

This improves type checking accuracy and helps catch type errors at development time.

