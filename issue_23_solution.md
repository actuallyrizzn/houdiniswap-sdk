## Proposed Solution

1. **Add validation helper methods**:
   - `_validate_amount(amount, field_name)` - check > 0
   - `_validate_address(address, network=None)` - check format using regex
   - `_validate_page(page)` - check > 0
   - `_validate_page_size(page_size)` - check > 0
   - `_validate_hex_string(value, field_name)` - check hex format
   - `_validate_houdini_id(houdini_id)` - check format (alphanumeric, length)
   - `_validate_token_id(token_id)` - check non-empty

2. **Apply validation to all public methods**:
   - Quote methods: validate amounts, tokens
   - Exchange methods: validate amounts, addresses, tokens
   - Status methods: validate houdini_id
   - DEX methods: validate tx_hash, transaction_id, page/page_size
   - Token methods: validate page/page_size

3. **Use Network.address_validation** when network is known:
   - For CEX exchanges, validate addresses against token network
   - For DEX exchanges, validate against known formats

This ensures all inputs are validated before API calls.

