"""End-to-end tests for DEX exchange workflow."""

import pytest
from unittest.mock import patch
from decimal import Decimal

from houdiniswap import HoudiniSwapClient
from houdiniswap.models import TransactionStatus, RouteDTO


class TestDexExchangeWorkflow:
    """Tests for complete DEX exchange workflow."""
    
    def test_complete_dex_exchange_flow(self, client, sample_dex_token_data, sample_dex_quote_data,
                                        sample_route_data, sample_exchange_response_data,
                                        sample_dex_approve_response_data, sample_status_data):
        """Test complete DEX exchange workflow: tokens -> quote -> approve -> exchange -> confirm -> status."""
        from houdiniswap.models import DEXTokensResponse, DEXToken
        
        # Step 1: Get DEX tokens
        dex_tokens_response = DEXTokensResponse(
            count=1,
            tokens=[DEXToken.from_dict(sample_dex_token_data)]
        )
        
        # Step 2: Get quote
        quote_data = sample_dex_quote_data.copy()
        quote_data["route"] = sample_route_data
        
        # Step 3: Approve (may return empty list if not needed)
        approve_data = sample_dex_approve_response_data
        
        # Step 4: Exchange
        exchange_data = sample_exchange_response_data
        
        # Step 5: Status updates
        status_waiting = {**sample_status_data, "status": TransactionStatus.WAITING.value}
        status_finished = {**sample_status_data, "status": TransactionStatus.FINISHED.value}
        
        with patch('houdiniswap.client.HoudiniSwapClient._request', side_effect=[
            {"count": 1, "tokens": [sample_dex_token_data]},  # get_dex_tokens
            [quote_data],  # get_dex_quote
            [approve_data],  # post_dex_approve
            exchange_data,  # post_dex_exchange
            status_waiting,  # get_status
            status_finished,  # get_status (final)
        ]):
            # Get DEX tokens
            tokens_response = client.get_dex_tokens(chain="base")
            assert tokens_response.count > 0
            
            # Get quote
            quotes = client.get_dex_quote(
                amount="1.0",
                token_id_from=sample_dex_token_data["id"],
                token_id_to=sample_dex_token_data["id"]
            )
            assert len(quotes) > 0
            quote = quotes[0]
            route = RouteDTO.from_dict(sample_route_data)
            
            # Approve tokens (if needed)
            approvals = client.post_dex_approve(
                token_id_from=sample_dex_token_data["id"],
                token_id_to=sample_dex_token_data["id"],
                address_from="0x1111111111111111111111111111111111111111",
                amount=1.0,
                swap=quote.swap,
                route=route
            )
            # Note: In real scenario, user would sign and broadcast approval tx here
            
            # Execute exchange
            exchange = client.post_dex_exchange(
                amount=1.0,
                token_id_from=sample_dex_token_data["id"],
                token_id_to=sample_dex_token_data["id"],
                address_from="0x1111111111111111111111111111111111111111",
                address_to="0x2222222222222222222222222222222222222222",
                swap=quote.swap,
                quote_id=quote.quote_id,
                route=route
            )
            houdini_id = exchange.houdini_id
            
            # Check status
            status = client.get_status(houdini_id)
            assert status.status == TransactionStatus.WAITING
            
            # Poll until finished
            with patch('time.sleep'):  # Speed up test
                final_status = client.poll_until_finished(houdini_id, timeout=10, poll_interval=0.1)
                assert final_status.status == TransactionStatus.FINISHED
    
    def test_dex_exchange_no_approval_needed(self, client, sample_dex_quote_data, sample_route_data,
                                              sample_exchange_response_data):
        """Test DEX exchange when approval is not needed."""
        route = RouteDTO.from_dict(sample_route_data)
        
        with patch('houdiniswap.client.HoudiniSwapClient._request', side_effect=[
            [sample_dex_quote_data],  # get_dex_quote
            [],  # post_dex_approve (empty = no approval needed)
            sample_exchange_response_data,  # post_dex_exchange
        ]):
            # Get quote
            quotes = client.get_dex_quote("1.0", "token1", "token2")
            quote = quotes[0]
            
            # Check if approval needed
            approvals = client.post_dex_approve(
                token_id_from="token1",
                token_id_to="token2",
                address_from="0x111",
                amount=1.0,
                swap=quote.swap,
                route=route
            )
            assert len(approvals) == 0  # No approval needed
            
            # Proceed directly to exchange
            exchange = client.post_dex_exchange(
                amount=1.0,
                token_id_from="token1",
                token_id_to="token2",
                address_from="0x111",
                address_to="0x222",
                swap=quote.swap,
                quote_id=quote.quote_id,
                route=route
            )
            assert exchange.houdini_id is not None
    
    def test_dex_exchange_with_confirm_tx(self, client, sample_dex_quote_data, sample_route_data,
                                           sample_exchange_response_data):
        """Test DEX exchange with transaction confirmation."""
        route = RouteDTO.from_dict(sample_route_data)
        
        with patch('houdiniswap.client.HoudiniSwapClient._request', side_effect=[
            [sample_dex_quote_data],  # get_dex_quote
            sample_exchange_response_data,  # post_dex_exchange
            True,  # post_dex_confirm_tx
        ]):
            # Get quote
            quotes = client.get_dex_quote("1.0", "token1", "token2")
            quote = quotes[0]
            
            # Execute exchange
            exchange = client.post_dex_exchange(
                amount=1.0,
                token_id_from="token1",
                token_id_to="token2",
                address_from="0x111",
                address_to="0x222",
                swap=quote.swap,
                quote_id=quote.quote_id,
                route=route
            )
            
            # Confirm transaction (after user signs and broadcasts)
            confirmed = client.post_dex_confirm_tx(
                transaction_id="tx123",
                tx_hash="0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890"
            )
            assert confirmed is True
    
    def test_dex_exchange_multiple_quotes(self, client, sample_dex_quote_data):
        """Test DEX exchange with multiple quote options."""
        quote1 = sample_dex_quote_data.copy()
        quote2 = {**sample_dex_quote_data, "quoteId": "quote2", "amountOut": "0.06"}
        
        with patch('houdiniswap.client.HoudiniSwapClient._request', return_value=[quote1, quote2]):
            quotes = client.get_dex_quote("1.0", "token1", "token2")
            assert len(quotes) == 2
            # User can choose best quote
            best_quote = max(quotes, key=lambda q: q.amount_out)
            assert best_quote.amount_out == Decimal("0.06")


