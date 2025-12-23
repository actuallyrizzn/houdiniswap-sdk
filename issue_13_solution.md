## Proposed Solution

1. **Create RouteDTO model**:
   - Based on API documentation structure
   - Include common fields (bridge, steps, etc.)
   - Keep flexible for dynamic route data

2. **Update ExchangeResponse**:
   - `quote: Optional[Quote]` - parse quote object into Quote model
   - `out_token: Optional[Token]` - parse outToken into Token model
   - `in_token: Optional[Token]` - parse inToken into Token model
   - Keep `metadata` as `Dict[str, Any]` (truly dynamic)

3. **Update method signatures**:
   - `post_dex_exchange(route: RouteDTO)` 
   - `post_dex_approve(route: RouteDTO)`
   - Update builder.py to use RouteDTO

4. **Update from_dict methods**:
   - Parse nested objects when present
   - Handle None/missing gracefully

This improves type safety while maintaining backward compatibility.

