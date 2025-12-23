## Investigation

Current code at `houdiniswap/client.py:155-162`:
```python
if response.status_code >= HTTP_STATUS_BAD_REQUEST:
    try:
        error_data = response.json()
        error_message = error_data.get("message", f"API error: {response.status_code}")
    except ValueError:
        error_message = f"API error: {response.status_code} - {response.text}"
    
    raise APIError(
        error_message,
        status_code=response.status_code,
        response=error_data if 'error_data' in locals() else None,
    )
```

**Issues found:**
1. `error_data` might not exist in `locals()` when referenced
2. If JSON parsing fails, error structure is lost
3. No logging of actual error response for debugging
4. Silent failure - no indication that JSON parsing failed

## Proposed Solution

1. Initialize `error_data = None` before the try block
2. Always use `error_data` variable (never check `locals()`)
3. Include raw response text in error message when JSON parsing fails
4. Consider logging the error response (with credential redaction) for debugging

