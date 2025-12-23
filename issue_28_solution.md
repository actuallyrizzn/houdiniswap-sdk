## Proposed Solution

1. **Support environment variable**:
   - Check `HOUDINI_SWAP_API_URL` environment variable
   - Fall back to default production URL if not set

2. **Update `__init__`**:
   - Check environment variable first
   - Then check `base_url` parameter
   - Finally use default from constants

3. **Update constants.py**:
   - Add `BASE_URL_PRODUCTION` constant
   - Add `ENV_VAR_API_URL` constant for environment variable name

This allows easy configuration for different environments without code changes.

