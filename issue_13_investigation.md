## Investigation

Current code uses `Dict[str, Any]` in multiple places:
1. `post_dex_exchange()` and `post_dex_approve()` accept `route: Dict[str, Any]`
2. `ExchangeResponse` has `quote: Optional[Dict[str, Any]]` instead of `Optional[Quote]`
3. `ExchangeResponse` has `out_token`, `in_token`, `metadata` as `Dict[str, Any]`
4. `DEXQuote` has `raw: Optional[Dict[str, Any]]` (this might be intentional for raw route data)
5. `DexApproveResponse` has `from_chain: Optional[Dict[str, Any]]`

**Issues:**
- No type safety for route objects
- Quote in ExchangeResponse should use Quote model
- Token objects should use Token/DEXToken models

## Proposed Solution

1. **Create RouteDTO model** for route data:
   - Based on API documentation structure
   - Used in DEX exchange and approve operations

2. **Update ExchangeResponse**:
   - `quote: Optional[Quote]` instead of `Dict[str, Any]`
   - `out_token: Optional[Token]` instead of `Dict[str, Any]`
   - `in_token: Optional[Token]` instead of `Dict[str, Any]`
   - Keep `metadata` as `Dict[str, Any]` if it's truly dynamic

3. **Update method signatures**:
   - `post_dex_exchange(route: RouteDTO)` instead of `Dict[str, Any]`
   - `post_dex_approve(route: RouteDTO)` instead of `Dict[str, Any]`

4. **Update from_dict methods**:
   - Parse nested objects into proper models
   - Handle missing/None values gracefully

