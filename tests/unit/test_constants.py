"""Unit tests for constants."""

import os
from houdiniswap import constants


class TestConstants:
    """Tests for constant values."""
    
    def test_http_status_codes(self):
        """Test HTTP status code constants."""
        assert constants.HTTP_STATUS_OK == 200
        assert constants.HTTP_STATUS_BAD_REQUEST == 400
        assert constants.HTTP_STATUS_UNAUTHORIZED == 401
        assert constants.HTTP_STATUS_NOT_FOUND == 404
        assert constants.HTTP_STATUS_TOO_MANY_REQUESTS == 429
        assert constants.HTTP_STATUS_INTERNAL_SERVER_ERROR == 500
        assert constants.HTTP_STATUS_BAD_GATEWAY == 502
        assert constants.HTTP_STATUS_SERVICE_UNAVAILABLE == 503
        assert constants.HTTP_STATUS_GATEWAY_TIMEOUT == 504
    
    def test_default_values(self):
        """Test default configuration values."""
        assert constants.DEFAULT_TIMEOUT == 30
        assert constants.DEFAULT_PAGE_SIZE == 100
        assert constants.DEFAULT_MAX_RETRIES == 3
        assert constants.DEFAULT_RETRY_BACKOFF_FACTOR == 1.0
        assert constants.DEFAULT_CACHE_TTL == 300
    
    def test_base_url(self):
        """Test base URL constant."""
        assert constants.BASE_URL_PRODUCTION == "https://api-partner.houdiniswap.com"
        assert isinstance(constants.BASE_URL_PRODUCTION, str)
    
    def test_env_var_name(self):
        """Test environment variable name."""
        assert constants.ENV_VAR_API_URL == "HOUDINI_SWAP_API_URL"
    
    def test_endpoints(self):
        """Test endpoint constants."""
        endpoints = [
            constants.ENDPOINT_TOKENS,
            constants.ENDPOINT_DEX_TOKENS,
            constants.ENDPOINT_QUOTE,
            constants.ENDPOINT_DEX_QUOTE,
            constants.ENDPOINT_EXCHANGE,
            constants.ENDPOINT_DEX_EXCHANGE,
            constants.ENDPOINT_DEX_APPROVE,
            constants.ENDPOINT_DEX_CONFIRM_TX,
            constants.ENDPOINT_STATUS,
            constants.ENDPOINT_MIN_MAX,
            constants.ENDPOINT_VOLUME,
            constants.ENDPOINT_WEEKLY_VOLUME,
        ]
        for endpoint in endpoints:
            assert isinstance(endpoint, str)
            assert endpoint.startswith("/")
    
    def test_error_messages(self):
        """Test error message constants."""
        assert isinstance(constants.ERROR_INVALID_CREDENTIALS, str)
        assert isinstance(constants.ERROR_AUTHENTICATION_FAILED, str)
        assert isinstance(constants.ERROR_NETWORK, str)
        assert isinstance(constants.ERROR_UNEXPECTED, str)
        assert "{}" in constants.ERROR_NETWORK  # Format string
        assert "{}" in constants.ERROR_UNEXPECTED  # Format string
    
    def test_api_versioning(self):
        """Test API versioning constants."""
        assert constants.API_VERSION_DEFAULT == "v1"
        assert constants.HEADER_API_VERSION == "X-API-Version"
