"""Integration tests for client API methods."""

import pytest
from unittest.mock import patch, MagicMock
from decimal import Decimal

from houdiniswap import HoudiniSwapClient
from houdiniswap.exceptions import APIError, AuthenticationError, NetworkError, ValidationError
from houdiniswap.models import TransactionStatus


class TestGetCexTokens:
    """Tests for get_cex_tokens method."""
    
    def test_get_cex_tokens_success(self, client, sample_token_data):
        """Test successful get_cex_tokens call."""
        mock_response = [sample_token_data]
        with patch.object(client, '_request', return_value=mock_response):
            tokens = client.get_cex_tokens()
            assert len(tokens) == 1
            assert tokens[0].symbol == "ETH"
            assert tokens[0].name == "Ethereum"
            client._request.assert_called_once_with("GET", "/tokens")
    
    def test_get_cex_tokens_empty_list(self, client):
        """Test get_cex_tokens with empty response."""
        with patch.object(client, '_request', return_value=[]):
            tokens = client.get_cex_tokens()
            assert tokens == []
    
    def test_get_cex_tokens_multiple(self, client, sample_token_data):
        """Test get_cex_tokens with multiple tokens."""
        mock_response = [sample_token_data, {**sample_token_data, "id": "BTC", "symbol": "BTC"}]
        with patch.object(client, '_request', return_value=mock_response):
            tokens = client.get_cex_tokens()
            assert len(tokens) == 2
            assert tokens[0].symbol == "ETH"
            assert tokens[1].symbol == "BTC"
    
    def test_get_cex_tokens_invalid_response(self, client):
        """Test get_cex_tokens with invalid response type."""
        with patch.object(client, '_request', return_value={"error": "invalid"}):
            with pytest.raises(APIError, match="Unexpected response type"):
                client.get_cex_tokens()
    
    def test_get_cex_tokens_with_caching(self, client, sample_token_data):
        """Test get_cex_tokens with caching enabled."""
        client.cache_enabled = True
        mock_response = [sample_token_data]
        
        with patch.object(client, '_request', return_value=mock_response) as mock_request:
            # First call - should make API request
            tokens1 = client.get_cex_tokens()
            assert len(tokens1) == 1
            assert mock_request.call_count == 1
            
            # Second call - should use cache
            tokens2 = client.get_cex_tokens()
            assert len(tokens2) == 1
            assert mock_request.call_count == 1  # No additional call
    
    def test_get_cex_tokens_cache_expired(self, client, sample_token_data):
        """Test get_cex_tokens with expired cache."""
        import time
        client.cache_enabled = True
        client.cache_ttl = 0.1  # Very short TTL
        mock_response = [sample_token_data]
        
        with patch.object(client, '_request', return_value=mock_response) as mock_request:
            client.get_cex_tokens()
            assert mock_request.call_count == 1
            
            time.sleep(0.2)  # Wait for cache to expire
            client.get_cex_tokens()
            assert mock_request.call_count == 2  # Should make new request


class TestGetDexTokens:
    """Tests for get_dex_tokens method."""
    
    def test_get_dex_tokens_success(self, client, sample_dex_tokens_response_data):
        """Test successful get_dex_tokens call."""
        with patch.object(client, '_request', return_value=sample_dex_tokens_response_data):
            result = client.get_dex_tokens()
            assert result.count == 1
            assert len(result.tokens) == 1
            assert result.tokens[0].symbol == "USDC"
            client._request.assert_called_once()
            call_args = client._request.call_args
            assert call_args[0][0] == "GET"
            assert call_args[0][1] == "/dexTokens"
            assert call_args[1]["params"]["page"] == 1
            assert call_args[1]["params"]["pageSize"] == 100
    
    def test_get_dex_tokens_with_page(self, client, sample_dex_tokens_response_data):
        """Test get_dex_tokens with custom page."""
        with patch.object(client, '_request', return_value=sample_dex_tokens_response_data):
            result = client.get_dex_tokens(page=2, page_size=50)
            call_args = client._request.call_args
            assert call_args[1]["params"]["page"] == 2
            assert call_args[1]["params"]["pageSize"] == 50
    
    def test_get_dex_tokens_with_chain(self, client, sample_dex_tokens_response_data):
        """Test get_dex_tokens with chain filter."""
        with patch.object(client, '_request', return_value=sample_dex_tokens_response_data):
            result = client.get_dex_tokens(chain="base")
            call_args = client._request.call_args
            assert call_args[1]["params"]["chain"] == "base"
    
    def test_get_dex_tokens_empty(self, client):
        """Test get_dex_tokens with empty response."""
        with patch.object(client, '_request', return_value={"count": 0, "tokens": []}):
            result = client.get_dex_tokens()
            assert result.count == 0
            assert len(result.tokens) == 0
    
    def test_get_dex_tokens_invalid_page(self, client):
        """Test get_dex_tokens with invalid page number."""
        with pytest.raises(ValidationError, match="must be >= 1"):
            client.get_dex_tokens(page=0)
    
    def test_get_dex_tokens_with_caching(self, client, sample_dex_tokens_response_data):
        """Test get_dex_tokens with caching."""
        client.cache_enabled = True
        with patch.object(client, '_request', return_value=sample_dex_tokens_response_data) as mock_request:
            client.get_dex_tokens(page=1, chain="base")
            assert mock_request.call_count == 1
            client.get_dex_tokens(page=1, chain="base")  # Same params
            assert mock_request.call_count == 1  # Cached


