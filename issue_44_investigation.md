## Investigation

Current code:
- Each API call is separate
- No support for batch requests
- No parallel request execution
- No request queuing

**Note:** The Houdini Swap API doesn't appear to support batch requests. This would require API support.

## Proposed Solution

1. **Add request queuing helper** (if needed):
   - Queue multiple requests
   - Execute sequentially with rate limiting

2. **Document limitations**:
   - API doesn't support batch requests
   - Users can use threading/async for parallel requests

3. **Add helper for parallel requests** (using threading):
   - `execute_parallel()` method
   - Takes list of callables
   - Executes in parallel with thread pool

Since the API doesn't support true batching, we'll add utilities for parallel execution.

