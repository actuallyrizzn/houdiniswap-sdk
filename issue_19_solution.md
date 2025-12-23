## Proposed Solution

1. **Add validation to `from_dict()` methods**:
   - Check that input is a dict: `if not isinstance(data, dict): raise ValidationError(...)`
   - Validate required fields exist
   - For Status model, validate TransactionStatus enum value

2. **Focus on critical models first**:
   - Network (required: name, shortName, addressValidation)
   - Token (required: id, name, symbol, network)
   - ExchangeResponse (required: houdiniId, status)
   - DexApproveResponse (required: data, to, from)
   - Status (required: houdiniId, status)

3. **Raise `ValidationError`** with descriptive messages indicating missing fields

This prevents silent failures and provides clear error messages when API responses are malformed.

