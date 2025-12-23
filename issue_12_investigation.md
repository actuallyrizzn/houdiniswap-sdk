## Investigation

Current code at `houdiniswap/client.py:108`:
```python
self.session = requests.Session()
```

**Issues found:**
1. Session is created but never explicitly closed
2. No `__enter__` / `__exit__` methods for context manager support
3. For long-running applications, sessions should be properly cleaned up
4. No way to manually close the session

**Impact:**
- While Python GC handles cleanup, explicit management is better practice
- Connection pools may not be released promptly
- No way to use `with client:` syntax

## Proposed Solution

1. Add `__enter__` and `__exit__` methods to support context manager protocol
2. In `__exit__`, explicitly close the session with `self.session.close()`
3. Add a public `close()` method for manual cleanup
4. Update docstrings to document context manager usage