class TestGetCexQuote:
    """Tests for get_cex_quote method."""
    
    def test_get_cex_quote_success(self, client, sample_quote_data):
        """Test successful get_cex_quote call."""
        with patch.object(client, '_request', return_value=sample_quote_data):
            quote = client.get_cex_quote(
                amount="1.0",
                from_token="ETH",
                to_token="BNB",
                anonymous=False
            )
            assert quote.amount_in == Decimal("1.0")
            assert quote.amount_out == Decimal("0.05")
            client._request.assert_called_once()
            call_args = client._request.call_args
            assert call_args[0][0] == "GET"
            assert call_args[0][1] == "/quote"
            assert call_args[1]["params"]["amount"] == "1.0"
            assert call_args[1]["params"]["from"] == "ETH"
            assert call_args[1]["params"]["to"] == "BNB"
            assert call_args[1]["params"]["anonymous"] is False
    
    def test_get_cex_quote_with_use_xmr(self, client, sample_quote_data):
        """Test get_cex_quote with use_xmr parameter."""
        with patch.object(client, '_request', return_value=sample_quote_data):
            quote = client.get_cex_quote(
                amount="1.0",
                from_token="ETH",
                to_token="BNB",
                anonymous=True,
                use_xmr=True
            )
            call_args = client._request.call_args
            assert call_args[1]["params"]["useXmr"] is True
    
    def test_get_cex_quote_anonymous(self, client, sample_quote_data):
        """Test get_cex_quote with anonymous flag."""
        with patch.object(client, '_request', return_value=sample_quote_data):
            quote = client.get_cex_quote(
                amount="1.0",
                from_token="ETH",
                to_token="BNB",
                anonymous=True
            )
            call_args = client._request.call_args
            assert call_args[1]["params"]["anonymous"] is True


