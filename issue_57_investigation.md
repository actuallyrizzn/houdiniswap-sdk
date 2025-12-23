## Investigation

Current code:
- `get_status()` requires manual polling
- Users must implement their own polling loop
- No convenience methods for waiting for status changes

## Proposed Solution

1. **Add `wait_for_status()` method**:
   - Polls `get_status()` until desired status is reached
   - Configurable timeout and polling interval
   - Raises timeout error if status not reached

2. **Add `poll_until_finished()` method**:
   - Waits until transaction is FINISHED, FAILED, or EXPIRED
   - Returns final status
   - Configurable timeout

3. **Add status change callbacks** (optional):
   - Callback function called on status changes
   - Useful for progress tracking

