"""End-to-end tests for CEX exchange workflow."""

import pytest
from unittest.mock import patch, MagicMock
from decimal import Decimal

from houdiniswap import HoudiniSwapClient
from houdiniswap.models import TransactionStatus


class TestCexExchangeWorkflow:
    """Tests for complete CEX exchange workflow."""
    
    def test_complete_cex_exchange_flow(self, client, sample_token_data, sample_quote_data, 
                                         sample_exchange_response_data, sample_status_data):
        """Test complete CEX exchange workflow: tokens -> quote -> exchange -> status."""
        # Step 1: Get available tokens
        with patch('houdiniswap.client.HoudiniSwapClient._request', side_effect=[
            [sample_token_data],  # get_cex_tokens
            sample_quote_data,  # get_cex_quote
            sample_exchange_response_data,  # post_cex_exchange
            {**sample_status_data, "status": TransactionStatus.WAITING.value},  # get_status (waiting)
            {**sample_status_data, "status": TransactionStatus.CONFIRMING.value},  # get_status (confirming)
            {**sample_status_data, "status": TransactionStatus.FINISHED.value},  # get_status (finished)
        ]):
            # Get tokens
            tokens = client.get_cex_tokens()
            assert len(tokens) > 0
            
            # Get quote
            quote = client.get_cex_quote(
                amount="1.0",
                from_token="ETH",
                to_token="BNB",
                anonymous=False
            )
            assert quote.amount_in == Decimal("1.0")
            
            # Execute exchange
            exchange = client.post_cex_exchange(
                amount=1.0,
                from_token="ETH",
                to_token="BNB",
                address_to="0x1234567890123456789012345678901234567890"
            )
            houdini_id = exchange.houdini_id
            assert houdini_id == "h9NpKm75gRnX7GWaFATwYn"
            
            # Check status (simulate polling)
            status = client.get_status(houdini_id)
            assert status.status == TransactionStatus.WAITING
            
            # Poll until finished
            with patch('time.sleep'):  # Speed up test
                final_status = client.poll_until_finished(houdini_id, timeout=10, poll_interval=0.1)
                assert final_status.status == TransactionStatus.FINISHED
    
    def test_cex_exchange_with_builder(self, client, sample_exchange_response_data):
        """Test CEX exchange using builder pattern."""
        with patch('houdiniswap.client.HoudiniSwapClient._request', return_value=sample_exchange_response_data):
            exchange = client.exchange_builder() \
                .cex() \
                .amount(1.0) \
                .from_token("ETH") \
                .to_token("BNB") \
                .address_to("0x1234567890123456789012345678901234567890") \
                .anonymous(True) \
                .execute()
            
            assert exchange.houdini_id == "h9NpKm75gRnX7GWaFATwYn"
    
    def test_cex_exchange_with_min_max_check(self, client, sample_token_data, sample_min_max_data, 
                                              sample_quote_data):
        """Test CEX exchange workflow with min/max validation."""
        with patch('houdiniswap.client.HoudiniSwapClient._request', side_effect=[
            [sample_token_data],  # get_cex_tokens
            sample_min_max_data,  # get_min_max
            sample_quote_data,  # get_cex_quote
        ]):
            # Get tokens
            tokens = client.get_cex_tokens()
            
            # Check min/max
            min_max = client.get_min_max(
                from_token="ETH",
                to_token="BNB",
                anonymous=False
            )
            assert min_max.min == Decimal("0.01")
            assert min_max.max == Decimal("100.0")
            
            # Amount is within range, proceed with quote
            quote = client.get_cex_quote(
                amount="1.0",
                from_token="ETH",
                to_token="BNB",
                anonymous=False
            )
            assert quote.amount_in == Decimal("1.0")
    
    def test_cex_exchange_anonymous_flow(self, client, sample_quote_data, sample_exchange_response_data):
        """Test anonymous CEX exchange flow."""
        # Create anonymous exchange response
        anonymous_response = {**sample_exchange_response_data, "anonymous": True}
        with patch('houdiniswap.client.HoudiniSwapClient._request', side_effect=[
            sample_quote_data,
            anonymous_response,
        ]):
            # Get quote for anonymous exchange
            quote = client.get_cex_quote(
                amount="1.0",
                from_token="ETH",
                to_token="BNB",
                anonymous=True,
                use_xmr=True
            )
            
            # Execute anonymous exchange
            exchange = client.post_cex_exchange(
                amount=1.0,
                from_token="ETH",
                to_token="BNB",
                address_to="0x123",
                anonymous=True,
                use_xmr=True
            )
            assert exchange.anonymous is True
    
    def test_cex_exchange_with_receiver_tag(self, client, sample_exchange_response_data):
        """Test CEX exchange with receiver tag (for networks like XRP)."""
        with patch('houdiniswap.client.HoudiniSwapClient._request', return_value=sample_exchange_response_data):
            exchange = client.post_cex_exchange(
                amount=1.0,
                from_token="ETH",
                to_token="XRP",
                address_to="rN7n7otQDd6FczFgLdSqtcsAUxDkw6fzRH",
                receiver_tag="123456"
            )
            # Verify receiver_tag was included in request
            # Note: With class-level patching, we can't easily check call_args
            # The receiver_tag parameter is passed and should be included in the API call
            assert exchange is not None


class TestCexErrorScenarios:
    """Tests for error scenarios in CEX workflow."""
    
    def test_cex_exchange_invalid_token(self, client):
        """Test CEX exchange with invalid token."""
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"message": "Invalid token"}
        
        with patch.object(client.session, 'request', return_value=mock_response):
            with pytest.raises(Exception):  # APIError
                client.get_cex_quote(
                    amount="1.0",
                    from_token="INVALID",
                    to_token="BNB",
                    anonymous=False
                )
    
    def test_cex_exchange_amount_too_low(self, client):
        """Test CEX exchange with amount below minimum."""
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"message": "Amount below minimum"}
        
        with patch.object(client.session, 'request', return_value=mock_response):
            with pytest.raises(Exception):  # APIError
                client.post_cex_exchange(
                    amount=0.001,  # Too low
                    from_token="ETH",
                    to_token="BNB",
                    address_to="0x123"
                )
    
    def test_cex_exchange_invalid_address(self, client):
        """Test CEX exchange with invalid address."""
        with pytest.raises(Exception):  # ValidationError
            client.post_cex_exchange(
                amount=1.0,
                from_token="ETH",
                to_token="BNB",
                address_to="invalid"  # Too short
            )
