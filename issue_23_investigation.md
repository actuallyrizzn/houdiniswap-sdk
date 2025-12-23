## Investigation

Current code lacks comprehensive input validation:
- No validation that `amount > 0`
- No validation that addresses match expected format
- No validation that token IDs are non-empty
- No validation that `page > 0` and `page_size > 0`
- No validation that `houdini_id` format is correct
- No validation that `tx_hash` is a valid hex string

**Note:** We already have `_sanitize_input()` method, but need to add:
- Amount validation
- Address format validation (using Network.address_validation)
- Numeric range validation
- Format validation (hex strings, IDs)

## Proposed Solution

1. **Add validation helpers**:
   - `_validate_amount(amount)` - check > 0
   - `_validate_address(address, network)` - check format using regex
   - `_validate_page(page)` - check > 0
   - `_validate_hex_string(value, field_name)` - check hex format
   - `_validate_houdini_id(houdini_id)` - check format

2. **Apply validation to all public methods**:
   - Quote methods: validate amounts, tokens
   - Exchange methods: validate amounts, addresses, tokens
   - Status methods: validate houdini_id
   - DEX methods: validate tx_hash, transaction_id

3. **Use Network.address_validation** for address validation when network is known

