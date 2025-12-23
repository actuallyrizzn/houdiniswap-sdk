## Investigation

Current code:
- User inputs go directly to API with no sanitization
- Could lead to injection attacks, header injection, URL manipulation

**Examples:**
- Addresses not validated against network format
- Amounts not validated (could be negative, zero, etc.)
- Token IDs not validated
- Strings not sanitized

## Proposed Solution

1. **Add input validation helper** `_sanitize_input()`:
   - Strip whitespace
   - Validate format (addresses, amounts, etc.)
   - Raise `ValidationError` for invalid inputs

2. **Add validation to public methods**:
   - Validate addresses match expected format
   - Validate amounts > 0
   - Validate token IDs are non-empty
   - Sanitize string inputs

3. **Use existing Network.address_validation** for address validation

