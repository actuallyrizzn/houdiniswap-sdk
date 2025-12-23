## Proposed Solution

1. **Add simple in-memory cache**:
   - Use dictionary with timestamps: `_token_cache: Dict[str, tuple]`
   - Cache key -> (data, timestamp)

2. **Add cache configuration**:
   - `cache_enabled: bool = True` (default)
   - `cache_ttl: int = 300` (5 minutes in seconds)

3. **Implement caching for**:
   - `get_cex_tokens()` - cache token list
   - `get_dex_tokens()` - cache DEX token list (with parameters in cache key)

4. **Add cache invalidation**:
   - `clear_cache()` method to manually invalidate
   - Automatic expiration based on TTL

5. **Log cache hits/misses** for debugging

This reduces unnecessary API calls and improves response times for frequently accessed token lists.

