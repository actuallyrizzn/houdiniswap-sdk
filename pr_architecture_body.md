## Summary

This PR addresses 4 architecture improvement issues identified in the audit report:

- **#25**: NO RETRY LOGIC - Added automatic retry with exponential backoff
- **#28**: HARDCODED BASE URL - Added environment variable support
- **#29**: NO LOGGING - Added structured logging with credential redaction
- **#30**: NO CACHING MECHANISM - Added in-memory caching for token lists

## Changes

### Retry Logic (#25)
- Added `max_retries` and `retry_backoff_factor` parameters to `__init__`
- Implemented automatic retry for:
  - Network errors (transient failures)
  - 5xx server errors (500, 502, 503, 504)
  - 429 rate limit errors
- Exponential backoff: `wait_time = retry_backoff_factor * (2 ** attempt)`
- Logs retry attempts for debugging

### Configurable Base URL (#28)
- Added `HOUDINI_SWAP_API_URL` environment variable support
- Resolution order: `base_url` parameter > environment variable > default
- Updated constants with `BASE_URL_PRODUCTION` and `ENV_VAR_API_URL`

### Logging (#29)
- Added structured logging using Python's standard `logging` module
- Configurable via `log_level` parameter (DEBUG, INFO, WARNING, ERROR)
- Logs requests/responses with credential redaction
- Logs errors, retries, and performance metrics
- `_redact_credentials()` method to sanitize logged data

### Caching (#30)
- Added in-memory cache for token lists
- Configurable via `cache_enabled` (default: True) and `cache_ttl` (default: 300s)
- Caches `get_cex_tokens()` and `get_dex_tokens()` results
- Cache key includes parameters for DEX tokens (page, page_size, chain)
- `clear_cache()` method for manual invalidation
- Automatic expiration based on TTL

## Testing

- All imports successful
- No linter errors
- Code follows existing patterns

## Related Issues

Closes #25, #28, #29, #30

