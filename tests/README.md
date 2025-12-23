# Houdini Swap SDK Test Suite

This directory contains comprehensive test coverage for the Houdini Swap SDK, including unit, integration, and end-to-end tests.

## Test Structure

```
tests/
├── conftest.py                    # Shared fixtures and configuration
├── unit/                          # Unit tests
│   ├── test_models.py            # Model class tests
│   ├── test_exceptions.py         # Exception class tests
│   ├── test_constants.py          # Constants tests
│   ├── test_client_helpers.py     # Client helper method tests
│   └── test_builder.py            # Builder pattern tests
├── integration/                   # Integration tests
│   ├── test_client_init.py        # Client initialization tests
│   ├── test_client_api_methods.py # API method tests
│   ├── test_client_error_handling.py # Error handling and retry tests
│   └── test_client_helpers.py     # Helper method integration tests
└── e2e/                           # End-to-end tests
    ├── test_cex_workflow.py       # Complete CEX exchange workflows
    ├── test_dex_workflow.py       # Complete DEX exchange workflows
    └── test_parallel_operations.py # Parallel operations and pagination
```

## Running Tests

### Install Dependencies

```bash
pip install -r requirements-dev.txt
```

### Run All Tests

```bash
pytest
```

### Run by Category

```bash
# Unit tests only
pytest tests/unit/

# Integration tests only
pytest tests/integration/

# E2E tests only
pytest tests/e2e/
```

### Run with Coverage

```bash
pytest --cov=houdiniswap --cov-report=html --cov-report=term-missing
```

This will generate:
- Terminal coverage report
- HTML coverage report in `htmlcov/index.html`
- XML coverage report for CI/CD

### Run Specific Test File

```bash
pytest tests/unit/test_models.py
```

### Run Specific Test

```bash
pytest tests/unit/test_models.py::TestToken::test_from_dict_complete
```

## Test Coverage

### Unit Tests (tests/unit/)

- **test_models.py**: Tests for all model classes
  - Network, Token, DEXToken, RouteDTO
  - Quote, DEXQuote, ExchangeResponse
  - DexApproveResponse, Status, MinMax
  - Volume, WeeklyVolume, DEXTokensResponse
  - All `from_dict()` methods
  - Validation logic
  - `__repr__` methods
  - Frozen dataclass behavior

- **test_exceptions.py**: Tests for exception classes
  - HoudiniSwapError (base)
  - AuthenticationError
  - APIError (with status_code and response)
  - ValidationError
  - NetworkError

- **test_constants.py**: Tests for constants
  - HTTP status codes
  - Default values
  - Endpoints
  - Error messages
  - API versioning

- **test_client_helpers.py**: Tests for client helper methods
  - Credential validation
  - Input sanitization
  - Amount validation and normalization
  - Token ID validation
  - Page validation
  - Hex string validation
  - Houdini ID validation
  - Address validation
  - Credential redaction

- **test_builder.py**: Tests for ExchangeBuilder
  - Fluent interface
  - CEX and DEX configuration
  - Parameter validation
  - Execute methods

### Integration Tests (tests/integration/)

- **test_client_init.py**: Client initialization
  - Credential handling
  - Base URL configuration
  - Timeout and retry settings
  - SSL verification
  - Caching configuration
  - Logging setup
  - Context manager support
  - Session management

- **test_client_api_methods.py**: All API methods
  - `get_cex_tokens()` - with caching
  - `get_dex_tokens()` - with pagination
  - `get_cex_quote()` - with all parameters
  - `get_dex_quote()` - with multiple routes
  - `post_cex_exchange()` - with optional params
  - `post_dex_exchange()` - with route
  - `post_dex_approve()` - with empty response
  - `post_dex_confirm_tx()` - with validation
  - `get_status()` - with houdini_id injection
  - `get_min_max()` - with cex_only
  - `get_volume()` - with dict/list responses
  - `get_weekly_volume()` - with dict/list responses

- **test_client_error_handling.py**: Error handling
  - Authentication errors (401)
  - API errors with messages
  - Network errors (connection, timeout)
  - Retry logic for retryable status codes
  - Retry backoff timing
  - No retry for non-retryable errors
  - Request/response logging
  - Credential redaction in logs
  - Defensive copying of parameters

- **test_client_helpers.py**: Helper methods
  - `iter_dex_tokens()` - pagination
  - `get_all_dex_tokens()` - convenience method
  - `wait_for_status()` - polling
  - `poll_until_finished()` - final status polling
  - `execute_parallel()` - parallel requests
  - `clear_cache()` - cache management
  - `exchange_builder()` - builder creation

### E2E Tests (tests/e2e/)

- **test_cex_workflow.py**: Complete CEX workflows
  - Full exchange flow: tokens → quote → exchange → status
  - Exchange with builder pattern
  - Min/max validation workflow
  - Anonymous exchange flow
  - Exchange with receiver tag
  - Error scenarios (invalid token, amount too low, invalid address)

- **test_dex_workflow.py**: Complete DEX workflows
  - Full exchange flow: tokens → quote → approve → exchange → confirm → status
  - Exchange without approval needed
  - Exchange with transaction confirmation
  - Multiple quote selection
  - Error scenarios (expired quote, invalid route)

- **test_parallel_operations.py**: Parallel operations
  - Parallel token queries
  - Parallel status checks
  - Parallel quotes
  - Parallel operations with errors
  - Iteration and pagination helpers

## Test Fixtures

All fixtures are defined in `conftest.py`:

- `api_key`, `api_secret`: Test credentials
- `client`: HoudiniSwapClient instance
- `mock_session`: Mock requests.Session
- `sample_*_data`: Sample API response data for all models

## Coverage Goals

The test suite aims for **100% code coverage** across:
- ✅ All model classes and methods
- ✅ All exception classes
- ✅ All client API methods
- ✅ All helper methods
- ✅ All validation logic
- ✅ All error handling paths
- ✅ All retry logic
- ✅ All caching functionality
- ✅ Complete workflows (CEX and DEX)
- ✅ Parallel operations
- ✅ Edge cases and error scenarios

## Continuous Integration

The test suite is configured to:
- Run automatically on CI/CD
- Generate coverage reports
- Fail if coverage drops below 100%
- Run with pytest markers for categorization

## Notes

- All tests use mocked API responses (no real API calls)
- Tests are designed to be fast and deterministic
- E2E tests simulate complete workflows but still use mocks
- Time-based operations use `time.sleep` mocking for speed
- Parallel operations are tested with ThreadPoolExecutor
