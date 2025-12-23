## Summary

This PR addresses 7 error handling and type safety issues identified in the audit report:

- **#10**: Authorization header construction vulnerability - Added credential validation
- **#12**: Session reuse without proper cleanup - Added context manager support
- **#14**: Missing type guards - Added TypeGuard functions for better type checking
- **#17**: Exception swallowing - Added exception chaining to preserve context
- **#18**: Silent failure in error parsing - Fixed error_data initialization
- **#19**: No validation of API responses - Added validation to model from_dict() methods
- **#20**: Inconsistent error handling for empty responses - Added proper type checking

## Changes

### Security Improvements
- Added `_validate_credentials()` method to check for `:` characters and length limits
- Prevents malformed Authorization headers

### Resource Management
- Added `__enter__()` and `__exit__()` methods for context manager support
- Added `close()` method for explicit session cleanup
- Updated docstrings to document context manager usage

### Type Safety
- Added `TypeGuard` functions `_is_list_response()` and `_is_dict_response()`
- Replaced `isinstance()` checks with type guards for better type narrowing
- Type checkers (mypy, pyright) now understand type narrowing

### Error Handling
- Added exception chaining (`from e`) to preserve original exception context
- Fixed error parsing to always initialize `error_data` variable
- Added validation to all model `from_dict()` methods
- Added proper type checking and error handling for empty/unexpected responses

### Model Validation
- Added validation to `Network`, `Token`, `ExchangeResponse`, `DexApproveResponse`, and `Status` models
- Raises `ValidationError` with descriptive messages for invalid data
- Prevents silent failures when API returns unexpected structure

## Testing

- All imports successful
- No linter errors
- Code follows existing patterns

## Related Issues

Closes #10, #12, #14, #17, #18, #19, #20

