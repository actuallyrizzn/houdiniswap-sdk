## Investigation

Current code:
- Only basic auth (ApiKey:ApiSecret in Authorization header)
- No request signing, nonces, or timestamp validation
- If API adds these requirements, SDK breaks

**Note:** The API currently only requires basic auth. Request signing would be needed if the API adds it in the future.

## Proposed Solution

1. **Add extensible authentication mechanism**:
   - Create `_sign_request()` method (currently no-op)
   - Add hooks for future request signing
   - Document that signing can be added if API requires it

2. **Add authentication adapter pattern**:
   - Allow custom authentication methods
   - Prepare for future signing requirements

Since the API doesn't currently require signing, we'll add infrastructure to support it when needed.