class TestDexErrorScenarios:
    """Tests for error scenarios in DEX workflow."""
    
    def test_dex_exchange_expired_quote(self, client, sample_route_data):
        """Test DEX exchange with expired quote."""
        from houdiniswap.models import RouteDTO
        route = RouteDTO.from_dict(sample_route_data)
        
        from unittest.mock import MagicMock
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"message": "Quote expired"}
        
        with patch.object(client.session, 'request', return_value=mock_response):
            with pytest.raises(Exception):  # APIError
                client.post_dex_exchange(
                    amount=1.0,
                    token_id_from="token1",
                    token_id_to="token2",
                    address_from="0x111",
                    address_to="0x222",
                    swap="sw",
                    quote_id="expired_quote",
                    route=route
                )
    
    def test_dex_exchange_invalid_route(self, client, sample_dex_quote_data):
        """Test DEX exchange with mismatched route."""
        from houdiniswap.models import RouteDTO
        # Use route from different quote
        wrong_route = RouteDTO.from_dict({"bridge": "wrong_bridge"})
        
        from unittest.mock import MagicMock
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"message": "Route mismatch"}
        
        with patch.object(client.session, 'request', return_value=mock_response):
            with pytest.raises(Exception):  # APIError
                client.post_dex_exchange(
                    amount=1.0,
                    token_id_from="token1",
                    token_id_to="token2",
                    address_from="0x111",
                    address_to="0x222",
                    swap="sw",
                    quote_id="quote123",
                    route=wrong_route
                )
