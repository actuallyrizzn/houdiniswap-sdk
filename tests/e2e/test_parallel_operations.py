"""End-to-end tests for parallel operations."""

import pytest
from unittest.mock import patch

from houdiniswap import HoudiniSwapClient


class TestParallelOperations:
    """Tests for parallel API operations."""
    
    def test_parallel_token_queries(self, client, sample_token_data, sample_dex_tokens_response_data):
        """Test parallel queries for CEX and DEX tokens."""
        with patch.object(client, '_request', side_effect=[
            [sample_token_data],  # get_cex_tokens
            sample_dex_tokens_response_data,  # get_dex_tokens
        ]):
            results = client.execute_parallel([
                lambda: client.get_cex_tokens(),
                lambda: client.get_dex_tokens(),
            ])
            
            assert len(results) == 2
            assert len(results[0]) > 0  # CEX tokens
            assert results[1].count > 0  # DEX tokens
    
    def test_parallel_status_checks(self, client, sample_status_data):
        """Test parallel status checks for multiple transactions."""
        status1 = {**sample_status_data, "houdiniId": "id1", "status": 0}
        status2 = {**sample_status_data, "houdiniId": "id2", "status": 4}
        status3 = {**sample_status_data, "houdiniId": "id3", "status": 1}
        
        with patch.object(client, '_request', side_effect=[status1, status2, status3]):
            results = client.execute_parallel([
                lambda: client.get_status("id1"),
                lambda: client.get_status("id2"),
                lambda: client.get_status("id3"),
            ])
            
            assert len(results) == 3
            assert results[0].houdini_id == "id1"
            assert results[1].houdini_id == "id2"
            assert results[2].houdini_id == "id3"
    
    def test_parallel_quotes(self, client, sample_quote_data):
        """Test parallel quote requests for different token pairs."""
        quote1 = {**sample_quote_data, "amountOut": "0.05"}
        quote2 = {**sample_quote_data, "amountOut": "0.10"}
        
        with patch.object(client, '_request', side_effect=[quote1, quote2]):
            results = client.execute_parallel([
                lambda: client.get_cex_quote("1.0", "ETH", "BNB", anonymous=False),
                lambda: client.get_cex_quote("1.0", "BTC", "ETH", anonymous=False),
            ])
            
            assert len(results) == 2
            assert results[0].amount_out > 0
            assert results[1].amount_out > 0
    
    def test_parallel_with_errors(self, client, sample_token_data):
        """Test parallel operations where some fail."""
        from unittest.mock import MagicMock
        
        mock_error = MagicMock()
        mock_error.status_code = 400
        mock_error.json.return_value = {"message": "Error"}
        
        with patch.object(client.session, 'request', side_effect=[
            [sample_token_data],  # Success
            mock_error,  # Error
        ]):
            results = client.execute_parallel([
                lambda: client.get_cex_tokens(),
                lambda: client.get_cex_tokens(),  # This will fail
            ])
            
            assert len(results) == 2
            assert len(results[0]) > 0  # First succeeded
            assert isinstance(results[1], Exception)  # Second failed
    
    def test_parallel_volume_queries(self, client, sample_volume_data, sample_weekly_volume_data):
        """Test parallel volume and weekly volume queries."""
        with patch.object(client, '_request', side_effect=[
            sample_volume_data,  # get_volume
            [sample_weekly_volume_data],  # get_weekly_volume
        ]):
            results = client.execute_parallel([
                lambda: client.get_volume(),
                lambda: client.get_weekly_volume(),
            ])
            
            assert len(results) == 2
            assert results[0].count > 0
            assert len(results[1]) > 0


class TestIterationAndPagination:
    """Tests for iteration and pagination helpers."""
    
    def test_iterate_all_dex_tokens(self, client, sample_dex_token_data):
        """Test iterating through all DEX tokens."""
        from houdiniswap.models import DEXTokensResponse, DEXToken
        
        page1 = DEXTokensResponse(
            count=250,
            tokens=[DEXToken.from_dict(sample_dex_token_data) for _ in range(100)]
        )
        page2 = DEXTokensResponse(
            count=250,
            tokens=[DEXToken.from_dict(sample_dex_token_data) for _ in range(100)]
        )
        page3 = DEXTokensResponse(
            count=250,
            tokens=[DEXToken.from_dict(sample_dex_token_data) for _ in range(50)]
        )
        
        with patch.object(client, 'get_dex_tokens', side_effect=[page1, page2, page3]):
            tokens = list(client.iter_dex_tokens(page_size=100))
            assert len(tokens) == 250
    
    def test_get_all_dex_tokens(self, client, sample_dex_token_data):
        """Test getting all DEX tokens at once."""
        from houdiniswap.models import DEXTokensResponse, DEXToken
        
        response = DEXTokensResponse(
            count=1,
            tokens=[DEXToken.from_dict(sample_dex_token_data)]
        )
        
        with patch.object(client, 'iter_dex_tokens', return_value=iter([DEXToken.from_dict(sample_dex_token_data)])):
            tokens = client.get_all_dex_tokens()
            assert len(tokens) == 1
            assert tokens[0].symbol == "USDC"
