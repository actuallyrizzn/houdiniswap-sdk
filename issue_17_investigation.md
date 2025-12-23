## Investigation

Current code at `houdiniswap/client.py:175-179`:
```python
except requests.exceptions.RequestException as e:
    raise NetworkError(ERROR_NETWORK.format(str(e)))
except (APIError, AuthenticationError):
    raise
except Exception as e:
    raise HoudiniSwapError(ERROR_UNEXPECTED.format(str(e)))
```

**Issues found:**
1. Generic exceptions are converted to `HoudiniSwapError` without chaining
2. Original exception context and stack trace are lost
3. No `raise ... from e` to preserve exception chain
4. Makes debugging difficult - can't see original exception type

## Proposed Solution

1. Use exception chaining: `raise HoudiniSwapError(...) from e`
2. Preserve original exception type information in error message
3. Ensure all exception conversions maintain the chain
4. This allows `__cause__` to be inspected for debugging