class TestGetDexQuote:
    """Tests for get_dex_quote method."""
    
    def test_get_dex_quote_success(self, client, sample_dex_quote_data):
        """Test successful get_dex_quote call."""
        mock_response = [sample_dex_quote_data]
        with patch.object(client, '_request', return_value=mock_response):
            quotes = client.get_dex_quote(
                amount="1.0",
                token_id_from="token1",
                token_id_to="token2"
            )
            assert len(quotes) == 1
            assert quotes[0].quote_id == "quote_12345"
            assert quotes[0].amount_out == Decimal("0.05")
            client._request.assert_called_once()
            call_args = client._request.call_args
            assert call_args[0][0] == "GET"
            assert call_args[0][1] == "/dexQuote"
            assert call_args[1]["params"]["amount"] == "1.0"
            assert call_args[1]["params"]["tokenIdFrom"] == "token1"
            assert call_args[1]["params"]["tokenIdTo"] == "token2"
    
    def test_get_dex_quote_empty_list(self, client):
        """Test get_dex_quote with empty response."""
        with patch.object(client, '_request', return_value=[]):
            quotes = client.get_dex_quote("1.0", "token1", "token2")
            assert quotes == []
    
    def test_get_dex_quote_multiple_routes(self, client, sample_dex_quote_data):
        """Test get_dex_quote with multiple routes."""
        mock_response = [sample_dex_quote_data, {**sample_dex_quote_data, "quoteId": "quote2"}]
        with patch.object(client, '_request', return_value=mock_response):
            quotes = client.get_dex_quote("1.0", "token1", "token2")
            assert len(quotes) == 2
    
    def test_get_dex_quote_invalid_response(self, client):
        """Test get_dex_quote with invalid response type."""
        with patch.object(client, '_request', return_value={"error": "invalid"}):
            with pytest.raises(APIError, match="Unexpected response type"):
                client.get_dex_quote("1.0", "token1", "token2")
    
    def test_get_dex_quote_with_decimal(self, client, sample_dex_quote_data):
        """Test get_dex_quote with Decimal amount."""
        mock_response = [sample_dex_quote_data]
        with patch.object(client, '_request', return_value=mock_response):
            quotes = client.get_dex_quote(Decimal("1.0"), "token1", "token2")
            call_args = client._request.call_args
            assert call_args[1]["params"]["amount"] == "1.0"
    
    def test_get_dex_quote_with_float(self, client, sample_dex_quote_data):
        """Test get_dex_quote with float amount."""
        mock_response = [sample_dex_quote_data]
        with patch.object(client, '_request', return_value=mock_response):
            quotes = client.get_dex_quote(1.5, "token1", "token2")
            call_args = client._request.call_args
            assert isinstance(call_args[1]["params"]["amount"], str)


class TestPostCexExchange:
    """Tests for post_cex_exchange method."""
    
    def test_post_cex_exchange_success(self, client, sample_exchange_response_data):
        """Test successful post_cex_exchange call."""
        with patch.object(client, '_request', return_value=sample_exchange_response_data):
            response = client.post_cex_exchange(
                amount=1.0,
                from_token="ETH",
                to_token="BNB",
                address_to="0x1234567890123456789012345678901234567890"
            )
            assert response.houdini_id == "h9NpKm75gRnX7GWaFATwYn"
            client._request.assert_called_once()
            call_args = client._request.call_args
            assert call_args[0][0] == "POST"
            assert call_args[0][1] == "/exchange"
            json_data = call_args[1]["json_data"]
            assert json_data["amount"] == 1.0
            assert json_data["from"] == "ETH"
            assert json_data["to"] == "BNB"
            assert json_data["addressTo"] == "0x1234567890123456789012345678901234567890"
            assert json_data["anonymous"] is False
    
    def test_post_cex_exchange_with_optional_params(self, client, sample_exchange_response_data):
        """Test post_cex_exchange with optional parameters."""
        with patch.object(client, '_request', return_value=sample_exchange_response_data):
            response = client.post_cex_exchange(
                amount=1.0,
                from_token="ETH",
                to_token="BNB",
                address_to="0x123",
                anonymous=True,
                receiver_tag="tag123",
                wallet_id="wallet123",
                ip="192.168.1.1",
                user_agent="Mozilla/5.0",
                timezone="UTC",
                use_xmr=True
            )
            call_args = client._request.call_args
            json_data = call_args[1]["json_data"]
            assert json_data["anonymous"] is True
            assert json_data["receiverTag"] == "tag123"
            assert json_data["walletId"] == "wallet123"
            assert json_data["ip"] == "192.168.1.1"
            assert json_data["userAgent"] == "Mozilla/5.0"
            assert json_data["timezone"] == "UTC"
            assert json_data["useXmr"] is True
    
    def test_post_cex_exchange_invalid_amount(self, client):
        """Test post_cex_exchange with invalid amount."""
        with pytest.raises(ValidationError, match="must be greater than 0"):
            client.post_cex_exchange(
                amount=0,
                from_token="ETH",
                to_token="BNB",
                address_to="0x123"
            )
    
    def test_post_cex_exchange_with_decimal(self, client, sample_exchange_response_data):
        """Test post_cex_exchange with Decimal amount."""
        with patch.object(client, '_request', return_value=sample_exchange_response_data):
            response = client.post_cex_exchange(
                amount=Decimal("1.5"),
                from_token="ETH",
                to_token="BNB",
                address_to="0x123"
            )
            call_args = client._request.call_args
            json_data = call_args[1]["json_data"]
            assert json_data["amount"] == 1.5


