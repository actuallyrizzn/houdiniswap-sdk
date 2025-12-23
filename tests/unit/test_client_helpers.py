"""Unit tests for client helper methods."""

import pytest
from decimal import Decimal

from houdiniswap import HoudiniSwapClient
from houdiniswap.exceptions import ValidationError


class TestClientValidation:
    """Tests for client validation methods."""
    
    def test_validate_credentials_valid(self, api_key, api_secret):
        """Test validating valid credentials."""
        client = HoudiniSwapClient(api_key, api_secret)
        # Should not raise
        client._validate_credentials(api_key, api_secret)
    
    def test_validate_credentials_with_colon(self, api_key, api_secret):
        """Test that credentials with colon raise ValidationError."""
        client = HoudiniSwapClient(api_key, api_secret)
        with pytest.raises(ValidationError, match="cannot contain ':'"):
            client._validate_credentials("key:with:colon", api_secret)
        with pytest.raises(ValidationError, match="cannot contain ':'"):
            client._validate_credentials(api_key, "secret:with:colon")
    
    def test_validate_credentials_too_long(self, api_key, api_secret):
        """Test that credentials that are too long raise ValidationError."""
        client = HoudiniSwapClient(api_key, api_secret)
        long_key = "x" * 1001
        with pytest.raises(ValidationError, match="exceed maximum length"):
            client._validate_credentials(long_key, api_secret)
    
    def test_validate_credentials_empty_after_strip(self, api_key, api_secret):
        """Test that empty credentials after strip raise ValidationError."""
        client = HoudiniSwapClient(api_key, api_secret)
        with pytest.raises(ValidationError):
            client._validate_credentials("   ", api_secret)
        with pytest.raises(ValidationError):
            client._validate_credentials(api_key, "   ")
    
    def test_sanitize_input_valid(self, client):
        """Test sanitizing valid input."""
        result = client._sanitize_input("valid_input", "field")
        assert result == "valid_input"
    
    def test_sanitize_input_strips_whitespace(self, client):
        """Test that sanitize_input strips whitespace."""
        result = client._sanitize_input("  input  ", "field")
        assert result == "input"
    
    def test_sanitize_input_empty_raises(self, client):
        """Test that empty input raises ValidationError."""
        with pytest.raises(ValidationError, match="cannot be empty"):
            client._sanitize_input("", "field")
        with pytest.raises(ValidationError, match="cannot be empty"):
            client._sanitize_input("   ", "field")
    
    def test_sanitize_input_non_string_raises(self, client):
        """Test that non-string input raises ValidationError."""
        with pytest.raises(ValidationError, match="must be a string"):
            client._sanitize_input(123, "field")
        with pytest.raises(ValidationError, match="must be a string"):
            client._sanitize_input(None, "field")
    
    def test_sanitize_input_dangerous_chars(self, client):
        """Test that dangerous characters raise ValidationError."""
        dangerous = ["\n", "\r", "\t", "\x00"]
        for char in dangerous:
            with pytest.raises(ValidationError, match="invalid characters"):
                client._sanitize_input(f"input{char}test", "field")
    
    def test_validate_amount_positive(self, client):
        """Test validating positive amounts."""
        client._validate_amount(1.0, "amount")
        client._validate_amount(0.01, "amount")
        client._validate_amount(100, "amount")
    
    def test_validate_amount_zero_raises(self, client):
        """Test that zero amount raises ValidationError."""
        with pytest.raises(ValidationError, match="must be greater than 0"):
            client._validate_amount(0, "amount")
    
    def test_validate_amount_negative_raises(self, client):
        """Test that negative amount raises ValidationError."""
        with pytest.raises(ValidationError, match="must be greater than 0"):
            client._validate_amount(-1, "amount")
    
    def test_validate_amount_non_number_raises(self, client):
        """Test that non-number raises ValidationError."""
        with pytest.raises(ValidationError, match="must be a number"):
            client._validate_amount("1.0", "amount")
        with pytest.raises(ValidationError, match="must be a number"):
            client._validate_amount(None, "amount")
    
    def test_validate_token_id_valid(self, client):
        """Test validating valid token ID."""
        client._validate_token_id("token123", "token_id")
    
    def test_validate_token_id_empty_raises(self, client):
        """Test that empty token ID raises ValidationError."""
        with pytest.raises(ValidationError):
            client._validate_token_id("", "token_id")
    
    def test_validate_page_valid(self, client):
        """Test validating valid page numbers."""
        client._validate_page(1, "page")
        client._validate_page(100, "page")
    
    def test_validate_page_zero_raises(self, client):
        """Test that page 0 raises ValidationError."""
        with pytest.raises(ValidationError, match="must be >= 1"):
            client._validate_page(0, "page")
    
    def test_validate_page_negative_raises(self, client):
        """Test that negative page raises ValidationError."""
        with pytest.raises(ValidationError, match="must be >= 1"):
            client._validate_page(-1, "page")
    
    def test_validate_page_non_integer_raises(self, client):
        """Test that non-integer page raises ValidationError."""
        with pytest.raises(ValidationError, match="must be an integer"):
            client._validate_page(1.5, "page")
    
    def test_validate_page_size_valid(self, client):
        """Test validating valid page sizes."""
        client._validate_page_size(1, "page_size")
        client._validate_page_size(100, "page_size")
    
    def test_validate_page_size_zero_raises(self, client):
        """Test that page size 0 raises ValidationError."""
        with pytest.raises(ValidationError, match="must be >= 1"):
            client._validate_page_size(0, "page_size")
    
    def test_validate_hex_string_valid(self, client):
        """Test validating valid hex strings."""
        client._validate_hex_string("0x123abc", "hex_string")
        client._validate_hex_string("123abc", "hex_string")
        client._validate_hex_string("ABCDEF", "hex_string")
    
    def test_validate_hex_string_invalid_raises(self, client):
        """Test that invalid hex string raises ValidationError."""
        with pytest.raises(ValidationError, match="valid hexadecimal string"):
            client._validate_hex_string("nothex", "hex_string")
        with pytest.raises(ValidationError, match="valid hexadecimal string"):
            client._validate_hex_string("0xGHIJKL", "hex_string")
    
    def test_validate_houdini_id_valid(self, client):
        """Test validating valid houdini IDs."""
        client._validate_houdini_id("h9NpKm75gRnX7GWaFATwYn")
        client._validate_houdini_id("test_123-abc")
    
    def test_validate_houdini_id_too_short_raises(self, client):
        """Test that too short houdini ID raises ValidationError."""
        with pytest.raises(ValidationError, match="between 10 and 50 characters"):
            client._validate_houdini_id("short")
    
    def test_validate_houdini_id_too_long_raises(self, client):
        """Test that too long houdini ID raises ValidationError."""
        long_id = "a" * 51
        with pytest.raises(ValidationError, match="between 10 and 50 characters"):
            client._validate_houdini_id(long_id)
    
    def test_validate_houdini_id_invalid_chars_raises(self, client):
        """Test that houdini ID with invalid chars raises ValidationError."""
        with pytest.raises(ValidationError, match="alphanumeric"):
            client._validate_houdini_id("invalid@id!")
    
    def test_validate_address_valid(self, client):
        """Test validating valid addresses."""
        client._validate_address("0x1234567890123456789012345678901234567890", field_name="address")
        client._validate_address("1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa", field_name="address")
    
    def test_validate_address_too_short_raises(self, client):
        """Test that too short address raises ValidationError."""
        with pytest.raises(ValidationError, match="between 10 and 200 characters"):
            client._validate_address("short", field_name="address")
    
    def test_validate_address_too_long_raises(self, client):
        """Test that too long address raises ValidationError."""
        long_address = "x" * 201
        with pytest.raises(ValidationError, match="between 10 and 200 characters"):
            client._validate_address(long_address, field_name="address")
    
    def test_validate_address_with_network(self, client, sample_network_data):
        """Test validating address with network regex."""
        from houdiniswap.models import Network
        network = Network.from_dict(sample_network_data)
        # Valid Ethereum address
        client._validate_address("0x1234567890123456789012345678901234567890", network=network, field_name="address")
        # Invalid format for Ethereum
        with pytest.raises(ValidationError):
            client._validate_address("invalid_address", network=network, field_name="address")


