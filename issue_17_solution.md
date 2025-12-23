## Proposed Solution

1. **Use exception chaining** with `from e`:
   - Change `raise NetworkError(...)` to `raise NetworkError(...) from e`
   - Change `raise HoudiniSwapError(...)` to `raise HoudiniSwapError(...) from e`

2. **Preserve exception context**:
   - Original exception type and stack trace will be available via `__cause__`
   - Better debugging experience

This maintains the exception chain, allowing developers to see the root cause of errors.

