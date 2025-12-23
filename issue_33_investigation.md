## Investigation

Current code:
- No API version in requests
- If API changes, SDK breaks
- No version negotiation

## Proposed Solution

1. **Add API version header**:
   - Add `X-API-Version` header (or similar)
   - Default to latest version
   - Make configurable via `api_version` parameter

2. **Add version constant**:
   - `API_VERSION = "v1"` in constants.py
   - Allow override in `__init__`

3. **Document version support**:
   - Update docstrings to mention versioning

