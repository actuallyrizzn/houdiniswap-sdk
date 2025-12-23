# Migration Guide

This guide helps you migrate between different versions of the Houdini Swap Python SDK.

## Version 0.1.0

This is the initial release of the SDK. No migration is needed if you're starting fresh.

### Breaking Changes

None - this is the first release.

### New Features

- Complete API coverage (12 endpoints)
- Type-safe data models
- Comprehensive error handling
- Full type hints

---

## Future Versions

When new versions are released, migration instructions will be added here.

### Planned Changes

- Async support (will be additive, not breaking)
- Enhanced type safety (may require minor code updates)
- Additional convenience methods (additive)

---

## General Migration Tips

### Updating Dependencies

Always update dependencies in a controlled environment:

```bash
# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install specific version
pip install houdiniswap-sdk==0.1.0

# Or update to latest
pip install --upgrade houdiniswap-sdk
```

### Testing After Migration

After updating the SDK version:

1. Run your test suite
2. Check for deprecation warnings
3. Review the changelog for breaking changes
4. Test critical paths in your application

### Handling Deprecations

If you see deprecation warnings:

1. Check the changelog for migration instructions
2. Update your code to use the new API
3. Test thoroughly before deploying

### Getting Help

If you encounter issues during migration:

1. Check the [API Reference](API_REFERENCE.md)
2. Review [Error Handling examples](../README.md#error-handling)
3. Open an issue on GitHub with:
   - Your current SDK version
   - Target SDK version
   - Error messages or unexpected behavior
   - Minimal code example

---

## Version Compatibility

### Python Version Support

- **0.1.0+**: Python 3.8+

### API Compatibility

The SDK follows semantic versioning:
- **Major version** changes may include breaking API changes
- **Minor version** changes add new features (backward compatible)
- **Patch version** changes are bug fixes (backward compatible)

### Backward Compatibility Policy

- We maintain backward compatibility within major versions
- Deprecated features will be marked and removed in the next major version
- At least one minor version will pass between deprecation and removal

