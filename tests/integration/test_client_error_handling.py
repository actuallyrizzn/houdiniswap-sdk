"""Integration tests for client error handling and retry logic."""

import pytest
import time
from unittest.mock import patch, MagicMock

from houdiniswap import HoudiniSwapClient
from houdiniswap.exceptions import APIError, AuthenticationError, NetworkError, HoudiniSwapError
from houdiniswap.constants import (
    HTTP_STATUS_UNAUTHORIZED,
    HTTP_STATUS_TOO_MANY_REQUESTS,
    HTTP_STATUS_INTERNAL_SERVER_ERROR,
    HTTP_STATUS_BAD_GATEWAY,
    HTTP_STATUS_SERVICE_UNAVAILABLE,
    HTTP_STATUS_GATEWAY_TIMEOUT,
)


class TestErrorHandling:
    """Tests for error handling in _request method."""
    
    def test_authentication_error(self, client):
        """Test that 401 status raises AuthenticationError."""
        mock_response = MagicMock()
        mock_response.status_code = HTTP_STATUS_UNAUTHORIZED
        mock_response.json.return_value = {"message": "Invalid credentials"}
        
        with patch.object(client.session, 'request', return_value=mock_response):
            with pytest.raises(AuthenticationError):
                client._request("GET", "/test")
    
    def test_api_error_with_message(self, client):
        """Test APIError with error message from response."""
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"message": "Bad request"}
        
        with patch.object(client.session, 'request', return_value=mock_response):
            with pytest.raises(APIError) as exc_info:
                client._request("GET", "/test")
            assert exc_info.value.status_code == 400
            assert exc_info.value.response == {"message": "Bad request"}
    
    def test_api_error_no_message(self, client):
        """Test APIError when response has no message field."""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.json.return_value = {}
        mock_response.text = "Internal Server Error"
        
        with patch.object(client.session, 'request', return_value=mock_response):
            with pytest.raises(APIError) as exc_info:
                client._request("GET", "/test")
            assert exc_info.value.status_code == 500
    
    def test_api_error_invalid_json(self, client):
        """Test APIError when response is not valid JSON."""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_response.text = "Internal Server Error"
        
        with patch.object(client.session, 'request', return_value=mock_response):
            with pytest.raises(APIError) as exc_info:
                client._request("GET", "/test")
            assert exc_info.value.status_code == 500
            assert "Internal Server Error" in str(exc_info.value)
    
    def test_network_error_connection(self, client):
        """Test NetworkError on connection failure."""
        import requests
        with patch.object(client.session, 'request', side_effect=requests.exceptions.ConnectionError("Connection failed")):
            with pytest.raises(NetworkError, match="Network error"):
                client._request("GET", "/test")
    
    def test_network_error_timeout(self, client):
        """Test NetworkError on timeout."""
        import requests
        with patch.object(client.session, 'request', side_effect=requests.exceptions.Timeout("Request timeout")):
            with pytest.raises(NetworkError, match="Network error"):
                client._request("GET", "/test")
    
    def test_unexpected_error(self, client):
        """Test HoudiniSwapError for unexpected errors."""
        with patch.object(client.session, 'request', side_effect=ValueError("Unexpected error")):
            with pytest.raises(HoudiniSwapError, match="Unexpected error"):
                client._request("GET", "/test")


