## Investigation

Current code:
- `get_cex_tokens()` and `get_dex_tokens()` make API calls every time
- Token lists probably don't change frequently
- No caching means:
  - Unnecessary API calls
  - Slower responses
  - Higher API usage costs
  - No TTL management

## Proposed Solution

1. **Add simple in-memory cache**:
   - Use `functools.lru_cache` or custom cache with TTL
   - Cache token lists with configurable TTL (default: 5 minutes)

2. **Add cache configuration**:
   - `cache_enabled: bool = True` (default)
   - `cache_ttl: int = 300` (5 minutes in seconds)

3. **Implement caching for**:
   - `get_cex_tokens()` - cache token list
   - `get_dex_tokens()` - cache DEX token list

4. **Add cache invalidation**:
   - `clear_cache()` method to manually invalidate
   - Automatic expiration based on TTL

5. **Consider thread-safety**:
   - Use thread-safe cache if needed
   - Or document that cache is per-instance

