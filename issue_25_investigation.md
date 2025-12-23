## Investigation

Current code at `houdiniswap/client.py:_request()`:
- No retry logic for transient network failures
- No exponential backoff
- Users must implement their own retry logic (examples in README)

**Issues:**
- Network requests can fail transiently (DNS, connection timeouts, etc.)
- 5xx server errors should be retried
- 429 rate limit errors should be retried with backoff
- No automatic retry mechanism

## Proposed Solution

1. **Add retry configuration** to `__init__`:
   - `max_retries: int = 3` (default)
   - `retry_backoff_factor: float = 1.0` (exponential backoff multiplier)
   - `retry_on_status: List[int] = [429, 500, 502, 503, 504]` (status codes to retry)

2. **Implement retry logic in `_request()`**:
   - Retry on `NetworkError` (transient network failures)
   - Retry on 5xx server errors
   - Retry on 429 rate limit errors with exponential backoff
   - Don't retry on 4xx client errors (except 429)
   - Use exponential backoff: `wait_time = retry_backoff_factor * (2 ** attempt)`

3. **Add `urllib3` retry adapter** (optional, but recommended):
   - Use `requests.adapters.HTTPAdapter` with `urllib3.util.retry.Retry`
   - More robust and handles connection pooling

