## Investigation

Current code:
- Exchange methods have many parameters
- `post_cex_exchange()` has 10+ parameters
- `post_dex_exchange()` has 7+ parameters
- No builder pattern for complex requests

## Proposed Solution

1. **Add `ExchangeBuilder` class**:
   - Fluent interface for building exchange requests
   - Validates before sending
   - Manages default values

2. **Example usage**:
   ```python
   exchange = client.exchange_builder() \
       .cex() \
       .amount(1.0) \
       .from_token("ETH") \
       .to_token("BNB") \
       .address_to("0x...") \
       .anonymous(True) \
       .execute()
   ```

3. **Add validation**:
   - Validate all required fields before sending
   - Provide clear error messages

