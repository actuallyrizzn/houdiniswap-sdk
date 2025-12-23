## Proposed Solution

1. **Add retry configuration** to `__init__`:
   - `max_retries: int = 3` (default)
   - `retry_backoff_factor: float = 1.0` (exponential backoff multiplier)

2. **Implement retry logic in `_request()`**:
   - Retry on `NetworkError` (transient network failures)
   - Retry on 5xx server errors (500, 502, 503, 504)
   - Retry on 429 rate limit errors with exponential backoff
   - Don't retry on 4xx client errors (except 429)
   - Use exponential backoff: `wait_time = retry_backoff_factor * (2 ** attempt)`

3. **Log retry attempts** for debugging

This provides automatic retry for transient failures, reducing the need for users to implement their own retry logic.

