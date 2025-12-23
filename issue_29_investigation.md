## Investigation

Current codebase:
- Zero logging throughout
- No way to debug issues in production
- No request/response logging
- No error tracking
- No performance metrics

**Required:**
- Structured logging with configurable log levels
- Request/response logging (with credential redaction)
- Error logging
- Performance metrics

## Proposed Solution

1. **Add logging module** (`houdiniswap/logging.py` or use Python's `logging`):
   - Use Python's standard `logging` module
   - Create logger: `logger = logging.getLogger("houdiniswap")`
   - Support configurable log levels

2. **Add logging to `_request()`**:
   - Log request method, URL, params (redact credentials)
   - Log response status, timing
   - Log errors with full context

3. **Add credential redaction**:
   - Redact `Authorization` header in logs
   - Redact API key/secret from any logged data

4. **Add performance metrics**:
   - Log request duration
   - Optional: track request counts, error rates

5. **Make logging configurable**:
   - `log_level` parameter in `__init__`
   - Support `logging.DEBUG`, `INFO`, `WARNING`, `ERROR`
   - Default to `WARNING` to avoid noise