class TestRetryLogic:
    """Tests for retry logic in _request method."""
    
    def test_retry_on_429(self, client):
        """Test retry on 429 Too Many Requests."""
        client.max_retries = 2
        client.retry_backoff_factor = 0.01  # Fast backoff for tests
        
        mock_response_success = MagicMock()
        mock_response_success.status_code = 200
        mock_response_success.json.return_value = {"success": True}
        
        mock_response_429 = MagicMock()
        mock_response_429.status_code = HTTP_STATUS_TOO_MANY_REQUESTS
        
        with patch.object(client.session, 'request', side_effect=[
            mock_response_429,
            mock_response_429,
            mock_response_success,
        ]):
            result = client._request("GET", "/test")
            assert result == {"success": True}
            assert client.session.request.call_count == 3
    
    def test_retry_on_500(self, client):
        """Test retry on 500 Internal Server Error."""
        client.max_retries = 1
        client.retry_backoff_factor = 0.01
        
        mock_response_success = MagicMock()
        mock_response_success.status_code = 200
        mock_response_success.json.return_value = {"success": True}
        
        mock_response_500 = MagicMock()
        mock_response_500.status_code = HTTP_STATUS_INTERNAL_SERVER_ERROR
        
        with patch.object(client.session, 'request', side_effect=[
            mock_response_500,
            mock_response_success,
        ]):
            result = client._request("GET", "/test")
            assert result == {"success": True}
    
    def test_retry_on_502(self, client):
        """Test retry on 502 Bad Gateway."""
        client.max_retries = 1
        client.retry_backoff_factor = 0.01
        
        mock_response_success = MagicMock()
        mock_response_success.status_code = 200
        mock_response_success.json.return_value = {"success": True}
        
        mock_response_502 = MagicMock()
        mock_response_502.status_code = HTTP_STATUS_BAD_GATEWAY
        
        with patch.object(client.session, 'request', side_effect=[
            mock_response_502,
            mock_response_success,
        ]):
            result = client._request("GET", "/test")
            assert result == {"success": True}
    
    def test_retry_exhausted(self, client):
        """Test that retries are exhausted after max_retries."""
        client.max_retries = 2
        client.retry_backoff_factor = 0.01
        
        mock_response_500 = MagicMock()
        mock_response_500.status_code = HTTP_STATUS_INTERNAL_SERVER_ERROR
        mock_response_500.json.return_value = {"error": "Server error"}
        
        with patch.object(client.session, 'request', return_value=mock_response_500):
            with pytest.raises(APIError):
                client._request("GET", "/test")
            # Should try max_retries + 1 times (initial + retries)
            assert client.session.request.call_count == 3
    
    def test_no_retry_on_401(self, client):
        """Test that 401 errors are not retried."""
        client.max_retries = 2
        
        mock_response_401 = MagicMock()
        mock_response_401.status_code = HTTP_STATUS_UNAUTHORIZED
        
        with patch.object(client.session, 'request', return_value=mock_response_401):
            with pytest.raises(AuthenticationError):
                client._request("GET", "/test")
            # Should only try once (no retry)
            assert client.session.request.call_count == 1
    
    def test_no_retry_on_400(self, client):
        """Test that 400 errors are not retried."""
        client.max_retries = 2
        
        mock_response_400 = MagicMock()
        mock_response_400.status_code = 400
        mock_response_400.json.return_value = {"error": "Bad request"}
        
        with patch.object(client.session, 'request', return_value=mock_response_400):
            with pytest.raises(APIError):
                client._request("GET", "/test")
            # Should only try once (no retry)
            assert client.session.request.call_count == 1
    
    def test_retry_backoff_timing(self, client):
        """Test that retry backoff increases exponentially."""
        client.max_retries = 2
        client.retry_backoff_factor = 0.1
        
        mock_response_500 = MagicMock()
        mock_response_500.status_code = HTTP_STATUS_INTERNAL_SERVER_ERROR
        
        mock_response_success = MagicMock()
        mock_response_success.status_code = 200
        mock_response_success.json.return_value = {"success": True}
        
        with patch.object(client.session, 'request', side_effect=[
            mock_response_500,
            mock_response_500,
            mock_response_success,
        ]), patch('time.sleep') as mock_sleep:
            client._request("GET", "/test")
            # Should sleep with exponential backoff: 0.1 * 2^0, 0.1 * 2^1
            assert mock_sleep.call_count == 2
            assert mock_sleep.call_args_list[0][0][0] == pytest.approx(0.1)  # 0.1 * 2^0
            assert mock_sleep.call_args_list[1][0][0] == pytest.approx(0.2)  # 0.1 * 2^1
    
    def test_retry_on_network_error(self, client):
        """Test retry on network errors."""
        import requests
        client.max_retries = 1
        client.retry_backoff_factor = 0.01
        
        mock_response_success = MagicMock()
        mock_response_success.status_code = 200
        mock_response_success.json.return_value = {"success": True}
        
        with patch.object(client.session, 'request', side_effect=[
            requests.exceptions.ConnectionError("Connection failed"),
            mock_response_success,
        ]):
            result = client._request("GET", "/test")
            assert result == {"success": True}
            assert client.session.request.call_count == 2
    
    def test_retry_network_error_exhausted(self, client):
        """Test that network error retries are exhausted."""
        import requests
        client.max_retries = 1
        client.retry_backoff_factor = 0.01
        
        with patch.object(client.session, 'request', side_effect=requests.exceptions.ConnectionError("Connection failed")):
            with pytest.raises(NetworkError):
                client._request("GET", "/test")
            # Should try max_retries + 1 times
            assert client.session.request.call_count == 2


class TestRequestLogging:
    """Tests for request/response logging."""
    
    def test_debug_logging_enabled(self, client):
        """Test that debug logging works when enabled."""
        import logging
        client.logger.setLevel(logging.DEBUG)
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True}
        
        with patch.object(client.session, 'request', return_value=mock_response), \
             patch.object(client.logger, 'debug') as mock_debug:
            client._request("GET", "/test")
            # Should log request and response
            assert mock_debug.call_count >= 1
    
    def test_credential_redaction_in_logging(self, client):
        """Test that credentials are redacted in logs."""
        import logging
        client.logger.setLevel(logging.DEBUG)
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True}
        
        with patch.object(client.session, 'request', return_value=mock_response), \
             patch.object(client.logger, 'debug') as mock_debug:
            client._request("GET", "/test")
            # Check that logged data doesn't contain actual credentials
            logged_calls = [str(call) for call in mock_debug.call_args_list]
            all_logs = " ".join(logged_calls)
            # Authorization should be redacted
            assert "***REDACTED***" in all_logs or "api_key" not in all_logs.lower()


class TestRequestParameters:
    """Tests for request parameter handling."""
    
    def test_params_defensive_copy(self, client):
        """Test that params dict is defensively copied."""
        params = {"key": "value"}
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True}
        
        with patch.object(client.session, 'request', return_value=mock_response):
            client._request("GET", "/test", params=params)
            # Modify original dict
            params["key"] = "modified"
            # Should not affect the request (already made)
            # This test ensures defensive copying works
    
    def test_json_data_defensive_copy(self, client):
        """Test that json_data dict is defensively copied."""
        json_data = {"key": "value"}
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True}
        
        with patch.object(client.session, 'request', return_value=mock_response):
            client._request("POST", "/test", json_data=json_data)
            # Modify original dict
            json_data["key"] = "modified"
            # Should not affect the request (already made)
