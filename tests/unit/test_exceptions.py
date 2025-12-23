"""Unit tests for exception classes."""

import pytest

from houdiniswap.exceptions import (
    HoudiniSwapError,
    AuthenticationError,
    APIError,
    ValidationError,
    NetworkError,
)


class TestHoudiniSwapError:
    """Tests for base exception class."""
    
    def test_inheritance(self):
        """Test that HoudiniSwapError inherits from Exception."""
        error = HoudiniSwapError("Test error")
        assert isinstance(error, Exception)
    
    def test_message(self):
        """Test exception message."""
        error = HoudiniSwapError("Test error message")
        assert str(error) == "Test error message"
    
    def test_empty_message(self):
        """Test exception with empty message."""
        error = HoudiniSwapError("")
        assert str(error) == ""


class TestAuthenticationError:
    """Tests for AuthenticationError."""
    
    def test_inheritance(self):
        """Test that AuthenticationError inherits from HoudiniSwapError."""
        error = AuthenticationError("Auth failed")
        assert isinstance(error, HoudiniSwapError)
        assert isinstance(error, Exception)
    
    def test_message(self):
        """Test exception message."""
        error = AuthenticationError("Invalid credentials")
        assert str(error) == "Invalid credentials"


class TestAPIError:
    """Tests for APIError."""
    
    def test_inheritance(self):
        """Test that APIError inherits from HoudiniSwapError."""
        error = APIError("API error")
        assert isinstance(error, HoudiniSwapError)
    
    def test_message_only(self):
        """Test APIError with message only."""
        error = APIError("API error message")
        assert str(error) == "API error message"
        assert error.status_code is None
        assert error.response is None
    
    def test_with_status_code(self):
        """Test APIError with status code."""
        error = APIError("Not found", status_code=404)
        assert str(error) == "Not found"
        assert error.status_code == 404
        assert error.response is None
    
    def test_with_response(self):
        """Test APIError with response data."""
        response_data = {"error": "Invalid request", "code": 400}
        error = APIError("Bad request", status_code=400, response=response_data)
        assert str(error) == "Bad request"
        assert error.status_code == 400
        assert error.response == response_data
    
    def test_with_all_fields(self):
        """Test APIError with all fields."""
        response_data = {"message": "Rate limit exceeded"}
        error = APIError(
            "Too many requests",
            status_code=429,
            response=response_data
        )
        assert str(error) == "Too many requests"
        assert error.status_code == 429
        assert error.response == response_data


class TestValidationError:
    """Tests for ValidationError."""
    
    def test_inheritance(self):
        """Test that ValidationError inherits from HoudiniSwapError."""
        error = ValidationError("Validation failed")
        assert isinstance(error, HoudiniSwapError)
    
    def test_message(self):
        """Test exception message."""
        error = ValidationError("Invalid input")
        assert str(error) == "Invalid input"


class TestNetworkError:
    """Tests for NetworkError."""
    
    def test_inheritance(self):
        """Test that NetworkError inherits from HoudiniSwapError."""
        error = NetworkError("Network failed")
        assert isinstance(error, HoudiniSwapError)
    
    def test_message(self):
        """Test exception message."""
        error = NetworkError("Connection timeout")
        assert str(error) == "Connection timeout"
    
    def test_with_details(self):
        """Test NetworkError with detailed message."""
        error = NetworkError("Network error: Connection refused")
        assert "Connection refused" in str(error)
