"""Integration tests for client initialization."""

import pytest
import os
from unittest.mock import patch, MagicMock

from houdiniswap import HoudiniSwapClient
from houdiniswap.exceptions import ValidationError


class TestClientInitialization:
    """Tests for HoudiniSwapClient initialization."""
    
    def test_init_with_credentials(self, api_key, api_secret):
        """Test initializing client with credentials."""
        client = HoudiniSwapClient(api_key, api_secret)
        assert client.base_url == "https://api-partner.houdiniswap.com"
        assert client.timeout == 30
        assert client.api_version == "v1"
        assert client.verify_ssl is True
    
    def test_init_with_custom_base_url(self, api_key, api_secret):
        """Test initializing client with custom base URL."""
        custom_url = "https://custom-api.example.com"
        client = HoudiniSwapClient(api_key, api_secret, base_url=custom_url)
        assert client.base_url == custom_url
    
    def test_init_with_env_var_base_url(self, api_key, api_secret):
        """Test initializing client with base URL from environment variable."""
        env_url = "https://env-api.example.com"
        with patch.dict(os.environ, {"HOUDINI_SWAP_API_URL": env_url}):
            client = HoudiniSwapClient(api_key, api_secret)
            assert client.base_url == env_url
    
    def test_init_with_custom_timeout(self, api_key, api_secret):
        """Test initializing client with custom timeout."""
        client = HoudiniSwapClient(api_key, api_secret, timeout=60)
        assert client.timeout == 60
    
    def test_init_with_custom_api_version(self, api_key, api_secret):
        """Test initializing client with custom API version."""
        client = HoudiniSwapClient(api_key, api_secret, api_version="v2")
        assert client.api_version == "v2"
    
    def test_init_with_ssl_verification_disabled(self, api_key, api_secret):
        """Test initializing client with SSL verification disabled."""
        client = HoudiniSwapClient(api_key, api_secret, verify_ssl=False)
        assert client.verify_ssl is False
    
    def test_init_with_retry_config(self, api_key, api_secret):
        """Test initializing client with retry configuration."""
        client = HoudiniSwapClient(
            api_key,
            api_secret,
            max_retries=5,
            retry_backoff_factor=2.0
        )
        assert client.max_retries == 5
        assert client.retry_backoff_factor == 2.0
    
    def test_init_with_caching(self, api_key, api_secret):
        """Test initializing client with caching enabled."""
        client = HoudiniSwapClient(
            api_key,
            api_secret,
            cache_enabled=True,
            cache_ttl=600
        )
        assert client.cache_enabled is True
        assert client.cache_ttl == 600
    
    def test_init_with_logging(self, api_key, api_secret):
        """Test initializing client with logging."""
        import logging
        client = HoudiniSwapClient(api_key, api_secret, log_level=logging.DEBUG)
        assert client.logger.level == logging.DEBUG
    
    def test_init_empty_api_key_raises(self, api_secret):
        """Test that empty API key raises ValidationError."""
        with pytest.raises(ValidationError, match="API key and secret are required"):
            HoudiniSwapClient("", api_secret)
    
    def test_init_empty_api_secret_raises(self, api_key):
        """Test that empty API secret raises ValidationError."""
        with pytest.raises(ValidationError, match="API key and secret are required"):
            HoudiniSwapClient(api_key, "")
    
    def test_init_none_api_key_raises(self, api_secret):
        """Test that None API key raises ValidationError."""
        with pytest.raises(ValidationError):
            HoudiniSwapClient(None, api_secret)
    
    def test_init_credentials_not_accessible(self, client):
        """Test that credentials cannot be accessed directly."""
        with pytest.raises(AttributeError, match="has no attribute 'api_key'"):
            _ = client.api_key
        with pytest.raises(AttributeError, match="has no attribute 'api_secret'"):
            _ = client.api_secret
    
    def test_repr(self, client):
        """Test client string representation."""
        repr_str = repr(client)
        assert "HoudiniSwapClient" in repr_str
        assert "base_url" in repr_str
        assert "api_key" not in repr_str.lower()  # Should not expose credentials
    
    def test_context_manager(self, api_key, api_secret):
        """Test client as context manager."""
        with HoudiniSwapClient(api_key, api_secret) as client:
            assert isinstance(client, HoudiniSwapClient)
            # Session should be open
            assert client.session is not None
        # After context exit, session should be closed
        assert client.session.closed
    
    def test_close(self, client):
        """Test closing client session."""
        assert client.session is not None
        client.close()
        assert client.session.closed
    
    def test_session_headers(self, client):
        """Test that session headers are set correctly."""
        assert "Authorization" in client.session.headers
        assert "Content-Type" in client.session.headers
        assert client.session.headers["Content-Type"] == "application/json"
        # Authorization should contain credentials (but we can't check exact value)
        auth_header = client.session.headers["Authorization"]
        assert ":" in auth_header  # Format: key:secret
    
    def test_session_ssl_verification(self, api_key, api_secret):
        """Test that session SSL verification is set correctly."""
        client_verify = HoudiniSwapClient(api_key, api_secret, verify_ssl=True)
        assert client_verify.session.verify is True
        
        client_no_verify = HoudiniSwapClient(api_key, api_secret, verify_ssl=False)
        assert client_no_verify.session.verify is False
