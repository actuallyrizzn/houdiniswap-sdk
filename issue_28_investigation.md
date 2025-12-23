## Investigation

Current code at `houdiniswap/client.py:81`:
```python
BASE_URL = "https://api-partner.houdiniswap.com"
```

**Issues:**
- Hardcoded base URL (class variable)
- No support for different environments (dev/staging/prod)
- Not configurable via environment variable
- Users can override via `base_url` parameter, but no standard way

## Proposed Solution

1. **Support environment variable**:
   - Check `HOUDINI_SWAP_API_URL` environment variable
   - Fall back to default production URL if not set

2. **Add environment presets**:
   - `production` (default): `https://api-partner.houdiniswap.com`
   - `staging`: `https://api-staging.houdiniswap.com` (if exists)
   - `development`: `https://api-dev.houdiniswap.com` (if exists)

3. **Update `__init__`**:
   - Check environment variable first
   - Then check `base_url` parameter
   - Finally use default

4. **Update constants.py**:
   - Add environment variable name constant
   - Document environment variable usage

