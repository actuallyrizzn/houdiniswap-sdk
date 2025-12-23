## Proposed Solution

1. **Add context manager support**:
   - Implement `__enter__()` method returning `self`
   - Implement `__exit__()` method that calls `close()`

2. **Add public `close()` method**:
   - Explicitly closes the session with `self.session.close()`
   - Checks if session exists before closing

3. **Update docstrings** to document context manager usage:
   ```python
   # Usage:
   with HoudiniSwapClient(api_key, api_secret) as client:
       tokens = client.get_cex_tokens()
   # Session automatically closed
   ```

This allows proper resource management and explicit cleanup.

