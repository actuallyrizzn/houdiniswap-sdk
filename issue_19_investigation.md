## Investigation

All `from_dict()` methods in `houdiniswap/models.py` blindly accept dictionaries:
- `Token.from_dict({})` creates a Token with all empty strings
- No validation that required fields exist
- No type checking of field values
- No schema validation

**Example problem:**
```python
Token.from_dict({})  # Creates invalid Token with empty strings
```

## Proposed Solution

1. Add validation to `from_dict()` methods:
   - Check that required fields exist
   - Validate field types
   - Raise `ValidationError` for invalid data

2. Create a base validation helper or use a validation library approach

3. For critical models, add `@classmethod validate()` methods

4. Consider using `TypedDict` for better type checking

