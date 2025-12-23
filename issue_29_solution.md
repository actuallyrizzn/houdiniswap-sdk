## Proposed Solution

1. **Add logging using Python's standard `logging` module**:
   - Create logger: `logger = logging.getLogger("houdiniswap")`
   - Support configurable log levels via `log_level` parameter

2. **Add logging to `_request()`**:
   - Log request method, URL, params (redact credentials)
   - Log response status, timing
   - Log errors with full context
   - Log retry attempts

3. **Add credential redaction**:
   - `_redact_credentials()` method to sanitize logged data
   - Redact `Authorization` header in logs

4. **Make logging configurable**:
   - `log_level` parameter in `__init__` (default: None, no logging)
   - Support `logging.DEBUG`, `INFO`, `WARNING`, `ERROR`

This provides comprehensive logging for debugging and monitoring without exposing credentials.

