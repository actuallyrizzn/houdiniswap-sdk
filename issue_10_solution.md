## Proposed Solution

1. **Add credential validation method** `_validate_credentials()`:
   - Check for `:` character in credentials (would break Authorization header)
   - Validate length (max 1000 chars to stay well under HTTP header limits)
   - Check for empty/whitespace-only credentials

2. **Call validation in `__init__`** before storing credentials

3. **Raise `ValidationError`** with clear messages for invalid credentials

This ensures credentials are validated at initialization time, preventing runtime authentication failures.