class TestClientNormalization:
    """Tests for client normalization methods."""
    
    def test_normalize_amount_string(self, client):
        """Test normalizing string amount."""
        result = client._normalize_amount("1.5")
        assert result == "1.5"
    
    def test_normalize_amount_decimal(self, client):
        """Test normalizing Decimal amount."""
        result = client._normalize_amount(Decimal("1.5"))
        assert result == "1.5"
    
    def test_normalize_amount_float(self, client):
        """Test normalizing float amount."""
        result = client._normalize_amount(1.5)
        assert isinstance(result, str)
        assert Decimal(result) == Decimal("1.5")
    
    def test_normalize_amount_int(self, client):
        """Test normalizing int amount."""
        result = client._normalize_amount(100)
        assert isinstance(result, str)
        assert Decimal(result) == Decimal("100")
    
    def test_normalize_amount_invalid_raises(self, client):
        """Test that invalid amount raises ValidationError."""
        with pytest.raises(ValidationError, match="valid number"):
            client._normalize_amount("not_a_number")
        with pytest.raises(ValidationError, match="must be str, Decimal, or number"):
            client._normalize_amount(None)
    
    def test_normalize_amount_to_decimal_string(self, client):
        """Test normalizing string to Decimal."""
        result = client._normalize_amount_to_decimal("1.5")
        assert result == Decimal("1.5")
    
    def test_normalize_amount_to_decimal_float(self, client):
        """Test normalizing float to Decimal."""
        result = client._normalize_amount_to_decimal(1.5)
        assert result == Decimal("1.5")
    
    def test_normalize_amount_to_decimal_decimal(self, client):
        """Test normalizing Decimal to Decimal."""
        result = client._normalize_amount_to_decimal(Decimal("1.5"))
        assert result == Decimal("1.5")
    
    def test_normalize_amount_to_decimal_invalid_raises(self, client):
        """Test that invalid amount raises ValidationError."""
        with pytest.raises(ValidationError, match="valid number"):
            client._normalize_amount_to_decimal("invalid")
        with pytest.raises(ValidationError, match="must be str, Decimal, or number"):
            client._normalize_amount_to_decimal(None)


class TestClientRedaction:
    """Tests for credential redaction."""
    
    def test_redact_credentials(self, client):
        """Test redacting credentials from data."""
        data = {
            "Authorization": "key:secret",
            "other": "data",
        }
        redacted = client._redact_credentials(data)
        assert redacted["Authorization"] == "***REDACTED***"
        assert redacted["other"] == "data"
    
    def test_redact_credentials_no_auth(self, client):
        """Test redacting when no Authorization header."""
        data = {"other": "data"}
        redacted = client._redact_credentials(data)
        assert redacted == data


class TestClientSignRequest:
    """Tests for request signing."""
    
    def test_sign_request_noop(self, client):
        """Test that sign_request is currently a no-op."""
        result = client._sign_request("GET", "https://example.com")
        assert result == {}
    
    def test_sign_request_with_params(self, client):
        """Test sign_request with parameters."""
        result = client._sign_request(
            "POST",
            "https://example.com",
            params={"key": "value"},
            json_data={"data": "test"}
        )
        assert result == {}