class TestPostDexExchange:
    """Tests for post_dex_exchange method."""
    
    def test_post_dex_exchange_success(self, client, sample_exchange_response_data, sample_route_data):
        """Test successful post_dex_exchange call."""
        from houdiniswap.models import RouteDTO
        route = RouteDTO.from_dict(sample_route_data)
        
        with patch.object(client, '_request', return_value=sample_exchange_response_data):
            response = client.post_dex_exchange(
                amount=1.0,
                token_id_from="token1",
                token_id_to="token2",
                address_from="0x111",
                address_to="0x222",
                swap="sw",
                quote_id="quote123",
                route=route
            )
            assert response.houdini_id == "h9NpKm75gRnX7GWaFATwYn"
            client._request.assert_called_once()
            call_args = client._request.call_args
            assert call_args[0][0] == "POST"
            assert call_args[0][1] == "/dexExchange"
            json_data = call_args[1]["json_data"]
            assert json_data["amount"] == 1.0
            assert json_data["tokenIdFrom"] == "token1"
            assert json_data["tokenIdTo"] == "token2"
            assert json_data["swap"] == "sw"
            assert json_data["quoteId"] == "quote123"
            assert "route" in json_data


class TestPostDexApprove:
    """Tests for post_dex_approve method."""
    
    def test_post_dex_approve_success(self, client, sample_dex_approve_response_data, sample_route_data):
        """Test successful post_dex_approve call."""
        from houdiniswap.models import RouteDTO
        route = RouteDTO.from_dict(sample_route_data)
        mock_response = [sample_dex_approve_response_data]
        
        with patch.object(client, '_request', return_value=mock_response):
            responses = client.post_dex_approve(
                token_id_from="token1",
                token_id_to="token2",
                address_from="0x111",
                amount=1.0,
                swap="sw",
                route=route
            )
            assert len(responses) == 1
            assert responses[0].data == "0x1234567890abcdef"
            client._request.assert_called_once()
            call_args = client._request.call_args
            assert call_args[0][0] == "POST"
            assert call_args[0][1] == "/dexApprove"
    
    def test_post_dex_approve_empty_list(self, client, sample_route_data):
        """Test post_dex_approve with empty response (approval not needed)."""
        from houdiniswap.models import RouteDTO
        route = RouteDTO.from_dict(sample_route_data)
        
        with patch.object(client, '_request', return_value=[]):
            responses = client.post_dex_approve(
                token_id_from="token1",
                token_id_to="token2",
                address_from="0x111",
                amount=1.0,
                swap="sw",
                route=route
            )
            assert responses == []
    
    def test_post_dex_approve_invalid_response(self, client, sample_route_data):
        """Test post_dex_approve with invalid response type."""
        from houdiniswap.models import RouteDTO
        route = RouteDTO.from_dict(sample_route_data)
        
        with patch.object(client, '_request', return_value={"error": "invalid"}):
            with pytest.raises(APIError, match="Unexpected response type"):
                client.post_dex_approve(
                    token_id_from="token1",
                    token_id_to="token2",
                    address_from="0x111",
                    amount=1.0,
                    swap="sw",
                    route=route
                )


class TestPostDexConfirmTx:
    """Tests for post_dex_confirm_tx method."""
    
    def test_post_dex_confirm_tx_success(self, client):
        """Test successful post_dex_confirm_tx call."""
        with patch.object(client, '_request', return_value=True):
            result = client.post_dex_confirm_tx(
                transaction_id="tx123",
                tx_hash="0xabcdef1234567890"
            )
            assert result is True
            client._request.assert_called_once()
            call_args = client._request.call_args
            assert call_args[0][0] == "POST"
            assert call_args[0][1] == "/dexConfirmTx"
            json_data = call_args[1]["json_data"]
            assert json_data["id"] == "tx123"
            assert json_data["txHash"] == "0xabcdef1234567890"
    
    def test_post_dex_confirm_tx_invalid_hash(self, client):
        """Test post_dex_confirm_tx with invalid hash."""
        with pytest.raises(ValidationError, match="valid hexadecimal string"):
            client.post_dex_confirm_tx("tx123", "invalid_hash")


class TestGetStatus:
    """Tests for get_status method."""
    
    def test_get_status_success(self, client, sample_status_data):
        """Test successful get_status call."""
        with patch.object(client, '_request', return_value=sample_status_data):
            status = client.get_status("h9NpKm75gRnX7GWaFATwYn")
            assert status.houdini_id == "h9NpKm75gRnX7GWaFATwYn"
            assert status.status == TransactionStatus.FINISHED
            client._request.assert_called_once()
            call_args = client._request.call_args
            assert call_args[0][0] == "GET"
            assert call_args[0][1] == "/status"
            assert call_args[1]["params"]["id"] == "h9NpKm75gRnX7GWaFATwYn"
    
    def test_get_status_adds_houdini_id(self, client):
        """Test that get_status adds houdini_id if missing."""
        response_data = {"status": 0}
        with patch.object(client, '_request', return_value=response_data):
            status = client.get_status("test123")
            assert status.houdini_id == "test123"
    
    def test_get_status_invalid_id(self, client):
        """Test get_status with invalid houdini ID."""
        with pytest.raises(ValidationError):
            client.get_status("short")  # Too short


class TestGetMinMax:
    """Tests for get_min_max method."""
    
    def test_get_min_max_success(self, client, sample_min_max_data):
        """Test successful get_min_max call."""
        with patch.object(client, '_request', return_value=sample_min_max_data):
            min_max = client.get_min_max(
                from_token="ETH",
                to_token="BNB",
                anonymous=False
            )
            assert min_max.min == Decimal("0.01")
            assert min_max.max == Decimal("100.0")
            client._request.assert_called_once()
            call_args = client._request.call_args
            assert call_args[0][0] == "GET"
            assert call_args[0][1] == "/minMax"
            assert call_args[1]["params"]["from"] == "ETH"
            assert call_args[1]["params"]["to"] == "BNB"
    
    def test_get_min_max_with_cex_only(self, client, sample_min_max_data):
        """Test get_min_max with cex_only parameter."""
        with patch.object(client, '_request', return_value=sample_min_max_data):
            min_max = client.get_min_max(
                from_token="ETH",
                to_token="BNB",
                anonymous=False,
                cex_only=True
            )
            call_args = client._request.call_args
            assert call_args[1]["params"]["cexOnly"] is True


class TestGetVolume:
    """Tests for get_volume method."""
    
    def test_get_volume_success_dict(self, client, sample_volume_data):
        """Test successful get_volume call with dict response."""
        with patch.object(client, '_request', return_value=sample_volume_data):
            volume = client.get_volume()
            assert volume.count == 1000
            assert volume.total_transacted_usd == Decimal("1000000.50")
            client._request.assert_called_once_with("GET", "/volume")
    
    def test_get_volume_success_list(self, client, sample_volume_data):
        """Test successful get_volume call with list response."""
        with patch.object(client, '_request', return_value=[sample_volume_data]):
            volume = client.get_volume()
            assert volume.count == 1000
    
    def test_get_volume_invalid_response(self, client):
        """Test get_volume with invalid response type."""
        with patch.object(client, '_request', return_value="invalid"):
            with pytest.raises(APIError, match="Unexpected response type"):
                client.get_volume()


class TestGetWeeklyVolume:
    """Tests for get_weekly_volume method."""
    
    def test_get_weekly_volume_success_list(self, client, sample_weekly_volume_data):
        """Test successful get_weekly_volume call with list response."""
        mock_response = [sample_weekly_volume_data]
        with patch.object(client, '_request', return_value=mock_response):
            volumes = client.get_weekly_volume()
            assert len(volumes) == 1
            assert volumes[0].week == 1
            assert volumes[0].year == 2024
            client._request.assert_called_once_with("GET", "/weeklyVolume")
    
    def test_get_weekly_volume_success_dict(self, client, sample_weekly_volume_data):
        """Test successful get_weekly_volume call with dict response."""
        with patch.object(client, '_request', return_value=sample_weekly_volume_data):
            volumes = client.get_weekly_volume()
            assert len(volumes) == 1
    
    def test_get_weekly_volume_invalid_response(self, client):
        """Test get_weekly_volume with invalid response type."""
        with patch.object(client, '_request', return_value="invalid"):
            with pytest.raises(APIError, match="Unexpected response type"):
                client.get_weekly_volume()
